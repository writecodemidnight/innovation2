package com.campusclub.fund.dto;

import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * 资金审批请求DTO
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class FundReviewRequest {

    @NotNull(message = "审批决定不能为空")
    private Boolean approved;

    @Size(max = 1000, message = "审批意见不能超过1000字")
    private String comment;
}
