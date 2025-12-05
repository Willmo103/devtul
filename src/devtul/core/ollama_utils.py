from git import Optional
import ollama
import os

from pydantic import BaseModel, computed_field

HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
_client = ollama.Client(host=HOST, timeout=90)

def _get_generate_response():
    _client.generate(
        model=""
        prompt="",
        suffix="",
        system="",
        format="",
        images=[],
    )


class LoopItem(BaseModel):
    content: str | dict[str, str]
    index: int

    @computed_field
    def template_args(self):
        if isinstance(self.content, str):
            return {"content": self.content}
        else:
            return {dict(self.content)[k]: v for k, v in dict(self.content).items()}


class GenerateLoop:
    def __init__(
        self,
        system: str,
        model: str,
        temprature: float = 0.7,
        max_tokens: int = 1224,
        template: Optional[str] = None,
        items: list[LoopItem] = [],
        responses: list[ollama.GenerateResponse] = [],
    ):
        self._system = system
        self._model = model
        self._temprature = temprature
        self._max_tokens = max_tokens
        self._items = items
        self._responses = responses
        self._client = _client
        if template:
            self._template = template


    def execute_step(self,
