# campus-ai/tests/unit/test_hierarchical_scheduler.py
import pytest
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from scheduling.models import TimeSlot, Activity, ActivityPriority, VenueSchedule
from scheduling.hierarchical_scheduler import HierarchicalScheduler


class TestTimeSlot:
    """测试时间槽"""

    def test_timeslot_creation(self):
        """测试时间槽创建"""
        slot = TimeSlot(
            venue_id="venue_1",
            start_time=datetime(2024, 1, 1, 9, 0),
            end_time=datetime(2024, 1, 1, 11, 0)
        )
        assert slot.venue_id == "venue_1"
        assert slot.duration_hours == 2.0

    def test_timeslot_conflict_same_venue(self):
        """测试同场地时间冲突"""
        slot1 = TimeSlot(
            venue_id="venue_1",
            start_time=datetime(2024, 1, 1, 9, 0),
            end_time=datetime(2024, 1, 1, 11, 0)
        )
        slot2 = TimeSlot(
            venue_id="venue_1",
            start_time=datetime(2024, 1, 1, 10, 0),
            end_time=datetime(2024, 1, 1, 12, 0)
        )
        assert slot1.conflicts_with(slot2)

    def test_timeslot_no_conflict_different_venue(self):
        """测试不同场地无冲突"""
        slot1 = TimeSlot(
            venue_id="venue_1",
            start_time=datetime(2024, 1, 1, 9, 0),
            end_time=datetime(2024, 1, 1, 11, 0)
        )
        slot2 = TimeSlot(
            venue_id="venue_2",
            start_time=datetime(2024, 1, 1, 10, 0),
            end_time=datetime(2024, 1, 1, 12, 0)
        )
        assert not slot1.conflicts_with(slot2)


class TestVenueSchedule:
    """测试场地调度表"""

    def test_add_slot_no_conflict(self):
        """测试无冲突添加"""
        schedule = VenueSchedule("venue_1")
        slot = TimeSlot(
            venue_id="venue_1",
            start_time=datetime(2024, 1, 1, 9, 0),
            end_time=datetime(2024, 1, 1, 11, 0)
        )
        assert schedule.add_slot(slot) is True
        assert len(schedule.slots) == 1

    def test_add_slot_with_conflict(self):
        """测试有冲突时添加失败"""
        schedule = VenueSchedule("venue_1")
        slot1 = TimeSlot(
            venue_id="venue_1",
            start_time=datetime(2024, 1, 1, 9, 0),
            end_time=datetime(2024, 1, 1, 11, 0)
        )
        slot2 = TimeSlot(
            venue_id="venue_1",
            start_time=datetime(2024, 1, 1, 10, 0),
            end_time=datetime(2024, 1, 1, 12, 0)
        )
        schedule.add_slot(slot1)
        assert schedule.add_slot(slot2) is False


class TestHierarchicalScheduler:
    """测试分层调度器"""

    def test_initialization(self):
        """测试调度器初始化"""
        scheduler = HierarchicalScheduler(
            venues=["v1", "v2"],
            available_staff=["s1", "s2"],
            total_budget=10000.0
        )
        assert len(scheduler.venues) == 2
        assert scheduler.total_budget == 10000.0
        assert "v1" in scheduler.venue_schedules
        assert "v2" in scheduler.venue_schedules

    def test_schedule_single_activity(self):
        """测试单个活动调度"""
        scheduler = HierarchicalScheduler(
            venues=["hall_a"],
            available_staff=["staff_1"],
            total_budget=1000.0
        )

        activities = [
            Activity(
                id="act_1",
                name="Test Activity",
                priority=ActivityPriority.HIGH,
                duration_hours=2.0,
                acceptable_venues=["hall_a"],
                preferred_time_ranges=[
                    (datetime(2024, 1, 1, 9, 0), datetime(2024, 1, 1, 17, 0))
                ],
                min_budget=100.0,
                max_budget=500.0,
                required_staff_count=1,
                expected_participants=50,
                club_id="club_1"
            )
        ]

        result = scheduler.schedule(
            activities,
            planning_horizon_start=datetime(2024, 1, 1, 8, 0),
            planning_horizon_end=datetime(2024, 1, 7, 20, 0)
        )

        assert len(result["scheduled"]) == 1
        assert len(result["unscheduled"]) == 0
        assert result["scheduled"][0].assigned_slot is not None
        assert result["scheduled"][0].assigned_budget >= 100.0

    def test_priority_ordering(self):
        """测试优先级排序"""
        scheduler = HierarchicalScheduler(
            venues=["hall_a"],
            available_staff=["s1"],
            total_budget=1000.0
        )

        activities = [
            Activity(
                id=f"act_{i}",
                name=f"Activity {i}",
                priority=priority,
                duration_hours=2.0,
                acceptable_venues=["hall_a"],
                preferred_time_ranges=[
                    (datetime(2024, 1, 1, 9, 0), datetime(2024, 1, 1, 17, 0))
                ],
                min_budget=50.0,
                max_budget=200.0,
                required_staff_count=1,
                expected_participants=30,
                club_id="club_1"
            )
            for i, priority in enumerate([
                ActivityPriority.LOW,
                ActivityPriority.CRITICAL,
                ActivityPriority.MEDIUM
            ])
        ]

        # 只给一个时间段，应该优先安排CRITICAL
        result = scheduler.schedule(
            activities,
            planning_horizon_start=datetime(2024, 1, 1, 9, 0),
            planning_horizon_end=datetime(2024, 1, 1, 11, 0)
        )

        scheduled_ids = {a.id for a in result["scheduled"]}
        assert "act_1" in scheduled_ids  # CRITICAL优先级应该被安排

    def test_calculate_metrics(self):
        """测试指标计算"""
        scheduler = HierarchicalScheduler(
            venues=["hall_a", "hall_b"],
            available_staff=["s1", "s2"],
            total_budget=10000.0
        )

        activities = [
            Activity(
                id="act_1",
                name="Activity 1",
                priority=ActivityPriority.HIGH,
                duration_hours=4.0,
                acceptable_venues=["hall_a"],
                preferred_time_ranges=[
                    (datetime(2024, 1, 1, 9, 0), datetime(2024, 1, 1, 17, 0))
                ],
                min_budget=500.0,
                max_budget=1000.0,
                required_staff_count=1,
                expected_participants=100,
                club_id="club_1"
            )
        ]

        result = scheduler.schedule(
            activities,
            planning_horizon_start=datetime(2024, 1, 1, 8, 0),
            planning_horizon_end=datetime(2024, 1, 1, 20, 0)
        )

        metrics = result["metrics"]
        assert "venue_utilization" in metrics
        assert "budget_utilization" in metrics
        assert metrics["scheduled_count"] == 1
        assert metrics["avg_budget_per_activity"] >= 500.0
