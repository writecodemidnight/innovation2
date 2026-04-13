# campus-ai/src/api/v3/__init__.py

from fastapi import APIRouter

from .clustering import router as clustering_router
from .scheduling import router as scheduling_router
from .tasks import router as tasks_router

v3_router = APIRouter(prefix="/api/v3/ml")

v3_router.include_router(clustering_router)
v3_router.include_router(scheduling_router)
v3_router.include_router(tasks_router)

__all__ = ['v3_router']
