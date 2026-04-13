# campus-ai/src/tasks/clustering_tasks.py

from celery import shared_task
from celery.exceptions import SoftTimeLimitExceeded
from typing import List, Dict
import numpy as np
import pandas as pd
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.scalable_pipeline import ScalableFeaturePipeline
from core.fast_explainer import FastExplainableClustering


@shared_task(bind=True, max_retries=3, soft_time_limit=300)
def train_clustering_model(
    self,
    student_ids: List[str] = None,
    n_clusters: int = 6,
    model_version: str = None
) -> Dict:
    """
    异步训练聚类模型

    时间预估:
    - 1000学生: ~30秒
    - 10000学生: ~2分钟
    - 100000学生: ~5分钟
    """
    try:
        # 从数据库获取特征数据（模拟）
        features_df = _get_student_features_from_db(student_ids)
        feature_names = features_df.columns.tolist()
        X = features_df.values

        # 训练管道
        pipeline = ScalableFeaturePipeline(
            n_clusters=n_clusters,
            batch_size=1000
        )
        pipeline.fit(X)

        # 预测
        labels = pipeline.predict(X)
        cluster_centers = pipeline.kmeans_.cluster_centers_

        # 训练解释器
        explainer = FastExplainableClustering()
        explainer.fit(X, labels, cluster_centers, feature_names)

        # 保存模型
        if model_version:
            pipeline.save(model_version)
            explainer.save(f"{pipeline.model_dir}/explainer_{model_version}.joblib")

        return {
            "status": "success",
            "model_version": model_version,
            "n_students": len(X),
            "n_clusters": n_clusters,
            "silhouette_score": float(pipeline.kmeans_.inertia_)
        }

    except SoftTimeLimitExceeded:
        self.retry(countdown=60)
    except Exception as exc:
        self.retry(exc=exc, countdown=30)


@shared_task(bind=True, max_retries=3)
def predict_student_clusters(
    self,
    student_ids: List[str],
    model_version: str
) -> List[Dict]:
    """异步预测学生聚类"""
    try:
        # 加载模型
        pipeline = ScalableFeaturePipeline.load(model_version)
        explainer = FastExplainableClustering.load(
            f"{pipeline.model_dir}/explainer_{model_version}.joblib"
        )

        # 获取特征
        features_df = _get_student_features_from_db(student_ids)
        X = features_df.values

        # 预测
        labels = pipeline.predict(X)

        # 生成解释
        explanations = explainer.batch_explain(X, labels)

        # 组装结果
        results = []
        for i, student_id in enumerate(student_ids):
            results.append({
                "student_id": student_id,
                "cluster_id": int(labels[i]),
                "explanation": explanations[i]
            })

        return results

    except Exception as exc:
        self.retry(exc=exc, countdown=10)


def _get_student_features_from_db(student_ids: List[str] = None) -> pd.DataFrame:
    """从数据库获取学生特征（模拟实现）"""
    # 实际实现应查询数据库
    if student_ids is None:
        # 返回模拟数据
        np.random.seed(42)
        return pd.DataFrame(
            np.random.randn(1000, 20),
            columns=[f"feature_{i}" for i in range(20)]
        )

    # 根据ID查询
    np.random.seed(42)
    return pd.DataFrame(
        np.random.randn(len(student_ids), 20),
        columns=[f"feature_{i}" for i in range(20)],
        index=student_ids
    )
