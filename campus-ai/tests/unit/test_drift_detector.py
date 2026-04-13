# campus-ai/tests/unit/test_drift_detector.py
import pytest
import sys
from pathlib import Path
import numpy as np

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from monitoring.drift_detector import DataDriftDetector, DriftReport


class TestDataDriftDetector:
    """测试数据漂移检测器"""

    def test_initialization(self):
        """测试初始化"""
        detector = DataDriftDetector(
            psi_threshold=0.2,
            ks_pvalue_threshold=0.05,
            wasserstein_threshold=0.1
        )
        assert detector.psi_threshold == 0.2
        assert detector.ks_pvalue_threshold == 0.05
        assert detector.wasserstein_threshold == 0.1
        assert detector.baseline_stats == {}

    def test_fit_baseline(self):
        """测试基线建立"""
        np.random.seed(42)
        X = np.random.randn(100, 5)
        feature_names = [f"feature_{i}" for i in range(5)]

        detector = DataDriftDetector()
        detector.fit_baseline(X, feature_names)

        assert len(detector.baseline_stats) == 5
        assert "feature_0" in detector.baseline_stats
        assert "mean" in detector.baseline_stats["feature_0"]
        assert "std" in detector.baseline_stats["feature_0"]
        assert "histogram" in detector.baseline_stats["feature_0"]

    def test_detect_drift_no_drift(self):
        """测试无漂移情况 - 使用相同数据作为当前数据"""
        np.random.seed(42)
        X_baseline = np.random.randn(100, 3)
        X_current = X_baseline.copy()  # 完全相同的数据
        feature_names = ["f1", "f2", "f3"]

        detector = DataDriftDetector()
        detector.fit_baseline(X_baseline, feature_names)
        reports = detector.detect_drift(X_current, feature_names)

        assert len(reports) == 3
        for report in reports:
            assert report.feature_name in feature_names
            assert isinstance(report.p_value, float)
            assert 0 <= report.p_value <= 1

    def test_detect_drift_with_drift(self):
        """测试有漂移情况"""
        np.random.seed(42)
        X_baseline = np.random.randn(100, 3)
        X_current = np.random.randn(100, 3) + 5  # 有明显偏移
        feature_names = ["f1", "f2", "f3"]

        detector = DataDriftDetector(
            psi_threshold=0.1,  # 更严格的阈值
            ks_pvalue_threshold=0.01
        )
        detector.fit_baseline(X_baseline, feature_names)
        reports = detector.detect_drift(X_current, feature_names)

        assert len(reports) == 3
        # 大部分应该检测为漂移
        drift_count = sum(1 for r in reports if r.drift_detected)
        assert drift_count >= 2  # 至少2个特征检测到漂移

    def test_generate_report(self):
        """测试报告生成"""
        reports = [
            DriftReport(
                feature_name="f1",
                drift_detected=True,
                p_value=0.001,
                statistic=0.5,
                baseline_mean=0.0,
                current_mean=5.0,
                severity="high"
            ),
            DriftReport(
                feature_name="f2",
                drift_detected=False,
                p_value=0.5,
                statistic=0.1,
                baseline_mean=0.0,
                current_mean=0.1,
                severity="low"
            ),
        ]

        detector = DataDriftDetector()
        report = detector.generate_report(reports)

        assert report["total_features"] == 2
        assert report["drifted_features_count"] == 1
        assert report["high_severity_count"] == 1
        assert report["drift_rate"] == 0.5
        assert report["needs_retraining"] is True
        assert len(report["drifted_features"]) == 1

    def test_report_no_high_severity(self):
        """测试无高严重性漂移的报告"""
        reports = [
            DriftReport(
                feature_name="f1",
                drift_detected=False,
                p_value=0.5,
                statistic=0.1,
                baseline_mean=0.0,
                current_mean=0.1,
                severity="low"
            ),
        ]

        detector = DataDriftDetector()
        report = detector.generate_report(reports)

        assert report["needs_retraining"] is False
        assert report["high_severity_count"] == 0
