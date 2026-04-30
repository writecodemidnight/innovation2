package com.campusclub.feedback.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;
import java.util.List;

/**
 * 反馈评价DTO
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class FeedbackDTO {

    private Long id;
    private Long activityId;
    private String activityTitle;
    private Long userId;
    private String username;
    private String avatar;
    private Integer rating;
    private Integer organizationRating;
    private Integer contentRating;
    private String content;
    private List<String> images;

    // NLP情感分析结果
    private Double sentimentScore;
    private String sentimentLevel;
    private List<String> keywords;

    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
}
