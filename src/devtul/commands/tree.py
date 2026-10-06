"""
Tree command for devtul - generates tree structures from git repositories or directories.
"""

from pathlib import Path
from typing import List, Optional

import typer

from devtul.core.command import FileCommand
from devtul.core.file_utils import build_tree_structure
from devtul.core.models import FileFilterOptions, FilePath, TreeResult
from devtul.core.utils import write_to_file


class TreeCommand(FileCommand):
    """Command that creates a visual tree representation of repository files."""

    name = "tree"
    help = "Generate a tree structure from git tracked files or directory files."

    @property
    def usage(self) -> str:
        return "dt tree [PATH] [OPTIONS]"

    @property
    def examples(self) -> list[str]:
        return [
            "dt tree ./my-repo",
            'dt tree ./my-repo --match "*.py" --exclude "tests/"',
            "dt tree ./my-repo -e .\\tests\\test_migration_and_paths.py",
            "dt tree ./my-repo --no-git -f tree_output.txt",
            "dt tree --debug",
        ]

    def execute(
        self,
        path: Path = Path.cwd().resolve(),
        file: Optional[Path] = None,
        match: List[str] = [],
        exclude: List[str] = [],
        include_empty: bool = False,
        git: bool = True,
        no_ignore: bool = False,
        debug: bool = False,
        fmt_parent: bool = True,
    ) -> Optional[TreeResult]:
        if not path.exists():
            typer.echo(f"Error: Path {path} does not exist", err=True)
            raise typer.Exit(1)

        options = FileFilterOptions(
            path=path,
            match=match,
            exclude=exclude,
            git=git,
            include_empty=include_empty,
            no_ignore=no_ignore,
            debug=debug,
        )

        filtered_results, metrics = self.gather_and_filter_files(options)
        if not filtered_results:
            typer.echo("No files match the specified criteria", err=True)
            return None

        filtered_file_strings = [res.relative_path.as_posix() for res in filtered_results]
        tree_output = build_tree_structure(
            filtered_file_strings, parent=path.as_posix(), fmt_parent=fmt_parent
        )

        result = TreeResult(
            command_name=self.name,
            root_path=FilePath.from_path(path),
            files=filtered_results,
            metrics=metrics,
            tree_text=tree_output,
        )

        # Output handling
        if file is None:
            print(tree_output)
        else:
            output_file = file
            if file == Path():
                output_file = Path.cwd() / "file_tree.md"
            write_to_file(tree_output, output_file)

        return result


_tree_cmd = TreeCommand()


def tree(
    path: Path = typer.Argument(
        Path().cwd().resolve(),
        help="Path to the repository or directory",
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
    git: bool = typer.Option(
        True, "--git/--no-git", help="Look for git tracked files or all files"
    ),
    no_ignore: bool = typer.Option(
        False, "--no-ignore", help="Do not apply default ignore patterns"
    ),
    debug: bool = typer.Option(
        False, "--debug", help="Print debug information for pattern matching"
    ),
    fmt_parent: bool = typer.Option(
        True,
        "--fmt-parent/--no-fmt-parent",
        "--parent/--fmt-root",
        help="Display only the parent folder name as tree root (use --fmt-root or --no-fmt-parent for full path)",
    ),
):
    return _tree_cmd.execute(
        path=path,
        file=file,
        match=match,
        exclude=exclude,
        include_empty=include_empty,
        git=git,
        no_ignore=no_ignore,
        debug=debug,
        fmt_parent=fmt_parent,
    )


tree.__doc__ = _tree_cmd.get_formatted_help()


def entry():
    typer.run(tree)
