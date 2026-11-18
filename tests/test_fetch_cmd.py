from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from devtul.commands.fetch_cmd import fetch_app
from devtul.core.web_fetcher import HTMLPage, WebpageFetcher
from devtul.main import app

runner = CliRunner()


def test_webpage_fetcher_url_validation():
    fetcher = WebpageFetcher()
    # Invalid schemes
    with pytest.raises(ValueError, match="Unsupported URL scheme"):
        fetcher.validate_url("ftp://example.com/file")

    # SSRF guard against private IPs
    with pytest.raises(ValueError, match="blocked"):
        fetcher.validate_url("http://127.0.0.1:8000")

    with pytest.raises(ValueError, match="blocked"):
        fetcher.validate_url("http://192.168.1.100")

    with pytest.raises(ValueError, match="blocked"):
        fetcher.validate_url("http://localhost:3000")

    # Allowed when allow_internal=True
    permissive_fetcher = WebpageFetcher(allow_internal=True)
    permissive_fetcher.validate_url("http://127.0.0.1:8000")


def test_html_to_markdown_cleaning():
    raw_html = """
    <html>
      <head>
        <title>Article Title</title>
        <script>alert('bad');</script>
        <style>.ad { color: red; }</style>
      </head>
      <body>
        <nav><a href="/home">Home</a></nav>
        <div class="ad-banner">Advertisement here</div>
        <main>
          <h1>Main Article</h1>
          <p>This is the substantive article paragraph with <strong>bold</strong> words.</p>
          <a href="https://example.com/learn">Learn More</a>
        </main>
        <footer><p>Copyright 2026</p></footer>
      </body>
    </html>
    """
    fetcher = WebpageFetcher()
    md = fetcher.html_to_markdown(raw_html)

    assert "Main Article" in md
    assert "substantive article paragraph" in md
    assert "alert" not in md
    assert "Advertisement" not in md
    assert "Copyright" not in md


def test_fetch_command_output_file(tmp_path: Path):
    sample_page = HTMLPage(
        url="https://example.com/post",
        title="Sample Page",
        html_content="<p>Hello world</p>",
        md_content="Hello world markdown content.",
        links=["https://example.com/learn"],
        status_code=200,
        content_length=28,
        fetched_at="2026-11-17T00:00:00Z",
    )

    out_file = tmp_path / "fetched.md"

    with patch.object(WebpageFetcher, "fetch", return_value=sample_page):
        res = runner.invoke(
            app, ["fetch", "https://example.com/post", "-o", str(out_file)]
        )
        assert res.exit_code == 0
        assert out_file.exists()
        saved_text = out_file.read_text(encoding="utf-8")
        assert "Sample Page" in saved_text
        assert "Hello world markdown content" in saved_text


def test_fetch_command_markdown_only_and_json(tmp_path: Path):
    sample_page = HTMLPage(
        url="https://example.com/post",
        title="Sample Page",
        html_content="<p>Hello world</p>",
        md_content="Pure markdown body.",
        links=[],
        status_code=200,
        content_length=19,
        fetched_at="2026-11-17T00:00:00Z",
    )

    # 1. Markdown only to stdout
    with patch.object(WebpageFetcher, "fetch", return_value=sample_page):
        res_m = runner.invoke(
            app, ["fetch", "https://example.com/post", "--markdown-only", "--raw"]
        )
        assert res_m.exit_code == 0
        assert "Pure markdown body." in res_m.output
        assert "Sample Page" not in res_m.output

    # 2. JSON output to file
    json_file = tmp_path / "output.json"
    with patch.object(WebpageFetcher, "fetch", return_value=sample_page):
        res_j = runner.invoke(
            app, ["fetch", "https://example.com/post", "--json", "-o", str(json_file)]
        )
        assert res_j.exit_code == 0
        assert json_file.exists()
        assert '"url": "https://example.com/post"' in json_file.read_text(
            encoding="utf-8"
        )
