"""
模糊综合评价法测试
"""

import pytest
import numpy as np
import os
import tempfile

from src.evaluation.fuzzy_evaluator import (
    FuzzyComprehensiveEvaluator,
    FuzzyMembershipFunction,
    RatingLevel
)


class TestFuzzyMembershipFunction:
    """测试模糊隶属度函数"""

    def test_init(self):
        """测试初始化"""
        fmf = FuzzyMembershipFunction()
        assert fmf.min_score == 0
        assert fmf.max_score == 100

    def test_calculate_membership(self):
        """测试隶属度计算"""
        fmf = FuzzyMembershipFunction()

        # 测试中心点（完全属于）
        assert fmf.calculate_membership(95, "优秀") == 1.0
        assert fmf.calculate_membership(85, "良好") == 1.0
        assert fmf.calculate_membership(72.5, "中等") == 1.0

        # 测试边界
        assert fmf.calculate_membership(85, "优秀") == 0.0
        assert fmf.calculate_membership(60, "及格") == 1.0

        # 测试中间值
        membership = fmf.calculate_membership(88, "优秀")
        assert 0 < membership < 1

    def test_get_membership_vector(self):
        """测试获取隶属度向量"""
        fmf = FuzzyMembershipFunction()

        vector = fmf.get_membership_vector(85)

        assert len(vector) == 5
        assert abs(np.sum(vector) - 1.0) < 0.1  # 近似归一化


class TestFuzzyComprehensiveEvaluator:
    """测试模糊综合评价器"""

    def test_init(self):
        """测试初始化"""
        evaluator = FuzzyComprehensiveEvaluator()

        assert evaluator.factors == ["参与度", "教育性", "创新性", "影响力", "可持续性"]
        assert len(evaluator.weights) == 5
        assert abs(np.sum(evaluator.weights) - 1.0) < 1e-6

    def test_custom_weights(self):
        """测试自定义权重"""
        weights = {
            "参与度": 0.3,
            "教育性": 0.3,
            "创新性": 0.2,
            "影响力": 0.1,
            "可持续性": 0.1
        }

        evaluator = FuzzyComprehensiveEvaluator(weights=weights)

        assert evaluator.weights[0] == 0.3  # 参与度
        assert evaluator.weights[1] == 0.3  # 教育性

    def test_evaluate(self):
        """测试评价"""
        evaluator = FuzzyComprehensiveEvaluator()

        scores = {
            "参与度": 85,
            "教育性": 90,
            "创新性": 75,
            "影响力": 80,
            "可持续性": 88
        }

        result = evaluator.evaluate(scores)

        assert isinstance(result.final_score, float)
        assert isinstance(result.grade, str)
        assert len(result.membership_vector) == 5
        assert result.evaluation_matrix.shape == (5, 5)
        assert result.confidence > 0

        # 检查分数范围
        assert 0 <= result.final_score <= 100

    def test_evaluate_detailed(self):
        """测试详细分析版评价"""
        evaluator = FuzzyComprehensiveEvaluator()

        scores = {
            "参与度": 85,
            "教育性": 90,
            "创新性": 75,
            "影响力": 80,
            "可持续性": 88
        }

        result = evaluator.evaluate_with_detailed_analysis(scores)

        assert "final_score" in result
        assert "grade" in result
        assert "dimension_analysis" in result
        assert "grade_distribution" in result
        assert "improvement_suggestions" in result

        assert len(result["dimension_analysis"]) == 5

    def test_fuzzy_composition_methods(self):
        """测试不同合成方法"""
        evaluator = FuzzyComprehensiveEvaluator()

        scores = {
            "参与度": 85,
            "教育性": 90,
            "创新性": 75,
            "影响力": 80,
            "可持续性": 88
        }

        methods = ["weighted_average", "max_min", "max_product"]

        for method in methods:
            result = evaluator.evaluate(scores, method)
            assert isinstance(result.final_score, float)

    def test_compare_activities(self):
        """测试活动对比"""
        evaluator = FuzzyComprehensiveEvaluator()

        activities = [
            {
                "id": "A1",
                "name": "活动1",
                "scores": {"参与度": 85, "教育性": 90, "创新性": 75,
                          "影响力": 80, "可持续性": 88}
            },
            {
                "id": "A2",
                "name": "活动2",
                "scores": {"参与度": 70, "教育性": 85, "创新性": 90,
                          "影响力": 75, "可持续性": 80}
            }
        ]

        result = evaluator.compare_activities(activities)

        assert "ranking" in result
        assert "statistics" in result
        assert "best_activity" in result
        assert len(result["ranking"]) == 2

    def test_suggestions_generation(self):
        """测试建议生成"""
        evaluator = FuzzyComprehensiveEvaluator()

        # 低分活动
        low_scores = {
            "参与度": 50,
            "教育性": 55,
            "创新性": 45,
            "影响力": 40,
            "可持续性": 50
        }

        result = evaluator.evaluate_with_detailed_analysis(low_scores)

        assert len(result["improvement_suggestions"]) > 0

    def test_sensitivity_analysis(self):
        """测试敏感性分析"""
        evaluator = FuzzyComprehensiveEvaluator()

        scores = {
            "参与度": 85,
            "教育性": 90,
            "创新性": 75,
            "影响力": 80,
            "可持续性": 88
        }

        result = evaluator.sensitivity_analysis(scores, n_simulations=50)

        assert "mean_score" in result
        assert "std_score" in result
        assert "stability" in result

    def test_export_import(self):
        """测试导出导入"""
        evaluator = FuzzyComprehensiveEvaluator()

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            filepath = f.name

        try:
            evaluator.export_model(filepath)
            assert os.path.exists(filepath)

            loaded = FuzzyComprehensiveEvaluator.load_model(filepath)
            assert loaded.factors == evaluator.factors
            assert np.allclose(loaded.weights, evaluator.weights)
        finally:
            os.unlink(filepath)


class TestRatingLevel:
    """测试评价等级枚举"""

    def test_levels(self):
        """测试等级定义"""
        assert RatingLevel.EXCELLENT.value == "优秀"
        assert RatingLevel.GOOD.value == "良好"
        assert RatingLevel.MEDIUM.value == "中等"
        assert RatingLevel.PASS.value == "及格"
        assert RatingLevel.FAIL.value == "不及格"
