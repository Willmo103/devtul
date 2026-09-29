# DevTul Project Guide & Workspace Rules (GEMINI.md)

Welcome to **DevTul** (`dt`). This document serves as the primary guidance, architectural reference, and operational playbook for Gemini and other AI coding agents working in this codebase.

---

## 1. Project Overview

**DevTul** is a modular CLI developer toolsuite written in Python and built with [Typer](https://typer.tiangolo.com/), [GitPython](https://gitpython.readthedocs.io/), and [Rich](https://rich.readthedocs.io/). It provides repository utilities for:
- Visualizing directory structures (`dt tree`)
- Generating comprehensive markdown repository documentation with frontmatter and syntax-highlighted source code (`dt md`)
- Listing and filtering git-tracked or all files with format conversions (`dt ls`)
- Searching keywords across codebase files (`dt find`)
- Locating marker folders/files (`dt find-folder`)
- Identifying empty files and empty folders (`dt empty files`, `dt empty dirs`)
- Managing and scaffolding user file templates from a local SQLite database (`dt new`)
- Storing and managing database connection profiles (`dt db`)
- Generating and serving visual repository HTML inspection reports (`dt reporter scan`, `dt reporter serve`)
- Copying/archiving repository files (`dt cp`)

---

## 2. Codebase Architecture & Structure

```
c:/src/devtul/
├── src/devtul/
│   ├── commands/              # CLI Subcommands & entrypoints
│   │   ├── copy.py            # 'dt cp' - File copying & zip archiving
│   │   ├── db.py              # 'dt db' - Database connection management
│   │   ├── dirs.py            # 'dt find-folder' - Search for marker directories/files
│   │   ├── empty_items.py     # 'dt empty' - Locate empty files/dirs
│   │   ├── find.py            # 'dt find' - Search text inside repo files
│   │   ├── list_files.py      # 'dt ls' - List files with format export (JSON/YAML/CSV)
│   │   ├── markdown.py        # 'dt md' - Repository markdown documentation generator
│   │   ├── metadata.py        # 'dt meta' - Display git repository metadata table
│   │   ├── new.py             # 'dt new' - User file template management (SQLite)
│   │   └── tree.py            # 'dt tree' - Formatted tree hierarchy output
│   ├── core/                  # Core domain logic, models, and shared utilities
│   │   ├── db/                # Specialized database handlers (Postgres session/utils)
│   │   ├── templates/         # Jinja2 templates (report.html, git_meta.md.jinja, base.md.jinja)
│   │   ├── config.py          # App paths (~/.devtul), Jinja environment, default EDITOR
│   │   ├── constants.py       # Global ignore patterns, extensions, format enums, syntax xref
│   │   ├── database.py        # SQLite interface (~/.devtul/devtul_interface.db) via sqlite-utils
│   │   ├── file_utils.py      # Path gathering, filtering, tree building, file search
│   │   ├── interactive.py     # Interactive prompts for database connections
│   │   ├── models.py          # Pydantic & domain models (FileResult, RepoMarkdownHeader, etc.)
│   │   ├── reporter.py        # 'dt reporter' - Scan repo to JSON cache & serve HTML report
│   │   └── utils.py           # Serialization, template rendering, editor launch helpers
│   ├── git/                   # Git repository utilities
│   │   ├── models.py          # GitCommit & GitMetadata Pydantic models
│   │   └── utils.py           # GitPython inspection (remotes, branches, commits, dirty state)
│   ├── __init__.py            # Package root & __version__ definition
│   └── main.py                # Primary Typer application instance & CLI entry point
├── scripts/                   # Helper scripts
│   ├── build-exe.cmd          # PyInstaller Windows build script
│   ├── cleanup.cmd            # Cleanup temporary build artifacts
│   └── run-help.ps1           # CLI help verification script
├── devtul.spec                # PyInstaller specification file
├── pyproject.toml             # Project configuration (uv_build, dependencies, scripts)
├── .flake8                    # Flake8 linter configuration
└── issues.md                  # Known issues tracking
```

---

## 3. Development Environment & Tooling

The project uses [uv](https://github.com/astral-sh/uv) as the package and environment manager with Python `>=3.13`.

### Dependency Synchronization

- **Core Dependencies:**
  ```powershell
  uv sync
  ```
- **Development Tooling (flake8, black, isort, pytest):**
  ```powershell
  uv sync --group dev
  ```
- **Optional Database Drivers (psycopg2, pymongo, mysql, pyodbc):**
  > **Note:** Database drivers are defined under `[project.optional-dependencies]`, NOT dependency groups.
  ```powershell
  # Install specific extra:
  uv sync --extra pg
  uv sync --extra all

  # Install everything (all extras + dev group):
  uv sync --all-extras --group dev
  ```

### CLI Execution

DevTul commands can be run through `uv`:
```powershell
# Run via root entry point
uv run dt --help
uv run dt tree
uv run dt md -f repo_docs.md
uv run dt ls --json
uv run dt reporter scan .
uv run dt reporter serve --port 9099

# Run via registered direct script entry points (defined in pyproject.toml):
uv run dt-tree
uv run dt-ls
uv run dt-find
uv run dt-md
uv run dt-new
```
> **Gotcha:** Running `uv run dt` without any subcommand will display the help text and exit with a non-zero exit code (`1` or `2`) because `no_args_is_help=True` is enabled on the top-level Typer application.

### Code Quality & Formatting

- **Linting:**
  ```powershell
  uv run flake8 src
  ```
  Linting configuration is in `.flake8` (`max-line-length = 150`, ignores `E501, W503, F541, F401`).
- **Formatting & Import Sorting:**
  ```powershell
  uv run black src
  uv run isort src
  ```

### Testing

- Run test suite:
  ```powershell
  uv run pytest
  ```
  *(Note: Tests directory `tests/` is configured in `pyproject.toml` under `[tool.pytest.coverage.run]` but currently requires test cases to be implemented).*

### Packaging (Windows Executable)

- Build standalone binary using PyInstaller:
  ```cmd
  scripts\build-exe.cmd --onefile
  ```
  Produces `dist\devtul.exe`.

---

## 4. Key Design Patterns & Conventions

### 1. The Standard File-Processing Pipeline
Most commands (`dt tree`, `dt md`, `dt ls`, `dt find`, `dt cp`) adhere to a structured multi-stage pipeline:
1. **Path Gathering:**
   - Git tracked files: `try_gather_all_git_tracked_paths(repo_path)`
   - All files: `gather_all_paths(root_path)`
2. **Default Ignores:**
   - Evaluated using `filter_gathered_paths_by_default_ignores(paths)` based on `IGNORE_PARTS` and `IGNORE_EXTENSIONS` in `devtul.core.constants`.
3. **Domain Model Wrapping:**
   - File paths wrapped into `FileResult(p, input_path)` objects to capture metadata, file size, content state (`EMPTY`, `NOT_EMPTY`), created/modified timestamps, and event history.
4. **Pattern & Option Filtering:**
   - Filter using `fnmatch` for `--match` and `--exclude` options.
   - Filter empty files via `FileContentStatus.EMPTY` unless `--empty` / `--no-empty` overrides.
5. **Output Generation:**
   - Formatted to Markdown, JSON, YAML, CSV, or formatted ASCII tree.

### 2. State & Data Persistence
- **User Data Directory:** `~/.devtul` (created automatically by `devtul.core.config`).
- **SQLite Database:** `~/.devtul/devtul_interface.db` managed via `sqlite-utils.Database`.
  - Table `database_hosts`: Stores connection profiles for Postgres, MySQL, MsSQL, MongoDB, SQLite.
  - Table `file_templates`: Stores user templates created via `dt new create`.
- **Cache File:** `.devtul_cache.json` stores file metadata and git commit history produced by `dt reporter scan`.

### 3. Templating
- Jinja2 templates are placed in `src/devtul/core/templates/`.
- Accessed via `devtul.core.config.JINJA_ENVIRONMENT` or `render_template(template_name, obj)` in `devtul.core.utils`.

---

## 5. Critical Gotchas & Known Technical Debt

1. **Path Separators & Tree Indentation on Windows (Bug in `issues.md`):**
   - In `devtul.core.file_utils.build_tree_structure(files, parent)`:
     ```python
     parts = file_path.split("/")
     ```
   - When paths use Windows backslashes `\`, `parts` is not split, causing directory items to render flat at the root level without indentation (`├── commands\__init__.py`).
   - **Rule:** Always ensure relative paths passed to `build_tree_structure` use forward slashes (e.g. `res.relative_path.as_posix()`).

2. **Undefined Symbol in `src/devtul/core/file_utils.py`:**
   - In `get_files_from_marked_directories(root, dir_marker, ...)` (line 311): calls `get_all_files(...)`, which was removed in an earlier refactor. Any agent working on this function must replace it with `gather_all_paths` + `filter_gathered_paths_by_default_ignores`.

3. **Subprocess Execution on Windows:**
   - In `devtul.core.file_utils.try_gather_all_git_tracked_paths`, `subprocess.run(["git", ...], shell=True)` is used for Windows compatibility. Ensure `shell=True` or explicit path resolution is respected for cross-platform stability.
   - Safe directory handling is implemented: git may return `dubious ownership` errors on Windows when repositories belong to different user accounts.

4. **Version Number Inconsistencies:**
   - `pyproject.toml`: `0.1.13`
   - `src/devtul/__init__.py`: `0.1.11`
   - `src/devtul/main.py`: `0.1.5`
   - When bumping versions, ensure all three locations are synchronized.

---

## 6. Guidelines for AI Agents

When working on DevTul:
- **Adding Commands:**
  1. Implement command logic in `src/devtul/commands/<name>.py`.
  2. Export in `src/devtul/commands/__init__.py`.
  3. Register on the `app` instance in `src/devtul/main.py`.
  4. If standalone execution is desired, add entrypoint in `pyproject.toml` under `[project.scripts]`.
- **Code Style:**
  - Preserve all existing docstrings and comments.
  - Run `uv run flake8 src` to verify no lint regressions before finishing.
  - Maintain type annotations compatible with Python 3.13.
- **Paths:**
  - Prefer `pathlib.Path` over raw strings for file system operations.
  - Always use `.as_posix()` when converting paths for cross-platform output, tree rendering, or JSON serialization.

