"""
Markdown command for devtul - generates comprehensive markdown documentation.
"""

from datetime import datetime
from pathlib import Path
from typing import List, Optional

import typer
import yaml

from ..core import (
    apply_filters,
    build_tree_structure,
    format_git_metadata_table,
    get_git_files,
    get_git_metadata,
    process_paths_for_subdir,
    write_output,
)


def markdown(
    path: Path = typer.Argument(
        Path().cwd().resolve(),
        help="Path to the git repository",
        callback=lambda v: Path(v).resolve(),
    ),
    print_output: bool = typer.Option(
        False, "-p", "--print", help="Print output to STDOUT"
    ),
    encoding: str = typer.Option(
        "utf8",
        "--encoding",
        help="Character encoding to use",
        callback=lambda v: (
            v
            if v in ["utf8", "ascii", "utf16", "latin1"]
            else typer.BadParameter("Invalid encoding")
        ),
    ),
    file: Optional[Path] = typer.Option(None, "-f", "--file", help="Output file path"),
    sub_dir: Optional[str] = typer.Option(
        None, "--sub-dir", help="Specify a sub-directory to treat as the root"
    ),
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
    if not path.exists():
        typer.echo(f"Error: Path {path} does not exist", err=True)
        raise typer.Exit(1)

    if not (path / ".git").exists():
        typer.echo(f"Error: {path} is not a git repository", err=True)
        raise typer.Exit(1)

    # Get all git files
    all_git_files = get_git_files(path, include_empty)

    # Process for sub-directory
    original_files, adjusted_files = process_paths_for_subdir(
        all_git_files, sub_dir
    )

    # Create a map to get original path from adjusted path
    path_map = dict(zip(adjusted_files, original_files))

    # Apply match/exclude filters on the adjusted paths
    filtered_adjusted_files = apply_filters(adjusted_files, match, exclude)

    if not filtered_adjusted_files:
        typer.echo("No files match the specified criteria", err=True)
        raise typer.Exit(1)

    # Get the corresponding original files for reading content
    filtered_original_files = [path_map[f] for f in filtered_adjusted_files]

    # Get git metadata
    git_metadata = get_git_metadata(path)

    # Build tree structure using the adjusted paths
    tree_structure = build_tree_structure(filtered_adjusted_files)

    # Build markdown content
    markdown_content = []

    # YAML frontmatter
    frontmatter = {
        "generated_at": datetime.now().isoformat(),
        "repo_path": str(path.absolute()),
        "file_count": len(all_git_files),
        "files_included": len(filtered_original_files),
    }

    markdown_content.append("---")
    markdown_content.append(
        yaml.dump(frontmatter, default_flow_style=False).strip()
    )
    markdown_content.append("---")
    markdown_content.append("")

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

    # File contents - iterate using both original and adjusted paths
    for adj_path, orig_path in zip(
        sorted(filtered_adjusted_files), sorted(filtered_original_files)
    ):
        full_path = path / orig_path
        display_path = adj_path

        markdown_content.append(f"### {Path(display_path).name}")
        markdown_content.append("")

        if file_meta:
            # File metadata table
            try:
                stat = full_path.stat()
                file_size = stat.st_size
                last_modified = datetime.fromtimestamp(
                    stat.st_mtime
                ).isoformat()
            except Exception:
                file_size = "Unknown"
                last_modified = "Unknown"

            file_table = [
                "| Property | Value |",
                "|----------|-------|",
                f"| Relative Path | {display_path} |",
                f"| Last Modified | {last_modified} |",
                f"| Size | {file_size} bytes |",
            ]

            markdown_content.extend(file_table)
            markdown_content.append("")
        else:
            # Just show relative path
            markdown_content.append(f"**Path:** `{display_path}`")
            markdown_content.append("")

        # File content
        markdown_content.append("#### Content")
        markdown_content.append("")
        markdown_content.append("```")

        try:
            with open(
                full_path, "r", encoding=encoding, errors="replace"
            ) as f:
                content = f.read()
                markdown_content.append(content)
        except Exception as e:
            markdown_content.append(f"Error reading file: {e}")

        markdown_content.append("```")
        markdown_content.append("")

    # Join all content
    final_content = "\n".join(markdown_content)

    # Determine output behavior
    should_print = print_output or (file is None)
    output_file = file
    if file is not None and file == Path():
        output_file = Path.cwd() / "flattened_repo.md"

    # Write output
    write_output(final_content, output_file, encoding, should_print)
