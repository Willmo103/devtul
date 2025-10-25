import json
from typing import Optional

import yaml
from sqlalchemy import ForeignKeyConstraint, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from devtul.core.db.database import Base


class Repo(Base):
    __tablename__ = "repos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    git_meta: Mapped[Optional[str]] = mapped_column(
        String, nullable=True
    )  # YAML string
    tree: Mapped[Optional[str]] = mapped_column(String, nullable=True)
