package com.campusclub.user.application.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

/**
 * 学生注册请求
 */
public record StudentRegistrationRequest(
    @NotBlank(message = "学号不能为空")
    @Size(max = 50, message = "学号最多50个字符")
    String studentId,

    @NotBlank(message = "用户名不能为空")
    @Size(min = 4, max = 50, message = "用户名长度应为4-50个字符")
    String username,

    @NotBlank(message = "密码不能为空")
    @Size(min = 6, max = 100, message = "密码长度至少6个字符")
    String password,

    @Size(max = 50, message = "昵称最多50个字符")
    String nickname,

    @Size(max = 20, message = "手机号格式不正确")
    String phone,

    @Size(max = 100, message = "邮箱最多100个字符")
    String email
) {}
