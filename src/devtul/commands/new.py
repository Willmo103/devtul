import typer
from pathlib import Path
from typing import Optional
from devtul.core.database import database
from devtul.core.models import UserTemplate
from devtul.core.utils import edit_as_temp


def user_template_from_file(fpath: Path, name: Optional[str]) -> UserTemplate:
    """Create a UserTemplate instance from a file."""
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()
    return UserTemplate(name=name or fpath.name, content=content)


def user_template_from_editor(name: str) -> UserTemplate:
    """Create a UserTemplate instance from the editor."""
    content = edit_as_temp(content="", file_path=None)
    return UserTemplate(name=name, content=content)


def save_user_template_to_db(template: UserTemplate) -> UserTemplate:
    """Save a UserTemplate instance to the database."""
    database["file_templates"].insert(template.model_dump(), pk="name", replace=True)
    return template


def get_user_template_by_name(name: str) -> Optional[UserTemplate]:
    """Retrieve a UserTemplate instance from the database by name."""
    result = database["file_templates"].get(name)
    if result:
        return UserTemplate.model_validate(result)
    return None


def get_all_user_templates() -> list[UserTemplate]:
    """Retrieve all UserTemplate instances from the database."""
    results = database["file_templates"].rows
    return [UserTemplate.model_validate(r) for r in results]


def edit_db_template_in_editor(name: str) -> Optional[UserTemplate]:
    """Edit a UserTemplate stored in the database using the editor."""
    template = get_user_template_by_name(name)
    if not template:
        return None
    updated_content = edit_as_temp(content=template.content)
    template.content = updated_content
    save_user_template_to_db(template)
    return template


def create_new_file_from_template(
    template_name: str,
    output_path: str,
) -> None:
    """Create a new file from a user-defined template."""
    template = get_user_template_by_name(template_name)
    if not template:
        raise ValueError(f"Template '{template_name}' not found in database.")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(template.content)
    return


# commands

app = typer.Typer(name="new", help="Create new files from templates")


@app.command("create", help="Create a new template")
def create_template(
    template_name: str = typer.Argument(..., help="Name for the template"),
    file_path: Optional[Path] = typer.Option(
        None,
        help="Path to an existing file to use as template",
        callback=lambda v: Path(v).resolve() if v else None,
    ),
):
    """
    Create a new file from a user-defined template stored in the database.

    Examples:
        new create basic_resume -f ./resume_template.rst
        new create project_readme (this will open the editor to input template content)
    """
    if not template_name:
        typer.echo("Error: Template name is required", err=True)
        raise typer.Exit(1)

    try:
        if file_path:
            tmpl = user_template_from_file(file_path, name=template_name)
        else:
            tmpl = user_template_from_editor(name=template_name)
        save_user_template_to_db(tmpl)
        typer.echo(f"Template '{tmpl.name}' saved to database.")
        typer.echo(f"Use 'new ls' to view all templates.")
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)


@app.command("ls", help="List all user-defined templates in the database")
def list_templates():
    """
    List stored templates.
    """
    templates = get_all_user_templates()
    if not templates:
        typer.echo("No templates found in the database.")
        return

    for tmpl in templates:
        typer.echo(f"- {tmpl.name} ({len(tmpl.content)} bytes)")


@app.command("edit", help="Edit a user-defined template in the database")
def edit_template(
    template_name: str = typer.Argument(..., help="Name of the template to edit"),
):
    """
    Edit a user-defined template stored in the database using the editor.

    Examples:
        new edit my_template
    """
    try:
        updated_tmpl = edit_db_template_in_editor(template_name)
        if not updated_tmpl:
            raise typer.Exit(1)
        typer.echo(f"Template '{template_name}' updated successfully.")
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)


@app.command("make", help="Create a new file from a user-defined template")
def make_file_from_template(
    template_name: str = typer.Argument(..., help="Name of the template to use"),
    output_path: Path = typer.Argument(
        ...,
        help="Path to the output file",
        callback=lambda v: Path(v).resolve(),
    ),
):
    """
    Create a new file from a user-defined template stored in the database.

    Examples:
        new make my_template ./output.txt
    """
    try:
        create_new_file_from_template(template_name, str(output_path))
        typer.echo(f"File created at '{output_path}' from template '{template_name}'.")
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)
