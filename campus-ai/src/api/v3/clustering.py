# campus-ai/src/api/v3/clustering.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict

try:
    from celery.result import AsyncResult
    from ...tasks.clustering_tasks import train_clustering_model, predict_student_clusters
    from ...tasks.celery_app import celery_app
    CELERY_AVAILABLE = True
except ImportError:
    CELERY_AVAILABLE = False

router = APIRouter(prefix="/clustering", tags=["v3-clustering"])


class ClusteringTrainRequest(BaseModel):
    """聚类训练请求"""
    student_ids: Optional[List[str]] = None
    n_clusters: int = 6
    retrain: bool = False


class ClusteringPredictRequest(BaseModel):
    """聚类预测请求"""
    student_ids: List[str]
    model_version: str = "latest"


class TaskResponse(BaseModel):
    """任务响应"""
    task_id: str
    status: str
    message: str


@router.post("/train", response_model=TaskResponse)
async def train_clustering(request: ClusteringTrainRequest):
    """
    异步训练聚类模型

    返回任务ID用于轮询结果
    """
    if not CELERY_AVAILABLE:
        raise HTTPException(status_code=503, detail="Celery not available")

    from datetime import datetime

    task = train_clustering_model.delay(
        student_ids=request.student_ids,
        n_clusters=request.n_clusters,
        model_version=f"kmeans_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    )

    return TaskResponse(
        task_id=task.id,
        status="submitted",
        message="Training job submitted. Use /tasks/{task_id} to check status."
    )


@router.post("/predict", response_model=TaskResponse)
async def predict_clustering(request: ClusteringPredictRequest):
    """异步预测学生聚类"""
    if not CELERY_AVAILABLE:
        raise HTTPException(status_code=503, detail="Celery not available")

    task = predict_student_clusters.delay(
        student_ids=request.student_ids,
        model_version=request.model_version
    )

    return TaskResponse(
        task_id=task.id,
        status="submitted",
        message="Prediction job submitted."
    )
