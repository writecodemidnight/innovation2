package com.campusclub.fund.dto;

import com.campusclub.fund.domain.entity.FundApplication;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.time.LocalDateTime;

/**
 * 资金申请DTO
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class FundApplicationDTO {

    private Long id;
    private Long clubId;
    private String clubName;
    private Long activityId;
    private String activityTitle;
    private Long applicantId;
    private String applicantName;
    private BigDecimal amount;
    private String purpose;
    private String budgetBreakdown;
    private FundApplication.FundStatus status;
    private Long reviewerId;
    private String reviewerName;
    private String reviewerComment;
    private LocalDateTime reviewedAt;
    private LocalDateTime cancelledAt;
    private String cancelReason;
    private LocalDateTime createdAt;

    /**
     * 状态文本
     */
    public String getStatusText() {
        if (status == null) return "未知";
        return switch (status) {
            case PENDING -> "待审批";
            case APPROVED -> "已通过";
            case REJECTED -> "已拒绝";
            case CANCELLED -> "已取消";
        };
    }
}
