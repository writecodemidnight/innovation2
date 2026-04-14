package com.campusclub.activity.application.dto;

import com.campusclub.activity.domain.entity.ActivityParticipant;

import java.time.LocalDateTime;

public record ActivityParticipantDto(
    Long id,
    Long activityId,
    Long userId,
    String username,
    String nickname,
    String avatarUrl,
    ActivityParticipant.ParticipationStatus status,
    LocalDateTime registeredAt,
    LocalDateTime checkedInAt
) {}
