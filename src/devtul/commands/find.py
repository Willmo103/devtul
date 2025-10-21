"""
Find command for devtul - searches for terms in git tracked files.
"""

import json
from pathlib import Path
from typing import List, Optional

import typer

from devtul.core.file_utils import get_all_files

from ..core import (
    apply_filters,
    get_git_files,
    process_paths_for_subdir,
    search_in_file,
    write_to_file,
)


def find(
    term: str = typer.Argument(..., help="Search term to find in files"),
    path: Path = typer.Option(
        Path().cwd().resolve(), help="Path to the git repository"
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
    json_format: bool = typer.Option(
        False, "--json", help="Output as JSON instead of table"
    ),
    ignore_case: bool = typer.Option(
        True,
        "--ignore-case/--no-ignore-case",
        help="Case insensitive search (default true)",
    ),
    git: bool = typer.Option(
        True, "--git/--no-git", help="look for git files or all files"
    ),
):
    """
    Search for a term within git tracked files.

    Searches for the specified term in all git tracked files and returns
    matching lines with file names and line numbers. Results can be output
    as a table or JSON format.

    Examples:
        find ./my-repo "function"
        find ./my-repo "TODO" --match "*.py" --print
        find ./my-repo "import" --sub-dir src -f search_results.json --json
    """
    if not path.exists():
        typer.echo(f"Error: Path {path} does not exist", err=True)
        raise typer.Exit(1)

    if not git or not (path / ".git").exists():
        all_files = get_all_files(path, include_empty=False)
    # Get git files (always exclude empty for searching)
    all_git_files = get_git_files(path, include_empty=False)

    # Process for sub-directory
    original_files, adjusted_files = process_paths_for_subdir(all_git_files, sub_dir)

    # Create a map to get original path from adjusted path
    path_map = dict(zip(adjusted_files, original_files))

    # Apply match/exclude filters on the adjusted paths
    filtered_adjusted_files = apply_filters(adjusted_files, match, exclude)

    if not filtered_adjusted_files:
        typer.echo("No files match the specified criteria", err=True)
        raise typer.Exit(1)

    # Get the corresponding original files for reading content
    filtered_original_files = [path_map[f] for f in filtered_adjusted_files]

    # Search in files
    all_matches = []
    for adj_path, orig_path in zip(
        sorted(filtered_adjusted_files), sorted(filtered_original_files)
    ):
        full_path = path / orig_path
        matches = search_in_file(full_path, term, encoding)
        for match in matches:
            match["relative_path"] = adj_path  # Use the adjusted path for display
            all_matches.append(match)

    if not all_matches:
        output = f"No matches found for term: {term}"
    else:
        if json_format:
            output = json.dumps(
                {
                    "search_term": term,
                    "total_matches": len(all_matches),
                    "matches": all_matches,
                },
                indent=2,
            )
        else:
            # Create table format
            table_lines = [
                "| File | Line | Content |",
                "|------|------|---------|",
            ]

            for match in all_matches:
                file_path = match["relative_path"]
                line_num = match["line_number"]
                content = match["content"][:100] + (
                    "..." if len(match["content"]) > 100 else ""
                )
                # Escape pipe characters in content for table
                content = content.replace("|", "\\|")
                table_lines.append(f"| {file_path} | {line_num} | {content} |")

            output = "\n".join(table_lines)

    # Determine output behavior
    should_print = print_output or (file is None)

    # Write output
    write_to_file(output, file, encoding, should_print)
