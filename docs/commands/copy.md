# File Copying & Archiving (`dt cp`)

The `dt cp` command allows you to copy filtered repository files to another directory or bundle them directly into a compressed `.zip` archive.

It integrates directly with DevTul's `UnixPathMatcher` pipeline, ensuring that files can be selectively packaged without copying temporary files, caches, or unwanted directories.

---

## 📋 Command Syntax

```bash
dt cp [SOURCE_PATH] <DESTINATION_PATH> [OPTIONS]
```

---

## ⚙️ Options Reference

| Option | Shorthand | Description | Default |
| :--- | :--- | :--- | :--- |
| `DESTINATION` | — | Target directory path or zip file path. | **Required** |
| `--archive` | `-a` | Bundle matched files into a `.zip` archive instead of copying files. | `False` |
| `--match` | `-m` | Unix-style pattern to include files (can be repeated). | All files |
| `--exclude` | `-e` | Unix-style pattern to exclude files (can be repeated). | Default ignores |
| `--git` | `-g` / `--no-git` | Filter using git-tracked index if in a Git repository. | `--git` |
| `--empty` | `-E` / `--no-empty` | Include empty files. | `--no-empty` |
| `--debug` | — | Enable verbose path resolution logs. | `False` |

---

## 💡 Practical Examples

### Example 1: Copy Source Code to an External Folder
```powershell
# Copy all Python files from src to a staging directory:
dt cp ./src C:/deploy/staging -m "*.py"
```

### Example 2: Create a Clean Source Code Zip Archive
Bundle git-tracked repository files into a zip archive for distribution or backup, excluding tests and git history:
```powershell
# Package repository into a clean zip archive:
dt cp . ./backups/devtul_source.zip -a -e "tests/*" -e ".artifacts/*"
```

### Example 3: Filter Files with Wildcards
```powershell
# Copy only markdown documentation:
dt cp . C:/docs/exported_docs -m "*.md"
```
