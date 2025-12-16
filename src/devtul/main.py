"""
DevTul - A collection of developer tools for working with git repositories.
"""

__version__ = "0.1.5"
import typer

from .commands import (db_cli, empty, find, find_folder, git_meta, ls,
                       markdown, new_cli, tree)

app = typer.Typer(
    name="devtul",
    help="Generate tree structures and markdown documentation from git repositories",
    no_args_is_help=True,
)


# Register commands
app.command(name="tree")(tree)
app.command(name="md")(markdown)
app.command(name="ls")(ls)
app.command(name="find")(find)
app.command(name="find-folder")(find_folder)
app.add_typer(empty, name="empty", help="Locate empty files and folders")
app.add_typer(
    new_cli, name="new", help="Create new files from templates", no_args_is_help=True
)
app.command(name="version", help="Show the DevTul version and exit")(
    lambda: typer.echo(__version__)
)
app.add_typer(
    db_cli,
    name="db",
    help="Database related commands",
    no_args_is_help=True,
)


def main():
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
