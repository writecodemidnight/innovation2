"""
NLP情感分析模块（桥梁接口）

进阶挑战功能：处理学生的文本反馈，提取情感倾向

当前状态：基础桥梁实现，预留深度学习扩展接口
未来扩展：可接入BERT/RoBERTa等预训练模型
"""

import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json


class SentimentLevel(Enum):
    """情感等级"""
    VERY_NEGATIVE = "非常负面"  # 0.0-0.2
    NEGATIVE = "负面"          # 0.2-0.4
    NEUTRAL = "中性"           # 0.4-0.6
    POSITIVE = "正面"          # 0.6-0.8
    VERY_POSITIVE = "非常正面"  # 0.8-1.0


@dataclass
class SentimentResult:
    """情感分析结果"""
    text: str
    sentiment_score: float  # 0-1, 越接近1越正面
    sentiment_level: str
    confidence: float
    keywords: List[str]
    aspect_sentiments: Dict[str, float]  # 各方面情感（组织、内容、体验等）


class NLPSentimentAnalyzer:
    """
    NLP情感分析器（桥梁实现）

    当前实现：基于规则的基础分析
    未来扩展：接入深度学习模型（BERT/RoBERTa）

    使用方式:
        analyzer = NLPSentimentAnalyzer()
        result = analyzer.analyze("活动组织得很好，学到了很多！")
    """

    # 正面/负面词典（基础规则）
    POSITIVE_WORDS = {
        "好", "棒", "优秀", "精彩", "有趣", "有用", "收获", "满意",
        "喜欢", "开心", "愉快", "充实", "有意义", "组织得好", "内容丰富",
        "学到很多", "受益匪浅", "期待下次", "推荐", "赞", "完美"
    }

    NEGATIVE_WORDS = {
        "差", "糟糕", "无聊", "没用", "失望", "不满意", "浪费时间",
        "混乱", "无聊", "枯燥", "不好", "讨厌", "后悔", "差评",
        "组织混乱", "内容空洞", "没意思", "没收获"
    }

    # 方面词（用于细粒度分析）
    ASPECT_KEYWORDS = {
        "organization": ["组织", "安排", "流程", "时间", "地点", "通知"],
        "content": ["内容", "主题", "知识", "干货", "深度", "广度"],
        "experience": ["体验", "氛围", "互动", "参与感", "收获"],
        "speaker": ["讲师", "嘉宾", "主持人", "分享者", "水平"]
    }

    def __init__(self, use_deep_learning: bool = False):
        """
        初始化分析器

        Args:
            use_deep_learning: 是否使用深度学习模型（当前预留，未来实现）
        """
        self.use_deep_learning = use_deep_learning
        self._model = None

        if use_deep_learning:
            # TODO: 未来接入BERT等预训练模型
            self._load_deep_learning_model()

    def _load_deep_learning_model(self):
        """加载深度学习模型（预留接口）"""
        # try:
        #     from transformers import AutoTokenizer, AutoModelForSequenceClassification
        #     self._tokenizer = AutoTokenizer.from_pretrained("bert-base-chinese")
        #     self._model = AutoModelForSequenceClassification.from_pretrained(
        #         "bert-base-chinese", num_labels=5
        #     )
        # except ImportError:
        #     print("Transformers not available, falling back to rule-based")
        pass

    def analyze(self, text: str) -> SentimentResult:
        """
        分析文本情感

        Args:
            text: 输入文本（学生反馈）

        Returns:
            情感分析结果
        """
        if not text or not text.strip():
            return SentimentResult(
                text=text,
                sentiment_score=0.5,
                sentiment_level=SentimentLevel.NEUTRAL.value,
                confidence=0.0,
                keywords=[],
                aspect_sentiments={}
            )

        if self.use_deep_learning and self._model is not None:
            # TODO: 实现深度学习推理
            return self._analyze_with_dl(text)
        else:
            return self._analyze_with_rules(text)

    def _analyze_with_rules(self, text: str) -> SentimentResult:
        """基于规则的情感分析"""
        text_lower = text.lower()

        # 1. 基础情感计算
        pos_count = sum(1 for word in self.POSITIVE_WORDS if word in text_lower)
        neg_count = sum(1 for word in self.NEGATIVE_WORDS if word in text_lower)

        total = pos_count + neg_count
        if total == 0:
            sentiment_score = 0.5  # 中性
            confidence = 0.3
        else:
            sentiment_score = pos_count / total
            # 词越多，置信度越高（简化假设）
            confidence = min(0.9, 0.5 + total * 0.05)

        # 2. 提取关键词
        keywords = []
        for word in self.POSITIVE_WORDS | self.NEGATIVE_WORDS:
            if word in text_lower:
                keywords.append(word)

        # 3. 各方面情感分析
        aspect_sentiments = self._analyze_aspects(text)

        # 4. 确定情感等级
        level = self._score_to_level(sentiment_score)

        return SentimentResult(
            text=text,
            sentiment_score=round(sentiment_score, 3),
            sentiment_level=level.value,
            confidence=round(confidence, 3),
            keywords=keywords[:5],  # 最多5个关键词
            aspect_sentiments={k: round(v, 3) for k, v in aspect_sentiments.items()}
        )

    def _analyze_with_dl(self, text: str) -> SentimentResult:
        """基于深度学习的情感分析（预留）"""
        # TODO: 实现BERT等模型推理
        # 当前回退到规则方法
        return self._analyze_with_rules(text)

    def _analyze_aspects(self, text: str) -> Dict[str, float]:
        """各方面情感分析"""
        aspect_sentiments = {}
        text_lower = text.lower()

        for aspect, keywords in self.ASPECT_KEYWORDS.items():
            # 检查文本中是否提到该方面
            mentioned = any(kw in text_lower for kw in keywords)
            if mentioned:
                # 计算该方面的情感（简化版）
                pos = sum(1 for w in self.POSITIVE_WORDS if w in text_lower)
                neg = sum(1 for w in self.NEGATIVE_WORDS if w in text_lower)
                if pos + neg > 0:
                    aspect_sentiments[aspect] = pos / (pos + neg)
                else:
                    aspect_sentiments[aspect] = 0.5

        return aspect_sentiments

    def _score_to_level(self, score: float) -> SentimentLevel:
        """分数转等级"""
        if score < 0.2:
            return SentimentLevel.VERY_NEGATIVE
        elif score < 0.4:
            return SentimentLevel.NEGATIVE
        elif score < 0.6:
            return SentimentLevel.NEUTRAL
        elif score < 0.8:
            return SentimentLevel.POSITIVE
        else:
            return SentimentLevel.VERY_POSITIVE

    def analyze_batch(self, texts: List[str]) -> List[SentimentResult]:
        """批量分析"""
        return [self.analyze(text) for text in texts]

    def analyze_activity_feedback(self, activity_id: str,
                                   feedbacks: List[Dict]) -> Dict:
        """
        分析活动的所有反馈

        Args:
            activity_id: 活动ID
            feedbacks: 反馈列表，每个包含text和student_id

        Returns:
            综合分析结果
        """
        results = []
        for feedback in feedbacks:
            text = feedback.get("text", "")
            result = self.analyze(text)
            results.append({
                "student_id": feedback.get("student_id"),
                "result": result
            })

        if not results:
            return {
                "activity_id": activity_id,
                "total_feedback": 0,
                "average_sentiment": 0.5,
                "sentiment_distribution": {},
                "key_aspects": {}
            }

        # 统计
        scores = [r["result"].sentiment_score for r in results]
        avg_sentiment = sum(scores) / len(scores)

        # 情感分布
        distribution = {}
        for r in results:
            level = r["result"].sentiment_level
            distribution[level] = distribution.get(level, 0) + 1

        # 收集各方面评价
        aspect_scores = {}
        for r in results:
            for aspect, score in r["result"].aspect_sentiments.items():
                if aspect not in aspect_scores:
                    aspect_scores[aspect] = []
                aspect_scores[aspect].append(score)

        key_aspects = {
            aspect: round(sum(scores) / len(scores), 3)
            for aspect, scores in aspect_scores.items()
        }

        return {
            "activity_id": activity_id,
            "total_feedback": len(results),
            "average_sentiment": round(avg_sentiment, 3),
            "sentiment_distribution": distribution,
            "key_aspects": key_aspects,
            "details": results
        }

    def get_improvement_suggestions(self, analysis_result: Dict) -> List[str]:
        """
        基于NLP分析生成改进建议

        Args:
            analysis_result: analyze_activity_feedback的结果

        Returns:
            改进建议列表
        """
        suggestions = []

        avg_sentiment = analysis_result.get("average_sentiment", 0.5)
        aspects = analysis_result.get("key_aspects", {})

        # 整体情感偏低
        if avg_sentiment < 0.4:
            suggestions.append("活动整体满意度较低，建议全面审查活动组织和内容质量")

        # 某方面评分低
        for aspect, score in aspects.items():
            if score < 0.4:
                aspect_names = {
                    "organization": "活动组织",
                    "content": "内容质量",
                    "experience": "参与体验",
                    "speaker": "讲师水平"
                }
                name = aspect_names.get(aspect, aspect)
                suggestions.append(f"{name}方面评价较低，需要重点改进")

        return suggestions


# ==================== 扩展接口（未来实现） ====================

class DeepLearningSentimentAnalyzer(NLPSentimentAnalyzer):
    """
    深度学习情感分析器（未来扩展）

    可接入的模型：
    - BERT/RoBERTa: 通用情感分类
    - Senta: 百度情感分析
    - 自研模型: 针对校园活动场景微调
    """

    def __init__(self, model_path: Optional[str] = None):
        super().__init__(use_deep_learning=True)
        self.model_path = model_path
        self._load_model()

    def _load_model(self):
        """加载预训练模型"""
        # TODO: 实现模型加载
        # if self.model_path:
        #     self._model = load_model(self.model_path)
        pass

    def fine_tune(self, training_data: List[Tuple[str, float]]):
        """
        在特定领域数据上微调

        Args:
            training_data: [(text, sentiment_score), ...]
        """
        # TODO: 实现微调逻辑
        pass
