# Agent Development Workflow Rules

These rules govern how AI coding agents plan, develop, track, and document all changes within the DevTul codebase. All agents MUST adhere to these rules without exception.

---

## Rule 1: Workspace Artifact Persistence (`.artifacts/`)
- Every artifact created by an agent MUST be stored into the `.artifacts/` directory located at the root of this codebase.
- No artifacts should be left unversioned in the root or temporary system folders.

---

## Rule 2: Natural Workflow Documentation (`.agents/workflows/`)
- Any procedure, operational task, or developmental pattern that evolves naturally during engineering work MUST be codified by the agent into a workflow file under `.agents/workflows/` (e.g., `.agents/workflows/<workflow_name>.md`).
- Workflow documents must provide clear, step-by-step instructions so future agents can reliably execute the same task.

---

## Rule 3: Session Directory & Turn Documentation
All user interaction sessions MUST be archived in `.artifacts/<session-slug>/`, where `<session-slug>` is a descriptive, kebab-case directory name representing the objective (e.g., `.artifacts/update-project-rules/`).

Inside each session directory:
1. `user_prompt.txt`: Contains the **verbatim** user prompt text that initiated the session.
2. `implementation_plan.md`: The detailed architectural and implementation plan generated for the task.
3. `user_feedback_<n>.md`: Any user feedback received during iterative review turns MUST be recorded sequentially as `user_feedback_1.md`, `user_feedback_2.md`, etc.
4. `walkthrough.md`: A summary walkthrough of changes, verification results, and next steps for each completed turn.
5. Supplementary session artifacts: Any diagrams, reports, or data artifacts generated for the session.

---

## Rule 4: Branch-Based Development & Draft Pull Requests
- **Never develop directly on `master` or `main`.**
- Every task must be performed on a dedicated git branch (e.g., `feature/<name>`, `fix/<name>`, or `<task-name>`).
- Upon creating the branch and establishing the initial plan, create a **Draft Pull Request** on GitHub using the `gh` CLI:
  ```bash
  gh pr create --draft --title "<Title>" --body "<Body with task checklist>"
  ```
- As progress commits are made, push to the branch and keep the draft PR description updated with task completion status.

---

## Rule 5: GitHub Issue Lifecycle Tracking
- Every user request must be converted into one or more GitHub issues on the repository using the `gh` CLI:
  ```bash
  gh issue create --title "<Issue Title>" --body "<Detailed issue description>"
  ```
  *(There is no limit to the number of issues created for a request; break complex requests down into focused, actionable issues).*
- All created issues must be cross-referenced in the draft pull request description.
- Commits addressing issues must use GitHub closing keywords (e.g., `feat: ... Closes #12` or `fix: ... Resolves #15`).
- Issues must be verified and resolved as development progresses toward PR merge.

---

## Operational Tooling (`gh` CLI & Helper Scripts)
Agents have access to the GitHub CLI (`gh`) and helper scripts located in `.agents/skills/agent-ops/scripts/`:
- `gh auth status`: Verify authentication.
- `gh issue list`, `gh issue create`, `gh issue view`, `gh issue close`.
- `gh pr list`, `gh pr create --draft`, `gh pr edit`, `gh pr status`.
- Helper script `python .agents/skills/agent-ops/scripts/agent_ops.py` can be used to automate session scaffolding, issue tracking, and PR updates.
