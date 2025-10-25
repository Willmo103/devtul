from pydantic import BaseModel
from typing import Any, Dict, Optional


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
