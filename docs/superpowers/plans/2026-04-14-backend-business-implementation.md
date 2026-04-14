# 校园社团活动评估系统 - 后端业务实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 完成后端六大业务模块（用户、社团、活动、资源、评估、审批）的全部功能开发，实现与前端三端的完整API对接。

**Architecture:** 采用领域驱动设计（DDD）+ 分层架构，按业务领域划分模块。技术栈：Spring Boot 3.2.x + Java 21 + PostgreSQL + Redis + JWT + MapStruct。

**Tech Stack:** Spring Boot 3.2.5, Spring Data JPA, Spring Security, PostgreSQL, Redis, JWT, MapStruct 1.5.5, Flyway, Lombok

---

## 第一阶段：数据库迁移脚本（基础）

### Task 1: 创建用户表迁移脚本

**Files:**
- Create: `campus-main/src/main/resources/db/migration/V1__create_users_table.sql`

- [ ] **Step 1: 创建用户表迁移脚本**

```sql
CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    openid VARCHAR(100) UNIQUE,
    student_id VARCHAR(50) UNIQUE,
    username VARCHAR(50) NOT NULL,
    nickname VARCHAR(50),
    avatar_url VARCHAR(500),
    phone VARCHAR(20),
    email VARCHAR(100),
    role VARCHAR(20) NOT NULL DEFAULT 'STUDENT',
    status VARCHAR(20) DEFAULT 'ACTIVE',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    deleted BOOLEAN DEFAULT FALSE
);

CREATE INDEX IF NOT EXISTS idx_users_openid ON users(openid);
CREATE INDEX IF NOT EXISTS idx_users_student_id ON users(student_id);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
```

- [ ] **Step 2: Commit**

```bash
git add campus-main/src/main/resources/db/migration/V1__create_users_table.sql
git commit -m "feat: add users table migration"
```

---

### Task 2: 创建社团表迁移脚本

**Files:**
- Create: `campus-main/src/main/resources/db/migration/V2__create_clubs_table.sql`

- [ ] **Step 1: 创建社团表迁移脚本**

```sql
CREATE TABLE IF NOT EXISTS clubs (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(50) UNIQUE,
    description TEXT,
    category VARCHAR(50),
    logo_url VARCHAR(500),
    president_id BIGINT REFERENCES users(id),
    faculty_advisor VARCHAR(100),
    status VARCHAR(20) DEFAULT 'ACTIVE',
    member_count INT DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    deleted BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS club_members (
    id BIGSERIAL PRIMARY KEY,
    club_id BIGINT NOT NULL REFERENCES clubs(id),
    user_id BIGINT NOT NULL REFERENCES users(id),
    role VARCHAR(20) DEFAULT 'MEMBER',
    joined_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(club_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_clubs_category ON clubs(category);
CREATE INDEX IF NOT EXISTS idx_clubs_status ON clubs(status);
CREATE INDEX IF NOT EXISTS idx_club_members_club_id ON club_members(club_id);
CREATE INDEX IF NOT EXISTS idx_club_members_user_id ON club_members(user_id);
```

- [ ] **Step 2: Commit**

```bash
git add campus-main/src/main/resources/db/migration/V2__create_clubs_table.sql
git commit -m "feat: add clubs and club_members table migration"
```

---

### Task 3: 创建活动表迁移脚本

**Files:**
- Create: `campus-main/src/main/resources/db/migration/V3__create_activities_table.sql`

- [ ] **Step 1: 创建活动表迁移脚本**

```sql
CREATE TABLE IF NOT EXISTS activities (
    id BIGSERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    activity_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'DRAFT',
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    location VARCHAR(200),
    capacity INT,
    current_participants INT DEFAULT 0,
    club_id BIGINT REFERENCES clubs(id),
    created_by BIGINT REFERENCES users(id),
    cover_image_url VARCHAR(500),
    budget DECIMAL(10,2),
    required_resources JSONB,
    approval_status VARCHAR(20) DEFAULT 'NONE',
    approval_comment TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    deleted BOOLEAN DEFAULT FALSE,
    CHECK (end_time > start_time)
);

CREATE TABLE IF NOT EXISTS activity_participants (
    id BIGSERIAL PRIMARY KEY,
    activity_id BIGINT NOT NULL REFERENCES activities(id),
    user_id BIGINT NOT NULL REFERENCES users(id),
    status VARCHAR(20) DEFAULT 'REGISTERED',
    registered_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    checked_in_at TIMESTAMP,
    UNIQUE(activity_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_activities_status ON activities(status);
CREATE INDEX IF NOT EXISTS idx_activities_club_id ON activities(club_id);
CREATE INDEX IF NOT EXISTS idx_activities_start_time ON activities(start_time);
CREATE INDEX IF NOT EXISTS idx_activities_type ON activities(activity_type);
CREATE INDEX IF NOT EXISTS idx_participants_activity_id ON activity_participants(activity_id);
CREATE INDEX IF NOT EXISTS idx_participants_user_id ON activity_participants(user_id);
```

- [ ] **Step 2: Commit**

```bash
git add campus-main/src/main/resources/db/migration/V3__create_activities_table.sql
git commit -m "feat: add activities and activity_participants table migration"
```

---

### Task 4: 创建资源表迁移脚本

**Files:**
- Create: `campus-main/src/main/resources/db/migration/V4__create_resources_table.sql`

- [ ] **Step 1: 创建资源表迁移脚本**

```sql
CREATE TABLE IF NOT EXISTS resources (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    description TEXT,
    capacity INT,
    available_count INT DEFAULT 0,
    total_count INT NOT NULL,
    unit VARCHAR(20),
    location VARCHAR(200),
    manager_id BIGINT REFERENCES users(id),
    constraints JSONB,
    status VARCHAR(20) DEFAULT 'AVAILABLE',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    deleted BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS resource_reservations (
    id BIGSERIAL PRIMARY KEY,
    resource_id BIGINT NOT NULL REFERENCES resources(id),
    activity_id BIGINT REFERENCES activities(id),
    applicant_id BIGINT NOT NULL REFERENCES users(id),
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    quantity INT DEFAULT 1,
    status VARCHAR(20) DEFAULT 'PENDING',
    purpose TEXT,
    approval_comment TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    CHECK (end_time > start_time)
);

CREATE INDEX IF NOT EXISTS idx_resources_type ON resources(resource_type);
CREATE INDEX IF NOT EXISTS idx_resources_status ON resources(status);
CREATE INDEX IF NOT EXISTS idx_reservations_resource_id ON resource_reservations(resource_id);
CREATE INDEX IF NOT EXISTS idx_reservations_activity_id ON resource_reservations(activity_id);
CREATE INDEX IF NOT EXISTS idx_reservations_time_range ON resource_reservations(start_time, end_time);
```

- [ ] **Step 2: Commit**

```bash
git add campus-main/src/main/resources/db/migration/V4__create_resources_table.sql
git commit -m "feat: add resources and resource_reservations table migration"
```

---

### Task 5: 创建评估和反馈表迁移脚本

**Files:**
- Create: `campus-main/src/main/resources/db/migration/V5__create_evaluations_table.sql`

- [ ] **Step 1: 创建评估和反馈表迁移脚本**

```sql
CREATE TABLE IF NOT EXISTS evaluations (
    id BIGSERIAL PRIMARY KEY,
    activity_id BIGINT NOT NULL UNIQUE REFERENCES activities(id),
    participant_count INT,
    satisfaction_score DECIMAL(3,2),
    participation_score DECIMAL(5,2),
    educational_score DECIMAL(5,2),
    innovation_score DECIMAL(5,2),
    influence_score DECIMAL(5,2),
    sustainability_score DECIMAL(5,2),
    overall_score DECIMAL(5,2),
    algorithm_version VARCHAR(50),
    radar_chart_data JSONB,
    generated_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS activity_feedbacks (
    id BIGSERIAL PRIMARY KEY,
    activity_id BIGINT NOT NULL REFERENCES activities(id),
    user_id BIGINT NOT NULL REFERENCES users(id),
    rating INT NOT NULL CHECK (rating >= 1 AND rating <= 5),
    content TEXT,
    sentiment_score DECIMAL(3,2),
    photos JSONB,
    is_anonymous BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(activity_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_evaluations_activity_id ON evaluations(activity_id);
CREATE INDEX IF NOT EXISTS idx_feedbacks_activity_id ON activity_feedbacks(activity_id);
CREATE INDEX IF NOT EXISTS idx_feedbacks_user_id ON activity_feedbacks(user_id);
```

- [ ] **Step 2: Commit**

```bash
git add campus-main/src/main/resources/db/migration/V5__create_evaluations_table.sql
git commit -m "feat: add evaluations and activity_feedbacks table migration"
```

---

### Task 6: 创建审批记录表迁移脚本

**Files:**
- Create: `campus-main/src/main/resources/db/migration/V6__create_approvals_table.sql`

- [ ] **Step 1: 创建审批记录表迁移脚本**

```sql
CREATE TABLE IF NOT EXISTS approval_records (
    id BIGSERIAL PRIMARY KEY,
    target_type VARCHAR(50) NOT NULL,
    target_id BIGINT NOT NULL,
    applicant_id BIGINT NOT NULL REFERENCES users(id),
    approver_id BIGINT REFERENCES users(id),
    status VARCHAR(20) NOT NULL,
    submit_data JSONB,
    comment TEXT,
    submitted_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_approvals_target ON approval_records(target_type, target_id);
CREATE INDEX IF NOT EXISTS idx_approvals_status ON approval_records(status);
CREATE INDEX IF NOT EXISTS idx_approvals_applicant ON approval_records(applicant_id);
```

