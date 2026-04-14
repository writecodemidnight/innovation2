package com.campusclub.user.application.dto;

import com.campusclub.user.domain.entity.User;

import java.time.LocalDateTime;

public record UserDto(
    Long id,
    String studentId,
    String username,
    String nickname,
    String avatarUrl,
    String phone,
    String email,
    User.UserRole role,
    User.UserStatus status,
    LocalDateTime createdAt
) {}
