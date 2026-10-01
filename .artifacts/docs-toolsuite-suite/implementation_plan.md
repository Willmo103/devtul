# Implementation Plan: Comprehensive DevTul Toolsuite Documentation & Example Suite

- **Session Slug:** `docs-toolsuite-suite`
- **GitHub Issue:** [#24](https://github.com/Willmo103/devtul/issues/24)
- **Draft Pull Request:** [#25](https://github.com/Willmo103/devtul/pull/25)
- **Status:** Awaiting User Review & Approval

---

## 1. Problem Statement & User Goal

DevTul (`dt`) has grown into a powerful, multifaceted developer toolsuite with capabilities spanning:
- High-fidelity repository representation to Word (`.docx`), Markdown, and plain text (`dt rpr`, `dt rpr clone`)
- Cross-platform Unix-style string stream filtering and binary inspection (`dt str`, `dt ppdf`, `--grep`, `--sed`, `--lines-with`)
- Advanced repository discovery and format exports (`dt tree`, `dt ls --json|yaml|csv`, `dt find`, `dt empty`, `dt find-folder`)
- Database connection management across PostgreSQL, MySQL, MSSQL, MongoDB, and SQLite (`dt db`)
- Local SQLite-backed template scaffolding (`dt new`)
- Interactive repository HTML inspection dashboards (`dt reporter scan`, `dt reporter serve`)
- File copying and zip archiving (`dt cp`)

However, the repository documentation (`README.md`) is severely outdated (dating back to v0.1.11), and lacks a structured guide with concrete, real-world examples. Furthermore, future development candidates (Issues #19–#23) need a centralized, organized roadmap document.

---

## 2. Proposed Documentation Architecture

```
devtul/
├── README.md                      # Modernized, comprehensive quickstart, cheatsheet & command matrix
├── mkdocs.yml                     # MkDocs site configuration with navigation & theme setup
└── docs/
    ├── index.md                   # Getting Started, Installation, and Architecture Overview
    ├── commands/
    │   ├── repr.md                # dt rpr (docx, md, text, and rpr clone)
    │   ├── inspection.md          # dt tree, dt ls (formats), dt find, dt empty, dt find-folder
    │   ├── strings.md             # dt str, dt ppdf, and StringCommand stream pipeline (sed/grep/head/tail/lines-with)
    │   ├── database.md            # dt db (connection profiles & session management)
    │   ├── templates.md           # dt new (template creation, SQLite storage, scaffolding)
    │   ├── reporter.md            # dt reporter (scan cache & interactive HTML dashboard)
    │   └── copy.md                # dt cp (file copying & zip archiving)
    ├── guides/
    │   └── path-filtering.md      # Unix-style path matching guide (-m, -e, globstar, debugging)
    └── roadmap.md                 # Centralized development candidates tracker (Issues #19–#23, #4, #5)
```

---

## 3. Detailed Component Plan

### A. Modernized Root `README.md`
- **Header & Badges:** Version `v0.5.0`, Python `>=3.13`, MIT License, CI/Release status.
- **Quick Installation:** `uv tool install`, `pip install`, and standalone binary download from GitHub Releases.
- **Command Matrix & Cheatsheet:** Summary table mapping subcommands, standalone script aliases (`dt-tree`, `dt-rpr`, `dt-ppdf`, `dt-str`, etc.), and primary flags.
- **Top 5 High-Impact Use Cases:**
  1. *Convert a whole repo into a styled Word document for client review:* `dt rpr . -f project_spec.docx`
  2. *Audit a remote GitHub repo without local cloning overhead:* `dt rpr clone <URL> -f audit.docx`
  3. *Extract printable strings from an executable with regex filtering:* `dt str app.exe --grep "https://" --head 10`
  4. *Inspect a PDF directly in your terminal with pattern substitution:* `dt ppdf report.pdf --grep "Total" --sed "s/Total/FINAL/g"`
  5. *Export filtered git repository structure to JSON/YAML for automation:* `dt ls -m "*.py" -e "tests/*" --json`

### B. Command Reference Documentation (`docs/commands/`)
- **`repr.md`:** Detailed explanation of Word `.docx` styling (Consolas code blocks with `#F6F8FA` shading and `#D0D7DE` border, bumped header sizes, table formatting, frontmatter tables), format options (`md`, `docx`, `text`), and `rpr clone` with temporary sandbox vs `--dest`.
- **`strings.md`:** Deep-dive into `dt str` and `dt ppdf`, explaining `StringCommand` stream options: `--head`, `--tail`, `--grep`, `--sed` (`s/find/replace/flags` with custom delimiters), `--numbered`, and `--lines-with` (Rich highlighting).
- **`inspection.md`:** Explains `dt tree`, `dt ls` (`--json`, `--yaml`, `--csv`), `dt find` (keyword searching), `dt empty` (`files`, `dirs`), and `dt find-folder` with marker matching.
- **`database.md`:** Explains `dt db add`, `dt db ls`, `dt db test`, `dt db conn`, interactive wizards, and storage in `~/.devtul/devtul_interface.db`.
- **`templates.md`:** Explains `dt new create`, `dt new ls`, `dt new edit`, `dt new make`, and template parameters.
- **`reporter.md`:** Explains `dt reporter scan` (caching metadata to `.devtul_cache.json`) and `dt reporter serve` (serving HTML dashboard).
- **`copy.md`:** Explains `dt cp` with destination directory and `--archive` zip packaging.

### C. Guides & Roadmap
- **`guides/path-filtering.md`:** Clarifies how Unix-style path matching works, matching against filenames, relative paths, directory prefixes (`tests/`), globstars (`**/*.py`), and how to use `--debug`.
- **`roadmap.md`:** Complete catalog of future development candidates:
  - Issue [#19](https://github.com/Willmo103/devtul/issues/19): `dt db merge` (SQLite merger CLI from `concat_sqlite_dbs.py`)
  - Issue [#20](https://github.com/Willmo103/devtul/issues/20): `dt watch` (Asynchronous file watcher from `watch_src.py` & `file_watcher.py`)
  - Issue [#21](https://github.com/Willmo103/devtul/issues/21): `dt req` (Developer HTTP client from `postman_cli.py`)
  - Issue [#22](https://github.com/Willmo103/devtul/issues/22): `dt new script` (PEP 723 inline script scaffolding from `uv_script_add.cmd`)
  - Issue [#23](https://github.com/Willmo103/devtul/issues/23): `dt spk` (Local neural TTS synthesizer from `piper_cli.py`)

### D. MkDocs Configuration (`mkdocs.yml`)
- Provides clean site navigation structure, enabling `mkdocs serve` for local browser preview or static HTML site generation.

---

## 4. Implementation Steps

1. **Step 1:** Draft and update `README.md` with modern layout, command matrix, and real-world examples.
2. **Step 2:** Create `docs/index.md` and `mkdocs.yml`.
3. **Step 3:** Author command reference documents in `docs/commands/` (`repr.md`, `strings.md`, `inspection.md`, `database.md`, `templates.md`, `reporter.md`, `copy.md`).
4. **Step 4:** Author `docs/guides/path-filtering.md` and `docs/roadmap.md`.
5. **Step 5:** Run test suite and flake8 to verify no regressions.
6. **Step 6:** Record UAT and walkthrough in `.artifacts/docs-toolsuite-suite/`.
