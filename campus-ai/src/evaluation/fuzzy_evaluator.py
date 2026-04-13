"""
模糊综合评价法 (Fuzzy Comprehensive Evaluation)

用于处理评价指标具有模糊性的活动效果评估。

评价等级：优秀、良好、中等、及格、不及格
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import json


class RatingLevel(Enum):
    """评价等级"""
    EXCELLENT = "优秀"
    GOOD = "良好"
    MEDIUM = "中等"
    PASS = "及格"
    FAIL = "不及格"


@dataclass
class FuzzyEvaluationResult:
    """模糊评价结果"""
    final_score: float
    grade: str
    membership_vector: np.ndarray
    evaluation_matrix: np.ndarray
    confidence: float


class FuzzyMembershipFunction:
    """
    模糊隶属度函数

    定义各评价等级的隶属度函数（使用梯形或三角形隶属函数）
    """

    def __init__(self, score_range: Tuple[float, float] = (0, 100)):
        self.min_score, self.max_score = score_range
        self.levels = ["优秀", "良好", "中等", "及格", "不及格"]

    def calculate_membership(
        self,
        score: float,
        level: str
    ) -> float:
        """
        计算某得分对某等级的隶属度

        使用梯形隶属函数:
        - 优秀: [85, 90, 100, 100]
        - 良好: [75, 80, 90, 95]
        - 中等: [65, 70, 80, 85]
        - 及格: [60, 60, 70, 75]
        - 不及格: [0, 0, 60, 65]
        """
        ranges = {
            "优秀": (85, 90, 100, 100),
            "良好": (75, 80, 90, 95),
            "中等": (65, 70, 80, 85),
            "及格": (60, 60, 70, 75),
            "不及格": (0, 0, 60, 65)
        }

        a, b, c, d = ranges[level]

        if score < a or score > d:
            return 0.0
        elif b <= score <= c:
            return 1.0
        elif a <= score < b:
            return (score - a) / (b - a) if b != a else 1.0
        elif c < score <= d:
            return (d - score) / (d - c) if d != c else 1.0
        else:
            return 0.0

    def get_membership_vector(self, score: float) -> np.ndarray:
        """
        获取某得分对所有等级的隶属度向量

        Returns:
            隶属度向量 [μ_优秀, μ_良好, μ_中等, μ_及格, μ_不及格]
        """
        return np.array([
            self.calculate_membership(score, level)
            for level in self.levels
        ])


class FuzzyComprehensiveEvaluator:
    """
    模糊综合评价器

    适用于评价因素具有模糊性的活动效果评估

    使用步骤:
    1. 确定因素集和评语集
    2. 确定权重向量
    3. 构建模糊评价矩阵
    4. 进行模糊合成运算
    5. 计算综合评价值
    """

    # 等级分值（用于计算最终得分）
    LEVEL_SCORES = {
        "优秀": 95,
        "良好": 85,
        "中等": 72.5,
        "及格": 67.5,
        "不及格": 30
    }

    def __init__(
        self,
        factors: List[str] = None,
        weights: Optional[Dict[str, float]] = None,
        score_thresholds: Optional[Dict[str, Tuple[float, float]]] = None
    ):
        """
        初始化模糊综合评价器

        Args:
            factors: 评价因素列表（默认五维）
            weights: 因素权重字典
            score_thresholds: 等级阈值定义
        """
        self.factors = factors or [
            "参与度", "教育性", "创新性", "影响力", "可持续性"
        ]

        # 默认等权重
        if weights is None:
            n = len(self.factors)
            self.weights = np.array([1.0 / n] * n)
        else:
            self.weights = np.array([
                weights.get(f, 1.0 / len(self.factors))
                for f in self.factors
            ])
            # 归一化
            self.weights = self.weights / np.sum(self.weights)

        self.membership_func = FuzzyMembershipFunction()
        self.levels = ["优秀", "良好", "中等", "及格", "不及格"]

    def build_evaluation_matrix(
        self,
        scores: Dict[str, float]
    ) -> np.ndarray:
        """
        构建模糊评价矩阵

        Args:
            scores: 各因素得分

        Returns:
            模糊评价矩阵 R (n_factors × n_levels)
        """
        matrix = np.zeros((len(self.factors), len(self.levels)))

        for i, factor in enumerate(self.factors):
            score = scores.get(factor, 0)
            matrix[i] = self.membership_func.get_membership_vector(score)

        return matrix

    def fuzzy_composition(
        self,
        evaluation_matrix: np.ndarray,
        method: str = "weighted_average"
    ) -> np.ndarray:
        """
        模糊合成运算

        Args:
            evaluation_matrix: 评价矩阵
            method: 合成方法
                   - "weighted_average": 加权平均型 (M(·,+))
                   - "max_min": 主因素决定型 (M(∧,∨))
                   - "max_product": 主因素突出型 (M(·,∨))

        Returns:
            合成结果向量
        """
        if method == "weighted_average":
            # M(·,+): b_j = Σ(w_i × r_ij)
            return self.weights @ evaluation_matrix

        elif method == "max_min":
            # M(∧,∨): b_j = max_i(min(w_i, r_ij))
            result = np.zeros(len(self.levels))
            for j in range(len(self.levels)):
                result[j] = np.max(np.minimum(self.weights, evaluation_matrix[:, j]))
            return result

        elif method == "max_product":
            # M(·,∨): b_j = max_i(w_i × r_ij)
            result = np.zeros(len(self.levels))
            for j in range(len(self.levels)):
                result[j] = np.max(self.weights * evaluation_matrix[:, j])
            return result

        else:
            raise ValueError(f"Unknown method: {method}")

    def evaluate(
        self,
        scores: Dict[str, float],
        composition_method: str = "weighted_average"
    ) -> FuzzyEvaluationResult:
        """
        进行模糊综合评价

        Args:
            scores: 各因素得分 {因素: 得分}
            composition_method: 模糊合成方法

        Returns:
            评价结果
        """
        # 1. 构建评价矩阵
        R = self.build_evaluation_matrix(scores)

        # 2. 模糊合成
        B = self.fuzzy_composition(R, composition_method)

        # 3. 归一化
        B = B / np.sum(B) if np.sum(B) > 0 else B

        # 4. 计算综合得分
        level_scores = np.array([self.LEVEL_SCORES[level] for level in self.levels])
        final_score = B @ level_scores

        # 5. 确定等级
        max_idx = np.argmax(B)
        grade = self.levels[max_idx]

        # 6. 计算置信度（最大隶属度与次大隶属度之比）
        sorted_b = np.sort(B)[::-1]
        confidence = sorted_b[0] / (sorted_b[1] + 1e-10) if len(sorted_b) > 1 else 1.0

        return FuzzyEvaluationResult(
            final_score=float(final_score),
            grade=grade,
            membership_vector=B,
            evaluation_matrix=R,
            confidence=float(confidence)
        )

    def evaluate_with_detailed_analysis(
        self,
        scores: Dict[str, float],
        composition_method: str = "weighted_average"
    ) -> Dict:
        """
        详细分析版评价

        包含各维度的详细分析结果
        """
        result = self.evaluate(scores, composition_method)

        # 各维度详细分析
        dimension_analysis = []
        for i, factor in enumerate(self.factors):
            membership = result.evaluation_matrix[i]
            max_idx = np.argmax(membership)
            dimension_analysis.append({
                "factor": factor,
                "score": scores.get(factor, 0),
                "primary_level": self.levels[max_idx],
                "membership": {
                    level: round(float(membership[j]), 4)
                    for j, level in enumerate(self.levels)
                },
                "weight": round(float(self.weights[i]), 4)
            })

        # 等级分布
        grade_distribution = {
            level: round(float(result.membership_vector[i]), 4)
            for i, level in enumerate(self.levels)
        }

        # 改进建议
        suggestions = self._generate_suggestions(scores, dimension_analysis)

        return {
            "final_score": round(result.final_score, 2),
            "grade": result.grade,
            "confidence": round(result.confidence, 2),
            "dimension_analysis": dimension_analysis,
            "grade_distribution": grade_distribution,
            "improvement_suggestions": suggestions,
            "method_used": composition_method
        }

    def _generate_suggestions(
        self,
        scores: Dict[str, float],
        dimension_analysis: List[Dict]
    ) -> List[str]:
        """生成改进建议"""
        suggestions = []

        # 找出得分最低的维度
        sorted_dims = sorted(
            dimension_analysis,
            key=lambda x: x["score"]
        )

        # 如果最低分低于60分
        if sorted_dims[0]["score"] < 60:
            suggestions.append(
                f"{sorted_dims[0]['factor']}维度得分较低({sorted_dims[0]['score']}分)，"
                f"建议重点改进"
            )

        # 如果总分低于70分
        avg_score = np.mean(list(scores.values()))
        if avg_score < 70:
            suggestions.append("整体活动效果有待提升，建议全面审查活动各环节")

        # 检查不平衡性
        score_std = np.std(list(scores.values()))
        if score_std > 15:
            suggestions.append("各维度得分差异较大，建议优化活动的整体协调性")

        # 如果创新性低但可持续性高
        innovation_score = scores.get("创新性", 0)
        sustainability_score = scores.get("可持续性", 0)
        if innovation_score < 70 and sustainability_score > 80:
            suggestions.append("活动可持续性较高但创新性不足，建议在保持现有优势基础上增加创新元素")

        return suggestions

    def compare_activities(
        self,
        activities: List[Dict[str, any]]
    ) -> Dict:
        """
        对比多个活动

        Args:
            activities: 活动列表，每项包含id、name、scores

        Returns:
            对比结果
        """
        results = []
        for activity in activities:
            eval_result = self.evaluate(activity["scores"])
            results.append({
                "id": activity.get("id"),
                "name": activity.get("name"),
                "final_score": eval_result.final_score,
                "grade": eval_result.grade,
                "confidence": eval_result.confidence
            })

        # 排序
        results.sort(key=lambda x: x["final_score"], reverse=True)

        # 计算统计信息
        scores = [r["final_score"] for r in results]

        return {
            "ranking": results,
            "statistics": {
                "highest_score": max(scores),
                "lowest_score": min(scores),
                "average_score": round(np.mean(scores), 2),
                "std": round(np.std(scores), 2)
            },
            "best_activity": results[0] if results else None
        }

    def sensitivity_analysis(
        self,
        scores: Dict[str, float],
        weight_perturbation: float = 0.2,
        n_simulations: int = 100
    ) -> Dict:
        """
        权重敏感性分析

        分析权重变化对评价结果的影响
        """
        scores_history = []

        for _ in range(n_simulations):
            # 扰动权重
            perturbed_weights = self.weights * (
                1 + np.random.uniform(-weight_perturbation, weight_perturbation, len(self.weights))
            )
            perturbed_weights = perturbed_weights / np.sum(perturbed_weights)

            # 临时设置权重
            original_weights = self.weights
            self.weights = perturbed_weights

            result = self.evaluate(scores)
            scores_history.append(result.final_score)

            self.weights = original_weights

        scores_array = np.array(scores_history)

        return {
            "mean_score": round(float(np.mean(scores_array)), 2),
            "std_score": round(float(np.std(scores_array)), 2),
            "min_score": round(float(np.min(scores_array)), 2),
            "max_score": round(float(np.max(scores_array)), 2),
            "cv": round(float(np.std(scores_array) / np.mean(scores_array)), 4),
            "stability": "stable" if np.std(scores_array) < 5 else "unstable"
        }

    def export_model(self, filepath: str):
        """导出模型配置"""
        data = {
            "factors": self.factors,
            "weights": self.weights.tolist(),
            "levels": self.levels,
            "level_scores": self.LEVEL_SCORES
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    @classmethod
    def load_model(cls, filepath: str) -> "FuzzyComprehensiveEvaluator":
        """加载模型配置"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        evaluator = cls.__new__(cls)
        evaluator.factors = data["factors"]
        evaluator.weights = np.array(data["weights"])
        evaluator.levels = data["levels"]
        evaluator.LEVEL_SCORES = data["level_scores"]
        evaluator.membership_func = FuzzyMembershipFunction()

        return evaluator
