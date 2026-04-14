package com.campusclub.user.application.dto;

import jakarta.validation.constraints.NotBlank;

public record WechatLoginRequest(
    @NotBlank String code,
    String userInfo
) {}
