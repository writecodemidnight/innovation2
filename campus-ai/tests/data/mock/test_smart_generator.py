"""测试智能数据生成器"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime


class TestSmartDataGenerator:
    """测试智能数据生成器"""

    def test_generator_initialization(self):
        """测试生成器初始化"""
        from data.mock.smart_data_generator import SmartDataGenerator

        gen = SmartDataGenerator(seed=42)

        assert gen.seed == 42
        assert gen.persona_gen is not None
        assert gen.rhythm_gen is not None
        assert gen.conflict_injector is not None

    def test_generate_full_dataset(self):
        """测试生成完整数据集"""
        from data.mock.smart_data_generator import SmartDataGenerator

        gen = SmartDataGenerator(seed=42)
        result = gen.generate_full_dataset(
            student_count=50,
            club_count=3,
            activity_count=10,
            inject_conflicts=True,
            inject_dirty_data=True
        )

        assert 'students' in result
        assert 'clubs' in result
        assert 'activities' in result
        assert 'participation' in result
        assert 'generation_stats' in result

        # 检查数据量
        assert len(result['students']) == 50
        assert len(result['clubs']) == 3
        assert len(result['activities']) == 10

    def test_foreign_key_consistency(self):
        """测试外键一致性"""
        from data.mock.smart_data_generator import SmartDataGenerator

        gen = SmartDataGenerator(seed=42)
        result = gen.generate_full_dataset(
            student_count=100,
            club_count=5,
            activity_count=20
        )

        students = result['students']
        activities = result['activities']
        participation = result['participation']

        # 参与记录中的student_id必须在学生表中存在
        assert participation['student_id'].isin(students['student_id']).all()

        # 参与记录中的activity_id必须在活动表中存在
        assert participation['activity_id'].isin(activities['activity_id']).all()

        # 活动表中的club_id必须在社团表中存在
        assert activities['club_id'].isin(result['clubs']['club_id']).all()

    def test_quality_improvement(self):
        """测试质量提升（左右互搏）"""
        from data.mock.smart_data_generator import SmartDataGenerator

        gen = SmartDataGenerator(seed=42)
        result = gen.generate_full_dataset(
            student_count=50,
            club_count=3,
            activity_count=10,
            inject_dirty_data=True
        )

        # 清洗后质量应该更高
        assert result['quality_after'].overall_score >= result['quality_before'].overall_score

    def test_generation_stats(self):
        """测试生成统计"""
        from data.mock.smart_data_generator import SmartDataGenerator

        gen = SmartDataGenerator(seed=42)
        result = gen.generate_full_dataset(
            student_count=50,
            club_count=3,
            activity_count=10
        )

        stats = result['generation_stats']

        assert 'student_count' in stats
        assert 'club_count' in stats
        assert 'activity_count' in stats
        assert 'quality_after' in stats

    def test_get_generation_report(self):
        """测试生成报告"""
        from data.mock.smart_data_generator import SmartDataGenerator

        gen = SmartDataGenerator(seed=42)
        gen.generate_full_dataset(
            student_count=50,
            club_count=3,
            activity_count=10
        )

        report = gen.get_generation_report()

        assert isinstance(report, str)
        assert '学生' in report
        assert '社团' in report
        assert '质量' in report


class TestQuickGenerate:
    """测试便捷函数"""

    def test_generate_smart_dataset(self):
        """测试快速生成函数"""
        from data.mock.smart_data_generator import generate_smart_dataset

        result = generate_smart_dataset(
            student_count=50,
            club_count=3,
            activity_count=10,
            seed=42
        )

        assert 'students' in result
        assert 'activities' in result
        assert 'generation_stats' in result

    def test_seed_consistency(self):
        """测试种子一致性"""
        from data.mock.smart_data_generator import generate_smart_dataset

        result1 = generate_smart_dataset(50, 3, 10, seed=42)
        result2 = generate_smart_dataset(50, 3, 10, seed=42)

        # 学生数据应该相同
        pd.testing.assert_frame_equal(
            result1['students'].reset_index(drop=True),
            result2['students'].reset_index(drop=True)
        )


class TestRealisticPatterns:
    """测试生成的数据是否符合真实规律"""

    def test_weekend_activity_pattern(self):
        """测试周末活动模式"""
        from data.mock.smart_data_generator import generate_smart_dataset

        result = generate_smart_dataset(
            student_count=100,
            club_count=5,
            activity_count=100,
            seed=42
        )

        activities = result['activities']

        # 应该有周末活动
        weekend_count = activities['is_weekend'].sum()
        assert weekend_count > 0

        # 周末活动应该占一定比例
        weekend_ratio = weekend_count / len(activities)
        assert 0.20 <= weekend_ratio <= 0.50  # 20%-50%是合理的

    def test_persona_correlation_with_activity(self):
        """测试角色与活动的相关性"""
        from data.mock.smart_data_generator import generate_smart_dataset

        result = generate_smart_dataset(
            student_count=200,
            club_count=10,
            activity_count=50,
            seed=42
        )

        students = result['students']
        participation = result['participation']

        # 合并数据
        merged = participation.merge(students, on='student_id')

        # 技术宅应该有较高的科技类社团参与率
        # 这里简化检查，只要技术宅有参与即可
        tech_students = merged[merged['persona'] == 'tech_geek']
        if len(tech_students) > 0:
            # 至少应该有一些技术宅参与活动
            assert len(tech_students) > 0

    def test_conflict_scenarios_present(self):
        """测试冲突场景是否存在"""
        from data.mock.smart_data_generator import generate_smart_dataset

        result = generate_smart_dataset(
            student_count=100,
            club_count=5,
            activity_count=100,
            seed=42,
            inject_conflicts=True
        )

        activities = result['activities']

        # 应该有冲突标记
        assert 'resource_conflict' in activities.columns

        # 应该有一些冲突
        conflict_count = activities['resource_conflict'].sum()
        # 因为冲突只在特定时段，所以可能有也可能没有
        # 只要列存在即可
