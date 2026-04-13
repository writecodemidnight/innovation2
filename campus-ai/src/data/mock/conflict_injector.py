"""
资源冲突注入器 (Conflict Injector)

核心概念：
- 故意在热门时段安排过多活动，但资源不足
- 迫使GA遗传算法执行冲突解决逻辑
- 测试算法在高压情况下的表现
"""

import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass


@dataclass
class ResourceConstraint:
    """资源约束配置"""
    resource_type: str
    total_count: int  # 该类型资源总数
    hot_time_slots: List[Tuple[int, int]]  # [(星期几, 小时), ...]
    conflict_ratio: float  # 冲突比例 (例如 3.0 表示3倍需求)


class ConflictInjector:
    """
    资源冲突注入器

    在热门时段故意制造资源冲突，测试GA算法的调度能力。

    冲突场景：
    1. 周五下午：10个活动抢3个多媒体教室
    2. 周六全天：体育馆场地严重不足
    3. 大型活动周：多个社团同时举办大型活动
    """

    # 预定义冲突场景
    CONFLICT_SCENARIOS = {
        'friday_afternoon': {
            'description': '周五下午多媒体教室告急',
            'time_filter': lambda dt: dt.weekday() == 4 and 14 <= dt.hour <= 17,
            'resource_type': 'multimedia_room',
            'resource_count': 3,
            'demand_multiplier': 3.5,  # 需求是供应的3.5倍
        },
        'saturday_gym': {
            'description': '周六体育馆爆满',
            'time_filter': lambda dt: dt.weekday() == 5 and 9 <= dt.hour <= 18,
            'resource_type': 'gym',
            'resource_count': 2,
            'demand_multiplier': 4.0,
        },
        'club_recruitment': {
            'description': '社团招新周',
            'time_filter': lambda dt: dt.month in [9, 3] and dt.day <= 14,
            'resource_type': 'plaza',
            'resource_count': 5,
            'demand_multiplier': 2.5,
        },
        'final_party': {
            'description': '期末晚会扎堆',
            'time_filter': lambda dt: (dt.month == 6 or dt.month == 12) and dt.day >= 20,
            'resource_type': 'auditorium',
            'resource_count': 2,
            'demand_multiplier': 3.0,
        }
    }

    def __init__(self, seed: Optional[int] = None):
        if seed:
            random.seed(seed)
            np.random.seed(seed)

        self.conflict_stats = []

    def inject_conflicts(
        self,
        activities_df: pd.DataFrame,
        conflict_scenarios: Optional[List[str]] = None,
        conflict_intensity: float = 1.0
    ) -> pd.DataFrame:
        """
        向活动数据注入资源冲突

        Args:
            activities_df: 活动DataFrame
            conflict_scenarios: 冲突场景列表，None则使用所有场景
            conflict_intensity: 冲突强度乘数 (1.0 = 正常，2.0 = 双倍冲突)

        Returns:
            添加了资源冲突信息的活动DataFrame
        """
        df = activities_df.copy()

        # 确保有时间字段
        if 'start_time' not in df.columns:
            raise ValueError("activities_df必须包含start_time列")

        df['start_time'] = pd.to_datetime(df['start_time'])

        # 初始化资源分配列
        df['resource_type'] = None
        df['resource_id'] = None
        df['resource_conflict'] = False
        df['conflict_severity'] = 0  # 0-10

        # 确定要应用的冲突场景
        scenarios = conflict_scenarios or list(self.CONFLICT_SCENARIOS.keys())

        for scenario_name in scenarios:
            if scenario_name not in self.CONFLICT_SCENARIOS:
                continue

            scenario = self.CONFLICT_SCENARIOS[scenario_name]
            df = self._apply_conflict_scenario(
                df, scenario, conflict_intensity
            )

        # 为非冲突活动分配默认资源
        df = self._assign_default_resources(df)

        return df

    def _apply_conflict_scenario(
        self,
        df: pd.DataFrame,
        scenario: Dict,
        intensity: float
    ) -> pd.DataFrame:
        """应用单个冲突场景"""

        # 找出符合冲突时段的活动
        mask = df['start_time'].apply(scenario['time_filter'])
        conflict_activities = df[mask].copy()

        if len(conflict_activities) == 0:
            return df

        # 计算需要的资源数量
        available = scenario['resource_count']
        demand = int(len(conflict_activities) * scenario['demand_multiplier'] * intensity)

        # 为这些活动标记冲突
        for idx in conflict_activities.index:
            df.at[idx, 'resource_type'] = scenario['resource_type']
            df.at[idx, 'resource_conflict'] = True

            # 计算冲突严重程度
            severity = min(10, int(demand / available * 3))
            df.at[idx, 'conflict_severity'] = max(
                df.at[idx, 'conflict_severity'],
                severity
            )

        # 分配资源ID（制造冲突：多个活动分配到同一资源）
        resource_ids = [f"{scenario['resource_type']}_{i}" for i in range(available)]

        for i, idx in enumerate(conflict_activities.index):
            # 故意让多个活动共享资源
            resource_idx = i % available
            df.at[idx, 'resource_id'] = resource_ids[resource_idx]

        # 记录冲突统计
        self.conflict_stats.append({
            'scenario': scenario['description'],
            'time_filter': str(scenario['time_filter']),
            'affected_activities': len(conflict_activities),
            'available_resources': available,
            'estimated_demand': demand,
            'conflict_ratio': demand / available if available > 0 else 0
        })

        return df

    def _assign_default_resources(self, df: pd.DataFrame) -> pd.DataFrame:
        """为非冲突活动分配默认资源"""

        default_resources = {
            'lecture': 'classroom',
            'competition': 'hall',
            'exhibition': 'gallery',
            'party': 'activity_room',
            'training': 'training_room',
            'volunteer': 'outdoor',
            'sports': 'sports_field',
            'performance': 'auditorium',
            'recruitment': 'plaza',
            'other': 'general_room'
        }

        for idx, row in df.iterrows():
            if pd.isna(row['resource_type']):
                # 根据活动类型分配默认资源
                activity_type = row.get('activity_type', 'other')
                resource_type = default_resources.get(activity_type, 'general_room')

                df.at[idx, 'resource_type'] = resource_type
                df.at[idx, 'resource_id'] = f"{resource_type}_{random.randint(1, 20)}"

        return df

    def generate_resource_utilization_report(self) -> pd.DataFrame:
        """生成资源利用率报告"""
        if not self.conflict_stats:
            return pd.DataFrame()

        return pd.DataFrame(self.conflict_stats)

    def get_conflict_summary(self) -> Dict:
        """获取冲突摘要统计"""
        if not self.conflict_stats:
            return {"message": "未注入冲突"}

        total_affected = sum(s['affected_activities'] for s in self.conflict_stats)
        avg_conflict_ratio = np.mean([s['conflict_ratio'] for s in self.conflict_stats])

        return {
            'total_scenarios': len(self.conflict_stats),
            'total_affected_activities': total_affected,
            'average_conflict_ratio': round(avg_conflict_ratio, 2),
            'max_conflict_ratio': max(s['conflict_ratio'] for s in self.conflict_stats),
            'scenarios': [s['scenario'] for s in self.conflict_stats]
        }


