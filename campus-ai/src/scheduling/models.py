# campus-ai/src/scheduling/models.py

from dataclasses import dataclass, field
from typing import List, Tuple, Optional
from datetime import datetime
from enum import Enum


class ActivityPriority(Enum):
    """活动优先级枚举"""
    CRITICAL = 4    # 校级重大活动
    HIGH = 3        # 重要社团活动
    MEDIUM = 2      # 常规活动
    LOW = 1         # 小型活动


@dataclass
class TimeSlot:
    """时间槽 - 调度的基本单元"""
    venue_id: str
    start_time: datetime
    end_time: datetime
    duration_hours: float = field(init=False)

    def __post_init__(self):
        self.duration_hours = (self.end_time - self.start_time).total_seconds() / 3600

    def conflicts_with(self, other: 'TimeSlot') -> bool:
        """检查时间冲突"""
        if self.venue_id != other.venue_id:
            return False
        return not (self.end_time <= other.start_time or self.start_time >= other.end_time)


@dataclass
class Activity:
    """活动定义"""
    id: str
    name: str
    priority: ActivityPriority
    duration_hours: float
    acceptable_venues: List[str]
    preferred_time_ranges: List[Tuple[datetime, datetime]]
    min_budget: float
    max_budget: float
    required_staff_count: int
    expected_participants: int
    club_id: str

    # 运行时分配
    assigned_slot: Optional[TimeSlot] = None
    assigned_budget: float = 0.0
    assigned_staff: List[str] = field(default_factory=list)


@dataclass
class VenueSchedule:
    """场地调度表 - 使用区间树思想优化冲突检测"""
    venue_id: str
    slots: List[TimeSlot] = field(default_factory=list)

    def add_slot(self, slot: TimeSlot) -> bool:
        """添加时间槽，返回是否成功"""
        if self._has_conflict(slot):
            return False

        # 插入并保持有序
        idx = self._find_insert_position(slot)
        self.slots.insert(idx, slot)
        return True

    def _has_conflict(self, slot: TimeSlot) -> bool:
        """使用二分查找检测冲突: O(log n)"""
        if not self.slots:
            return False

        idx = self._find_insert_position(slot)

        # 只检查相邻的几个槽位
        check_range = range(max(0, idx - 2), min(len(self.slots), idx + 2))
        for i in check_range:
            if self.slots[i].conflicts_with(slot):
                return True
        return False

    def _find_insert_position(self, slot: TimeSlot) -> int:
        """二分查找插入位置"""
        left, right = 0, len(self.slots)
        while left < right:
            mid = (left + right) // 2
            if self.slots[mid].start_time < slot.start_time:
                left = mid + 1
            else:
                right = mid
        return left

    def get_utilization(self, start: datetime, end: datetime) -> float:
        """计算时间段内的场地利用率"""
        total_hours = (end - start).total_seconds() / 3600
        if total_hours == 0:
            return 0.0

        occupied_hours = sum(
            s.duration_hours for s in self.slots
            if s.start_time >= start and s.end_time <= end
        )
        return occupied_hours / total_hours