- [ ] **Step 2: Commit**

```bash
git add campus-main/src/main/resources/db/migration/V6__create_approvals_table.sql
git commit -m "feat: add approval_records table migration"
```

---

## 第二阶段：用户模块实现

### Task 7: 创建用户领域实体

**Files:**
- Create: `campus-main/src/main/java/com/campusclub/user/domain/entity/User.java`

- [ ] **Step 1: 创建用户实体**

```java
package com.campusclub.user.domain.entity;

import com.campusclub.common.model.BaseEntity;
import jakarta.persistence.*;
import lombok.*;

@Entity
@Table(name = "users")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class User extends BaseEntity {

    @Column(name = "openid", unique = true, length = 100)
    private String openid;

    @Column(name = "student_id", unique = true, length = 50)
    private String studentId;

    @Column(name = "username", nullable = false, length = 50)
    private String username;

    @Column(name = "nickname", length = 50)
    private String nickname;

    @Column(name = "avatar_url", length = 500)
    private String avatarUrl;

    @Column(name = "phone", length = 20)
    private String phone;

    @Column(name = "email", length = 100)
    private String email;

    @Column(name = "password", length = 100)
    private String password;

    @Enumerated(EnumType.STRING)
    @Column(name = "role", nullable = false, length = 20)
    private UserRole role = UserRole.STUDENT;

    @Enumerated(EnumType.STRING)
    @Column(name = "status", length = 20)
    private UserStatus status = UserStatus.ACTIVE;

    public enum UserRole {
        STUDENT, CLUB_MEMBER, CLUB_MANAGER, CLUB_PRESIDENT, ADMIN, SUPER_ADMIN
    }

    public enum UserStatus {
        ACTIVE, INACTIVE
    }
}
```

- [ ] **Step 2: Commit**

```bash
git add campus-main/src/main/java/com/campusclub/user/domain/entity/User.java
git commit -m "feat: add User entity"
```

---

### Task 8: 创建用户Repository接口

**Files:**
- Create: `campus-main/src/main/java/com/campusclub/user/domain/repository/UserRepository.java`

- [ ] **Step 1: 创建用户Repository接口**

```java
package com.campusclub.user.domain.repository;

import com.campusclub.user.domain.entity.User;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface UserRepository extends JpaRepository<User, Long> {

    Optional<User> findByOpenid(String openid);

    Optional<User> findByStudentId(String studentId);

    Optional<User> findByUsername(String username);

    boolean existsByOpenid(String openid);

    boolean existsByStudentId(String studentId);

    Page<User> findByRole(User.UserRole role, Pageable pageable);
}
```

- [ ] **Step 2: Commit**

```bash
git add campus-main/src/main/java/com/campusclub/user/domain/repository/UserRepository.java
git commit -m "feat: add UserRepository interface"
```

---

### Task 9: 创建用户DTO

**Files:**
- Create: `campus-main/src/main/java/com/campusclub/user/application/dto/UserDto.java`

- [ ] **Step 1: 创建用户DTO**

```java
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
```

- [ ] **Step 2: 创建用户信息更新请求DTO**

```java
package com.campusclub.user.application.dto;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.Size;

public record UserUpdateRequest(
    @Size(max = 50) String nickname,
    @Size(max = 500) String avatarUrl,
    @Size(max = 20) String phone,
    @Email @Size(max = 100) String email
) {}
```

- [ ] **Step 3: Commit**

```bash
git add campus-main/src/main/java/com/campusclub/user/application/dto/
git commit -m "feat: add User DTOs"
```

---

### Task 10: 创建UserMapper

**Files:**
- Create: `campus-main/src/main/java/com/campusclub/user/application/mapper/UserMapper.java`

- [ ] **Step 1: 创建UserMapper接口**

```java
package com.campusclub.user.application.mapper;

import com.campusclub.user.application.dto.UserDto;
import com.campusclub.user.application.dto.UserUpdateRequest;
import com.campusclub.user.domain.entity.User;
import org.mapstruct.*;

@Mapper(componentModel = "spring", unmappedTargetPolicy = ReportingPolicy.IGNORE)
public interface UserMapper {

    UserDto toDto(User user);

    @BeanMapping(nullValuePropertyMappingStrategy = NullValuePropertyMappingStrategy.IGNORE)
    void updateEntityFromRequest(UserUpdateRequest request, @MappingTarget User user);
}
```

- [ ] **Step 2: Commit**

```bash
git add campus-main/src/main/java/com/campusclub/user/application/mapper/UserMapper.java
git commit -m "feat: add UserMapper"
```

---

### Task 11: 创建微信登录Service

**Files:**
- Create: `campus-main/src/main/java/com/campusclub/user/infrastructure/external/WechatMpClient.java`

- [ ] **Step 1: 创建微信客户端配置属性**

```java
package com.campusclub.user.infrastructure.external;

import lombok.Data;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.stereotype.Component;

@Data
@Component
@ConfigurationProperties(prefix = "wechat.mp")
public class WechatMpProperties {
    private String appId;
    private String secret;
}
```

- [ ] **Step 2: 创建微信登录响应DTO**

```java
package com.campusclub.user.infrastructure.external;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;

@Data
public class WechatSessionResponse {
    private String openid;
    @JsonProperty("session_key")
    private String sessionKey;
    private String unionid;
    private Integer errcode;
    private String errmsg;
}
```

- [ ] **Step 3: 创建微信客户端**

```java
package com.campusclub.user.infrastructure.external;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.util.UriComponentsBuilder;

@Slf4j
@Component
@RequiredArgsConstructor
public class WechatMpClient {

    private static final String AUTH_CODE2SESSION_URL = "https://api.weixin.qq.com/sns/jscode2session";
    
    private final WechatMpProperties properties;
    private final RestTemplate restTemplate = new RestTemplate();

    public WechatSessionResponse code2Session(String code) {
        String url = UriComponentsBuilder.fromHttpUrl(AUTH_CODE2SESSION_URL)
                .queryParam("appid", properties.getAppId())
                .queryParam("secret", properties.getSecret())
                .queryParam("js_code", code)
                .queryParam("grant_type", "authorization_code")
                .toUriString();

        log.info("Requesting WeChat session with code: {}", code);
        
        WechatSessionResponse response = restTemplate.getForObject(url, WechatSessionResponse.class);
        
        if (response != null && response.getErrcode() != null && response.getErrcode() != 0) {
            log.error("WeChat API error: {} - {}", response.getErrcode(), response.getErrmsg());
            throw new RuntimeException("微信登录失败: " + response.getErrmsg());
        }
        
        return response;
    }
}
```

- [ ] **Step 4: Commit**

```bash
git add campus-main/src/main/java/com/campusclub/user/infrastructure/external/
git commit -m "feat: add WeChat Mini Program client"
```

---

### Task 12: 创建认证Service

**Files:**
- Create: `campus-main/src/main/java/com/campusclub/user/application/service/AuthApplicationService.java`

- [ ] **Step 1: 创建登录请求/响应DTO**

```java
package com.campusclub.user.application.dto;

import jakarta.validation.constraints.NotBlank;

public record WechatLoginRequest(
    @NotBlank String code,
    String userInfo
) {}
```

```java
package com.campusclub.user.application.dto;

public record LoginResponse(
    String accessToken,
    String refreshToken,
    Long expiresIn,
    UserDto user
) {}
```

- [ ] **Step 2: 创建认证Service**

```java
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
        // 1. 获取微信openid
        WechatSessionResponse session = wechatMpClient.code2Session(request.getCode());
        String openid = session.getOpenid();
        
        // 2. 查找或创建用户
        User user = userRepository.findByOpenid(openid)
                .orElseGet(() -> createNewUser(openid));
        
        // 3. 生成JWT Token
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
```

- [ ] **Step 3: Commit**

```bash
git add campus-main/src/main/java/com/campusclub/user/application/service/AuthApplicationService.java
git add campus-main/src/main/java/com/campusclub/user/application/dto/WechatLoginRequest.java
git add campus-main/src/main/java/com/campusclub/user/application/dto/LoginResponse.java
git commit -m "feat: add auth application service with WeChat login"
```

---

### Task 13: 创建认证Controller

**Files:**
- Create: `campus-main/src/main/java/com/campusclub/user/interfaces/rest/AuthController.java`

- [ ] **Step 1: 创建认证Controller**

```java
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
        // 可以在这里实现token黑名单逻辑
        return ResponseEntity.ok(ApiResponse.success(null));
    }
}
```

- [ ] **Step 2: Commit**

```bash
git add campus-main/src/main/java/com/campusclub/user/interfaces/rest/AuthController.java
git commit -m "feat: add AuthController"
```

---

### Task 14: 创建用户Service

**Files:**
- Create: `campus-main/src/main/java/com/campusclub/user/application/service/UserApplicationService.java`

- [ ] **Step 1: 创建用户Service**

```java
package com.campusclub.user.application.service;

import com.campusclub.user.application.dto.UserDto;
import com.campusclub.user.application.dto.UserUpdateRequest;
import com.campusclub.user.application.mapper.UserMapper;
import com.campusclub.user.domain.entity.User;
import com.campusclub.user.domain.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class UserApplicationService {

    private final UserRepository userRepository;
    private final UserMapper userMapper;

    @Transactional(readOnly = true)
    public UserDto getCurrentUser(Long userId) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new RuntimeException("用户不存在"));
        return userMapper.toDto(user);
    }

    @Transactional
    public UserDto updateUser(Long userId, UserUpdateRequest request) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new RuntimeException("用户不存在"));
        
        userMapper.updateEntityFromRequest(request, user);
        User updatedUser = userRepository.save(user);
        
        return userMapper.toDto(updatedUser);
    }
}
```

