# campus-ai/src/api/v3/scheduling.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict
from datetime import datetime

try:
    from ...tasks.scheduling_tasks import optimize_schedule
    CELERY_AVAILABLE = True
except ImportError:
    CELERY_AVAILABLE = False

router = APIRouter(prefix="/scheduling", tags=["v3-scheduling"])


class ActivityRequest(BaseModel):
    """活动请求数据"""
    id: str
    name: str
    priority: str  # CRITICAL, HIGH, MEDIUM, LOW
    duration_hours: float
    acceptable_venues: List[str]
    preferred_time_ranges: List[tuple]  # [(start, end), ...]
    min_budget: float
    max_budget: float
    required_staff_count: int
    expected_participants: int
    club_id: str


class SchedulingRequest(BaseModel):
    """调度优化请求"""
    activities: List[ActivityRequest]
    venues: List[str]
    available_staff: List[str]
    total_budget: float
    planning_start: str  # ISO格式
    planning_end: str
    optimization_timeout: int = 600


@router.post("/optimize")
async def optimize_scheduling(request: SchedulingRequest):
    """
    异步资源调度优化

    复杂度高，必须异步执行
    预估时间: 5-10分钟
    """
    if not CELERY_AVAILABLE:
        raise HTTPException(status_code=503, detail="Celery not available")

    activities_data = [
        {
            "id": a.id,
            "name": a.name,
            "priority": a.priority,
            "duration_hours": a.duration_hours,
            "acceptable_venues": a.acceptable_venues,
            "preferred_time_ranges": a.preferred_time_ranges,
            "min_budget": a.min_budget,
            "max_budget": a.max_budget,
            "required_staff_count": a.required_staff_count,
            "expected_participants": a.expected_participants,
            "club_id": a.club_id
        }
        for a in request.activities
    ]

    task = optimize_schedule.delay(
        activities_data=activities_data,
        venues=request.venues,
        available_staff=request.available_staff,
        total_budget=request.total_budget,
        planning_start=request.planning_start,
        planning_end=request.planning_end,
        timeout=request.optimization_timeout
    )

    return {
        "task_id": task.id,
        "status": "submitted",
        "estimated_time": "5-10 minutes"
    }
