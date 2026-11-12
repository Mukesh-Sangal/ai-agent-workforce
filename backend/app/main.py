import logging
from typing import Literal
from uuid import UUID, uuid4

from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict, Field

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("workforce")

app = FastAPI(title="AI Agent Workforce", version="0.1.0")


class TaskRequest(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True, extra="forbid", strict=True
    )
    description: str = Field(min_length=10, max_length=2000)


class TaskPreview(BaseModel):
    id: UUID
    description: str
    status: Literal["preview_only"] = "preview_only"
    model_called: bool = False


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/task-previews", response_model=TaskPreview)
def preview_task(task: TaskRequest) -> TaskPreview:
    preview = TaskPreview(id=uuid4(), description=task.description)
    logger.info("task_preview_created id=%s", preview.id)
    return preview
