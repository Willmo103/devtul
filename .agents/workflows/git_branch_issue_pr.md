# Workflow: Git Branch, Issue & Draft PR Management

This workflow governs how agents create GitHub issues, manage git branches, open draft pull requests, and maintain traceability across development cycles.

---

## 1. Branch Naming Conventions

Always use descriptive branch names. Note that if a branch named `feature` already exists, git references will fail on `feature/*` sub-namespaces. Use hyphenated prefixes:
- `feat-<name>`: New commands or substantial enhancements (e.g. `feat-clipboard-command`).
- `fix-<name>`: Bug fixes (e.g. `fix-windows-tree-slashes`).
- `chore-<name>`: Refactoring, linting, dependency updates (e.g. `chore-ruff-migration`).
- `agent-<name>`: Agent tooling, rules, or workflows (e.g. `agent-dev-setup`).

---

## 2. GitHub Issue Creation with `gh`

Every user request must be converted into one or more GitHub issues before or alongside implementation.

```bash
# Basic issue creation
gh issue create --title "<Title>" --body "<Detailed description>"

# Issue with labels
gh issue create --title "<Title>" --body "<Detailed description>" --label "enhancement"
```

Capture the returned issue number (e.g., `#7`) for use in commits and PR bodies.

---

## 3. Branch Checkout & Draft PR Creation

```bash
# 1. Create and switch to new branch
git checkout -b feat-new-feature

# 2. Make initial setup commit
git add .
git commit -m "chore: initialize branch for #7"

# 3. Push branch to remote
git push -u origin feat-new-feature

# 4. Open Draft Pull Request linking the issue(s)
gh pr create --draft --title "feat: Implement new feature" --body "## Summary
Initial draft for user request.

### Linked Issues
- Closes #7
- Closes #8

### Progress Checklist
- [ ] Task 1: Scaffolding
- [ ] Task 2: Implementation
- [ ] Task 3: Unit tests
"
```

---

## 4. Progress Tracking & PR Updates

As progress is made:
1. Stage and commit specific units of work:
   ```bash
   git commit -m "feat(module): implement parser logic (Refs #7)"
   git push origin <branch>
   ```
2. Update the Draft PR description to check off completed items:
   ```bash
   gh pr edit --body "## Summary
Updated progress.

### Linked Issues
- Closes #7
- Closes #8

### Progress Checklist
- [x] Task 1: Scaffolding
- [x] Task 2: Implementation
- [ ] Task 3: Unit tests
"
   ```

---

## 5. Resolving Issues & Readying the PR

When all tasks are complete and verified:
1. Commit the final closing commit:
   ```bash
   git commit -m "test(module): complete test suite (Closes #7, Closes #8)"
   git push origin <branch>
   ```
2. Mark the draft PR as ready for review:
   ```bash
   gh pr ready
   ```
3. When merged, GitHub will automatically close the linked issues.
