"""测试资源冲突注入器"""

import pytest
import pandas as pd
from datetime import datetime, timedelta


class TestConflictInjector:
    """测试冲突注入器"""

    def test_conflict_injection_basic(self):
        """测试基本冲突注入"""
        from data.mock.conflict_injector import ConflictInjector

        # 创建测试活动（周五下午）
        activities = []
        base_time = datetime(2024, 3, 15, 15, 0)  # 周五下午3点

        for i in range(10):
            activities.append({
                'activity_id': f'ACT{i:03d}',
                'start_time': base_time + timedelta(minutes=i*10),
                'activity_type': 'lecture',
                'participant_count': 50
            })

        df = pd.DataFrame(activities)

        injector = ConflictInjector(seed=42)
        df_with_conflicts = injector.inject_conflicts(df)

        # 检查是否标记了冲突
        assert 'resource_conflict' in df_with_conflicts.columns
        assert 'resource_type' in df_with_conflicts.columns
        assert 'resource_id' in df_with_conflicts.columns

    def test_conflict_severity(self):
        """测试冲突严重程度"""
        from data.mock.conflict_injector import ConflictInjector

        activities = []
        base_time = datetime(2024, 3, 15, 15, 0)  # 周五下午

        for i in range(20):
            activities.append({
                'activity_id': f'ACT{i:03d}',
                'start_time': base_time + timedelta(minutes=i*5),
                'activity_type': 'lecture',
                'participant_count': 50
            })

        df = pd.DataFrame(activities)

        injector = ConflictInjector(seed=42)
        df_with_conflicts = injector.inject_conflicts(df, intensity=2.0)

        # 应该有严重冲突
        max_severity = df_with_conflicts['conflict_severity'].max()
        assert max_severity > 0

    def test_get_conflict_summary(self):
        """测试冲突摘要"""
        from data.mock.conflict_injector import ConflictInjector

        activities = []
        base_time = datetime(2024, 3, 15, 15, 0)

        for i in range(15):
            activities.append({
                'activity_id': f'ACT{i:03d}',
                'start_time': base_time + timedelta(minutes=i*10),
                'activity_type': 'lecture',
                'participant_count': 50
            })

        df = pd.DataFrame(activities)

        injector = ConflictInjector(seed=42)
        injector.inject_conflicts(df)

        summary = injector.get_conflict_summary()

        assert 'total_scenarios' in summary
        assert 'total_affected_activities' in summary

    def test_default_resource_assignment(self):
        """测试非冲突活动的默认资源分配"""
        from data.mock.conflict_injector import ConflictInjector

        activities = []
        base_time = datetime(2024, 3, 13, 10, 0)  # 周三上午（非热门时段）

        for i in range(5):
            activities.append({
                'activity_id': f'ACT{i:03d}',
                'start_time': base_time + timedelta(hours=i),
                'activity_type': 'sports',
                'participant_count': 30
            })

        df = pd.DataFrame(activities)

        injector = ConflictInjector(seed=42)
        df_with_conflicts = injector.inject_conflicts(df)

        # 所有活动都应该有资源类型
        assert df_with_conflicts['resource_type'].notna().all()
        assert df_with_conflicts['resource_id'].notna().all()


class TestResourceSchedulerTestCase:
    """测试GA算法测试用例生成器"""

    def test_extreme_conflict_case(self):
        """测试极端冲突场景"""
        from data.mock.conflict_injector import ResourceSchedulerTestCase

        test_gen = ResourceSchedulerTestCase()
        df = test_gen.create_extreme_conflict_case(
            num_activities=10,
            num_resources=2
        )

        assert len(df) == 10
        assert 'start_time' in df.columns
        assert 'duration_hours' in df.columns
        assert 'resource_type' in df.columns

        # 所有活动应该有相同的资源类型
        assert df['resource_type'].nunique() == 1

    def test_multi_resource_case(self):
        """测试多资源类型场景"""
        from data.mock.conflict_injector import ResourceSchedulerTestCase

        test_gen = ResourceSchedulerTestCase()
        df = test_gen.create_multi_resource_case()

        # 应该包含多种资源类型
        resource_types = df['resource_type'].unique()
        assert len(resource_types) >= 2

        # 应该有体育馆、教室、礼堂等
        assert 'gym' in resource_types or 'classroom' in resource_types or 'auditorium' in resource_types


class TestQuickInject:
    """测试便捷函数"""

    def test_inject_resource_conflicts(self):
        """测试快速注入函数"""
        from data.mock.conflict_injector import inject_resource_conflicts

        df = pd.DataFrame({
            'activity_id': [f'ACT{i:03d}' for i in range(20)],
            'start_time': pd.date_range('2024-03-15 15:00', periods=20, freq='10min'),
            'activity_type': ['lecture'] * 20,
            'participant_count': [50] * 20
        })

        df_with_conflicts = inject_resource_conflicts(df, seed=42)

        assert 'resource_conflict' in df_with_conflicts.columns