- [ ] **Step 2: Commit**

```bash
git add campus-main/src/main/java/com/campusclub/user/application/service/UserApplicationService.java
git commit -m "feat: add UserApplicationService"
```

---

### Task 15: 创建用户Controller

**Files:**
- Create: `campus-main/src/main/java/com/campusclub/user/interfaces/rest/UserController.java`

- [ ] **Step 1: 创建用户Controller**

```java
package com.campusclub.user.interfaces.rest;

import com.campusclub.dto.ApiResponse;
import com.campusclub.user.application.dto.UserDto;
import com.campusclub.user.application.dto.UserUpdateRequest;
import com.campusclub.user.application.service.UserApplicationService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1/users")
@RequiredArgsConstructor
@SecurityRequirement(name = "bearerAuth")
@Tag(name = "用户", description = "用户管理相关接口")
public class UserController {

    private final UserApplicationService userService;

    @GetMapping("/me")
    @Operation(summary = "获取当前用户信息", description = "获取当前登录用户的详细信息")
    public ResponseEntity<ApiResponse<UserDto>> getCurrentUser(
            @AuthenticationPrincipal Long userId) {
        UserDto user = userService.getCurrentUser(userId);
        return ResponseEntity.ok(ApiResponse.success(user));
    }

    @PutMapping("/me")
    @Operation(summary = "更新当前用户信息", description = "更新当前登录用户的个人信息")
    public ResponseEntity<ApiResponse<UserDto>> updateCurrentUser(
            @AuthenticationPrincipal Long userId,
            @RequestBody @Valid UserUpdateRequest request) {
        UserDto updatedUser = userService.updateUser(userId, request);
        return ResponseEntity.ok(ApiResponse.success(updatedUser));
    }
}
```

- [ ] **Step 2: Commit**

```bash
git add campus-main/src/main/java/com/campusclub/user/interfaces/rest/UserController.java
git commit -m "feat: add UserController"
```

---

## 第三阶段：社团模块实现

### Task 16: 创建社团领域实体

**Files:**
- Create: `campus-main/src/main/java/com/campusclub/club/domain/entity/Club.java`
- Create: `campus-main/src/main/java/com/campusclub/club/domain/entity/ClubMember.java`

- [ ] **Step 1: 创建Club实体**

```java
package com.campusclub.club.domain.entity;

import com.campusclub.common.model.BaseEntity;
import jakarta.persistence.*;
import lombok.*;

@Entity
@Table(name = "clubs")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Club extends BaseEntity {

    @Column(name = "name", nullable = false, length = 100)
    private String name;

    @Column(name = "code", unique = true, length = 50)
    private String code;

    @Column(name = "description", columnDefinition = "TEXT")
    private String description;

    @Enumerated(EnumType.STRING)
    @Column(name = "category", length = 50)
    private ClubCategory category;

    @Column(name = "logo_url", length = 500)
    private String logoUrl;

    @Column(name = "president_id")
    private Long presidentId;

    @Column(name = "faculty_advisor", length = 100)
    private String facultyAdvisor;

    @Enumerated(EnumType.STRING)
    @Column(name = "status", length = 20)
    private ClubStatus status = ClubStatus.ACTIVE;

    @Column(name = "member_count")
    private Integer memberCount = 0;

    public enum ClubCategory {
        ACADEMIC, ARTS, SPORTS, VOLUNTEER, TECHNOLOGY, CULTURE, OTHER
    }

    public enum ClubStatus {
        ACTIVE, INACTIVE, SUSPENDED
    }
}
```

- [ ] **Step 2: 创建ClubMember实体**

```java
package com.campusclub.club.domain.entity;

import com.campusclub.common.model.BaseEntity;
import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDateTime;

@Entity
@Table(name = "club_members")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class ClubMember extends BaseEntity {

    @Column(name = "club_id", nullable = false)
    private Long clubId;

    @Column(name = "user_id", nullable = false)
    private Long userId;

    @Enumerated(EnumType.STRING)
    @Column(name = "role", length = 20)
    private MemberRole role = MemberRole.MEMBER;

    @Column(name = "joined_at", nullable = false)
    private LocalDateTime joinedAt = LocalDateTime.now();

    public enum MemberRole {
        MEMBER, MANAGER, PRESIDENT
    }
}
```

- [ ] **Step 3: Commit**

```bash
git add campus-main/src/main/java/com/campusclub/club/domain/entity/
git commit -m "feat: add Club and ClubMember entities"
```

---

### Task 17: 创建社团Repository

**Files:**
- Create: `campus-main/src/main/java/com/campusclub/club/domain/repository/ClubRepository.java`
- Create: `campus-main/src/main/java/com/campusclub/club/domain/repository/ClubMemberRepository.java`

- [ ] **Step 1: 创建ClubRepository**

```java
package com.campusclub.club.domain.repository;

import com.campusclub.club.domain.entity.Club;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface ClubRepository extends JpaRepository<Club, Long> {

    Optional<Club> findByCode(String code);

    Page<Club> findByStatus(Club.ClubStatus status, Pageable pageable);

    Page<Club> findByCategory(Club.ClubCategory category, Pageable pageable);

    List<Club> findByPresidentId(Long presidentId);

    boolean existsByCode(String code);
}
```

- [ ] **Step 2: 创建ClubMemberRepository**

```java
package com.campusclub.club.domain.repository;

import com.campusclub.club.domain.entity.ClubMember;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface ClubMemberRepository extends JpaRepository<ClubMember, Long> {

    List<ClubMember> findByClubId(Long clubId);

    List<ClubMember> findByUserId(Long userId);

    Optional<ClubMember> findByClubIdAndUserId(Long clubId, Long userId);

    boolean existsByClubIdAndUserId(Long clubId, Long userId);

    long countByClubId(Long clubId);

    List<ClubMember> findByClubIdAndRole(Long clubId, ClubMember.MemberRole role);
}
```

- [ ] **Step 3: Commit**

```bash
git add campus-main/src/main/java/com/campusclub/club/domain/repository/
git commit -m "feat: add Club and ClubMember repositories"
```

---

### Task 18: 创建社团DTO

**Files:**
- Create: `campus-main/src/main/java/com/campusclub/club/application/dto/ClubDto.java`
- Create: `campus-main/src/main/java/com/campusclub/club/application/dto/ClubCreateRequest.java`
- Create: `campus-main/src/main/java/com/campusclub/club/application/dto/ClubMemberDto.java`

- [ ] **Step 1: 创建ClubDto**

```java
package com.campusclub.club.application.dto;

import com.campusclub.club.domain.entity.Club;

import java.time.LocalDateTime;

public record ClubDto(
    Long id,
    String name,
    String code,
    String description,
    Club.ClubCategory category,
    String logoUrl,
    Long presidentId,
    String facultyAdvisor,
    Club.ClubStatus status,
    Integer memberCount,
    LocalDateTime createdAt
) {}
```

- [ ] **Step 2: 创建ClubCreateRequest**

```java
package com.campusclub.club.application.dto;

import com.campusclub.club.domain.entity.Club;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;

public record ClubCreateRequest(
    @NotBlank @Size(max = 100) String name,
    @Size(max = 50) String code,
    String description,
    @NotNull Club.ClubCategory category,
    @Size(max = 500) String logoUrl,
    Long presidentId,
    @Size(max = 100) String facultyAdvisor
) {}
```

- [ ] **Step 3: 创建ClubMemberDto**

```java
package com.campusclub.club.application.dto;

import com.campusclub.club.domain.entity.ClubMember;
import com.campusclub.user.application.dto.UserDto;

import java.time.LocalDateTime;

public record ClubMemberDto(
    Long id,
    Long clubId,
    Long userId,
    String username,
    String nickname,
    ClubMember.MemberRole role,
    LocalDateTime joinedAt
) {}
```

- [ ] **Step 4: Commit**

```bash
git add campus-main/src/main/java/com/campusclub/club/application/dto/
git commit -m "feat: add Club DTOs"
```

---

### Task 19: 创建ClubMapper

**Files:**
- Create: `campus-main/src/main/java/com/campusclub/club/application/mapper/ClubMapper.java`

- [ ] **Step 1: 创建ClubMapper**

```java
package com.campusclub.club.application.mapper;

import com.campusclub.club.application.dto.ClubCreateRequest;
import com.campusclub.club.application.dto.ClubDto;
import com.campusclub.club.application.dto.ClubMemberDto;
import com.campusclub.club.domain.entity.Club;
import com.campusclub.club.domain.entity.ClubMember;
import com.campusclub.user.domain.entity.User;
import org.mapstruct.*;

@Mapper(componentModel = "spring", unmappedTargetPolicy = ReportingPolicy.IGNORE)
public interface ClubMapper {

    ClubDto toDto(Club club);

    Club toEntity(ClubCreateRequest request);

    @Mapping(target = "username", source = "user.username")
    @Mapping(target = "nickname", source = "user.nickname")
    ClubMemberDto toMemberDto(ClubMember member, User user);
}
```

- [ ] **Step 2: Commit**

```bash
git add campus-main/src/main/java/com/campusclub/club/application/mapper/ClubMapper.java
git commit -m "feat: add ClubMapper"
```

---

### Task 20: 创建社团Service

**Files:**
- Create: `campus-main/src/main/java/com/campusclub/club/application/service/ClubApplicationService.java`

- [ ] **Step 1: 创建社团Service**

