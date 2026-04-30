package com.campusclub.user.interfaces.rest;

import com.campusclub.dto.ApiResponse;
import com.campusclub.user.application.dto.*;
import com.campusclub.user.application.service.AuthApplicationService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/v1/auth")
@RequiredArgsConstructor
@Tag(name = "认证", description = "用户认证相关接口")
public class AuthController {

    private final AuthApplicationService authService;

    @PostMapping("/login")
    @Operation(summary = "用户登录", description = "使用用户名和密码登录")
    public ResponseEntity<ApiResponse<LoginResponse>> login(
            @RequestBody @Valid LoginRequest request) {
        LoginResponse response = authService.login(request);
        return ResponseEntity.ok(ApiResponse.success(response));
    }

    @PostMapping("/wechat-login")
    @Operation(summary = "微信登录", description = "微信小程序登录，获取JWT Token")
    public ResponseEntity<ApiResponse<LoginResponse>> wechatLogin(
            @RequestBody @Valid WechatLoginRequest request) {
        LoginResponse response = authService.wechatLogin(request);
        return ResponseEntity.ok(ApiResponse.success(response));
    }

    @PostMapping("/refresh")
    @Operation(summary = "刷新Token", description = "使用刷新令牌获取新的访问令牌")
    public ResponseEntity<ApiResponse<LoginResponse>> refreshToken(
            @RequestHeader("X-Refresh-Token") String refreshToken) {
        LoginResponse response = authService.refreshToken(refreshToken);
        return ResponseEntity.ok(ApiResponse.success(response));
    }

    @PostMapping("/logout")
    @Operation(summary = "退出登录", description = "用户退出登录")
    public ResponseEntity<ApiResponse<Void>> logout() {
        return ResponseEntity.ok(ApiResponse.success(null));
    }

    @PostMapping("/register/club")
    @Operation(summary = "社团注册", description = "注册新社团，同时创建社长账号")
    public ResponseEntity<ApiResponse<LoginResponse>> registerClub(
            @RequestBody @Valid ClubRegistrationRequest request) {
        LoginResponse response = authService.registerClub(request);
        return ResponseEntity.ok(ApiResponse.success("社团注册成功", response));
    }

    @PostMapping("/register/student")
    @Operation(summary = "学生注册", description = "学生用户注册")
    public ResponseEntity<ApiResponse<LoginResponse>> registerStudent(
            @RequestBody @Valid StudentRegistrationRequest request) {
        LoginResponse response = authService.registerStudent(request);
        return ResponseEntity.ok(ApiResponse.success("注册成功", response));
    }
}
