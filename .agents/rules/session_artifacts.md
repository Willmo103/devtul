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
