# Template Management & Scaffolding (`dt new`)

The `dt new` command (available as both `dt new` and standalone `dt-new`) provides a local template repository and scaffolding engine.

Templates are stored in the local SQLite database at `~/.devtul/devtul_interface.db` (table `file_templates`), making boilerplate code, scripts, configurations, and licenses immediately scaffoldable across any directory.

---

## 📋 Subcommands Reference

### 1. Create a New Template (`dt new create`)
Store a new template in the local database:

```bash
dt new create <TEMPLATE_NAME> [OPTIONS]
```

**Options:**
- `--from-file` / `-f`: Import template content from an existing file on disk.
- `--desc` / `-d`: Description of the template's purpose.
- If `--from-file` is omitted, DevTul automatically opens your default system editor (configured via `$env:EDITOR` or defaulting to Notepad/VS Code) to author the template.

### 2. List All Templates (`dt new ls`)
List all registered templates in a formatted Rich table:

```bash
dt new ls
```

Displays:
- Template Name
- Description
- Character Length / Lines
- Created & Last Modified Timestamps

### 3. Edit a Template (`dt new edit`)
Open an existing template in your editor and save updates back into the SQLite database:

```bash
dt new edit <TEMPLATE_NAME>
```

### 4. Scaffold a File from Template (`dt new make`)
Instantiate a new file from a saved template:

```bash
dt new make <TEMPLATE_NAME> <OUTPUT_PATH>
```

---

## 💡 Practical Examples

### Example 1: Save a Standard Python CLI Boilerplate
```powershell
# Create a template called 'cli-app' from an existing file:
dt new create cli-app --from-file ./boilerplate_cli.py -d "Typer CLI application boilerplate"
```

### Example 2: Scaffold a Script in a New Directory
```powershell
# Instantly create main.py from the 'cli-app' template:
dt new make cli-app ./src/my_tool/main.py
```

### Example 3: Manage Common Config Files (.gitignore, Dockerfile, pyproject.toml)
```powershell
# Save a standardized Python .gitignore:
dt new create python-gitignore --from-file ./.gitignore -d "Standard Python gitignore"

# Scaffold in any new project directory:
cd C:/src/new_project
dt new make python-gitignore ./.gitignore
```
