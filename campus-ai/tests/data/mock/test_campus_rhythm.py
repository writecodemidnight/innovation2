"""测试校园时间规律生成器"""

import pytest
import pandas as pd
from datetime import datetime


class TestCampusRhythmGenerator:
    """测试校园时间规律生成器"""

    def test_exam_period_detection(self):
        """测试考试周检测"""
        from data.mock.campus_rhythm import CampusRhythmGenerator

        gen = CampusRhythmGenerator(seed=42, base_year=2024)

        # 6月中旬应该是考试周
        exam_date = datetime(2024, 6, 20)
        assert gen.is_exam_period(exam_date) is True

        # 3月初应该是正常上课
        normal_date = datetime(2024, 3, 15)
        assert gen.is_exam_period(normal_date) is False

    def test_holiday_detection(self):
        """测试假期检测"""
        from data.mock.campus_rhythm import CampusRhythmGenerator

        gen = CampusRhythmGenerator(seed=42)

        # 寒暑假月份
        assert gen.is_holiday(datetime(2024, 7, 15)) is True
        assert gen.is_holiday(datetime(2024, 2, 10)) is True

        # 非假期月份
        assert gen.is_holiday(datetime(2024, 4, 15)) is False

    def test_generate_activity_datetime(self):
        """测试生成活动时间"""
        from data.mock.campus_rhythm import CampusRhythmGenerator

        gen = CampusRhythmGenerator(seed=42)
        times = gen.generate_activity_datetime(count=100)

        assert len(times) == 100

        # 检查所有时间
        for start, end in times:
            assert end > start  # 结束时间必须晚于开始时间
            assert 6 <= start.hour <= 23  # 活动在合理时段
            assert not gen.is_exam_period(start)  # 避开考试周

    def test_weekend_preference(self):
        """测试周末偏好"""
        from data.mock.campus_rhythm import CampusRhythmGenerator

        gen = CampusRhythmGenerator(seed=42)
        times = gen.generate_activity_datetime(count=500)

        dates = [t[0] for t in times]
        weekend_count = sum(1 for d in dates if d.weekday() in [5, 6])

        # 周末活动应该占较高比例
        weekend_ratio = weekend_count / len(dates)
        assert weekend_ratio > 0.30  # 至少30%

    def test_preferred_hours(self):
        """测试时段偏好"""
        from data.mock.campus_rhythm import CampusRhythmGenerator

        # 自定义时段偏好（晚上）
        evening_hours = {19: 0.3, 20: 0.3, 21: 0.2, 22: 0.2}
        gen = CampusRhythmGenerator(seed=42)

        times = gen.generate_activity_datetime(count=200, preferred_hours=evening_hours)
        hours = [t[0].hour for t in times]

        # 大部分应该在晚上7-10点
        evening_count = sum(1 for h in hours if 19 <= h <= 22)
        assert evening_count / len(hours) > 0.60

    def test_generate_time_series_features(self):
        """测试时间特征生成"""
        from data.mock.campus_rhythm import CampusRhythmGenerator

        gen = CampusRhythmGenerator(seed=42)

        df = pd.DataFrame({
            'start_time': pd.date_range('2024-01-01', periods=10, freq='D')
        })

        df_features = gen.generate_time_series_features(df)

        assert 'is_weekend' in df_features.columns
        assert 'semester' in df_features.columns
        assert 'time_slot' in df_features.columns
        assert 'week_of_semester' in df_features.columns

        # 检查1月1日是否为冬季学期
        assert df_features.loc[0, 'semester'] in ['winter_summer', 'fall']

    def test_get_rhythm_stats(self):
        """测试时间分布统计"""
        from data.mock.campus_rhythm import CampusRhythmGenerator

        gen = CampusRhythmGenerator(seed=42)
        times = gen.generate_activity_datetime(count=200)
        dates = [t[0] for t in times]

        stats = gen.get_rhythm_stats(dates)

        assert 'weekday_distribution' in stats
        assert 'hour_distribution' in stats
        assert 'weekend_ratio' in stats
        assert stats['weekend_ratio'] > 0


class TestQuickGenerate:
    """测试便捷函数"""

    def test_generate_campus_activity_times(self):
        """测试快速生成函数"""
        from data.mock.campus_rhythm import generate_campus_activity_times

        times = generate_campus_activity_times(count=50, seed=42)

        assert len(times) == 50
        assert all(end > start for start, end in times)

    def test_seed_consistency(self):
        """测试种子一致性"""
        from data.mock.campus_rhythm import generate_campus_activity_times

        times1 = generate_campus_activity_times(count=50, seed=42)
        times2 = generate_campus_activity_times(count=50, seed=42)

        for (s1, e1), (s2, e2) in zip(times1, times2):
            assert s1 == s2
            assert e1 == e2
