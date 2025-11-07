import json
from pathlib import Path
from pydantic import BaseModel
from typing import Any, Dict, Optional
from jinja2 import Template
import yaml

from devtul.core.config import EDITOR
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


def edit_file_in_editor(file_path: Path) -> None:
    """
    Open a file in the specified editor.

    Args:
        file_path: Path to the file to edit
        editor_cmd: Command to launch the editor (e.g., "nano", "code", etc.)
    """
    import subprocess

    if EDITOR is None:
        raise ValueError("No editor specified. Please set the EDITOR variable.")

    subprocess.run([EDITOR, str(file_path)])
