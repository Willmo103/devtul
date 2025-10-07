"""
DevTul - A collection of developer tools for working with git repositories.
"""

import typer

from .commands import find, git_meta, ls, markdown, scan, tree

app = typer.Typer(
    name="devtul",
    help="Generate tree structures and markdown documentation from git repositories",
    no_args_is_help=True,
    add_completion=True,
)

# Register commands
app.command(name="tree", no_args_is_help=True)(tree)
app.command(name="md", no_args_is_help=True)(markdown)
app.command(name="ls", no_args_is_help=True)(ls)
app.command(name="meta", no_args_is_help=True)(git_meta)
app.command(name="find", no_args_is_help=True)(find)
app.command(name="scan", no_args_is_help=True)(scan)


def main():
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
