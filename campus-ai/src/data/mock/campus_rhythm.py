"""
校园时间规律生成器 (Campus Rhythm Generator)

核心概念：
- 活动分布要符合真实的校园节奏
- 避开考试周，周五周六活动多
- 这样LSTM时间序列模型才能学到规律
"""

import random
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import pandas as pd


class CampusRhythmGenerator:
    """
    校园时间规律生成器

    模拟真实校园的时间分布：
    - 学期分布：春/秋季学期
    - 周分布：周五、周六活动最多，周日次之
    - 日分布：晚上和下午最受欢迎
    - 避开考试周（第16-18周）
    """

    # 一周的权重分布（周一到周日）
    WEEKDAY_WEIGHTS = {
        0: 0.08,   # 周一
        1: 0.10,   # 周二
        2: 0.12,   # 周三
        3: 0.12,   # 周四
        4: 0.18,   # 周五 - 最高峰
        5: 0.25,   # 周六 - 最高峰
        6: 0.15,   # 周日
    }

    # 时段权重（24小时）
    HOUR_WEIGHTS = {
        # 早晨 (6-11)
        6: 0.02, 7: 0.03, 8: 0.05, 9: 0.05, 10: 0.04, 11: 0.03,
        # 中午 (12-13)
        12: 0.03, 13: 0.03,
        # 下午 (14-17)
        14: 0.08, 15: 0.10, 16: 0.12, 17: 0.10,
        # 晚上 (18-23)
        18: 0.08, 19: 0.12, 20: 0.10, 21: 0.05, 22: 0.02, 23: 0.01,
        # 深夜 (0-5)
        0: 0.00, 1: 0.00, 2: 0.00, 3: 0.00, 4: 0.00, 5: 0.00,
    }

    # 月份权重（避开寒暑假和考试月）
    MONTH_WEIGHTS = {
        1: 0.05,   # 期末/寒假
        2: 0.02,   # 寒假
        3: 0.10,   # 开学
        4: 0.12,   # 春季学期
        5: 0.12,   # 春季学期
        6: 0.08,   # 期末
        7: 0.02,   # 暑假
        8: 0.02,   # 暑假
        9: 0.12,   # 开学
        10: 0.15,  # 秋季学期
        11: 0.12,  # 秋季学期
        12: 0.08,  # 期末
    }

    def __init__(self, seed: Optional[int] = None, base_year: int = 2023):
        if seed:
            random.seed(seed)
            np.random.seed(seed)

        self.base_year = base_year

        # 预计算考试周日期（简化版）
        self.exam_weeks = self._calculate_exam_weeks()

    def _calculate_exam_weeks(self) -> List[Tuple[datetime, datetime]]:
        """计算考试周时间段"""
        exam_periods = []

        # 春季学期期末（6月第3-4周）
        spring_exam_start = datetime(self.base_year, 6, 15)
        exam_periods.append((spring_exam_start, spring_exam_start + timedelta(days=14)))

        # 秋季学期期末（12月第3-4周）
        fall_exam_start = datetime(self.base_year, 12, 15)
        exam_periods.append((fall_exam_start, fall_exam_start + timedelta(days=14)))

        # 补考周（开学后2周）
        makeup_start = datetime(self.base_year, 3, 1)
        exam_periods.append((makeup_start, makeup_start + timedelta(days=14)))

        return exam_periods

    def is_exam_period(self, date: datetime) -> bool:
        """判断日期是否在考试周"""
        for start, end in self.exam_weeks:
            if start <= date <= end:
                return True
        return False

    def is_holiday(self, date: datetime) -> bool:
        """判断是否是假期（简化版）"""
        month = date.month
        # 寒暑假月份
        if month in [1, 2, 7, 8]:
            return True
        return False

    def generate_activity_datetime(
        self,
        count: int = 1,
        preferred_hours: Optional[Dict[int, float]] = None,
        avoid_exam: bool = True
    ) -> List[Tuple[datetime, datetime]]:
        """
        生成活动时间

        Args:
            count: 生成数量
            preferred_hours: 偏好的时段（基于角色）
            avoid_exam: 是否避开考试周

        Returns:
            [(start_time, end_time), ...]
        """
        results = []

        # 使用自定义时段权重或默认
        hour_weights = preferred_hours or self.HOUR_WEIGHTS
        hours = list(hour_weights.keys())
        hour_probs = list(hour_weights.values())

        # 归一化概率
        total = sum(hour_probs)
        hour_probs = [p / total for p in hour_probs]

        # 生成日期范围（近2年）
        end_date = datetime.now()
        start_date = end_date - timedelta(days=730)

        for _ in range(count):
            # 生成日期（考虑月份权重）
            date = self._generate_weighted_date(start_date, end_date, avoid_exam)

            # 生成时段
            hour = np.random.choice(hours, p=hour_probs)
            minute = random.choice([0, 15, 30, 45])

            start_time = date.replace(hour=hour, minute=minute)

            # 活动时长（根据类型不同）
            duration_hours = self._generate_duration()
            end_time = start_time + timedelta(hours=duration_hours)

            results.append((start_time, end_time))

        return results

    def _generate_weighted_date(
        self,
        start_date: datetime,
        end_date: datetime,
        avoid_exam: bool
    ) -> datetime:
        """根据权重生成日期"""
        max_attempts = 100

        for _ in range(max_attempts):
            # 随机选择日期
            days_range = (end_date - start_date).days
            random_days = random.randint(0, days_range)
            date = start_date + timedelta(days=random_days)

            # 检查条件
            if avoid_exam and self.is_exam_period(date):
                continue

            if self.is_holiday(date):
                # 假期降低概率但不是完全排除
                if random.random() > 0.2:  # 80%概率跳过
                    continue

            # 检查周权重（周五周六概率更高）
            weekday = date.weekday()
            if random.random() > self.WEEKDAY_WEIGHTS.get(weekday, 0.1):
                continue

            # 检查月份权重
            month_weight = self.MONTH_WEIGHTS.get(date.month, 0.1)
            if random.random() > month_weight:
                continue

            return date

        # 如果重试多次失败，返回一个随机日期
        days_range = (end_date - start_date).days
        return start_date + timedelta(days=random.randint(0, days_range))

    def _generate_duration(self) -> float:
        """生成活动时长"""
        # 时长分布：1小时(15%), 2小时(40%), 3小时(30%), 4小时(15%)
        durations = [1, 2, 3, 4]
        weights = [0.15, 0.40, 0.30, 0.15]
        return float(np.random.choice(durations, p=weights))

    def generate_time_series_features(self, df: pd.DataFrame, datetime_col: str = 'start_time') -> pd.DataFrame:
        """
        为DataFrame添加时间序列特征

        生成的特征：
        - is_weekend: 是否周末
        - is_exam_period: 是否考试周
        - semester: 学期（spring/fall）
        - week_of_semester: 学期第几周
        - time_slot: 时段标签
        """
        df = df.copy()

        # 确保是datetime类型
        df[datetime_col] = pd.to_datetime(df[datetime_col])

        # 基础时间特征
        df['year'] = df[datetime_col].dt.year
        df['month'] = df[datetime_col].dt.month
        df['day'] = df[datetime_col].dt.day
        df['hour'] = df[datetime_col].dt.hour
        df['weekday'] = df[datetime_col].dt.weekday
        df['weekofyear'] = df[datetime_col].dt.isocalendar().week

        # 校园特定特征
        df['is_weekend'] = df['weekday'].isin([5, 6])
        df['is_friday'] = df['weekday'] == 4
        df['is_exam_period'] = df[datetime_col].apply(self.is_exam_period)

        # 学期
        df['semester'] = df['month'].apply(
            lambda m: 'spring' if m in [3, 4, 5, 6] else
                     'fall' if m in [9, 10, 11, 12] else
                     'winter_summer'
        )

        # 时段标签
        def get_time_slot(hour):
            if 6 <= hour < 12:
                return 'morning'
            elif 12 <= hour < 14:
                return 'noon'
            elif 14 <= hour < 18:
                return 'afternoon'
            elif 18 <= hour < 22:
                return 'evening'
            else:
                return 'night'

        df['time_slot'] = df['hour'].apply(get_time_slot)

        # 学期周数（简化计算）
        df['week_of_semester'] = df.apply(self._calculate_week_of_semester, axis=1)

        return df

    def _calculate_week_of_semester(self, row) -> int:
        """计算学期第几周"""
        month = row['month']
        day = row['day']

        if row['semester'] == 'spring':
            # 春季学期从3月1日开始
            start = datetime(row['year'], 3, 1)
        elif row['semester'] == 'fall':
            # 秋季学期从9月1日开始
            start = datetime(row['year'], 9, 1)
        else:
            return -1

        current = datetime(row['year'], month, day)
        week = (current - start).days // 7 + 1
        return max(1, min(week, 20))  # 限制在1-20周

    def get_rhythm_stats(self, dates: List[datetime]) -> Dict:
        """获取时间分布统计"""
        df = pd.DataFrame({'date': dates})
        df['date'] = pd.to_datetime(df['date'])
        df['weekday'] = df['date'].dt.weekday
        df['hour'] = df['date'].dt.hour
        df['month'] = df['date'].dt.month

        return {
            'weekday_distribution': df['weekday'].value_counts().to_dict(),
            'hour_distribution': df['hour'].value_counts().to_dict(),
            'month_distribution': df['month'].value_counts().to_dict(),
            'exam_period_ratio': sum(1 for d in dates if self.is_exam_period(d)) / len(dates),
            'weekend_ratio': sum(1 for d in dates if d.weekday() in [5, 6]) / len(dates),
        }


# 便捷函数
def generate_campus_activity_times(
    count: int = 100,
    seed: int = 42,
    preferred_hours: Optional[Dict[int, float]] = None
) -> List[Tuple[datetime, datetime]]:
    """
    快速生成符合校园规律的活动时间

    示例：
        >>> times = generate_campus_activity_times(100)
        >>> print(f"周五活动数: {sum(1 for t in times if t[0].weekday() == 4)}")
    """
    generator = CampusRhythmGenerator(seed=seed)
    return generator.generate_activity_datetime(count, preferred_hours)


if __name__ == '__main__':
    # 测试生成
    print("生成100个活动时间...")
    generator = CampusRhythmGenerator(seed=42)
    times = generator.generate_activity_datetime(100)

    print(f"\n总计生成: {len(times)} 个时间段")

    # 统计分布
    dates = [t[0] for t in times]
    stats = generator.get_rhythm_stats(dates)

    print("\n星期分布:")
    weekdays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    for i, count in sorted(stats['weekday_distribution'].items()):
        print(f"  {weekdays[i]}: {count}")

    print(f"\n周末占比: {stats['weekend_ratio']:.1%}")
    print(f"考试周占比: {stats['exam_period_ratio']:.1%}")
