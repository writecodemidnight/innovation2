package com.campusclub.user.interfaces.rest;

import com.campusclub.dto.ApiResponse;
import com.campusclub.user.application.dto.LoginResponse;
import com.campusclub.user.application.dto.WechatLoginRequest;
import com.campusclub.user.application.service.AuthApplicationService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1/auth")
@RequiredArgsConstructor
@Tag(name = "认证", description = "用户认证相关接口")
public class AuthController {

    private final AuthApplicationService authService;

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
}
