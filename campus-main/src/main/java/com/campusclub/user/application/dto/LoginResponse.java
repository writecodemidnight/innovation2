package com.campusclub.user.application.dto;

public record LoginResponse(
    String accessToken,
    String refreshToken,
    Long expiresIn,
    UserDto user
) {}
