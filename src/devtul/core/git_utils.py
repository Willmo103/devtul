"""
Git-related utilities for devtul.
"""

import subprocess
from pathlib import Path
from typing import List

import git
import typer

from .constants import IGNORE_PARTS


def get_git_files(repo_path: Path, include_empty: bool = False) -> List[str]:
    """Get list of files tracked by git in the repository, optionally filtering empty files."""
    try:
        result = subprocess.run(
            ["git", "-C", str(repo_path), "ls-files"],
            capture_output=True,
            text=True,
            check=True,
        )
        files = [f.strip() for f in result.stdout.splitlines() if f.strip()]

        if not include_empty:
            # Filter out empty files
            non_empty_files = []
            for file_path in files:
                if any(ign in file_path for ign in IGNORE_PARTS):
                    continue
                full_path = repo_path / file_path
                try:
                    if full_path.exists() and full_path.stat().st_size > 0:
                        non_empty_files.append(file_path)
                except Exception:
                    # If we can't check the file, include it anyway
                    non_empty_files.append(file_path)
            files = non_empty_files

        return files
    except subprocess.CalledProcessError as e:
        typer.echo(
            f"Error: Unable to get git files from {repo_path}", err=True
        )
        typer.echo(f"Git error: {e.stderr}", err=True)
        raise typer.Exit(1)


def get_git_metadata(repo_path: Path) -> dict:
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
            commit_info = {
                "hash": latest_commit.hexsha[:8],
                "message": latest_commit.message.strip(),
                "author": str(latest_commit.author),
                "date": latest_commit.committed_datetime.isoformat(),
            }
        except Exception:
            commit_info = {"error": "Unable to get commit info"}

        # Check for uncommitted changes
        is_dirty = repo.is_dirty()
        untracked_files = len(repo.untracked_files)

        return {
            "remotes": remotes,
            "current_branch": current_branch,
            "branches": branches,
            "latest_commit": commit_info,
            "uncommitted_changes": is_dirty,
            "untracked_files": untracked_files,
        }
    except Exception as e:
        return {"error": f"Unable to get git metadata: {str(e)}"}


def format_git_metadata_table(metadata: dict) -> str:
    """Format git metadata as markdown table."""
    if "error" in metadata:
        return f"Error retrieving git metadata: {metadata['error']}"

    table_lines = ["| Property | Value |", "|----------|-------|"]

    table_lines.append(
        f"| Current Branch | {metadata.get('current_branch', 'Unknown')} |"
    )
    table_lines.append(
        f"| Branches | {', '.join(metadata.get('branches', []))} |"
    )

    if (
        "latest_commit" in metadata
        and "error" not in metadata["latest_commit"]
    ):
        commit = metadata["latest_commit"]
        table_lines.append(
            f"| Latest Commit | {commit.get('hash', 'Unknown')} |"
        )
        table_lines.append(
            f"| Commit Message | {commit.get('message', 'Unknown')} |"
        )
        table_lines.append(f"| Author | {commit.get('author', 'Unknown')} |")
        table_lines.append(
            f"| Commit Date | {commit.get('date', 'Unknown')} |"
        )

    table_lines.append(
        f"| Uncommitted Changes | {'Yes' if metadata.get('uncommitted_changes') else 'No'} |"
    )
    table_lines.append(
        f"| Untracked Files | {metadata.get('untracked_files', 0)} |"
    )

    if metadata.get("remotes"):
        remotes_str = ", ".join(
            [f"{name}: {url}" for name, url in metadata["remotes"].items()]
        )
        table_lines.append(f"| Remotes | {remotes_str} |")

    return "\n".join(table_lines)
