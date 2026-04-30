package com.campusclub.feedback.service.nlp;

import lombok.Builder;
import lombok.Data;

import java.util.List;

/**
 * 批量情感分析结果
 */
@Data
@Builder
public class BatchSentimentResult {

    /**
     * 平均情感得分
     */
    private double averageScore;

    /**
     * 正面评价数量
     */
    private int positiveCount;

    /**
     * 负面评价数量
     */
    private int negativeCount;

    /**
     * 中性评价数量
     */
    private int neutralCount;

    /**
     * 详细结果列表
     */
    private List<SentimentResult> results;
}
