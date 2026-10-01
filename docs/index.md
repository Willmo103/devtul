# DevTul Documentation

Welcome to the official documentation for **DevTul** (`dt`), a modular developer CLI toolsuite designed to make repository inspection, documentation generation, stream processing, and developer workflows seamless.

---

## 🎯 What is DevTul?

When developing software, engineers frequently encounter small but repetitive friction points:
- *How do I export this entire repository or subset of code into a single, beautifully styled document (Word or Markdown) to review with a client or LLM?*
- *How do I inspect a remote repository without cloning it to my local drive and cluttering my filesystem?*
- *How do I quickly extract readable strings from a binary, DLL, or compiled executable on Windows without installing heavy toolchains?*
- *How do I search or inspect text inside a PDF file directly from my terminal?*
- *How do I export a git repository's file list to clean JSON or YAML to feed into another script?*
- *How do I manage my local database connection profiles or file templates from one place?*

**DevTul provides unified, cross-platform CLI solutions to all of these problems.**

---

## 🚀 Installation & Setup

### Standalone Executable
You do not need Python installed on your system to use DevTul. Download the latest standalone `devtul.exe` binary from the [GitHub Releases](https://github.com/Willmo103/devtul/releases/latest) page and add it to your `PATH`.

```powershell
devtul.exe --help
```

### Using `uv` (Recommended for Python Developers)
Install DevTul as a standalone global CLI tool:
```powershell
uv tool install git+https://github.com/Willmo103/devtul.git
```

Run without installing:
```powershell
uvx --from git+https://github.com/Willmo103/devtul.git dt --help
```

---

## 🏗️ Architectural Foundations

DevTul is built on three core extensible command abstractions located in `devtul.core.command`:

1. **`BaseCommand`:**
   - Centralizes CLI metadata, examples, and docstring formatting across all commands.

2. **`FileCommand`:**
   - Powers all file-oriented commands (`dt tree`, `dt ls`, `dt find`, `dt md`, `dt rpr`).
   - Integrates the `UnixPathMatcher` engine for cross-platform pattern matching (`--match` / `-m` and `--exclude` / `-e`).
   - Auto-detects Git repositories to filter by tracked index, falling back to filesystem scanning.
   - Wraps files in rich Pydantic domain models (`FileResult`, `FilePath`, `FileStat`) for consistent serialization.

3. **`StringCommand`:**
   - Powers stream and text processing commands (`dt ppdf`, `dt str`).
   - Provides a unified stream pipeline for line slicing (`--head`, `--tail`), filtering (`--grep`, `--lines-with`), and sed pattern substitution (`--sed`).

---

## 📖 Command Reference Sitemap

Explore the detailed command guides and real-world examples:

- [**Multi-Format Representation (`dt rpr`)**](commands/repr.md): Export codebases to Word `.docx`, Markdown, or text, and clone remote repositories with `dt rpr clone`.
- [**Stream & PDF Inspection (`dt str`, `dt ppdf`)**](commands/strings.md): Printable string extraction and PDF terminal reading with the `StringCommand` stream engine.
- [**Discovery & Listing (`dt tree`, `dt ls`, `dt find`)**](commands/inspection.md): Formatted ASCII trees, format conversions (JSON, YAML, CSV), and code search.
- [**Database Management (`dt db`)**](commands/database.md): Store and test connection profiles for Postgres, MySQL, MSSQL, MongoDB, and SQLite.
- [**Template Scaffolding (`dt new`)**](commands/templates.md): Create and generate files from local SQLite-backed templates.
- [**Visual Repository Reports (`dt reporter`)**](commands/reporter.md): Generate and serve interactive HTML repository dashboards.
- [**File Copying & Archiving (`dt cp`)**](commands/copy.md): Copy files or bundle repositories into zip archives.
- [**Unix Path Filtering Engine Guide**](guides/path-filtering.md): How globbing, exact paths, and pattern debugging work in DevTul.
- [**Development Candidates Roadmap**](roadmap.md): Centralized backlog of future tool ideas.
