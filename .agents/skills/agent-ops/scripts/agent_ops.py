#!/usr/bin/env python3
"""
Agent Ops Helper Utility (agent_ops.py)
Automates session artifact tracking, GitHub issues, and draft PR synchronization for AI agents.
"""

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import List, Optional


def get_repo_root() -> Path:
    """Find the root directory of the git repository."""
    try:
        res = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True,
        )
        return Path(res.stdout.strip()).resolve()
    except Exception:
        # Fallback to parent directories of this script
        return Path(__file__).resolve().parent.parent.parent.parent


def run_gh_cmd(cmd_args: List[str]) -> subprocess.CompletedProcess:
    """Run a gh CLI command and return the CompletedProcess."""
    shell = os.name == "nt"
    return subprocess.run(
        ["gh"] + cmd_args,
        capture_output=True,
        text=True,
        shell=shell,
    )


# ---------------------------------------------------------------------------
# Session Artifact Helpers
# ---------------------------------------------------------------------------


def cmd_session_init(args: argparse.Namespace) -> None:
    root = get_repo_root()
    session_dir = root / ".artifacts" / args.name
    session_dir.mkdir(parents=True, exist_ok=True)

    # 1. Write user_prompt.txt
    prompt_file = session_dir / "user_prompt.txt"
    prompt_content = ""
    if args.prompt:
        if Path(args.prompt).is_file():
            prompt_content = Path(args.prompt).read_text(encoding="utf-8")
        else:
            prompt_content = args.prompt
        prompt_file.write_text(prompt_content, encoding="utf-8")
        print(f"[agent_ops] Verbatim prompt saved to: {prompt_file.relative_to(root).as_posix()}")

    # 2. Template implementation_plan.md if not exists
    plan_file = session_dir / "implementation_plan.md"
    if not plan_file.exists():
        template = f"""# Implementation Plan: {args.name.replace('-', ' ').title()}

**Status:** Proposed  
**Author:** AI Agent  
**Session:** `{args.name}`  

---

## 1. Overview & Problem Diagnostic

## 2. Proposed Architecture & Design

## 3. Phased Task Checklist
- [ ] Phase 1: Preparation & Scaffolding
- [ ] Phase 2: Implementation
- [ ] Phase 3: Verification & Tests

## 4. Verification & Testing
"""
        plan_file.write_text(template, encoding="utf-8")
        print(f"[agent_ops] Initialized implementation plan: {plan_file.relative_to(root).as_posix()}")
    else:
        print(f"[agent_ops] Implementation plan already exists at: {plan_file.relative_to(root).as_posix()}")


def cmd_session_feedback(args: argparse.Namespace) -> None:
    root = get_repo_root()
    session_dir = root / ".artifacts" / args.name
    if not session_dir.exists():
        session_dir.mkdir(parents=True, exist_ok=True)

    # Find next index for user_feedback_<n>.md
    idx = 1
    while (session_dir / f"user_feedback_{idx}.md").exists():
        idx += 1

    feedback_file = session_dir / f"user_feedback_{idx}.md"
    content = ""
    if Path(args.feedback).is_file():
        content = Path(args.feedback).read_text(encoding="utf-8")
    else:
        content = args.feedback

    feedback_file.write_text(content, encoding="utf-8")
    print(f"[agent_ops] Saved feedback #{idx} to: {feedback_file.relative_to(root).as_posix()}")


def cmd_session_walkthrough(args: argparse.Namespace) -> None:
    root = get_repo_root()
    session_dir = root / ".artifacts" / args.name
    session_dir.mkdir(parents=True, exist_ok=True)

    walkthrough_file = session_dir / "walkthrough.md"
    content = ""
    if Path(args.walkthrough).is_file():
        content = Path(args.walkthrough).read_text(encoding="utf-8")
    else:
        content = args.walkthrough

    walkthrough_file.write_text(content, encoding="utf-8")
    print(f"[agent_ops] Saved walkthrough to: {walkthrough_file.relative_to(root).as_posix()}")


# ---------------------------------------------------------------------------
# GitHub Issue & PR Helpers
# ---------------------------------------------------------------------------


def cmd_issue_create(args: argparse.Namespace) -> None:
    gh_args = ["issue", "create", "--title", args.title, "--body", args.body]
    if args.label:
        for lbl in args.label:
            gh_args.extend(["--label", lbl])

    res = run_gh_cmd(gh_args)
    if res.returncode == 0:
        url = res.stdout.strip()
        issue_num = url.split("/")[-1]
        print(f"[agent_ops] Successfully created Issue #{issue_num}: {url}")
    else:
        print(f"[agent_ops] Failed to create issue: {res.stderr}", file=sys.stderr)
        sys.exit(res.returncode)


