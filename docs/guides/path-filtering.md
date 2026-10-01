# Unix Path Matching & Filtering Guide

DevTul features a centralized cross-platform path matching engine (`UnixPathMatcher` in `devtul.core.path_matcher`). This engine powers file filtering across all file commands (`dt tree`, `dt ls`, `dt rpr`, `dt find`, `dt cp`), ensuring identical, intuitive behavior whether you run commands on Windows, Linux, or macOS.

---

## 🎯 The Problem DevTul Solves

In standard Windows shells (PowerShell, CMD), developers often struggle with path filtering because:
1. Windows uses backslashes (`\`) while Unix tools and Git use forward slashes (`/`).
2. Tools often fail to distinguish between directory exclusions (`-e tests/`) and filename exclusions (`-e *test*`).
3. Passing exact paths like `-e .\tests\test_migration.py` often fails because relative paths do not match bare filenames.

**DevTul standardizes all path inputs into normalized Unix-style POSIX paths before evaluation.**

---

## 🔍 How Patterns Are Evaluated

When you run a file command (e.g. `dt tree`, `dt ls`, `dt rpr`), paths pass through a structured multi-stage pipeline:

```
Gathered Files (Git Index or Filesystem)
  │
  ├── 1. Default Ignore Filter (excludes .git, __pycache__, node_modules, etc.)
  │
  ├── 2. Match Filter (--match / -m)
  │      File must match at least one match pattern (if any are specified).
  │
  ├── 3. Exclude Filter (--exclude / -e)
  │      File is excluded if it matches ANY exclude pattern.
  │
  └── 4. Empty File Filter (--empty / --no-empty)
         File is excluded if zero bytes (unless --empty is specified).
```

---

## 📐 Pattern Syntax & Matching Rules

DevTul tests patterns against multiple representations of each file:

### 1. Simple Extension Matching
Matches files by extension anywhere in the repository:
```bash
-m "*.py"          # Matches all Python files
-m "*.{ts,tsx}"    # Matches TypeScript and TSX files
```

### 2. Directory Prefix Matching (`dir/`)
A pattern ending with a forward slash matches any file located inside that directory or its subdirectories:
```bash
-e "tests/"        # Excludes all files in tests/ and any subfolders (tests/unit/...)
-m "src/"          # Includes only files inside src/
```

### 3. Exact Relative Path Matching
Supports both Windows backslashes and Unix forward slashes, stripping leading `./` or `.\`:
```bash
-e ".\tests\test_version_bump.py"  # Excludes that specific file
-e "tests/test_version_bump.py"    # Identical match
```

### 4. Globstar Wildcards (`**`)
Matches across arbitrary directory depths:
```bash
-m "src/**/*.py"   # Matches all Python files under src at any directory depth
-e "**/internal/*" # Excludes any file inside an 'internal' folder anywhere
```

### 5. Bare Substring / Wildcard Matching
```bash
-e "*test*"        # Excludes files containing 'test' anywhere in their name or path
```

---

## 🔬 Debugging Pattern Matching (`--debug`)

If you want to understand exactly why a file was included or excluded, pass the `--debug` flag. DevTul prints real-time resolution logs to stderr:

```powershell
dt rpr . -m "*.py" -e "tests/*" --debug
```

**Example Debug Output:**
```
[DEBUG] Target path: C:\src\devtul (git_mode=True, has_git=True)
[DEBUG] File 'src/devtul/main.py' matched pattern '*.py' (pattern: *.py matched basename)
[DEBUG] File 'tests/test_migration.py' excluded by pattern 'tests/*' (pattern: tests/* matched directory prefix)
[DEBUG] File pipeline finished in 0.04s: 18 selected, 4 excluded, 0 empty.
```
