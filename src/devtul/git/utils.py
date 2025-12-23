"""
Git-related utilities for devtul.
"""

import os
from pathlib import Path
from typing import Dict, List

import git

from devtul.git.models import GitMetadata
from devtul.git.models import GitCommit


def has_nested_git_repo(path: Path) -> bool:
    """Check if the given path contains a nested git repository."""
    for root, dirs, _ in os.walk(path):
        if ".git" in dirs and Path(root) != path:
            return True
    return False


def get_git_metadata(repo_path: Path) -> GitMetadata | None:
    """Extract git metadata from repository."""
    if not (repo_path / ".git").exists() or not repo_path.is_dir():
        return None
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
    max_key_length = len("Uncommitted Changes")
    max_value_length = max(
        len(str(value))
        for value in [
            metadata.current_branch,
            (
                metadata.latest_commit.hash
                if metadata.latest_commit and "error" not in metadata.latest_commit
                else ""
            ),
            (
                metadata.latest_commit.message
                if metadata.latest_commit and "error" not in metadata.latest_commit
                else ""
            ),
            metadata.branches,
            metadata.remotes,
        ]
    )
    if "error" in metadata:
        return f"Error retrieving git metadata: {metadata['error']}"

    table_lines = []
    table_lines.append(
        f"| {'Key'.ljust(max_key_length)} | {'Value'.ljust(max_value_length)} |"
    )
    table_lines.append(f"|{'-' * (max_key_length + 2)}|{'-' * (max_value_length + 2)}|")
    # center everything using the max lengths
    table_lines.append(
        f"| {'Current Branch'.ljust(max_key_length)} | {metadata.current_branch.ljust(max_value_length)} |"
    )
    table_lines.append(
        f"| {'Branches'.ljust(max_key_length)} | {', '.join(metadata.branches).ljust(max_value_length)} |"
    )

    if metadata.latest_commit and "error" not in metadata.latest_commit:
        commit = metadata.latest_commit
        table_lines.append(
            f"| {'Latest Commit'.ljust(max_key_length)} | {commit.hash.ljust(max_value_length)} |"
        )
        table_lines.append(
            f"| {'Commit Message'.ljust(max_key_length)} | {commit.message.ljust(max_value_length)} |"
        )
        table_lines.append(
            f"| {'Author'.ljust(max_key_length)} | {commit.author.ljust(max_value_length)} |"
        )
        table_lines.append(
            f"| {'Commit Date'.ljust(max_key_length)} | {commit.date.ljust(max_value_length)} |"
        )

    table_lines.append(
        f"| {'Uncommitted Changes'.ljust(max_key_length)} | {'Yes'.ljust(max_value_length) if metadata.uncommitted_changes else 'No'.ljust(max_value_length)} |"
    )
    table_lines.append(
        f"| {'Untracked Files'.ljust(max_key_length)} | {str(metadata.untracked_files).ljust(max_value_length)} |"
    )

    if metadata.remotes:
        remotes_str = ", ".join(
            f"{name}: {url}" for name, url in metadata.remotes.items()
        )
        table_lines.append(
            f"| {'Remotes'.ljust(max_key_length)} | {remotes_str.ljust(max_value_length)} |"
        )

    return "\n".join(table_lines)


def get_file_git_history(repo: git.Repo, file_path: Path) -> List[Dict]:
    """Extracts commit history for a specific file."""
    history = []
    try:
        # Get last 10 commits for this specific file
        commits = list(repo.iter_commits(paths=str(file_path), max_count=10))
        for commit in commits:
            history.append(
                {
                    "type": "commit",
                    "date": commit.committed_datetime.isoformat(),
                    "message": commit.message.strip(),
                    "author": commit.author.name,
                    "hash": commit.hexsha[:7],
                }
            )
    except Exception:
        pass
    return history
