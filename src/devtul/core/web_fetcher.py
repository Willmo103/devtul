"""
Webpage fetcher and Markdown extractor for DevTul.
Provides URL validation with SSRF protection, HTTP fetching with custom headers,
boilerplate/script stripping, link extraction, and clean Markdown distillation.
"""

from __future__ import annotations

import hashlib
import ipaddress
import json
import re
import socket
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from urllib.parse import parse_qs, urljoin, urlparse, urlsplit

try:
    import httpx
except ImportError:
    httpx = None

try:
    from bs4 import BeautifulSoup, Comment, Tag
except ImportError:
    BeautifulSoup = None

try:
    from html2text import HTML2Text
except ImportError:
    HTML2Text = None

from pydantic import BaseModel, Field, field_validator


class ParsedUrl(BaseModel):
    """Decomposed components of a URL."""

    scheme: str
    netloc: str
    path: Optional[str] = None
    fragments: Optional[str] = None
    query: Optional[str] = None
    port: Optional[int] = None
    hostname: Optional[str] = None

    @classmethod
    def from_url(cls, url: str) -> "ParsedUrl":
        parsed = urlparse(url)
        try:
            port = parsed.port
        except (ValueError, TypeError):
            port = None

        try:
            hostname = parsed.hostname
        except (ValueError, TypeError):
            hostname = None

        return cls(
            scheme=parsed.scheme,
            netloc=parsed.netloc,
            path=parsed.path,
            fragments=parsed.fragment,
            query=parsed.query,
            port=port,
            hostname=hostname,
        )


class HTMLPage(BaseModel):
    """Scraped and distilled web page representation."""

    url: str
    title: Optional[str] = None
    html_content: Optional[str] = ""
    md_content: Optional[str] = ""
    links: List[str] = Field(default_factory=list)
    html_content_hash: Optional[str] = ""
    md_content_hash: Optional[str] = ""
    fetched_at: Optional[str] = ""
    description: Optional[str] = None
    keywords: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    status_code: Optional[int] = 200
    content_length: Optional[int] = 0

    @field_validator("links", mode="before")
    @classmethod
    def ensure_links_list(cls, v: Any, info: Any) -> List[str]:
        url = ""
        if hasattr(info, "data") and isinstance(info.data, dict):
            url = info.data.get("url", "")
        if isinstance(v, str):
            try:
                links_list = json.loads(v)
                if isinstance(links_list, list):
                    return [
                        urljoin(url, link) if link.startswith("/") else link
                        for link in links_list
                    ]
            except json.JSONDecodeError:
                return [urljoin(url, v) if v.startswith("/") else v]
        elif isinstance(v, list):
            return [
                urljoin(url, str(link)) if str(link).startswith("/") else str(link)
                for link in v
            ]
        return []


BOILERPLATE_TAGS = [
    "script",
    "style",
    "noscript",
    "header",
    "nav",
    "footer",
    "aside",
    "svg",
    "form",
    "iframe",
    "button",
    "canvas",
    "dialog",
]

BOILERPLATE_ATTR_PATTERN = re.compile(
    r"(cookie|consent|banner|newsletter|sidebar|social-share|ad-|advertisement|popup|modal|breadcrumb|widget|share-buttons|flyout)",
    re.IGNORECASE,
)

PRIMARY_CONTAINER_TEXT_THRESHOLD = 250


def get_configured_html2text() -> Any:
    """Configures HTML2Text for dense, readable Markdown output without line-wrapping."""
    if HTML2Text is None:
        return None
    h = HTML2Text()
    h.body_width = 0  # Disable line wrapping
    h.ignore_links = False
    h.ignore_images = False
    h.ignore_emphasis = False
    h.protect_links = True
    h.wrap_links = False
    h.single_line_break = False
    h.skip_internal_links = True
    h.inline_links = True
    return h


def strip_boilerplate_elements(soup: BeautifulSoup) -> None:
    """Decomposes script, style, navigation, footer, and boilerplate elements in place."""
    for comment in soup.find_all(string=lambda s: isinstance(s, Comment)):
        comment.extract()

    for tag_name in BOILERPLATE_TAGS:
        for element in soup.find_all(tag_name):
            element.decompose()

    for element in list(soup.find_all(True)):
        if getattr(element, "decomposed", False):
            continue
        classes = (
            " ".join(element.get("class", []))
            if isinstance(element.get("class"), list)
            else str(element.get("class", ""))
        )
        el_id = str(element.get("id", ""))
        combined_attr = f"{classes} {el_id}"

        if element.name in ("html", "body", "main", "article"):
            continue

        if BOILERPLATE_ATTR_PATTERN.search(combined_attr):
            if not element.find(["article", "main"]):
                element.decompose()


def extract_primary_content_container(soup: BeautifulSoup) -> Tag:
    """Finds the most specific substantive article container (<article> or <main>)."""
    for article in soup.find_all("article"):
        if len(article.get_text(strip=True)) >= PRIMARY_CONTAINER_TEXT_THRESHOLD:
            return article

    for main in soup.find_all("main"):
        if len(main.get_text(strip=True)) >= PRIMARY_CONTAINER_TEXT_THRESHOLD:
            return main

    for role_el in soup.find_all(attrs={"role": re.compile(r"^(main|article)$", re.I)}):
        if len(role_el.get_text(strip=True)) >= PRIMARY_CONTAINER_TEXT_THRESHOLD:
            return role_el

    return soup.body or soup


