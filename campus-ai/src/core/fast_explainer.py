# campus-ai/src/core/fast_explainer.py

from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
import numpy as np
from typing import List, Dict
import joblib


class FastExplainableClustering:
    """
    快速可解释聚类

    解决SHAP实时计算太慢的问题:
    - V2: KernelSHAP每次预测需O(T×M×2^|S|) ~ 3-5秒
    - V3: 预训练Ridge回归解释器，每次预测O(n_features) ~ 5毫秒

    原理: 用线性模型近似聚类决策边界，特征系数即为特征重要性
    """

    def __init__(
        self,
        regularization: float = 1.0,
        top_k_features: int = 5
    ):
        self.regularization = regularization
        self.top_k_features = top_k_features
        self.explainers_: Dict[int, Ridge] = {}
        self.scaler_ = StandardScaler()
        self.feature_names_: List[str] = []

    def fit(
        self,
        X: np.ndarray,
        cluster_labels: np.ndarray,
        cluster_centers: np.ndarray,
        feature_names: List[str]
    ) -> 'FastExplainableClustering':
        """
        为每个聚类训练解释器

        Args:
            X: 原始特征 (n_samples, n_features)
            cluster_labels: 聚类标签 (n_samples,)
            cluster_centers: 聚类中心 (n_clusters, n_features_reduced)
            feature_names: 特征名列表
        """
        self.feature_names_ = feature_names
        X_scaled = self.scaler_.fit_transform(X)

        n_clusters = len(np.unique(cluster_labels))

        for cluster_id in range(n_clusters):
            # 创建二分类问题: 属于该聚类 vs 不属于
            y_binary = (cluster_labels == cluster_id).astype(int)

            # 用Ridge回归学习决策边界
            pos_idx = np.where(y_binary == 1)[0]
            neg_idx = np.where(y_binary == 0)[0]

            # 平衡采样
            n_pos = len(pos_idx)
            n_neg_sample = min(n_pos * 3, len(neg_idx))
            neg_sample_idx = np.random.choice(neg_idx, n_neg_sample, replace=False)

            sample_idx = np.concatenate([pos_idx, neg_sample_idx])
            X_sample = X_scaled[sample_idx]
            y_sample = y_binary[sample_idx]

            # 训练Ridge分类器
            ridge = Ridge(alpha=self.regularization)
            ridge.fit(X_sample, y_sample)

            self.explainers_[cluster_id] = ridge

        return self

    def explain(
        self,
        student_features: np.ndarray,
        cluster_id: int
    ) -> Dict:
        """
        快速解释聚类结果

        Returns:
            {
                "top_positive_features": [("feature_name", weight), ...],
                "top_negative_features": [("feature_name", weight), ...],
                "confidence": float
            }
        """
        if cluster_id not in self.explainers_:
            raise ValueError(f"Unknown cluster_id: {cluster_id}")

        ridge = self.explainers_[cluster_id]

        # 标准化特征
        student_scaled = self.scaler_.transform(student_features.reshape(1, -1))

        # 获取特征系数 (O(n_features)复杂度)
        coefficients = ridge.coef_

        # 按重要性排序
        feature_importance = list(zip(self.feature_names_, coefficients))
        feature_importance.sort(key=lambda x: abs(x[1]), reverse=True)

        # 正负向特征
        top_positive = [
            (name, float(weight))
            for name, weight in feature_importance
            if weight > 0
        ][:self.top_k_features]

        top_negative = [
            (name, float(weight))
            for name, weight in feature_importance
            if weight < 0
        ][:self.top_k_features]

        # 预测置信度
        prediction = ridge.predict(student_scaled)[0]
        confidence = float(prediction)

        return {
            "cluster_id": cluster_id,
            "top_positive_features": top_positive,
            "top_negative_features": top_negative,
            "confidence": confidence,
            "explanation_method": "ridge_approximation"
        }

    def batch_explain(
        self,
        X: np.ndarray,
        cluster_labels: np.ndarray
    ) -> List[Dict]:
        """批量解释"""
        explanations = []
        for i, features in enumerate(X):
            exp = self.explain(features, cluster_labels[i])
            explanations.append(exp)
        return explanations

    def save(self, path: str):
        """保存解释器"""
        joblib.dump({
            "explainers": self.explainers_,
            "scaler": self.scaler_,
            "feature_names": self.feature_names_,
            "regularization": self.regularization,
            "top_k_features": self.top_k_features
        }, path)

    @classmethod
    def load(cls, path: str) -> 'FastExplainableClustering':
        """加载解释器"""
        data = joblib.load(path)
        instance = cls.__new__(cls)
        instance.explainers_ = data["explainers"]
        instance.scaler_ = data["scaler"]
        instance.feature_names_ = data["feature_names"]
        instance.regularization = data["regularization"]
        instance.top_k_features = data["top_k_features"]
        return instance
