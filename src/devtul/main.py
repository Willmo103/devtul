"""
DevTul - A collection of developer tools for working with git repositories.
"""

__version__ = "0.1.5"
import typer

from .commands import empty, find, find_folder, git_meta, ls, markdown, tree

app = typer.Typer(
    name="devtul",
    help="Generate tree structures and markdown documentation from git repositories",
    no_args_is_help=True,
)


# Register commands
app.command(name="tree")(tree)
app.command(name="md")(markdown)
app.command(name="ls")(ls)
app.command(name="meta")(git_meta)
app.command(name="find")(find)
app.command(name="find-folder")(find_folder)
app.add_typer(empty, name="empty", help="Locate empty files and folders")


app.command(name="version", help="Show the DevTul version and exit")(
    lambda: typer.echo(__version__)
)


def main():
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
