"""
智能数据生成器 (Smart Data Generator)

将所有组件整合，生成比真的还真的数据：
1. 角色模板 - 让学生有真实的兴趣分布
2. 校园时间 - 让活动符合校园节奏
3. 资源冲突 - 测试GA算法的冲突解决
4. 脏数据 - 测试DataCleaner的清洗能力
5. 质量自验证 - 左右互搏验证

使用示例：
    generator = SmartDataGenerator(seed=42)
    result = generator.generate_full_dataset(
        student_count=1000,
        club_count=20,
        activity_count=200,
        inject_conflicts=True,
        inject_dirty_data=True
    )
"""

import random
import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path

from .personas import PersonaGenerator, StudentPersona
from .campus_rhythm import CampusRhythmGenerator
from .conflict_injector import ConflictInjector
from .dirty_data_injector import DirtyDataInjector, DirtyDataType

# 尝试导入已有的清洗和质量检查（如果不可用则使用模拟实现）
import sys
sys.path.append(str(Path(__file__).parent.parent))

try:
    from transformers.cleaner import DataCleaner
    from transformers.feature_engineer import FeatureEngineer
    from quality import DataQualityChecker
    HAS_DATA_PIPELINE = True
except ImportError:
    HAS_DATA_PIPELINE = False
    # 模拟实现
    class MockQualityReport:
        def __init__(self, score):
            self.overall_score = score

    class DataCleaner:
        def clean(self, df, column_strategies=None):
            # 简单的清洗：填充缺失值
            df_clean = df.copy()
            for col in df_clean.columns:
                if df_clean[col].isnull().any():
                    if df_clean[col].dtype in ['int64', 'float64']:
                        df_clean[col] = df_clean[col].fillna(df_clean[col].median())
                    else:
                        df_clean[col] = df_clean[col].fillna('未知')
            return df_clean

    class FeatureEngineer:
        def generate_activity_features(self, df):
            # 简单的特征工程：确保所有列存在
            return df

    class DataQualityChecker:
        def check(self, df, name=None):
            # 计算简单的质量分数
            total_cells = df.size
            null_cells = df.isnull().sum().sum()
            score = max(0, 100 - (null_cells / total_cells * 100)) if total_cells > 0 else 100
            return MockQualityReport(score)

        def get_quality_level(self, score):
            if score >= 90:
                return '优秀'
            elif score >= 80:
                return '良好'
            elif score >= 60:
                return '及格'
            else:
                return '需改进'


