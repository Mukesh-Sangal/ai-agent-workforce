from fastapi import APIRouter

from app.schemas.task import TaskPreview, TaskRequest
from app.services.task_service import create_task_preview

router = APIRouter()


@router.get("/")
def root():
    return {"message": "Hello World"}


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/task-previews", response_model=TaskPreview)
def preview_task(task: TaskRequest) -> TaskPreview:
    return create_task_preview(task)