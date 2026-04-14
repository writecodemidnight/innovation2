# 校园社团活动评估系统 - 后端业务开发设计文档

## 文档信息

| 项目 | 内容 |
|------|------|
| 文档版本 | 1.0 |
| 编写日期 | 2026-04-14 |
| 文档状态 | 正式开发版 |
| 编写者 | Claude Code |

---

## 一、项目概述

### 1.1 项目背景
基于大数据分析的校园社团活动效果评估与资源优化配置系统，后端采用Spring Boot 3.2.x + Java 21架构，需要完成核心业务模块的开发。

### 1.2 开发目标
完成后端六大业务模块的全部功能开发，实现与前端三端（学生端、社团端、管理端）的完整API对接。

### 1.3 当前状态

| 模块 | 状态 | 完成度 | 说明 |
|------|------|--------|------|
| 基础框架 | ✅ 已完成 | 100% | Spring Boot、Security、JPA、Redis |
| 算法服务 | ✅ 已完成 | 100% | Python FastAPI + 7大算法 |
| 数据库表 | 🔄 待创建 | 0% | 需要Flyway迁移脚本 |
| 业务模块 | 🔄 待开发 | 0% | 用户、社团、活动、资源、评估、审批 |
| API接口 | 🔄 待开发 | 0% | RESTful API |

---

## 二、架构设计

### 2.1 整体架构

采用**领域驱动设计（DDD）** + **分层架构**，按业务领域划分模块，每个模块内部采用分层结构。

```
┌─────────────────────────────────────────────────────────────────────┐
│                         接口层 (Interfaces)                          │
│  ┌──────────┬──────────┬──────────┬──────────┬──────────┐          │
│  │ REST API │   DTO    │  Mapper  │  校验器   │ 文档注解 │          │
│  └──────────┴──────────┴──────────┴──────────┴──────────┘          │
├─────────────────────────────────────────────────────────────────────┤
│                       应用层 (Application)                           │
│  ┌──────────────┬──────────────┬──────────────┬──────────────┐     │
│  │   Service    │ 事务管理     │  用例编排    │  事件发布    │     │
│  └──────────────┴──────────────┴──────────────┴──────────────┘     │
├─────────────────────────────────────────────────────────────────────┤
│                        领域层 (Domain)                               │
│  ┌──────────┬──────────┬──────────┬──────────┬──────────┐          │
│  │  Entity  │   VO     │ Repository│ DomainService │ 事件 │          │
│  └──────────┴──────────┴──────────┴──────────┴──────────┘          │
├─────────────────────────────────────────────────────────────────────┤
│                      基础设施层 (Infrastructure)                      │
│  ┌──────────┬──────────┬──────────┬──────────┬──────────┐          │
│  │ JPA实现  │  Redis   │  外部API  │  文件存储  │  消息队列 │          │
│  └──────────┴──────────┴──────────┴──────────┴──────────┘          │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2 模块划分

```
campus-main/src/main/java/com/campusclub/
├── CampusClubApplication.java          # 应用入口
├── common/                             # 通用基础设施
│   ├── config/                         # 全局配置（已存在）
│   ├── exception/                      # 全局异常（已存在）
│   ├── model/                          # 基础实体（已存在）
│   └── util/                           # 通用工具
│
├── user/                               # 用户模块 (P0)
│   ├── domain/
│   │   ├── entity/User.java
│   │   ├── entity/ClubMember.java
│   │   ├── repository/UserRepository.java
│   │   └── service/WechatAuthDomainService.java
│   ├── application/
│   │   ├── service/UserApplicationService.java
│   │   ├── dto/UserDto.java
│   │   └── mapper/UserMapper.java
│   ├── infrastructure/
│   │   ├── persistence/UserJpaRepository.java
│   │   └── external/WechatMpClient.java
│   └── interfaces/
│       ├── rest/AuthController.java
│       └── rest/UserController.java
│
├── club/                               # 社团模块 (P0)
│   ├── domain/
│   │   ├── entity/Club.java
│   │   ├── entity/ClubAnnouncement.java
│   │   └── repository/ClubRepository.java
│   ├── application/
│   │   ├── service/ClubApplicationService.java
│   │   └── dto/ClubDto.java
│   └── interfaces/
│       └── rest/ClubController.java
│
├── activity/                           # 活动模块 (P0)
│   ├── domain/
│   │   ├── entity/Activity.java
│   │   ├── entity/ActivityParticipant.java
│   │   ├── enums/ActivityStatus.java
│   │   ├── enums/ActivityType.java
│   │   ├── service/ActivityDomainService.java
│   │   └── repository/ActivityRepository.java
│   ├── application/
│   │   ├── service/ActivityApplicationService.java
│   │   ├── dto/ActivityDto.java
│   │   ├── dto/ActivityCreateRequest.java
│   │   └── event/ActivityCreatedEvent.java
│   └── interfaces/
│       └── rest/ActivityController.java
│
├── resource/                           # 资源模块 (P1)
│   ├── domain/
│   │   ├── entity/Resource.java
│   │   ├── entity/ResourceReservation.java
│   │   ├── enums/ResourceType.java
│   │   └── repository/ResourceRepository.java
│   ├── application/
│   │   ├── service/ResourceApplicationService.java
│   │   └── dto/ResourceDto.java
│   └── interfaces/
│       └── rest/ResourceController.java
│
├── evaluation/                         # 评估模块 (P1)
│   ├── domain/
│   │   ├── entity/Evaluation.java
│   │   ├── entity/EvaluationMetrics.java
│   │   ├── valueobject/FiveDimensions.java
│   │   └── repository/EvaluationRepository.java
│   ├── application/
│   │   ├── service/EvaluationApplicationService.java
│   │   ├── service/AlgorithmIntegrationService.java
│   │   └── dto/EvaluationDto.java
│   └── interfaces/
│       └── rest/EvaluationController.java
│
└── approval/                           # 审批模块 (P2)
    ├── domain/
    │   ├── entity/ApprovalRecord.java
    │   ├── enums/ApprovalStatus.java
    │   └── repository/ApprovalRecordRepository.java
    ├── application/
    │   └── service/ApprovalApplicationService.java
    └── interfaces/
        └── rest/ApprovalController.java
