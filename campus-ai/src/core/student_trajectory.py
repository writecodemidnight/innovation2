"""
学生活动参与轨迹系统

模型1核心组件：记录和分析学生的活动参与轨迹，为K-Means聚类和个性化推荐提供数据基础

功能：
1. 学生活动参与记录（时间、类型、频率、评分）
2. 轨迹特征提取（用于聚类分析）
3. 兴趣标签生成
4. 个性化推荐接口（桥梁，待扩展）
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict
import json


@dataclass
class ActivityParticipation:
    """单次活动参与记录"""
    activity_id: str
    activity_name: str
    activity_type: str  # 体育、文艺、学术、志愿、社团
    participation_date: datetime
    duration_hours: float
    self_rating: Optional[int] = None  # 1-5分自评
    feedback_text: Optional[str] = None  # 文本反馈（用于NLP分析）
    has_photos: bool = False  # 是否有现场照片（用于图像分析）
    role: str = "participant"  # participant, organizer, volunteer


@dataclass
class StudentTrajectory:
    """学生参与活动轨迹"""
    student_id: str
    student_name: str
    major: str
    grade: int  # 年级 1-4
    participations: List[ActivityParticipation] = field(default_factory=list)

    # 缓存的特征（延迟计算）
    _feature_vector: Optional[np.ndarray] = None
    _cluster_label: Optional[int] = None

    def add_participation(self, participation: ActivityParticipation):
        """添加参与记录"""
        self.participations.append(participation)
        self._feature_vector = None  # 清除缓存

    def get_participation_stats(self) -> Dict:
        """获取参与统计信息"""
        if not self.participations:
            return {
                "total_count": 0,
                "total_hours": 0.0,
                "activity_types": {},
                "avg_rating": 0.0
            }

        # 按活动类型统计
        type_counts = defaultdict(int)
        type_hours = defaultdict(float)
        ratings = []

        for p in self.participations:
            type_counts[p.activity_type] += 1
            type_hours[p.activity_type] += p.duration_hours
            if p.self_rating:
                ratings.append(p.self_rating)

        return {
            "total_count": len(self.participations),
            "total_hours": sum(p.duration_hours for p in self.participations),
            "activity_types": dict(type_counts),
            "type_hours": dict(type_hours),
            "avg_rating": np.mean(ratings) if ratings else 0.0,
            "first_participation": min(p.participation_date for p in self.participations),
            "last_participation": max(p.participation_date for p in self.participations)
        }

    def extract_features(self, activity_types: List[str]) -> np.ndarray:
        """
        提取轨迹特征向量（用于K-Means聚类）

        特征维度：
        1. 各类活动的参与次数（归一化）
        2. 各类活动的总时长（归一化）
        3. 活动参与频率（次/月）
        4. 平均活动评分
        5. 活动类型多样性（参与的类型数/总类型数）
        6. 组织参与比例（作为组织者或志愿者的比例）
        """
        if self._feature_vector is not None:
            return self._feature_vector

        stats = self.get_participation_stats()

        if stats["total_count"] == 0:
            self._feature_vector = np.zeros(len(activity_types) * 2 + 4)
            return self._feature_vector

        features = []

        # 1. 各类活动参与次数占比
        type_counts = stats["activity_types"]
        for atype in activity_types:
            count = type_counts.get(atype, 0)
            features.append(count / stats["total_count"])

        # 2. 各类活动时长占比
        type_hours = stats["type_hours"]
        total_hours = stats["total_hours"]
        for atype in activity_types:
            hours = type_hours.get(atype, 0)
            features.append(hours / total_hours if total_hours > 0 else 0)

        # 3. 活动参与频率（次/月）
        if len(self.participations) >= 2:
            first_date = min(p.participation_date for p in self.participations)
            last_date = max(p.participation_date for p in self.participations)
            months = max(1, (last_date - first_date).days / 30)
            features.append(stats["total_count"] / months)
        else:
            features.append(0.0)

        # 4. 平均评分（归一化到0-1）
        features.append(stats["avg_rating"] / 5.0)

        # 5. 活动类型多样性
        diversity = len(type_counts) / len(activity_types)
        features.append(diversity)

        # 6. 组织参与比例
        organizer_count = sum(1 for p in self.participations if p.role != "participant")
        features.append(organizer_count / stats["total_count"])

        self._feature_vector = np.array(features)
        return self._feature_vector


class StudentTrajectoryManager:
    """
    学生活动轨迹管理器

    管理所有学生的活动参与轨迹，提供聚类分析和个性化推荐功能
    """

    # 标准活动类型
    ACTIVITY_TYPES = ["体育", "文艺", "学术", "志愿", "社团"]

    def __init__(self):
        self.trajectories: Dict[str, StudentTrajectory] = {}
        self._cluster_centers: Optional[np.ndarray] = None

    def register_student(self, student_id: str, student_name: str,
                        major: str, grade: int) -> StudentTrajectory:
        """注册学生"""
        trajectory = StudentTrajectory(
            student_id=student_id,
            student_name=student_name,
            major=major,
            grade=grade
        )
        self.trajectories[student_id] = trajectory
        return trajectory

    def record_participation(self, student_id: str,
                           participation: ActivityParticipation):
        """记录学生参与活动"""
        if student_id not in self.trajectories:
            raise ValueError(f"Student {student_id} not registered")

        self.trajectories[student_id].add_participation(participation)

    def get_trajectory(self, student_id: str) -> Optional[StudentTrajectory]:
        """获取学生轨迹"""
        return self.trajectories.get(student_id)

    def get_all_features(self) -> Tuple[np.ndarray, List[str]]:
        """
        获取所有学生的特征矩阵（用于K-Means聚类）

        Returns:
            (特征矩阵, 学生ID列表)
        """
        features_list = []
        student_ids = []

        for student_id, trajectory in self.trajectories.items():
            features = trajectory.extract_features(self.ACTIVITY_TYPES)
            features_list.append(features)
            student_ids.append(student_id)

        if not features_list:
            return np.array([]), []

        return np.vstack(features_list), student_ids

    def update_cluster_labels(self, labels: np.ndarray, student_ids: List[str]):
        """更新聚类标签（由ScalableFeaturePipeline调用）"""
        for student_id, label in zip(student_ids, labels):
            if student_id in self.trajectories:
                self.trajectories[student_id]._cluster_label = label

    def get_students_by_cluster(self, cluster_id: int) -> List[StudentTrajectory]:
        """获取指定聚类的所有学生"""
        return [
            traj for traj in self.trajectories.values()
            if traj._cluster_label == cluster_id
        ]

    def get_cluster_profiles(self) -> Dict[int, Dict]:
        """
        获取各聚类的特征画像

        Returns:
            {cluster_id: profile_dict}
        """
        profiles = defaultdict(lambda: {
            "count": 0,
            "avg_participation": 0.0,
            "dominant_types": [],
            "students": []
        })

        for student_id, trajectory in self.trajectories.items():
            label = trajectory._cluster_label
            if label is None:
                continue

            stats = trajectory.get_participation_stats()
            profiles[label]["count"] += 1
            profiles[label]["students"].append(student_id)

            # 统计主导活动类型
            if stats["activity_types"]:
                dominant = max(stats["activity_types"].items(), key=lambda x: x[1])
                profiles[label]["dominant_types"].append(dominant[0])

        # 计算每类的平均参与度和主导类型
        for label, profile in profiles.items():
            if profile["count"] > 0:
                # 找出最常见的主导类型
                type_counts = defaultdict(int)
                for t in profile["dominant_types"]:
                    type_counts[t] += 1
                profile["characteristic"] = max(type_counts.items(), key=lambda x: x[1])[0] if type_counts else "未知"
                del profile["dominant_types"]

        return dict(profiles)

    # ==================== 个性化推荐接口（桥梁） ====================

    def recommend_activities(self, student_id: str,
                           available_activities: List[Dict],
                           top_n: int = 5) -> List[Dict]:
        """
        为学生推荐活动（桥梁接口，基础实现）

        当前实现：基于聚类相似度推荐
        未来扩展：可接入深度学习推荐模型

        Args:
            student_id: 学生ID
            available_activities: 可选活动列表
            top_n: 推荐数量

        Returns:
            推荐活动列表（带推荐分数）
        """
        if student_id not in self.trajectories:
            return []

        trajectory = self.trajectories[student_id]
        student_cluster = trajectory._cluster_label

        # 获取学生历史活动类型偏好
        stats = trajectory.get_participation_stats()
        preferred_types = set(stats["activity_types"].keys())

        recommendations = []

        for activity in available_activities:
            score = 0.0
            reasons = []

            # 1. 基于聚类的推荐（如果学生在某个聚类）
            if student_cluster is not None:
                # 检查该活动类型是否被同聚类学生喜欢
                cluster_students = self.get_students_by_cluster(student_cluster)
                cluster_types = defaultdict(int)
                for s in cluster_students:
                    for t in s.get_participation_stats()["activity_types"]:
                        cluster_types[t] += 1

                activity_type = activity.get("type", "")
                if activity_type in cluster_types:
                    score += 0.3
                    reasons.append("同兴趣群体热门")

            # 2. 基于历史偏好的推荐
            activity_type = activity.get("type", "")
            if activity_type in preferred_types:
                score += 0.4
                reasons.append("符合您的历史偏好")
            else:
                # 推荐新类型（多样性）
                score += 0.1
                reasons.append("尝试新类型")

            # 3. 时间冲突检查（基础）
            # TODO: 未来可接入更复杂的调度算法

            recommendations.append({
                "activity": activity,
                "score": min(1.0, score),
                "reasons": reasons
            })

        # 按分数排序
        recommendations.sort(key=lambda x: x["score"], reverse=True)
        return recommendations[:top_n]

    def get_similar_students(self, student_id: str,
                            top_n: int = 5) -> List[Tuple[str, float]]:
        """
        获取相似学生（基于轨迹特征相似度）

        Args:
            student_id: 目标学生ID
            top_n: 返回数量

        Returns:
            [(学生ID, 相似度), ...]
        """
        if student_id not in self.trajectories:
            return []

        target_traj = self.trajectories[student_id]
        target_features = target_traj.extract_features(self.ACTIVITY_TYPES)

        similarities = []
        for sid, traj in self.trajectories.items():
            if sid == student_id:
                continue

            features = traj.extract_features(self.ACTIVITY_TYPES)
            # 余弦相似度
            similarity = np.dot(target_features, features) / (
                np.linalg.norm(target_features) * np.linalg.norm(features) + 1e-10
            )
            similarities.append((sid, similarity))

        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_n]

    def export_trajectory_data(self, filepath: str):
        """导出轨迹数据到JSON"""
        data = {
            "activity_types": self.ACTIVITY_TYPES,
            "students": []
        }

        for student_id, trajectory in self.trajectories.items():
            stats = trajectory.get_participation_stats()
            data["students"].append({
                "student_id": student_id,
                "student_name": trajectory.student_name,
                "major": trajectory.major,
                "grade": trajectory.grade,
                "cluster_label": trajectory._cluster_label,
                "participation_stats": {
                    "total_count": stats["total_count"],
                    "total_hours": stats["total_hours"],
                    "activity_types": stats["activity_types"],
                    "avg_rating": stats["avg_rating"]
                }
            })

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    @classmethod
    def create_sample_data(cls, n_students: int = 100) -> "StudentTrajectoryManager":
        """创建示例数据（用于测试）"""
        import random

        manager = cls()

        # 生成学生
        majors = ["计算机", "机械", "经管", "外语", "艺术"]
        activity_types = cls.ACTIVITY_TYPES

        for i in range(n_students):
            student_id = f"S{i:04d}"
            student_name = f"Student {i}"
            major = random.choice(majors)
            grade = random.randint(1, 4)

            manager.register_student(student_id, student_name, major, grade)

            # 生成参与记录
            n_participations = random.randint(0, 20)
            for _ in range(n_participations):
                participation = ActivityParticipation(
                    activity_id=f"A{random.randint(1, 1000)}",
                    activity_name=f"Activity {random.randint(1, 100)}",
                    activity_type=random.choice(activity_types),
                    participation_date=datetime(2024, 1, 1) + timedelta(days=random.randint(0, 365)),
                    duration_hours=random.uniform(1, 4),
                    self_rating=random.randint(1, 5) if random.random() > 0.3 else None,
                    role=random.choice(["participant", "participant", "participant", "organizer", "volunteer"])
                )
                manager.record_participation(student_id, participation)

        return manager
