# Implementation Plan: CI/CD Automated Version Bumping & Release Pipeline

**Session Slug:** `cicd-release-pipeline`  
**Date:** 2026-09-29  
**Linked Issues:** Closes [#14](https://github.com/Willmo103/devtul/issues/14)  
**Target Branch:** `feature/code-migration-controller-api` -> `master` (Linked PR: [#13](https://github.com/Willmo103/devtul/pull/13))

---

## 1. Problem Diagnostic & Context

1. **Version Fragmentation:**
   - `pyproject.toml`: `0.1.13`
   - `src/devtul/__init__.py`: `0.1.11`
   - `src/devtul/main.py`: `0.1.5`
   - `dt version` outputs `0.1.5` because it reads a stale hardcoded string in `main.py`.
2. **Missing CI/CD Pipeline:**
   - No GitHub Actions workflows exist in `.github/workflows/`.
   - Manual release steps are error-prone and risk out-of-sync tags, builds, and versions.
3. **User Goal:**
   - When a PR is merged back into `master`, automatically bump the project version, commit/tag, build release assets (wheel, sdist, Windows binary), and publish a GitHub Release.

---

## 2. Architecture & Design Decisions

### A. Version Management Utility (`scripts/bump_version.py`)
- Standardized, zero-dependency Python script to manage versions.
- Features:
  - `python scripts/bump_version.py show`: Output current version from `pyproject.toml`.
  - `python scripts/bump_version.py patch`: Increments patch (`0.1.13` -> `0.1.14`).
  - `python scripts/bump_version.py minor`: Increments minor (`0.1.13` -> `0.2.0`).
  - `python scripts/bump_version.py major`: Increments major (`0.1.13` -> `1.0.0`).
  - `python scripts/bump_version.py set <version>`: Explicitly set a version string.
- Atomically synchronizes:
  - `pyproject.toml` (`version = "..."`)
  - `src/devtul/__init__.py` (`__version__ = "..."`)
  - `src/devtul/main.py` (`__version__ = "..."`)
- In `main.py` and `__init__.py`, also support dynamic resolution:
  ```python
  try:
      from importlib.metadata import version as _pkg_version
      __version__ = _pkg_version("devtul")
  except Exception:
      __version__ = "0.1.13"
  ```

### B. Continuous Integration Workflow (`.github/workflows/ci.yml`)
- Triggers on:
  - `pull_request` targeting `master`
  - `push` targeting `master` (excluding `[skip ci]`)
- Steps:
  - Checkout repository
  - Set up Python 3.13 and install `uv`
  - Sync dependencies: `uv sync --all-extras --group dev`
  - Run flake8 linter: `uv run flake8 src tests`
  - Run pytest test suite: `uv run pytest -v`

### C. Automated Release Workflow (`.github/workflows/release.yml`)
- Triggers on:
  - `pull_request` closed on `master` with `merged == true`
  - `workflow_dispatch` (manual trigger with bump choice: `patch`, `minor`, `major`)
- Jobs:
  1. **Bump & Tag (`bump`):**
     - Determine bump type (checks PR labels `bump:major`, `bump:minor`, `bump:patch`, or commit prefix `feat!:`, `feat:`, default `patch`).
     - Run `python scripts/bump_version.py <bump_type>`.
     - Git commit version bump back to `master` with `[skip ci] chore(release): bump version to v<new_version>`.
     - Create and push Git tag `v<new_version>`.
     - Output `new_version` and `tag_name`.
  2. **Build Python Packages (`build-wheel`):**
     - Runs `uv build` to produce `.whl` and `.tar.gz`.
     - Uploads artifacts for the release step.
  3. **Build Windows Executable (`build-exe`):**
     - Runs on `windows-latest`.
     - Uses `pyinstaller devtul.spec` (or `scripts/build-exe.cmd --onefile`) to generate `dist/devtul.exe`.
     - Uploads `devtul.exe`.
  4. **Publish Release (`release`):**
     - Creates GitHub Release via `softprops/action-gh-release@v2`.
     - Attaches `.whl`, `.tar.gz`, and `devtul.exe`.
     - Automatically generates changelog release notes.

### D. Workflow Codification
- Create `.agents/workflows/cicd_versioning_and_release.md` documenting:
  - How merging PRs initiates automated releases.
  - Conventional commit / label triggers for patch vs minor vs major bumps.
  - Manual release triggers via GitHub Actions UI.
  - Local version bump testing.

---

## 3. Implementation Phased Checklist

- [ ] **Phase 1: Codebase Version Synchronization & Script**
  - [ ] Synchronize `pyproject.toml`, `src/devtul/__init__.py`, and `src/devtul/main.py` to `0.1.13`.
  - [ ] Implement `scripts/bump_version.py` supporting `show`, `patch`, `minor`, `major`, `set`.
  - [ ] Update `main.py` and `__init__.py` to use dynamic `importlib.metadata` with fallback.
- [ ] **Phase 2: GitHub Actions Workflows**
  - [ ] Create `.github/workflows/ci.yml` for pull request testing and linting.
  - [ ] Create `.github/workflows/release.yml` for automated version bumping, building, and GitHub release creation on PR merge.
- [ ] **Phase 3: Agent Workflow Documentation**
  - [ ] Create `.agents/workflows/cicd_versioning_and_release.md`.
- [ ] **Phase 4: Programmatic Testing & UAT Validation**
  - [ ] Write unit tests for `scripts/bump_version.py` in `tests/test_version_bump.py`.
  - [ ] Validate YAML workflow syntax and structure.
  - [ ] Run `uv run pytest` and `uv run flake8 src tests scripts`.
  - [ ] Execute UAT dry-run and log results in `.artifacts/cicd-release-pipeline/uat_test_run_1.log`.
- [ ] **Phase 5: Commit, Push & PR Update**
  - [ ] Commit all changes and push to `feature/code-migration-controller-api`.
  - [ ] Update PR #13 body with linked Issue #14 and release pipeline details.
