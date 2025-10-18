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
app.command(name="tree")(tree)
app.command(name="md")(markdown)
app.command(name="ls")(ls)
app.command(name="meta")(git_meta)
app.command(name="find")(find)
app.command(name="scan")(scan)


def main():
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
