from pydantic import BaseModel
from typing import Any


class CommandResult(BaseModel):
    result: Any
    stdout: list[str]
    success: bool
    error: str | None
