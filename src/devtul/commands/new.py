from typing import Optional
from devtul.core.database import database
from pydantic import BaseModel


class UserTemplate(BaseModel):
    """Schema for user-defined templates stored in the database."""

    id: Optional[int] = None
    name: str
    fname: str
    content: str


def user_template_from_file(
    fpath: str, name: Optional[str], fname: Optional[str] = None
) -> UserTemplate:
    """Create a UserTemplate instance from a file."""
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()
    if not fname:
        fname = fpath.split("/")[-1]
    if not name:
        name = fname.rsplit(".", 1)[0]
    return UserTemplate(name=name, fname=fname, content=content)

def from_temp(name: str)
