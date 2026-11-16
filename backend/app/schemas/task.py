from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class TaskRequest(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
        strict=True,
    )

    description: str = Field(min_length=10, max_length=2000)


class TaskPreview(BaseModel):
    id: UUID
    description: str
    status: Literal["preview_only"] = "preview_only"
    model_called: bool = False