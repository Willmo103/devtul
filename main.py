"""
DevTul - A collection of developer tools for working with git repositories.
"""

import subprocess
from pathlib import Path
from typing import List, Optional
from datetime import datetime
import fnmatch
import json

import typer
import git
import yaml

app = typer.Typer(
    name="repo-tools",
    help="Generate tree structures and markdown documentation from git repositories",
    no_args_is_help=True,
    add_completion=True,
)

IGNORE_LIST = [
    "uv.lock",
    ".idea",
    ".vscode",
    ".DS_Store",
    "__pycache__",
    "coverave.xml",
    ".*cache",
    ".python-version",
]


def process_paths_for_subdir(
    files: List[str], sub_dir: Optional[str]
) -> tuple[List[str], List[str]]:
    """
    Filters files by a subdirectory and returns both original and adjusted paths.

    This function is key to making the --sub-dir feature work. It takes all the
    files from git, finds the ones inside the target sub-directory, and then
    creates a "virtual" view of them by stripping the sub-directory prefix.
    We need both the original paths (for reading files) and the adjusted paths
    (for display in the tree or list).

    Args:
        files: List of file paths relative to the repo root.
        sub_dir: The subdirectory to filter by, e.g., "src/app".

    Returns:
        A tuple containing:
        - original_paths: Filtered list of original paths (e.g., ['src/app/main.py']).
        - adjusted_paths: Paths adjusted to be relative to the sub_dir (e.g., ['main.py']).
    """
    if not sub_dir:
        return files, files

    # Normalize the path to use forward slashes and remove any leading/trailing ones.
    normalized_dir = sub_dir.strip("/\\").replace("\\", "/")
    if not normalized_dir:
        return files, files

    prefix = normalized_dir + "/"

    # Find all files that start with the subdirectory path.
    original_paths = [f for f in files if f.startswith(prefix)]

    # Create new paths with the subdirectory prefix removed.
    adjusted_paths = [f.removeprefix(prefix) for f in original_paths]

    return original_paths, adjusted_paths


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
                if any(ign in file_path for ign in IGNORE_LIST):
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


def apply_filters(
    files: List[str], match_patterns: List[str], exclude_patterns: List[str]
) -> List[str]:
    """Apply match and exclude patterns to filter files using set intersection/difference."""
    file_set = set(files)

    # Apply match patterns (if any) - only include files that match at least one pattern
    if match_patterns:
        matched_files = set()
        for pattern in match_patterns:
            pattern_matches = {
                f for f in file_set if fnmatch.fnmatch(f, pattern)
            }
            matched_files.update(pattern_matches)
        file_set = file_set.intersection(matched_files)

    # Apply exclude patterns - remove files that match any exclude pattern
    if exclude_patterns:
        excluded_files = set()
        for pattern in exclude_patterns:
            pattern_matches = {
                f for f in file_set if fnmatch.fnmatch(f, pattern)
            }
            excluded_files.update(pattern_matches)
        file_set = file_set.difference(excluded_files)

    return sorted(list(file_set))


def build_tree_structure(files: List[str]) -> str:
    """Build a tree structure string from a list of file paths."""
    if not files:
        return ""

    # Build directory structure
    tree_dict = {}
    for file_path in sorted(files):
        parts = file_path.split("/")
        current = tree_dict

        for i, part in enumerate(parts):
            if i == len(parts) - 1:  # It's a file
                if "__files__" not in current:
                    current["__files__"] = []
                current["__files__"].append(part)
            else:  # It's a directory
                if part not in current:
                    current[part] = {}
                current = current[part]

    # Convert tree_dict to tree string
    def render_tree(
        node: dict, prefix: str = "", is_last: bool = True
    ) -> List[str]:
        lines = []

        # Collect directories
        dirs = [
            (k, v)
            for k, v in node.items()
            if k != "__files__" and isinstance(v, dict)
        ]
        dirs.sort(key=lambda x: x[0])

        # Collect files
        files = node.get("__files__", [])
        files.sort()

        # Combine directories and files
        all_items = [(name, "dir", content) for name, content in dirs] + [
            (name, "file", None) for name in files
        ]

        for i, (name, item_type, content) in enumerate(all_items):
            is_last_item = i == len(all_items) - 1

            if item_type == "dir":
                symbol = "└── " if is_last_item else "├── "
                lines.append(f"{prefix}{symbol}{name}/")

                next_prefix = prefix + ("    " if is_last_item else "│   ")
                lines.extend(render_tree(content, next_prefix, is_last_item))
            else:
                symbol = "└── " if is_last_item else "├── "
                lines.append(f"{prefix}{symbol}{name}")

        return lines

    if not tree_dict:
        return ""

    # Start with root directory
    root_lines = []
    if len(tree_dict) == 1 and "__files__" not in tree_dict:
        # Single root directory
        root_name = list(tree_dict.keys())[0]
        root_lines.append(f"{root_name}/")
        root_lines.extend(render_tree(tree_dict[root_name], "   "))
    else:
        # Multiple items at root or files at root
        root_lines.extend(render_tree(tree_dict))

    return "\n".join(root_lines)


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


