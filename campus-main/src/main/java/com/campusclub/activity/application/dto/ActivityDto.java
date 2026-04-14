package com.campusclub.activity.application.dto;

import com.campusclub.activity.domain.entity.Activity;

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
    LocalDateTime createdAt
) {}
