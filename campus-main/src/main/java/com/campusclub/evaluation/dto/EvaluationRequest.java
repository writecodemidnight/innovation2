package com.campusclub.evaluation.dto;

import jakarta.validation.constraints.NotNull;
import lombok.Builder;
import lombok.Data;

/**
 * 活动评估请求
 */
@Data
@Builder
public class EvaluationRequest {

    @NotNull(message = "活动ID不能为空")
    private Long activityId;

    @NotNull(message = "五维得分不能为空")
    private FiveDimensionScores scores;

    private String comment;  // 评估备注
}
