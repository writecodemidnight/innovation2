# campus-ai/tests/integration/test_celery_tasks.py
import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


# Skip all tests if Celery is not installed
pytestmark = pytest.mark.skipif(
    not pytest.importorskip("celery", reason="Celery not installed"),
    reason="Celery not installed"
)


class TestCeleryTasks:
    """测试Celery异步任务"""

    @pytest.fixture
    def mock_celery(self):
        """模拟Celery任务"""
        with patch('src.tasks.clustering_tasks._get_student_features_from_db') as mock_db:
            mock_db.return_value = MagicMock()
            yield mock_db

    def test_train_clustering_model_task_exists(self):
        """测试训练任务存在"""
        from src.tasks.clustering_tasks import train_clustering_model
        assert train_clustering_model is not None

    def test_predict_student_clusters_task_exists(self):
        """测试预测任务存在"""
        from src.tasks.clustering_tasks import predict_student_clusters
        assert predict_student_clusters is not None

    def test_optimize_schedule_task_exists(self):
        """测试调度任务存在"""
        from src.tasks.scheduling_tasks import optimize_schedule
        assert optimize_schedule is not None

    def test_train_forecasting_model_task_exists(self):
        """测试预测模型训练任务存在"""
        from src.tasks.forecasting_tasks import train_forecasting_model
        assert train_forecasting_model is not None

    def test_predict_activity_attendance_task_exists(self):
        """测试活动参与预测任务存在"""
        from src.tasks.forecasting_tasks import predict_activity_attendance
        assert predict_activity_attendance is not None
