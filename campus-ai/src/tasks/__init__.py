# campus-ai/src/tasks/__init__.py

from .celery_app import celery_app
from .clustering_tasks import train_clustering_model, predict_student_clusters
from .scheduling_tasks import optimize_schedule

__all__ = [
    'celery_app',
    'train_clustering_model',
    'predict_student_clusters',
    'optimize_schedule',
]
