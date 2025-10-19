"""
Output handling utilities for devtul.
"""

from pathlib import Path
from typing import List
import typer


def write_output(content: str, file_path: Path):
    """Write content to file and/or stdout based on options."""
    try:
        with open(file_path, "w", encoding="utf8") as f:
            f.write(content)
        typer.echo(f"Output written to: {file_path}")
    except Exception as e:
        typer.echo(f"Error writing to file {file_path}: {e}", err=True)
        raise typer.Exit(1)


def build_tree_structure(files: List[str], parent: str = ".") -> str:
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
    first_line = f"{parent}/"
    root_lines = [first_line]
    if len(tree_dict) == 1 and "__files__" not in tree_dict:
        # Single root directory
        root_name = list(tree_dict.keys())[0]
        root_lines.append(f"{root_name}/")
        root_lines.extend(render_tree(tree_dict[root_name], "   "))
    else:
        # Multiple items at root or files at root
        root_lines.extend(render_tree(tree_dict))

    return "\n".join(root_lines)


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
