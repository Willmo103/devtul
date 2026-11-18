"""
Command 'dt fetch' / 'dt-fetch'.
Fetches webpage, strips boilerplate noise, and converts to clean Markdown.
Renders with Rich Markdown in terminal and/or saves to a file.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.markdown import Markdown
import typer

from devtul.core.web_fetcher import WebpageFetcher

console = Console()

fetch_app = typer.Typer(
    name="fetch",
    help="Fetch a webpage, clean HTML, and display or save clean Markdown.",
    no_args_is_help=True,
)


@fetch_app.command(name="page", hidden=True)
def fetch_page_cmd(
    url: str = typer.Argument(..., help="Target URL to fetch (http or https)."),
    output: Optional[Path] = typer.Option(
        None, "--output", "-o", help="File path to save the output Markdown."
    ),
    markdown_only: bool = typer.Option(
        False,
        "--markdown-only",
        "-m",
        help="Print only clean Markdown without metadata header.",
    ),
    raw: bool = typer.Option(
        False,
        "--raw",
        help="Print raw unrendered Markdown instead of rich terminal rendering.",
    ),
    json_output: bool = typer.Option(
        False, "--json", "-j", help="Output complete structured JSON payload."
    ),
    allow_internal: bool = typer.Option(
        False,
        "--allow-internal",
        help="Allow loopback or internal private IP addresses.",
    ),
    timeout: int = typer.Option(
        30, "--timeout", "-t", help="HTTP connection timeout in seconds."
    ),
) -> None:
    fetch_command(
        url=url,
        output=output,
        markdown_only=markdown_only,
        raw=raw,
        json_output=json_output,
        allow_internal=allow_internal,
        timeout=timeout,
    )


def fetch_command(
    url: str = typer.Argument(..., help="Target URL to fetch (http or https)."),
    output: Optional[Path] = typer.Option(
        None, "--output", "-o", help="File path to save the output Markdown."
    ),
    markdown_only: bool = typer.Option(
        False,
        "--markdown-only",
        "-m",
        help="Print only clean Markdown without metadata header.",
    ),
    raw: bool = typer.Option(
        False,
        "--raw",
        help="Print raw unrendered Markdown instead of rich terminal rendering.",
    ),
    json_output: bool = typer.Option(
        False, "--json", "-j", help="Output complete structured JSON payload."
    ),
    allow_internal: bool = typer.Option(
        False,
        "--allow-internal",
        help="Allow loopback or internal private IP addresses.",
    ),
    timeout: int = typer.Option(
        30, "--timeout", "-t", help="HTTP connection timeout in seconds."
    ),
) -> None:
    """
    Downloads webpage content, strips boilerplate, and displays or saves clean Markdown.
    Examples:
        dt fetch https://example.com
        dt fetch https://example.com -o article.md
        dt fetch https://example.com --raw
    """
    fetcher = WebpageFetcher(timeout=timeout, allow_internal=allow_internal)

    try:
        page = fetcher.fetch(url)
    except Exception as e:
        console.print(f"[bold red]Error fetching {url}:[/bold red] {e}")
        raise typer.Exit(code=1)

    if json_output:
        json_str = json.dumps(page.model_dump(), indent=2)
        if output:
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(json_str, encoding="utf-8")
            console.print(
                f"[bold green]Successfully saved JSON output to {output}[/bold green]"
            )
        else:
            typer.echo(json_str)
        return

    if markdown_only:
        text_content = page.md_content or ""
    else:
        text_content = (
            f"# {page.title}\n"
            f"- URL: {page.url}\n"
            f"- Fetched At: {page.fetched_at}\n"
            f"- HTTP Status: {page.status_code}\n"
            f"- Extracted Links: {len(page.links)}\n"
            f"- Markdown Length: {page.content_length} chars\n\n"
            f"## Clean Markdown Content\n\n"
            f"{page.md_content}\n"
        )

    # Save to file if output specified
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(text_content, encoding="utf-8")
        console.print(
            f"[bold green]Successfully saved Markdown to {output}[/bold green]"
        )

    # Print to console (always print if no output specified, or preview)
    if not output:
        if raw:
            typer.echo(text_content)
        else:
            console.print(Markdown(text_content))


@fetch_app.command(name="links", help="Extract and list all hyperlinks from a webpage.")
def fetch_links_cmd(
    url: str = typer.Argument(..., help="Target URL to extract links from."),
    json_output: bool = typer.Option(
        False, "--json", "-j", help="Output links as a JSON array."
    ),
    allow_internal: bool = typer.Option(
        False,
        "--allow-internal",
        help="Allow loopback or internal private IP addresses.",
    ),
    timeout: int = typer.Option(
        30, "--timeout", "-t", help="HTTP connection timeout in seconds."
    ),
) -> None:
    """Scrapes raw HTML and extracts all resolved hyperlinks."""
    fetcher = WebpageFetcher(timeout=timeout, allow_internal=allow_internal)

    try:
        page = fetcher.fetch(url)
    except Exception as e:
        console.print(f"[bold red]Error extracting links from {url}:[/bold red] {e}")
        raise typer.Exit(code=1)

    if json_output:
        typer.echo(json.dumps(page.links, indent=2))
    else:
        console.print(f"[bold cyan]Found {len(page.links)} links on {url}:[/bold cyan]")
        for link in page.links:
            typer.echo(f"  - {link}")


@fetch_app.command(name="clean", help="Convert a local HTML file into clean Markdown.")
def fetch_clean_cmd(
    html_file: Path = typer.Argument(..., help="Path to local HTML file."),
    output: Optional[Path] = typer.Option(
        None, "--output", "-o", help="File path to save the cleaned Markdown."
    ),
    raw: bool = typer.Option(
        False,
        "--raw",
        help="Print raw unrendered Markdown instead of rich terminal rendering.",
    ),
) -> None:
    """Reads local HTML, removes boilerplate, and prints or saves clean Markdown."""
    if not html_file.exists():
        console.print(f"[bold red]File not found: {html_file}[/bold red]")
        raise typer.Exit(code=1)

    raw_html = html_file.read_text(encoding="utf-8", errors="ignore")
    fetcher = WebpageFetcher()
    md_content = fetcher.html_to_markdown(raw_html)

    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(md_content, encoding="utf-8")
        console.print(
            f"[bold green]Successfully cleaned and saved Markdown to {output}[/bold green]"
        )
    else:
        if raw:
            typer.echo(md_content)
        else:
            console.print(Markdown(md_content))


def entry():
    import sys

    known_commands = {"page", "links", "clean", "--help", "-h"}
    if (
        len(sys.argv) > 1
        and not sys.argv[1].startswith("-")
        and sys.argv[1] not in known_commands
    ):
        sys.argv.insert(1, "page")
    fetch_app()
