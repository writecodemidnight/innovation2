# campus-ai/src/api/v3/__init__.py

from fastapi import APIRouter

from .clustering import router as clustering_router
from .scheduling import router as scheduling_router
from .tasks import router as tasks_router
from .evaluation import router as evaluation_router, AHPEvaluateRequest, AHPEvaluateResponse, evaluate_ahp
from .nlp import router as nlp_router
from .forecasting import router as forecasting_router

v3_router = APIRouter(prefix="/api/v3/ml")

v3_router.include_router(clustering_router)
v3_router.include_router(scheduling_router)
v3_router.include_router(tasks_router)
v3_router.include_router(evaluation_router)
v3_router.include_router(nlp_router)
v3_router.include_router(forecasting_router)


# 直接注册 AHP 路由到根路径，供后端兼容调用
@v3_router.post("/ahp", response_model=AHPEvaluateResponse, tags=["v3-ahp"])
async def ahp_root(request: AHPEvaluateRequest):
    """AHP评估 - 兼容旧版调用路径 /api/v3/ml/ahp"""
    return await evaluate_ahp(request)


__all__ = ['v3_router']
