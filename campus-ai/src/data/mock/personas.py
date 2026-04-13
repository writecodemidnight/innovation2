"""
角色模板系统 (Persona-Based Data Generation)

核心概念：
- 不是随机给学生分配标签，而是基于"角色模板"生成
- 每个角色有特定的兴趣分布、行为模式
- 这样K-Means聚类才能找到真实的群体
"""

import random
import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional
from faker import Faker
import pandas as pd
from datetime import datetime

fake = Faker('zh_CN')


@dataclass
class ClubPreference:
    """社团偏好配置"""
    club_type: str
    probability: float  # 0-1
    engagement_level: str  # 'high', 'medium', 'low'
    typical_budget_range: Tuple[int, int]  # (min, max)


@dataclass
class StudentPersona:
    """
    学生角色模板

    示例角色：
    - 技术宅 (TechGeek): 高概率参加科技类社团
    - 文艺青年 (Artist): 高概率参加文艺类社团
    - 体育达人 (Athlete): 高概率参加体育类社团
    - 社交达人 (Socializer): 参加各类社团，活动频繁
    - 学霸 (Scholar): 高概率参加学术类社团
    """
    persona_id: str
    name: str
    description: str

    # 人口统计分布
    gender_ratio: float = 0.5  # 男性比例
    grade_distribution: Dict[int, float] = field(default_factory=dict)  # 年级分布

    # 专业偏好 (专业代码 -> 权重)
    major_weights: Dict[str, float] = field(default_factory=dict)

    # 社团偏好列表
    club_preferences: List[ClubPreference] = field(default_factory=list)

    # 行为特征
    activity_frequency: str = 'medium'  # 'high', 'medium', 'low'
    feedback_style: str = 'balanced'  # 'critical', 'balanced', 'positive'

    # 时间偏好 (小时 -> 权重)
    preferred_hours: Dict[int, float] = field(default_factory=dict)


