package com.campusclub.activity.application.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.util.Map;

/**
 * 活动效果评估响应DTO
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ActivityEvaluationResponse {

    private Long activityId;
    private String activityTitle;

    // 总分
    private BigDecimal totalScore;

    // 各维度得分
    private BigDecimal engagementScore;
    private BigDecimal educationalScore;
    private BigDecimal innovationScore;
    private BigDecimal impactScore;
    private BigDecimal sustainabilityScore;

    // 权重配置
    private Map<String, BigDecimal> weights;

    // 贡献度（加权后的得分）
    private Map<String, BigDecimal> contributions;

    // 一致性检验
    private Boolean consistencyCheckPassed;
    private Double consistencyRatio;

    // 评估等级
    private String evaluationLevel;

    // 改进建议
    private String suggestions;

    // 处理时间
    private Long processingTimeMs;
}
