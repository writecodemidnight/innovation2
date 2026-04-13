"""
Apriori关联规则挖掘算法

用于发现校园活动与资源消耗之间的关联规则

应用场景:
- 发现活动类型与场地需求的关联
- 发现活动规模与预算消耗的关联
- 发现活动时段与物资需求的关联
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Set, FrozenSet, Optional
from dataclasses import dataclass
from collections import defaultdict
from itertools import combinations
import json


@dataclass
class AssociationRule:
    """关联规则"""
    antecedent: FrozenSet[str]  # 前件
    consequent: FrozenSet[str]  # 后件
    support: float              # 支持度
    confidence: float           # 置信度
    lift: float                 # 提升度
    conviction: float           # 确信度

    def __repr__(self) -> str:
        antecedent_str = ", ".join(sorted(self.antecedent))
        consequent_str = ", ".join(sorted(self.consequent))
        return (f"{antecedent_str} => {consequent_str} "
                f"(support={self.support:.3f}, confidence={self.confidence:.3f}, lift={self.lift:.3f})")


@dataclass
class FrequentItemset:
    """频繁项集"""
    items: FrozenSet[str]
    support: float
    count: int


class AprioriMiner:
    """
    Apriori关联规则挖掘器

    核心思想：
    1. 频繁项集的所有子集也必须是频繁的
    2. 如果一个项集不频繁，其超集也不频繁

    算法步骤：
    1. 找出所有频繁1-项集
    2. 通过连接生成候选k-项集
    3. 剪枝：移除包含非频繁子集的候选
    4. 扫描数据库计算支持度
    5. 重复直到无法生成更多频繁项集
    6. 从频繁项集生成关联规则

    示例:
        miner = AprioriMiner(min_support=0.1, min_confidence=0.5)
        transactions = [
            ["体育", "大场地", "高预算"],
            ["文艺", "小场地", "中预算"],
            ...
        ]
        rules = miner.fit(transactions).get_rules()
    """

    def __init__(
        self,
        min_support: float = 0.1,
        min_confidence: float = 0.5,
        min_lift: float = 1.0,
        max_itemset_size: int = 4
    ):
        """
        初始化Apriori挖掘器

        Args:
            min_support: 最小支持度 (0-1)
            min_confidence: 最小置信度 (0-1)
            min_lift: 最小提升度 (>=1)
            max_itemset_size: 最大项集大小
        """
        self.min_support = min_support
        self.min_confidence = min_confidence
        self.min_lift = min_lift
        self.max_itemset_size = max_itemset_size

        self.transactions: List[List[str]] = []
        self.n_transactions: int = 0
        self.frequent_itemsets: Dict[int, List[FrequentItemset]] = {}
        self.rules: List[AssociationRule] = []
        self.item_counts: Dict[str, int] = defaultdict(int)

    def fit(self, transactions: List[List[str]]) -> 'AprioriMiner':
        """
        执行Apriori算法挖掘关联规则

        Args:
            transactions: 交易列表，每个交易是项的列表

        Returns:
            self
        """
        self.transactions = transactions
        self.n_transactions = len(transactions)

        if self.n_transactions == 0:
            return self

        # 统计单项出现次数
        self._count_single_items()

        # 找出频繁1-项集
        L1 = self._get_frequent_1_itemsets()
        self.frequent_itemsets[1] = L1

        # 迭代生成更大项集
        k = 2
        while k <= self.max_itemset_size and (k - 1) in self.frequent_itemsets:
            # 生成候选k-项集
            candidates = self._generate_candidates(k)

            if not candidates:
                break

            # 计算支持度
            frequent_k = self._get_frequent_itemsets(candidates, k)

            if frequent_k:
                self.frequent_itemsets[k] = frequent_k
                k += 1
            else:
                break

        # 生成关联规则
        self._generate_rules()

        return self

    def _count_single_items(self):
        """统计单项出现次数"""
        for transaction in self.transactions:
            for item in set(transaction):
                self.item_counts[item] += 1

    def _get_frequent_1_itemsets(self) -> List[FrequentItemset]:
        """找出频繁1-项集"""
        frequent = []
        for item, count in self.item_counts.items():
            support = count / self.n_transactions
            if support >= self.min_support:
                frequent.append(FrequentItemset(
                    items=frozenset([item]),
                    support=support,
                    count=count
                ))
        return frequent

    def _generate_candidates(self, k: int) -> Set[FrozenSet[str]]:
        """
        生成候选k-项集

        通过连接L_{k-1} × L_{k-1}生成候选
        """
        if k - 1 not in self.frequent_itemsets:
            return set()

        prev_itemsets = [fi.items for fi in self.frequent_itemsets[k - 1]]
        candidates = set()

        # 连接步骤
        for i in range(len(prev_itemsets)):
            for j in range(i + 1, len(prev_itemsets)):
                itemset1 = list(prev_itemsets[i])
                itemset2 = list(prev_itemsets[j])

                # 排序后比较前k-2个元素
                itemset1.sort()
                itemset2.sort()

                if itemset1[:-1] == itemset2[:-1]:
                    # 合并两个项集
                    candidate = frozenset(prev_itemsets[i] | prev_itemsets[j])
                    if len(candidate) == k:
                        candidates.add(candidate)

        # 剪枝步骤：移除包含非频繁子集的候选
        pruned_candidates = set()
        for candidate in candidates:
            if self._has_frequent_subsets(candidate, k):
                pruned_candidates.add(candidate)

        return pruned_candidates

    def _has_frequent_subsets(self, candidate: FrozenSet[str], k: int) -> bool:
        """检查候选的所有(k-1)子集是否都频繁"""
        for subset in combinations(candidate, k - 1):
            subset_frozen = frozenset(subset)
            if not any(fi.items == subset_frozen for fi in self.frequent_itemsets.get(k - 1, [])):
                return False
        return True

    def _get_frequent_itemsets(
        self,
        candidates: Set[FrozenSet[str]],
        k: int
    ) -> List[FrequentItemset]:
        """计算候选项集的支持度，返回频繁项集"""
        candidate_counts = defaultdict(int)

        # 扫描数据库
        for transaction in self.transactions:
            transaction_set = set(transaction)
            for candidate in candidates:
                if candidate.issubset(transaction_set):
                    candidate_counts[candidate] += 1

        # 筛选频繁项集
        frequent = []
        for candidate, count in candidate_counts.items():
            support = count / self.n_transactions
            if support >= self.min_support:
                frequent.append(FrequentItemset(
                    items=candidate,
                    support=support,
                    count=count
                ))

        return frequent

    def _generate_rules(self):
        """从频繁项集生成关联规则"""
        self.rules = []

        # 从大小>=2的频繁项集生成规则
        for k in range(2, self.max_itemset_size + 1):
            if k not in self.frequent_itemsets:
                continue

            for itemset in self.frequent_itemsets[k]:
                # 生成所有可能的非空真子集作为前件
                items = list(itemset.items)
                for r in range(1, len(items)):
                    for antecedent in combinations(items, r):
                        antecedent_set = frozenset(antecedent)
                        consequent_set = itemset.items - antecedent_set

                        rule = self._create_rule(
                            antecedent_set,
                            consequent_set,
                            itemset.support
                        )

                        if rule and rule.confidence >= self.min_confidence and rule.lift >= self.min_lift:
                            self.rules.append(rule)

        # 按置信度排序
        self.rules.sort(key=lambda x: x.confidence, reverse=True)

    def _create_rule(
        self,
        antecedent: FrozenSet[str],
        consequent: FrozenSet[str],
        itemset_support: float
    ) -> Optional[AssociationRule]:
        """创建关联规则"""
        # 查找前件的支持度
        antecedent_support = self._get_itemset_support(antecedent)
        if antecedent_support == 0:
            return None

        # 计算指标
        confidence = itemset_support / antecedent_support
        lift = confidence / self._get_itemset_support(consequent) if self._get_itemset_support(consequent) > 0 else 0

        # 计算确信度
        consequent_support = self._get_itemset_support(consequent)
        if consequent_support < 1.0:
            conviction = (1 - consequent_support) / (1 - confidence) if confidence < 1 else float('inf')
        else:
            conviction = float('inf')

        return AssociationRule(
            antecedent=antecedent,
            consequent=consequent,
            support=itemset_support,
            confidence=confidence,
            lift=lift,
            conviction=conviction
        )

    def _get_itemset_support(self, itemset: FrozenSet[str]) -> float:
        """获取项集的支持度"""
        k = len(itemset)
        if k == 1:
            item = list(itemset)[0]
            return self.item_counts.get(item, 0) / self.n_transactions

        if k in self.frequent_itemsets:
            for fi in self.frequent_itemsets[k]:
                if fi.items == itemset:
                    return fi.support

        # 重新计算
        count = 0
        for transaction in self.transactions:
            if itemset.issubset(set(transaction)):
                count += 1

        return count / self.n_transactions

    def get_rules(
        self,
        sort_by: str = "confidence",
        top_n: Optional[int] = None
    ) -> List[AssociationRule]:
        """
        获取关联规则

        Args:
            sort_by: 排序依据 ("confidence", "support", "lift")
            top_n: 返回前N条规则

        Returns:
            关联规则列表
        """
        sorted_rules = sorted(
            self.rules,
            key=lambda x: getattr(x, sort_by),
            reverse=True
        )

        if top_n:
            return sorted_rules[:top_n]
        return sorted_rules

    def get_rules_by_consequent(
        self,
        consequent_item: str
    ) -> List[AssociationRule]:
        """获取指定后件的关联规则"""
        return [
            rule for rule in self.rules
            if consequent_item in rule.consequent
        ]

    def get_rules_by_antecedent(
        self,
        antecedent_item: str
    ) -> List[AssociationRule]:
        """获取指定前件的关联规则"""
        return [
            rule for rule in self.rules
            if antecedent_item in rule.antecedent
        ]

    def analyze_activity_resource_patterns(self) -> Dict:
        """
        分析活动-资源消耗模式

        返回分析结果摘要
        """
        # 按活动类型分组规则
        activity_rules = defaultdict(list)
        resource_rules = defaultdict(list)

        for rule in self.rules:
            for item in rule.antecedent:
                if "活动" in item or any(t in item for t in ["体育", "文艺", "学术", "志愿", "社团"]):
                    activity_rules[item].append(rule)
                elif any(r in item for r in ["场地", "预算", "物资", "人力"]):
                    resource_rules[item].append(rule)

        # 统计信息
        stats = {
            "total_rules": len(self.rules),
            "total_frequent_itemsets": sum(len(itemsets) for itemsets in self.frequent_itemsets.values()),
            "max_itemset_size": max(self.frequent_itemsets.keys()) if self.frequent_itemsets else 0,
            "avg_confidence": np.mean([r.confidence for r in self.rules]) if self.rules else 0,
            "avg_lift": np.mean([r.lift for r in self.rules]) if self.rules else 0,
            "activity_types": list(activity_rules.keys()),
            "resource_types": list(resource_rules.keys()),
            "top_rules": self.get_rules(sort_by="lift", top_n=10)
        }

        return stats

    def recommend_resources(self, activity_features: List[str]) -> List[Dict]:
        """
        基于活动特征推荐资源

        Args:
            activity_features: 活动特征列表

        Returns:
            推荐资源列表
        """
        activity_set = set(activity_features)
        recommendations = []

        for rule in self.rules:
            if rule.antecedent.issubset(activity_set):
                # 计算推荐分数
                score = rule.confidence * rule.lift

                for resource in rule.consequent:
                    recommendations.append({
                        "resource": resource,
                        "confidence": rule.confidence,
                        "lift": rule.lift,
                        "support": rule.support,
                        "score": score,
                        "based_on": list(rule.antecedent)
                    })

        # 去重并排序
        seen = set()
        unique_recommendations = []
        for rec in sorted(recommendations, key=lambda x: x["score"], reverse=True):
            if rec["resource"] not in seen:
                seen.add(rec["resource"])
                unique_recommendations.append(rec)

        return unique_recommendations

    def export_rules(self, filepath: str):
        """导出规则到JSON文件"""
        rules_data = [
            {
                "antecedent": list(rule.antecedent),
                "consequent": list(rule.consequent),
                "support": rule.support,
                "confidence": rule.confidence,
                "lift": rule.lift,
                "conviction": rule.conviction
            }
            for rule in self.rules
        ]

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(rules_data, f, ensure_ascii=False, indent=2)

    @classmethod
    def create_sample_transactions(cls, n: int = 1000) -> List[List[str]]:
        """
        创建示例交易数据

        用于测试和演示
        """
        np.random.seed(42)

        activity_types = ["体育活动", "文艺表演", "学术讲座", "志愿服务", "社团招新"]
        venue_sizes = ["大场地", "中场地", "小场地"]
        budget_levels = ["高预算", "中预算", "低预算"]
        time_slots = ["上午", "下午", "晚上"]
        seasons = ["春季", "夏季", "秋季", "冬季"]

        # 定义一些关联模式
        patterns = [
            (["体育活动", "大场地", "高预算"], 0.7),
            (["文艺表演", "中场地", "中预算"], 0.6),
            (["学术讲座", "小场地", "低预算"], 0.8),
            (["志愿服务", "下午", "低预算"], 0.5),
            (["社团招新", "秋季", "中场地"], 0.6),
        ]

        transactions = []
        for _ in range(n):
            # 随机选择活动类型
            activity = np.random.choice(activity_types)
            transaction = [activity]

            # 根据模式添加相关项
            for pattern, prob in patterns:
                if activity in pattern and np.random.random() < prob:
                    for item in pattern:
                        if item != activity and np.random.random() < 0.8:
                            transaction.append(item)

            # 随机添加其他项
            if np.random.random() < 0.3:
                transaction.append(np.random.choice(time_slots))
            if np.random.random() < 0.2:
                transaction.append(np.random.choice(seasons))

            transactions.append(list(set(transaction)))

        return transactions


def analyze_activity_resource_association(
    activity_data: pd.DataFrame,
    min_support: float = 0.05,
    min_confidence: float = 0.5
) -> Dict:
    """
    分析活动-资源关联的便捷函数

    Args:
        activity_data: 活动数据DataFrame
        min_support: 最小支持度
        min_confidence: 最小置信度

    Returns:
        分析结果
    """
    # 转换为交易格式
    transactions = []
    for _, row in activity_data.iterrows():
        transaction = []
        for col, value in row.items():
            if pd.notna(value):
                transaction.append(f"{col}={value}")
        transactions.append(transaction)

    # 运行Apriori
    miner = AprioriMiner(
        min_support=min_support,
        min_confidence=min_confidence
    )
    miner.fit(transactions)

    return {
        "rules": miner.get_rules(top_n=20),
        "stats": miner.analyze_activity_resource_patterns(),
        "miner": miner
    }
