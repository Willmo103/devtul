Closes #24.

### Summary
Creates a comprehensive, production-grade documentation suite for **DevTul** (`dt`) covering all tools, command options, standalone script aliases, and rich real-world examples, alongside a centralized candidate roadmap.

### Key Deliverables
1. **Modernized README.md:** Badges, installation options, full Command Matrix, registered standalone scripts, and 6 high-impact real-world workflow examples.
2. **MkDocs Site (`mkdocs.yml`):** Configured documentation site with syntax highlighting and structured navigation.
3. **Dedicated Topic Guides (`docs/`):**
   - Multi-format representation (`docs/commands/repr.md`)
   - Stream & PDF inspection (`docs/commands/strings.md`)
   - File discovery & listing (`docs/commands/inspection.md`)
   - Database connection management (`docs/commands/database.md`)
   - Template scaffolding (`docs/commands/templates.md`)
   - Visual repository reports (`docs/commands/reporter.md`)
   - File copying & archiving (`docs/commands/copy.md`)
   - Unix path filtering guide (`docs/guides/path-filtering.md`)
4. **Candidate Feature Roadmap (`docs/roadmap.md`):** Centralized tracker for cherrypicked development candidates:
   - #19 (`dt db merge`)
   - #20 (`dt watch`)
   - #21 (`dt req`)
   - #22 (`dt new script`)
   - #23 (`dt spk`)
   - Legacy issues #4 and #5

### Verification
- **Test Suite:** `uv run pytest -v` -> 47/47 tests passed (2.69s).
- **Linter:** `uv run flake8 src tests scripts` -> 0 errors.
- **MkDocs Strict Build:** `uv run --extra docs mkdocs build --strict` -> Built in 0.14s with 0 warnings or broken links.
- **Artifacts:** Execution logs and session walkthrough archived in `.artifacts/docs-toolsuite-suite/`.