```java
package com.campusclub.club.application.service;

import com.campusclub.club.application.dto.*;
import com.campusclub.club.application.mapper.ClubMapper;
import com.campusclub.club.domain.entity.Club;
import com.campusclub.club.domain.entity.ClubMember;
import com.campusclub.club.domain.repository.ClubMemberRepository;
import com.campusclub.club.domain.repository.ClubRepository;
import com.campusclub.user.domain.entity.User;
import com.campusclub.user.domain.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@RequiredArgsConstructor
public class ClubApplicationService {

    private final ClubRepository clubRepository;
    private final ClubMemberRepository clubMemberRepository;
    private final UserRepository userRepository;
    private final ClubMapper clubMapper;

    @Transactional(readOnly = true)
    public Page<ClubDto> listClubs(Club.ClubCategory category, Club.ClubStatus status, Pageable pageable) {
        Page<Club> clubs;
        if (category != null) {
            clubs = clubRepository.findByCategory(category, pageable);
        } else if (status != null) {
            clubs = clubRepository.findByStatus(status, pageable);
        } else {
            clubs = clubRepository.findAll(pageable);
        }
        return clubs.map(clubMapper::toDto);
    }

    @Transactional(readOnly = true)
    public ClubDto getClub(Long id) {
        Club club = clubRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("社团不存在"));
        return clubMapper.toDto(club);
    }

    @Transactional
    public ClubDto createClub(ClubCreateRequest request) {
        if (request.code() != null && clubRepository.existsByCode(request.code())) {
            throw new RuntimeException("社团代码已存在");
        }
        
        Club club = clubMapper.toEntity(request);
        club.setStatus(Club.ClubStatus.ACTIVE);
        club.setMemberCount(0);
        
        Club savedClub = clubRepository.save(club);
        return clubMapper.toDto(savedClub);
    }

    @Transactional
    public ClubDto updateClub(Long id, ClubCreateRequest request) {
        Club club = clubRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("社团不存在"));
        
        if (request.code() != null && !request.code().equals(club.getCode()) 
                && clubRepository.existsByCode(request.code())) {
            throw new RuntimeException("社团代码已存在");
        }
        
        club.setName(request.name());
        club.setCode(request.code());
        club.setDescription(request.description());
        club.setCategory(request.category());
        club.setLogoUrl(request.logoUrl());
        club.setPresidentId(request.presidentId());
        club.setFacultyAdvisor(request.facultyAdvisor());
        
        Club updatedClub = clubRepository.save(club);
        return clubMapper.toDto(updatedClub);
    }

    @Transactional
    public void deleteClub(Long id) {
        Club club = clubRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("社团不存在"));
        club.setDeleted(true);
        clubRepository.save(club);
    }

    @Transactional(readOnly = true)
    public List<ClubMemberDto> listClubMembers(Long clubId) {
        List<ClubMember> members = clubMemberRepository.findByClubId(clubId);
        return members.stream()
                .map(member -> {
                    User user = userRepository.findById(member.getUserId()).orElse(null);
                    return clubMapper.toMemberDto(member, user);
                })
                .toList();
    }

    @Transactional
    public void addClubMember(Long clubId, Long userId, ClubMember.MemberRole role) {
        if (clubMemberRepository.existsByClubIdAndUserId(clubId, userId)) {
            throw new RuntimeException("该用户已是社团成员");
        }
        
        ClubMember member = ClubMember.builder()
                .clubId(clubId)
                .userId(userId)
                .role(role != null ? role : ClubMember.MemberRole.MEMBER)
                .build();
        
        clubMemberRepository.save(member);
        
        // 更新社团成员数
        Club club = clubRepository.findById(clubId).orElseThrow();
        club.setMemberCount((int) clubMemberRepository.countByClubId(clubId));
        clubRepository.save(club);
    }

    @Transactional
    public void removeClubMember(Long clubId, Long userId) {
        ClubMember member = clubMemberRepository.findByClubIdAndUserId(clubId, userId)
                .orElseThrow(() -> new RuntimeException("该用户不是社团成员"));
        
        clubMemberRepository.delete(member);
        
        // 更新社团成员数
        Club club = clubRepository.findById(clubId).orElseThrow();
        club.setMemberCount((int) clubMemberRepository.countByClubId(clubId));
        clubRepository.save(club);
    }
}
```

- [ ] **Step 2: Commit**

```bash
git add campus-main/src/main/java/com/campusclub/club/application/service/ClubApplicationService.java
git commit -m "feat: add ClubApplicationService"
```

---

### Task 21: 创建社团Controller

**Files:**
- Create: `campus-main/src/main/java/com/campusclub/club/interfaces/rest/ClubController.java`

- [ ] **Step 1: 创建社团Controller**

```java
package com.campusclub.club.interfaces.rest;

import com.campusclub.club.application.dto.*;
import com.campusclub.club.application.service.ClubApplicationService;
import com.campusclub.club.domain.entity.Club;
import com.campusclub.club.domain.entity.ClubMember;
import com.campusclub.dto.ApiResponse;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/v1/clubs")
@RequiredArgsConstructor
@Tag(name = "社团", description = "社团管理相关接口")
public class ClubController {

    private final ClubApplicationService clubService;

    @GetMapping
    @Operation(summary = "社团列表", description = "获取社团列表，支持按类别和状态筛选")
    public ResponseEntity<ApiResponse<Page<ClubDto>>> listClubs(
            @RequestParam(required = false) Club.ClubCategory category,
            @RequestParam(required = false) Club.ClubStatus status,
            Pageable pageable) {
        Page<ClubDto> clubs = clubService.listClubs(category, status, pageable);
        return ResponseEntity.ok(ApiResponse.success(clubs));
    }

    @GetMapping("/{id}")
    @Operation(summary = "社团详情", description = "获取社团详细信息")
    public ResponseEntity<ApiResponse<ClubDto>> getClub(@PathVariable Long id) {
        ClubDto club = clubService.getClub(id);
        return ResponseEntity.ok(ApiResponse.success(club));
    }

    @PostMapping
    @PreAuthorize("hasRole('ADMIN') or hasRole('SUPER_ADMIN')")
    @SecurityRequirement(name = "bearerAuth")
    @Operation(summary = "创建社团", description = "创建新社团（管理员权限）")
    public ResponseEntity<ApiResponse<ClubDto>> createClub(
            @RequestBody @Valid ClubCreateRequest request) {
        ClubDto club = clubService.createClub(request);
        return ResponseEntity.status(HttpStatus.CREATED).body(ApiResponse.success(club));
    }

    @PutMapping("/{id}")
    @PreAuthorize("hasRole('ADMIN') or hasRole('SUPER_ADMIN') or @clubSecurity.isClubPresident(#id, authentication)")
    @SecurityRequirement(name = "bearerAuth")
    @Operation(summary = "更新社团", description = "更新社团信息")
    public ResponseEntity<ApiResponse<ClubDto>> updateClub(
            @PathVariable Long id,
            @RequestBody @Valid ClubCreateRequest request) {
        ClubDto club = clubService.updateClub(id, request);
        return ResponseEntity.ok(ApiResponse.success(club));
    }

    @DeleteMapping("/{id}")
    @PreAuthorize("hasRole('ADMIN') or hasRole('SUPER_ADMIN')")
    @SecurityRequirement(name = "bearerAuth")
    @Operation(summary = "删除社团", description = "删除社团（管理员权限）")
    public ResponseEntity<ApiResponse<Void>> deleteClub(@PathVariable Long id) {
        clubService.deleteClub(id);
        return ResponseEntity.ok(ApiResponse.success(null));
    }

    @GetMapping("/{id}/members")
    @SecurityRequirement(name = "bearerAuth")
    @Operation(summary = "社团成员列表", description = "获取社团成员列表")
    public ResponseEntity<ApiResponse<List<ClubMemberDto>>> listClubMembers(
            @PathVariable Long id) {
        List<ClubMemberDto> members = clubService.listClubMembers(id);
        return ResponseEntity.ok(ApiResponse.success(members));
    }

    @PostMapping("/{id}/members")
    @PreAuthorize("hasRole('ADMIN') or hasRole('SUPER_ADMIN') or @clubSecurity.isClubManager(#id, authentication)")
    @SecurityRequirement(name = "bearerAuth")
    @Operation(summary = "添加社团成员", description = "添加成员到社团")
    public ResponseEntity<ApiResponse<Void>> addClubMember(
            @PathVariable Long id,
            @RequestParam Long userId,
            @RequestParam(required = false) ClubMember.MemberRole role) {
        clubService.addClubMember(id, userId, role);
        return ResponseEntity.status(HttpStatus.CREATED).body(ApiResponse.success(null));
    }

    @DeleteMapping("/{id}/members/{userId}")
    @PreAuthorize("hasRole('ADMIN') or hasRole('SUPER_ADMIN') or @clubSecurity.isClubManager(#id, authentication)")
    @SecurityRequirement(name = "bearerAuth")
    @Operation(summary = "移除社团成员", description = "从社团移除成员")
    public ResponseEntity<ApiResponse<Void>> removeClubMember(
            @PathVariable Long id,
            @PathVariable Long userId) {
        clubService.removeClubMember(id, userId);
        return ResponseEntity.ok(ApiResponse.success(null));
    }
}
```

- [ ] **Step 2: Commit**

```bash
git add campus-main/src/main/java/com/campusclub/club/interfaces/rest/ClubController.java
git commit -m "feat: add ClubController"
```

---

## 第四阶段：活动模块实现

### Task 22: 创建活动领域实体