```

---

## 三、技术选型

### 3.1 已集成组件

| 组件 | 版本 | 用途 | 状态 |
|------|------|------|------|
| Spring Boot | 3.2.5 | 核心框架 | ✅ 已集成 |
| Spring Data JPA | 3.2.5 | ORM框架 | ✅ 已集成 |
| Spring Security | 3.2.5 | 安全认证 | ✅ 已集成 |
| Redis | 3.2.5 | 缓存 | ✅ 已集成 |
| JWT (jjwt) | 0.12.3 | Token认证 | ✅ 已集成 |
| 微信SDK | 4.5.0 | 微信登录 | ✅ 已集成 |
| MapStruct | 1.5.5 | DTO转换 | ✅ 已集成 |
| Lombok | 1.18.36 | 代码简化 | ✅ 已集成 |
| Flyway | 10.x | 数据库迁移 | ✅ 已集成 |
| SpringDoc | 2.5.0 | API文档 | ✅ 已集成 |
| PostgreSQL Driver | 15.x | 数据库驱动 | ✅ 已集成 |

### 3.2 API设计规范

**基础路径**: `/api/v1`

**响应格式**:
```json
{
  "code": "SUCCESS",
  "message": "操作成功",
  "data": { }
}
```

**错误码规范**:
| 错误码 | 含义 | HTTP状态码 |
|--------|------|------------|
| SUCCESS | 成功 | 200 |
| BAD_REQUEST | 请求参数错误 | 400 |
| UNAUTHORIZED | 未认证 | 401 |
| FORBIDDEN | 无权限 | 403 |
| NOT_FOUND | 资源不存在 | 404 |
| VALIDATION_ERROR | 数据校验失败 | 422 |
| INTERNAL_ERROR | 服务器内部错误 | 500 |
| ALGORITHM_ERROR | 算法服务错误 | 502 |

---

## 四、数据库设计

### 4.1 Flyway迁移脚本规划

```
campus-main/src/main/resources/
└── db/migration/
    ├── V1__create_users_table.sql           # 用户表
    ├── V2__create_clubs_table.sql           # 社团表
    ├── V3__create_activities_table.sql      # 活动表
    ├── V4__create_resources_table.sql       # 资源表
    ├── V5__create_evaluations_table.sql     # 评估表
    └── V6__create_approvals_table.sql       # 审批表
```

### 4.2 核心表结构

#### 4.2.1 用户表 (users)

```sql
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    openid VARCHAR(100) UNIQUE COMMENT '微信OpenID',
    student_id VARCHAR(50) UNIQUE COMMENT '学号',
    username VARCHAR(50) NOT NULL COMMENT '用户名',
    nickname VARCHAR(50) COMMENT '昵称',
    avatar_url VARCHAR(500) COMMENT '头像URL',
    phone VARCHAR(20) COMMENT '手机号',
    email VARCHAR(100) COMMENT '邮箱',
    role VARCHAR(20) NOT NULL DEFAULT 'STUDENT' COMMENT '角色: STUDENT, CLUB_MEMBER, CLUB_PRESIDENT, ADMIN, SUPER_ADMIN',
    status VARCHAR(20) DEFAULT 'ACTIVE' COMMENT '状态: ACTIVE, INACTIVE',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    deleted BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_users_openid ON users(openid);
