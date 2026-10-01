# Repository Discovery & Inspection (`dt tree`, `dt ls`, `dt find`, `dt empty`, `dt find-folder`)

DevTul provides a comprehensive suite of repository discovery and file inspection tools designed to give you quick, structured insight into any codebase.

---

## 🌳 Visual Directory Trees (`dt tree` / `dt-tree`)

The `dt tree` command renders clean ASCII directory trees using standard tree box-drawing characters (`├──`, `└──`, `│`).

### Syntax
```bash
dt tree [PATH] [OPTIONS]
dt-tree [PATH] [OPTIONS]
```

### Options
- `--match` / `-m`: Unix-style pattern to include files (e.g. `-m "*.py"`).
- `--exclude` / `-e`: Unix-style pattern to exclude files (e.g. `-e "tests/*"`).
- `--file` / `-f`: Save the tree output to a text file.
- `--git` / `--no-git`: Toggle between Git-tracked files and raw filesystem scanning.
- `--empty` / `-E`: Include empty files.
- `--debug`: Display real-time pattern matching resolution logs.

### Examples
```powershell
# Tree of Python files, excluding test directories:
dt tree -m "*.py" -e "tests/*"

# Write full repository tree to a file:
dt tree . -f repo_structure.txt

# Inspect filesystem directly outside of Git:
dt tree C:/storage/archive --no-git
```

---

## 📋 File Listing & Format Conversion (`dt ls` / `dt-ls`)

The `dt ls` command lists repository files with Unix-style pattern filtering and instant export to structured data formats.

### Syntax
```bash
dt ls [PATH] [OPTIONS]
dt-ls [PATH] [OPTIONS]
```

### Format Flags
- `--json`: Output as a JSON array of relative path strings.
- `--yaml`: Output as a YAML list of relative path strings.
- `--csv`: Output as a CSV file with a `path` header.
- (Default): Outputs one path per line.

### Examples
```powershell
# Export Python file list to JSON for automation scripts:
dt ls -m "*.py" --json

# Export non-test TypeScript files to YAML:
dt ls -m "*.ts" -e "*.test.ts" --yaml

# Feed CSV directly into spreadsheets or data pipelines:
dt ls -m "*.sql" --csv > schemas.csv
```

---

## 🔍 Keyword Code Search (`dt find` / `dt-find`)

The `dt find` command searches for a term across codebase files, returning matching line numbers and source lines.

### Syntax
```bash
dt find <TERM> [OPTIONS]
dt-find <TERM> [OPTIONS]
```

### Options
- `--match` / `-m`: Filter search to specific file patterns.
- `--exclude` / `-e`: Exclude specific file patterns.
- `--json`: Output matches as structured JSON.
- `--table`: Output matches as a Rich formatted table.
- `--path`: Target directory (defaults to current working directory).

### Examples
```powershell
# Search for 'TODO' in all Python files:
dt find "TODO" -m "*.py"

# Search for deprecated functions as a formatted table:
dt find "old_api_call" --table

# Export search results to JSON:
dt find "DATABASE_URL" --json > db_usages.json
```

---

## 🕳️ Locate Empty Items (`dt empty`)

Identify zero-byte files or empty directory trees in your codebase to maintain repository cleanliness.

### Syntax
```bash
# Locate empty files:
dt empty files [PATH]

# Locate empty directories:
dt empty dirs [PATH]
```

### Examples
```powershell
# Find all empty files in current project:
dt empty files .

# Find all empty directories in build output:
dt empty dirs ./dist
```

---

## 📂 Marker Directory Finder (`dt find-folder` / `dt-dirs`)

Quickly locate directories across deep folder hierarchies that contain specific marker files (e.g. `package.json`, `.git`, `pyproject.toml`, or `Dockerfile`).

### Syntax
```bash
dt find-folder [ROOT] [OPTIONS]
dt-dirs [ROOT] [OPTIONS]
```

### Options
- `--with-file`: Filename pattern to look for (e.g. `package.json`, `Cargo.toml`).
- `--with-dir`: Directory name pattern to look for (e.g. `.git`, `node_modules`).
- `--recurse` / `-r`: Recurse into nested subdirectories.

### Examples
```powershell
# Find all Node.js projects in workspace:
dt find-folder C:/src --with-file "package.json" -r

# Find all Git repositories:
dt find-folder C:/src --with-dir ".git"
```