**Files:**
- Create: `campus-main/src/main/java/com/campusclub/activity/domain/entity/Activity.java`
- Create: `campus-main/src/main/java/com/campusclub/activity/domain/entity/ActivityParticipant.java`

- [ ] **Step 1: 创建Activity实体**

```java
package com.campusclub.activity.domain.entity;

import com.campusclub.common.model.BaseEntity;
import jakarta.persistence.*;
import lombok.*;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Entity
@Table(name = "activities")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Activity extends BaseEntity {

    @Column(name = "title", nullable = false, length = 200)
    private String title;

    @Column(name = "description", columnDefinition = "TEXT")
    private String description;

    @Enumerated(EnumType.STRING)
    @Column(name = "activity_type", nullable = false, length = 50)
    private ActivityType activityType;

    @Enumerated(EnumType.STRING)
    @Column(name = "status", length = 20)
    private ActivityStatus status = ActivityStatus.DRAFT;

    @Column(name = "start_time", nullable = false)
    private LocalDateTime startTime;

    @Column(name = "end_time", nullable = false)
    private LocalDateTime endTime;

    @Column(name = "location", length = 200)
    private String location;

    @Column(name = "capacity")
    private Integer capacity;

    @Column(name = "current_participants")
    private Integer currentParticipants = 0;

    @Column(name = "club_id")
    private Long clubId;

    @Column(name = "created_by")
    private Long createdBy;

    @Column(name = "cover_image_url", length = 500)
    private String coverImageUrl;

    @Column(name = "budget", precision = 10, scale = 2)
    private BigDecimal budget;

    @Column(name = "required_resources", columnDefinition = "jsonb")
    private String requiredResources;

    @Enumerated(EnumType.STRING)
    @Column(name = "approval_status", length = 20)
    private ApprovalStatus approvalStatus = ApprovalStatus.NONE;

    @Column(name = "approval_comment", columnDefinition = "TEXT")
    private String approvalComment;

    public enum ActivityType {
        LECTURE, WORKSHOP, COMPETITION, SOCIAL, VOLUNTEER, SPORTS, ENTERTAINMENT
    }

    public enum ActivityStatus {
        DRAFT, PENDING, APPROVED, REJECTED, REGISTERING, ONGOING, COMPLETED, CANCELLED
    }

    public enum ApprovalStatus {
        NONE, PENDING, APPROVED, REJECTED
    }

    // 状态转换方法
    public void submitForApproval() {
        if (this.status != ActivityStatus.DRAFT) {
            throw new IllegalStateException("只有草稿状态的活动可以提交审批");
        }
        this.status = ActivityStatus.PENDING;
        this.approvalStatus = ApprovalStatus.PENDING;
    }

    public void approve() {
        if (this.status != ActivityStatus.PENDING) {
            throw new IllegalStateException("只有待审批状态的活动可以审批通过");
        }
        this.status = ActivityStatus.APPROVED;
        this.approvalStatus = ApprovalStatus.APPROVED;
    }

    public void reject(String comment) {
        if (this.status != ActivityStatus.PENDING) {
            throw new IllegalStateException("只有待审批状态的活动可以驳回");
        }
        this.status = ActivityStatus.REJECTED;
        this.approvalStatus = ApprovalStatus.REJECTED;
        this.approvalComment = comment;
    }

    public void startRegistration() {
        if (this.status != ActivityStatus.APPROVED) {
            throw new IllegalStateException("只有已批准的活动可以开始报名");
        }
        this.status = ActivityStatus.REGISTERING;
    }

    public void startActivity() {
        if (this.status != ActivityStatus.REGISTERING) {
            throw new IllegalStateException("只有报名中的活动可以开始");
        }
        this.status = ActivityStatus.ONGOING;
    }

    public void complete() {
        if (this.status != ActivityStatus.ONGOING) {
            throw new IllegalStateException("只有进行中的活动可以结束");
        }
        this.status = ActivityStatus.COMPLETED;
    }

    public void cancel() {
        if (this.status == ActivityStatus.COMPLETED || this.status == ActivityStatus.CANCELLED) {
            throw new IllegalStateException("已结束或已取消的活动无法再次取消");
        }
        this.status = ActivityStatus.CANCELLED;
    }

    public boolean canRegister() {
        return this.status == ActivityStatus.REGISTERING
                && (this.capacity == null || this.currentParticipants < this.capacity);
    }
}
```

- [ ] **Step 2: 创建ActivityParticipant实体**

```java
package com.campusclub.activity.domain.entity;

import com.campusclub.common.model.BaseEntity;
import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDateTime;

@Entity
@Table(name = "activity_participants")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class ActivityParticipant extends BaseEntity {

    @Column(name = "activity_id", nullable = false)
    private Long activityId;

    @Column(name = "user_id", nullable = false)
    private Long userId;

    @Enumerated(EnumType.STRING)
    @Column(name = "status", length = 20)
    private ParticipationStatus status = ParticipationStatus.REGISTERED;

    @Column(name = "registered_at", nullable = false)
    private LocalDateTime registeredAt = LocalDateTime.now();

    @Column(name = "checked_in_at")
    private LocalDateTime checkedInAt;

    public enum ParticipationStatus {
        REGISTERED, CHECKED_IN, CANCELLED, NO_SHOW
    }

    public void checkIn() {
        if (this.status != ParticipationStatus.REGISTERED) {
            throw new IllegalStateException("只有已报名状态可以签到");
        }
        this.status = ParticipationStatus.CHECKED_IN;
        this.checkedInAt = LocalDateTime.now();
    }

    public void cancel() {
        if (this.status != ParticipationStatus.REGISTERED) {
            throw new IllegalStateException("只有已报名状态可以取消");
        }
        this.status = ParticipationStatus.CANCELLED;
    }
}
```

- [ ] **Step 3: Commit**

```bash
git add campus-main/src/main/java/com/campusclub/activity/domain/entity/
git commit -m "feat: add Activity and ActivityParticipant entities with state machine"
```

---

### Task 23: 创建活动Repository

**Files:**
- Create: `campus-main/src/main/java/com/campusclub/activity/domain/repository/ActivityRepository.java`
- Create: `campus-main/src/main/java/com/campusclub/activity/domain/repository/ActivityParticipantRepository.java`

- [ ] **Step 1: 创建ActivityRepository**

```java
package com.campusclub.activity.domain.repository;

import com.campusclub.activity.domain.entity.Activity;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;

@Repository
public interface ActivityRepository extends JpaRepository<Activity, Long> {

    Page<Activity> findByStatus(Activity.ActivityStatus status, Pageable pageable);

    Page<Activity> findByClubId(Long clubId, Pageable pageable);

    Page<Activity> findByClubIdAndStatus(Long clubId, Activity.ActivityStatus status, Pageable pageable);

    List<Activity> findByCreatedBy(Long createdBy);

    Page<Activity> findByActivityType(Activity.ActivityType type, Pageable pageable);

    @Query("SELECT a FROM Activity a WHERE a.status = :status AND a.startTime <= :time")
    List<Activity> findByStatusAndStartTimeBefore(
            @Param("status") Activity.ActivityStatus status,
            @Param("time") LocalDateTime time);

    @Query("SELECT a FROM Activity a WHERE a.status = :status AND a.endTime <= :time")
    List<Activity> findByStatusAndEndTimeBefore(
            @Param("status") Activity.ActivityStatus status,
            @Param("time") LocalDateTime time);

    @Query("SELECT a FROM Activity a WHERE a.status IN ('APPROVED', 'REGISTERING', 'ONGOING') " +
           "AND a.startTime BETWEEN :start AND :end")
    List<Activity> findActiveActivitiesInTimeRange(
            @Param("start") LocalDateTime start,
            @Param("end") LocalDateTime end);
}
```

- [ ] **Step 2: 创建ActivityParticipantRepository**

```java
package com.campusclub.activity.domain.repository;

import com.campusclub.activity.domain.entity.ActivityParticipant;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface ActivityParticipantRepository extends JpaRepository<ActivityParticipant, Long> {

    List<ActivityParticipant> findByActivityId(Long activityId);

    List<ActivityParticipant> findByUserId(Long userId);

    Optional<ActivityParticipant> findByActivityIdAndUserId(Long activityId, Long userId);

    boolean existsByActivityIdAndUserId(Long activityId, Long userId);

    long countByActivityId(Long activityId);

    long countByActivityIdAndStatus(Long activityId, ActivityParticipant.ParticipationStatus status);

    @Query("SELECT ap FROM ActivityParticipant ap WHERE ap.userId = :userId AND ap.status = 'REGISTERED'")
    List<ActivityParticipant> findActiveRegistrationsByUserId(@Param("userId") Long userId);
}
```

- [ ] **Step 3: Commit**

```bash
git add campus-main/src/main/java/com/campusclub/activity/domain/repository/
git commit -m "feat: add Activity and ActivityParticipant repositories"
```

---

### Task 24: 创建活动DTO

**Files:**
- Create: `campus-main/src/main/java/com/campusclub/activity/application/dto/ActivityDto.java`
- Create: `campus-main/src/main/java/com/campusclub/activity/application/dto/ActivityCreateRequest.java`
- Create: `campus-main/src/main/java/com/campusclub/activity/application/dto/ActivityParticipantDto.java`

- [ ] **Step 1: 创建ActivityDto**

```java
package com.campusclub.activity.application.dto;

import com.campusclub.activity.domain.entity.Activity;

import java.math.BigDecimal;
import java.time.LocalDateTime;

public record ActivityDto(
    Long id,
    String title,
    String description,
    Activity.ActivityType activityType,
    Activity.ActivityStatus status,
    LocalDateTime startTime,
    LocalDateTime endTime,
    String location,
    Integer capacity,
    Integer currentParticipants,
    Long clubId,
    String clubName,
    Long createdBy,
    String coverImageUrl,
    BigDecimal budget,
    Activity.ApprovalStatus approvalStatus,
    LocalDateTime createdAt
) {}
```

