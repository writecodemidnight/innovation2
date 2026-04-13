# campus-ai/src/api/v3/tasks.py

from fastapi import APIRouter, HTTPException

try:
    from celery.result import AsyncResult
    from ...tasks.celery_app import celery_app
    CELERY_AVAILABLE = True
except ImportError:
    CELERY_AVAILABLE = False

router = APIRouter(prefix="/tasks", tags=["v3-tasks"])


@router.get("/{task_id}")
async def get_task_status(task_id: str):
    """查询异步任务状态"""
    if not CELERY_AVAILABLE:
        raise HTTPException(status_code=503, detail="Celery not available")

    result = AsyncResult(task_id, app=celery_app)

    response = {
        "task_id": task_id,
        "status": result.status,
    }

    if result.ready():
        if result.successful():
            response["result"] = result.get()
        else:
            response["error"] = str(result.result)

    return response
