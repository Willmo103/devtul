---
name: agent-ops
description: >-
  Operational CLI tools and procedures for managing AI agent sessions, archiving verbatim user prompts in .artifacts/, creating GitHub issues, maintaining draft PRs, and recording feedback turns.
---

# Agent Ops Skill (`agent-ops`)

This skill provides the standard procedures and helper tooling for maintaining agent traceability, archiving session artifacts, and executing Git/GitHub workflows.

---

## When to Use

Activate this skill whenever:
1. A new user session begins (to initialize `.artifacts/<session-slug>/` and store the verbatim user prompt).
2. Creating GitHub issues corresponding to user requests.
3. Checking out a feature/chore branch and creating a draft PR via `gh pr create --draft`.
4. Storing user review feedback (`user_feedback_1.md`, `user_feedback_2.md`).
5. Generating walkthrough summaries (`walkthrough.md`) for user verification.

---

## Quick Reference CLI (`agent_ops.py`)

The companion script `.agents/skills/agent-ops/scripts/agent_ops.py` provides convenience commands:

### 1. Initialize Session
```bash
python .agents/skills/agent-ops/scripts/agent_ops.py session-init --name <session-slug> --prompt "<verbatim user input>"
```

### 2. Record Review Feedback
```bash
python .agents/skills/agent-ops/scripts/agent_ops.py session-feedback --name <session-slug> --feedback "<user review feedback>"
```

### 3. Record Walkthrough
```bash
python .agents/skills/agent-ops/scripts/agent_ops.py session-walkthrough --name <session-slug> --walkthrough "<walkthrough markdown>"
```

### 4. Create Issue
```bash
python .agents/skills/agent-ops/scripts/agent_ops.py issue-create --title "<Title>" --body "<Body>"
```

### 5. Create Draft PR
```bash
python .agents/skills/agent-ops/scripts/agent_ops.py pr-create-draft --title "<Title>" --body "<Body>"
```

---

## Manual Fallbacks (`gh` CLI)

If running the helper script is not desired, the identical operations can be performed using native `gh` and `git` commands:
```bash
# Issues
gh issue create --title "<Title>" --body "<Body>"

# Draft PR
git push -u origin <branch-name>
gh pr create --draft --title "<Title>" --body "<Body>"

# Update PR
gh pr edit <pr-number> --body "<Updated Body>"
```
