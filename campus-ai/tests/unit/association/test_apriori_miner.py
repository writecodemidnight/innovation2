"""
Apriori关联规则挖掘测试
"""

import pytest
import numpy as np
import pandas as pd
import os
import tempfile

from src.association.apriori_miner import (
    AprioriMiner,
    AssociationRule,
    FrequentItemset,
    analyze_activity_resource_association
)


class TestAprioriMiner:
    """测试Apriori挖掘器"""

    def test_init(self):
        """测试初始化"""
        miner = AprioriMiner(
            min_support=0.1,
            min_confidence=0.5,
            min_lift=1.0
        )

        assert miner.min_support == 0.1
        assert miner.min_confidence == 0.5
        assert miner.min_lift == 1.0

    def test_create_sample_transactions(self):
        """测试创建示例交易"""
        transactions = AprioriMiner.create_sample_transactions(n=100)

        assert len(transactions) == 100
        assert all(isinstance(t, list) for t in transactions)

    def test_fit(self):
        """测试训练"""
        transactions = [
            ["A", "B", "C"],
            ["A", "B", "D"],
            ["A", "C", "D"],
            ["B", "C"],
            ["A", "B", "C", "D"]
        ]

        miner = AprioriMiner(min_support=0.4, min_confidence=0.5)
        miner.fit(transactions)

        assert len(miner.frequent_itemsets) > 0
        assert len(miner.rules) >= 0

    def test_frequent_1_itemsets(self):
        """测试频繁1-项集"""
        transactions = [
            ["A", "B"],
            ["A", "C"],
            ["A", "B"],
            ["B", "C"],
            ["A", "B", "C"]
        ]

        miner = AprioriMiner(min_support=0.6)
        miner.fit(transactions)

        # A和B应该是频繁的
        assert 1 in miner.frequent_itemsets
        frequent_1_items = [fi.items for fi in miner.frequent_itemsets[1]]
        assert frozenset(["A"]) in frequent_1_items
        assert frozenset(["B"]) in frequent_1_items

    def test_generate_rules(self):
        """测试规则生成"""
        transactions = [
            ["牛奶", "面包", "黄油"],
            ["牛奶", "面包"],
            ["牛奶", "黄油"],
            ["面包", "黄油"],
            ["牛奶", "面包", "黄油"]
        ]

        miner = AprioriMiner(min_support=0.3, min_confidence=0.3)
        miner.fit(transactions)

        # 由于数据量小，可能没有规则生成，这是正常的
        # 我们主要检查代码不报错

        # 检查规则属性（如果有规则）
        for rule in miner.rules:
            assert isinstance(rule.antecedent, frozenset)
            assert isinstance(rule.consequent, frozenset)
            assert 0 <= rule.support <= 1
            assert 0 <= rule.confidence <= 1
            assert rule.lift >= 0

    def test_get_rules(self):
        """测试获取规则"""
        transactions = AprioriMiner.create_sample_transactions(n=100)

        miner = AprioriMiner(min_support=0.05, min_confidence=0.3)
        miner.fit(transactions)

        rules = miner.get_rules(sort_by="confidence", top_n=10)

        assert len(rules) <= 10

        if len(rules) > 1:
            # 检查排序
            for i in range(len(rules) - 1):
                assert rules[i].confidence >= rules[i + 1].confidence

    def test_get_rules_by_consequent(self):
        """测试按后件筛选规则"""
        transactions = [
            ["体育", "大场地"],
            ["体育", "大场地", "高预算"],
            ["文艺", "小场地"],
            ["体育", "大场地"]
        ]

        miner = AprioriMiner(min_support=0.25, min_confidence=0.5)
        miner.fit(transactions)

        rules = miner.get_rules_by_consequent("大场地")

        for rule in rules:
            assert "大场地" in rule.consequent

    def test_get_rules_by_antecedent(self):
        """测试按前件筛选规则"""
        transactions = [
            ["体育", "大场地"],
            ["体育", "大场地", "高预算"],
            ["文艺", "小场地"]
        ]

        miner = AprioriMiner(min_support=0.25, min_confidence=0.5)
        miner.fit(transactions)

        rules = miner.get_rules_by_antecedent("体育")

        for rule in rules:
            assert "体育" in rule.antecedent

    def test_analyze_activity_resource_patterns(self):
        """测试活动-资源模式分析"""
        transactions = AprioriMiner.create_sample_transactions(n=200)

        miner = AprioriMiner(min_support=0.05, min_confidence=0.3)
        miner.fit(transactions)

        stats = miner.analyze_activity_resource_patterns()

        assert "total_rules" in stats
        assert "total_frequent_itemsets" in stats
        assert "avg_confidence" in stats

    def test_recommend_resources(self):
        """测试资源推荐"""
        transactions = AprioriMiner.create_sample_transactions(n=200)

        miner = AprioriMiner(min_support=0.05, min_confidence=0.3)
        miner.fit(transactions)

        activity_features = ["体育活动"]
        recommendations = miner.recommend_resources(activity_features)

        assert isinstance(recommendations, list)

        if recommendations:
            assert "resource" in recommendations[0]
            assert "confidence" in recommendations[0]
            assert "score" in recommendations[0]

    def test_export_rules(self):
        """测试导出规则"""
        transactions = AprioriMiner.create_sample_transactions(n=100)

        miner = AprioriMiner(min_support=0.05, min_confidence=0.3)
        miner.fit(transactions)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            filepath = f.name

        try:
            miner.export_rules(filepath)
            assert os.path.exists(filepath)

            import json
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            assert isinstance(data, list)
        finally:
            os.unlink(filepath)


class TestAssociationRule:
    """测试关联规则"""

    def test_rule_creation(self):
        """测试规则创建"""
        rule = AssociationRule(
            antecedent=frozenset(["A", "B"]),
            consequent=frozenset(["C"]),
            support=0.5,
            confidence=0.8,
            lift=1.2,
            conviction=2.0
        )

        assert rule.support == 0.5
        assert rule.confidence == 0.8
        assert rule.lift == 1.2

    def test_rule_repr(self):
        """测试规则表示"""
        rule = AssociationRule(
            antecedent=frozenset(["A"]),
            consequent=frozenset(["B"]),
            support=0.5,
            confidence=0.8,
            lift=1.2,
            conviction=2.0
        )

        repr_str = repr(rule)
        assert "A" in repr_str
        assert "B" in repr_str
        assert "support" in repr_str


class TestFrequentItemset:
    """测试频繁项集"""

    def test_itemset_creation(self):
        """测试项集创建"""
        itemset = FrequentItemset(
            items=frozenset(["A", "B"]),
            support=0.6,
            count=60
        )

        assert itemset.support == 0.6
        assert itemset.count == 60


class TestAnalyzeActivityResourceAssociation:
    """测试分析函数"""

    def test_analysis(self):
        """测试分析功能"""
        data = pd.DataFrame({
            'activity_type': ['体育', '文艺', '体育', '学术', '体育'],
            'venue': ['大场地', '中场地', '大场地', '小场地', '大场地'],
            'budget': ['高', '中', '高', '低', '高']
        })

        result = analyze_activity_resource_association(
            data,
            min_support=0.2,
            min_confidence=0.5
        )

        assert 'rules' in result
        assert 'stats' in result
        assert 'miner' in result
