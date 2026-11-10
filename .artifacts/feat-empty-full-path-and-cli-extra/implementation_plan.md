# Implementation Plan: Empty Command Full Path Output, [cli] Option, & Prune Piper/ONNX

**Status:** Completed  
**Author:** AI Agent  
**Session:** `feat-empty-full-path-and-cli-extra`  
**Tracking Issue:** [#28](https://github.com/Willmo103/devtul/issues/28)  
**Pull Request:** [#29](https://github.com/Willmo103/devtul/pull/29)  

---

## 1. Overview & Problem Diagnostic

1. **Dependency Pruning (`onnxruntime`, `piper-tts`):**
   - `piper-tts` was listed in `pyproject.toml` dependencies, bringing heavy native binary dependencies including `onnxruntime`.
   - The user requested removing `onnxruntime` and `piper` from dependencies and removing any active usages in the codebase.
   - `src/devtul/core/tts/` contained `PiperEngine` and `PiperConfig`, which were tested in `tests/test_migration_and_paths.py`. These were cleanly pruned and 18 packages (~200MB) uninstalled.

2. **`[cli]` Extra for Library Install:**
   - When consuming `devtul` as a library in downstream projects (e.g. `uv add git+https://github.com/willmo103/devtul`), users want a lightweight library footprint without being forced to install CLI-only frameworks.
   - Added a `[cli]` extra in `[project.optional-dependencies]` containing `typer` and `rich`.
   - Ensured `devtul` can be imported safely as a library even if `typer` is omitted, with clear error messaging when attempting to invoke the CLI without `[cli]`.
   - Preserved seamless local developer workflow (`uv sync`, `uv run dt`, `uv run pytest`) by configuring dev groups and optional dependency extras appropriately.

3. **Feature Enhancement: `dt empty --folders / --files`:**
   - The user specified:
     > The `dt empty --folders / --files` command needs to return the full path of the file or folder.
   - Updated `dt empty files` and `dt empty dirs` to return absolute POSIX full paths (`res.full_path.as_posix()`, `Path(dirpath).resolve().as_posix()`).
   - In addition, added support for flags `--folders` / `--dirs` and `--files` directly on `dt empty` (e.g. `dt empty --folders`, `dt empty --files`), along with alias `dt empty folders`.
   - Supported structured format options (`--json`, `--yaml`, `--csv`) consistently for both empty files and empty folders.

---

## 2. Proposed Architecture & Design

### A. Dependencies & Packaging
In `pyproject.toml`:
- Removed `"piper-tts>=1.3.0"` from `dependencies`.
- Removed `"typer>=0.20.0"` and `"rich>=14.2.0"` from `dependencies`, moving them to `[project.optional-dependencies]` under `cli`.
- In `[project.optional-dependencies]`:
  ```toml
  cli = [
      "typer>=0.20.0",
      "rich>=14.2.0",
  ]
  all = [
      "pyodbc>=5.3.0",
      "pymongo>=4.15.5",
      "mysql>=0.0.3",
      "psycopg2-binary>=2.9.11",
      "typer>=0.20.0",
      "rich>=14.2.0",
  ]
  dev = [
      "uv_build>=0.8.22,<0.9.0",
      "mkdocs>=1.6.1",
      "pytest>=7.4.2",
      "pytest-cov>=4.1.0",
      "pre-commit>=3.4.0",
      "typer>=0.20.0",
      "rich>=14.2.0",
  ]
  ```
- In `[dependency-groups] dev`:
  Added `"typer>=0.20.0"` and `"rich>=14.2.0"` so `uv sync` installs them by default for local development.

### B. Prune TTS Usages
- Deleted `src/devtul/core/tts/piper_engine.py` and `src/devtul/core/tts/__init__.py`.
- Removed `test_piper_engine_config` from `tests/test_migration_and_paths.py`.

### C. Enhance `empty_items.py`
- Enabled `invoke_without_command=True` on `empty = typer.Typer(...)`.
- Added `@empty.callback(invoke_without_command=True)` supporting:
  - `files: bool = typer.Option(False, "--files", help="Locate empty files and return full paths")`
  - `folders: bool = typer.Option(False, "--folders", "--dirs", help="Locate empty folders and return full paths")`
  - `path: Optional[Path] = typer.Option(None, "--path", "-p", help="Path to search for empty files or folders")`
  - `--json`, `--yaml`, `--csv`, `--git/--no-git`
- When invoked as `dt empty --files` or `dt empty --folders`, runs the respective scanner and outputs absolute POSIX full paths.
- Added subcommand `folders` as an alias to `dirs`.
- Updated `locate_empty_files` to output `res.full_path.as_posix()`.
- Updated `find_empty_folders` to output `Path(dirpath).resolve().as_posix()` and implement `--json`, `--yaml`, and `--csv` formatting.

---

## 3. Phased Task Checklist
- [x] Phase 1: Prune `piper-tts`, `onnxruntime`, and `devtul.core.tts`
- [x] Phase 2: Configure `[cli]` optional dependency in `pyproject.toml` and update `main.py` / `__init__.py`
- [x] Phase 3: Implement full path output and flag support for `dt empty`
- [x] Phase 4: Add comprehensive tests in `tests/test_empty_items.py` and run full test suite
- [x] Phase 5: Run formatting (`black`, `isort`, `flake8`) and synchronize `uv.lock`
