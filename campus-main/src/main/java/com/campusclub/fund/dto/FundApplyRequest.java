package com.campusclub.fund.dto;

import jakarta.validation.constraints.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;

/**
 * 资金申请请求DTO
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class FundApplyRequest {

    @NotNull(message = "活动ID不能为空")
    private Long activityId;

    @NotNull(message = "申请金额不能为空")
    @DecimalMin(value = "0.01", message = "申请金额必须大于0")
    @DecimalMax(value = "100000", message = "申请金额不能超过10万元")
    private BigDecimal amount;

    @NotBlank(message = "用途说明不能为空")
    @Size(max = 1000, message = "用途说明不能超过1000字")
    private String purpose;

    @Size(max = 2000, message = "预算明细不能超过2000字")
    private String budgetBreakdown;
}
