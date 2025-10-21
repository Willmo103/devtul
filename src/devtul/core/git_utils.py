"""
Git-related utilities for devtul.
"""

import os
import shutil
import subprocess
from pathlib import Path
from typing import List

import git
import typer

from devtul.core.constants import IGNORE_PARTS, IGNORE_EXTENSIONS
from devtul.core.db.schemas import GitMetadata, GitCommit

def get_git_files(
    repo_path: Path, include_empty: bool = False, only_empty: bool = False
) -> List[str]:
    """
    Get list of files tracked by git in the repository, optionally filtering empty files.
    Args:
        repo_path: Path to the git repository
        include_empty: Whether to include empty files
        only_empty: Whether to include only empty files
    Returns:
        List of git tracked file paths (strings)
    """
    (shell := os.name == "nt")
    if not repo_path.is_dir():
        typer.echo(f"Error: {repo_path} is not a valid directory", err=True)
        raise typer.Exit(1)
    if not (repo_path / ".git").exists():
        typer.echo(f"Error: {repo_path} is not a git repository", err=True)
        raise typer.Exit(1)
    if not shutil.which("git"):
        typer.echo("Error: git is not installed or not found in PATH", err=True)
        raise typer.Exit(1)
    if only_empty:
        include_empty = True
    try:
        result = subprocess.run(
            ["git", "-C", str(repo_path), "ls-files"],
            capture_output=True,
            text=True,
            check=True,
            shell=shell,
        )
        files = [f.strip() for f in result.stdout.splitlines() if f.strip()]
        for f in files:
            if any(ign in f for ign in IGNORE_PARTS):
                files.remove(f)
                continue
            if any(f.endswith(ext) for ext in IGNORE_EXTENSIONS):
                files.remove(f)
                continue

        if not include_empty or only_empty:
            if only_empty:
                # Get only empty files
                empty_files = []
                for f in files:
                    file_path = repo_path / f
                    if file_path.is_file() and file_path.stat().st_size == 0:
                        empty_files.append(f)
                return empty_files
            else:
                # Exclude empty files
                non_empty_files = []
                for f in files:
                    file_path = repo_path / f
                    if file_path.is_file() and file_path.stat().st_size > 0:
                        non_empty_files.append(f)
                return non_empty_files
        return files
    except subprocess.CalledProcessError as e:
        typer.echo(f"Error: Unable to get git files from {repo_path}", err=True)
        typer.echo(f"Git error: {e.stderr}", err=True)
        raise typer.Exit(1)


def get_git_metadata(repo_path: Path) -> GitMetadata:
    """Extract git metadata from repository."""
    try:
        repo = git.Repo(repo_path)

        # Get remotes
        remotes = {remote.name: remote.url for remote in repo.remotes}

        # Get current branch
        try:
            current_branch = repo.active_branch.name
        except TypeError:
            current_branch = "HEAD (detached)"

        # Get all branches
        branches = [branch.name for branch in repo.branches]

        # Get commit info
        try:
            latest_commit = repo.head.commit
            commit_info = GitCommit(
                hash=latest_commit.hexsha[:8],
                message=latest_commit.message.strip(),
                author=str(latest_commit.author),
                date=latest_commit.committed_datetime.isoformat(),
            )
        except Exception:
            commit_info = {"error": "Unable to get commit info"}

        # Check for uncommitted changes
        is_dirty = repo.is_dirty()
        untracked_files = len(repo.untracked_files)

        return GitMetadata(
            remotes=remotes,
            current_branch=current_branch,
            branches=branches,
            latest_commit=commit_info,
            uncommitted_changes=is_dirty,
            untracked_files=untracked_files,
        )
    except Exception as e:
        return {"error": f"Unable to get git metadata: {str(e)}"}


def format_git_metadata_table(metadata: GitMetadata) -> str:
    """Format git metadata as markdown table."""
    if "error" in metadata:
        return f"Error retrieving git metadata: {metadata['error']}"

    table_lines = ["| Property | Value |", "|----------|-------|"]

    table_lines.append(f"| Current Branch | {metadata.current_branch} |")
    table_lines.append(f"| Branches | {', '.join(metadata.branches)} |")

    if "latest_commit" in metadata and "error" not in metadata["latest_commit"]:
        commit = metadata["latest_commit"]
        table_lines.append(f"| Latest Commit | {commit.hash} |")
        table_lines.append(f"| Commit Message | {commit.message} |")
        table_lines.append(f"| Author | {commit.author} |")
        table_lines.append(f"| Commit Date | {commit.date} |")

    table_lines.append(
        f"| Uncommitted Changes | {'Yes' if metadata.uncommitted_changes else 'No'} |"
    )
    table_lines.append(f"| Untracked Files | {metadata.untracked_files} |")

    if metadata.remotes:
        remotes_str = ", ".join(
            [f"{name}: {url}" for name, url in metadata.remotes.items()]
        )
        table_lines.append(f"| Remotes | {remotes_str} |")

    return "\n".join(table_lines)
