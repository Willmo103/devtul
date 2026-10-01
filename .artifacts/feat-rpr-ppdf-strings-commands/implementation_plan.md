# Implementation Plan: 'rpr' Representation Suite, 'ppdf' PDF Viewer, 'strings', and Cherrypicking Roadmap

- **Session Slug:** `feat-rpr-ppdf-strings-commands`
- **GitHub Issue:** [#17](https://github.com/Willmo103/devtul/issues/17)
- **Draft Pull Request:** [#18](https://github.com/Willmo103/devtul/pull/18)
- **Status:** Awaiting User Review & Approval

---

## 1. Problem Statement & User Requirements

1. **Evolution from `md` to `rpr` (Representation Suite):**
   - The existing `dt md` command only outputs raw Markdown files.
   - Users need rich document formats including Microsoft Word (`.docx`) with styled code blocks, tables, callouts, and bumped headers, based on the established [.agents/docs/to_docx_processor.py](file:///c:/src/devtul/.agents/docs/to_docx_processor.py).
   - Users need a `rpr clone` subcommand that can clone remote Git repositories into a temporary (or custom) directory, generate the complete flattened representation, and output the document.

2. **PDF Cat & Line Inspection (`ppdf` / `print-pdf`):**
   - Need a fast, terminal-friendly way to inspect and `cat` PDF documents using `pdfplumber`.
   - Need line filtering and inspection tools: `--head`, `--tail`, `--grep`, `--sed`, `--numbered`, and `--lines-with` (with Rich color highlighting).

3. **Unix-Style `strings` Command (`str` / `strings`):**
   - Need a native cross-platform `strings` command to extract printable character sequences from binary files, executables, or raw text files, with configurable minimum length (`-n`, `--min-len`).

4. **`StringCommand` Abstraction:**
   - Standardize text/stream processing options across string-based CLI commands (`ppdf`, `strings`, and future commands) into a reusable base class:
     - `--head <int>`: Extract first N lines.
     - `--tail <int>`: Extract last N lines.
     - `--grep <PATTERN: str>`: Filter lines matching regex or literal string.
     - `--sed <EXPR: str>`: Sed-like pattern substitution (`s/find/replace/g`).
     - `--numbered` / `-n`: Prepend 1-indexed line numbers.
     - `--lines-with <TERM: str>`: Display matching lines with line numbers and highlighted terms using Rich.

---

## 2. Cherrypicking Analysis from `Callable` Repository

A comprehensive deep-dive into [.agents/docs/callable_repo_(code that i have in my PATH).md](file:///c:/src/devtul/.agents/docs/callable_repo_%28code%20that%20i%20have%20in%20my%20PATH%29.md) identified several key utilities and architectural patterns that can be cherrypicked into DevTul:

| Source File in `Callable` | Core Capabilities & Architecture | DevTul Integration Target & Value |
| :--- | :--- | :--- |
| **`concat_sqlite_dbs.py`** | Multi-database SQLite concatenator. Analyzes table schemas via `PRAGMA table_info`, reconciles schema discrepancies by dynamically executing `ALTER TABLE ... ADD COLUMN ... TEXT`, copies `CREATE TABLE` definitions for missing tables, and bulk inserts records with `INSERT OR IGNORE` to prevent duplicate primary key violations. | **`dt db merge` / `dt db concat`**: Extends `src/devtul/commands/db.py` to allow combining multiple SQLite databases into a consolidated target database. Extremely valuable for aggregating telemetry, report caches, or dataset fragments. |
| **`py-scripts/watch_src.py` & `file_watcher.py`** | Async file system monitor utilizing `watchfiles.awatch` and `watchdog`. Dispatches configurable action handlers (webhook, file copy, Gotify notification, custom shell script) on file creation, modification, or deletion. Includes config persistence in `~/.backup_config.json`. | **`dt watch`**: Native repository watcher. Can monitor repository source trees (filtered using DevTul's `UnixPathMatcher`) and trigger test suites (`dt watch --run "pytest"`), documentation rebuilds (`dt watch --run "dt rpr"`), or quality checks on save. |
| **`postman_cli.py`** | Terminal-based HTTP client powered by Typer, `requests`, and Rich. Displays colored request summaries, execution latency, response headers, and syntax-highlighted JSON bodies. Persists request/response history in `~/.postman_cli_history.json` (TinyDB) with deduplication. | **`dt req` / `dt http`**: Embedded developer HTTP client. Enables fast API verification and curl-like functionality without leaving the CLI, storing history alongside other DevTul profiles. |
| **`run_checks_on_save.py`** | Continuous code quality daemon configuring `black`, `flake8`, `isort`, and `mypy` with `.watch_ignore` and `pyproject.toml` support. | **`dt check --watch`**: Integrated lint/format runner on file modifications. |
| **`uv_script_add.cmd` & `uv_script_create.cmd`** | Shell scripts automating PEP 723 inline script metadata management (`uv init --script` and `uv add --script`). | **`dt new script <name> --dep <pkg>`**: Enhances DevTul's `dt new` template engine to scaffold standalone, self-contained single-file Python scripts with uv inline dependencies. |
| **`piper_cli.py`** | Script entrypoint reserved for Piper TTS (`piper-tts`, `onnxruntime`). | **`dt spk` / `dt speak`**: User-requested voice synthesizer command to pipe text or CLI output directly to local neural speech audio, preserving `piper-tts` and `onnxruntime`. |
| **`create_models.py` & `sql_formatter.ps1`** | Schema extraction via `sqlite-utils schema`, system prompt templates for DDL translation (SQLite -> PostgreSQL / MySQL), and automated SQLAlchemy/Pydantic model generation. | **`dt db schema --codegen` / `dt sql translate`**: Future LLM-assisted schema and model generator under the database suite. |

---

## 3. Architectural Design

```
BaseCommand (ABC)
│   ├── FileCommand (dt tree, dt ls, dt find, dt rpr)
│   │   └── RprCommand (dt rpr)
│   │       ├── Subcommand: rpr clone <url>
│   │       ├── Formats: md, docx, text
│   │       └── Processor: DocxProcessor (adapted from to_docx_processor.py)
│   │
│   └── StringCommand (ABC in devtul.core.command)
│       │   # Standard line pipeline: head, tail, grep, sed, numbered, lines-with
│       ├── process_lines(lines: list[str], options: StringFilterOptions) -> list[str]
│       │
│       ├── PrintPdfCommand (dt ppdf, dt print-pdf)
│       │   └── backend: pdfplumber
│       │
│       └── StringsCommand (dt str, dt strings)
│           └── printable sequence extractor (ASCII & UTF-8)
```

### A. The `StringCommand` Abstraction (`src/devtul/core/command.py`)
- Defines `StringFilterOptions(BaseModel)`:
  - `head: Optional[int] = None`
  - `tail: Optional[int] = None`
  - `grep: Optional[str] = None`
  - `sed: Optional[str] = None`
  - `numbered: bool = False`
  - `lines_with: Optional[str] = None`
- Defines `StringCommand(BaseCommand)`:
  - Implements `apply_sed(text: str, expr: str) -> str` supporting `s/pattern/replacement/flags`.
  - Implements `process_lines(lines: list[str], options: StringFilterOptions) -> list[str]`.
  - Implements Rich syntax highlighting for `--lines-with` using `rich.console.Console`.

### B. The `ppdf` / `print-pdf` Command (`src/devtul/commands/pdf.py`)
- Uses `pdfplumber` to open PDF files, extract page text, and feed line lists into `StringCommand.process_lines()`.
- Supports reading specific page ranges (`--pages 1-5`, `--pages 3`).
- Registered as both `dt ppdf` and `dt print-pdf` with standalone console script `dt-ppdf`.

### C. The `str` / `strings` Command (`src/devtul/commands/strings_cmd.py`)
- Reads raw binary or text files and yields printable ASCII and UTF-8 strings of at least `--min-len` (default: 4).
- Passes extracted strings through `StringCommand.process_lines()`.
- Registered as `dt str` and `dt strings` with standalone console script `dt-str`.

### D. The `rpr` Command & `rpr clone` Subcommand (`src/devtul/commands/repr_cmd.py`)
- **`dt rpr [PATH] [OPTIONS]`:**
  - Subclasses `FileCommand`, inheriting all Unix-like path filtering (`-m`, `-e`, `--git`, `--debug`).
  - Output formats via `--format` / `-fmt`:
    - `md`: Markdown generation (compatible with existing `dt md`).
    - `docx`: High-fidelity Word document generation using `DocxProcessor` integrated from `.agents/docs/to_docx_processor.py` (with styled code blocks, borders, tables, bumped headings).
    - `text`: Plain text representation.
  - Shortcut flags: `--docx`, `--md`.
- **`dt rpr clone <REPO_URL> [OPTIONS]`:**
  - Clones remote repository into a temporary directory (via `tempfile.TemporaryDirectory`) or specified `--dest`.
  - Runs `rpr` generation on the cloned repo.
  - Automatically cleans up temporary files after generation.
- Registered as `dt rpr` with standalone script `dt-rpr`.

---

## 4. Implementation Tasks

- [ ] **Task 1: Add Dependencies to `pyproject.toml`**
  - Add `python-docx>=1.1.2`, `markdown>=3.7`, `beautifulsoup4>=4.12.3`, `pdfplumber>=0.11.5`.
  - Run `uv sync` to update `uv.lock`.

- [ ] **Task 2: Implement `StringCommand` & `StringFilterOptions` (`src/devtul/core/command.py`)**
  - Define `StringFilterOptions` model.
  - Implement sed parser (`s/pattern/replacement/flags`).
  - Implement `process_lines` with head, tail, grep, sed, numbered lines, and Rich term highlighting.

- [ ] **Task 3: Implement `ppdf` / `print-pdf` Command (`src/devtul/commands/pdf.py`)**
  - Implement `PrintPdfCommand(StringCommand)` using `pdfplumber`.
  - Add page range parsing (`--pages`).
  - Integrate with `StringFilterOptions`.

- [ ] **Task 4: Implement `str` / `strings` Command (`src/devtul/commands/strings_cmd.py`)**
  - Implement `StringsCommand(StringCommand)` for binary printable sequence extraction.
  - Add `--min-len` / `-n` option (default 4).
  - Integrate with `StringFilterOptions`.

- [ ] **Task 5: Implement `DocxProcessor` & `rpr` Command (`src/devtul/commands/repr_cmd.py`)**
  - Adapt `.agents/docs/to_docx_processor.py` into `devtul.core.docx_processor`.
  - Implement `RprCommand(FileCommand)` supporting `--format` (`md`, `docx`, `text`).
  - Implement `rpr clone` subcommand for remote git URL cloning and representation.

- [ ] **Task 6: Register Commands & Standalone Scripts**
  - Register in `src/devtul/main.py`: `app.command(name="rpr")`, `app.command(name="ppdf")`, `app.command(name="str")`, etc.
  - Add script entry points in `pyproject.toml`: `dt-rpr`, `dt-ppdf`, `dt-str`.

- [ ] **Task 7: Test Suite & Artifact Archiving**
  - Unit tests for `StringCommand` (head, tail, grep, sed, numbered, highlighting).
  - Unit tests for `DocxProcessor` and `rpr` formats.
  - Unit tests for `strings` command.
  - Unit tests for `rpr clone` in isolated mock temp directory.
  - Run `uv run pytest -v` and archive to `impl_test_run_1.log`.
  - Run `uv run flake8 src tests scripts`.

- [ ] **Task 8: User Acceptance Testing (UAT)**
  - Validate `dt ppdf` on a sample PDF.
  - Validate `dt str` on a binary file with `--grep` and `--head`.
  - Validate `dt rpr -fmt docx -f repo.docx` and check generated `.docx`.
  - Validate `dt rpr clone <url>`.
  - Archive to `uat_test_run_1.log` and author `walkthrough.md`.

---

## 5. Verification Protocol

| Feature | Verification Command | Expected Outcome |
| :--- | :--- | :--- |
| **String Filtering (Head/Tail/Grep)** | `dt str <binary> --head 10 --grep "import"` | Outputs first 10 printable strings matching pattern. |
| **Sed Substitution** | `dt str <binary> --sed "s/devtul/REPLACED/g"` | Substitutes occurrences in stream output. |
| **Line Numbering & Highlighting** | `dt ppdf sample.pdf --numbered --lines-with "title"` | Lines printed with line numbers and term highlighted. |
| **Docx Representation** | `dt rpr . --format docx -f output.docx` | Produces valid `.docx` document with styled code blocks and tables. |
| **Clone & Represent** | `dt rpr clone <repo_url> -f clone_repr.md` | Clones to temp dir, generates representation, cleans up temp dir. |
| **Regression Testing** | `uv run pytest` | All existing 28 tests + new tests pass (0 failures). |
| **Linter Cleanliness** | `uv run flake8 src tests scripts` | 0 errors. |