def write_output(
    content: str, file_path: Optional[Path], encoding: str, print_output: bool
):
    """Write content to file and/or stdout based on options."""
    if print_output:
        if encoding != "utf8":
            content = content.encode(encoding, errors="ignore").decode(
                encoding, errors="ignore"
            )
        typer.echo(content)

    if file_path:
        try:
            with open(file_path, "w", encoding=encoding) as f:
                f.write(content)
            if (
                not print_output
            ):  # Only show file message if not printing to stdout
                typer.echo(f"Output written to: {file_path}")
        except Exception as e:
            typer.echo(f"Error writing to file {file_path}: {e}", err=True)
            raise typer.Exit(1)


def search_in_file(
    file_path: Path, search_term: str, encoding: str
) -> List[dict]:
    """Search for a term in a file and return matching lines with context."""
    matches = []
    try:
        with open(file_path, "r", encoding=encoding, errors="replace") as f:
            for line_num, line in enumerate(f, 1):
                if search_term.lower() in line.lower():
                    matches.append(
                        {
                            "line_number": line_num,
                            "content": line.strip(),
                            "file": str(file_path),
                        }
                    )
    except Exception as e:
        matches.append(
            {
                "line_number": 0,
                "content": f"Error reading file: {e}",
                "file": str(file_path),
            }
        )
    return matches


@app.command(name="tree", no_args_is_help=True)
def tree(
    path: Path = typer.Argument(..., help="Path to the git repository"),
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
    file: Optional[Path] = typer.Option(
        None, "-f", "--file", help="Output file path"
    ),
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
):
    """
    Generate a tree structure from git tracked files.

    Creates a visual tree representation of all files tracked by git in the specified repository.
    Uses the same tree characters as standard tree commands (├── └── │).

    Examples:
        tree ./my-repo
        tree ./my-repo --match "*.py" --match "*.md" --print
        tree ./my-repo --sub-dir src -f tree_output.txt
    """
    if not path.exists():
        typer.echo(f"Error: Path {path} does not exist", err=True)
        raise typer.Exit(1)

    if not (path / ".git").exists():
        typer.echo(f"Error: {path} is not a git repository", err=True)
        raise typer.Exit(1)

    # Get git files
    all_git_files = get_git_files(path, include_empty)

    # Process for sub-directory if provided, giving us adjusted paths for display/filtering
    _, adjusted_files = process_paths_for_subdir(all_git_files, sub_dir)

    # Apply match/exclude filters to the adjusted paths
    filtered_files = apply_filters(adjusted_files, match, exclude)

    if not filtered_files:
        typer.echo("No files match the specified criteria", err=True)
        raise typer.Exit(1)

    # Build tree structure using the final filtered and adjusted list
    tree_output = build_tree_structure(filtered_files)

    # Determine output behavior
    should_print = print_output or (file is None)
    output_file = file
    if file is not None and file == Path():
        output_file = Path.cwd() / "flattened_repo.md"

    # Write output
    write_output(tree_output, output_file, encoding, should_print)


