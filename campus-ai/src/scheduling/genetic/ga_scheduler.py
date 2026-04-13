"""
遗传算法(GA)资源调度器

基于NSGA-II的多目标遗传算法实现，用于智能资源调度优化

目标：
1. 最大化活动安排数量
2. 最小化场地冲突
3. 均衡预算分配
4. 满足时间偏好

与HierarchicalScheduler的对比：
- GA: 全局搜索，可能找到更优解但计算成本高 O(pop×gens×n²)
- HierarchicalScheduler: 贪心+局部搜索，计算快但可能局部最优 O(n log n)
"""

import numpy as np
import random
from typing import Dict, List, Tuple, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from copy import deepcopy
import sys

# 导入已有的调度模型
from ..models import Activity, TimeSlot, ActivityPriority
from ..hierarchical_scheduler import VenueSchedule


@dataclass
class GeneticAlgorithmConfig:
    """遗传算法配置"""
    population_size: int = 100
    generations: int = 200
    crossover_rate: float = 0.8
    mutation_rate: float = 0.2
    elite_size: int = 10
    tournament_size: int = 5
    early_stopping_generations: int = 50
    multi_objective: bool = True  # 使用NSGA-II
    timeout_seconds: int = 600  # 10分钟超时


@dataclass
class Chromosome:
    """染色体 - 代表一个调度方案"""
    genes: Dict[str, Optional[TimeSlot]]  # activity_id -> TimeSlot
    fitness: float = 0.0
    objectives: Dict[str, float] = field(default_factory=dict)
    rank: int = 0  # NSGA-II非支配排序等级
    crowding_distance: float = 0.0

    def copy(self) -> 'Chromosome':
        return Chromosome(
            genes=deepcopy(self.genes),
            fitness=self.fitness,
            objectives=deepcopy(self.objectives),
            rank=self.rank,
            crowding_distance=self.crowding_distance
        )


