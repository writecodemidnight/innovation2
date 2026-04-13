"""测试角色模板系统"""

import pytest
import pandas as pd
import numpy as np


class TestStudentPersona:
    """测试学生角色模板"""

    def test_persona_structure(self):
        """测试角色数据结构"""
        from data.mock.personas import StudentPersona, ClubPreference

        persona = StudentPersona(
            persona_id='test',
            name='测试角色',
            description='用于测试',
            gender_ratio=0.6,
            major_weights={'CS': 0.5, 'ART': 0.5},
            club_preferences=[
                ClubPreference('tech', 0.8, 'high', (1000, 5000))
            ]
        )

        assert persona.persona_id == 'test'
        assert persona.gender_ratio == 0.6
        assert len(persona.club_preferences) == 1

    def test_tech_geek_persona(self):
        """测试技术宅角色"""
        from data.mock.personas import PersonaGenerator

        gen = PersonaGenerator(seed=42)
        tech_geek = gen.personas['tech_geek']

        assert tech_geek.gender_ratio == 0.75
        assert 'CS' in tech_geek.major_weights
        assert any(p.club_type == 'tech' for p in tech_geek.club_preferences)


class TestPersonaGenerator:
    """测试角色生成器"""

    def test_generate_students_basic(self):
        """测试基本生成"""
        from data.mock.personas import PersonaGenerator

        gen = PersonaGenerator(seed=42)
        df = gen.generate_students(100)

        assert len(df) == 100
        assert 'student_id' in df.columns
        assert 'persona' in df.columns
        assert 'interest_tags' in df.columns

    def test_persona_distribution(self):
        """测试角色分布"""
        from data.mock.personas import PersonaGenerator

        gen = PersonaGenerator(seed=42)
        df = gen.generate_students(1000)

        # 检查每种角色都有
        assert len(df['persona'].unique()) >= 4

        # 检查角色比例大致符合预期
        persona_counts = df['persona'].value_counts()
        total = len(df)

        # tech_geek 应该约占15%
        tech_ratio = persona_counts.get('tech_geek', 0) / total
        assert 0.10 <= tech_ratio <= 0.20

    def test_gender_distribution_by_persona(self):
        """测试不同角色的性别分布"""
        from data.mock.personas import PersonaGenerator

        gen = PersonaGenerator(seed=42)
        df = gen.generate_students(1000)

        # 技术宅男性比例应该较高
        tech_males = df[df['persona'] == 'tech_geek']['gender'].value_counts().get('M', 0)
        tech_total = len(df[df['persona'] == 'tech_geek'])
        if tech_total > 0:
            male_ratio = tech_males / tech_total
            assert male_ratio >= 0.60  # 技术宅男性应占多数

    def test_student_id_format(self):
        """测试学号格式"""
        from data.mock.personas import PersonaGenerator

        gen = PersonaGenerator(seed=42)
        df = gen.generate_students(100)

        # 学号格式：年份(2位) + 专业代码(2位) + 序号(4位)
        for student_id in df['student_id']:
            assert len(student_id) == 8
            assert student_id[:2].isdigit()  # 年份
            assert student_id[2:4].isalpha()  # 专业代码
            assert student_id[4:].isdigit()  # 序号

    def test_interest_tags_correlation(self):
        """测试兴趣标签与角色相关"""
        from data.mock.personas import PersonaGenerator

        gen = PersonaGenerator(seed=42)
        df = gen.generate_students(500)

        # 技术宅应该有tech标签
        tech_students = df[df['persona'] == 'tech_geek']
        tech_with_tech_tag = tech_students['interest_tags'].str.contains('tech', na=False).sum()

        # 大部分技术宅应该有tech标签
        if len(tech_students) > 0:
            assert tech_with_tech_tag / len(tech_students) >= 0.6

    def test_get_persona_insights(self):
        """测试角色洞察"""
        from data.mock.personas import PersonaGenerator

        gen = PersonaGenerator(seed=42)
        insights = gen.get_persona_insights()

        assert len(insights) == len(gen.personas)
        assert 'persona_id' in insights.columns
        assert 'male_ratio' in insights.columns


class TestQuickGenerate:
    """测试便捷生成函数"""

    def test_generate_mock_students(self):
        """测试快速生成函数"""
        from data.mock.personas import generate_mock_students

        df = generate_mock_students(100, seed=42)

        assert len(df) == 100
        assert 'persona' in df.columns

    def test_seed_consistency(self):
        """测试种子一致性"""
        from data.mock.personas import generate_mock_students

        df1 = generate_mock_students(100, seed=42)
        df2 = generate_mock_students(100, seed=42)

        pd.testing.assert_frame_equal(df1, df2)