- [ ] **Step 2: 创建ActivityCreateRequest**

```java
package com.campusclub.activity.application.dto;

import com.campusclub.activity.domain.entity.Activity;
import jakarta.validation.constraints.*;

import java.math.BigDecimal;
import java.time.LocalDateTime;

public record ActivityCreateRequest(
    @NotBlank @Size(max = 200) String title,
    String description,
    @NotNull Activity.ActivityType activityType,
    @NotNull @Future LocalDateTime startTime,
    @NotNull @Future LocalDateTime endTime,
    @Size(max = 200) String location,
    @Min(1) Integer capacity,
    Long clubId,
    @Size(max = 500) String coverImageUrl,
    @DecimalMin("0.00") BigDecimal budget,
    String requiredResources
) {}
```

- [ ] **Step 3: 创建ActivityParticipantDto**

```java
package com.campusclub.activity.application.dto;

import com.campusclub.activity.domain.entity.ActivityParticipant;

import java.time.LocalDateTime;

public record ActivityParticipantDto(
    Long id,
    Long activityId,
    Long userId,
    String username,
    String nickname,
    String avatarUrl,
    ActivityParticipant.ParticipationStatus status,
    LocalDateTime registeredAt,
    LocalDateTime checkedInAt
) {}
```

- [ ] **Step 4: Commit**

```bash
git add campus-main/src/main/java/com/campusclub/activity/application/dto/
git commit -m "feat: add Activity DTOs"
```

---

### Task 25: 创建ActivityMapper

**Files:**
- Create: `campus-main/src/main/java/com/campusclub/activity/application/mapper/ActivityMapper.java`

- [ ] **Step 1: 创建ActivityMapper**

```java
package com.campusclub.activity.application.mapper;

import com.campusclub.activity.application.dto.ActivityCreateRequest;
import com.campusclub.activity.application.dto.ActivityDto;
import com.campusclub.activity.application.dto.ActivityParticipantDto;
import com.campusclub.activity.domain.entity.Activity;
import com.campusclub.activity.domain.entity.ActivityParticipant;
import com.campusclub.user.domain.entity.User;
import org.mapstruct.*;

@Mapper(componentModel = "spring", unmappedTargetPolicy = ReportingPolicy.IGNORE)
public interface ActivityMapper {

    @Mapping(target = "clubName", ignore = true)
    ActivityDto toDto(Activity activity);

    Activity toEntity(ActivityCreateRequest request);

    @Mapping(target = "username", source = "user.username")
    @Mapping(target = "nickname", source = "user.nickname")
    @Mapping(target = "avatarUrl", source = "user.avatarUrl")
    ActivityParticipantDto toParticipantDto(ActivityParticipant participant, User user);
}
```

- [ ] **Step 2: Commit**

```bash
git add campus-main/src/main/java/com/campusclub/activity/application/mapper/ActivityMapper.java
git commit -m "feat: add ActivityMapper"
```

---

### Task 26: 创建活动Service

**Files:**
- Create: `campus-main/src/main/java/com/campusclub/activity/application/service/ActivityApplicationService.java`

- [ ] **Step 1: 创建活动Service**

```java
package com.campusclub.activity.application.service;

import com.campusclub.activity.application.dto.*;
import com.campusclub.activity.application.mapper.ActivityMapper;
import com.campusclub.activity.domain.entity.Activity;
import com.campusclub.activity.domain.entity.ActivityParticipant;
import com.campusclub.activity.domain.repository.ActivityParticipantRepository;
import com.campusclub.activity.domain.repository.ActivityRepository;
import com.campusclub.club.domain.entity.Club;
import com.campusclub.club.domain.repository.ClubRepository;
import com.campusclub.user.domain.entity.User;
import com.campusclub.user.domain.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@RequiredArgsConstructor
public class ActivityApplicationService {

    private final ActivityRepository activityRepository;
    private final ActivityParticipantRepository participantRepository;
    private final ClubRepository clubRepository;
    private final UserRepository userRepository;
    private final ActivityMapper activityMapper;

    @Transactional(readOnly = true)
    public Page<ActivityDto> listActivities(
            Activity.ActivityStatus status,
            Activity.ActivityType type,
            Long clubId,
            Pageable pageable) {
        Page<Activity> activities;
        if (clubId != null) {
            activities = status != null 
                ? activityRepository.findByClubIdAndStatus(clubId, status, pageable)
                : activityRepository.findByClubId(clubId, pageable);
        } else if (status != null) {
            activities = activityRepository.findByStatus(status, pageable);
        } else if (type != null) {
            activities = activityRepository.findByActivityType(type, pageable);
        } else {
            activities = activityRepository.findAll(pageable);
        }
        
        return activities.map(activity -> {
            ActivityDto dto = activityMapper.toDto(activity);
            return enrichWithClubName(dto);
        });
    }

    @Transactional(readOnly = true)
    public ActivityDto getActivity(Long id) {
        Activity activity = activityRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("活动不存在"));
        ActivityDto dto = activityMapper.toDto(activity);
        return enrichWithClubName(dto);
    }

    private ActivityDto enrichWithClubName(ActivityDto dto) {
        if (dto.clubId() != null) {
            clubRepository.findById(dto.clubId())
                    .ifPresent(club -> dto = new ActivityDto(
                            dto.id(), dto.title(), dto.description(),
                            dto.activityType(), dto.status(),
                            dto.startTime(), dto.endTime(), dto.location(),
                            dto.capacity(), dto.currentParticipants(),
                            dto.clubId(), club.getName(),
                            dto.createdBy(), dto.coverImageUrl(),
                            dto.budget(), dto.approvalStatus(), dto.createdAt()
                    ));
        }
        return dto;
    }

    @Transactional
    public ActivityDto createActivity(Long userId, ActivityCreateRequest request) {
        Activity activity = activityMapper.toEntity(request);
        activity.setCreatedBy(userId);
        activity.setStatus(Activity.ActivityStatus.DRAFT);
        activity.setCurrentParticipants(0);
        
        Activity saved = activityRepository.save(activity);
        return activityMapper.toDto(saved);
    }

    @Transactional
    public ActivityDto updateActivity(Long id, ActivityCreateRequest request) {
        Activity activity = activityRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("活动不存在"));
        
        if (activity.getStatus() != Activity.ActivityStatus.DRAFT) {
            throw new IllegalStateException("只有草稿状态的活动可以编辑");
        }
        
        activity.setTitle(request.title());
        activity.setDescription(request.description());
        activity.setActivityType(request.activityType());
        activity.setStartTime(request.startTime());
        activity.setEndTime(request.endTime());
        activity.setLocation(request.location());
        activity.setCapacity(request.capacity());
        activity.setClubId(request.clubId());
        activity.setCoverImageUrl(request.coverImageUrl());
        activity.setBudget(request.budget());
        activity.setRequiredResources(request.requiredResources());
        
        Activity updated = activityRepository.save(activity);
        return activityMapper.toDto(updated);
    }

    @Transactional
    public void deleteActivity(Long id) {
        Activity activity = activityRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("活动不存在"));
        
        if (activity.getStatus() != Activity.ActivityStatus.DRAFT) {
            throw new IllegalStateException("只有草稿状态的活动可以删除");
        }
        
        activity.setDeleted(true);
        activityRepository.save(activity);
    }

    @Transactional
    public void submitForApproval(Long id) {
        Activity activity = activityRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("活动不存在"));
        activity.submitForApproval();
        activityRepository.save(activity);
    }

    @Transactional
    public void registerForActivity(Long activityId, Long userId) {
        Activity activity = activityRepository.findById(activityId)
                .orElseThrow(() -> new RuntimeException("活动不存在"));
        
        if (!activity.canRegister()) {
            throw new IllegalStateException("活动不可报名");
        }
        
        if (participantRepository.existsByActivityIdAndUserId(activityId, userId)) {
            throw new IllegalStateException("您已经报名了该活动");
        }
        
        ActivityParticipant participant = ActivityParticipant.builder()
                .activityId(activityId)
                .userId(userId)
                .status(ActivityParticipant.ParticipationStatus.REGISTERED)
                .build();
        
        participantRepository.save(participant);
        
        // 更新当前参与人数
        activity.setCurrentParticipants(activity.getCurrentParticipants() + 1);
        activityRepository.save(activity);
    }

    @Transactional
    public void cancelRegistration(Long activityId, Long userId) {
        ActivityParticipant participant = participantRepository
                .findByActivityIdAndUserId(activityId, userId)
                .orElseThrow(() -> new RuntimeException("您未报名该活动"));
        
        participant.cancel();
        participantRepository.save(participant);
        
        // 更新当前参与人数
        Activity activity = activityRepository.findById(activityId).orElseThrow();
        activity.setCurrentParticipants(Math.max(0, activity.getCurrentParticipants() - 1));
        activityRepository.save(activity);
    }

    @Transactional
    public void checkIn(Long activityId, Long userId) {
        ActivityParticipant participant = participantRepository
                .findByActivityIdAndUserId(activityId, userId)
                .orElseThrow(() -> new RuntimeException("您未报名该活动"));
        
        participant.checkIn();
        participantRepository.save(participant);
    }

    @Transactional(readOnly = true)
    public List<ActivityParticipantDto> listParticipants(Long activityId) {
        List<ActivityParticipant> participants = participantRepository.findByActivityId(activityId);
        return participants.stream()
                .map(p -> {
                    User user = userRepository.findById(p.getUserId()).orElse(null);
                    return activityMapper.toParticipantDto(p, user);
                })
                .toList();
    }

    @Transactional(readOnly = true)
    public List<ActivityDto> listMyActivities(Long userId) {
        List<ActivityParticipant> registrations = participantRepository.findByUserId(userId);
        return registrations.stream()
                .map(r -> activityRepository.findById(r.getActivityId()).orElse(null))
                .filter(a -> a != null)
                .map(activityMapper::toDto)
                .toList();
    }
}
```

