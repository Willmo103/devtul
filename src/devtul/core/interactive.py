from dataclasses import dataclass
from typing import Optional

@dataclass
class MenuItem:
    prompt: str
    default: Optional[str] = None

    def display(self) -> str:
        if self.default:
            return f"{self.prompt} ({self.default}): "
        return f"{self.prompt}: "


