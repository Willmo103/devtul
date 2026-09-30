# Walkthrough: CI/CD Pipeline, Version Bump Automation & Release Workflows

## Summary of Accomplishments

In this session, we established a complete CI/CD and release automation pipeline for DevTul, synchronized codebase versioning, resolved a Windows CLI Unicode encoding bug, and codified testing artifact incrementing standards.

---

### 1. Codebase Version Synchronization & CLI Parity (Issue #14)
- **Resolved Version Drift:**
  - `pyproject.toml`: `0.1.13`
  - `src/devtul/__init__.py`: updated to import `__version__` from `.main`.
  - `src/devtul/main.py`: updated to dynamically resolve version from `importlib.metadata` with `0.1.13` static fallback.
- **Windows UTF-8 Encoding Fix:**
  - Added stdout/stderr UTF-8 reconfiguration in [`src/devtul/main.py`](file:///c:/src/devtul/src/devtul/main.py#L13-L22) on Windows to prevent `UnicodeEncodeError: 'charmap'` when printing Unicode box-drawing characters (`├──`, `│`, `└──`) in Windows command prompt and compiled binaries.
- **Package Module Execution (`python -m devtul`):**
  - Created [`src/devtul/__main__.py`](file:///c:/src/devtul/src/devtul/__main__.py) allowing direct package invocation and clean PyInstaller entry point resolution.

---

### 2. Standalone Version Bumper Tool (`scripts/bump_version.py`)
- Created [`scripts/bump_version.py`](file:///c:/src/devtul/scripts/bump_version.py) with zero third-party dependencies:
  - `python scripts/bump_version.py show`: Prints active version.
  - `python scripts/bump_version.py patch`: Calculates and applies patch bump (e.g., `0.1.13` -> `0.1.14`).
  - `python scripts/bump_version.py minor`: Calculates and applies minor bump (e.g., `0.1.13` -> `0.2.0`).
  - `python scripts/bump_version.py major`: Calculates and applies major bump (e.g., `0.1.13` -> `1.0.0`).
  - `python scripts/bump_version.py set <ver>`: Sets explicit version string.
- Atomically synchronizes `pyproject.toml`, `src/devtul/main.py`, and `src/devtul/__init__.py`.
- Integrates with GitHub Actions `$GITHUB_OUTPUT` setting `version` and `tag_name`.

---

### 3. GitHub Actions CI/CD Pipeline
- **Continuous Integration ([`.github/workflows/ci.yml`](file:///c:/src/devtul/.github/workflows/ci.yml)):**
  - Triggers on PRs to `master` and pushes to `master`.
  - Matrix across `ubuntu-latest` and `windows-latest` with Python 3.13 and `uv`.
  - Executes `flake8 src tests scripts` and `pytest -v`.
- **Automated Release ([`.github/workflows/release.yml`](file:///c:/src/devtul/.github/workflows/release.yml)):**
  - Triggers when a PR is merged into `master` (`pull_request: closed` with `merged == true`), or via manual `workflow_dispatch`.
  - Detects bump type automatically from PR labels (`bump:major`, `bump:minor`, `bump:patch`) or conventional commit PR titles (`feat!:`, `feat:`, default `patch`).
  - Commits version bump to `master` with `[skip ci]`.
  - Tags release commit `v<version>`.
  - Builds Python distribution packages (`.whl` and `.tar.gz`) via `uv build`.
  - Builds Windows standalone executable (`dist/devtul.exe`) via PyInstaller on `windows-latest`.
  - Creates a GitHub Release with automated changelog notes and attaches all build assets.
- **PyInstaller Specification ([`devtul.spec`](file:///c:/src/devtul/devtul.spec)):**
  - Updated entrypoint to `src/devtul/__main__.py` with `pathex=['src']`.
  - Excluded unused heavy dependencies (`matplotlib`, `scipy`, `pandas`, `IPython`, `tkinter`).

---

### 4. Mandatory Incrementing Test Run Artifact Standards
Updated agent rules and workflows to enforce the incrementing test log policy:
- [`.agents/rules/session_artifacts.md`](file:///c:/src/devtul/.agents/rules/session_artifacts.md#L48-L58): Added Section 5 and 6 defining `impl_test_run_<n>.log` and `uat_test_run_<n>.log`.
- [`.agents/workflows/code_migration_and_evaluation.md`](file:///c:/src/devtul/.agents/workflows/code_migration_and_evaluation.md#L71-L93): Enforced `_1`, `_2`, `_3` incrementing policy without overwriting.
- [`.agents/workflows/session_lifecycle.md`](file:///c:/src/devtul/.agents/workflows/session_lifecycle.md#L100-L110): Added Step 5b for testing artifact archiving.
- [`.agents/workflows/cicd_versioning_and_release.md`](file:///c:/src/devtul/.agents/workflows/cicd_versioning_and_release.md#L68-L76): Documented release testing and validation logging.

---

## Verification & Artifacts

### 1. Programmatic Test Suite
- First test run encountered an import resolution error during test collection; captured into:
  - [`.artifacts/cicd-release-pipeline/impl_test_run_1.log`](file:///c:/src/devtul/.artifacts/cicd-release-pipeline/impl_test_run_1.log)
- Resolved by configuring `[tool.pytest.ini_options]` with `pythonpath = ["."]`.
- Rerun resulted in **13 passed, 0 failed** across `tests/test_migration_and_paths.py` and `tests/test_version_bump.py`.
- Flake8 linter passed with **0 errors** across `src`, `tests`, and `scripts`.

### 2. User Acceptance Testing (UAT)
- Full output recorded into:
  - [`.artifacts/cicd-release-pipeline/uat_test_run_1.log`](file:///c:/src/devtul/.artifacts/cicd-release-pipeline/uat_test_run_1.log)
- Verified:
  1. `dt version`: `0.1.13`
  2. `python scripts/bump_version.py show`: `0.1.13`
  3. `python -m devtul version`: `0.1.13`
  4. `dist\devtul.exe version`: `0.1.13`
  5. `dist\devtul.exe tree --no-git`: Formatted complete Unicode tree hierarchy with zero encode errors.
  6. `uv build`: Built `devtul-0.1.13.tar.gz` and `devtul-0.1.13-py3-none-any.whl`.
  7. GitHub Actions workflows parsed and verified valid YAML.
