"""
AHP层次分析法评估器
用于计算五维活动效果评估指标的权重

五维指标：
- 参与度 (Engagement)
- 教育性 (Educational)
- 创新性 (Innovation)
- 影响力 (Impact)
- 可持续性 (Sustainability)
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import json


class EvaluationDimension(Enum):
    """五维评估维度"""
    ENGAGEMENT = "参与度"       # 学生参与程度
    EDUCATIONAL = "教育性"      # 教育价值
    INNOVATION = "创新性"       # 创新程度
    IMPACT = "影响力"           # 社会/校园影响
    SUSTAINABILITY = "可持续性"  # 活动可持续性/长期价值


@dataclass
class AHPWeights:
    """AHP权重结果"""
    weights: Dict[str, float]
    consistency_ratio: float
    consistency_check_passed: bool
    eigenvalues: np.ndarray
    eigenvector: np.ndarray


class AHPEvaluator:
    """
    AHP层次分析法评估器

    使用步骤:
    1. 构建判断矩阵
    2. 计算权重向量
    3. 一致性检验
    4. 获取各维度权重

    示例:
        evaluator = AHPEvaluator()
        # 使用默认的判断矩阵或自定义
        weights = evaluator.calculate_weights()
        print(weights.weights)
    """

    # 标准1-9标度
    SCALE_DESCRIPTIONS = {
        1: "同等重要",
        3: "稍微重要",
        5: "明显重要",
        7: "强烈重要",
        9: "极端重要",
        2: "介于1和3之间",
        4: "介于3和5之间",
        6: "介于5和7之间",
        8: "介于7和9之间"
    }

    # 随机一致性指标RI
    RI_TABLE = {
        1: 0.00,
        2: 0.00,
        3: 0.58,
        4: 0.90,
        5: 1.12,
        6: 1.24,
        7: 1.32,
        8: 1.41,
        9: 1.45,
        10: 1.49
    }

    def __init__(
        self,
        criteria: List[str] = None,
        consistency_threshold: float = 0.1
    ):
        """
        初始化AHP评估器

        Args:
            criteria: 评估准则列表，默认为五维指标
            consistency_threshold: 一致性比率阈值，默认0.1
        """
        self.criteria = criteria or [
            EvaluationDimension.ENGAGEMENT.value,
            EvaluationDimension.EDUCATIONAL.value,
            EvaluationDimension.INNOVATION.value,
            EvaluationDimension.IMPACT.value,
            EvaluationDimension.SUSTAINABILITY.value
        ]
        self.n = len(self.criteria)
        self.consistency_threshold = consistency_threshold
        self.comparison_matrix: Optional[np.ndarray] = None

    def build_comparison_matrix(
        self,
        judgments: Optional[Dict[Tuple[int, int], float]] = None
    ) -> np.ndarray:
        """
        构建判断矩阵

        Args:
            judgments: 自定义判断值，格式为 {(i,j): value}
                      如果不提供，使用默认的校园活动经验判断

        Returns:
            判断矩阵
        """
        matrix = np.ones((self.n, self.n))

        if judgments:
            for (i, j), value in judgments.items():
                matrix[i, j] = value
                matrix[j, i] = 1.0 / value
        else:
            # 默认判断矩阵（基于校园活动经验）
            # 行/列顺序: 参与度, 教育性, 创新性, 影响力, 可持续性
            default_judgments = {
                (0, 1): 2.0,   # 参与度比教育性稍微重要
                (0, 2): 1.5,   # 参与度比创新性略重要
                (0, 3): 1.0,   # 参与度与影响力同等重要
                (0, 4): 2.0,   # 参与度比可持续性稍微重要
                (1, 2): 0.5,   # 教育性比创新性略不重要
                (1, 3): 0.5,   # 教育性比影响力略不重要
                (1, 4): 1.0,   # 教育性与可持续性同等重要
                (2, 3): 0.67,  # 创新性比影响力略不重要
                (2, 4): 0.5,   # 创新性比可持续性略不重要
                (3, 4): 2.0,   # 影响力比可持续性稍微重要
            }

            for (i, j), value in default_judgments.items():
                matrix[i, j] = value
                matrix[j, i] = 1.0 / value

        self.comparison_matrix = matrix
        return matrix

    def calculate_weights(
        self,
        method: str = "eigenvalue"
    ) -> AHPWeights:
        """
        计算权重向量

        Args:
            method: 计算方法，可选 "eigenvalue"(特征值法), "geometric"(几何平均法)

        Returns:
            AHPWeights对象，包含权重和一致性检验结果
        """
        if self.comparison_matrix is None:
            self.build_comparison_matrix()

        if method == "eigenvalue":
            weights, eigenvalues, eigenvector = self._eigenvalue_method()
        elif method == "geometric":
            weights, eigenvalues, eigenvector = self._geometric_method()
        else:
            raise ValueError(f"Unknown method: {method}")

        # 一致性检验
        cr = self._calculate_consistency_ratio(eigenvalues)

        weights_dict = {
            criterion: float(weight)
            for criterion, weight in zip(self.criteria, weights)
        }

        return AHPWeights(
            weights=weights_dict,
            consistency_ratio=cr,
            consistency_check_passed=cr < self.consistency_threshold,
            eigenvalues=eigenvalues,
            eigenvector=eigenvector
        )

    def _eigenvalue_method(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """特征值法计算权重"""
        # 计算特征值和特征向量
        eigenvalues, eigenvectors = np.linalg.eig(self.comparison_matrix)

        # 找到最大特征值
        max_idx = np.argmax(eigenvalues.real)
        max_eigenvalue = eigenvalues[max_idx].real
        eigenvector = eigenvectors[:, max_idx].real

        # 归一化得到权重
        weights = eigenvector / np.sum(eigenvector)

        return weights, np.array([max_eigenvalue]), eigenvector

    def _geometric_method(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """几何平均法计算权重"""
        # 计算每行的几何平均数
        product = np.prod(self.comparison_matrix, axis=1)
        geometric_means = np.power(product, 1.0 / self.n)

        # 归一化
        weights = geometric_means / np.sum(geometric_means)

        # 计算最大特征值（近似）
        weighted_sum = self.comparison_matrix @ weights
        max_eigenvalue = np.mean(weighted_sum / weights)

        return weights, np.array([max_eigenvalue]), geometric_means

    def _calculate_consistency_ratio(self, eigenvalues: np.ndarray) -> float:
        """计算一致性比率CR"""
        if len(eigenvalues) == 0:
            return 0.0

        max_eigenvalue = np.max(eigenvalues.real)

        # 一致性指标 CI = (λmax - n) / (n - 1)
        ci = (max_eigenvalue - self.n) / (self.n - 1)

        # 一致性比率 CR = CI / RI
        ri = self.RI_TABLE.get(self.n, 1.49)
        cr = ci / ri if ri > 0 else 0.0

        return float(cr)

    def calculate_sub_criteria_weights(
        self,
        dimension: str,
        sub_criteria: List[str],
        judgments: Optional[Dict[Tuple[int, int], float]] = None
    ) -> AHPWeights:
        """
        计算子准则层权重（用于更细粒度的评估）

        Args:
            dimension: 父维度名称
            sub_criteria: 子准则列表
            judgments: 子准则判断矩阵，如果不提供则使用均等权重

        Returns:
            子准则权重
        """
        # 临时保存当前状态
        original_criteria = self.criteria
        original_matrix = self.comparison_matrix
        original_n = self.n

        # 设置子准则
        self.criteria = sub_criteria
        self.n = len(sub_criteria)
        self.comparison_matrix = None

        # 构建判断矩阵
        if judgments is None:
            # 创建等重要性判断矩阵（单位矩阵）
            judgments = {}
            for i in range(self.n):
                for j in range(i + 1, self.n):
                    judgments[(i, j)] = 1.0  # 同等重要

        self.build_comparison_matrix(judgments)

        # 计算权重
        weights = self.calculate_weights()

        # 恢复原始状态
        self.criteria = original_criteria
        self.n = original_n
        self.comparison_matrix = original_matrix

        return weights

    def sensitivity_analysis(
        self,
        perturbation_range: Tuple[float, float] = (0.8, 1.2),
        n_simulations: int = 100
    ) -> Dict[str, Dict[str, float]]:
        """
        敏感性分析

        通过扰动判断矩阵元素，分析权重的稳定性

        Args:
            perturbation_range: 扰动范围
            n_simulations: 模拟次数

        Returns:
            各准则权重的统计信息
        """
        if self.comparison_matrix is None:
            self.build_comparison_matrix()

        weights_history = {criterion: [] for criterion in self.criteria}

        for _ in range(n_simulations):
            # 复制原矩阵
            perturbed_matrix = self.comparison_matrix.copy()

            # 随机扰动上三角元素
            for i in range(self.n):
                for j in range(i + 1, self.n):
                    perturbation = np.random.uniform(*perturbation_range)
                    perturbed_matrix[i, j] *= perturbation
                    perturbed_matrix[j, i] = 1.0 / perturbed_matrix[i, j]

            # 临时设置扰动矩阵并计算权重
            original_matrix = self.comparison_matrix
            self.comparison_matrix = perturbed_matrix

            weights = self.calculate_weights()
            for criterion, weight in weights.weights.items():
                weights_history[criterion].append(weight)

            self.comparison_matrix = original_matrix

        # 统计结果
        results = {}
        for criterion, values in weights_history.items():
            values_array = np.array(values)
            results[criterion] = {
                "mean": float(np.mean(values_array)),
                "std": float(np.std(values_array)),
                "min": float(np.min(values_array)),
                "max": float(np.max(values_array)),
                "cv": float(np.std(values_array) / np.mean(values_array)) if np.mean(values_array) > 0 else 0
            }

        return results


class FiveDimensionEvaluator:
    """
    五维活动效果评估器

    整合AHP权重计算和活动评分功能
    """

    DIMENSIONS = [
        "参与度",
        "教育性",
        "创新性",
        "影响力",
        "可持续性"
    ]

    def __init__(self, consistency_threshold: float = 0.1):
        self.ahp = AHPEvaluator(
            criteria=self.DIMENSIONS,
            consistency_threshold=consistency_threshold
        )
        self.weights: Optional[AHPWeights] = None

    def fit(self, custom_judgments: Optional[Dict[Tuple[int, int], float]] = None):
        """
        训练/计算权重

        Args:
            custom_judgments: 自定义判断矩阵值
        """
        self.ahp.build_comparison_matrix(custom_judgments)
        self.weights = self.ahp.calculate_weights()
        return self

    def evaluate_activity(
        self,
        scores: Dict[str, float]
    ) -> Dict:
        """
        评估单个活动

        Args:
            scores: 各维度得分，范围[0, 100]

        Returns:
            评估结果
        """
        if self.weights is None:
            raise RuntimeError("请先调用fit()计算权重")

        # 验证输入
        for dim in self.DIMENSIONS:
            if dim not in scores:
                raise ValueError(f"缺少维度得分: {dim}")

        # 计算加权总分
        weighted_score = sum(
            scores[dim] * self.weights.weights[dim]
            for dim in self.DIMENSIONS
        )

        # 计算各维度贡献度
        contributions = {
            dim: scores[dim] * self.weights.weights[dim]
            for dim in self.DIMENSIONS
        }

        return {
            "total_score": round(weighted_score, 2),
            "dimension_scores": {k: round(v, 2) for k, v in scores.items()},
            "weights": {k: round(v, 4) for k, v in self.weights.weights.items()},
            "contributions": {k: round(v, 2) for k, v in contributions.items()},
            "consistency_ratio": round(self.weights.consistency_ratio, 4),
            "consistency_check_passed": self.weights.consistency_check_passed
        }

    def evaluate_batch(
        self,
        activities: List[Dict[str, Dict[str, float]]]
    ) -> List[Dict]:
        """
        批量评估活动

        Args:
            activities: 活动列表，每个活动包含id和scores

        Returns:
            评估结果列表
        """
        results = []
        for activity in activities:
            result = self.evaluate_activity(activity["scores"])
            result["activity_id"] = activity.get("id")
            results.append(result)
        return results

    def get_dimension_weights(self) -> Dict[str, float]:
        """获取各维度权重"""
        if self.weights is None:
            raise RuntimeError("请先调用fit()计算权重")
        return self.weights.weights

    def export_weights(self, filepath: str):
        """导出权重到JSON文件"""
        if self.weights is None:
            raise RuntimeError("请先调用fit()计算权重")

        data = {
            "dimensions": self.DIMENSIONS,
            "weights": self.weights.weights,
            "consistency_ratio": self.weights.consistency_ratio,
            "consistency_check_passed": self.weights.consistency_check_passed,
            "comparison_matrix": self.ahp.comparison_matrix.tolist()
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    @classmethod
    def load_weights(cls, filepath: str) -> "FiveDimensionEvaluator":
        """从JSON文件加载权重"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        evaluator = cls()
        evaluator.ahp.comparison_matrix = np.array(data["comparison_matrix"])
        evaluator.weights = AHPWeights(
            weights=data["weights"],
            consistency_ratio=data["consistency_ratio"],
            consistency_check_passed=data["consistency_check_passed"],
            eigenvalues=np.array([]),
            eigenvector=np.array([])
        )

        return evaluator
