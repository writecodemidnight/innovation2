"""
脏数据注入器 (Dirty Data Injector)

核心概念：
- 故意制造5%的脏数据
- 测试DataCleaner是否真的能发现问题并修复
- 模拟真实世界中常见的数据质量问题
"""

import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Callable
from enum import Enum


class DirtyDataType(Enum):
    """脏数据类型枚举"""
    MISSING_VALUE = "missing"           # 缺失值
    OUT_OF_RANGE = "out_of_range"       # 超出范围
    WRONG_FORMAT = "wrong_format"       # 格式错误
    DUPLICATE = "duplicate"             # 重复数据
    INCONSISTENT = "inconsistent"       # 不一致数据
    TYPO = "typo"                       # 拼写错误
    WRONG_TYPE = "wrong_type"           # 类型错误


class DirtyDataInjector:
    """
    脏数据注入器

    在干净数据中注入各种"脏数据"，用于测试数据清洗流程。

    注入类型：
    1. 缺失值 (5%): 随机删除某些字段
    2. 异常值 (3%): 超出合理范围的数值
    3. 格式错误 (2%): 日期格式混乱、字符串乱码
    4. 重复数据 (1%): 完全重复或部分重复的记录
    5. 不一致 (2%): 逻辑矛盾的数据（如结束时间早于开始时间）
    6. 拼写错误 (2%): 随机字符替换
    """

    # 默认污染比例
    DEFAULT_RATIOS = {
        DirtyDataType.MISSING_VALUE: 0.05,    # 5%
        DirtyDataType.OUT_OF_RANGE: 0.03,     # 3%
        DirtyDataType.WRONG_FORMAT: 0.02,     # 2%
        DirtyDataType.DUPLICATE: 0.01,        # 1%
        DirtyDataType.INCONSISTENT: 0.02,     # 2%
        DirtyDataType.TYPO: 0.02,             # 2%
    }

    def __init__(
        self,
        seed: Optional[int] = None,
        dirty_ratios: Optional[Dict[DirtyDataType, float]] = None
    ):
        if seed:
            random.seed(seed)
            np.random.seed(seed)

        self.dirty_ratios = dirty_ratios or self.DEFAULT_RATIOS.copy()
        self.injection_log = []  # 记录注入的脏数据

    def inject_dirty_data(
        self,
        df: pd.DataFrame,
        table_name: str = "unknown"
    ) -> pd.DataFrame:
        """
        向DataFrame注入脏数据

        Args:
            df: 干净的DataFrame
            table_name: 表名（用于日志）

        Returns:
            被污染的DataFrame
        """
        df_dirty = df.copy()
        total_rows = len(df_dirty)

        # 为每种脏数据类型选择目标行
        for dirty_type, ratio in self.dirty_ratios.items():
            num_to_inject = max(1, int(total_rows * ratio))
            target_indices = random.sample(
                list(df_dirty.index),
                min(num_to_inject, total_rows)
            )

            for idx in target_indices:
                original_value = df_dirty.loc[idx].to_dict()
                df_dirty, changes = self._apply_dirty_type(
                    df_dirty, idx, dirty_type
                )

                if changes:
                    self.injection_log.append({
                        'table': table_name,
                        'row_index': idx,
                        'dirty_type': dirty_type.value,
                        'changes': changes,
                        'original': original_value
                    })

        return df_dirty

    def _apply_dirty_type(
        self,
        df: pd.DataFrame,
        idx: int,
        dirty_type: DirtyDataType
    ) -> tuple[pd.DataFrame, Dict]:
        """应用特定类型的脏数据"""

        changes = {}

        if dirty_type == DirtyDataType.MISSING_VALUE:
            df, changes = self._inject_missing_value(df, idx)
        elif dirty_type == DirtyDataType.OUT_OF_RANGE:
            df, changes = self._inject_out_of_range(df, idx)
        elif dirty_type == DirtyDataType.WRONG_FORMAT:
            df, changes = self._inject_wrong_format(df, idx)
        elif dirty_type == DirtyDataType.DUPLICATE:
            df, changes = self._inject_duplicate(df, idx)
        elif dirty_type == DirtyDataType.INCONSISTENT:
            df, changes = self._inject_inconsistent(df, idx)
        elif dirty_type == DirtyDataType.TYPO:
            df, changes = self._inject_typo(df, idx)

        return df, changes

    def _inject_missing_value(self, df: pd.DataFrame, idx: int) -> tuple[pd.DataFrame, Dict]:
        """注入缺失值"""
        # 随机选择一个可空的列
        nullable_cols = [c for c in df.columns if c not in ['id', 'student_id', 'activity_id']]
        if not nullable_cols:
            return df, {}

        col = random.choice(nullable_cols)
        original = df.at[idx, col]
        df.at[idx, col] = np.nan if pd.api.types.is_numeric_dtype(df[col]) else None

        return df, {col: {'from': original, 'to': 'NULL'}}

    def _inject_out_of_range(self, df: pd.DataFrame, idx: int) -> tuple[pd.DataFrame, Dict]:
        """注入超出范围的值"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns

        if len(numeric_cols) == 0:
            return df, {}

        col = random.choice(numeric_cols)
        original = df.at[idx, col]

        # 根据列名推断合理范围并制造异常
        if 'count' in col or 'participant' in col:
            new_value = random.choice([-10, -5, 9999, 100000])
        elif 'budget' in col or 'amount' in col:
            new_value = random.choice([-1000, -500, 1000000, 9999999])
        elif 'score' in col or 'rating' in col:
            new_value = random.choice([-10, -5, 15, 100])
        else:
            multiplier = random.choice([100, -100])
            new_value = (original if pd.notna(original) else 100) * multiplier

        df.at[idx, col] = new_value
        return df, {col: {'from': original, 'to': new_value}}

    def _inject_wrong_format(self, df: pd.DataFrame, idx: int) -> tuple[pd.DataFrame, Dict]:
        """注入格式错误"""
        # 查找日期时间列
        datetime_cols = []
        for col in df.columns:
            if 'time' in col or 'date' in col:
                datetime_cols.append(col)

        if datetime_cols:
            col = random.choice(datetime_cols)
            original = df.at[idx, col]

            # 将日期格式改为字符串错误格式
            wrong_formats = [
                "2024/13/45",  # 无效日期
                "not-a-date",
                "2024-01",
                "",
                "NULL"
            ]
            df.at[idx, col] = random.choice(wrong_formats)
            return df, {col: {'from': str(original), 'to': df.at[idx, col]}}

        # 如果没有日期列，修改字符串列
        string_cols = df.select_dtypes(include=['object']).columns
        if len(string_cols) > 0:
            col = random.choice(string_cols)
            original = df.at[idx, col]
            df.at[idx, col] = "\x00\x01\x02"  # 乱码字符
            return df, {col: {'from': original, 'to': 'CORRUPTED'}}

        return df, {}

    def _inject_duplicate(self, df: pd.DataFrame, idx: int) -> tuple[pd.DataFrame, Dict]:
        """注入重复数据"""
        # 随机复制另一行的数据
        other_idx = random.choice([i for i in df.index if i != idx])

        # 复制部分或全部列
        cols_to_copy = list(df.columns)
        if random.random() > 0.5:  # 50%概率保留ID
            id_cols = [c for c in cols_to_copy if 'id' in c.lower()]
            cols_to_copy = [c for c in cols_to_copy if c not in id_cols]

        for col in cols_to_copy:
            df.at[idx, col] = df.at[other_idx, col]

        return df, {'duplicated_from': other_idx, 'columns': cols_to_copy}

    def _inject_inconsistent(self, df: pd.DataFrame, idx: int) -> tuple[pd.DataFrame, Dict]:
        """注入逻辑不一致"""
        changes = {}

        # 检查是否有开始和结束时间
        if 'start_time' in df.columns and 'end_time' in df.columns:
            start = pd.to_datetime(df.at[idx, 'start_time'], errors='coerce')
            if pd.notna(start):
                # 让结束时间早于开始时间
                end = start - timedelta(hours=random.randint(1, 3))
                original_end = df.at[idx, 'end_time']
                df.at[idx, 'end_time'] = end
                changes['end_time'] = {'from': str(original_end), 'to': str(end)}

        # 检查人数逻辑
        if 'participant_count' in df.columns and 'max_capacity' in df.columns:
            participants = df.at[idx, 'participant_count']
            max_cap = df.at[idx, 'max_capacity']

            if pd.notna(participants) and pd.notna(max_cap):
                # 让参与人数超过容量
                df.at[idx, 'participant_count'] = int(max_cap * random.uniform(1.5, 3))
                changes['participant_count'] = {
                    'from': participants,
                    'to': df.at[idx, 'participant_count']
                }

        return df, changes

    def _inject_typo(self, df: pd.DataFrame, idx: int) -> tuple[pd.DataFrame, Dict]:
        """注入拼写错误"""
        string_cols = df.select_dtypes(include=['object']).columns

        if len(string_cols) == 0:
            return df, {}

        # 选择较短的字符串列（如名称、类型）
        suitable_cols = [c for c in string_cols
                        if df[c].astype(str).str.len().mean() < 50]

        if not suitable_cols:
            return df, {}

        col = random.choice(suitable_cols)
        original = str(df.at[idx, col])

        # 随机替换字符
        if len(original) > 3:
            char_list = list(original)
            pos = random.randint(0, len(char_list) - 1)

            # 常见错误类型
            typo_methods = [
                lambda: char_list.pop(pos),  # 删除字符
                lambda: char_list.insert(pos, random.choice('abcdefghijklmnopqrstuvwxyz')),  # 插入字符
                lambda: char_list.__setitem__(pos, random.choice('abcdefghijklmnopqrstuvwxyz')),  # 替换字符
            ]
            random.choice(typo_methods)()

            new_value = ''.join(char_list)
            df.at[idx, col] = new_value
            return df, {col: {'from': original, 'to': new_value}}

        return df, {}

    def get_injection_report(self) -> pd.DataFrame:
        """获取脏数据注入报告"""
        if not self.injection_log:
            return pd.DataFrame()

        return pd.DataFrame(self.injection_log)

    def get_summary(self) -> Dict:
        """获取注入摘要"""
        if not self.injection_log:
            return {"message": "未注入脏数据"}

        type_counts = {}
        for log in self.injection_log:
            dtype = log['dirty_type']
            type_counts[dtype] = type_counts.get(dtype, 0) + 1

        return {
            'total_injections': len(self.injection_log),
            'injection_by_type': type_counts,
            'tables_affected': len(set(log['table'] for log in self.injection_log))
        }

    def verify_cleaning_effectiveness(
        self,
        df_before: pd.DataFrame,
        df_after: pd.DataFrame,
        quality_checker
    ) -> Dict:
        """
        验证数据清洗效果（左右互搏）

        返回清洗前后的质量分数对比
        """
        report_before = quality_checker.check(df_before, "before_cleaning")
        report_after = quality_checker.check(df_after, "after_cleaning")

        return {
            'before': {
                'overall_score': report_before.overall_score,
                'completeness': report_before.completeness,
                'accuracy': report_before.accuracy,
            },
            'after': {
                'overall_score': report_after.overall_score,
                'completeness': report_after.completeness,
                'accuracy': report_after.accuracy,
            },
            'improvement': {
                'overall': report_after.overall_score - report_before.overall_score,
                'completeness': report_after.completeness - report_before.completeness,
                'accuracy': report_after.accuracy - report_before.accuracy,
            }
        }


# 便捷函数
def inject_dirty_data(
    df: pd.DataFrame,
    dirty_ratio: float = 0.05,
    seed: int = 42
) -> pd.DataFrame:
    """
    快速注入脏数据

    示例：
        >>> df_dirty = inject_dirty_data(df, dirty_ratio=0.05)
        >>> print(f"脏数据数量: {len(injector.injection_log)}")
    """
    ratios = {DirtyDataType.MISSING_VALUE: dirty_ratio}
    injector = DirtyDataInjector(seed=seed, dirty_ratios=ratios)
    return injector.inject_dirty_data(df)


if __name__ == '__main__':
    # 测试脏数据注入
    print("创建干净测试数据...")
    clean_data = []
    for i in range(100):
        clean_data.append({
            'id': i,
            'name': f'活动-{i}',
            'participant_count': random.randint(10, 100),
            'budget': random.randint(1000, 10000),
            'start_time': datetime(2024, 3, 15, 14, 0),
            'end_time': datetime(2024, 3, 15, 16, 0),
        })

    df_clean = pd.DataFrame(clean_data)
    print(f"干净数据: {len(df_clean)} 行")

    print("\n注入脏数据...")
    injector = DirtyDataInjector(seed=42)
    df_dirty = injector.inject_dirty_data(df_clean, table_name="activities")

    print(f"注入记录数: {len(injector.injection_log)}")

    print("\n注入类型分布:")
    summary = injector.get_summary()
    for dtype, count in summary['injection_by_type'].items():
        print(f"  {dtype}: {count}")

    print("\n部分注入记录:")
    report = injector.get_injection_report()
    print(report[['row_index', 'dirty_type']].head(10).to_string())
