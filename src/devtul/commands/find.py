"""
Find command for devtul - searches for terms in git tracked files.
"""

import json
from pathlib import Path
from typing import List, Optional

import typer

from devtul.core.file_utils import (
    gather_all_paths,
    try_gather_all_git_tracked_paths,
    search_in_file,
)
from devtul.core.models import FileResult
from devtul.core.utils import write_to_file


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
    table_format: bool = typer.Option(False, "--table", help="Output as table format"),
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

    # 1. Gather Paths
    if git:
        paths = try_gather_all_git_tracked_paths(path)
    else:
        paths = gather_all_paths(path)

    if not git:
        from devtul.core.file_utils import filter_gathered_paths_dy_default_ignores
        paths = filter_gathered_paths_dy_default_ignores(paths)

    # 2. Filter via FileResult pipeline
    path_map = {} # Store relative -> full path for search
    file_results = []
    for p in paths:
        if p.is_file():
             res = FileResult(p, path)
             file_results.append(res)
             path_map[res.relative_path.as_posix()] = p

    filtered_adjusted_files = []
    for res in file_results:
        if match:
            import fnmatch
            if not any(fnmatch.fnmatch(res.relative_path.as_posix(), m) for m in match):
                continue
        if exclude:
            import fnmatch
            if any(fnmatch.fnmatch(res.relative_path.as_posix(), e) for e in exclude):
                continue
        filtered_adjusted_files.append(res.relative_path.as_posix())

    if not filtered_adjusted_files:
        typer.echo("No files match the specified criteria", err=True)
        # raise typer.Exit(1)
        return

    # Search in files
    all_matches = []
    for adj_path in sorted(filtered_adjusted_files):
        # We need full path for search_in_file
        # We can reconstruct or use the map
        full_path = path_map.get(adj_path)
        if not full_path:
             full_path = path / adj_path

        matches = search_in_file(full_path, term)
        for match in matches:
            match.file_path = full_path.as_posix()  # Full file path for reading
            match.relative_path = adj_path  # Use the adjusted path for display
            all_matches.append(match)

    if not all_matches:
        output = f"No matches found for term: {term}"
    else:
        if json_format:
            output = json.dumps(
                {
                    "search_term": term,
                    "total_matches": len(all_matches),
                    "matches": [match.model_dump() for match in all_matches],
                },
                indent=2,
            )
        elif table_format:
            # Create table format
            table_lines = [
                "| File | Line | Content |",
                "|------|------|---------|",
            ]
            for match in all_matches:
                file_path = match.relative_path
                line_num = match.line_number
                content = match.content[:100] + (
                    "..." if len(match.content) > 100 else ""
                )
                # Escape pipe characters in content for table
                content = content.replace("|", "\\|")
                table_lines.append(f"| {file_path} | {line_num} | {content} |")
            output = "\n".join(table_lines)
        else:
            output = []
            for match in all_matches:
                if not match.is_error():
                    output.append(match.as_line())
            output = "\n".join(output)

    # Determine output behavior
    if file is not None:
        write_to_file(output, file)
    else:
        typer.echo(output)
    return

def entry():
    typer.run(find)