class PersonaGenerator:
    """
    基于角色的数据生成器

    预定义角色：
    1. TechGeek - 技术宅
    2. Artist - 文艺青年
    3. Athlete - 体育达人
    4. Socializer - 社交达人
    5. Scholar - 学霸
    6. Casual - 随缘型
    """

    def __init__(self, seed: Optional[int] = None):
        if seed:
            random.seed(seed)
            np.random.seed(seed)
            Faker.seed(seed)

        self.personas = self._define_personas()
        self.current_year = datetime.now().year

    def _define_personas(self) -> Dict[str, StudentPersona]:
        """定义所有角色模板"""

        personas = {}

        # 1. 技术宅 (TechGeek)
        personas['tech_geek'] = StudentPersona(
            persona_id='tech_geek',
            name='技术宅',
            description='热爱编程、机器人、黑客技术',
            gender_ratio=0.75,  # 男性居多
            grade_distribution={1: 0.3, 2: 0.3, 3: 0.25, 4: 0.15},
            major_weights={
                'CS': 0.4, 'EE': 0.25, 'AUTO': 0.15,
                'MATH': 0.1, 'PHY': 0.1
            },
            club_preferences=[
                ClubPreference('tech', 0.80, 'high', (2000, 8000)),
                ClubPreference('academic', 0.40, 'medium', (500, 2000)),
                ClubPreference('arts', 0.10, 'low', (100, 500)),
                ClubPreference('sports', 0.20, 'low', (100, 1000)),
            ],
            activity_frequency='high',
            feedback_style='critical',
            preferred_hours={
                14: 0.15, 15: 0.15, 16: 0.20,  # 下午
                19: 0.20, 20: 0.20, 21: 0.10   # 晚上
            }
        )

        # 2. 文艺青年 (Artist)
        personas['artist'] = StudentPersona(
            persona_id='artist',
            name='文艺青年',
            description='热爱音乐、绘画、摄影、文学',
            gender_ratio=0.45,
            grade_distribution={1: 0.35, 2: 0.30, 3: 0.20, 4: 0.15},
            major_weights={
                'CHN': 0.25, 'HIS': 0.15, 'PHI': 0.15,
                'MKT': 0.15, 'ART': 0.20, 'DES': 0.10
            },
            club_preferences=[
                ClubPreference('arts', 0.85, 'high', (1000, 5000)),
                ClubPreference('public', 0.30, 'medium', (200, 1000)),
                ClubPreference('academic', 0.20, 'low', (300, 1500)),
                ClubPreference('tech', 0.10, 'low', (500, 2000)),
            ],
            activity_frequency='medium',
            feedback_style='positive',
            preferred_hours={
                16: 0.20, 17: 0.20,  # 傍晚
                19: 0.25, 20: 0.25   # 晚上
            }
        )

        # 3. 体育达人 (Athlete)
        personas['athlete'] = StudentPersona(
            persona_id='athlete',
            name='体育达人',
            description='热爱运动、健身、户外',
            gender_ratio=0.60,
            grade_distribution={1: 0.30, 2: 0.35, 3: 0.25, 4: 0.10},
            major_weights={
                'PE': 0.30, 'AUTO': 0.20, 'EE': 0.15,
                'BA': 0.20, 'CS': 0.15
            },
            club_preferences=[
                ClubPreference('sports', 0.90, 'high', (500, 3000)),
                ClubPreference('public', 0.25, 'medium', (100, 800)),
                ClubPreference('arts', 0.15, 'low', (200, 1000)),
            ],
            activity_frequency='high',
            feedback_style='balanced',
            preferred_hours={
                8: 0.20, 9: 0.20,      # 早晨
                16: 0.25, 17: 0.25,    # 傍晚
                20: 0.10               # 晚上
            }
        )

        # 4. 社交达人 (Socializer)
        personas['socializer'] = StudentPersona(
            persona_id='socializer',
            name='社交达人',
            description='活跃于各类社团，喜欢组织活动',
            gender_ratio=0.50,
            grade_distribution={1: 0.40, 2: 0.35, 3: 0.15, 4: 0.10},
            major_weights={
                'MKT': 0.25, 'BA': 0.25, 'CHN': 0.20,
                'CS': 0.15, 'EE': 0.10, 'ART': 0.05
            },
            club_preferences=[
                ClubPreference('public', 0.60, 'high', (500, 3000)),
                ClubPreference('social', 0.70, 'high', (1000, 5000)),
                ClubPreference('arts', 0.40, 'medium', (500, 2000)),
                ClubPreference('tech', 0.30, 'medium', (1000, 4000)),
                ClubPreference('sports', 0.35, 'medium', (300, 2000)),
            ],
            activity_frequency='high',
            feedback_style='positive',
            preferred_hours={
                14: 0.15, 15: 0.15, 16: 0.15, 17: 0.15,
                19: 0.20, 20: 0.20
            }
        )

        # 5. 学霸 (Scholar)
        personas['scholar'] = StudentPersona(
            persona_id='scholar',
            name='学霸',
            description='专注学业，参加学术竞赛',
            gender_ratio=0.50,
            grade_distribution={1: 0.25, 2: 0.30, 3: 0.30, 4: 0.15},
            major_weights={
                'MATH': 0.25, 'PHY': 0.20, 'CHEM': 0.20,
                'CS': 0.20, 'EE': 0.10, 'BIO': 0.05
            },
            club_preferences=[
                ClubPreference('academic', 0.80, 'high', (1000, 5000)),
                ClubPreference('tech', 0.40, 'medium', (2000, 6000)),
                ClubPreference('public', 0.20, 'low', (200, 1000)),
            ],
            activity_frequency='medium',
            feedback_style='critical',
            preferred_hours={
                14: 0.30, 15: 0.30, 16: 0.20,  # 下午
                19: 0.15, 20: 0.05              # 晚上较少
            }
        )

        # 6. 随缘型 (Casual)
        personas['casual'] = StudentPersona(
            persona_id='casual',
            name='随缘型',
            description='偶尔参加，看心情',
            gender_ratio=0.50,
            grade_distribution={1: 0.30, 2: 0.25, 3: 0.25, 4: 0.20},
            major_weights={
                'CS': 0.20, 'BA': 0.20, 'CHN': 0.15,
                'ART': 0.15, 'PE': 0.15, 'OTH': 0.15
            },
            club_preferences=[
                ClubPreference('arts', 0.25, 'low', (100, 800)),
                ClubPreference('sports', 0.25, 'low', (100, 800)),
                ClubPreference('public', 0.20, 'low', (50, 500)),
            ],
            activity_frequency='low',
            feedback_style='balanced',
            preferred_hours={
                15: 0.20, 16: 0.20, 19: 0.30, 20: 0.30
            }
        )

        return personas

    def generate_students(self, count: int, persona_distribution: Optional[Dict[str, float]] = None) -> pd.DataFrame:
        """
        生成学生数据

        Args:
            count: 学生数量
            persona_distribution: 角色分布比例，默认均匀分布
        """
        if persona_distribution is None:
            # 默认分布
            persona_distribution = {
                'tech_geek': 0.15,
                'artist': 0.15,
                'athlete': 0.15,
                'socializer': 0.15,
                'scholar': 0.15,
                'casual': 0.25
            }

        students = []

        for i in range(count):
            # 随机选择角色
            persona_id = np.random.choice(
                list(persona_distribution.keys()),
                p=list(persona_distribution.values())
            )
            persona = self.personas[persona_id]

            # 生成学生
            student = self._generate_single_student(i, persona)
            students.append(student)

        return pd.DataFrame(students)

    def _generate_single_student(self, index: int, persona: StudentPersona) -> Dict:
        """生成单个学生"""

        # 性别
        gender = 'M' if random.random() < persona.gender_ratio else 'F'

        # 姓名
        name = fake.name_male() if gender == 'M' else fake.name_female()

        # 年级（根据角色分布）
        grades = list(persona.grade_distribution.keys())
        weights = list(persona.grade_distribution.values())
        grade_level = np.random.choice(grades, p=weights)
        enrollment_year = self.current_year - grade_level + 1

        # 专业
        majors = list(persona.major_weights.keys())
        major_weights = list(persona.major_weights.values())
        major = np.random.choice(majors, p=major_weights)

        # 生成学号：年份(2位) + 专业代码(2位) + 序号(4位)
        year_short = str(enrollment_year)[-2:]
        major_code = major[:2].upper()
        seq = index % 9999 + 1
        student_id = f"{year_short}{major_code}{seq:04d}"

        # 根据角色确定兴趣标签
        interest_tags = self._generate_interest_tags(persona)

        return {
            'student_id': student_id,
            'name': name,
            'gender': gender,
            'enrollment_year': enrollment_year,
            'grade_level': grade_level,
            'major': major,
            'persona': persona.persona_id,
            'interest_tags': ','.join(interest_tags),
            'activity_frequency': persona.activity_frequency,
            'feedback_style': persona.feedback_style,
            'created_at': datetime.now()
        }

    def _generate_interest_tags(self, persona: StudentPersona) -> List[str]:
        """根据角色生成兴趣标签"""
        tags = []

        for pref in persona.club_preferences:
            if random.random() < pref.probability:
                tags.append(pref.club_type)

        # 确保至少有1个标签
        if not tags and persona.club_preferences:
            tags.append(persona.club_preferences[0].club_type)

        return tags[:3]  # 最多3个标签

    def get_persona_insights(self) -> pd.DataFrame:
        """获取角色统计洞察（用于验证分布）"""
        data = []
        for persona_id, persona in self.personas.items():
            data.append({
                'persona_id': persona_id,
                'name': persona.name,
                'male_ratio': persona.gender_ratio,
                'avg_grade': sum(k*v for k,v in persona.grade_distribution.items()),
                'top_major': max(persona.major_weights.items(), key=lambda x: x[1])[0],
                'activity_freq': persona.activity_frequency
            })
        return pd.DataFrame(data)


# 便捷的生成函数
def generate_mock_students(
    count: int = 1000,
    seed: int = 42,
    persona_distribution: Optional[Dict[str, float]] = None
) -> pd.DataFrame:
    """
    快速生成学生模拟数据

    示例：
        >>> df = generate_mock_students(1000, seed=42)
        >>> print(df[['student_id', 'name', 'persona', 'interest_tags']].head())
    """
    generator = PersonaGenerator(seed=seed)
    return generator.generate_students(count, persona_distribution)


if __name__ == '__main__':
    # 测试生成
    print("生成1000个学生数据...")
    df = generate_mock_students(1000, seed=42)

    print(f"\n总计生成: {len(df)} 条记录")
    print("\n角色分布:")
    print(df['persona'].value_counts())

    print("\n性别分布:")
    print(df['gender'].value_counts(normalize=True))

    print("\n年级分布:")
    print(df['grade_level'].value_counts().sort_index())

    print("\n兴趣标签示例:")
    print(df['interest_tags'].value_counts().head(10))
