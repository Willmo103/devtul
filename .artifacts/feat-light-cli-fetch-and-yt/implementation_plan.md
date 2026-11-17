# Implementation Plan: Lighter Termux CLI, Optional docx, and dt fetch & dt yt Commands

**Status:** Completed  
**Author:** AI Agent  
**Session:** `feat-light-cli-fetch-and-yt`  
**Tracking Issue:** [#30](https://github.com/Willmo103/devtul/issues/30)  
**Pull Request:** [#31](https://github.com/Willmo103/devtul/pull/31)  

---

## 1. Overview & Problem Diagnostic

1. **Move `python-docx` to Optional Dependency:**
   - `python-docx` was previously in standard `dependencies`, pulling heavy binary wheels (`lxml`, etc.).
   - Moved `python-docx` into `[project.optional-dependencies]` under `docx = ["python-docx>=1.1.2"]`.
   - Guarded `src/devtul/core/docx_processor.py` and `src/devtul/commands/repr_cmd.py` with friendly error instructions when `devtul[docx]` is not installed.

2. **Lighter Standard CLI for Termux:**
   - Restored `typer` and `rich` into core `dependencies` so standard installs provide the `dt` CLI directly.
   - Kept heavy C/C++ compiled dependencies (`duckdb`, `pdfplumber`, `sqlalchemy`) in `[project.optional-dependencies]` (`db`, `pdf`) so standard installs are lightweight, pure-Python compatible, and installable on Android Termux.

3. **`dt fetch` Command:**
   - Adapted logic from `.agents/docs/fetch_webpage.py` into `devtul.core.web_fetcher` and `devtul.commands.fetch_cmd`.
   - Features: Fetches webpage, strips boilerplate noise with BeautifulSoup, converts to clean Markdown with `html2text`.
   - Output: Renders with Rich Markdown in terminal by default, or saves to file via `-o / --output <filepath>`.

4. **`dt yt` Command:**
   - Adapted logic from `.agents/docs/download_youtube.py` into `devtul.core.youtube_downloader` and `devtul.commands.youtube_cmd`.
   - Syntax: `dt yt <url> <filepath> [-t --trans [pth] | -a --audio [path]]`.
   - Supports video download, audio-only download (`-a`), and subtitle transcript extraction (`-t`).

---

## 2. Proposed Architecture & Design

### A. Dependencies & Packaging (`pyproject.toml`)
- `dependencies`:
  - `typer>=0.20.0`, `rich>=14.2.0` (CLI in normal install)
  - `sqlite-utils`, `python-dotenv`, `toml`, `jinja2`, `pydantic`, `ollama`, `gitpython`, `pyyaml`, `markdown`, `beautifulsoup4`
  - `httpx>=0.28.1`, `html2text>=2025.4.15` (for `dt fetch`)
  - `yt-dlp>=2026.10.26`, `youtube-transcript-api>=1.2.5` (for `dt yt`)
- `optional-dependencies`:
  - `docx = ["python-docx>=1.1.2"]`
  - `pdf = ["pdfplumber>=0.11.5"]`
  - `db = ["duckdb>=1.5.6", "sqlalchemy>=2.0.44"]`
  - `cli = ["typer>=0.20.0", "rich>=14.2.0"]`
  - `all = [...]`
- `dependency-groups.dev`:
  - Includes all optional dependencies so local `pytest` tests pass.
- `project.scripts`:
  - `dt-fetch = "devtul.commands.fetch_cmd:entry"`
  - `dt-yt = "devtul.commands.youtube_cmd:entry"`

### B. Core Engines & Commands
1. `src/devtul/core/web_fetcher.py`:
   - `WebpageFetcher` class with SSRF validation, boilerplate stripping, link extraction, HTML-to-Markdown distillation.
2. `src/devtul/commands/fetch_cmd.py`:
   - `dt fetch <url> [-o output] [-m markdown-only] [--raw] [-j json]`
   - Renders with `rich.markdown.Markdown` to console and writes to file if `-o` is given.
3. `src/devtul/core/youtube_downloader.py`:
   - `YouTubeDownloader` engine wrapping `yt_dlp` and `youtube_transcript_api`.
4. `src/devtul/commands/youtube_cmd.py`:
   - `dt yt <url> <filepath> [-t --trans [pth] | -a --audio [path]]`
   - Uses `TyperCommand` subclass to normalize optional argument flags `-t` and `-a`.

---

## 3. Phased Task Checklist
- [x] Phase 1: Update `pyproject.toml` with Termux-friendly light dependencies and optional `docx`, `pdf`, `db`.
- [x] Phase 2: Guard `DocxProcessor` and `RprCommand` for optional `docx` dependency.
- [x] Phase 3: Implement `devtul.core.web_fetcher` and `devtul.commands.fetch_cmd`.
- [x] Phase 4: Implement `devtul.core.youtube_downloader` and `devtul.commands.youtube_cmd`.
- [x] Phase 5: Register commands in `main.py` and `commands/__init__.py`.
- [x] Phase 6: Add test suite for `dt fetch`, `dt yt`, and optional docx handling.
- [x] Phase 7: Run linting (`flake8`), formatting (`black`), and full `pytest` verification.
