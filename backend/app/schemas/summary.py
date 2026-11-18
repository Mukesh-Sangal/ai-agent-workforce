from typing import Literal

from pydantic import BaseModel


class TaskSummary(BaseModel):
    response_id: str
    summary: str
    model: str
    model_called: Literal[True] = True