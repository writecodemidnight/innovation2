package com.campusclub.feedback.service.nlp;

import lombok.Builder;
import lombok.Data;

import java.util.List;
import java.util.Map;

/**
 * 活动反馈综合分析结果
 */
@Data
@Builder
public class ActivityFeedbackAnalysis {

    /**
     * 活动ID
     */
    private Long activityId;

    /**
     * 反馈总数
     */
    private int totalFeedback;

    /**
     * 平均情感得分
     */
    private double averageSentiment;

    /**
     * 情感分布统计
     */
    private Map<String, Integer> sentimentDistribution;

    /**
     * 关键方面评分
     */
    private Map<String, Float> keyAspects;

    /**
     * 改进建议
     */
    private List<String> suggestions;
}
