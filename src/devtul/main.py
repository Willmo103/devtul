"""
DevTul - A collection of developer tools for working with git repositories.
"""

try:
    from importlib.metadata import version as _pkg_version

    __version__ = _pkg_version("devtul")
except Exception:
    __version__ = "0.5.1"

import sys

# Ensure UTF-8 output encoding across Windows terminals and packaged binaries
if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import typer

from .commands import (
    copy,
    db_cli,
    empty,
    find,
    find_folder,
    git_meta,
    ls,
    markdown,
    new_cli,
    print_pdf_command,
    rpr_command,
    strings_command,
    tree,
)
from .core import reporter_app

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
app.add_typer(
    reporter_app,
    name="reporter",
    help="Generate reports from git repositories",
    no_args_is_help=True,
)
app.command(name="cp", help="Copy files from one location to another")(copy)
app.command(
    name="rpr",
    help="Generate repository representation (md, docx, text) or clone remote repo",
)(rpr_command)
app.command(name="ppdf", help="Extract and display text from PDF files with stream filtering")(
    print_pdf_command
)
app.command(
    name="print-pdf", help="Extract and display text from PDF files with stream filtering"
)(print_pdf_command)
app.command(name="str", help="Extract printable strings from binary or text files")(
    strings_command
)
app.command(name="strings", help="Extract printable strings from binary or text files")(
    strings_command
)


def main():

    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
