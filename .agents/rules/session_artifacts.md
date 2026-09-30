# Session Artifact Standards

This rule specifies the exact structure, directory hierarchy, and naming conventions for session tracking in `.artifacts/`.

---

## Directory Organization

```
.artifacts/
├── <session-slug-1>/
│   ├── user_prompt.txt          # Verbatim initial user prompt
│   ├── implementation_plan.md   # Architectural & implementation plan
│   ├── user_feedback_1.md       # First review feedback from user (if any)
│   ├── user_feedback_2.md       # Subsequent review feedback (if any)
│   └── walkthrough.md           # Completed work walkthrough & test results
└── <session-slug-2>/
    └── ...
```

---

## File Specifications

### 1. `user_prompt.txt`
- Must contain the exact, unmodified user prompt text received at the start of the session.
- No editing, summarizing, or truncation.

### 2. `implementation_plan.md`
- Must include:
  - Session metadata (Slug, Date, Author, Linked Issues).
  - Problem diagnostic & root cause analysis.
  - Architecture & design decisions.
  - Phased task checklist with markdown checkboxes (`- [ ]`, `- [x]`).
  - Verification & acceptance criteria.

### 3. `user_feedback_<n>.md`
- When a user responds to an implementation plan or turn with critique, corrections, or adjustments, save the feedback verbatim to `user_feedback_1.md`.
- Subsequent review turns save to `user_feedback_2.md`, `user_feedback_3.md`, etc.

### 4. `walkthrough.md`
- Outlines:
  - Changes implemented across files.
  - Commands executed and their outputs.
  - Test suite and lint validation results.
  - Current status of linked GitHub issues and PRs.

### 5. `impl_test_run_<n>.log` (Programmatic Testing Artifacts)
- All test suite runs (pytest, flake8, unit tests) containing failures or milestone execution logs MUST be captured in the session directory.
- **Incrementing Number Rule:** Every subsequent test run MUST increment the run index (`impl_test_run_1.log`, `impl_test_run_2.log`, `impl_test_run_3.log`, etc.).
- **Never Overwrite:** Never overwrite an existing run log. Preserving previous logs provides a complete historical audit trail of issues encountered and remedies applied.

### 6. `uat_test_run_<n>.log` (User Acceptance Testing Artifacts)
- All manual or automated CLI end-to-end user verification runs MUST be captured into the session directory.
- **Incrementing Number Rule:** Every subsequent UAT pass MUST increment the run index (`uat_test_run_1.log`, `uat_test_run_2.log`, `uat_test_run_3.log`, etc.).
- **Never Overwrite:** Never overwrite an existing UAT log file.

