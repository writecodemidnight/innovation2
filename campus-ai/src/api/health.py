from fastapi import APIRouter, Depends
from datetime import datetime
from loguru import logger

from ..core.config import get_settings

router = APIRouter()

@router.get("/health", tags=["健康检查"])
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "service": "campus-ai-algorithm-service",
        "timestamp": datetime.now().isoformat(),
        "version": get_settings().app_version,
        "uptime": "TODO: 实现运行时间计算"
    }

@router.get("/ready", tags=["健康检查"])
async def readiness_check():
    """就绪检查端点"""
    # 检查关键依赖是否就绪
    dependencies = {
        "config_loaded": True,
        "model_cache_available": False,  # 将在后续任务实现
        "oss_connection": False,  # 将在后续任务实现
    }

    all_ready = all(dependencies.values())

    return {
        "status": "ready" if all_ready else "not_ready",
        "timestamp": datetime.now().isoformat(),
        "dependencies": dependencies,
        "message": "就绪检查完成" if all_ready else "部分依赖未就绪"
    }

@router.get("/metrics", tags=["健康检查"])
async def metrics_endpoint():
    """Prometheus指标端点（由instrumentator自动处理）"""
    pass