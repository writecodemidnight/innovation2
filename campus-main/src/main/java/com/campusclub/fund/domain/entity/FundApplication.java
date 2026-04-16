package com.campusclub.fund.domain.entity;

import com.campusclub.activity.domain.entity.Activity;
import com.campusclub.club.domain.entity.Club;
import com.campusclub.common.model.BaseEntity;
import com.campusclub.user.domain.entity.User;
import jakarta.persistence.*;
import lombok.*;

import java.math.BigDecimal;
import java.time.LocalDateTime;

/**
 * 资金申请表实体
 */
@Entity
@Table(name = "fund_applications")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class FundApplication extends BaseEntity {

    /**
     * 申请状态枚举
     */
    public enum FundStatus {
        PENDING,    // 待审批
        APPROVED,   // 已通过
        REJECTED,   // 已拒绝
        CANCELLED   // 已取消
    }

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "club_id", nullable = false)
    private Club club;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "activity_id")
    private Activity activity;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "applicant_id", nullable = false)
    private User applicant;

    @Column(name = "amount", nullable = false, precision = 10, scale = 2)
    private BigDecimal amount;

    @Column(name = "purpose", nullable = false, length = 1000)
    private String purpose;

    @Column(name = "budget_breakdown", columnDefinition = "TEXT")
    private String budgetBreakdown;  // JSON 格式存储预算明细

    @Enumerated(EnumType.STRING)
    @Column(name = "status", nullable = false, length = 20)
    @Builder.Default
    private FundStatus status = FundStatus.PENDING;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "reviewer_id")
    private User reviewer;

    @Column(name = "reviewer_comment", length = 1000)
    private String reviewerComment;

    @Column(name = "reviewed_at")
    private LocalDateTime reviewedAt;

    @Column(name = "cancelled_at")
    private LocalDateTime cancelledAt;

    @Column(name = "cancel_reason", length = 500)
    private String cancelReason;

    /**
     * 审批通过
     */
    public void approve(User reviewer, String comment) {
        this.status = FundStatus.APPROVED;
        this.reviewer = reviewer;
        this.reviewerComment = comment;
        this.reviewedAt = LocalDateTime.now();
    }

    /**
     * 审批拒绝
     */
    public void reject(User reviewer, String comment) {
        this.status = FundStatus.REJECTED;
        this.reviewer = reviewer;
        this.reviewerComment = comment;
        this.reviewedAt = LocalDateTime.now();
    }

    /**
     * 取消申请
     */
    public void cancel(String reason) {
        this.status = FundStatus.CANCELLED;
        this.cancelReason = reason;
        this.cancelledAt = LocalDateTime.now();
    }

    /**
     * 是否可以审批
     */
    public boolean canReview() {
        return this.status == FundStatus.PENDING;
    }

    /**
     * 是否可以取消
     */
    public boolean canCancel() {
        return this.status == FundStatus.PENDING;
    }
}
