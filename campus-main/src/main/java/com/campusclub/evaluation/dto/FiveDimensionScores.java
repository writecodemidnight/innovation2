package com.campusclub.evaluation.dto;

import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotNull;
import lombok.Builder;
import lombok.Data;

/**
 * 五维评估得分
 */
@Data
@Builder
public class FiveDimensionScores {

    @NotNull(message = "参与度得分不能为空")
    @Min(value = 0, message = "得分最小为0")
    @Max(value = 100, message = "得分最大为100")
    private Double engagement;      // 参与度

    @NotNull(message = "教育性得分不能为空")
    @Min(value = 0, message = "得分最小为0")
    @Max(value = 100, message = "得分最大为100")
    private Double educational;     // 教育性

    @NotNull(message = "创新性得分不能为空")
    @Min(value = 0, message = "得分最小为0")
    @Max(value = 100, message = "得分最大为100")
    private Double innovation;      // 创新性

    @NotNull(message = "影响力得分不能为空")
    @Min(value = 0, message = "得分最小为0")
    @Max(value = 100, message = "得分最大为100")
    private Double impact;          // 影响力

    @NotNull(message = "可持续性得分不能为空")
    @Min(value = 0, message = "得分最小为0")
    @Max(value = 100, message = "得分最大为100")
    private Double sustainability;  // 可持续性
}
