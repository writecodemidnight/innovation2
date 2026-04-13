"""测试脏数据注入器"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime


class TestDirtyDataInjector:
    """测试脏数据注入器"""

    def test_missing_value_injection(self):
        """测试缺失值注入"""
        from data.mock.dirty_data_injector import DirtyDataInjector, DirtyDataType

        df = pd.DataFrame({
            'id': range(100),
            'name': [f'name_{i}' for i in range(100)],
            'value': range(100)
        })

        injector = DirtyDataInjector(
            seed=42,
            dirty_ratios={DirtyDataType.MISSING_VALUE: 0.05}
        )
        df_dirty = injector.inject_dirty_data(df)

        # 应该有缺失值
        assert df_dirty.isnull().sum().sum() > 0

        # 记录注入的日志
        assert len(injector.injection_log) > 0

    def test_out_of_range_injection(self):
        """测试异常值注入"""
        from data.mock.dirty_data_injector import DirtyDataInjector, DirtyDataType

        df = pd.DataFrame({
            'id': range(100),
            'participant_count': [50] * 100,
            'budget': [1000] * 100
        })

        injector = DirtyDataInjector(
            seed=42,
            dirty_ratios={DirtyDataType.OUT_OF_RANGE: 0.05}
        )
        df_dirty = injector.inject_dirty_data(df)

        # 应该有一些异常值
        assert (df_dirty['participant_count'] < 0).any() or (df_dirty['participant_count'] > 1000).any()

    def test_inconsistent_injection(self):
        """测试不一致数据注入"""
        from data.mock.dirty_data_injector import DirtyDataInjector, DirtyDataType

        df = pd.DataFrame({
            'id': range(10),
            'start_time': pd.date_range('2024-03-15 14:00', periods=10, freq='1H'),
            'end_time': pd.date_range('2024-03-15 16:00', periods=10, freq='1H'),
            'participant_count': [50] * 10,
            'max_capacity': [60] * 10
        })

        injector = DirtyDataInjector(
            seed=42,
            dirty_ratios={DirtyDataType.INCONSISTENT: 0.3}
        )
        df_dirty = injector.inject_dirty_data(df)

        # 应该有结束时间早于开始时间的情况
        inconsistent = df_dirty['end_time'] <= df_dirty['start_time']
        assert inconsistent.any()

    def test_typo_injection(self):
        """测试拼写错误注入"""
        from data.mock.dirty_data_injector import DirtyDataInjector, DirtyDataType

        df = pd.DataFrame({
            'id': range(100),
            'name': ['activity_name'] * 100
        })

        injector = DirtyDataInjector(
            seed=42,
            dirty_ratios={DirtyDataType.TYPO: 0.1}
        )
        df_dirty = injector.inject_dirty_data(df)

        # 应该有一些名称被修改
        modified = (df_dirty['name'] != 'activity_name').sum()
        assert modified > 0

    def test_injection_report(self):
        """测试注入报告"""
        from data.mock.dirty_data_injector import DirtyDataInjector, DirtyDataType

        df = pd.DataFrame({
            'id': range(100),
            'name': [f'name_{i}' for i in range(100)],
            'value': range(100)
        })

        injector = DirtyDataInjector(seed=42)
        df_dirty = injector.inject_dirty_data(df)

        report = injector.get_injection_report()
        summary = injector.get_summary()

        assert len(report) > 0
        assert summary['total_injections'] > 0

    def test_verify_cleaning_effectiveness(self):
        """测试清洗效果验证"""
        from data.mock.dirty_data_injector import DirtyDataInjector
        from data.quality import DataQualityChecker

        # 创建干净数据
        df_clean = pd.DataFrame({
            'id': range(50),
            'name': [f'name_{i}' for i in range(50)],
            'value': range(50)
        })

        # 注入脏数据
        injector = DirtyDataInjector(seed=42)
        df_dirty = injector.inject_dirty_data(df_clean)

        # 模拟清洗（这里简单复制，实际应该调用DataCleaner）
        df_cleaned = df_dirty.copy()
        df_cleaned['value'] = df_cleaned['value'].fillna(df_cleaned['value'].median())

        # 验证效果
        checker = DataQualityChecker()
        effectiveness = injector.verify_cleaning_effectiveness(
            df_dirty, df_cleaned, checker
        )

        assert 'before' in effectiveness
        assert 'after' in effectiveness
        assert 'improvement' in effectiveness


class TestQuickInject:
    """测试便捷函数"""

    def test_inject_dirty_data(self):
        """测试快速注入函数"""
        from data.mock.dirty_data_injector import inject_dirty_data

        df = pd.DataFrame({
            'id': range(100),
            'value': range(100)
        })

        df_dirty = inject_dirty_data(df, dirty_ratio=0.1, seed=42)

        # 应该有缺失值
        assert df_dirty.isnull().sum().sum() > 0
