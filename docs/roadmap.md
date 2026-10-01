# DevTul Development Roadmap & Candidate Features

This document provides a centralized catalog of planned features, candidate extensions cherrypicked from developer scripts, and architectural enhancements under evaluation for **DevTul**.

---

## 1. Candidate Development Features (Active Backlog)

The following candidates represent modular CLI capabilities evaluated and tracked in the issue tracker. Each candidate is designed to integrate seamlessly with DevTul's core abstractions (`FileCommand`, `StringCommand`, and `UnixPathMatcher`).

### 1.1. SQLite Database Merger (`dt db merge`)
* **Tracking Issue:** [#19](https://github.com/Willmo103/devtul/issues/19)
* **Origin:** `concat_sqlite_dbs.py` from local developer tool scripts.
* **Proposed Command:** `dt db merge <source_dbs...> -o <destination.db>`
* **Description:**
  A database utility to concatenate and reconcile multiple SQLite databases into a unified destination database.
* **Key Capabilities:**
  - Automated schema reconciliation via `PRAGMA table_info`.
  - Dynamic schema migration (`ALTER TABLE ... ADD COLUMN ... TEXT`) when columns exist in source but not destination.
  - Automatic creation of missing table definitions.
  - Conflict-free record insertion with `INSERT OR IGNORE` to bypass primary key collisions.
  - Rich-formatted migration statistics and progress bars.

---

### 1.2. Asynchronous Repository File Watcher (`dt watch`)
* **Tracking Issue:** [#20](https://github.com/Willmo103/devtul/issues/20)
* **Origin:** `watch_src.py` & `file_watcher.py`
* **Proposed Command:** `dt watch [path] --run "<command>"`
* **Description:**
  A continuous filesystem monitor that watches repository directories for modifications and triggers automated actions or DevTul pipelines.
* **Key Capabilities:**
  - Fast, asynchronous event detection via `watchfiles` or `watchdog`.
  - Integration with `UnixPathMatcher` to respect `--match`, `--exclude`, and default repository ignores.
  - Debouncing to avoid repeated triggers on multi-file saves.
  - Automatic execution of arbitrary commands (e.g. `dt watch --run "dt rpr -f repo.docx"` or `dt watch --run "pytest"`).
  - Optional notification dispatch (e.g. Gotify or webhook).

---

### 1.3. Developer HTTP Client & Request History (`dt req`)
* **Tracking Issue:** [#21](https://github.com/Willmo103/devtul/issues/21)
* **Origin:** `postman_cli.py`
* **Proposed Command:** `dt req <URL> [-X METHOD] [-H HEADER] [-d DATA]`
* **Description:**
  A lightweight, terminal-native HTTP client optimized for rapid API testing and debugging without switching out of the shell.
* **Key Capabilities:**
  - Supports standard HTTP methods (`GET`, `POST`, `PUT`, `DELETE`, `PATCH`, `HEAD`).
  - Rich syntax-highlighted response bodies (JSON, HTML, XML) and status metadata (latency, status code, size).
  - Persistent request history stored in SQLite (`~/.devtul/devtul_interface.db`) with deduplication.
  - Request replay and collections support.

---

### 1.4. PEP 723 Single-File Python Script Generator (`dt new script`)
* **Tracking Issue:** [#22](https://github.com/Willmo103/devtul/issues/22)
* **Origin:** `uv_script_add.cmd` & `uv_script_create.cmd`
* **Proposed Command:** `dt new script <filename.py> [--dep <pkg>]...`
* **Description:**
  Extends `dt new` to scaffold self-contained single-file Python scripts using PEP 723 inline script metadata that can be directly executed with `uv run script.py`.
* **Key Capabilities:**
  - Scaffolds PEP 723 script headers with specified Python version and inline dependencies:
    ```python
    # /// script
    # requires-python = ">=3.11"
    # dependencies = [
    #   "requests",
    #   "rich",
    # ]
    # ///
    ```
  - Subcommand `dt new script add <filename.py> <packages...>` to append dependencies safely.
  - Integration with DevTul template storage.

---

### 1.5. Local Neural Speech Synthesis (`dt spk`)
* **Tracking Issue:** [#23](https://github.com/Willmo103/devtul/issues/23)
* **Origin:** `piper_cli.py` & voice roadmap
* **Proposed Command:** `dt spk [TEXT]`, `cat output.txt | dt spk`, or `dt rpr . --spk`
* **Description:**
  A local, neural text-to-speech audio synthesis utility built with Piper TTS and `onnxruntime`, allowing command summaries, logs, or piped streams to be spoken aloud.
* **Key Capabilities:**
  - Direct synthesis from command-line arguments or piped standard input (`stdin`).
  - Subcommands or flags to download and cache local ONNX voice models in `~/.devtul/models/`.
  - Configurable rate, pitch, volume, and multi-speaker indexing.
  - Integration flag (`--spk`) across DevTul file and stream commands for audible task completion alerts.

---

## 2. Legacy Maintenance & Quality Tracking

| Issue | Title | Status | Notes |
| :--- | :--- | :--- | :--- |
| [#4](https://github.com/Willmo103/devtul/issues/4) | CLI Argument handling needs improvement | Resolved in v0.4.0+ | Unified scanning logic under `FileCommand` and `UnixPathMatcher`. |
| [#5](https://github.com/Willmo103/devtul/issues/5) | Tree command does not render hierarchy on `--no-git` | Resolved in v0.4.0+ | Fixed POSIX path normalization across Windows backslashes. |

---

## 3. Future Architectural Explorations

1. **Direct PDF Output in `dt rpr`:**
   - Currently, `dt rpr --format pdf` converts structured Markdown to HTML/DOCX before generating PDF. A native, headless rendering backend (via WeasyPrint or docx2pdf) will enable zero-external-dependency PDF compilation.
2. **Interactive TUI Exploration:**
   - Explore Textual-based interactive views for `dt tree` and `dt reporter` for live terminal navigation.
3. **Shell Completion Scaffolding:**
   - Automated generation of PowerShell, Bash, and Zsh completion scripts installed directly to user configuration paths.
