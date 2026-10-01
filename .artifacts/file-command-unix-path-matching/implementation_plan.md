# Implementation Plan: Class-Based FileCommand Abstraction, Input/Output Modeling & Unix-Like Path Matching

- **Session Slug:** `file-command-unix-path-matching`
- **GitHub Issue:** [#15](https://github.com/Willmo103/devtul/issues/15)
- **Draft Pull Request:** [#16](https://github.com/Willmo103/devtul/pull/16)
- **Status:** Awaiting User Review & Approval (Updated with Output Modeling & Future-Ready Templating Architecture)

---

## 1. Problem Statement & Root Cause Analysis

### Identified Failure Scenarios

1. **Windows Separators & Leading `./` or `.\` in `-e` / `--exclude` and `-m` / `--match`:**
   - **Command:** `dt md -m *.py -e .\tests\test_migration_and_paths.py -e .\tests\test_version_bump.py`
   - **Cause:** Currently, `devtul.commands.markdown` (and `tree`, `ls`, `find`) tests exclusions using:
     ```python
     any(fnmatch.fnmatch(res.relative_path.as_posix(), e) for e in exclude)
     ```
     `res.relative_path.as_posix()` produces POSIX format (`tests/test_migration_and_paths.py`). On Windows, passing `.\tests\test_migration_and_paths.py` preserves literal backslashes and `.\` in `e`. Because `fnmatch` treats `\` as a regular character (or literal) rather than a path separator, and expects an exact string match without leading `.\`, `fnmatch` returns `False`, causing the files to be included instead of excluded.

2. **Directory-Level Exclusions (`-e tests/` or `-e tests`):**
   - **Cause:** `fnmatch` matches the *entire* path string against the pattern. If a user passes `-e tests/` or `-e tests`, `fnmatch("tests/foo.py", "tests/")` is `False`. In standard Unix/Git semantics, specifying a directory name or trailing slash must match all files contained within that directory hierarchy.

3. **Shell Wildcard Expansion on Windows (`-e *test*`):**
   - **Cause:** When a user passes `-e *test*` or `-e "*test*"` in PowerShell or cmd, the shell expands `*test*` against existing directories in the current folder, passing `tests` as the argument to Typer. Combined with the lack of directory matching in `fnmatch`, this pattern fails to match files under `tests/`.

4. **Ad-hoc Outputs & Duplicated Logic Across Commands:**
   - File gathering, default-ignore filtering, FileResult instantiation, match filtering, exclude filtering, and empty-status filtering are duplicated across `markdown.py`, `tree.py`, `list_files.py`, and `find.py`.
   - Command outputs are directly printed or constructed as unmodeled strings, making multi-format rendering (Markdown, JSON, YAML, future DOCX/PDF), templating, and speech synthesis (`--spk`, `dt speak`) brittle and non-reusable.

5. **Lack of Pattern Debug Visibility:**
   - Users have no way to inspect why a file was included or excluded without a `--debug` option.

---

## 2. Architectural Design: Standardizing Command Inputs & Outputs

```
+---------------------------------------------------------------------------------------+
|                                    BaseCommand (ABC)                                  |
|   - name: str                                                                         |
|   - help: str                                                                         |
|   - @property @abstractmethod usage -> str                                            |
|   - @property @abstractmethod examples -> list[str]                                   |
|   - get_formatted_help() -> str (synthesizes rich Typer docstrings)                   |
|   - execute(...) -> CommandResult                                                     |
+-------------------------------------------+-------------------------------------------+
                                            |
                                            v
+---------------------------------------------------------------------------------------+
|                                    FileCommand (ABC)                                  |
|   [Input Modeling]                                                                    |
|   - FileFilterOptions: path, match, exclude, git, include_empty, no_ignore, debug     |
|   - gather_and_filter_files(...) -> (list[FileResult], FilterMetrics)                 |
|   - UnixPathMatcher: directory matching, globstar, Windows separator normalization    |
|                                                                                       |
|   [Output Modeling]                                                                   |
|   - execute(...) -> FileCommandResult (Pydantic Model)                                |
|     * root_path: FilePath                                                             |
|     * files: list[FileResult] (interop with BaseTextFile, BaseFileStat)               |
|     * render(format='text'|'md'|'json'|'yaml'|'tree') -> str                          |
|     * to_speech_summary() -> str (for TTS / --spk pipeline)                           |
+-------------------------------------------+-------------------------------------------+
                                            |
        +------------------+----------------+------------------+------------------+
        |                  |                                   |                  |
        v                  v                                   v                  v
+---------------+  +------------------+             +--------------------+  +---------------+
|  TreeCommand  |  | MarkdownCommand  |             |  ListFilesCommand  |  |  FindCommand  |
|  (dt tree)    |  | (dt md / repr)   |             |  (dt ls)           |  |  (dt find)    |
| -> TreeResult |  | -> MarkdownResult|             |  -> ListingResult  |  | -> FindResult |
+---------------+  +------------------+             +--------------------+  +---------------+
```

### A. Input Modeling & Parameter Standardization
1. **`FileFilterOptions(BaseModel)`:**
   - Encapsulates CLI inputs: `path: Path`, `match: list[str]`, `exclude: list[str]`, `git: bool`, `include_empty: bool`, `no_ignore: bool`, `debug: bool`.
   - Provides clean validation and enables direct Python programmatic usage beyond CLI flags.
2. **`UnixPathMatcher`:**
   - Normalizes Windows separators (`\` $\rightarrow$ `/`) and strips leading `./` / `.\`.
   - Resolves absolute/relative paths against target repository root.
   - Directory-level exclusions (`tests/` and bare `tests`).
   - Globstar (`**`), wildcards (`*test*`, `*.py`), and basename matching.
   - Debug tracing stream to `stderr` when `debug=True`.

### B. Output Modeling via Pydantic (`CommandResult` & `FileCommandResult`)
1. **`CommandResult(BaseModel)` & `FileCommandResult(CommandResult)` in `devtul.core.models`:**
   - Holds structured results: `root_path: FilePath`, `files: list[FileResult]`, `metrics: FilterMetrics`.
   - **Multi-Format Rendering:**
     - `.render(format="md" | "json" | "yaml" | "tree" | "csv" | "text")`
     - Decouples computation from formatting; paves the way for upcoming format converters (`dt repr`, `--fmt docx|pdf|md`).
   - **TTS & Speech Integration:**
     - `.to_speech_summary() -> str`: Generates a natural-language audible summary of the command's outcome (e.g. *"DevTul tree scanned 42 files across 6 directories in devtul"*), ready for direct piping into `dt speak` or future `--spk` flags.
   - **Jinja2 Templating Ready:**
     - Provides clean Pydantic dictionaries/objects directly into Jinja2 templates (`render_template`).
2. **Specialized Result Subclasses:**
   - `TreeResult(FileCommandResult)`: contains formatted ASCII tree and structured hierarchy nodes.
   - `MarkdownResult(FileCommandResult)`: contains `RepoMarkdownHeader`, file sections, and rendered markdown text.
   - `ListingResult(FileCommandResult)`: contains tabular file listings with CSV, JSON, and YAML export.
   - `FindResult(FileCommandResult)`: contains search term, matches per file, line numbers, and content.

### C. Class-Based Command Hierarchy & Typer Integration
1. **`BaseCommand(ABC)`:**
   - Requires `@property @abstractmethod usage -> str` and `@property @abstractmethod examples -> list[str]`.
   - Auto-generates comprehensive Typer docstrings with standardized `Usage:` and `Examples:` sections.
2. **Backward Compatibility:**
   - Module functions in `devtul.commands` (`markdown`, `tree`, `ls`, `find`) and console scripts in `pyproject.toml` (`dt-tree`, `dt-ls`, `dt-md`, `dt-find`) will delegate cleanly to the class instances.

---

## 3. Implementation Tasks

- [ ] **Task 1: Implement `UnixPathMatcher` (`src/devtul/core/path_matcher.py`)**
  - Implement pattern normalization (Windows separators, leading `./`, absolute path resolution).
  - Implement directory matching (`tests/` and component match `tests`).
  - Implement glob and globstar matching (`PurePosixPath.match`, `fnmatch`).
  - Implement debug callback / tracing.
  - Export in `src/devtul/core/__init__.py`.

- [ ] **Task 2: Define Output Models in `src/devtul/core/models.py`**
  - Define `FilterMetrics`, `FileFilterOptions`.
  - Define `CommandResult` and `FileCommandResult`.
  - Implement `.render(format=...)` and `.to_speech_summary()`.
  - Define specialized subclasses: `TreeResult`, `MarkdownResult`, `ListingResult`, `FindResult`.

- [ ] **Task 3: Implement Class-Based Hierarchy (`src/devtul/core/command.py`)**
  - Create `BaseCommand(ABC)` with abstract `usage`, `examples`, and automated help synthesis.
  - Create `FileCommand(BaseCommand)` with shared options (`path`, `match`, `exclude`, `git`, `include_empty`, `no_ignore`, `debug`).
  - Implement `FileCommand.gather_and_filter_files()` using `UnixPathMatcher`.
  - Implement debug logging to `stderr`.

- [ ] **Task 4: Refactor File Commands to Subclass `FileCommand` & Return Output Models**
  - Refactor `src/devtul/commands/tree.py` -> `TreeCommand` (returns `TreeResult`).
  - Refactor `src/devtul/commands/markdown.py` -> `MarkdownCommand` (returns `MarkdownResult`).
  - Refactor `src/devtul/commands/list_files.py` -> `ListFilesCommand` (returns `ListingResult`).
  - Refactor `src/devtul/commands/find.py` -> `FindCommand` (returns `FindResult`).
  - Add `--debug` flag to each command.
  - Maintain function backward-compatibility wrappers in each module.

- [ ] **Task 5: Update Command Registration & Entrypoints**
  - Update `src/devtul/main.py` to register command instances.
  - Verify `dt --help`, `dt md --help`, `dt tree --help`, etc. display standardized `Usage` and `Examples`.

- [ ] **Task 6: Comprehensive Test Suite & Artifact Archiving**
  - Create `tests/test_path_matcher.py` testing:
    - Exact paths with Windows separators (`.\tests\foo.py`)
    - Directory patterns (`tests/` and `tests`)
    - Wildcard patterns (`*test*`, `*.py`, `src/**/*.py`)
    - Root-relative absolute path exclusions
  - Create `tests/test_command_io_models.py` testing:
    - Input options parsing and validation
    - `FileCommandResult` format rendering and speech summaries (`to_speech_summary()`)
    - `BaseCommand` and `FileCommand` execution with `--debug` feedback
  - Run full test suite (`uv run pytest`) and archive output to `.artifacts/file-command-unix-path-matching/impl_test_run_1.log`.
  - Run linter (`uv run flake8 src tests scripts`).

- [ ] **Task 7: User Acceptance Testing (UAT)**
  - Validate verbatim user command:
    `dt md -m *.py -e .\tests\test_migration_and_paths.py -e .\tests\test_version_bump.py` (verify test files excluded).
  - Validate directory exclusion:
    `dt ls -e tests/` and `dt ls -e tests` (verify no files under `tests/` appear).
  - Validate wildcard exclusion:
    `dt ls -m *.py -e *test*` (verify `tests/` files excluded).
  - Validate debug flag:
    `dt ls -m *.py -e tests/ --debug` (verify stderr shows debug traces).
  - Archive UAT logs to `.artifacts/file-command-unix-path-matching/uat_test_run_1.log`.

---

## 4. Verification & Validation Protocol

| Scenario | Command | Expected Result |
| :--- | :--- | :--- |
| **Exact Path Exclusion (Windows)** | `dt md -m *.py -e .\tests\test_migration_and_paths.py -e .\tests\test_version_bump.py` | Markdown output does **not** include either test file. |
| **Directory Exclusion (Trailing Slash)** | `dt ls -e tests/` | File listing contains zero files from `tests/`. |
| **Directory Exclusion (Bare Name)** | `dt ls -e tests` | File listing contains zero files from `tests/`. |
| **Wildcard Exclusion** | `dt ls -m *.py -e *test*` | Excludes files in `tests/` and any file matching `*test*`. |
| **Debug Flag Feedback** | `dt ls -e tests/ --debug` | Prints exclusion reasons to stderr. |
| **Speech Summary Verification** | Python test verifying `result.to_speech_summary()` | Returns audible natural-language summary ready for TTS. |
| **Output Model Serialization** | Python test verifying `result.model_dump_json()` | Full structured output serialized to JSON cleanly. |
| **Command Help Standardization** | `dt md --help`, `dt tree --help` | Shows standard `Usage:` and `Examples:` sections generated from class properties. |
| **Regression Testing** | `uv run pytest` | All existing 13 tests plus new tests pass (0 failures). |
| **Linter Cleanliness** | `uv run flake8 src tests scripts` | 0 errors. |
