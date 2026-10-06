# DevTul (`dt`)

[![Version](https://img.shields.io/badge/version-v0.5.1-blue.svg)](https://github.com/Willmo103/devtul/releases)
[![Python](https://img.shields.io/badge/python-3.13%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![CI/CD](https://github.com/Willmo103/devtul/actions/workflows/release.yml/badge.svg)](https://github.com/Willmo103/devtul/actions)

**DevTul** (`dt`) is a modular, high-performance developer CLI toolsuite designed to eliminate everyday friction when inspecting repositories, exporting multi-format documentation, auditing remote codebases, processing streams, and managing development workflows.

Built with [Typer](https://typer.tiangolo.com/), [Rich](https://rich.readthedocs.io/), [GitPython](https://gitpython.readthedocs.io/), and [python-docx](https://python-docx.readthedocs.io/).

---

## ⚡ Quickstart & Installation

### Option 1: Standalone Windows Binary (No Python Required)
Download the latest pre-compiled single-file executable `devtul.exe` directly from the [GitHub Releases](https://github.com/Willmo103/devtul/releases/latest) page and add it to your system `PATH`.

```powershell
devtul.exe --help
```

### Option 2: Using `uv` (Recommended)
```powershell
# Install directly as a global CLI tool:
uv tool install git+https://github.com/Willmo103/devtul.git

# Or run instantly without installing:
uvx --from git+https://github.com/Willmo103/devtul.git dt --help
```

### Option 3: Local Developer Setup
```powershell
git clone https://github.com/Willmo103/devtul.git
cd devtul
uv sync --all-extras --group dev

# Run directly via uv:
uv run dt --help
```

---

## 🧭 Command Matrix & Standalone Scripts

DevTul commands can be invoked through the unified `dt` entrypoint or through fast, dedicated standalone script aliases:

| Command | Standalone Alias | Domain / Purpose | Key Highlights |
| :--- | :--- | :--- | :--- |
| **`dt rpr`** | `dt-rpr` | Multi-Format Representation | Generates styled Word (`.docx`), Markdown, or text documentation. Includes `rpr clone` for remote repositories. |
| **`dt ppdf`** | `dt-ppdf` | PDF Text Inspection | Terminal PDF `cat` powered by `pdfplumber` with `--pages`, `--grep`, `--sed`, and line numbering. Alias: `dt print-pdf`. |
| **`dt str`** | `dt-str` | Printable String Extractor | Cross-platform Unix-style `strings` extractor for binaries, DLLs, and text files. Alias: `dt strings`. |
| **`dt tree`** | `dt-tree` | Directory Hierarchy | Renders formatted ASCII directory trees with Unix-like path filtering (`-m`, `-e`). |
| **`dt ls`** | `dt-ls` | File Listing & Conversion | Lists files with instant export to JSON (`--json`), YAML (`--yaml`), and CSV (`--csv`). |
| **`dt find`** | `dt-find` | Keyword Code Search | Fast multi-file keyword locator across git-tracked or directory files. |
| **`dt empty`** | `dt-empty` | Empty Item Detection | Pinpoints empty files (`dt empty files`) or empty folders (`dt empty dirs`). |
| **`dt find-folder`** | `dt-dirs` | Marker Directory Finder | Locates directories matching specific marker files or folder patterns. |
| **`dt new`** | `dt-new` | Template Scaffolding | SQLite-backed user file template manager (`create`, `ls`, `edit`, `make`). |
| **`dt db`** | `dt-db` | Database Profile & Query Suite | Stores profiles, views SQLite schemas, runs SQL queries with multi-format export (`--json`, `--yaml`, `--csv`, `--md`), and queries flat files (CSV, Parquet, JSON) with DuckDB. |
| **`dt reporter`** | — | Visual Repository Reports | Scans repository metadata to JSON cache and serves an interactive web dashboard. |
| **`dt cp`** | — | File Archiving | Copies repository files or packages them into zip archives. |

---

## 🚀 High-Impact Real-World Examples

### 1. Generate a Styled Word Document (`.docx`) from a Codebase
Turn an entire repository into a client-ready Microsoft Word document complete with Consolas syntax blocks, shading (`#F6F8FA`), left border accents (`#D0D7DE`), bumped heading sizes (+2pt), and frontmatter tables:

```powershell
# Export repository to Word document:
dt rpr . -f project_spec.docx

# Filter to Python files, excluding tests:
dt rpr . -m "*.py" -e "tests/*" -f python_codebase.docx
```

### 2. Audit a Remote GitHub Repository Without Local Cloning Overhead
The `rpr clone` command clones a remote repository into an isolated temporary sandbox, generates your requested representation, writes the output, and automatically cleans up:

```powershell
# Clone remote repo and generate Word documentation:
dt rpr clone https://github.com/tiangolo/typer -f typer_spec.docx

# Clone shallow history and generate Markdown:
dt rpr clone https://github.com/astral-sh/uv --depth 1 -f uv_repo.md
```

### 3. Extract Printable Strings from Binaries & Executables
Inspect compiled executables, shared libraries (`.dll`), or binary caches for embedded strings, URLs, or secrets:

```powershell
# Find all HTTP URLs inside an executable:
dt str devtul.exe --grep "https://" --head 15

# Search for specific API keywords with line numbers:
dt str my_app.bin --lines-with "auth" --numbered

# Replace strings on-the-fly using sed substitution:
dt str my_app.bin --sed "s/internal_dev/PRODUCTION/g" --head 20
```

### 4. Inspect PDF Text Directly in Your Terminal
Inspect and filter PDF pages without leaving the terminal:

```powershell
# Display pages 1 through 3 of a PDF:
dt ppdf document.pdf --pages 1-3

# Search for financial lines containing 'Total':
dt ppdf invoice.pdf --grep "Total" --numbered

# Highlight specific keywords with Rich terminal colors:
dt ppdf paper.pdf --lines-with "conclusion"
```

### 5. Format-Converted File Listing for Automation (JSON, YAML, CSV)
Feed repository file structures directly into automation scripts or CI/CD pipelines:

```powershell
# Export Python file paths as JSON array:
dt ls -m "*.py" --json

# Export to YAML or CSV:
dt ls -m "*.ts" --yaml
dt ls -e "vendor/*" --csv
```

### 6. ASCII Directory Trees with Unix-Style Path Filtering & Root Formatting
DevTul uses a unified `UnixPathMatcher` engine across commands. Filter by extension, directory prefix, or wildcard, and format the tree root:

```powershell
# Tree of Python files, displaying only parent directory basename (default):
dt tree -m "*.py" -e "tests/*"

# Display full absolute path as root:
dt tree --no-fmt-parent

# Debug pattern matching behavior:
dt tree -m "*.py" --debug
```

### 7. Database Inspection & DuckDB Flat File Queries
Inspect SQLite databases or query flat files (CSV, Parquet, JSON, SQLite) using embedded DuckDB:

```powershell
# View schema and tables of the DevTul SQLite database or any target db:
dt db view
dt db view --db my_database.db --table users

# Query SQLite with multi-format export (table, json, yaml, csv, md):
dt db query "SELECT * FROM file_templates" --fmt json -o templates.json
dt db query "SELECT * FROM users LIMIT 5" --db app.db --fmt md

# Query local CSV, Parquet, or JSON files using DuckDB:
dt db query-file "SELECT count(*) FROM 'data.csv'"
dt db duck "SELECT department, AVG(salary) FROM 'employees.parquet' GROUP BY department"
```

---

## 🛠️ Architecture & Extensibility

DevTul is built on three core command abstractions:

1. **`BaseCommand`:** Enforces standardized usage, examples, and docstring synthesis.
2. **`FileCommand`:** Powers `dt tree`, `dt ls`, `dt find`, `dt md`, and `dt rpr`. Provides centralized file discovery (git-tracked or filesystem), Unix-like path matching, default ignore filtering, and Pydantic model serialization.
3. **`StringCommand`:** Powers `dt ppdf` and `dt str`. Provides a standardized stream filtering pipeline supporting `--head`, `--tail`, `--grep`, `--sed`, `--numbered`, and `--lines-with`.

---

## 📚 Complete Documentation Suite

For comprehensive documentation, visit the `docs/` folder or serve the interactive documentation site:

- [Repository Representation Guide (`docs/commands/repr.md`)](docs/commands/repr.md)
- [String Stream & PDF Inspection Guide (`docs/commands/strings.md`)](docs/commands/strings.md)
- [File Discovery & Inspection Guide (`docs/commands/inspection.md`)](docs/commands/inspection.md)
- [Database Profiles Guide (`docs/commands/database.md`)](docs/commands/database.md)
- [Template Scaffolding Guide (`docs/commands/templates.md`)](docs/commands/templates.md)
- [HTML Inspection Reporter (`docs/commands/reporter.md`)](docs/commands/reporter.md)
- [File Copying & Archiving (`docs/commands/copy.md`)](docs/commands/copy.md)
- [Unix Path Filtering Engine Guide (`docs/guides/path-filtering.md`)](docs/guides/path-filtering.md)
- [Development Candidates Roadmap (`docs/roadmap.md`)](docs/roadmap.md)

Run local documentation server:
```powershell
uv run mkdocs serve
```

---

## 📄 License

DevTul is open-source software licensed under the [MIT License](LICENSE).
