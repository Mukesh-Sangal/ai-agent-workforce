from fastapi import APIRouter, HTTPException
from app.schemas.summary import TaskSummary
from app.schemas.task import TaskPreview, TaskRequest
from app.schemas.analysis import TaskAnalysis
from app.services.summary_service import (
    SummaryError,
    SummaryTimeout,
    SummaryUnavailable,
    generate_task_summary,
)
from app.services.analysis_service import (
    AnalysisError,
    AnalysisRefused,
    AnalysisTimeout,
    AnalysisUnavailable,
    generate_task_analysis,
)
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

@router.post("/task-summaries", response_model=TaskSummary)
def summarize_task(task: TaskRequest) -> TaskSummary:
    try:
        return generate_task_summary(task)
    except SummaryTimeout as error:
        raise HTTPException(
            status_code=504,
            detail=str(error),
        ) from error
    except SummaryUnavailable as error:
        raise HTTPException(
            status_code=503,
            detail=str(error),
        ) from error
    except SummaryError as error:
        raise HTTPException(
            status_code=502,
            detail=str(error),
        ) from error

@router.post("/task-analyses", response_model=TaskAnalysis)
def analyze_task(task: TaskRequest) -> TaskAnalysis:
    try:
        return generate_task_analysis(task)

    except AnalysisTimeout as error:
        raise HTTPException(
            status_code=504,
            detail=str(error),
        ) from error

    except AnalysisUnavailable as error:
        raise HTTPException(
            status_code=503,
            detail=str(error),
        ) from error

    except AnalysisRefused as error:
        raise HTTPException(
            status_code=422,
            detail=str(error),
        ) from error

    except AnalysisError as error:
        raise HTTPException(
            status_code=502,
            detail=str(error),
        ) from error