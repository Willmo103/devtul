"""
Markdown command for devtul - generates comprehensive markdown documentation.
"""

from datetime import datetime
from pathlib import Path
from typing import List, Optional

import typer

from devtul.core.file_utils import build_tree_structure
from devtul.core.file_utils import gather_all_paths, try_gather_all_git_tracked_paths
from devtul.core.models import FileResult, RepoMarkdownHeader
from devtul.core.utils import get_markdown_mapping, write_to_file
from devtul.git.utils import get_git_metadata, format_git_metadata_table


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

    has_git = any(path.rglob(".git"))

    # 1. Gather Paths
    if (not git) or (not has_git):
        GIT_MODE = False
        paths = gather_all_paths(path)
    else:
        # Get all git files
        paths = try_gather_all_git_tracked_paths(path)

    # 2. Filter via FileResult pipeline
    if not GIT_MODE:
        from devtul.core.file_utils import filter_gathered_paths_dy_default_ignores
        paths = filter_gathered_paths_dy_default_ignores(paths)

    file_results = []
    # Original get_all_files did filtering, but gather_all_paths returns all.
    # Convert to FileResults
    for p in paths:
        if p.is_file():
             file_results.append(FileResult(p, path))

    # Filter
    filtered_results = []
    for res in file_results:
        # Match
        if match:
            import fnmatch
            if not any(fnmatch.fnmatch(res.relative_path.as_posix(), m) for m in match):
                continue
        # Exclude
        if exclude:
            import fnmatch
            if any(fnmatch.fnmatch(res.relative_path.as_posix(), e) for e in exclude):
                continue
        # Empty
        from devtul.core.constants import FileContentStatus
        if not include_empty:
             if res.content_status == FileContentStatus.EMPTY:
                 continue

        filtered_results.append(res)

    if not filtered_results:
        typer.echo("No files match the specified criteria", err=True)
        # raise typer.Exit(1)
        return

    filtered_files_paths = sorted([res.relative_path.as_posix() for res in filtered_results])

    if GIT_MODE:
        # Get git metadata
        git_metadata = get_git_metadata(path)
    else:
        git_metadata = None

    # Build tree structure using the adjusted paths
    tree_structure = build_tree_structure(filtered_files_paths, parent=path.as_posix())

    # Build markdown content
    markdown_content = []

    # YAML frontmatter
    frontmatter = RepoMarkdownHeader(
        generated_at=datetime.now().isoformat(),
        repo_path=str(path.absolute()),
        file_count=len(file_results), # Total before filter? or total scanned? Assuming before filter but after gather.
        files_included=len(filtered_results),
    )

    markdown_content.append(frontmatter.frontmatter())

    if GIT_MODE and git_metadata:
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

    # File contents
    # We can iterate filtered_results directly
    for res in sorted(filtered_results, key=lambda x: x.relative_path.as_posix()):
        try:
            full_path = res.full_path
            display_path = res.relative_path.as_posix()

            markdown_content.append(f"### {Path(display_path).name}")
            markdown_content.append("")

            if file_meta:
                # File metadata table
                # We can use info from res
                file_size = res.size
                last_modified = (res.modified_at.isoformat() if res.modified_at else "Unknown")
                created_at = (res.created_at.isoformat() if res.created_at else "Unknown")

                max_key_length = len("Relative Path")
                max_value_length = max(
                    len(display_path), len(str(last_modified)), len(str(file_size)) + 7
                )  # +7 for " bytes"
                file_table = [
                    f"| {'Property'.ljust(max_key_length)} | {'Value'.ljust(max_value_length)} |",
                    "|"
                    + "-" * (max_key_length + 2)
                    + "|"
                    + "-" * (max_value_length + 2)
                    + "|",
                    f"| {'Relative Path'.ljust(max_key_length)} | {display_path.ljust(max_value_length)} |",
                    f"| {'Created At'.ljust(max_key_length)} | {str(created_at).ljust(max_value_length)} |",
                    f"| {'Last Modified'.ljust(max_key_length)} | {str(last_modified).ljust(max_value_length)} |",
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
        except Exception as e:
            markdown_content.append(f"Error processing metadata for {full_path}: {e}")
            markdown_content.append("```")
            markdown_content.append("")
            continue

        try:
            with open(full_path, "r", encoding="utf8", errors="replace") as f:
                content = f.read()
                markdown_content.append(content)
        except Exception as e:
             markdown_content.append(f"Error reading file content: {e}")

        markdown_content.append("```")
        markdown_content.append("")
        markdown_content.append("---")
        markdown_content.append("")

    # Join all content
    final_content = "\n".join(markdown_content)

    if file is not None:
        write_to_file(final_content, file)
    else:
        # Avoid printing massive content to stdout if not requested?
        # Original code did print.
        # But for huge repos this might be bad.
        # Wait, original code: `if file is not None: write... else: print(final_content)`

        # NOTE: Typer/Click might handle paging or big outputs, but printing huge text is risky in terminals.
        # However, `dt md` output is often piped.

        # To be safe and since I'm in an agent, I'll print. But `typer.echo` is safer.
        # However, for huge content, standard print might be better if we expect pipes.
        # Use simple print as original did? Original used `print`.
        print(final_content)

def entry():
    typer.run(markdown)
