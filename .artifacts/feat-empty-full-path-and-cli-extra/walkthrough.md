# Walkthrough: Empty Command Full Path Output, [cli] Option, & Prune Piper/ONNX

**Tracking Issue:** [#28](https://github.com/Willmo103/devtul/issues/28)
**Pull Request:** [#29](https://github.com/Willmo103/devtul/pull/29)

---

## 1. Summary of Changes

### Dependency & Usage Cleanup
- Removed `piper-tts>=1.3.0` from `pyproject.toml` dependencies.
- Pruned `onnxruntime` and all transitive dependencies (18 packages removed, reducing install footprint significantly).
- Removed unused `src/devtul/core/tts/` module and removed the piper engine unit test from `tests/test_migration_and_paths.py`.

### Packaging & Optional `[cli]` Extra
- Established `cli = ["typer>=0.20.0", "rich>=14.2.0"]` under `[project.optional-dependencies]`.
- Moved `typer` and `rich` out of mandatory library dependencies into the `[cli]` extra.
- Downstream projects installing `devtul` as a library via `uv add git+https://github.com/willmo103/devtul` will install only the lightweight library dependencies.
- Projects needing the CLI install via `uv add "devtul[cli] @ git+https://github.com/willmo103/devtul"`.
- Guarded `src/devtul/__init__.py`, `src/devtul/main.py`, and `src/devtul/core/` modules (`file_utils.py`, `command.py`, `interactive.py`, `reporter.py`, `utils.py`) with graceful import fallbacks so library consumers can import models and utilities without needing CLI packages.
- When `dt` is invoked in an environment missing the `[cli]` extra, it exits cleanly with a helpful installation message.

### Feature Enhancement: `dt empty --folders / --files`
- Enhanced `dt empty` in `src/devtul/commands/empty_items.py` to output absolute resolved POSIX paths (`C:/path/to/file.txt`).
- Added flag support directly to `dt empty`:
  - `dt empty --files` (scans current directory or path specified via `-p` / `--path`).
  - `dt empty --folders` / `dt empty --dirs`.
- Supported subcommands with positional path argument:
  - `dt empty files [PATH]`
  - `dt empty dirs [PATH]`
  - `dt empty folders [PATH]` (new alias for `dirs`).
- Implemented structured format options (`--json`, `--yaml`, `--csv`) consistently across both empty files and empty folders.

---

## 2. Verification Results

### Automated Tests
Run via `uv run pytest`:
```
============================= 69 passed in 2.74s ==============================
```
- Added `tests/test_empty_items.py` (8 test cases covering `--files`, `--folders`, `--dirs`, `files`, `dirs`, `folders`, `--json`, `--yaml`, `--csv`, cwd default, and nonexistent path handling).
- Added `tests/test_cli_extra.py` (2 test cases verifying isolated library imports and fallback CLI error behavior).

### Code Quality & Linting
- `uv run flake8 src tests`: Passed with 0 errors.
- `uv run black`: Applied formatting to modified files.
- `uv sync`: Synchronized `uv.lock`.

### Manual CLI Verification
```powershell
uv run dt empty --help
uv run dt empty --files
uv run dt empty --folders
```
Empty files and empty directories return resolved full paths.