class WebpageFetcher:
    """
    Webpage fetcher with SSRF validation, boilerplate stripping,
    hyperlink extraction, and markdown conversion.
    """

    USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36 devtul/0.7"
    )

    HEADERS = {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
    }

    def __init__(self, timeout: int = 30, allow_internal: bool = False):
        self.timeout = timeout
        self.allow_internal = allow_internal

    @staticmethod
    def is_internal_ip(ip_str: str) -> bool:
        """Determines whether an IP address belongs to private or loopback ranges."""
        try:
            ip = ipaddress.ip_address(ip_str)
            return (
                ip.is_private
                or ip.is_loopback
                or ip.is_link_local
                or ip.is_reserved
                or ip.is_multicast
            )
        except ValueError:
            return False

    def validate_url(self, url: str) -> None:
        """Validates the target URL to prevent SSRF against loopback or private networks."""
        if not url or not isinstance(url, str):
            raise ValueError("URL must be a non-empty string.")

        parsed = urlsplit(url)
        scheme = parsed.scheme.lower()
        if scheme not in ("http", "https"):
            raise ValueError(
                f"Unsupported URL scheme '{scheme}'. Only http and https are permitted."
            )

        hostname = parsed.hostname
        if not hostname:
            raise ValueError("URL must contain a valid hostname.")

        if self.allow_internal:
            return

        # Check raw IP
        if self.is_internal_ip(hostname):
            raise ValueError(
                f"Access to private/internal IP address '{hostname}' is blocked."
            )

        # Check DNS resolution
        try:
            addr_info = socket.getaddrinfo(hostname, None)
            for entry in addr_info:
                ip_addr = entry[4][0]
                if self.is_internal_ip(ip_addr):
                    raise ValueError(
                        f"Target host '{hostname}' resolves to internal IP '{ip_addr}'. Request blocked."
                    )
        except socket.gaierror as e:
            raise ValueError(
                f"DNS resolution failure for host '{hostname}': {e}"
            ) from e

    def extract_links(self, raw_html: str, base_url: Optional[str] = None) -> List[str]:
        """Extracts and normalizes unique hyperlinks from HTML content."""
        if not raw_html:
            return []

        if BeautifulSoup is None:
            return re.findall(r'href=[\'"]?([^\'" >]+)', raw_html)

        soup = BeautifulSoup(
            raw_html, "html5lib" if "html5lib" in sys.modules else "html.parser"
        )
        resolved_links: List[str] = []
        seen: Set[str] = set()

        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            if not href or href.startswith(("#", "javascript:", "mailto:", "tel:")):
                continue
            if base_url:
                resolved = (
                    urljoin(base_url, href)
                    if href.startswith("/") or "://" not in href
                    else href
                )
            else:
                resolved = href
            if resolved and resolved not in seen:
                seen.add(resolved)
                resolved_links.append(resolved)

        return resolved_links

    def html_to_markdown(self, raw_html: str) -> str:
        """Sanitizes raw HTML and converts the substantive container into clean Markdown."""
        if not raw_html or not raw_html.strip():
            return ""

        if BeautifulSoup is None:
            return raw_html

        soup = BeautifulSoup(
            raw_html, "html5lib" if "html5lib" in sys.modules else "html.parser"
        )
        strip_boilerplate_elements(soup)
        primary_container = extract_primary_content_container(soup)
        cleaned_html = str(primary_container)

        h = get_configured_html2text()
        if h is not None:
            md_content = h.handle(cleaned_html)
        else:
            # Fallback simple text extraction
            md_content = primary_container.get_text(separator="\n\n").strip()

        # Collapse excessive blank lines (3+ down to 2)
        md_content = re.sub(r"\n{3,}", "\n\n", md_content)
        return md_content.strip()

    def fetch(self, url: str) -> HTMLPage:
        """
        Downloads a webpage, extracts raw hyperlinks, strips boilerplate,
        converts to clean Markdown, and computes cryptographic hashes.
        """
        if httpx is None:
            raise RuntimeError("httpx is required. Install with: pip install httpx")
        if BeautifulSoup is None:
            raise RuntimeError(
                "beautifulsoup4 is required. Install with: pip install beautifulsoup4"
            )

        self.validate_url(url)

        try:
            response = httpx.get(
                url,
                timeout=self.timeout,
                follow_redirects=True,
                headers=self.HEADERS,
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise RuntimeError(
                f"HTTP error {e.response.status_code} fetching {url}"
            ) from e
        except Exception as e:
            raise RuntimeError(f"Connection error fetching {url}: {e}") from e

        html_content = response.text
        content_type = response.headers.get("content-type", "").lower()
        if "text" not in content_type and "html" not in content_type:
            raise RuntimeError(
                f"Target URL returned non-text content type: {content_type}"
            )

        # 1. Extract hyperlinks from raw untouched HTML
        links = self.extract_links(html_content, base_url=url)

        # 2. Clean and convert to Markdown
        md_content = self.html_to_markdown(html_content)

        # 3. Extract title and description
        soup = BeautifulSoup(
            html_content, "html5lib" if "html5lib" in sys.modules else "html.parser"
        )
        title = url
        if soup.title and soup.title.string:
            title = soup.title.string.strip()

        og_desc = ""
        meta_desc = soup.find("meta", attrs={"name": "description"}) or soup.find(
            "meta", attrs={"property": "og:description"}
        )
        if meta_desc and meta_desc.get("content"):
            og_desc = meta_desc["content"].strip()

        # 4. Compute SHA-256 hashes
        html_hash = hashlib.sha256(html_content.encode("utf-8")).hexdigest()
        md_hash = hashlib.sha256(md_content.encode("utf-8")).hexdigest()

        return HTMLPage(
            url=str(response.url),
            title=title,
            html_content=html_content,
            md_content=md_content,
            links=links,
            html_content_hash=html_hash,
            md_content_hash=md_hash,
            fetched_at=datetime.now(timezone.utc).isoformat(),
            description=og_desc or None,
            status_code=response.status_code,
            content_length=len(md_content),
        )