class ResourceSchedulerTestCase:
    """
    GA算法测试用例生成器

    生成特定的资源调度测试场景，用于验证GA算法
    """

    def __init__(self):
        self.test_cases = []

    def create_extreme_conflict_case(
        self,
        num_activities: int = 20,
        num_resources: int = 3,
        time_slot: Tuple[int, int] = (4, 15)  # 周五下午3点
    ) -> pd.DataFrame:
        """
        创建极端冲突测试用例

        场景：20个活动同时开始，但只有3个场地可用
        """
        activities = []
        base_time = datetime(2024, 3, 15, time_slot[1], 0)  # 周五

        for i in range(num_activities):
            activities.append({
                'activity_id': f'EXTREME_{i:03d}',
                'activity_name': f'冲突测试活动-{i}',
                'start_time': base_time + timedelta(minutes=random.randint(-30, 30)),
                'duration_hours': random.choice([1, 2, 2, 3]),
                'participant_count': random.randint(20, 100),
                'priority': random.choice(['high', 'medium', 'low']),
                'resource_type': 'multimedia_room',
                'resource_id': None  # 待分配
            })

        df = pd.DataFrame(activities)
        df['end_time'] = df['start_time'] + pd.to_timedelta(df['duration_hours'], unit='h')

        return df

    def create_multi_resource_case(self) -> pd.DataFrame:
        """
        创建多资源类型测试用例

        场景：不同类型活动竞争不同类型资源
        """
        base_time = datetime(2024, 3, 16, 10, 0)  # 周六上午

        activities = []

        # 体育馆活动
        for i in range(5):
            activities.append({
                'activity_id': f'GYM_{i:03d}',
                'activity_name': f'体育比赛-{i}',
                'start_time': base_time + timedelta(hours=i),
                'duration_hours': 2,
                'participant_count': 50,
                'resource_type': 'gym',
                'resource_demand': 1
            })

        # 教室活动
        for i in range(8):
            activities.append({
                'activity_id': f'CLS_{i:03d}',
                'activity_name': f'学术讲座-{i}',
                'start_time': base_time + timedelta(hours=i//2),
                'duration_hours': 1.5,
                'participant_count': 30,
                'resource_type': 'classroom',
                'resource_demand': 1
            })

        # 礼堂活动
        for i in range(3):
            activities.append({
                'activity_id': f'AUD_{i:03d}',
                'activity_name': f'文艺演出-{i}',
                'start_time': base_time + timedelta(hours=i*2),
                'duration_hours': 3,
                'participant_count': 200,
                'resource_type': 'auditorium',
                'resource_demand': 1
            })

        df = pd.DataFrame(activities)
        df['end_time'] = df['start_time'] + pd.to_timedelta(df['duration_hours'], unit='h')

        return df


# 便捷函数
def inject_resource_conflicts(
    activities_df: pd.DataFrame,
    seed: int = 42,
    intensity: float = 1.0
) -> pd.DataFrame:
    """
    快速注入资源冲突

    示例：
        >>> df_with_conflicts = inject_resource_conflicts(df, intensity=2.0)
        >>> print(df_with_conflicts['conflict_severity'].value_counts())
    """
    injector = ConflictInjector(seed=seed)
    return injector.inject_conflicts(activities_df, conflict_intensity=intensity)


if __name__ == '__main__':
    # 测试冲突注入
    print("创建测试活动数据...")
    test_data = []
    base_time = datetime(2024, 3, 15, 14, 0)  # 周五下午

    for i in range(30):
        test_data.append({
            'activity_id': f'TEST_{i:03d}',
            'activity_name': f'测试活动-{i}',
            'start_time': base_time + timedelta(minutes=random.randint(0, 180)),
            'activity_type': random.choice(['lecture', 'competition', 'party']),
            'participant_count': random.randint(10, 100)
        })

    df = pd.DataFrame(test_data)

    print("注入资源冲突...")
    injector = ConflictInjector(seed=42)
    df_conflicts = injector.inject_conflicts(df, intensity=1.5)

    print("\n冲突统计:")
    print(f"总活动数: {len(df_conflicts)}")
    print(f"冲突活动数: {df_conflicts['resource_conflict'].sum()}")
    print(f"冲突严重程度分布:")
    print(df_conflicts['conflict_severity'].value_counts().sort_index())

    print("\n冲突场景详情:")
    report = injector.generate_resource_utilization_report()
    print(report.to_string())
