import logging
from uuid import uuid4

from app.schemas.task import TaskPreview, TaskRequest

logger = logging.getLogger("workforce")


def create_task_preview(task: TaskRequest) -> TaskPreview:
    preview = TaskPreview(
        id=uuid4(),
        description=task.description,
    )
    logger.info("task_preview_created id=%s", preview.id)
    return preview