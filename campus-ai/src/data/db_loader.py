"""
数据库加载器 (Database Loader)
===============================
将模拟数据快速导入PostgreSQL的微型桥梁

用法:
    from data.db_loader import load_mock_data_to_db

    # 一键加载
    load_mock_data_to_db(
        student_count=1000,
        club_count=20,
        activity_count=200,
        db_url="postgresql://user:pass@localhost/campus_club"
    )
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Optional, Dict, Any
import logging

try:
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import sessionmaker
    HAS_SQLALCHEMY = True
except ImportError:
    HAS_SQLALCHEMY = False
    print("[警告] SQLAlchemy 未安装，数据库加载功能不可用")
    print("       运行: pip install sqlalchemy psycopg2-binary")

# 导入mock数据生成器
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from data.mock.smart_data_generator import generate_smart_dataset

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MockDataLoader:
    """模拟数据加载器"""

    def __init__(self, db_url: str):
        """
        初始化加载器

        Args:
            db_url: PostgreSQL连接URL
                   格式: postgresql://user:password@host:port/database
        """
        if not HAS_SQLALCHEMY:
            raise ImportError("需要安装 sqlalchemy: pip install sqlalchemy psycopg2-binary")

        self.db_url = db_url
        self.engine = create_engine(db_url)
        self.Session = sessionmaker(bind=self.engine)

    def load_data(self,
                  student_count: int = 1000,
                  club_count: int = 20,
                  activity_count: int = 200,
                  seed: int = 42) -> Dict[str, Any]:
        """
        生成并加载数据到数据库

        Returns:
            加载统计信息
        """
        logger.info(f"[开始] 生成模拟数据: {student_count}学生, {club_count}社团, {activity_count}活动")

        # 生成数据
        data = generate_smart_dataset(
            student_count=student_count,
            club_count=club_count,
            activity_count=activity_count,
            seed=seed
        )

        stats = {
            'generated': {},
            'loaded': {},
            'errors': []
        }

        with self.Session() as session:
            try:
                # 1. 加载学生数据
                logger.info("[加载] 学生数据...")
                students_df = self._prepare_students(data['students'])
                students_df.to_sql('students', self.engine, if_exists='append', index=False)
                stats['loaded']['students'] = len(students_df)
                logger.info(f"       已加载 {len(students_df)} 条学生记录")

                # 2. 加载社团数据
                logger.info("[加载] 社团数据...")
                clubs_df = self._prepare_clubs(data['clubs'])
                clubs_df.to_sql('clubs', self.engine, if_exists='append', index=False)
                stats['loaded']['clubs'] = len(clubs_df)
                logger.info(f"       已加载 {len(clubs_df)} 条社团记录")

                # 3. 加载活动数据
                logger.info("[加载] 活动数据...")
                activities_df = self._prepare_activities(data['activities'])
                activities_df.to_sql('activities', self.engine, if_exists='append', index=False)
                stats['loaded']['activities'] = len(activities_df)
                logger.info(f"       已加载 {len(activities_df)} 条活动记录")

                # 4. 加载参与记录
                logger.info("[加载] 参与记录...")
                participation_df = self._prepare_participation(data['participation'])
                # 分批加载避免内存问题
                batch_size = 5000
                for i in range(0, len(participation_df), batch_size):
                    batch = participation_df.iloc[i:i+batch_size]
                    batch.to_sql('participation_records', self.engine, if_exists='append', index=False)
                    logger.info(f"       批次 {i//batch_size + 1}: {len(batch)} 条")
                stats['loaded']['participation'] = len(participation_df)

                session.commit()
                logger.info("[完成] 所有数据已加载到数据库")

            except Exception as e:
                session.rollback()
                stats['errors'].append(str(e))
                logger.error(f"[错误] 数据加载失败: {e}")
                raise

        return stats

    def _prepare_students(self, df: pd.DataFrame) -> pd.DataFrame:
        """准备学生数据（匹配数据库表结构）"""
        df = df.copy()

        # 确保列名匹配
        column_mapping = {
            'student_id': 'student_id',
            'name': 'name',
            'gender': 'gender',
            'enrollment_year': 'enrollment_year',
            'major': 'major',
            'email': 'email',
            'phone': 'phone',
            'created_at': 'created_at'
        }

        # 只保留存在的列
        available_cols = {k: v for k, v in column_mapping.items() if k in df.columns}
        df = df[list(available_cols.keys())]
        df.columns = list(available_cols.values())

        # 添加时间戳
        if 'created_at' not in df.columns:
            df['created_at'] = datetime.now()

        return df

    def _prepare_clubs(self, df: pd.DataFrame) -> pd.DataFrame:
        """准备社团数据"""
        df = df.copy()

        # 重命名列以匹配数据库
        column_mapping = {
            'club_id': 'club_id',
            'club_name': 'name',
            'club_type': 'category',
            'description': 'description',
            'founding_year': 'founding_date',  # 需要转换
            'member_count': 'member_count',
            'rating': 'star_rating',
            'advisor_name': 'advisor_name',
            'contact_email': 'contact_email',
            'status': 'status',
            'created_at': 'created_at'
        }

        available_cols = {k: v for k, v in column_mapping.items() if k in df.columns}
        df = df[list(available_cols.keys())]
        df.columns = list(available_cols.values())

        # 转换founding_year为日期
        if 'founding_date' in df.columns:
            df['founding_date'] = pd.to_datetime(df['founding_date'].astype(str) + '-01-01')

        if 'created_at' not in df.columns:
            df['created_at'] = datetime.now()

        return df

    def _prepare_activities(self, df: pd.DataFrame) -> pd.DataFrame:
        """准备活动数据"""
        df = df.copy()

        column_mapping = {
            'activity_id': 'activity_id',
            'club_id': 'club_id',
            'activity_name': 'name',
            'activity_type': 'type',
            'description': 'description',
            'start_time': 'start_time',
            'end_time': 'end_time',
            'location': 'location',
            'participant_count': 'max_participants',
            'budget_amount': 'budget',
            'status': 'status',
            'created_at': 'created_at'
        }

        available_cols = {k: v for k, v in column_mapping.items() if k in df.columns}
        df = df[list(available_cols.keys())]
        df.columns = list(available_cols.values())

        # 确保时间格式正确
        for col in ['start_time', 'end_time']:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col])

        if 'created_at' not in df.columns:
            df['created_at'] = datetime.now()

        return df

    def _prepare_participation(self, df: pd.DataFrame) -> pd.DataFrame:
        """准备参与记录"""
        df = df.copy()

        column_mapping = {
            'participation_id': 'id',
            'activity_id': 'activity_id',
            'student_id': 'student_id',
            'registration_time': 'registration_time',
            'check_in_time': 'check_in_time',
            'check_out_time': 'check_out_time',
            'rating': 'rating',
            'feedback': 'feedback',
            'status': 'status'
        }

        available_cols = {k: v for k, v in column_mapping.items() if k in df.columns}
        df = df[list(available_cols.keys())]
        df.columns = list(available_cols.values())

        # 确保时间格式正确
        for col in ['registration_time', 'check_in_time', 'check_out_time']:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col])

        return df

    def verify_load(self) -> Dict[str, int]:
        """验证数据库中的数据量"""
        tables = ['students', 'clubs', 'activities', 'participation_records']
        counts = {}

        with self.engine.connect() as conn:
            for table in tables:
                try:
                    result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    counts[table] = result.scalar()
                except Exception as e:
                    counts[table] = f"错误: {e}"

        return counts


# 便捷函数
def load_mock_data_to_db(
    db_url: str,
    student_count: int = 1000,
    club_count: int = 20,
    activity_count: int = 200,
    seed: int = 42
) -> Dict[str, Any]:
    """
    一键加载模拟数据到数据库

    示例:
        >>> result = load_mock_data_to_db(
        ...     db_url="postgresql://campus_user:password@localhost:5432/campus_club",
        ...     student_count=500,
        ...     club_count=10,
        ...     activity_count=50
        ... )
        >>> print(result['loaded'])
    """
    loader = MockDataLoader(db_url)
    return loader.load_data(
        student_count=student_count,
        club_count=club_count,
        activity_count=activity_count,
        seed=seed
    )


def quick_load_for_testing(db_url: str, seed: int = 42) -> Dict[str, Any]:
    """
    快速加载小规模数据（用于测试）

    生成: 100学生, 5社团, 20活动
    """
    return load_mock_data_to_db(
        db_url=db_url,
        student_count=100,
        club_count=5,
        activity_count=20,
        seed=seed
    )


if __name__ == '__main__':
    # 测试加载器
    import os

    # 从环境变量或默认值获取数据库URL
    db_url = os.getenv(
        'DATABASE_URL',
        'postgresql://campus_user:campus_pass@localhost:5432/campus_club'
    )

    print("=" * 60)
    print("模拟数据加载器测试")
    print("=" * 60)
    print(f"目标数据库: {db_url}")

    try:
        # 快速加载小规模数据
        result = quick_load_for_testing(db_url, seed=42)

        print("\n加载完成!")
        print(f"学生: {result['loaded'].get('students', 0)} 条")
        print(f"社团: {result['loaded'].get('clubs', 0)} 条")
        print(f"活动: {result['loaded'].get('activities', 0)} 条")
        print(f"参与记录: {result['loaded'].get('participation', 0)} 条")

        # 验证
        loader = MockDataLoader(db_url)
        counts = loader.verify_load()
        print("\n数据库验证:")
        for table, count in counts.items():
            print(f"  {table}: {count} 条")

    except Exception as e:
        print(f"\n错误: {e}")
        print("\n请确保:")
        print("1. PostgreSQL 已启动")
        print("2. 数据库 'campus_club' 已创建")
        print("3. 用户 'campus_user' 有写入权限")
        print("4. 已安装依赖: pip install sqlalchemy psycopg2-binary")