class GAScheduler:
    """
    遗传算法资源调度器

    基于NSGA-II算法实现多目标优化

    使用示例:
        config = GeneticAlgorithmConfig(
            population_size=100,
            generations=200,
            multi_objective=True
        )
        scheduler = GAScheduler(venues, staff, budget, config)
        result = scheduler.schedule(activities, horizon_start, horizon_end)
    """

    def __init__(
        self,
        venues: List[str],
        available_staff: List[str],
        total_budget: float,
        config: Optional[GeneticAlgorithmConfig] = None
    ):
        """
        初始化GA调度器

        Args:
            venues: 可用场地列表
            available_staff: 可用人员列表
            total_budget: 总预算
            config: GA配置
        """
        self.venues = venues
        self.available_staff = available_staff
        self.total_budget = total_budget
        self.config = config or GeneticAlgorithmConfig()

        self.activities: List[Activity] = []
        self.horizon_start: Optional[datetime] = None
        self.horizon_end: Optional[datetime] = None
        self.population: List[Chromosome] = []
        self.best_chromosome: Optional[Chromosome] = None
        self.generation_stats: List[Dict] = []

    def schedule(
        self,
        activities: List[Activity],
        planning_horizon_start: datetime,
        planning_horizon_end: datetime
    ) -> Dict:
        """
        执行遗传算法调度

        Args:
            activities: 待调度活动列表
            planning_horizon_start: 规划开始时间
            planning_horizon_end: 规划结束时间

        Returns:
            调度结果
        """
        self.activities = activities
        self.horizon_start = planning_horizon_start
        self.horizon_end = planning_horizon_end

        # 处理空活动列表
        if not activities:
            return {
                "scheduled": [],
                "unscheduled": [],
                "metrics": {
                    "scheduled_count": 0,
                    "unscheduled_count": 0,
                    "scheduled_ratio": 0.0,
                    "fitness": 0.0,
                    "objectives": {},
                    "generations": 0,
                    "final_best_fitness": 0.0
                },
                "evolution_history": []
            }

        start_time = datetime.now()

        # 1. 初始化种群
        self._initialize_population()

        # 2. 进化
        no_improvement_count = 0
        best_fitness_history = []

        for generation in range(self.config.generations):
            # 检查超时
            elapsed = (datetime.now() - start_time).total_seconds()
            if elapsed > self.config.timeout_seconds:
                print(f"GA timeout after {generation} generations")
                break

            # 评估种群
            self._evaluate_population()

            # 记录统计信息
            fitness_values = [c.fitness for c in self.population]
            best_fitness = max(fitness_values)
            avg_fitness = np.mean(fitness_values)

            best_fitness_history.append(best_fitness)

            self.generation_stats.append({
                'generation': generation,
                'best_fitness': best_fitness,
                'avg_fitness': avg_fitness,
                'diversity': np.std(fitness_values)
            })

            # 早停检查
            if generation > 0 and best_fitness <= best_fitness_history[-2]:
                no_improvement_count += 1
            else:
                no_improvement_count = 0
                self.best_chromosome = max(self.population, key=lambda c: c.fitness).copy()

            if no_improvement_count >= self.config.early_stopping_generations:
                print(f"Early stopping at generation {generation}")
                break

            # 生成下一代
            if self.config.multi_objective:
                self._nsga2_evolve()
            else:
                self._simple_ga_evolve()

        # 3. 返回最优解
        if self.best_chromosome is None:
            self._evaluate_population()
            self.best_chromosome = max(self.population, key=lambda c: c.fitness)

        return self._create_result()

    def _initialize_population(self):
        """初始化种群"""
        self.population = []

        for _ in range(self.config.population_size):
            chromosome = self._create_random_chromosome()
            self.population.append(chromosome)

    def _create_random_chromosome(self) -> Chromosome:
        """创建随机染色体"""
        genes = {}

        # 按优先级排序活动
        sorted_activities = sorted(
            self.activities,
            key=lambda a: (a.priority.value, -a.expected_participants),
            reverse=True
        )

        # 随机分配时间槽
        for activity in sorted_activities:
            if random.random() < 0.8:  # 80%概率尝试分配
                slot = self._generate_random_slot(activity)
                if slot and self._is_valid_assignment(genes, activity.id, slot):
                    genes[activity.id] = slot
                else:
                    genes[activity.id] = None
            else:
                genes[activity.id] = None

        return Chromosome(genes=genes)

    def _generate_random_slot(self, activity: Activity) -> Optional[TimeSlot]:
        """为活动生成随机时间槽"""
        if not activity.preferred_time_ranges:
            return None

        # 随机选择偏好时间段
        pref_start, pref_end = random.choice(activity.preferred_time_ranges)
        start = max(pref_start, self.horizon_start)
        end = min(pref_end, self.horizon_end)

        if start + timedelta(hours=activity.duration_hours) > end:
            return None

        # 随机选择开始时间
        max_offset = int((end - start - timedelta(hours=activity.duration_hours)).total_seconds() / 3600)
        if max_offset <= 0:
            return None

        offset_hours = random.randint(0, max_offset)
        slot_start = start + timedelta(hours=offset_hours)
        slot_end = slot_start + timedelta(hours=activity.duration_hours)

        # 随机选择场地
        venue = random.choice(activity.acceptable_venues)

        return TimeSlot(venue, slot_start, slot_end)

    def _is_valid_assignment(
        self,
        genes: Dict[str, Optional[TimeSlot]],
        activity_id: str,
        new_slot: TimeSlot
    ) -> bool:
        """检查时间槽分配是否有效（无冲突）"""
        for aid, slot in genes.items():
            if aid != activity_id and slot is not None:
                # 检查时间和场地冲突
                if (slot.venue_id == new_slot.venue_id and
                    not (slot.end_time <= new_slot.start_time or
                         slot.start_time >= new_slot.end_time)):
                    return False
        return True

    def _evaluate_population(self):
        """评估种群适应度"""
        for chromosome in self.population:
            self._evaluate_chromosome(chromosome)

    def _evaluate_chromosome(self, chromosome: Chromosome):
        """评估单个染色体"""
        objectives = self._calculate_objectives(chromosome)
        chromosome.objectives = objectives

        # 单目标：加权求和
        weights = {'scheduled': 0.4, 'no_conflict': 0.3, 'budget_balance': 0.2, 'preference': 0.1}
        chromosome.fitness = sum(objectives.get(k, 0) * w for k, w in weights.items())

    def _calculate_objectives(self, chromosome: Chromosome) -> Dict[str, float]:
        """计算多目标值"""
        objectives = {}

        # 目标1: 已调度活动比例
        scheduled_count = sum(1 for slot in chromosome.genes.values() if slot is not None)
        objectives['scheduled'] = scheduled_count / len(self.activities)

        # 目标2: 无冲突度（检测冲突数量）
        conflicts = self._count_conflicts(chromosome)
        objectives['no_conflict'] = 1.0 / (1 + conflicts)

        # 目标3: 预算均衡度
        budget_balance = self._evaluate_budget_balance(chromosome)
        objectives['budget_balance'] = budget_balance

        # 目标4: 时间偏好满足度
        preference_score = self._evaluate_time_preference(chromosome)
        objectives['preference'] = preference_score

        # 目标5: 场地利用率均衡
        venue_balance = self._evaluate_venue_balance(chromosome)
        objectives['venue_balance'] = venue_balance

        return objectives

    def _count_conflicts(self, chromosome: Chromosome) -> int:
        """计算冲突数量"""
        conflicts = 0
        scheduled = [(aid, slot) for aid, slot in chromosome.genes.items() if slot is not None]

        for i, (aid1, slot1) in enumerate(scheduled):
            for aid2, slot2 in scheduled[i+1:]:
                if slot1.venue_id == slot2.venue_id:
                    if not (slot1.end_time <= slot2.start_time or
                            slot1.start_time >= slot2.end_time):
                        conflicts += 1

        return conflicts

    def _evaluate_budget_balance(self, chromosome: Chromosome) -> float:
        """评估预算分配均衡度"""
        scheduled = [aid for aid, slot in chromosome.genes.items() if slot is not None]
        if not scheduled:
            return 0.0

        # 计算已分配预算
        total_allocated = sum(
            self._get_activity_by_id(aid).min_budget
            for aid in scheduled
        )

        if total_allocated > self.total_budget:
            return 0.0

        # 预算利用率
        utilization = total_allocated / self.total_budget

        # 优先级满足度
        priority_score = sum(
            self._get_activity_by_id(aid).priority.value
            for aid in scheduled
        ) / (len(scheduled) * 4)  # 4是最高优先级

        return (utilization + priority_score) / 2

    def _evaluate_time_preference(self, chromosome: Chromosome) -> float:
        """评估时间偏好满足度"""
        scores = []
        for aid, slot in chromosome.genes.items():
            if slot is None:
                continue

            activity = self._get_activity_by_id(aid)
            # 检查是否在偏好时间段内
            for pref_start, pref_end in activity.preferred_time_ranges:
                if pref_start <= slot.start_time and slot.end_time <= pref_end:
                    scores.append(1.0)
                    break
            else:
                scores.append(0.0)

        return np.mean(scores) if scores else 0.0

    def _evaluate_venue_balance(self, chromosome: Chromosome) -> float:
        """评估场地使用均衡度"""
        venue_usage = {v: 0 for v in self.venues}

        for slot in chromosome.genes.values():
            if slot:
                venue_usage[slot.venue_id] += 1

        if not venue_usage:
            return 0.0

        # 计算使用率的变异系数
        usages = list(venue_usage.values())
        mean_usage = np.mean(usages)
        if mean_usage == 0:
            return 1.0

        cv = np.std(usages) / mean_usage
        return 1.0 / (1 + cv)

    def _get_activity_by_id(self, activity_id: str) -> Activity:
        """根据ID获取活动"""
        for activity in self.activities:
            if activity.id == activity_id:
                return activity
        raise ValueError(f"Activity not found: {activity_id}")

    def _simple_ga_evolve(self):
        """简单遗传算法进化"""
        new_population = []

        # 精英保留
        sorted_pop = sorted(self.population, key=lambda c: c.fitness, reverse=True)
        new_population.extend([c.copy() for c in sorted_pop[:self.config.elite_size]])

        # 生成新个体
        while len(new_population) < self.config.population_size:
            parent1 = self._tournament_selection()
            parent2 = self._tournament_selection()

            if random.random() < self.config.crossover_rate:
                child1, child2 = self._crossover(parent1, parent2)
            else:
                child1, child2 = parent1.copy(), parent2.copy()

            child1 = self._mutate(child1)
            child2 = self._mutate(child2)

            new_population.extend([child1, child2])

        self.population = new_population[:self.config.population_size]

    def _nsga2_evolve(self):
        """NSGA-II进化"""
        # 非支配排序
        fronts = self._non_dominated_sort()

        # 计算拥挤度
        for front in fronts:
            self._calculate_crowding_distance(front)

        # 选择
        new_population = []
        front_idx = 0

        while len(new_population) + len(fronts[front_idx]) <= self.config.population_size:
            new_population.extend([c.copy() for c in fronts[front_idx]])
            front_idx += 1
            if front_idx >= len(fronts):
                break

        # 如果还需要更多个体，按拥挤度选择
        if len(new_population) < self.config.population_size and front_idx < len(fronts):
            last_front = fronts[front_idx]
            last_front.sort(key=lambda c: c.crowding_distance, reverse=True)
            remaining = self.config.population_size - len(new_population)
            new_population.extend([c.copy() for c in last_front[:remaining]])

        # 交叉和变异
        offspring = []
        while len(offspring) < self.config.population_size:
            parent1 = self._tournament_selection_nsga2(new_population)
            parent2 = self._tournament_selection_nsga2(new_population)

            if random.random() < self.config.crossover_rate:
                child1, child2 = self._crossover(parent1, parent2)
            else:
                child1, child2 = parent1.copy(), parent2.copy()

            child1 = self._mutate(child1)
            child2 = self._mutate(child2)

            offspring.extend([child1, child2])

        self.population = offspring[:self.config.population_size]

    def _non_dominated_sort(self) -> List[List[Chromosome]]:
        """非支配排序"""
        fronts = [[]]

        for p in self.population:
            p.dominated_set = []
            p.domination_count = 0

            for q in self.population:
                if p is q:
                    continue

                if self._dominates(p, q):
                    p.dominated_set.append(q)
                elif self._dominates(q, p):
                    p.domination_count += 1

            if p.domination_count == 0:
                p.rank = 0
                fronts[0].append(p)

        i = 0
        while len(fronts[i]) > 0:
            next_front = []
            for p in fronts[i]:
                for q in p.dominated_set:
                    q.domination_count -= 1
                    if q.domination_count == 0:
                        q.rank = i + 1
                        next_front.append(q)
            i += 1
            fronts.append(next_front)

        return fronts[:-1]  # 移除最后一个空前沿

    def _dominates(self, p: Chromosome, q: Chromosome) -> bool:
        """判断p是否支配q"""
        better_in_one = False

        for obj_name in p.objectives:
            p_val = p.objectives.get(obj_name, 0)
            q_val = q.objectives.get(obj_name, 0)

            if p_val < q_val:
                return False
            elif p_val > q_val:
                better_in_one = True

        return better_in_one

    def _calculate_crowding_distance(self, front: List[Chromosome]):
        """计算拥挤距离"""
        if len(front) <= 2:
            for c in front:
                c.crowding_distance = float('inf')
            return

        for c in front:
            c.crowding_distance = 0

        objectives = list(front[0].objectives.keys())

        for obj_name in objectives:
            front.sort(key=lambda c: c.objectives.get(obj_name, 0))

            front[0].crowding_distance = float('inf')
            front[-1].crowding_distance = float('inf')

            obj_min = front[0].objectives[obj_name]
            obj_max = front[-1].objectives[obj_name]

            if obj_max - obj_min == 0:
                continue

            for i in range(1, len(front) - 1):
                distance = (front[i + 1].objectives[obj_name] -
                           front[i - 1].objectives[obj_name])
                front[i].crowding_distance += distance / (obj_max - obj_min)

    def _tournament_selection(self) -> Chromosome:
        """锦标赛选择"""
        tournament = random.sample(self.population, min(self.config.tournament_size, len(self.population)))
        return max(tournament, key=lambda c: c.fitness)

    def _tournament_selection_nsga2(self, population: List[Chromosome]) -> Chromosome:
        """NSGA-II锦标赛选择"""
        tournament = random.sample(population, min(self.config.tournament_size, len(population)))
        tournament.sort(key=lambda c: (c.rank, -c.crowding_distance))
        return tournament[0]

    def _crossover(self, parent1: Chromosome, parent2: Chromosome) -> Tuple[Chromosome, Chromosome]:
        """交叉操作（均匀交叉）"""
        child1_genes = {}
        child2_genes = {}

        activity_ids = list(parent1.genes.keys())

        for aid in activity_ids:
            if random.random() < 0.5:
                child1_genes[aid] = deepcopy(parent1.genes[aid])
                child2_genes[aid] = deepcopy(parent2.genes[aid])
            else:
                child1_genes[aid] = deepcopy(parent2.genes[aid])
                child2_genes[aid] = deepcopy(parent1.genes[aid])

        child1 = Chromosome(genes=child1_genes)
        child2 = Chromosome(genes=child2_genes)

        return child1, child2

    def _mutate(self, chromosome: Chromosome) -> Chromosome:
        """变异操作"""
        mutated_genes = deepcopy(chromosome.genes)

        for aid in mutated_genes:
            if random.random() < self.config.mutation_rate:
                activity = self._get_activity_by_id(aid)

                # 随机决定：改变时间、改变场地、或取消安排
                mutation_type = random.choice(['time', 'venue', 'unschedule', 'schedule'])

                if mutation_type == 'unschedule':
                    mutated_genes[aid] = None
                elif mutation_type == 'schedule' and mutated_genes[aid] is None:
                    new_slot = self._generate_random_slot(activity)
                    if new_slot and self._is_valid_assignment(mutated_genes, aid, new_slot):
                        mutated_genes[aid] = new_slot
                elif mutated_genes[aid] is not None:
                    if mutation_type == 'time':
                        new_slot = self._generate_random_slot(activity)
                        if new_slot and self._is_valid_assignment(mutated_genes, aid, new_slot):
                            mutated_genes[aid] = new_slot
                    elif mutation_type == 'venue':
                        current_slot = mutated_genes[aid]
                        new_venue = random.choice(activity.acceptable_venues)
                        new_slot = TimeSlot(new_venue, current_slot.start_time, current_slot.end_time)
                        if self._is_valid_assignment(mutated_genes, aid, new_slot):
                            mutated_genes[aid] = new_slot

        return Chromosome(genes=mutated_genes)

    def _create_result(self) -> Dict:
        """创建调度结果"""
        if self.best_chromosome is None:
            return {"error": "No solution found"}

        scheduled = []
        unscheduled = []

        for aid, slot in self.best_chromosome.genes.items():
            activity = self._get_activity_by_id(aid)
            if slot:
                activity.assigned_slot = slot
                scheduled.append(activity)
            else:
                unscheduled.append(activity)

        # 分配资源
        self._allocate_resources(scheduled)

        return {
            "scheduled": scheduled,
            "unscheduled": unscheduled,
            "metrics": {
                "scheduled_count": len(scheduled),
                "unscheduled_count": len(unscheduled),
                "scheduled_ratio": len(scheduled) / len(self.activities),
                "fitness": self.best_chromosome.fitness,
                "objectives": self.best_chromosome.objectives,
                "generations": len(self.generation_stats),
                "final_best_fitness": self.generation_stats[-1]['best_fitness'] if self.generation_stats else 0
            },
            "evolution_history": self.generation_stats
        }

    def _allocate_resources(self, scheduled: List[Activity]):
        """分配预算和人员"""
        total_min = sum(a.min_budget for a in scheduled)
        remaining = self.total_budget - total_min

        if remaining > 0:
            priority_weights = {ActivityPriority.CRITICAL: 4, ActivityPriority.HIGH: 3,
                               ActivityPriority.MEDIUM: 2, ActivityPriority.LOW: 1}
            total_weight = sum(priority_weights[a.priority] * a.expected_participants for a in scheduled)

            for activity in scheduled:
                weight = priority_weights[activity.priority] * activity.expected_participants
                extra = remaining * (weight / total_weight) if total_weight > 0 else 0
                activity.assigned_budget = min(activity.min_budget + extra, activity.max_budget)
        else:
            for activity in scheduled:
                activity.assigned_budget = activity.min_budget

        staff_idx = 0
        for activity in scheduled:
            n_staff = activity.required_staff_count
            activity.assigned_staff = [
                self.available_staff[(staff_idx + i) % len(self.available_staff)]
                for i in range(n_staff)
            ]
            staff_idx += n_staff

    def compare_with_hierarchical(
        self,
        hierarchical_result: Dict
    ) -> Dict:
        """
        与分层调度器结果进行对比

        Args:
            hierarchical_result: 分层调度器的结果

        Returns:
            对比分析结果
        """
        ga_result = self._create_result()

        ga_scheduled = len(ga_result.get("scheduled", []))
        hier_scheduled = len(hierarchical_result.get("scheduled", []))

        comparison = {
            "scheduled_activities": {
                "ga": ga_scheduled,
                "hierarchical": hier_scheduled,
                "difference": ga_scheduled - hier_scheduled,
                "improvement_pct": ((ga_scheduled - hier_scheduled) / hier_scheduled * 100)
                                    if hier_scheduled > 0 else 0
            },
            "fitness_scores": {
                "ga_best": self.best_chromosome.fitness if self.best_chromosome else 0,
            },
            "computational_cost": {
                "ga_generations": len(self.generation_stats),
                "ga_population_size": self.config.population_size
            },
            "recommendation": ""
        }

        if comparison["scheduled_activities"]["improvement_pct"] > 5:
            comparison["recommendation"] = "GA found significantly better solution, but at higher computational cost"
        elif comparison["scheduled_activities"]["improvement_pct"] < -5:
            comparison["recommendation"] = "Hierarchical scheduler performed better, likely due to problem structure"
        else:
            comparison["recommendation"] = "Both methods perform similarly; hierarchical is preferred for speed"

        return comparison