- [ ] **Step 2: Commit**

```bash
git add campus-main/src/main/java/com/campusclub/activity/application/service/ActivityApplicationService.java
git commit -m "feat: add ActivityApplicationService"
```

---

### Task 27: 创建活动Controller

**Files:**
- Create: `campus-main/src/main/java/com/campusclub/activity/interfaces/rest/ActivityController.java`

- [ ] **Step 1: 创建活动Controller**

```java
package com.campusclub.activity.interfaces.rest;

import com.campusclub.activity.application.dto.*;
import com.campusclub.activity.application.service.ActivityApplicationService;
import com.campusclub.activity.domain.entity.Activity;
import com.campusclub.dto.ApiResponse;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/v1/activities")
@RequiredArgsConstructor
@Tag(name = "活动", description = "活动管理相关接口")
public class ActivityController {

    private final ActivityApplicationService activityService;

    @GetMapping
    @Operation(summary = "活动列表", description = "获取活动列表，支持按状态、类型、社团筛选")
    public ResponseEntity<ApiResponse<Page<ActivityDto>>> listActivities(
            @RequestParam(required = false) Activity.ActivityStatus status,
            @RequestParam(required = false) Activity.ActivityType type,
            @RequestParam(required = false) Long clubId,
            Pageable pageable) {
        Page<ActivityDto> activities = activityService.listActivities(status, type, clubId, pageable);
        return ResponseEntity.ok(ApiResponse.success(activities));
    }

    @GetMapping("/{id}")
    @Operation(summary = "活动详情", description = "获取活动详细信息")
    public ResponseEntity<ApiResponse<ActivityDto>> getActivity(@PathVariable Long id) {
        ActivityDto activity = activityService.getActivity(id);
        return ResponseEntity.ok(ApiResponse.success(activity));
    }

    @PostMapping
    @PreAuthorize("hasAnyRole('CLUB_MEMBER', 'CLUB_MANAGER', 'CLUB_PRESIDENT', 'ADMIN', 'SUPER_ADMIN')")
    @SecurityRequirement(name = "bearerAuth")
    @Operation(summary = "创建活动", description = "创建新活动")
    public ResponseEntity<ApiResponse<ActivityDto>> createActivity(
            @AuthenticationPrincipal Long userId,
            @RequestBody @Valid ActivityCreateRequest request) {
        ActivityDto activity = activityService.createActivity(userId, request);
        return ResponseEntity.status(HttpStatus.CREATED).body(ApiResponse.success(activity));
    }

    @PutMapping("/{id}")
    @PreAuthorize("@activitySecurity.isActivityCreator(#id, authentication) or hasAnyRole('ADMIN', 'SUPER_ADMIN')")
    @SecurityRequirement(name = "bearerAuth")
    @Operation(summary = "更新活动", description = "更新活动信息")
    public ResponseEntity<ApiResponse<ActivityDto>> updateActivity(
            @PathVariable Long id,
            @RequestBody @Valid ActivityCreateRequest request) {
        ActivityDto activity = activityService.updateActivity(id, request);
        return ResponseEntity.ok(ApiResponse.success(activity));
    }

    @DeleteMapping("/{id}")
    @PreAuthorize("@activitySecurity.isActivityCreator(#id, authentication) or hasAnyRole('ADMIN', 'SUPER_ADMIN')")
    @SecurityRequirement(name = "bearerAuth")
    @Operation(summary = "删除活动", description = "删除活动")
    public ResponseEntity<ApiResponse<Void>> deleteActivity(@PathVariable Long id) {
        activityService.deleteActivity(id);
        return ResponseEntity.ok(ApiResponse.success(null));
    }

    @PostMapping("/{id}/submit")
    @PreAuthorize("@activitySecurity.isActivityCreator(#id, authentication)")
    @SecurityRequirement(name = "bearerAuth")
    @Operation(summary = "提交审批", description = "提交活动审批")
    public ResponseEntity<ApiResponse<Void>> submitForApproval(@PathVariable Long id) {
        activityService.submitForApproval(id);
        return ResponseEntity.ok(ApiResponse.success(null));
    }

    @PostMapping("/{id}/register")
    @SecurityRequirement(name = "bearerAuth")
    @Operation(summary = "报名活动", description = "报名参加活动")
    public ResponseEntity<ApiResponse<Void>> registerForActivity(
            @PathVariable Long id,
            @AuthenticationPrincipal Long userId) {
        activityService.registerForActivity(id, userId);
        return ResponseEntity.status(HttpStatus.CREATED).body(ApiResponse.success(null));
    }

    @PostMapping("/{id}/cancel")
    @SecurityRequirement(name = "bearerAuth")
    @Operation(summary = "取消报名", description = "取消活动报名")
    public ResponseEntity<ApiResponse<Void>> cancelRegistration(
            @PathVariable Long id,
            @AuthenticationPrincipal Long userId) {
        activityService.cancelRegistration(id, userId);
        return ResponseEntity.ok(ApiResponse.success(null));
    }

    @PostMapping("/{id}/check-in")
    @SecurityRequirement(name = "bearerAuth")
    @Operation(summary = "活动签到", description = "活动签到")
    public ResponseEntity<ApiResponse<Void>> checkIn(
            @PathVariable Long id,
            @AuthenticationPrincipal Long userId) {
        activityService.checkIn(id, userId);
        return ResponseEntity.ok(ApiResponse.success(null));
    }

    @GetMapping("/{id}/participants")
    @PreAuthorize("@activitySecurity.isActivityCreator(#id, authentication) or hasAnyRole('ADMIN', 'SUPER_ADMIN')")
    @SecurityRequirement(name = "bearerAuth")
    @Operation(summary = "参与者列表", description = "获取活动参与者列表")
    public ResponseEntity<ApiResponse<List<ActivityParticipantDto>>> listParticipants(
            @PathVariable Long id) {
        List<ActivityParticipantDto> participants = activityService.listParticipants(id);
        return ResponseEntity.ok(ApiResponse.success(participants));
    }

    @GetMapping("/my")
    @SecurityRequirement(name = "bearerAuth")
    @Operation(summary = "我的活动", description = "获取我报名的活动列表")
    public ResponseEntity<ApiResponse<List<ActivityDto>>> listMyActivities(
            @AuthenticationPrincipal Long userId) {
        List<ActivityDto> activities = activityService.listMyActivities(userId);
        return ResponseEntity.ok(ApiResponse.success(activities));
    }
}
```

- [ ] **Step 2: Commit**

```bash
git add campus-main/src/main/java/com/campusclub/activity/interfaces/rest/ActivityController.java
git commit -m "feat: add ActivityController"
```

---

## 第五阶段：JWT工具类实现

### Task 28: 创建JWT工具类

**Files:**
- Create: `campus-main/src/main/java/com/campusclub/common/util/JwtUtil.java`

- [ ] **Step 1: 创建JWT配置属性**

```java
package com.campusclub.common.util;

import lombok.Data;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.stereotype.Component;

@Data
@Component
@ConfigurationProperties(prefix = "jwt")
public class JwtProperties {
    private String secret;
    private long accessTokenExpiration = 7200000; // 2小时
    private long refreshTokenExpiration = 604800000; // 7天
}
```

- [ ] **Step 2: 创建JWT工具类**

```java
package com.campusclub.common.util;

import io.jsonwebtoken.*;
import io.jsonwebtoken.security.Keys;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

import javax.crypto.SecretKey;
import java.nio.charset.StandardCharsets;
import java.util.Date;

@Slf4j
@Component
@RequiredArgsConstructor
public class JwtUtil {

    private final JwtProperties jwtProperties;

    private SecretKey getSigningKey() {
        return Keys.hmacShaKeyFor(jwtProperties.getSecret().getBytes(StandardCharsets.UTF_8));
    }

    public String generateAccessToken(Long userId, String role) {
        Date now = new Date();
        Date expiry = new Date(now.getTime() + jwtProperties.getAccessTokenExpiration());

        return Jwts.builder()
                .subject(userId.toString())
                .claim("role", role)
                .claim("type", "access")
                .issuedAt(now)
                .expiration(expiry)
                .signWith(getSigningKey())
                .compact();
    }

    public String generateRefreshToken(Long userId) {
        Date now = new Date();
        Date expiry = new Date(now.getTime() + jwtProperties.getRefreshTokenExpiration());

        return Jwts.builder()
                .subject(userId.toString())
                .claim("type", "refresh")
                .issuedAt(now)
                .expiration(expiry)
                .signWith(getSigningKey())
                .compact();
    }

    public boolean validateToken(String token) {
        try {
            Jwts.parser()
                    .verifyWith(getSigningKey())
                    .build()
                    .parseSignedClaims(token);
            return true;
        } catch (ExpiredJwtException e) {
            log.warn("JWT token is expired: {}", e.getMessage());
        } catch (UnsupportedJwtException e) {
            log.warn("JWT token is unsupported: {}", e.getMessage());
        } catch (MalformedJwtException e) {
            log.warn("JWT token is malformed: {}", e.getMessage());
        } catch (SecurityException e) {
            log.warn("JWT signature validation failed: {}", e.getMessage());
        } catch (IllegalArgumentException e) {
            log.warn("JWT token is empty or null: {}", e.getMessage());
        }
        return false;
    }

    public Long getUserIdFromToken(String token) {
        Claims claims = Jwts.parser()
                .verifyWith(getSigningKey())
                .build()
                .parseSignedClaims(token)
                .getPayload();
        return Long.valueOf(claims.getSubject());
    }

    public String getRoleFromToken(String token) {
        Claims claims = Jwts.parser()
                .verifyWith(getSigningKey())
                .build()
                .parseSignedClaims(token)
                .getPayload();
        return claims.get("role", String.class);
    }

    public long getAccessTokenExpiration() {
        return jwtProperties.getAccessTokenExpiration() / 1000; // 返回秒数
    }
}
```

