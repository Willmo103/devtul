# Visual Repository Reports (`dt reporter`)

The `dt reporter` command suite provides visual repository inspection by scanning repository files and git history into a persistent cache and serving an interactive, visual HTML dashboard in your browser.

---

## 📋 Subcommands Reference

### 1. Scan Repository (`dt reporter scan`)
Scans the repository structure, file metadata, commit history, and code statistics into a local cache file (`.devtul_cache.json`):

```bash
dt reporter scan [REPO_PATH] [OPTIONS]
```

**Options:**
- `REPO_PATH`: Path to the repository (defaults to current directory).
- `--cache-file` / `-c`: Custom path for the generated cache file (default: `.devtul_cache.json`).
- `--include-commits` / `-ic`: Extract recent Git commit history and author statistics.

### 2. Serve HTML Dashboard (`dt reporter serve`)
Starts a lightweight local HTTP server and opens the interactive repository report in your web browser:

```bash
dt reporter serve [OPTIONS]
```

**Options:**
- `--port` / `-p`: Port number to serve the dashboard on (default: `8000`).
- `--cache-file` / `-c`: Path to the cache file produced by `scan`.
- `--no-browser`: Do not automatically launch the system web browser.

---

## 📊 Dashboard Features

The generated HTML report (rendered from `devtul.core.templates.report.html`) provides:
- **Repository Summary Cards:** Total files, total lines of code, repository byte size, and git branch status.
- **Language & Extension Breakdown:** Visual distribution of file types (Python, Markdown, YAML, JavaScript, etc.).
- **Commit History & Activity:** Recent commit log, top commit authors, and timeline metrics.
- **Interactive File Explorer:** Navigable directory structure with size sorting.

---

## 💡 Practical Examples

### Example 1: Scan and View Report in One Workflow
```powershell
# 1. Scan repository:
dt reporter scan .

# 2. Launch browser dashboard on port 9090:
dt reporter serve --port 9090
```

### Example 2: Save Diagnostic Cache for Offline Inspection
```powershell
# Scan repository and save report to a specific file:
dt reporter scan C:/src/my-service -c ./reports/service_audit.json
```
