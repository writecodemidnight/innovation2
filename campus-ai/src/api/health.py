from fastapi import APIRouter, Depends
from datetime import datetime
from loguru import logger

from ..core.config import get_settings

router = APIRouter()

# 服务启动时间
_startup_time = datetime.now()


def _calculate_uptime() -> str:
    """计算服务运行时间"""
    elapsed = datetime.now() - _startup_time
    days = elapsed.days
    hours, remainder = divmod(elapsed.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    if days > 0:
        return f"{days}天 {hours}小时 {minutes}分钟"
    elif hours > 0:
        return f"{hours}小时 {minutes}分钟 {seconds}秒"
    elif minutes > 0:
        return f"{minutes}分钟 {seconds}秒"
    else:
        return f"{seconds}秒"


@router.get("/health", tags=["健康检查"])
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "service": "campus-ai-algorithm-service",
        "timestamp": datetime.now().isoformat(),
        "version": get_settings().app_version,
        "uptime": _calculate_uptime()
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