def cmd_pr_create_draft(args: argparse.Namespace) -> None:
    root = get_repo_root()

    # Determine current branch
    branch_res = subprocess.run(
        ["git", "branch", "--show-current"],
        capture_output=True,
        text=True,
        check=True,
        cwd=str(root),
    )
    current_branch = branch_res.stdout.strip()
    if not current_branch or current_branch in ("master", "main"):
        print(f"[agent_ops] Error: Cannot create PR directly from '{current_branch}'. Checkout a feature branch first.", file=sys.stderr)
        sys.exit(1)

    # Push branch
    print(f"[agent_ops] Pushing branch '{current_branch}' to origin...")
    subprocess.run(["git", "push", "-u", "origin", current_branch], check=True, cwd=str(root))

    # Create draft PR
    gh_args = ["pr", "create", "--draft", "--title", args.title, "--body", args.body]
    if args.base:
        gh_args.extend(["--base", args.base])

    res = run_gh_cmd(gh_args)
    if res.returncode == 0:
        url = res.stdout.strip()
        pr_num = url.split("/")[-1]
        print(f"[agent_ops] Successfully opened Draft PR #{pr_num}: {url}")
    else:
        print(f"[agent_ops] Failed to create draft PR: {res.stderr}", file=sys.stderr)
        sys.exit(res.returncode)


def cmd_pr_update(args: argparse.Namespace) -> None:
    gh_args = ["pr", "edit"]
    if args.pr:
        gh_args.append(str(args.pr))
    if args.title:
        gh_args.extend(["--title", args.title])
    if args.body:
        gh_args.extend(["--body", args.body])

    res = run_gh_cmd(gh_args)
    if res.returncode == 0:
        print(f"[agent_ops] PR updated successfully.")
    else:
        print(f"[agent_ops] Failed to update PR: {res.stderr}", file=sys.stderr)
        sys.exit(res.returncode)


# ---------------------------------------------------------------------------
# CLI Argument Parser
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(
        prog="agent_ops",
        description="DevTul Agent Operations CLI for session archiving and GitHub workflows",
    )
    subparsers = parser.add_subparsers(dest="subcommand", required=True)

    # session-init
    p_init = subparsers.add_parser("session-init", help="Initialize a session artifact directory")
    p_init.add_argument("--name", "-n", required=True, help="Session slug (e.g. update-project-rules)")
    p_init.add_argument("--prompt", "-p", help="Verbatim user prompt text or path to text file")
    p_init.set_defaults(func=cmd_session_init)

    # session-feedback
    p_fb = subparsers.add_parser("session-feedback", help="Record user feedback for review turn")
    p_fb.add_argument("--name", "-n", required=True, help="Session slug")
    p_fb.add_argument("--feedback", "-f", required=True, help="Verbatim feedback text or file path")
    p_fb.set_defaults(func=cmd_session_feedback)

    # session-walkthrough
    p_wt = subparsers.add_parser("session-walkthrough", help="Save walkthrough documentation")
    p_wt.add_argument("--name", "-n", required=True, help="Session slug")
    p_wt.add_argument("--walkthrough", "-w", required=True, help="Walkthrough markdown text or file path")
    p_wt.set_defaults(func=cmd_session_walkthrough)

    # issue-create
    p_issue = subparsers.add_parser("issue-create", help="Create a GitHub issue via gh")
    p_issue.add_argument("--title", "-t", required=True, help="Issue title")
    p_issue.add_argument("--body", "-b", required=True, help="Issue body content")
    p_issue.add_argument("--label", "-l", action="append", help="Issue labels")
    p_issue.set_defaults(func=cmd_issue_create)

    # pr-create-draft
    p_pr = subparsers.add_parser("pr-create-draft", help="Push branch and open a draft pull request")
    p_pr.add_argument("--title", "-t", required=True, help="PR title")
    p_pr.add_argument("--body", "-b", required=True, help="PR body content")
    p_pr.add_argument("--base", help="Target base branch (default: repo default)")
    p_pr.set_defaults(func=cmd_pr_create_draft)

    # pr-update
    p_pru = subparsers.add_parser("pr-update", help="Update pull request title/body")
    p_pru.add_argument("--pr", help="PR number or branch name")
    p_pru.add_argument("--title", "-t", help="Updated title")
    p_pru.add_argument("--body", "-b", help="Updated body")
    p_pru.set_defaults(func=cmd_pr_update)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
