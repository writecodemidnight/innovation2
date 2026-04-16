package com.campusclub.resource.dto;

import lombok.Builder;
import lombok.Data;

import java.time.LocalDateTime;

@Data
@Builder
public class ResourceBookingDTO {
    private Long id;
    private Long resourceId;
    private String resourceName;
    private Long activityId;
    private String activityTitle;
    private Long clubId;
    private LocalDateTime startTime;
    private LocalDateTime endTime;
    private Integer attendees;
    private String status;
    private String statusLabel;
    private String remark;
    private LocalDateTime approvedAt;
    private String approvalRemark;
    private LocalDateTime createdAt;
}
