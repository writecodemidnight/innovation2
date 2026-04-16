package com.campusclub.resource.domain.entity;

import com.campusclub.common.model.BaseEntity;
import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDateTime;

/**
 * 资源预约实体（对应resource_reservations表）
 */
@Entity
@Table(name = "resource_reservations")
@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ResourceBooking extends BaseEntity {

    @Column(name = "resource_id", nullable = false)
    private Long resourceId;

    @Column(name = "activity_id")
    private Long activityId;

    @Column(name = "applicant_id", nullable = false)
    private Long applicantId;

    @Column(name = "start_time", nullable = false)
    private LocalDateTime startTime;

    @Column(name = "end_time", nullable = false)
    private LocalDateTime endTime;

    @Column
    @Builder.Default
    private Integer quantity = 1;

    @Column(length = 20)
    @Builder.Default
    private String status = "PENDING";

    @Column
    private String purpose;

    @Column(name = "approval_comment")
    private String approvalComment;

    // 兼容字段
    @Transient
    private Long clubId;

    @Transient
    private Integer attendees;

    @Transient
    private String remark;

    @Transient
    private Long approvedBy;

    @Transient
    private LocalDateTime approvedAt;
}
