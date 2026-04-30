package com.campusclub.feedback.service.nlp;

import lombok.Builder;
import lombok.Data;

import java.util.List;
import java.util.Map;

/**
 * 情感分析结果
 */
@Data
@Builder
public class SentimentResult {

    /**
     * 原始文本
     */
    private String text;

    /**
     * 情感得分 0-1，越接近1越正面
     */
    private double sentimentScore;

    /**
     * 情感等级: 非常正面/正面/中性/负面/非常负面
     */
    private String sentimentLevel;

    /**
     * 置信度
     */
    private double confidence;

    /**
     * 提取的关键词
     */
    private List<String> keywords;

    /**
     * 各方面情感分析
     */
    private Map<String, Double> aspectSentiments;
}
