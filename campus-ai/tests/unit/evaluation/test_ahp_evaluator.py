"""
AHP层次分析法测试
"""

import pytest
import numpy as np
import os
import tempfile

from src.evaluation.ahp_evaluator import (
    AHPEvaluator,
    FiveDimensionEvaluator,
    EvaluationDimension
)


class TestAHPEvaluator:
    """测试AHP评估器"""

    def test_init(self):
        """测试初始化"""
        evaluator = AHPEvaluator()
        assert evaluator.n == 5  # 默认五维
        assert evaluator.consistency_threshold == 0.1

        custom_criteria = ["A", "B", "C"]
        evaluator2 = AHPEvaluator(criteria=custom_criteria)
        assert evaluator2.n == 3
        assert evaluator2.criteria == custom_criteria

    def test_build_comparison_matrix(self):
        """测试判断矩阵构建"""
        evaluator = AHPEvaluator()
        matrix = evaluator.build_comparison_matrix()

        assert matrix.shape == (5, 5)
        assert np.allclose(np.diag(matrix), 1.0)  # 对角线为1

        # 检查互反性
        for i in range(5):
            for j in range(5):
                if i != j:
                    assert abs(matrix[i, j] * matrix[j, i] - 1.0) < 1e-10

    def test_calculate_weights(self):
        """测试权重计算"""
        evaluator = AHPEvaluator()
        evaluator.build_comparison_matrix()

        result = evaluator.calculate_weights(method="eigenvalue")

        assert len(result.weights) == 5
        assert abs(sum(result.weights.values()) - 1.0) < 1e-6  # 权重和为1
        assert all(w >= 0 for w in result.weights.values())  # 非负
        assert result.consistency_ratio >= 0
        assert isinstance(result.consistency_check_passed, bool)

    def test_consistency_check(self):
        """测试一致性检验"""
        evaluator = AHPEvaluator()

        # 构建一致性矩阵
        consistent_judgments = {
            (0, 1): 2.0,
            (0, 2): 3.0,
            (1, 2): 1.5
        }

        evaluator.build_comparison_matrix(consistent_judgments)
        result = evaluator.calculate_weights()

        # 一致性比率应该小于阈值
        assert result.consistency_ratio < 0.1
        assert result.consistency_check_passed

    def test_geometric_method(self):
        """测试几何平均法"""
        evaluator = AHPEvaluator()
        evaluator.build_comparison_matrix()

        result = evaluator.calculate_weights(method="geometric")

        assert len(result.weights) == 5
        assert abs(sum(result.weights.values()) - 1.0) < 1e-6

    def test_calculate_sub_criteria_weights(self):
        """测试子准则权重计算"""
        evaluator = AHPEvaluator()
        evaluator.build_comparison_matrix()

        sub_criteria = ["子准则1", "子准则2", "子准则3"]
        sub_weights = evaluator.calculate_sub_criteria_weights(
            "参与度",
            sub_criteria
        )

        assert len(sub_weights.weights) == 3
        assert abs(sum(sub_weights.weights.values()) - 1.0) < 1e-6


class TestFiveDimensionEvaluator:
    """测试五维评估器"""

    def test_init(self):
        """测试初始化"""
        evaluator = FiveDimensionEvaluator()
        assert evaluator.DIMENSIONS == [
            "参与度", "教育性", "创新性", "影响力", "可持续性"
        ]
        assert evaluator.weights is None

    def test_fit(self):
        """测试训练"""
        evaluator = FiveDimensionEvaluator()
        evaluator.fit()

        assert evaluator.weights is not None
        assert evaluator.weights.consistency_check_passed

    def test_evaluate_activity(self):
        """测试单个活动评估"""
        evaluator = FiveDimensionEvaluator()
        evaluator.fit()

        scores = {
            "参与度": 85,
            "教育性": 90,
            "创新性": 75,
            "影响力": 80,
            "可持续性": 88
        }

        result = evaluator.evaluate_activity(scores)

        assert "total_score" in result
        assert "dimension_scores" in result
        assert "weights" in result
        assert "contributions" in result
        assert 0 <= result["total_score"] <= 100

    def test_evaluate_batch(self):
        """测试批量评估"""
        evaluator = FiveDimensionEvaluator()
        evaluator.fit()

        activities = [
            {
                "id": "A1",
                "scores": {
                    "参与度": 85, "教育性": 90, "创新性": 75,
                    "影响力": 80, "可持续性": 88
                }
            },
            {
                "id": "A2",
                "scores": {
                    "参与度": 70, "教育性": 85, "创新性": 90,
                    "影响力": 75, "可持续性": 80
                }
            }
        ]

        results = evaluator.evaluate_batch(activities)

        assert len(results) == 2
        assert results[0]["activity_id"] == "A1"
        assert results[1]["activity_id"] == "A2"

    def test_invalid_scores(self):
        """测试无效输入"""
        evaluator = FiveDimensionEvaluator()

        with pytest.raises(RuntimeError):
            evaluator.evaluate_activity({"参与度": 80})  # 未fit

        evaluator.fit()

        with pytest.raises(ValueError):
            evaluator.evaluate_activity({"参与度": 80})  # 缺少维度

    def test_export_import(self):
        """测试导出导入"""
        evaluator = FiveDimensionEvaluator()
        evaluator.fit()

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            filepath = f.name

        try:
            evaluator.export_weights(filepath)
            assert os.path.exists(filepath)

            loaded = FiveDimensionEvaluator.load_weights(filepath)
            assert loaded.weights is not None
        finally:
            os.unlink(filepath)

    def test_sensitivity_analysis(self):
        """测试敏感性分析"""
        evaluator = AHPEvaluator()
        evaluator.build_comparison_matrix()

        results = evaluator.sensitivity_analysis(
            n_simulations=50
        )

        assert len(results) == 5
        for criterion, stats in results.items():
            assert "mean" in stats
            assert "std" in stats
            assert "cv" in stats


class TestEvaluationDimension:
    """测试评估维度枚举"""

    def test_dimensions(self):
        """测试维度定义"""
        assert EvaluationDimension.ENGAGEMENT.value == "参与度"
        assert EvaluationDimension.EDUCATIONAL.value == "教育性"
        assert EvaluationDimension.INNOVATION.value == "创新性"
        assert EvaluationDimension.IMPACT.value == "影响力"
        assert EvaluationDimension.SUSTAINABILITY.value == "可持续性"
