"""
Markdown command for devtul - generates comprehensive markdown documentation.
"""

from datetime import datetime
from pathlib import Path
from typing import List, Optional

import typer

from devtul.core import (
    apply_filters,
    build_tree_structure,
    format_git_metadata_table,
    get_git_files,
    get_git_metadata,
    write_to_file,
)
from devtul.core.models import RepoMarkdownHeader
from devtul.core.file_utils import get_all_files
from devtul.core.utils import get_markdown_mapping


def markdown(
    path: Path = typer.Argument(
        Path().cwd().resolve(),
        help="Path to the git repository",
        callback=lambda v: Path(v).resolve(),
    ),
    file: Optional[Path] = typer.Option(None, "-f", "--file", help="Output file path"),
    match: List[str] = typer.Option(
        [],
        "-m",
        "--match",
        help="Pattern to match files (can be used multiple times)",
    ),
    exclude: List[str] = typer.Option(
        [],
        "-e",
        "--exclude",
        help="Pattern to exclude files (overrides match patterns)",
    ),
    include_empty: bool = typer.Option(
        False, "--empty/--no-empty", help="Include empty files"
    ),
    file_meta: bool = typer.Option(
        True, "--filemeta/--no-filemeta", help="Include file metadata tables"
    ),
    git: bool = typer.Option(
        True, "--git/--no-git", help="look for git files or all files"
    ),
):
    """
    Generate a comprehensive markdown documentation from git repository.

    Creates a single markdown file containing repository metadata, file structure,
    and content of all tracked files. Includes YAML frontmatter with generation metadata.

    Examples:
        md ./my-repo
        md ./my-repo --match "*.py" -f repo_docs.md
        md ./my-repo --sub-dir src --exclude "*.png"
    """
    GIT_MODE = True
    if not path.exists():
        typer.echo(f"Error: Path {path} does not exist", err=True)
        raise typer.Exit(1)

    if not git or not (path / ".git").exists():
        GIT_MODE = False
        all_files = get_all_files(path, include_empty=include_empty)
    else:
        # Get all git files
        all_files = get_git_files(path, include_empty)

    # Apply match/exclude filters on the adjusted paths
    filtered_files = apply_filters(all_files, match, exclude)

    if not filtered_files:
        typer.echo("No files match the specified criteria", err=True)
        raise typer.Exit(1)

    if GIT_MODE:
        # Get git metadata
        git_metadata = get_git_metadata(path)

    # Build tree structure using the adjusted paths
    tree_structure = build_tree_structure(filtered_files, parent=path.as_posix())

    # Build markdown content
    markdown_content = []

    # YAML frontmatter
    frontmatter = RepoMarkdownHeader(
        generated_at=datetime.now().isoformat(),
        repo_path=str(path.absolute()),
        file_count=len(all_files),
        files_included=len(filtered_files),
    )

    markdown_content.append(frontmatter.frontmatter())

    if GIT_MODE:
        # Repository title
        repo_name = path.name.upper()
        markdown_content.append(f"# {repo_name}")
        markdown_content.append("")
        markdown_content.append("---")
        markdown_content.append("")

        # Git metadata section
        markdown_content.append("## Git Metadata")
        markdown_content.append("")
        markdown_content.append(format_git_metadata_table(git_metadata))
        markdown_content.append("")
        markdown_content.append("---")
        markdown_content.append("")

    # Structure section
    markdown_content.append("## Structure")
    markdown_content.append("")
    markdown_content.append("```")
    markdown_content.append(tree_structure)
    markdown_content.append("```")
    markdown_content.append("")
    markdown_content.append("---")
    markdown_content.append("")
    markdown_content.append("## Files")
    markdown_content.append("")

    # File contents - iterate using both original and adjusted paths
    for adj_path, orig_path in zip(sorted(filtered_files), sorted(filtered_files)):
        full_path = path / orig_path
        display_path = adj_path

        markdown_content.append(f"### {Path(display_path).name}")
        markdown_content.append("")

        if file_meta:
            # File metadata table
            try:
                stat = full_path.stat()
                file_size = stat.st_size
                last_modified = datetime.fromtimestamp(stat.st_mtime).isoformat()
            except Exception:
                file_size = "Unknown"
                last_modified = "Unknown"

            max_key_length = len("Relative Path")
            max_value_length = max(
                len(display_path), len(last_modified), len(str(file_size)) + 7
            )  # +7 for " bytes"
            file_table = [
                f"| {'Property'.ljust(max_key_length)} | {'Value'.ljust(max_value_length)} |",
                "|"
                + "-" * (max_key_length + 2)
                + "|"
                + "-" * (max_value_length + 2)
                + "|",
                f"| {'Relative Path'.ljust(max_key_length)} | {display_path.ljust(max_value_length)} |",
                f"| {'Created At'.ljust(max_key_length)} | {datetime.fromtimestamp(full_path.stat().st_birthtime).isoformat().ljust(max_value_length)} |",
                f"| {'Last Modified'.ljust(max_key_length)} | {last_modified.ljust(max_value_length)} |",
                f"| {'Size'.ljust(max_key_length)} | {(str(file_size) + ' bytes').ljust(max_value_length)} |",
            ]

            markdown_content.extend(file_table)
            markdown_content.append("")
        else:
            # Just show relative path
            markdown_content.append(f"**Path:** `{display_path}`")
            markdown_content.append("")

        # File content
        markdown_content.append("**Content**:")
        markdown_content.append("")
        markdown_content.append("```" + get_markdown_mapping(full_path))

        try:
            with open(full_path, "r", encoding="utf8", errors="replace") as f:
                content = f.read()
                markdown_content.append(content)
        except Exception as e:
            markdown_content.append(f"Error reading file: {e}")

        markdown_content.append("```")
        markdown_content.append("")
        markdown_content.append("---")
        markdown_content.append("")

    # Join all content
    final_content = "\n".join(markdown_content)

    if file is not None:
        write_to_file(final_content, file)
    else:
        print(final_content)
