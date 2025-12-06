from pathlib import Path
from typing import Optional
import ollama
import os

from pydantic import BaseModel, computed_field

HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
_client = ollama.Client(host=HOST, timeout=90)


class LoopItem(BaseModel):
    content: str | dict[str, str]
    index: int

    @computed_field
    def template_args(self):
        if isinstance(self.content, str):
            return {"content": self.content}
        else:
            return {dict(self.content)[k]: v for k, v in dict(self.content).items()}


class LoopImageItem(LoopItem):
    @classmethod
    def from_url(cls, fname: Path, index: int):
        from devtul.core.utils import encode_image_to_base64

        content = encode_image_to_base64(fname)
        return cls(content=content, index=index)


class LoopResult(BaseModel):
    item: LoopItem
    response: ollama.GenerateResponse


class GenerateLoop:

    def __init__(
        self,
        system: str,
        template: str,
        format: Optional[str] = None,
        items: list[LoopItem] = [],
        responses: list[ollama.GenerateResponse] = [],
    ):
        self._items = items
        self._responses = responses
        self._client = _client
