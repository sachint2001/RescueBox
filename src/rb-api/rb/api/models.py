from typing import Any

from pydantic import BaseModel


class CommandResult(BaseModel):
    result: Any
    stdout: str | list[str]
    success: bool
    error: str | None
