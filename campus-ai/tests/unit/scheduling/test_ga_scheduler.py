"""
遗传算法调度器测试
"""

import pytest
import numpy as np
from datetime import datetime, timedelta

from src.scheduling.genetic.ga_scheduler import (
    GAScheduler,
    GeneticAlgorithmConfig,
    Chromosome
)
from src.scheduling.models import Activity, ActivityPriority, TimeSlot


class TestGeneticAlgorithmConfig:
    """测试GA配置"""

    def test_default_config(self):
        """测试默认配置"""
        config = GeneticAlgorithmConfig()

        assert config.population_size == 100
        assert config.generations == 200
        assert config.crossover_rate == 0.8
        assert config.mutation_rate == 0.2
        assert config.multi_objective is True

    def test_custom_config(self):
        """测试自定义配置"""
        config = GeneticAlgorithmConfig(
            population_size=50,
            generations=100,
            crossover_rate=0.9
        )

        assert config.population_size == 50
        assert config.generations == 100
        assert config.crossover_rate == 0.9


class TestChromosome:
    """测试染色体"""

    def test_chromosome_creation(self):
        """测试染色体创建"""
        genes = {
            "A1": TimeSlot("V1", datetime.now(), datetime.now() + timedelta(hours=2)),
            "A2": None
        }

        chromosome = Chromosome(genes=genes)

        assert chromosome.fitness == 0.0
        assert chromosome.genes == genes

    def test_chromosome_copy(self):
        """测试染色体复制"""
        genes = {"A1": None}
        chromosome = Chromosome(genes=genes, fitness=1.0)

        copied = chromosome.copy()

        assert copied.fitness == chromosome.fitness
        assert copied.genes == chromosome.genes


