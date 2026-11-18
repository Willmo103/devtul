# Walkthrough: Lighter Termux CLI, Optional docx, and dt fetch & dt yt Commands

**Tracking Issue:** [#30](https://github.com/Willmo103/devtul/issues/30)  
**Pull Request:** [#31](https://github.com/Willmo103/devtul/pull/31)  

---

## 1. Summary of Changes

### Lighter Termux-Compatible CLI & Optional `docx`
- **CLI Restored to Normal Install:** Re-added `typer>=0.20.0` and `rich>=14.2.0` directly to `dependencies` in [`pyproject.toml`](file:///c:/src/devtul/pyproject.toml).
- **Optional Dependencies:** Moved heavy C/C++ compiled dependencies (`python-docx`, `pdfplumber`, `duckdb`, `sqlalchemy`) out of standard dependencies into optional extras:
  - `docx = ["python-docx>=1.1.2"]`
  - `pdf = ["pdfplumber>=0.11.5"]`
  - `db = ["duckdb>=1.5.6", "sqlalchemy>=2.0.44"]`
- **Termux Portability:** Standard package install now consists of pure-Python and lightweight libraries, allowing direct installation on Android Termux without compilation failures.
- **Graceful Error Handling:** Commands requiring optional dependencies (`dt rpr --docx`, `dt ppdf`, `dt db`) display friendly installation guidance rather than tracebacks when extras are missing.

### New Command: `dt fetch`
- **Module:** [`src/devtul/commands/fetch_cmd.py`](file:///c:/src/devtul/src/devtul/commands/fetch_cmd.py) and [`src/devtul/core/web_fetcher.py`](file:///c:/src/devtul/src/devtul/core/web_fetcher.py).
- **Features:**
  - Full SSRF validation blocking private/loopback/internal IPs (with `--allow-internal` override).
  - HTML boilerplate and noise stripping (scripts, styles, navigation, footers, ads) via BeautifulSoup.
  - Substantive content distillation into clean Markdown using `html2text`.
  - Rich terminal Markdown rendering (`console.print(Markdown(...))`) by default.
  - File export via `-o / --output <filepath>`.
  - Flags for `--raw`, `--markdown-only`, and `--json`.
  - Script entrypoint: `dt-fetch`.

### New Command: `dt yt`
- **Module:** [`src/devtul/commands/youtube_cmd.py`](file:///c:/src/devtul/src/devtul/commands/youtube_cmd.py) and [`src/devtul/core/youtube_downloader.py`](file:///c:/src/devtul/src/devtul/core/youtube_downloader.py).
- **Syntax:** `dt yt <url> <filepath> [-t --trans [pth] | -a --audio [path]]`
- **Features:**
  - Robust video ID extraction supporting all YouTube URL formats (watch, shorts, embed, youtu.be, raw ID).
  - Downloads merged video stream (MP4) to `<filepath>` by default.
  - Downloads audio-only stream (`-a / --audio`) to `<filepath>` or custom path.
  - Extracts timestamped subtitle transcript (`-t / --trans`) to `<filepath>.txt` or custom path.
  - Custom `TyperCommand` subclass normalization supporting both flag and path argument variants.
  - Script entrypoint: `dt-yt`.

---

## 2. Verification Results

### Automated Tests
Run via `uv run pytest`:
```
============================= 79 passed in 3.06s ==============================
```
- Added `tests/test_fetch_cmd.py` (4 tests: URL validation, SSRF protection, boilerplate stripping, file export, Markdown-only, and JSON export).
- Added `tests/test_youtube_cmd.py` (4 tests: ID extraction across all formats, filename sanitization, arg normalization, mocked download & transcript).
- Added `tests/test_docx_optional.py` (2 tests: DocxProcessor and RprCommand graceful handling when `python-docx` is not installed).

### Code Quality & Linting
- `uv run flake8 src tests`: Passed with 0 errors.
- `uv run black`: Applied to all modified and new files.
- `uv sync`: Synchronized `uv.lock`.

### Manual CLI Inspection
```powershell
uv run dt --help
uv run dt fetch --help
uv run dt yt --help
```
Both `fetch` and `yt` commands are registered and functional.
