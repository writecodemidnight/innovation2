package com.campusclub.user.application.dto;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.Size;

public record UserUpdateRequest(
    @Size(max = 50) String nickname,
    @Size(max = 500) String avatarUrl,
    @Size(max = 20) String phone,
    @Email @Size(max = 100) String email
) {}
