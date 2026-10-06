# Multi-Format Repository Representation (`dt rpr`)

The `dt rpr` command (available as both `dt rpr` and standalone `dt-rpr`) is DevTul's unified repository representation suite. It replaces and modernizes single-format Markdown tools by generating high-fidelity documentation in Microsoft Word (`.docx`), Markdown (`.md`), or plain text (`.txt`).

It also includes the `rpr clone` subcommand, allowing you to clone remote Git repositories into a temporary sandbox, generate documentation, and automatically clean up without cluttering your filesystem.

---

## 📋 Command Syntax

```bash
# General representation of a local folder or repository
dt rpr [TARGET_PATH] [OPTIONS]

# Remote repository cloner and representer
dt rpr clone <REPO_URL> [OPTIONS]

# Standalone script alias
dt-rpr [TARGET_PATH] [OPTIONS]
```

---

## 🎨 Supported Output Formats

### 1. Microsoft Word (`.docx`)
When exporting to `.docx` (`--format docx` or `--docx` / `-dx`), DevTul utilizes its built-in `DocxProcessor` engine to generate professionally styled documents:
- **Typography:** Clean Calibri body typography (11pt, 1.15 line spacing, 6pt space after).
- **Code Callouts:** Syntax-styled Consolas code blocks (9.5pt) featuring light grey background shading (`#F6F8FA`), dark grey text (`#24292E`), and a solid left border accent (`#D0D7DE`).
- **Bumped Heading Hierarchy:** Heading font sizes are bumped by +2pt (H1: 20pt, H2: 16pt, H3: 14pt, H4: 12pt) for clear visual separation.
- **Frontmatter Summary Table:** Top YAML frontmatter is automatically parsed into a two-column styled metadata table.
- **Tables & Lists:** GitHub Flavored Markdown tables and nested bullet/numbered lists are rendered into native Word tables and list elements.

### 2. Markdown (`.md`)
Generates a complete, single-file Markdown document containing:
- YAML frontmatter header with generation timestamp, scanned file counts, and repository path.
- Git metadata table (branch, latest commit hash, author, commit date, dirty state, and remote URL).
- Visual ASCII tree hierarchy of all included files.
- Syntax-highlighted code blocks for each file with metadata properties (size, timestamps, relative path).

### 3. Plain Text (`.txt`)
Outputs raw text representations suitable for plain logging or text pipelines.

---

## ⚙️ Options Reference

| Option | Shorthand | Description | Default |
| :--- | :--- | :--- | :--- |
| `--file` | `-f` | Output file path for the generated representation. | `stdout` (or auto-named `.docx`) |
| `--format` | `-fmt` | Output format: `md`, `docx`, or `text`. | `md` (inferred from `-f` extension) |
| `--docx` | `-dx` | Shortcut flag to force Microsoft Word `.docx` output. | `False` |
| `--md` | — | Shortcut flag to force Markdown `.md` output. | `False` |
| `--match` | `-m` | Unix-style pattern to include files (can be specified multiple times). | All files |
| `--exclude` | `-e` | Unix-style pattern to exclude files (can be specified multiple times). | Standard ignores |
| `--empty` | `-E` / `--no-empty` | Include or exclude empty files. | `--no-empty` |
| `--filemeta` | `-fm` / `--no-filemeta` | Include or exclude individual file property tables. | `--filemeta` |
| `--fmt-parent` | `--fmt-root` / `--no-fmt-parent` | Display only the parent directory name as tree root rather than the full absolute path. | `--fmt-parent` (`True`) |
| `--git` | `-g` / `--no-git` | Filter using git-tracked index if in a Git repository. | `--git` |
| `--dest` | `-d` | *(Clone only)* Custom folder to clone into (preserves folder). | Ephemeral temp dir |
| `--depth` | — | *(Clone only)* Shallow clone history depth. | Full history |
| `--debug` | — | Enable verbose path resolution and pattern debugging. | `False` |

---

## 💡 Practical Examples

### Example 1: Export Codebase to a Word Document for Client Review
```powershell
# Export repository to Word document:
dt rpr . -f client_handoff.docx

# Export only Python source files and exclude tests:
dt rpr . -m "*.py" -e "tests/*" -f python_service.docx
```

### Example 2: Audit a Remote GitHub Repository Without Local Footprint
```powershell
# Clones remote repo to a temp folder, generates docx, cleans up:
dt rpr clone https://github.com/tiangolo/typer -f typer_architecture.docx

# Shallow clone of large repository to Markdown:
dt rpr clone https://github.com/astral-sh/uv --depth 1 -f uv_codebase.md
```

### Example 3: Preserve Cloned Checkout
If you want to keep the cloned repository on disk after generating the representation:
```powershell
dt rpr clone https://github.com/pallets/flask --dest C:/src/flask_checkout -f flask_spec.docx
```

### Example 4: Output to Terminal for Piping
```powershell
# Print flattened markdown directly to stdout:
dt rpr src/ -m "*.py" | Out-File -Encoding utf8 flattened.md
```
