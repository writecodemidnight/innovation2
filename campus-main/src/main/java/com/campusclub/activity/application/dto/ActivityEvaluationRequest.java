package com.campusclub.activity.application.dto;

import jakarta.validation.constraints.NotNull;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.util.Map;

/**
 * 活动效果评估请求DTO
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ActivityEvaluationRequest {

    @NotNull(message = "活动ID不能为空")
    private Long activityId;

    // 五维评估指标
    private BigDecimal engagementScore;      // 参与度得分 (0-100)
    private BigDecimal educationalScore;     // 教育性得分 (0-100)
    private BigDecimal innovationScore;      // 创新性得分 (0-100)
    private BigDecimal impactScore;          // 影响力得分 (0-100)
    private BigDecimal sustainabilityScore;  // 可持续性得分 (0-100)

    // 额外数据（用于算法分析）
    private Map<String, Object> extraData;
}
