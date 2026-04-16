package com.campusclub.evaluation.dto;

import lombok.Builder;
import lombok.Data;

import java.time.LocalDateTime;
import java.util.Map;

/**
 * 活动评估响应
 */
@Data
@Builder
public class EvaluationResponse {

    private Long activityId;                    // 活动ID
    private String activityTitle;               // 活动标题

    private Double totalScore;                  // 加权总分
    private FiveDimensionScores dimensionScores; // 各维度原始得分
    private Map<String, Double> weights;        // 各维度权重
    private Map<String, Double> contributions;  // 各维度贡献度得分

    private Double consistencyRatio;            // 一致性比率
    private Boolean consistencyCheckPassed;     // 一致性检验是否通过

    private String evaluatedBy;                 // 评估人
    private LocalDateTime evaluatedAt;          // 评估时间
}
