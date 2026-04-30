package com.campusclub.user.application.service;

import com.campusclub.club.domain.entity.Club;
import com.campusclub.club.domain.entity.ClubMember;
import com.campusclub.club.domain.repository.ClubMemberRepository;
import com.campusclub.club.domain.repository.ClubRepository;
import com.campusclub.common.exception.BusinessException;
import com.campusclub.common.util.JwtUtil;
import com.campusclub.user.application.dto.*;
import com.campusclub.user.application.mapper.UserMapper;
import com.campusclub.user.domain.entity.User;
import com.campusclub.user.domain.repository.UserRepository;
import com.campusclub.user.infrastructure.external.WechatMpClient;
import com.campusclub.user.infrastructure.external.WechatSessionResponse;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Slf4j
@Service
@RequiredArgsConstructor
public class AuthApplicationService {

    private final UserRepository userRepository;
    private final ClubRepository clubRepository;
    private final ClubMemberRepository clubMemberRepository;
    private final WechatMpClient wechatMpClient;
    private final UserMapper userMapper;
    private final JwtUtil jwtUtil;
    private final PasswordEncoder passwordEncoder;

    @Transactional
    public LoginResponse login(LoginRequest request) {
        User user = userRepository.findByUsername(request.username())
                .orElseThrow(() -> new BusinessException("用户名或密码错误"));

        log.debug("Login attempt: username={}, storedPassword={}", request.username(), user.getPassword());
        boolean matches = passwordEncoder.matches(request.password(), user.getPassword());
        log.debug("Password matches: {}", matches);

        if (!matches) {
            throw new BusinessException("用户名或密码错误");
        }

        if (user.getStatus() != User.UserStatus.ACTIVE) {
            throw new BusinessException("用户账号已被禁用");
        }

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
            throw new BusinessException("无效的刷新令牌");
        }

        Long userId = jwtUtil.getUserIdFromToken(refreshToken);
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new BusinessException("用户不存在"));

        String newAccessToken = jwtUtil.generateAccessToken(user.getId(), user.getRole().name());
        String newRefreshToken = jwtUtil.generateRefreshToken(user.getId());

        return new LoginResponse(
                newAccessToken,
                newRefreshToken,
                jwtUtil.getAccessTokenExpiration(),
                userMapper.toDto(user)
        );
    }

    /**
     * 注册新社团
     * 同时创建社长账号和社团
     */
    @Transactional
    public LoginResponse registerClub(ClubRegistrationRequest request) {
        // 检查用户名是否已存在
        if (userRepository.existsByUsername(request.presidentUsername())) {
            throw new BusinessException("该社长账号已被注册");
        }

        // 检查社团名称是否已存在（可选，根据业务需求）
        // 创建社长账号
        User president = User.builder()
                .username(request.presidentUsername())
                .password(passwordEncoder.encode(request.presidentPassword()))
                .nickname(request.presidentUsername())
                .role(User.UserRole.CLUB_PRESIDENT)
                .status(User.UserStatus.ACTIVE)
                .build();

        User savedPresident = userRepository.save(president);
        log.info("Created club president: {}", savedPresident.getId());

        // 创建社团
        Club club = Club.builder()
                .name(request.clubName())
                .code(generateClubCode(request.clubName()))
                .description(request.description())
                .category(parseCategory(request.category()))
                .presidentId(savedPresident.getId())
                .facultyAdvisor(request.facultyAdvisor())
                .status(Club.ClubStatus.ACTIVE)
                .memberCount(1)
                .build();

        Club savedClub = clubRepository.save(club);
        log.info("Created club: {} with president: {}", savedClub.getId(), savedPresident.getId());

        // 添加社长到 club_members 表，建立关联
        ClubMember clubMember = ClubMember.builder()
                .clubId(savedClub.getId())
                .userId(savedPresident.getId())
                .role(ClubMember.MemberRole.PRESIDENT)
                .build();
        clubMemberRepository.save(clubMember);
        log.info("Added president {} to club_members for club {}", savedPresident.getId(), savedClub.getId());

        // 生成Token并返回
        String accessToken = jwtUtil.generateAccessToken(savedPresident.getId(), savedPresident.getRole().name());
        String refreshToken = jwtUtil.generateRefreshToken(savedPresident.getId());

        return new LoginResponse(
                accessToken,
                refreshToken,
                jwtUtil.getAccessTokenExpiration(),
                userMapper.toDto(savedPresident)
        );
    }

    /**
     * 学生注册
     */
    @Transactional
    public LoginResponse registerStudent(StudentRegistrationRequest request) {
        // 检查学号是否已存在
        if (request.studentId() != null && userRepository.existsByStudentId(request.studentId())) {
            throw new BusinessException("该学号已被注册");
        }

        // 检查用户名是否已存在
        if (userRepository.existsByUsername(request.username())) {
            throw new BusinessException("该用户名已被注册");
        }

        // 创建学生账号
        User student = User.builder()
                .studentId(request.studentId())
                .username(request.username())
                .password(passwordEncoder.encode(request.password()))
                .nickname(request.nickname() != null ? request.nickname() : request.username())
                .phone(request.phone())
                .email(request.email())
                .role(User.UserRole.STUDENT)
                .status(User.UserStatus.ACTIVE)
                .build();

        User savedStudent = userRepository.save(student);
        log.info("Created student user: {}", savedStudent.getId());

        // 生成Token并返回
        String accessToken = jwtUtil.generateAccessToken(savedStudent.getId(), savedStudent.getRole().name());
        String refreshToken = jwtUtil.generateRefreshToken(savedStudent.getId());

        return new LoginResponse(
                accessToken,
                refreshToken,
                jwtUtil.getAccessTokenExpiration(),
                userMapper.toDto(savedStudent)
        );
    }

    private String generateClubCode(String clubName) {
        // 生成社团编码：社团名拼音首字母 + 时间戳
        String prefix = clubName.length() >= 2 ? clubName.substring(0, 2).toUpperCase() : clubName.toUpperCase();
        String timestamp = String.valueOf(System.currentTimeMillis()).substring(8);
        return prefix + timestamp;
    }

    private Club.ClubCategory parseCategory(String category) {
        if (category == null || category.isEmpty()) {
            return Club.ClubCategory.OTHER;
        }
        try {
            return Club.ClubCategory.valueOf(category.toUpperCase());
        } catch (IllegalArgumentException e) {
            return Club.ClubCategory.OTHER;
        }
    }
}
