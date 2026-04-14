package com.campusclub.user.application.service;

import com.campusclub.user.application.dto.*;
import com.campusclub.user.application.mapper.UserMapper;
import com.campusclub.user.domain.entity.User;
import com.campusclub.user.domain.repository.UserRepository;
import com.campusclub.user.infrastructure.external.WechatMpClient;
import com.campusclub.user.infrastructure.external.WechatSessionResponse;
import com.campusclub.common.util.JwtUtil;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Slf4j
@Service
@RequiredArgsConstructor
public class AuthApplicationService {

    private final UserRepository userRepository;
    private final WechatMpClient wechatMpClient;
    private final UserMapper userMapper;
    private final JwtUtil jwtUtil;

    @Transactional
    public LoginResponse wechatLogin(WechatLoginRequest request) {
        WechatSessionResponse session = wechatMpClient.code2Session(request.code());
        String openid = session.getOpenid();

        User user = userRepository.findByOpenid(openid)
                .orElseGet(() -> createNewUser(openid));

        String accessToken = jwtUtil.generateAccessToken(user.getId(), user.getRole().name());
        String refreshToken = jwtUtil.generateRefreshToken(user.getId());

        log.info("User logged in: {}, role: {}", user.getId(), user.getRole());

        return new LoginResponse(
                accessToken,
                refreshToken,
                jwtUtil.getAccessTokenExpiration(),
                userMapper.toDto(user)
        );
    }

    private User createNewUser(String openid) {
        User user = User.builder()
                .openid(openid)
                .username("wx_" + openid.substring(0, 8))
                .nickname("微信用户")
                .role(User.UserRole.STUDENT)
                .status(User.UserStatus.ACTIVE)
                .build();
        return userRepository.save(user);
    }

    public LoginResponse refreshToken(String refreshToken) {
        if (!jwtUtil.validateToken(refreshToken)) {
            throw new RuntimeException("无效的刷新令牌");
        }

        Long userId = jwtUtil.getUserIdFromToken(refreshToken);
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new RuntimeException("用户不存在"));

        String newAccessToken = jwtUtil.generateAccessToken(user.getId(), user.getRole().name());
        String newRefreshToken = jwtUtil.generateRefreshToken(user.getId());

        return new LoginResponse(
                newAccessToken,
                newRefreshToken,
                jwtUtil.getAccessTokenExpiration(),
                userMapper.toDto(user)
        );
    }
}