- [ ] **Step 3: Commit**

```bash
git add campus-main/src/main/java/com/campusclub/common/util/JwtUtil.java
git add campus-main/src/main/java/com/campusclub/common/util/JwtProperties.java
git commit -m "feat: add JWT utility class"
```

---

## 第六阶段：Spring Security配置更新

### Task 29: 更新Security配置

**Files:**
- Modify: `campus-main/src/main/java/com/campusclub/config/SecurityConfig.java`

- [ ] **Step 1: 创建JWT认证过滤器**

```java
package com.campusclub.common.security;

import com.campusclub.common.util.JwtUtil;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;
import java.util.Collections;

@Component
@RequiredArgsConstructor
public class JwtAuthenticationFilter extends OncePerRequestFilter {

    private final JwtUtil jwtUtil;

    @Override
    protected void doFilterInternal(HttpServletRequest request, 
                                     HttpServletResponse response, 
                                     FilterChain filterChain) throws ServletException, IOException {
        String authHeader = request.getHeader("Authorization");
        
        if (authHeader != null && authHeader.startsWith("Bearer ")) {
            String token = authHeader.substring(7);
            
            if (jwtUtil.validateToken(token)) {
                Long userId = jwtUtil.getUserIdFromToken(token);
                String role = jwtUtil.getRoleFromToken(token);
                
                UsernamePasswordAuthenticationToken authentication =
                        new UsernamePasswordAuthenticationToken(
                                userId, null, 
                                Collections.singletonList(() -> "ROLE_" + role)
                        );
                
                SecurityContextHolder.getContext().setAuthentication(authentication);
            }
        }
        
        filterChain.doFilter(request, response);
    }
}
```

- [ ] **Step 2: 更新Security配置**

```java
package com.campusclub.config;

import com.campusclub.common.security.JwtAuthenticationFilter;
import lombok.RequiredArgsConstructor;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.HttpMethod;
import org.springframework.security.config.annotation.method.configuration.EnableMethodSecurity;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.cors.CorsConfigurationSource;
import org.springframework.web.cors.UrlBasedCorsConfigurationSource;

import java.util.Arrays;
import java.util.List;

@Configuration
@EnableWebSecurity
@EnableMethodSecurity(prePostEnabled = true)
@RequiredArgsConstructor
public class SecurityConfig {

    private final JwtAuthenticationFilter jwtAuthenticationFilter;

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        http
            .csrf(csrf -> csrf.disable())
            .cors(cors -> cors.configurationSource(corsConfigurationSource()))
            .sessionManagement(session ->
                session.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            .authorizeHttpRequests(auth -> auth
                // 公开访问的接口
                .requestMatchers(
                    "/api/v1/auth/**",
                    "/api/public/**",
                    "/actuator/health",
                    "/v3/api-docs/**",
                    "/swagger-ui/**",
                    "/swagger-ui.html"
                ).permitAll()
                // GET请求活动列表公开访问
                .requestMatchers(HttpMethod.GET, "/api/v1/activities").permitAll()
                .requestMatchers(HttpMethod.GET, "/api/v1/activities/{id}").permitAll()
                // GET请求社团列表公开访问
                .requestMatchers(HttpMethod.GET, "/api/v1/clubs").permitAll()
                .requestMatchers(HttpMethod.GET, "/api/v1/clubs/{id}").permitAll()
                // 需要认证的接口
                .anyRequest().authenticated()
            )
            .addFilterBefore(jwtAuthenticationFilter, UsernamePasswordAuthenticationFilter.class);

        return http.build();
    }

    @Bean
    public CorsConfigurationSource corsConfigurationSource() {
        CorsConfiguration configuration = new CorsConfiguration();
        configuration.setAllowedOrigins(List.of(
            "http://localhost:3000",
            "http://localhost:5173",
            "http://localhost:8081"
        ));
        configuration.setAllowedMethods(Arrays.asList("GET", "POST", "PUT", "DELETE", "OPTIONS"));
        configuration.setAllowedHeaders(Arrays.asList("*"));
        configuration.setAllowCredentials(true);
        configuration.setMaxAge(3600L);

        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/**", configuration);
        return source;
    }

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }
}
```

- [ ] **Step 3: Commit**

```bash
git add campus-main/src/main/java/com/campusclub/common/security/JwtAuthenticationFilter.java
git add campus-main/src/main/java/com/campusclub/config/SecurityConfig.java
git commit -m "feat: add JWT authentication filter and update security config"
```

---

## 第七阶段：应用配置更新

### Task 30: 更新application.yml配置

**Files:**
- Modify: `campus-main/src/main/resources/application.yml`

- [ ] **Step 1: 更新应用配置**

```yaml
spring:
  application:
    name: campus-club-backend
  
  datasource:
    url: jdbc:postgresql://${DB_HOST:localhost}:${DB_PORT:5432}/${DB_NAME:campus_club}
    username: ${DB_USER:campus_user}
    password: ${DB_PASSWORD:campus_pass}
    driver-class-name: org.postgresql.Driver
  
  jpa:
    hibernate:
      ddl-auto: validate
    properties:
      hibernate:
        dialect: org.hibernate.dialect.PostgreSQLDialect
        format_sql: true
    show-sql: ${JPA_SHOW_SQL:false}
  
  flyway:
    enabled: true
    locations: classpath:db/migration
    baseline-on-migrate: true
  
  redis:
    host: ${REDIS_HOST:localhost}
    port: ${REDIS_PORT:6379}
    password: ${REDIS_PASSWORD:}
    timeout: 2000ms
    lettuce:
      pool:
        max-active: 8
        max-idle: 8
        min-idle: 0
  
  servlet:
    multipart:
      max-file-size: 10MB
      max-request-size: 50MB

# JWT配置
jwt:
  secret: ${JWT_SECRET:your-secret-key-change-in-production-minimum-256-bits}
  access-token-expiration: 7200000  # 2小时
  refresh-token-expiration: 604800000  # 7天

# 微信配置
wechat:
  mp:
    app-id: ${WECHAT_APP_ID:}
    secret: ${WECHAT_SECRET:}

# 算法服务配置
algorithm:
  service:
    url: ${ALGORITHM_SERVICE_URL:http://localhost:8000}
  timeout:
    seconds: 30
  retry:
    count: 3
  cache:
    ttl:
      standard: 600
      medium: 1800
      extended: 3600

# 日志配置
logging:
  level:
    com.campusclub: INFO
    org.springframework.security: DEBUG
  pattern:
    console: "%d{yyyy-MM-dd HH:mm:ss} [%thread] %-5level %logger{36} - %msg%n"

# SpringDoc配置
springdoc:
  api-docs:
    path: /v3/api-docs
  swagger-ui:
    path: /swagger-ui.html
  openapi:
    info:
      title: Campus Club API
      version: 1.0.0
      description: 校园社团活动评估系统API
```

- [ ] **Step 2: Commit**

```bash
git add campus-main/src/main/resources/application.yml
git commit -m "feat: update application.yml with complete configuration"
```

---

## 第八阶段：编译验证

### Task 31: 编译验证项目

**Files:**
- All modified files

- [ ] **Step 1: 编译项目**

Run: `cd campus-main && mvn clean compile`

Expected: BUILD SUCCESS

- [ ] **Step 2: 运行测试**

Run: `cd campus-main && mvn test`

Expected: Tests pass (or no tests if not created yet)

- [ ] **Step 3: Commit any fixes**

If there are compilation errors, fix them and commit:

```bash
git add -A
git commit -m "fix: resolve compilation errors"
```

---

## 任务汇总

| 阶段 | 任务数 | 描述 |
|------|--------|------|
| 第一阶段 | 6 | 数据库迁移脚本 |
| 第二阶段 | 9 | 用户模块实现 |
| 第三阶段 | 6 | 社团模块实现 |
| 第四阶段 | 6 | 活动模块实现 |
| 第五阶段 | 1 | JWT工具类 |
| 第六阶段 | 1 | Security配置更新 |
| 第七阶段 | 1 | 应用配置更新 |
| 第八阶段 | 1 | 编译验证 |
| **合计** | **31** | |

---

## 后续阶段（预留）

以下模块将在后续计划中实现：

### 资源模块 (P1)
- Resource实体与Repository
- ResourceReservation实体与Repository  
- ResourceService与Controller
- 预约冲突检测逻辑

### 评估模块 (P1)
- Evaluation实体与Repository
- ActivityFeedback实体与Repository
- 算法集成Service
- EvaluationService与Controller

### 审批模块 (P2)
- ApprovalRecord实体与Repository
- ApprovalService与Controller
- 审批工作流逻辑

---

*计划版本：1.0*
*创建日期：2026-04-14*
*状态：准备执行*
