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
    private Long totalCount;
    private List<RatingDistributionItem> ratingDistribution;

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
