package com.campusclub.user.application.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

/**
 * 社团注册请求
 * 注册新社团时，同时创建社长账号
 */
public record ClubRegistrationRequest(
    @NotBlank(message = "社团名称不能为空")
    @Size(max = 100, message = "社团名称最多100个字符")
    String clubName,

    @NotBlank(message = "社长账号不能为空")
    @Size(min = 4, max = 50, message = "社长账号长度应为4-50个字符")
    String presidentUsername,

    @NotBlank(message = "社长密码不能为空")
    @Size(min = 6, max = 100, message = "社长密码长度至少6个字符")
    String presidentPassword,

    String description,
    String category,
    String facultyAdvisor
) {}
