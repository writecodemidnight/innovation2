# campus-ai/src/tasks/scheduling_tasks.py

from celery import shared_task
from typing import List, Dict
from datetime import datetime
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scheduling.hierarchical_scheduler import HierarchicalScheduler
from scheduling.models import Activity, ActivityPriority


@shared_task(bind=True, max_retries=2, soft_time_limit=600)
def optimize_schedule(
    self,
    activities_data: List[Dict],
    venues: List[str],
    available_staff: List[str],
    total_budget: float,
    planning_start: str,
    planning_end: str,
    timeout: int = 600
) -> Dict:
    """
    异步资源调度优化

    预估时间: 5-10分钟
    """
    try:
        # 转换活动数据
        activities = [_dict_to_activity(a) for a in activities_data]

        # 创建调度器
        scheduler = HierarchicalScheduler(
            venues=venues,
            available_staff=available_staff,
            total_budget=total_budget,
            optimization_timeout=timeout
        )

        # 执行调度
        result = scheduler.schedule(
            activities,
            planning_horizon_start=datetime.fromisoformat(planning_start),
            planning_horizon_end=datetime.fromisoformat(planning_end)
        )

        # 序列化结果
        return {
            "status": "success",
            "scheduled_count": len(result["scheduled"]),
            "unscheduled_count": len(result["unscheduled"]),
            "metrics": result["metrics"],
            "scheduled_activities": [
                _activity_to_dict(a) for a in result["scheduled"]
            ],
            "unscheduled_activities": [
                {"id": a.id, "name": a.name} for a in result["unscheduled"]
            ]
        }

    except Exception as exc:
        self.retry(exc=exc, countdown=30)


def _dict_to_activity(data: Dict) -> Activity:
    """将字典转换为Activity对象"""
    priority_map = {
        "CRITICAL": ActivityPriority.CRITICAL,
        "HIGH": ActivityPriority.HIGH,
        "MEDIUM": ActivityPriority.MEDIUM,
        "LOW": ActivityPriority.LOW,
    }

    return Activity(
        id=data["id"],
        name=data["name"],
        priority=priority_map.get(data["priority"], ActivityPriority.MEDIUM),
        duration_hours=data["duration_hours"],
        acceptable_venues=data["acceptable_venues"],
        preferred_time_ranges=[
            (datetime.fromisoformat(start), datetime.fromisoformat(end))
            for start, end in data["preferred_time_ranges"]
        ],
        min_budget=data["min_budget"],
        max_budget=data["max_budget"],
        required_staff_count=data["required_staff_count"],
        expected_participants=data["expected_participants"],
        club_id=data["club_id"]
    )


def _activity_to_dict(activity: Activity) -> Dict:
    """将Activity对象转换为字典"""
    return {
        "id": activity.id,
        "name": activity.name,
        "priority": activity.priority.name,
        "assigned_slot": {
            "venue_id": activity.assigned_slot.venue_id,
            "start_time": activity.assigned_slot.start_time.isoformat(),
            "end_time": activity.assigned_slot.end_time.isoformat(),
        } if activity.assigned_slot else None,
        "assigned_budget": activity.assigned_budget,
        "assigned_staff": activity.assigned_staff,
    }
