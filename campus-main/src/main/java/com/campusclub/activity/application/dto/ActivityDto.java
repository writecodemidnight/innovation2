package com.campusclub.activity.application.dto;

import com.campusclub.activity.domain.entity.Activity;
import com.fasterxml.jackson.annotation.JsonProperty;

import java.math.BigDecimal;
import java.time.LocalDateTime;

public record ActivityDto(
    Long id,
    String title,
    String description,
    Activity.ActivityType activityType,
    Activity.ActivityStatus status,
    LocalDateTime startTime,
    LocalDateTime endTime,
    String location,
    Integer capacity,
    Integer currentParticipants,
    Long clubId,
    String clubName,
    Long createdBy,
    String coverImageUrl,
    BigDecimal budget,
    Activity.ApprovalStatus approvalStatus,
    LocalDateTime registrationDeadline,
    LocalDateTime createdAt
) {
    /**
     * 兼容性别名，前端使用 maxParticipants
     */
    @JsonProperty("maxParticipants")
    public Integer maxParticipants() {
        return capacity;
    }
}
