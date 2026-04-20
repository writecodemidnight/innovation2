from fastapi import APIRouter

from .algorithms import router as algorithms_router

# 创建API v1路由器
api_v1_router = APIRouter()

# 注册算法路由
api_v1_router.include_router(algorithms_router, tags=["v1-算法服务"])

# 其他路由将在后续任务实现
# from . import recommend, evaluation, nlp, prediction, optimization, mining, cv
# api_v1_router.include_router(recommend.router, prefix="/recommend", tags=["推荐"])
# api_v1_router.include_router(evaluation.router, prefix="/evaluation", tags=["评估"])
# api_v1_router.include_router(nlp.router, prefix="/nlp", tags=["自然语言处理"])
# api_v1_router.include_router(prediction.router, prefix="/prediction", tags=["预测"])
# api_v1_router.include_router(optimization.router, prefix="/optimization", tags=["优化"])
# api_v1_router.include_router(mining.router, prefix="/mining", tags=["数据挖掘"])
# api_v1_router.include_router(cv.router, prefix="/cv", tags=["计算机视觉"])