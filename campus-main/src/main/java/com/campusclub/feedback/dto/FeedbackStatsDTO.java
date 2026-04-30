package com.campusclub.feedback.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

/**
 * 反馈统计DTO
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class FeedbackStatsDTO {

    private Long activityId;
    private String activityTitle;
    private Double averageRating;
    private Double averageOrganizationRating;
    private Double averageContentRating;
    private Long totalCount;
    private List<RatingDistributionItem> ratingDistribution;

    // NLP情感分析统计
    private Double averageSentimentScore;
    private SentimentDistribution sentimentDistribution;
    private List<String> topKeywords;
    private List<String> suggestions;

    /**
     * 情感分布
     */
    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class SentimentDistribution {
        private Long positiveCount;
        private Long neutralCount;
        private Long negativeCount;
        private Double positivePercentage;
        private Double neutralPercentage;
        private Double negativePercentage;
    }

    /**
     * 评分分布项
     */
    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class RatingDistributionItem {
        private Integer stars;
        private Long count;
        private Double percentage;
    }
}
