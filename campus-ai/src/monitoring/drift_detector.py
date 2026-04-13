# campus-ai/src/monitoring/drift_detector.py

import numpy as np
from scipy import stats
from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime
import json


@dataclass
class DriftReport:
    """漂移检测报告"""
    feature_name: str
    drift_detected: bool
    p_value: float
    statistic: float
    baseline_mean: float
    current_mean: float
    severity: str  # low, medium, high


class DataDriftDetector:
    """
    数据漂移检测器

    检测方法:
    1. KS检验: 检测分布变化
    2. PSI (Population Stability Index): 检测人群稳定性
    3. Wasserstein距离: 检测分布偏移程度
    """

    def __init__(
        self,
        psi_threshold: float = 0.2,
        ks_pvalue_threshold: float = 0.05,
        wasserstein_threshold: float = 0.1
    ):
        self.psi_threshold = psi_threshold
        self.ks_pvalue_threshold = ks_pvalue_threshold
        self.wasserstein_threshold = wasserstein_threshold

        self.baseline_stats: Dict[str, dict] = {}

    def fit_baseline(self, X: np.ndarray, feature_names: List[str]):
        """建立基线统计"""
        for i, name in enumerate(feature_names):
            self.baseline_stats[name] = {
                "mean": float(np.mean(X[:, i])),
                "std": float(np.std(X[:, i])),
                "min": float(np.min(X[:, i])),
                "max": float(np.max(X[:, i])),
                "percentiles": np.percentile(X[:, i], [5, 25, 50, 75, 95]).tolist(),
                "histogram": np.histogram(X[:, i], bins=20)[0].tolist()
            }

    def detect_drift(
        self,
        X_current: np.ndarray,
        feature_names: List[str]
    ) -> List[DriftReport]:
        """检测数据漂移"""
        reports = []

        for i, name in enumerate(feature_names):
            baseline = self.baseline_stats.get(name)
            if not baseline:
                continue

            current = X_current[:, i]

            # KS检验
            baseline_samples = np.random.normal(
                baseline["mean"],
                baseline["std"],
                size=len(current)
            )
            ks_stat, ks_pvalue = stats.ks_2samp(baseline_samples, current)

            # PSI计算
            psi = self._calculate_psi(baseline["histogram"], current)

            # Wasserstein距离
            wasserstein = stats.wasserstein_distance(baseline_samples, current)

            # 判断是否漂移
            drift_detected = (
                ks_pvalue < self.ks_pvalue_threshold or
                psi > self.psi_threshold or
                wasserstein > self.wasserstein_threshold
            )

            # 严重度评估
            severity = "low"
            if psi > 0.3 or ks_pvalue < 0.01:
                severity = "high"
            elif psi > 0.2 or ks_pvalue < 0.05:
                severity = "medium"

            reports.append(DriftReport(
                feature_name=name,
                drift_detected=drift_detected,
                p_value=float(ks_pvalue),
                statistic=float(ks_stat),
                baseline_mean=baseline["mean"],
                current_mean=float(np.mean(current)),
                severity=severity
            ))

        return reports

    def _calculate_psi(self, expected_hist: List, current: np.ndarray) -> float:
        """计算PSI"""
        bins = len(expected_hist)
        current_hist, _ = np.histogram(current, bins=bins)

        expected_pct = np.array(expected_hist) / sum(expected_hist)
        current_pct = current_hist / sum(current_hist)

        expected_pct = np.where(expected_pct == 0, 0.0001, expected_pct)
        current_pct = np.where(current_pct == 0, 0.0001, current_pct)

        psi = np.sum((current_pct - expected_pct) * np.log(current_pct / expected_pct))
        return float(psi)

    def generate_report(self, reports: List[DriftReport]) -> Dict:
        """生成漂移检测报告"""
        drifted_features = [r for r in reports if r.drift_detected]
        high_severity = [r for r in drifted_features if r.severity == "high"]

        return {
            "timestamp": datetime.now().isoformat(),
            "total_features": len(reports),
            "drifted_features_count": len(drifted_features),
            "high_severity_count": len(high_severity),
            "drift_rate": len(drifted_features) / len(reports) if reports else 0,
            "needs_retraining": len(high_severity) > 0,
            "drifted_features": [
                {
                    "name": r.feature_name,
                    "severity": r.severity,
                    "p_value": r.p_value,
                    "baseline_mean": r.baseline_mean,
                    "current_mean": r.current_mean
                }
                for r in drifted_features
            ]
        }