CREATE INDEX idx_users_student_id ON users(student_id);
```

#### 4.2.2 社团表 (clubs)

```sql
CREATE TABLE clubs (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL COMMENT '社团名称',
    code VARCHAR(50) UNIQUE COMMENT '社团代码',
    description TEXT COMMENT '社团描述',
    category VARCHAR(50) COMMENT '类别: ACADEMIC, ARTS, SPORTS, VOLUNTEER',
    logo_url VARCHAR(500) COMMENT '社团Logo',
    president_id BIGINT REFERENCES users(id) COMMENT '社长ID',
    faculty_advisor VARCHAR(100) COMMENT '指导老师',
    status VARCHAR(20) DEFAULT 'ACTIVE' COMMENT '状态: ACTIVE, INACTIVE, SUSPENDED',
    member_count INT DEFAULT 0 COMMENT '成员数',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    deleted BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_clubs_category ON clubs(category);
CREATE INDEX idx_clubs_status ON clubs(status);
```

#### 4.2.3 社团成员表 (club_members)

```sql
CREATE TABLE club_members (
    id BIGSERIAL PRIMARY KEY,
    club_id BIGINT NOT NULL REFERENCES clubs(id),
    user_id BIGINT NOT NULL REFERENCES users(id),
    role VARCHAR(20) DEFAULT 'MEMBER' COMMENT '角色: MEMBER, MANAGER, PRESIDENT',
    joined_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(club_id, user_id)
);

CREATE INDEX idx_club_members_club_id ON club_members(club_id);
CREATE INDEX idx_club_members_user_id ON club_members(user_id);
```

#### 4.2.4 活动表 (activities)

```sql
CREATE TABLE activities (
    id BIGSERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL COMMENT '活动标题',
    description TEXT COMMENT '活动描述',
    activity_type VARCHAR(50) NOT NULL COMMENT '类型: LECTURE, WORKSHOP, COMPETITION, SOCIAL, VOLUNTEER',
    status VARCHAR(20) DEFAULT 'DRAFT' COMMENT '状态: DRAFT, PENDING, APPROVED, REJECTED, REGISTERING, ONGOING, COMPLETED, CANCELLED',
    start_time TIMESTAMP NOT NULL COMMENT '开始时间',
    end_time TIMESTAMP NOT NULL COMMENT '结束时间',
    location VARCHAR(200) COMMENT '活动地点',
    capacity INT COMMENT '容量限制',
    current_participants INT DEFAULT 0 COMMENT '当前参与人数',
    club_id BIGINT REFERENCES clubs(id) COMMENT '所属社团',
    created_by BIGINT REFERENCES users(id) COMMENT '创建人',
    cover_image_url VARCHAR(500) COMMENT '封面图片',
    budget DECIMAL(10,2) COMMENT '预算',
    required_resources JSONB COMMENT '所需资源JSON',
    approval_status VARCHAR(20) DEFAULT 'NONE' COMMENT '审批状态',
    approval_comment TEXT COMMENT '审批意见',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    deleted BOOLEAN DEFAULT FALSE,
    CHECK (end_time > start_time)
);

CREATE INDEX idx_activities_status ON activities(status);
CREATE INDEX idx_activities_club_id ON activities(club_id);
CREATE INDEX idx_activities_start_time ON activities(start_time);
CREATE INDEX idx_activities_type ON activities(activity_type);
```

#### 4.2.5 活动参与者表 (activity_participants)

```sql
CREATE TABLE activity_participants (
    id BIGSERIAL PRIMARY KEY,
    activity_id BIGINT NOT NULL REFERENCES activities(id),
    user_id BIGINT NOT NULL REFERENCES users(id),
    status VARCHAR(20) DEFAULT 'REGISTERED' COMMENT '状态: REGISTERED, CHECKED_IN, CANCELLED, NO_SHOW',
    registered_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    checked_in_at TIMESTAMP COMMENT '签到时间',
    UNIQUE(activity_id, user_id)
);

CREATE INDEX idx_participants_activity_id ON activity_participants(activity_id);
CREATE INDEX idx_participants_user_id ON activity_participants(user_id);
```

#### 4.2.6 资源表 (resources)

```sql
CREATE TABLE resources (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL COMMENT '资源名称',
    resource_type VARCHAR(50) NOT NULL COMMENT '类型: VENUE, EQUIPMENT, BUDGET',
    description TEXT COMMENT '资源描述',
    capacity INT COMMENT '容量（人数/数量）',
    available_count INT DEFAULT 0 COMMENT '可用数量',
    total_count INT NOT NULL COMMENT '总数量',
    unit VARCHAR(20) COMMENT '单位',
    location VARCHAR(200) COMMENT '位置',
    manager_id BIGINT REFERENCES users(id) COMMENT '管理员',
    constraints JSONB COMMENT '约束条件JSON',
    status VARCHAR(20) DEFAULT 'AVAILABLE' COMMENT '状态',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    deleted BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_resources_type ON resources(resource_type);
CREATE INDEX idx_resources_status ON resources(status);
```

#### 4.2.7 资源预约表 (resource_reservations)

```sql
CREATE TABLE resource_reservations (
    id BIGSERIAL PRIMARY KEY,
    resource_id BIGINT NOT NULL REFERENCES resources(id),
    activity_id BIGINT REFERENCES activities(id),
    applicant_id BIGINT NOT NULL REFERENCES users(id),
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    quantity INT DEFAULT 1 COMMENT '申请数量',
    status VARCHAR(20) DEFAULT 'PENDING' COMMENT '状态: PENDING, APPROVED, REJECTED, CANCELLED',
    purpose TEXT COMMENT '用途说明',
    approval_comment TEXT COMMENT '审批意见',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    CHECK (end_time > start_time)
);

CREATE INDEX idx_reservations_resource_id ON resource_reservations(resource_id);
CREATE INDEX idx_reservations_activity_id ON resource_reservations(activity_id);
CREATE INDEX idx_reservations_time_range ON resource_reservations(start_time, end_time);
```

#### 4.2.8 评估表 (evaluations)

```sql
CREATE TABLE evaluations (
    id BIGSERIAL PRIMARY KEY,
    activity_id BIGINT NOT NULL UNIQUE REFERENCES activities(id),
    participant_count INT COMMENT '参与人数',
    satisfaction_score DECIMAL(3,2) COMMENT '满意度分数 0-5',
    participation_score DECIMAL(5,2) COMMENT '参与度 0-100',
    educational_score DECIMAL(5,2) COMMENT '教育性 0-100',
    innovation_score DECIMAL(5,2) COMMENT '创新性 0-100',
    influence_score DECIMAL(5,2) COMMENT '影响力 0-100',
    sustainability_score DECIMAL(5,2) COMMENT '可持续性 0-100',
    overall_score DECIMAL(5,2) COMMENT '综合得分',
    algorithm_version VARCHAR(50) COMMENT '算法版本',
    radar_chart_data JSONB COMMENT '雷达图数据',
    generated_at TIMESTAMP COMMENT '生成时间',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE INDEX idx_evaluations_activity_id ON evaluations(activity_id);
```

#### 4.2.9 评价反馈表 (activity_feedbacks)

```sql
CREATE TABLE activity_feedbacks (
    id BIGSERIAL PRIMARY KEY,
    activity_id BIGINT NOT NULL REFERENCES activities(id),
    user_id BIGINT NOT NULL REFERENCES users(id),
    rating INT NOT NULL CHECK (rating >= 1 AND rating <= 5) COMMENT '星级 1-5',
    content TEXT COMMENT '文字评价',
    sentiment_score DECIMAL(3,2) COMMENT '情感分析分数 -1~1',
    photos JSONB COMMENT '照片URL数组',
    is_anonymous BOOLEAN DEFAULT FALSE COMMENT '是否匿名',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(activity_id, user_id)
);

CREATE INDEX idx_feedbacks_activity_id ON activity_feedbacks(activity_id);
CREATE INDEX idx_feedbacks_user_id ON activity_feedbacks(user_id);
```

#### 4.2.10 审批记录表 (approval_records)

```sql
CREATE TABLE approval_records (
    id BIGSERIAL PRIMARY KEY,
    target_type VARCHAR(50) NOT NULL COMMENT '审批对象类型: ACTIVITY, RESOURCE',
    target_id BIGINT NOT NULL COMMENT '审批对象ID',
    applicant_id BIGINT NOT NULL REFERENCES users(id) COMMENT '申请人',
    approver_id BIGINT REFERENCES users(id) COMMENT '审批人',
    status VARCHAR(20) NOT NULL COMMENT '状态: PENDING, APPROVED, REJECTED',
    submit_data JSONB COMMENT '提交的数据',
    comment TEXT COMMENT '审批意见',
    submitted_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP COMMENT '处理时间',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_approvals_target ON approval_records(target_type, target_id);
CREATE INDEX idx_approvals_status ON approval_records(status);
CREATE INDEX idx_approvals_applicant ON approval_records(applicant_id);
```

---

## 五、API接口设计

### 5.1 用户认证模块 (/api/v1/auth)

| 方法 | 路径 | 描述 | 权限 |
|------|------|------|------|
| POST | /auth/wechat-login | 微信登录 | 公开 |
| POST | /auth/refresh | 刷新Token | 已登录 |
| POST | /auth/logout | 退出登录 | 已登录 |

**微信登录请求/响应**:
```java
// 请求
public record WechatLoginRequest(
    @NotBlank String code,           // 微信临时登录凭证
    String userInfo                  // 可选：用户信息加密数据
) {}

// 响应
public record LoginResponse(
    String accessToken,              // JWT访问令牌
    String refreshToken,             // 刷新令牌
    Long expiresIn,                  // 过期时间（秒）
    UserDto user                     // 用户信息
) {}
```

### 5.2 用户模块 (/api/v1/users)

| 方法 | 路径 | 描述 | 权限 |
|------|------|------|------|
| GET | /users/me | 获取当前用户 | 已登录 |
| PUT | /users/me | 更新用户信息 | 已登录 |
| GET | /users/me/activities | 我的活动列表 | 已登录 |
| GET | /users/me/participation-stats | 参与统计 | 已登录 |

### 5.3 社团模块 (/api/v1/clubs)

| 方法 | 路径 | 描述 | 权限 |
|------|------|------|------|
| GET | /clubs | 社团列表 | 公开 |
| GET | /clubs/{id} | 社团详情 | 公开 |
| POST | /clubs | 创建社团 | ADMIN+ |
| PUT | /clubs/{id} | 更新社团 | 社长/ADMIN |
| POST | /clubs/{id}/members | 添加成员 | 社长/MANAGER |
| DELETE | /clubs/{id}/members/{userId} | 移除成员 | 社长/MANAGER |
| GET | /clubs/{id}/activities | 社团活动列表 | 公开 |
| GET | /clubs/{id}/members | 成员列表 | 已登录 |

### 5.4 活动模块 (/api/v1/activities)

| 方法 | 路径 | 描述 | 权限 |
|------|------|------|------|
| GET | /activities | 活动列表（支持筛选） | 公开 |
| GET | /activities/{id} | 活动详情 | 公开 |
| POST | /activities | 创建活动 | CLUB_MEMBER+ |
| PUT | /activities/{id} | 更新活动 | 创建者/MANAGER+ |
| DELETE | /activities/{id} | 删除活动 | 创建者/MANAGER+ |
| POST | /activities/{id}/submit | 提交审批 | 创建者 |
| POST | /activities/{id}/register | 报名活动 | 已登录 |
| POST | /activities/{id}/cancel | 取消报名 | 已登录 |
| POST | /activities/{id}/check-in | 活动签到 | 已登录 |
| POST | /activities/{id}/feedback | 提交评价 | 已报名 |
| GET | /activities/{id}/participants | 参与者列表 | MANAGER+ |
| GET | /activities/{id}/feedbacks | 评价列表 | MANAGER+ |
| GET | /activities/recommended | 推荐活动 | 已登录 |

**活动创建请求**:
```java
public record ActivityCreateRequest(
    @NotBlank @Size(max = 200) String title,
    String description,
    @NotNull ActivityType activityType,
    @NotNull @Future LocalDateTime startTime,
    @NotNull @Future LocalDateTime endTime,
    String location,
    @Min(1) Integer capacity,
    Long clubId,
    String coverImageUrl,
    BigDecimal budget,
    List<ResourceRequirement> requiredResources
) {}
```

### 5.5 资源模块 (/api/v1/resources)

| 方法 | 路径 | 描述 | 权限 |
|------|------|------|------|
| GET | /resources | 资源列表（支持筛选） | 已登录 |
| GET | /resources/{id} | 资源详情 | 已登录 |
| POST | /resources | 创建资源 | ADMIN+ |
| PUT | /resources/{id} | 更新资源 | ADMIN+ |
| GET | /resources/{id}/calendar | 资源日历（占用情况） | 已登录 |
| POST | /resources/{id}/reserve | 预约资源 | CLUB_MEMBER+ |
| GET | /resources/reservations | 我的预约列表 | 已登录 |
| POST | /resources/reservations/{id}/cancel | 取消预约 | 申请人 |

### 5.6 评估模块 (/api/v1/evaluations)

| 方法 | 路径 | 描述 | 权限 |
|------|------|------|------|
| GET | /evaluations/activities/{activityId} | 活动评估报告 | MANAGER+ |
| POST | /evaluations/activities/{activityId}/generate | 生成评估报告 | MANAGER+ |
| GET | /evaluations/clubs/{clubId}/overview | 社团评估概览 | 社长+ |
| GET | /evaluations/dashboard | 全局评估数据 | ADMIN+ |

**评估报告响应**:
```java
public record EvaluationReportDto(
    Long activityId,
    String activityTitle,
    FiveDimensionsDto scores,        // 五维得分
    Double overallScore,             // 综合得分
    RadarChartDto radarChart,        // 雷达图数据
    List<FeedbackSummaryDto> feedbacks, // 反馈汇总
    String algorithmVersion,
    LocalDateTime generatedAt
) {}

public record FiveDimensionsDto(
    Double participation,    // 参与度
    Double educational,      // 教育性
    Double innovation,       // 创新性
    Double influence,        // 影响力
    Double sustainability    // 可持续性
) {}
```

### 5.7 审批模块 (/api/v1/approvals)

| 方法 | 路径 | 描述 | 权限 |
|------|------|------|------|
| GET | /approvals/pending | 待审批列表 | ADMIN+ |
| GET | /approvals/my | 我的申请列表 | 已登录 |
| POST | /approvals/{id}/approve | 通过审批 | ADMIN+ |
| POST | /approvals/{id}/reject | 驳回审批 | ADMIN+ |

---

## 六、业务规则与状态机

### 6.1 活动状态流转

```
                    ┌─────────────┐
                    │   DRAFT    │ ← 创建活动初始状态
                    └──────┬──────┘
                           │ submit
                           ▼
                    ┌─────────────┐
         ┌─────────│   PENDING   │ ← 等待审批
         │         └──────┬──────┘
    reject │                │ approve
         │                ▼
         │         ┌─────────────┐
         └────────→│  APPROVED   │ ← 审批通过
                   └──────┬──────┘
                          │ 到达报名时间
                          ▼
                   ┌─────────────┐
                   │ REGISTERING │ ← 开放报名
                   └──────┬──────┘
                          │ 报名截止/开始时间到
                          ▼
                   ┌─────────────┐
                   │   ONGOING   │ ← 进行中
                   └──────┬──────┘
                          │ 结束时间到
                          ▼
                   ┌─────────────┐
                   │  COMPLETED  │ ← 已结束，可评价
                   └─────────────┘
```

**状态转换规则**:
- DRAFT → PENDING: 提交审批（仅限创建者）
- PENDING → APPROVED: 审批通过（仅限ADMIN）
- PENDING → REJECTED: 审批驳回（仅限ADMIN）
- APPROVED → REGISTERING: 自动转换（开始时间前24小时）
- REGISTERING → ONGOING: 自动转换（开始时间到）
- ONGOING → COMPLETED: 自动转换（结束时间到）
- 任何状态 → CANCELLED: 取消活动（仅限创建者/ADMIN）

### 6.2 报名规则

1. 活动状态为REGISTERING时才能报名
2. 已报名人数 < 容量限制
3. 每人同一时段只能报名一个活动
4. 报名后可在活动开始前取消
5. 活动开始后可以签到

### 6.3 评分计算规则

**五维评估权重**（可配置）:
```
参与度: 30%
教育性: 25%
创新性: 20%
影响力: 15%
可持续性: 10%
```

**数据来源**:
- 参与度: 签到率、参与人数/容量比
- 教育性: 问卷评分 + NLP分析
- 创新性: 社团自评 + 管理员评分
- 影响力: 分享数、传播范围
- 可持续性: 资源利用率、重复举办次数

---

## 七、开发计划

### 7.1 第一阶段：用户与社团模块（P0）

**目标**: 完成用户认证和社团管理基础功能

| 任务 | 文件/模块 | 预估工时 |
|------|----------|----------|
| 用户实体与Repository | user/domain/entity/User.java | 1h |
| 微信登录Service | user/infrastructure/external/WechatMpClient.java | 2h |
| JWT认证Service | application/service/AuthApplicationService.java | 2h |
| 登录Controller | user/interfaces/rest/AuthController.java | 1h |
| 社团实体与Repository | club/domain/entity/Club.java | 1h |
| 社团CRUD Service | club/application/service/ClubApplicationService.java | 2h |
| 社团Controller | club/interfaces/rest/ClubController.java | 1.5h |
| Flyway迁移脚本 | db/migration/V1__create_users_table.sql | 1h |
| 单元测试 | *Test.java | 2h |
| **小计** | | **13.5h** |

### 7.2 第二阶段：活动模块核心（P0）

**目标**: 完成活动申报、审批、报名核心链路

| 任务 | 文件/模块 | 预估工时 |
|------|----------|----------|
| 活动实体与状态机 | activity/domain/entity/Activity.java | 2h |
| 活动Repository | activity/domain/repository/ActivityRepository.java | 1h |
| 活动CRUD Service | activity/application/service/ActivityApplicationService.java | 3h |
| 报名/签到Service | activity/domain/service/ParticipationDomainService.java | 2h |
| 活动Controller | activity/interfaces/rest/ActivityController.java | 2h |
| 状态转换事件 | activity/application/event/ActivityStatusChangedEvent.java | 1h |
| Flyway迁移脚本 | db/migration/V3__create_activities_table.sql | 1h |
| 单元测试 | *Test.java | 3h |
| **小计** | | **15h** |

### 7.3 第三阶段：资源模块（P1）

**目标**: 完成资源管理与预约功能

| 任务 | 文件/模块 | 预估工时 |
|------|----------|----------|
| 资源实体 | resource/domain/entity/Resource.java | 1.5h |
| 预约冲突检测 | resource/domain/service/ReservationDomainService.java | 2h |
| 资源CRUD Service | resource/application/service/ResourceApplicationService.java | 2h |
| 资源Controller | resource/interfaces/rest/ResourceController.java | 1.5h |
| Flyway迁移脚本 | db/migration/V4__create_resources_table.sql | 1h |
| 单元测试 | *Test.java | 2h |
| **小计** | | **10h** |

### 7.4 第四阶段：评估模块（P1）

**目标**: 完成活动评估与算法集成

| 任务 | 文件/模块 | 预估工时 |
|------|----------|----------|
| 评估实体 | evaluation/domain/entity/Evaluation.java | 1.5h |
| 评价反馈实体 | evaluation/domain/entity/ActivityFeedback.java | 1h |
| 算法集成Service | evaluation/application/service/AlgorithmIntegrationService.java | 3h |
| 评估报告Service | evaluation/application/service/EvaluationApplicationService.java | 2h |
| 评估Controller | evaluation/interfaces/rest/EvaluationController.java | 1.5h |
| Flyway迁移脚本 | db/migration/V5__create_evaluations_table.sql | 1h |
| 单元测试 | *Test.java | 2h |
| **小计** | | **12h** |

### 7.5 第五阶段：审批模块（P2）

**目标**: 完成审批工作流

| 任务 | 文件/模块 | 预估工时 |
|------|----------|----------|
| 审批记录实体 | approval/domain/entity/ApprovalRecord.java | 1h |
| 审批Service | approval/application/service/ApprovalApplicationService.java | 2h |
| 审批Controller | approval/interfaces/rest/ApprovalController.java | 1h |
| Flyway迁移脚本 | db/migration/V6__create_approvals_table.sql | 0.5h |
| 单元测试 | *Test.java | 1.5h |
| **小计** | | **6h** |

### 7.6 总工时汇总

| 阶段 | 工时 | 里程碑 |
|------|------|--------|
| 第一阶段 | 13.5h | 用户可登录，社团可管理 |
| 第二阶段 | 15h | 活动全生命周期管理 |
| 第三阶段 | 10h | 资源预约可用 |
| 第四阶段 | 12h | 评估报告可生成 |
| 第五阶段 | 6h | 审批流程完善 |
| **合计** | **56.5h** | |

---

## 八、测试策略

### 8.1 测试分层

```
test/
├── unit/                          # 单元测试
│   ├── user/
│   ├── club/
│   ├── activity/
│   ├── resource/
│   ├── evaluation/
│   └── approval/
├── integration/                   # 集成测试
│   ├── repository/
│   ├── service/
│   └── api/
└── e2e/                          # 端到端测试
    └── api/
```

### 8.2 测试规范

**单元测试**（使用JUnit 5 + Mockito）:
- Service层逻辑测试
- Domain领域规则测试
- Repository查询测试（使用@DataJpaTest）

**集成测试**:
- Controller API测试（使用@WebMvcTest + MockMvc）
- 数据库集成测试（使用TestContainers）

**TDD适用场景**:
- 活动状态机转换
- 资源预约冲突检测
- 审批工作流
- 算法集成调用

### 8.3 测试数据

使用 **@Sql** 注解或 **@SqlGroup** 加载测试数据:
```java
@Sql({"/sql/test-users.sql", "/sql/test-clubs.sql"})
@Test
void shouldReturnClubActivities() {
    // 测试代码
}
```

---

## 九、部署配置

### 9.1 application.yml 配置

```yaml
spring:
  application:
    name: campus-club-backend
  
  datasource:
    url: jdbc:postgresql://${DB_HOST:localhost}:${DB_PORT:5432}/${DB_NAME:campus_club}
    username: ${DB_USER:campus_user}
    password: ${DB_PASSWORD:}
    driver-class-name: org.postgresql.Driver
  
  jpa:
    hibernate:
      ddl-auto: validate  # 生产环境使用validate，开发可用none
    properties:
      hibernate:
        dialect: org.hibernate.dialect.PostgreSQLDialect
        format_sql: true
    show-sql: false
  
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
  secret: ${JWT_SECRET:your-secret-key-change-in-production}
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
```

### 9.2 Docker Compose 配置

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: campus-postgres
    environment:
      POSTGRES_DB: campus_club
      POSTGRES_USER: campus_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U campus_user -d campus_club"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: campus-redis
    command: redis-server --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5

  java-app:
    build:
      context: ./campus-main
      dockerfile: Dockerfile
    container_name: campus-java
    environment:
      SPRING_PROFILES_ACTIVE: prod
      DB_HOST: postgres
      DB_PASSWORD: ${DB_PASSWORD}
      REDIS_HOST: redis
      REDIS_PASSWORD: ${REDIS_PASSWORD}
      JWT_SECRET: ${JWT_SECRET}
      WECHAT_APP_ID: ${WECHAT_APP_ID}
      WECHAT_SECRET: ${WECHAT_SECRET}
      ALGORITHM_SERVICE_URL: http://algorithm-service:8000
    ports:
      - "8080:8080"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped

  algorithm-service:
    build:
      context: ./campus-ai
      dockerfile: Dockerfile
    container_name: campus-algorithm
    environment:
      PYTHONPATH: /app
      MODEL_CACHE_DIR: /app/models
      REDIS_HOST: redis
    ports:
      - "8000:8000"
    volumes:
      - ./ai-models:/app/models
    deploy:
      resources:
        limits:
          memory: 4G
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
```

---

## 十、安全设计

### 10.1 认证流程

**微信小程序登录**:
```
1. 小程序调用 wx.login() 获取 code
2. 小程序将 code 发送到后端 /api/v1/auth/wechat-login
3. 后端用 code + appsecret 请求微信接口获取 openid
4. 根据 openid 查找或创建用户
5. 生成 JWT Token 返回给小程序
6. 小程序存储 token，后续请求携带 Authorization 头
```

**PC端登录**（社团端/管理端）:
```
1. 用户输入账号密码
2. 后端验证密码（BCrypt）
3. 生成 JWT Token 返回
4. 前端存储 token 到 localStorage
```

### 10.2 RBAC权限模型

**角色定义**:
- `STUDENT`: 学生，可报名活动、提交评价
- `CLUB_MEMBER`: 社团成员，可创建活动
- `CLUB_MANAGER`: 社团管理层，可管理社团成员
- `CLUB_PRESIDENT`: 社长，社团最高权限
- `ADMIN`: 系统管理员，可审批活动、管理资源
- `SUPER_ADMIN`: 超级管理员，所有权限

**权限粒度**:
| 资源 | 操作 | 所需角色 |
|------|------|----------|
| 活动 | 创建 | CLUB_MEMBER+ |
| 活动 | 审批 | ADMIN+ |
| 社团 | 管理成员 | CLUB_MANAGER+ |
| 资源 | 创建 | ADMIN+ |
| 评估 | 查看报告 | CLUB_MANAGER+ |

### 10.3 安全防护

- **SQL注入**: 使用JPA参数化查询
- **XSS**: 输入输出过滤，Content-Type检查
- **CSRF**: 前后端分离天然防御
- **限流**: Redis实现接口限流（登录60次/小时）
- **敏感数据脱敏**: 手机号、邮箱等脱敏返回

---

## 十一、风险与应对

| 风险 | 影响 | 可能性 | 应对措施 |
|------|------|--------|----------|
| 微信登录集成问题 | 高 | 中 | 提前申请测试账号，准备Mock方案 |
| 算法服务超时 | 中 | 中 | 设置熔断降级，返回缓存结果 |
| 并发报名超卖 | 高 | 低 | 数据库乐观锁或Redis分布式锁 |
| 数据库性能瓶颈 | 中 | 低 | 合理索引、查询优化、连接池调优 |
| 微信小程序审核 | 中 | 中 | 提前准备材料，预留审核时间 |

---

## 十二、附录

### 12.1 环境变量清单

| 变量名 | 说明 | 必需 |
|--------|------|------|
| DB_HOST | 数据库主机 | 是 |
| DB_PORT | 数据库端口 | 否（默认5432） |
| DB_NAME | 数据库名 | 否（默认campus_club） |
| DB_USER | 数据库用户 | 是 |
| DB_PASSWORD | 数据库密码 | 是 |
| REDIS_HOST | Redis主机 | 是 |
| REDIS_PORT | Redis端口 | 否（默认6379） |
| REDIS_PASSWORD | Redis密码 | 是 |
| JWT_SECRET | JWT密钥 | 是 |
| WECHAT_APP_ID | 微信小程序AppID | 是 |
| WECHAT_SECRET | 微信小程序Secret | 是 |
| ALGORITHM_SERVICE_URL | 算法服务地址 | 否（默认localhost:8000） |

### 12.2 相关文档

- [后端架构设计文档](./2026-04-09-campus-club-backend-architecture-design.md)
- [算法服务设计文档](./2026-04-09-campus-club-algorithm-service-design.md)
- [前端正式开发设计文档](./2026-04-14-frontend-development-plan.md)
- [API文档](http://localhost:8080/swagger-ui.html)（服务启动后）

### 12.3 开发规范

**代码风格**:
- 使用Google Java Format
- 类名使用PascalCase
- 方法名和变量名使用camelCase
- 常量使用UPPER_SNAKE_CASE

**Git提交规范**:
```
feat: 新功能
fix: 修复
docs: 文档
style: 代码格式
refactor: 重构
test: 测试
chore: 构建/工具
```

**包命名规范**:
- 领域包: `com.campusclub.{domain}`
- 通用包: `com.campusclub.common.{type}`

---

*文档版本：1.0*
*最后更新：2026-04-14*
*状态：正式开发版*
