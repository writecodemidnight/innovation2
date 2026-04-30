package com.campusclub.activity.domain.entity;

import com.campusclub.common.model.BaseEntity;
import jakarta.persistence.*;
import lombok.*;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Entity
@Table(name = "activities")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Activity extends BaseEntity {

    @Column(name = "title", nullable = false, length = 200)
    private String title;

    @Column(name = "description", columnDefinition = "TEXT")
    private String description;

    @Enumerated(EnumType.STRING)
    @Column(name = "activity_type", nullable = false, length = 50)
    private ActivityType activityType;

    @Enumerated(EnumType.STRING)
    @Column(name = "status", nullable = false, length = 20)
    private ActivityStatus status = ActivityStatus.PLANNING;

    @Column(name = "start_time", nullable = false)
    private LocalDateTime startTime;

    @Column(name = "end_time", nullable = false)
    private LocalDateTime endTime;

    @Column(name = "location", length = 200)
    private String location;

    @Column(name = "capacity")
    private Integer capacity;

    @Column(name = "current_participants")
    @Builder.Default
    private Integer currentParticipants = 0;

    @Version
    @Column(name = "version")
    @Builder.Default
    private Long version = 0L;

    @Column(name = "club_id")
    private Long clubId;

    @Column(name = "created_by")
    private Long createdBy;

    @Column(name = "cover_image_url", length = 500)
    private String coverImageUrl;

    @Column(name = "budget", precision = 10, scale = 2)
    private BigDecimal budget;

    @Column(name = "required_resources", columnDefinition = "jsonb")
    @JdbcTypeCode(SqlTypes.JSON)
    private String requiredResources;

    @Column(name = "registration_deadline")
    private LocalDateTime registrationDeadline;

    @Enumerated(EnumType.STRING)
    @Column(name = "approval_status", nullable = false, length = 20)
    private ApprovalStatus approvalStatus = ApprovalStatus.NONE;

    @Column(name = "approval_comment", columnDefinition = "TEXT")
    private String approvalComment;

    /**
     * Submit activity for approval: PLANNING -> PENDING_APPROVAL
     */
    public void submitForApproval() {
        if (this.status != ActivityStatus.PLANNING) {
            throw new IllegalStateException("Only PLANNING activities can be submitted for approval. Current status: " + this.status);
        }
        this.status = ActivityStatus.PENDING_APPROVAL;
        this.approvalStatus = ApprovalStatus.PENDING;
    }

    /**
     * Approve activity: PENDING_APPROVAL -> REGISTERING
     * 审批通过后直接进入报名状态，让学生可以立即报名
     */
    public void approve() {
        if (this.status != ActivityStatus.PENDING_APPROVAL) {
            throw new IllegalStateException("Only PENDING_APPROVAL activities can be approved. Current status: " + this.status);
        }
        this.status = ActivityStatus.REGISTERING;
        this.approvalStatus = ApprovalStatus.APPROVED;
    }

    /**
     * Reject activity: PENDING_APPROVAL -> REJECTED
     */
    public void reject(String comment) {
        if (this.status != ActivityStatus.PENDING_APPROVAL) {
            throw new IllegalStateException("Only PENDING_APPROVAL activities can be rejected. Current status: " + this.status);
        }
        this.status = ActivityStatus.REJECTED;
        this.approvalStatus = ApprovalStatus.REJECTED;
        this.approvalComment = comment;
    }

    /**
     * Start registration: APPROVED -> REGISTERING
     */
    public void startRegistration() {
        if (this.status != ActivityStatus.APPROVED) {
            throw new IllegalStateException("Only APPROVED activities can start registration. Current status: " + this.status);
        }
        this.status = ActivityStatus.REGISTERING;
    }

    /**
     * Start activity: REGISTERING -> ONGOING
     */
    public void startActivity() {
        if (this.status != ActivityStatus.REGISTERING) {
            throw new IllegalStateException("Only REGISTERING activities can be started. Current status: " + this.status);
        }
        this.status = ActivityStatus.ONGOING;
    }

    /**
     * Complete activity: ONGOING -> COMPLETED
     */
    public void complete() {
        if (this.status != ActivityStatus.ONGOING) {
            throw new IllegalStateException("Only ONGOING activities can be completed. Current status: " + this.status);
        }
        this.status = ActivityStatus.COMPLETED;
    }

    /**
     * Cancel activity: Any state (except COMPLETED/CANCELLED) -> CANCELLED
     */
    public void cancel() {
        if (this.status == ActivityStatus.COMPLETED || this.status == ActivityStatus.CANCELLED) {
            throw new IllegalStateException("Cannot cancel activity in " + this.status + " status");
        }
        this.status = ActivityStatus.CANCELLED;
    }

    /**
     * Check if users can register for this activity
     */
    public boolean canRegister() {
        if (this.status != ActivityStatus.REGISTERING) {
            return false;
        }
        if (this.capacity != null && this.currentParticipants != null) {
            return this.currentParticipants < this.capacity;
        }
        return true;
    }

    public enum ActivityType {
        LECTURE, WORKSHOP, COMPETITION, SOCIAL, VOLUNTEER, SPORTS, ENTERTAINMENT
    }

    public enum ActivityStatus {
        PLANNING, PENDING_APPROVAL, APPROVED, REJECTED, REGISTERING, ONGOING, COMPLETED, CANCELLED
    }

    public enum ApprovalStatus {
        NONE, PENDING, APPROVED, REJECTED
    }
}
