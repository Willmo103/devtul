import yaml
from dataclasses import dataclass
from typing import Optional
import typer
from devtul.core.config import scripts_dir
import subprocess

INIT_SCRIPT_COMMAND = ["uv", "init", "--script"]
RUN_SCRIPT_COMMAND = ["uv", "run"]
SCRIPT_INDEX_YAML = scripts_dir / "script_index.yaml"


@dataclass
class ScriptIndexEntry:
    filename: Optional[str] = scripts_dir / "untitled.py"
    content: Optional[str] = None
    readme: Optional[str] = None
    version: Optional[float] = 1.0

    def to_dict(self):
        return {
            "filename": self.filename,
            "content": self.content,
            "readme": self.readme,
            "version": self.version,
        }

    def to_yaml(self):
        return yaml.dump(self.to_dict())


def init_script(script_name: str):
    """Initialize a new script using the script template."""
    if not script_name.endswith(".py"):
        script_name += ".py"
    command = INIT_SCRIPT_COMMAND + [script_name]
    return subprocess.run(command)


script_cli = typer.Typer(help="Manage devtul scripts.")


@script_cli.command("ls")
def list_scripts():
    """List all available scripts."""
    scripts = scripts_dir.glob("*.py")
    for script in scripts:
        typer.echo(f" - {script.name}")


