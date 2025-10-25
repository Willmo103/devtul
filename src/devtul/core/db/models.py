import json
from typing import Optional
from sqlalchemy import ForeignKeyConstraint, String, Integer
from devtul.core.db.database import Base
from sqlalchemy.orm import Mapped, mapped_column
import yaml


class Repo(Base):
    __tablename__ = "repos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    git_meta: Mapped[Optional[str]] = mapped_column(
        String, nullable=True
    )  # YAML string
    tree: Mapped[Optional[str]] = mapped_column(String, nullable=True)