class TestGAScheduler:
    """测试GA调度器"""

    def create_sample_activities(self, n=10):
        """创建示例活动"""
        activities = []
        base_time = datetime(2024, 1, 1, 8, 0)

        priorities = [ActivityPriority.HIGH, ActivityPriority.MEDIUM, ActivityPriority.LOW]

        for i in range(n):
            priority = priorities[i % 3]
            activities.append(Activity(
                id=f"A{i}",
                name=f"Activity {i}",
                priority=priority,
                duration_hours=2.0,
                acceptable_venues=[f"V{i % 3}", f"V{(i+1) % 3}"],
                preferred_time_ranges=[(
                    base_time + timedelta(hours=i*3),
                    base_time + timedelta(hours=i*3+4)
                )],
                min_budget=100 * (priority.value),
                max_budget=500 * (priority.value),
                required_staff_count=2,
                expected_participants=20 * priority.value,
                club_id=f"Club{i % 5}"
            ))

        return activities

    def test_init(self):
        """测试初始化"""
        venues = ["V1", "V2", "V3"]
        staff = ["S1", "S2", "S3", "S4"]
        budget = 10000.0

        config = GeneticAlgorithmConfig(population_size=50, generations=50)
        scheduler = GAScheduler(venues, staff, budget, config)

        assert scheduler.venues == venues
        assert scheduler.available_staff == staff
        assert scheduler.total_budget == budget
        assert scheduler.config.population_size == 50

    def test_schedule(self):
        """测试调度"""
        venues = ["V0", "V1", "V2"]
        staff = ["S1", "S2", "S3", "S4", "S5", "S6"]
        budget = 10000.0

        config = GeneticAlgorithmConfig(
            population_size=30,
            generations=20,
            multi_objective=False
        )

        scheduler = GAScheduler(venues, staff, budget, config)
        activities = self.create_sample_activities(8)

        horizon_start = datetime(2024, 1, 1, 8, 0)
        horizon_end = datetime(2024, 1, 3, 20, 0)

        result = scheduler.schedule(activities, horizon_start, horizon_end)

        assert "scheduled" in result
        assert "unscheduled" in result
        assert "metrics" in result

        # 检查调度了多少活动
        scheduled_count = len(result["scheduled"])
        unscheduled_count = len(result["unscheduled"])
        assert scheduled_count + unscheduled_count == len(activities)

    def test_multi_objective_schedule(self):
        """测试多目标调度"""
        venues = ["V0", "V1", "V2"]
        staff = ["S1", "S2", "S3", "S4", "S5", "S6"]
        budget = 10000.0

        config = GeneticAlgorithmConfig(
            population_size=30,
            generations=20,
            multi_objective=True
        )

        scheduler = GAScheduler(venues, staff, budget, config)
        activities = self.create_sample_activities(8)

        horizon_start = datetime(2024, 1, 1, 8, 0)
        horizon_end = datetime(2024, 1, 3, 20, 0)

        result = scheduler.schedule(activities, horizon_start, horizon_end)

        assert "scheduled" in result
        assert "metrics" in result

    def test_evolution_history(self):
        """测试进化历史"""
        venues = ["V0", "V1", "V2"]
        staff = ["S1", "S2", "S3", "S4", "S5", "S6"]
        budget = 10000.0

        config = GeneticAlgorithmConfig(
            population_size=20,
            generations=10,
            multi_objective=False
        )

        scheduler = GAScheduler(venues, staff, budget, config)
        activities = self.create_sample_activities(5)

        horizon_start = datetime(2024, 1, 1, 8, 0)
        horizon_end = datetime(2024, 1, 3, 20, 0)

        result = scheduler.schedule(activities, horizon_start, horizon_end)

        assert "evolution_history" in result
        assert len(result["evolution_history"]) > 0

        # 检查历史记录结构
        for stats in result["evolution_history"]:
            assert "generation" in stats
            assert "best_fitness" in stats
            assert "avg_fitness" in stats

    def test_compare_with_hierarchical(self):
        """测试与分层调度器对比"""
        venues = ["V0", "V1", "V2"]
        staff = ["S1", "S2", "S3", "S4", "S5", "S6"]
        budget = 10000.0

        config = GeneticAlgorithmConfig(
            population_size=20,
            generations=10
        )

        scheduler = GAScheduler(venues, staff, budget, config)
        activities = self.create_sample_activities(5)

        horizon_start = datetime(2024, 1, 1, 8, 0)
        horizon_end = datetime(2024, 1, 3, 20, 0)

        ga_result = scheduler.schedule(activities, horizon_start, horizon_end)

        # 模拟分层调度器结果
        hierarchical_result = {
            "scheduled": activities[:3],  # 假设分层调度器安排了3个
            "unscheduled": activities[3:]
        }

        comparison = scheduler.compare_with_hierarchical(hierarchical_result)

        assert "scheduled_activities" in comparison
        assert "ga" in comparison["scheduled_activities"]
        assert "hierarchical" in comparison["scheduled_activities"]
        assert "recommendation" in comparison

    def test_empty_activities(self):
        """测试空活动列表"""
        venues = ["V1", "V2"]
        staff = ["S1", "S2"]
        budget = 1000.0

        config = GeneticAlgorithmConfig(population_size=10, generations=5)
        scheduler = GAScheduler(venues, staff, budget, config)

        horizon_start = datetime(2024, 1, 1, 8, 0)
        horizon_end = datetime(2024, 1, 3, 20, 0)

        result = scheduler.schedule([], horizon_start, horizon_end)

        assert result["scheduled"] == []
        assert result["unscheduled"] == []

    def test_objective_calculation(self):
        """测试目标函数计算"""
        venues = ["V0", "V1"]
        staff = ["S1", "S2"]
        budget = 10000.0

        config = GeneticAlgorithmConfig()
        scheduler = GAScheduler(venues, staff, budget, config)

        activities = self.create_sample_activities(5)
        scheduler.activities = activities
        scheduler.horizon_start = datetime(2024, 1, 1, 8, 0)
        scheduler.horizon_end = datetime(2024, 1, 3, 20, 0)

        # 创建一个染色体
        genes = {a.id: None for a in activities}
        # 安排前3个活动
        for i, aid in enumerate(list(genes.keys())[:3]):
            genes[aid] = TimeSlot(
                f"V{i % 2}",
                datetime(2024, 1, 1, 8 + i*3, 0),
                datetime(2024, 1, 1, 10 + i*3, 0)
            )

        chromosome = Chromosome(genes=genes)
        scheduler._evaluate_chromosome(chromosome)

        assert chromosome.fitness > 0
        assert "scheduled" in chromosome.objectives
        assert "no_conflict" in chromosome.objectives
        assert 0 <= chromosome.objectives["scheduled"] <= 1
