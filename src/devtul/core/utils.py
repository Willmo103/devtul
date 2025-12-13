import json
from pathlib import Path
from uuid import uuid4
from pydantic import BaseModel
from typing import Any, Dict, Optional
from jinja2 import Template
import typer
import yaml

from devtul.core.config import EDITOR, app_root
from devtul.core.constants import MD_XREF


def serialize(
    obj: Any,
) -> Optional[str]:
    """
    Serialize an object into JSON, YAML, or CSV format.
    Args:
        obj: The object to serialize
    Returns:
        The serialized object as a string
    """
    if type(obj) is BaseModel:
        return obj.model_dump_json()
    elif isinstance(obj, Dict):
        return str(", ".join([f"{k}: {serialize(v)}" for k, v in obj.items()]))
    elif isinstance(obj, (list, dict, set, tuple)):
        return str(", ".join([serialize(item) for item in obj]))
    else:
        return str(obj)


def render_template(template_name: str, obj: Any) -> str:
    """
    Render a Jinja2 template with the given object.
    Args:
        template_name: The name of the template file
        obj: The object to render in the template
    Returns:
        The rendered template as a string
    """
    from devtul.core.constants import TEMPLATES_DIR

    template_path = TEMPLATES_DIR / template_name
    with open(template_path, "r", encoding="utf-8") as f:
        template_content = f.read()

    template = Template(template_content)
    rendered_content = template.render(obj=obj)
    return rendered_content


def get_markdown_mapping(file_path: str | Path) -> str:
    """
    Get the markdown mapping for a given file.
    """
    if isinstance(file_path, str):
        file_path = Path(file_path)
    extension = file_path.suffix.lower()
    return MD_XREF.get(extension, "plaintext")


def edit_file_in_editor(file_path: Path, return_content: bool = False) -> None:
    """
    Open a file in the specified editor.

    Args:
        file_path: Path to the file to edit
        editor_cmd: Command to launch the editor (e.g., "nano", "code", etc.)
    """
    import subprocess

    if EDITOR is None:
        raise ValueError("No editor specified. Please set the EDITOR variable.")
    print(f"Opening file '{file_path}' in editor '{EDITOR}'...")
    subprocess.run(
        EDITOR.split() + [file_path.as_posix()],
        shell=True,
        check=True,
        capture_output=False,
        text=True,
    )
    # wait for the editor to close before returning
    if return_content:
        input("Press Enter to continue when done editing...")
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    return ""


def create_tmp_file(content: Optional[str] = None) -> Path:
    """
    Create a temporary file with optional content.

    Args:
        content: Content to write to the temporary file
        file_name: Optional name for the temporary file

    Returns:
        Path to the created temporary file
    """
    TMP_DIR = app_root / "temp"
    TMP_DIR.mkdir(exist_ok=True)

    tmp_file_path = TMP_DIR / (uuid4().hex + ".tmp")

    if content:
        with open(tmp_file_path, "w", encoding="utf-8") as f:
            f.write(content)

    return tmp_file_path


def edit_as_temp(
    content: Optional[str] = None,
    file_path: Optional[Path] = None,
) -> str:
    """
    Edit content as a temporary file in the specified editor.

    Args:
        content: Content to write to the temporary file
        file_path: Optional path to an existing file to edit
        file_name: Optional name for the temporary file
    Returns:
        The content of the file after editing
    """
    if file_path:
        content = file_path.read_text(encoding="utf-8")
        tmp_file_path = create_tmp_file(content=content)
    else:
        tmp_file_path = create_tmp_file(content=content)

    new_content = edit_file_in_editor(file_path=tmp_file_path, return_content=True)

    return new_content


def load_yaml_file(fpath: Path) -> Dict[str, Any]:
    """Load a YAML file and return its contents as a dictionary."""
    with open(fpath, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data


def save_yaml_file(fpath: Path, data: Dict[str, Any]) -> None:
    """Save a dictionary to a YAML file."""
    with open(fpath, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f)


def load_json_file(fpath: Path) -> Dict[str, Any]:
    """Load a JSON file and return its contents as a dictionary."""
    with open(fpath, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def save_json_file(fpath: Path, data: Dict[str, Any]) -> None:
    """Save a dictionary to a JSON file."""
    with open(fpath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def convert_from_file_to_base64(fpath: Path) -> str:
    """Convert a file to a base64-encoded string."""
    import base64

    with open(fpath, "rb") as f:
        encoded_bytes = base64.b64encode(f.read())
    return encoded_bytes.decode("utf-8")


def convert_from_base64_to_file(b64_string: str, output_path: Path) -> None:
    """Convert a base64-encoded string back to a file."""
    import base64

    decoded_bytes = base64.b64decode(b64_string.encode("utf-8"))
    with open(output_path, "wb") as f:
        f.write(decoded_bytes)


def create_base64_image_tag(
    b64_string: str, image_type: str = "png", fpath: Optional[Path] = None
) -> str:
    """Create an HTML image tag with a base64-encoded image."""
    if fpath:
        image_type = fpath.suffix.lstrip(".").lower()
    return f'<img src="data:image/{image_type};base64,{b64_string}" alt="Embedded Image" />'


def write_to_file(content: str, file_path: Path):
    """Write content to file and/or stdout based on options."""
    try:
        with open(file_path, "w", encoding="utf8") as f:
            f.write(content)
        typer.echo(f"Output written to: {file_path}")
    except Exception as e:
        typer.echo(f"Error writing to file {file_path}: {e}", err=True)
        raise typer.Exit(1)