class SmartDataGenerator:
    """
    智能数据生成器

    一站式生成完整的校园社团数据集，包含：
    - 学生数据（基于角色模板）
    - 社团数据
    - 活动数据（符合校园时间规律）
    - 资源冲突（可选）
    - 脏数据污染（可选）

    生成后可立即进行：
    - 数据清洗测试
    - 质量评分验证
    """

    # 社团类型映射
    CLUB_TYPES = {
        'tech': {'name': '科技类', 'prefix': ['机器人', '编程', '创客', 'AI']},
        'arts': {'name': '文艺类', 'prefix': ['合唱', '舞蹈', '摄影', '话剧']},
        'sports': {'name': '体育类', 'prefix': ['篮球', '羽毛球', '跑步', '瑜伽']},
        'academic': {'name': '学术类', 'prefix': ['数学', '物理', '英语', '辩论']},
        'public': {'name': '公益类', 'prefix': ['志愿', '环保', '支教', '爱心']},
    }

    def __init__(self, seed: int = 42):
        """
        初始化智能数据生成器

        Args:
            seed: 随机种子，保证可重复性
        """
        self.seed = seed
        random.seed(seed)
        np.random.seed(seed)

        # 初始化各组件
        self.persona_gen = PersonaGenerator(seed=seed)
        self.rhythm_gen = CampusRhythmGenerator(seed=seed)
        self.conflict_injector = ConflictInjector(seed=seed)
        self.dirty_injector = DirtyDataInjector(seed=seed)

        # 初始化清洗和质检工具
        self.cleaner = DataCleaner()
        self.feature_engineer = FeatureEngineer()
        self.quality_checker = DataQualityChecker()

        # 数据缓存
        self.students_df = None
        self.clubs_df = None
        self.activities_df = None
        self.participation_df = None

        # 生成统计
        self.generation_stats = {}

    def generate_full_dataset(
        self,
        student_count: int = 1000,
        club_count: int = 20,
        activity_count: int = 200,
        persona_distribution: Optional[Dict[str, float]] = None,
        inject_conflicts: bool = True,
        inject_dirty_data: bool = True,
        dirty_data_ratio: float = 0.05,
        output_dir: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        生成完整数据集

        Args:
            student_count: 学生数量
            club_count: 社团数量
            activity_count: 活动数量
            persona_distribution: 角色分布，None则使用默认
            inject_conflicts: 是否注入资源冲突
            inject_dirty_data: 是否注入脏数据
            dirty_data_ratio: 脏数据比例
            output_dir: 输出目录，None则不保存

        Returns:
            {
                'students': DataFrame,
                'clubs': DataFrame,
                'activities': DataFrame,
                'participation': DataFrame,
                'quality_report': QualityReport,
                'generation_stats': dict
            }
        """
        print(f"[开始] 生成智能数据集 (seed={self.seed})")
        print(f"   学生: {student_count} | 社团: {club_count} | 活动: {activity_count}")

        start_time = datetime.now()

        # Step 1: 生成基础数据
        print("\n[步骤1] 生成学生数据 (基于角色模板)...")
        self.students_df = self._generate_students(student_count, persona_distribution)

        print("[步骤2] 生成社团数据...")
        self.clubs_df = self._generate_clubs(club_count)

        print("[步骤3] 生成活动数据 (符合校园时间规律)...")
        self.activities_df = self._generate_activities(activity_count)

        print("[步骤4] 生成参与记录 (保持外键一致性)...")
        self.participation_df = self._generate_participation()

        # Step 2: 注入资源冲突（测试GA算法）
        if inject_conflicts:
            print("\n[步骤5] 注入资源冲突...")
            self.activities_df = self.conflict_injector.inject_conflicts(
                self.activities_df, conflict_intensity=1.5
            )
            conflict_summary = self.conflict_injector.get_conflict_summary()
            print(f"   冲突场景: {conflict_summary.get('total_scenarios', 0)}")
            print(f"   受影响活动: {conflict_summary.get('total_affected_activities', 0)}")

        # Step 3: 注入脏数据（测试DataCleaner）
        dirty_report = None
        if inject_dirty_data:
            print("\n[步骤6] 注入脏数据 (5%污染)...")

            # 调整脏数据比例
            dirty_ratios = {
                DirtyDataType.MISSING_VALUE: dirty_data_ratio * 0.4,
                DirtyDataType.OUT_OF_RANGE: dirty_data_ratio * 0.3,
                DirtyDataType.INCONSISTENT: dirty_data_ratio * 0.2,
                DirtyDataType.TYPO: dirty_data_ratio * 0.1,
            }
            self.dirty_injector = DirtyDataInjector(seed=self.seed, dirty_ratios=dirty_ratios)

            # 只对活动数据注入脏数据
            self.activities_df = self.dirty_injector.inject_dirty_data(
                self.activities_df, table_name="activities"
            )
            dirty_report = self.dirty_injector.get_summary()
            print(f"   注入记录: {dirty_report.get('total_injections', 0)}")

        # Step 4: 质量检查（清洗前）
        print("\n[步骤7] 质量检查 (清洗前)...")
        quality_before = self.quality_checker.check(self.activities_df, "activities_dirty")
        print(f"   质量评分: {quality_before.overall_score:.1f}/100")
        print(f"   等级: {self.quality_checker.get_quality_level(quality_before.overall_score)}")

        # Step 5: 数据清洗（左右互搏）
        print("\n[步骤8] 执行数据清洗...")
        self.activities_df = self._clean_activities(self.activities_df)

        # Step 6: 特征工程
        print("[步骤9] 特征工程...")
        self.activities_df = self._engineer_features(self.activities_df)

        # Step 7: 质量检查（清洗后）
        print("\n[步骤10] 质量检查 (清洗后)...")
        quality_after = self.quality_checker.check(self.activities_df, "activities_clean")
        print(f"   质量评分: {quality_after.overall_score:.1f}/100")
        print(f"   等级: {self.quality_checker.get_quality_level(quality_after.overall_score)}")

        improvement = quality_after.overall_score - quality_before.overall_score
        print(f"   提升: {improvement:+.1f}分")

        # 记录统计
        end_time = datetime.now()
        self.generation_stats = {
            'generation_time_seconds': (end_time - start_time).total_seconds(),
            'student_count': len(self.students_df),
            'club_count': len(self.clubs_df),
            'activity_count': len(self.activities_df),
            'participation_count': len(self.participation_df),
            'quality_before': quality_before.overall_score,
            'quality_after': quality_after.overall_score,
            'quality_improvement': improvement,
            'conflicts_injected': inject_conflicts,
            'dirty_data_injected': inject_dirty_data,
            'dirty_data_count': dirty_report.get('total_injections', 0) if dirty_report else 0,
        }

        # 保存到文件
        if output_dir:
            self._save_to_files(output_dir)

        print("\n" + "="*50)
        print("智能数据生成完成!")
        print("="*50)

        return {
            'students': self.students_df,
            'clubs': self.clubs_df,
            'activities': self.activities_df,
            'participation': self.participation_df,
            'quality_before': quality_before,
            'quality_after': quality_after,
            'generation_stats': self.generation_stats,
        }

    def _generate_students(self, count: int, distribution: Optional[Dict] = None) -> pd.DataFrame:
        """生成学生数据"""
        df = self.persona_gen.generate_students(count, distribution)

        # 添加额外字段
        df['email'] = df['student_id'].apply(lambda x: f"{x}@campus.edu.cn")
        df['phone'] = df.apply(lambda _: self._generate_phone(), axis=1)

        return df

    def _generate_clubs(self, count: int) -> pd.DataFrame:
        """生成社团数据"""
        clubs = []

        for i in range(count):
            club_type = random.choice(list(self.CLUB_TYPES.keys()))
            type_info = self.CLUB_TYPES[club_type]
            prefix = random.choice(type_info['prefix'])

            founding_year = random.randint(2015, 2023)
            age = 2024 - founding_year
            member_base = random.randint(20, 80)
            member_count = member_base + age * random.randint(2, 8)

            # 星级与规模相关
            if member_count > 100:
                rating = random.choices([4, 5], weights=[30, 70])[0]
            elif member_count > 50:
                rating = random.choices([3, 4, 5], weights=[20, 50, 30])[0]
            else:
                rating = random.choices([2, 3, 4], weights=[20, 50, 30])[0]

            clubs.append({
                'club_id': f"CLUB{1000 + i:04d}",
                'club_name': f"{prefix}社",
                'club_type': club_type,
                'club_type_name': type_info['name'],
                'description': f"这是一个{type_info['name']}社团，致力于{prefix}相关的活动。",
                'founding_year': founding_year,
                'member_count': min(member_count, 150),
                'rating': rating,
                'advisor_name': f"指导教师-{i}",
                'contact_email': f"club{1000+i}@campus.edu.cn",
                'status': random.choices(['active', 'inactive'], weights=[90, 10])[0],
            })

        return pd.DataFrame(clubs)

    def _generate_activities(self, count: int) -> pd.DataFrame:
        """生成活动数据"""
        activities = []

        # 生成符合校园规律的时间
        time_slots = self.rhythm_gen.generate_activity_datetime(
            count=count,
            preferred_hours=None,  # 使用默认时段
            avoid_exam=True
        )

        for i, (start_time, end_time) in enumerate(time_slots):
            # 随机选择社团
            club = self.clubs_df.sample(1).iloc[0]
            club_id = club['club_id']
            club_type = club['club_type']

            # 参与人数（基于社团规模）
            member_count = club['member_count']
            participation_rate = random.uniform(0.2, 0.8)
            participant_count = int(member_count * participation_rate)
            participant_count = max(10, participant_count)

            # 预算
            budget_per_person = random.randint(10, 100)
            budget_amount = participant_count * budget_per_person

            # 活动类型与社团类型相关
            activity_type = self._get_activity_type_by_club(club_type)

            activities.append({
                'activity_id': f"ACT{10000 + i:05d}",
                'club_id': club_id,
                'activity_name': f"{activity_type}-{i}",
                'activity_type': activity_type,
                'description': f"这是一个{activity_type}活动，欢迎参加！",
                'start_time': start_time,
                'end_time': end_time,
                'location': f"场地-{random.randint(1, 50)}",
                'participant_count': participant_count,
                'max_capacity': int(participant_count * random.uniform(1.2, 1.5)),
                'budget_amount': budget_amount,
                'status': random.choices(
                    ['completed', 'ongoing', 'cancelled'],
                    weights=[70, 20, 10]
                )[0],
            })

        df = pd.DataFrame(activities)

        # 添加时间特征
        df = self.rhythm_gen.generate_time_series_features(df)

        return df

    def _generate_participation(self) -> pd.DataFrame:
        """生成活动参与记录（保持外键一致性）"""
        participation_records = []

        for _, activity in self.activities_df.iterrows():
            activity_id = activity['activity_id']
            participant_count = activity['participant_count']

            # 从学生中随机选择参与者
            participants = self.students_df.sample(
                n=min(participant_count, len(self.students_df)),
                replace=False
            )

            for _, student in participants.iterrows():
                # 根据学生的feedback_style决定评分倾向
                feedback_style = student.get('feedback_style', 'balanced')

                if feedback_style == 'positive':
                    rating = random.choices([4, 5], weights=[30, 70])[0]
                elif feedback_style == 'critical':
                    rating = random.choices([1, 2, 3, 4], weights=[10, 20, 40, 30])[0]
                else:  # balanced
                    rating = random.choices([1, 2, 3, 4, 5], weights=[5, 10, 30, 40, 15])[0]

                participation_records.append({
                    'participation_id': f"PART{len(participation_records)+1:07d}",
                    'activity_id': activity_id,
                    'student_id': student['student_id'],
                    'registration_time': activity['start_time'] - pd.Timedelta(days=random.randint(1, 7)),
                    'check_in_time': activity['start_time'] + pd.Timedelta(minutes=random.randint(-10, 10)),
                    'check_out_time': activity['end_time'] + pd.Timedelta(minutes=random.randint(0, 20)),
                    'rating': rating,
                    'feedback': self._generate_feedback(rating),
                    'status': 'attended',
                })

        return pd.DataFrame(participation_records)

    def _clean_activities(self, df: pd.DataFrame) -> pd.DataFrame:
        """清洗活动数据"""
        # 定义清洗策略
        strategies = {
            'participant_count': {'missing': 'median', 'outlier': 'clip'},
            'budget_amount': {'missing': 'median', 'outlier': 'clip'},
            'start_time': {'missing': 'drop'},
            'end_time': {'missing': 'drop'},
        }

        # 清洗
        df_clean = self.cleaner.clean(df, column_strategies=strategies)

        # 修复时间逻辑（结束时间早于开始时间）
        mask = df_clean['end_time'] <= df_clean['start_time']
        df_clean.loc[mask, 'end_time'] = df_clean.loc[mask, 'start_time'] + pd.Timedelta(hours=2)

        return df_clean

    def _engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """特征工程"""
        # 时间特征已经在generate_activities中添加
        # 添加活动特征
        df = self.feature_engineer.generate_activity_features(df)

        return df

    def _get_activity_type_by_club(self, club_type: str) -> str:
        """根据社团类型获取活动类型"""
        type_mapping = {
            'tech': ['讲座', '培训', '比赛'],
            'arts': ['演出', '展览', '聚会'],
            'sports': ['比赛', '户外', '培训'],
            'academic': ['讲座', '比赛', '培训'],
            'public': ['志愿服务', '户外'],
        }
        return random.choice(type_mapping.get(club_type, ['聚会']))

    def _generate_phone(self) -> str:
        """生成手机号"""
        prefixes = ['138', '139', '150', '151', '152', '157', '158', '159', '182', '183']
        prefix = random.choice(prefixes)
        suffix = ''.join([str(random.randint(0, 9)) for _ in range(8)])
        return f"{prefix}{suffix}"

    def _generate_feedback(self, rating: int) -> str:
        """根据评分生成反馈文本"""
        feedbacks = {
            5: ["非常棒！", "很喜欢这次活动的组织！", "收获满满！"],
            4: ["活动还不错", "组织得挺好", "挺有意义的"],
            3: ["一般般吧", "还可以", "没有预期的好"],
            2: ["不太满意", "组织有些混乱", "内容不够丰富"],
            1: ["很失望", "浪费时间", "组织很差"],
        }
        return random.choice(feedbacks.get(rating, ["无评论"]))

    def _save_to_files(self, output_dir: str):
        """保存到文件"""
        import os
        os.makedirs(output_dir, exist_ok=True)

        self.students_df.to_csv(f"{output_dir}/students.csv", index=False, encoding='utf-8-sig')
        self.clubs_df.to_csv(f"{output_dir}/clubs.csv", index=False, encoding='utf-8-sig')
        self.activities_df.to_csv(f"{output_dir}/activities.csv", index=False, encoding='utf-8-sig')
        self.participation_df.to_csv(f"{output_dir}/participation.csv", index=False, encoding='utf-8-sig')

        print(f"\n[保存] 数据已保存到: {output_dir}/")

    def get_generation_report(self) -> str:
        """获取生成报告"""
        if not self.generation_stats:
            return "尚未生成数据"

        stats = self.generation_stats

        report = f"""
========================================
智能数据生成报告
========================================
生成时间: {stats['generation_time_seconds']:.1f}秒
随机种子: {self.seed}

数据规模:
  - 学生: {stats['student_count']} 人
  - 社团: {stats['club_count']} 个
  - 活动: {stats['activity_count']} 场
  - 参与记录: {stats['participation_count']} 条

质量报告:
  - 清洗前质量: {stats['quality_before']:.1f}/100
  - 清洗后质量: {stats['quality_after']:.1f}/100
  - 质量提升: {stats['quality_improvement']:+.1f}分

特殊处理:
  - 资源冲突注入: {'是' if stats['conflicts_injected'] else '否'}
  - 脏数据注入: {'是' if stats['dirty_data_injected'] else '否'}
  - 脏数据数量: {stats['dirty_data_count']} 条

角色分布:
{self._get_persona_distribution()}
========================================
"""
        return report

    def _get_persona_distribution(self) -> str:
        """获取角色分布字符串"""
        if self.students_df is None or 'persona' not in self.students_df.columns:
            return "  无数据"

        dist = self.students_df['persona'].value_counts()
        lines = []
        for persona, count in dist.items():
            pct = count / len(self.students_df) * 100
            lines.append(f"  - {persona}: {count}人 ({pct:.1f}%)")
        return "\n".join(lines)


# 便捷函数
def generate_smart_dataset(
    student_count: int = 1000,
    club_count: int = 20,
    activity_count: int = 200,
    seed: int = 42,
    output_dir: Optional[str] = None
) -> Dict[str, Any]:
    """
    快速生成智能数据集

    示例:
        >>> data = generate_smart_dataset(1000, 20, 200)
        >>> print(data['activities'].head())
        >>> print(data['generation_stats'])
    """
    generator = SmartDataGenerator(seed=seed)
    return generator.generate_full_dataset(
        student_count=student_count,
        club_count=club_count,
        activity_count=activity_count,
        inject_conflicts=True,
        inject_dirty_data=True,
        output_dir=output_dir
    )


if __name__ == '__main__':
    # 测试生成
    print("="*60)
    print("智能数据生成器测试")
    print("="*60)

    # 小规模测试
    result = generate_smart_dataset(
        student_count=100,
        club_count=5,
        activity_count=20,
        seed=42,
        output_dir="./test_data"
    )

    print("\n生成报告:")
    print(result['generation_stats'])

    print("\n学生角色分布:")
    print(result['students']['persona'].value_counts())

    print("\n活动时间分布:")
    print(result['activities']['is_weekend'].value_counts())

    print("\n活动冲突情况:")
    print(result['activities']['resource_conflict'].value_counts())