@app.command("md", no_args_is_help=True)
def markdown(
    path: Path = typer.Argument(..., help="Path to the git repository"),
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
    file: Optional[Path] = typer.Option(
        None, "-f", "--file", help="Output file path"
    ),
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


@app.command(name="ls", no_args_is_help=True)
def ls(
    path: Path = typer.Argument(..., help="Path to the git repository"),
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
    file: Optional[Path] = typer.Option(
        None, "-f", "--file", help="Output file path"
    ),
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
):
    """
    List git tracked files with optional filtering.

    Behaves like 'git ls-files' but with additional filtering capabilities.
    By default excludes empty files and supports pattern matching.

    Examples:
        ls ./my-repo
        ls ./my-repo --match "*.py" --print
        ls ./my-repo --sub-dir src -f files_list.txt
    """
    if not path.exists():
        typer.echo(f"Error: Path {path} does not exist", err=True)
        raise typer.Exit(1)

    if not (path / ".git").exists():
        typer.echo(f"Error: {path} is not a git repository", err=True)
        raise typer.Exit(1)

    # Get git files
    all_git_files = get_git_files(path, include_empty)

    # Process for sub-directory if provided
    _, adjusted_files = process_paths_for_subdir(all_git_files, sub_dir)

    # Apply match/exclude filters
    filtered_files = apply_filters(adjusted_files, match, exclude)

    if not filtered_files:
        typer.echo("No files match the specified criteria", err=True)
        raise typer.Exit(1)

    # Create output
    output = "\n".join(sorted(filtered_files))

    # Determine output behavior
    should_print = print_output or (file is None)

    # Write output
    write_output(output, file, encoding, should_print)


@app.command("meta", no_args_is_help=True)
def git_meta(
    path: Path = typer.Argument(..., help="Path to the git repository"),
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
    file: Optional[Path] = typer.Option(
        None, "-f", "--file", help="Output file path"
    ),
    json_format: bool = typer.Option(
        False, "--json", help="Output as JSON instead of markdown table"
    ),
):
    """
    Display git repository metadata.

    Shows git repository information including branches, commits, remotes, and status.
    Can output as markdown table or JSON format.

    Examples:
        meta ./my-repo
        meta ./my-repo --json --print
        meta ./my-repo -f metadata.json --json
    """
    if not path.exists():
        typer.echo(f"Error: Path {path} does not exist", err=True)
        raise typer.Exit(1)

    if not (path / ".git").exists():
        output = "Not a git repository"
        should_print = print_output or (file is None)
        write_output(output, file, encoding, should_print)
        return

    # Get git metadata
    git_metadata = get_git_metadata(path)

    # Format output
    if json_format:
        output = json.dumps(git_metadata, indent=2, default=str)
    else:
        output = format_git_metadata_table(git_metadata)

    # Determine output behavior
    should_print = print_output or (file is None)

    # Write output
    write_output(output, file, encoding, should_print)


@app.command(
    name="find",
    no_args_is_help=True,
)
def find(
    path: Path = typer.Argument(..., help="Path to the git repository"),
    term: str = typer.Argument(..., help="Search term to find in files"),
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
    file: Optional[Path] = typer.Option(
        None, "-f", "--file", help="Output file path"
    ),
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
    json_format: bool = typer.Option(
        False, "--json", help="Output as JSON instead of table"
    ),
    ignore_case: bool = typer.Option(
        True,
        "--ignore-case/--no-ignore-case",
        help="Case insensitive search (default true)",
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

    if not (path / ".git").exists():
        typer.echo(f"Error: {path} is not a git repository", err=True)
        raise typer.Exit(1)

    # Get git files (always exclude empty for searching)
    all_git_files = get_git_files(path, include_empty=False)

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

    # Search in files
    all_matches = []
    for adj_path, orig_path in zip(
        sorted(filtered_adjusted_files), sorted(filtered_original_files)
    ):
        full_path = path / orig_path
        matches = search_in_file(full_path, term, encoding)
        for match in matches:
            match["relative_path"] = (
                adj_path  # Use the adjusted path for display
            )
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
    write_output(output, file, encoding, should_print)


if __name__ == "__main__":
    app()
