# 数据库设计文档

本文档描述了校园社团系统的数据库表结构设计。

---

## 目录

1. [用户模块](#用户模块)
2. [社团模块](#社团模块)
3. [活动模块](#活动模块)
4. [资源模块](#资源模块)
5. [评估模块](#评估模块)
6. [资金模块](#资金模块)
7. [系统模块](#系统模块)

---

## ER 图概览

```
┌─────────────┐       ┌─────────────┐       ┌─────────────┐
│    users    │       │    clubs    │       │  activities │
├─────────────┤       ├─────────────┤       ├─────────────┤
│ id (PK)     │       │ id (PK)     │       │ id (PK)     │
│ username    │       │ name        │       │ title       │
│ email       │◄──────┤ category    │◄──────┤ club_id(FK) │
│ role        │       │ president_id│       │ status      │
│ phone       │       │ status      │       │ start_time  │
└─────────────┘       └─────────────┘       └─────────────┘
        │                     │                    │
        │              ┌──────┴──────┐             │
        │              │ club_members│             │
        │              ├─────────────┤             │
        │              │ club_id(FK) │             │
        └──────────────┤ user_id(FK) │             │
                       │ role        │             │
                       └─────────────┘             │
                                                   │
┌─────────────┐       ┌─────────────┐              │
│   resources │       │resource_    │◄─────────────┘
├─────────────┤       │bookings     │
│ id (PK)     │◄──────├─────────────┤
│ name        │       │ id (PK)     │
│ type        │       │ resource_id │       ┌─────────────┐
│ capacity    │       │ activity_id │──────►│ evaluations │
│ location    │       │ status      │       ├─────────────┤
└─────────────┘       └─────────────┘       │ id (PK)     │
                                            │ activity_id │
┌─────────────┐       ┌─────────────┐       │ scores      │
│fund_        │       │  feedbacks  │       │ total_score │
│applications ├───────┤             │       └─────────────┘
├─────────────┤       ├─────────────┤
│ id (PK)     │       │ id (PK)     │
│ club_id     │       │ activity_id │
│ amount      │       │ user_id     │
│ status      │       │ rating      │
└─────────────┘       │ sentiment   │
                      └─────────────┘
```

---

## 用户模块

### users (用户表)

存储系统用户信息。

```sql
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE COMMENT '用户名',
    password VARCHAR(255) NOT NULL COMMENT '加密密码',
    email VARCHAR(100) UNIQUE COMMENT '邮箱',
    phone VARCHAR(20) COMMENT '手机号',
    real_name VARCHAR(50) COMMENT '真实姓名',
    student_id VARCHAR(20) UNIQUE COMMENT '学号',
    avatar_url VARCHAR(255) COMMENT '头像URL',
    role VARCHAR(20) NOT NULL DEFAULT 'STUDENT' COMMENT '角色: STUDENT/CLUB_MANAGER/ADMIN',
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE' COMMENT '状态: ACTIVE/INACTIVE',
    last_login_time TIMESTAMP COMMENT '最后登录时间',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    version BIGINT DEFAULT 0
);

CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_status ON users(status);
CREATE INDEX idx_users_student_id ON users(student_id);
```

---

## 社团模块

### clubs (社团表)

存储社团基本信息。

```sql
CREATE TABLE clubs (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL COMMENT '社团名称',
    category VARCHAR(50) NOT NULL COMMENT '类别: 学术/文艺/体育/公益/其他',
    description TEXT COMMENT '社团简介',
    logo_url VARCHAR(255) COMMENT 'Logo URL',
    president_id BIGINT REFERENCES users(id) COMMENT '社长用户ID',
    advisor_name VARCHAR(50) COMMENT '指导老师',
    contact_email VARCHAR(100) COMMENT '联系邮箱',
    contact_phone VARCHAR(20) COMMENT '联系电话',
    member_count INTEGER DEFAULT 0 COMMENT '成员数量',
    activity_count INTEGER DEFAULT 0 COMMENT '活动数量',
    total_score DECIMAL(5,2) COMMENT '综合评分',
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING' COMMENT '状态: PENDING/ACTIVE/SUSPENDED',
    founded_at DATE COMMENT '成立日期',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    version BIGINT DEFAULT 0
);

CREATE INDEX idx_clubs_category ON clubs(category);
CREATE INDEX idx_clubs_status ON clubs(status);
CREATE INDEX idx_clubs_president ON clubs(president_id);
```

### club_members (社团成员表)

存储社团成员关系。

```sql
CREATE TABLE club_members (
    id BIGSERIAL PRIMARY KEY,
    club_id BIGINT NOT NULL REFERENCES clubs(id) ON DELETE CASCADE,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL DEFAULT 'MEMBER' COMMENT '角色: PRESIDENT/MANAGER/MEMBER',
    joined_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE' COMMENT '状态: ACTIVE/INACTIVE',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(club_id, user_id)
);

CREATE INDEX idx_club_members_club ON club_members(club_id);
CREATE INDEX idx_club_members_user ON club_members(user_id);
CREATE INDEX idx_club_members_role ON club_members(role);
```

---

## 活动模块

### activities (活动表)

存储活动信息。

```sql
CREATE TABLE activities (
    id BIGSERIAL PRIMARY KEY,
    club_id BIGINT NOT NULL REFERENCES clubs(id),
    title VARCHAR(200) NOT NULL COMMENT '活动标题',
    description TEXT COMMENT '活动描述',
    type VARCHAR(50) COMMENT '活动类型',
    location VARCHAR(200) COMMENT '活动地点',
    planned_date DATE COMMENT '计划日期',
    start_time TIMESTAMP COMMENT '开始时间',
    end_time TIMESTAMP COMMENT '结束时间',
    max_participants INTEGER COMMENT '最大参与人数',
    current_participants INTEGER DEFAULT 0 COMMENT '当前报名人数',
    budget DECIMAL(10,2) COMMENT '预算金额',
    status VARCHAR(20) NOT NULL DEFAULT 'DRAFT' COMMENT '状态: DRAFT/PENDING/REJECTED/APPROVED/ONGOING/COMPLETED/CANCELLED',
    approval_comment TEXT COMMENT '审批意见',
    approved_by BIGINT REFERENCES users(id) COMMENT '审批人',
    approved_at TIMESTAMP COMMENT '审批时间',
    poster_url VARCHAR(255) COMMENT '活动海报',
    evaluation_id BIGINT COMMENT '评估记录ID',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    version BIGINT DEFAULT 0
);

CREATE INDEX idx_activities_club ON activities(club_id);
CREATE INDEX idx_activities_status ON activities(status);
CREATE INDEX idx_activities_date ON activities(planned_date);
CREATE INDEX idx_activities_type ON activities(type);
```

### activity_participants (活动参与者表)

存储活动报名信息。

```sql
CREATE TABLE activity_participants (
    id BIGSERIAL PRIMARY KEY,
    activity_id BIGINT NOT NULL REFERENCES activities(id) ON DELETE CASCADE,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    registered_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    attended BOOLEAN DEFAULT FALSE COMMENT '是否签到',
    checked_in_at TIMESTAMP COMMENT '签到时间',
    feedback_submitted BOOLEAN DEFAULT FALSE COMMENT '是否已评价',
    status VARCHAR(20) NOT NULL DEFAULT 'REGISTERED' COMMENT '状态: REGISTERED/CANCELLED/ATTENDED',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(activity_id, user_id)
);

CREATE INDEX idx_participants_activity ON activity_participants(activity_id);
CREATE INDEX idx_participants_user ON activity_participants(user_id);
```

---

## 资源模块

### resources (资源表)

存储可预约的资源信息。

```sql
CREATE TABLE resources (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL COMMENT '资源名称',
    type VARCHAR(50) NOT NULL COMMENT '类型: VENUE/EQUIPMENT/FUND',
    description TEXT COMMENT '资源描述',
    location VARCHAR(200) COMMENT '位置',
    capacity INTEGER COMMENT '容量(场地)',
    quantity INTEGER COMMENT '数量(设备)',
    manager_id BIGINT REFERENCES users(id) COMMENT '管理员',
    status VARCHAR(20) NOT NULL DEFAULT 'AVAILABLE' COMMENT '状态: AVAILABLE/MAINTENANCE/RETIRED',
    open_time TIME COMMENT '开放时间',
    close_time TIME COMMENT '关闭时间',
    requires_approval BOOLEAN DEFAULT TRUE COMMENT '是否需要审批',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    version BIGINT DEFAULT 0
);

CREATE INDEX idx_resources_type ON resources(type);
CREATE INDEX idx_resources_status ON resources(status);
```

### resource_bookings (资源预约表)

存储资源预约记录。

```sql
CREATE TABLE resource_bookings (
    id BIGSERIAL PRIMARY KEY,
    resource_id BIGINT NOT NULL REFERENCES resources(id),
    activity_id BIGINT REFERENCES activities(id),
    club_id BIGINT NOT NULL REFERENCES clubs(id),
    applicant_id BIGINT NOT NULL REFERENCES users(id),
    booking_date DATE NOT NULL COMMENT '预约日期',
    start_time TIME NOT NULL COMMENT '开始时间',
    end_time TIME NOT NULL COMMENT '结束时间',
    purpose TEXT COMMENT '用途说明',
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING' COMMENT '状态: PENDING/APPROVED/REJECTED/CANCELLED',
    reviewer_id BIGINT REFERENCES users(id) COMMENT '审批人',
    reviewer_comment TEXT COMMENT '审批意见',
    reviewed_at TIMESTAMP COMMENT '审批时间',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    version BIGINT DEFAULT 0
);

CREATE INDEX idx_bookings_resource ON resource_bookings(resource_id);
CREATE INDEX idx_bookings_club ON resource_bookings(club_id);
CREATE INDEX idx_bookings_status ON resource_bookings(status);
CREATE INDEX idx_bookings_date ON resource_bookings(booking_date);
CREATE INDEX idx_bookings_activity ON resource_bookings(activity_id);
```

---

## 评估模块

### evaluations (活动评估表)

存储AHP评估结果。

```sql
CREATE TABLE evaluations (
    id BIGSERIAL PRIMARY KEY,
    activity_id BIGINT NOT NULL UNIQUE REFERENCES activities(id),
    evaluator_id BIGINT NOT NULL REFERENCES users(id),
    scores JSONB NOT NULL COMMENT '五维得分: {参与度,教育性,创新性,影响力,可持续性}',
    weights JSONB NOT NULL COMMENT '权重配置',
    total_score DECIMAL(5,2) NOT NULL COMMENT '加权总分',
    consistency_ratio DECIMAL(4,4) COMMENT '一致性比率',
    consistency_check_passed BOOLEAN DEFAULT TRUE,
    comments TEXT COMMENT '评估意见',
    evaluated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    version BIGINT DEFAULT 0
);

CREATE INDEX idx_evaluations_activity ON evaluations(activity_id);
CREATE INDEX idx_evaluations_total_score ON evaluations(total_score);
```

### feedbacks (活动反馈表)

存储学生评价和NLP分析结果。

```sql
CREATE TABLE feedbacks (
    id BIGSERIAL PRIMARY KEY,
    activity_id BIGINT NOT NULL REFERENCES activities(id),
    user_id BIGINT NOT NULL REFERENCES users(id),
    rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5) COMMENT '星级评分',
    content TEXT COMMENT '评价内容',
    sentiment_score DECIMAL(4,3) COMMENT '情感得分 -1~1',
    sentiment_level VARCHAR(20) COMMENT '情感级别: POSITIVE/NEUTRAL/NEGATIVE',
    keywords JSONB COMMENT '关键词',
    aspect_sentiments JSONB COMMENT '各方面情感分析',
    analysis_status VARCHAR(20) DEFAULT 'PENDING' COMMENT '分析状态: PENDING/ANALYZED/FAILED',
    photos JSONB COMMENT '照片URL列表',
    submitted_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    analyzed_at TIMESTAMP COMMENT '分析完成时间',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(activity_id, user_id)
);

CREATE INDEX idx_feedbacks_activity ON feedbacks(activity_id);
CREATE INDEX idx_feedbacks_user ON feedbacks(user_id);
CREATE INDEX idx_feedbacks_sentiment ON feedbacks(sentiment_level);
```

---

## 资金模块

### fund_applications (资金申请表)

```sql
CREATE TABLE fund_applications (
    id BIGSERIAL PRIMARY KEY,
    club_id BIGINT NOT NULL REFERENCES clubs(id),
    activity_id BIGINT REFERENCES activities(id),
    applicant_id BIGINT NOT NULL REFERENCES users(id),
    amount DECIMAL(10, 2) NOT NULL COMMENT '申请金额',
    purpose TEXT NOT NULL COMMENT '用途说明',
    budget_breakdown JSONB COMMENT '预算明细',
    status VARCHAR(20) DEFAULT 'PENDING' COMMENT '状态: PENDING/APPROVED/REJECTED/CANCELLED',
    reviewer_id BIGINT REFERENCES users(id) COMMENT '审批人',
    reviewer_comment TEXT COMMENT '审批意见',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reviewed_at TIMESTAMP COMMENT '审批时间',
    version BIGINT DEFAULT 0
);

CREATE INDEX idx_fund_app_club ON fund_applications(club_id);
CREATE INDEX idx_fund_app_status ON fund_applications(status);
CREATE INDEX idx_fund_app_activity ON fund_applications(activity_id);
```

---

## 系统模块

### operation_logs (操作日志表)

```sql
CREATE TABLE operation_logs (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id),
    operation_type VARCHAR(50) NOT NULL COMMENT '操作类型',
    module VARCHAR(50) NOT NULL COMMENT '操作模块',
    description TEXT COMMENT '操作描述',
    request_data JSONB COMMENT '请求数据',
    response_data JSONB COMMENT '响应数据',
    ip_address VARCHAR(50) COMMENT 'IP地址',
    user_agent TEXT COMMENT '用户代理',
    execution_time_ms INTEGER COMMENT '执行时间(ms)',
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_logs_user ON operation_logs(user_id);
CREATE INDEX idx_logs_type ON operation_logs(operation_type);
CREATE INDEX idx_logs_module ON operation_logs(module);
CREATE INDEX idx_logs_created ON operation_logs(created_at);
```

---

## 数据库规范

### 命名规范

| 对象 | 规范 | 示例 |
|------|------|------|
| 表名 | 小写，下划线分隔 | `club_members` |
| 字段名 | 小写，下划线分隔 | `created_at` |
| 索引名 | `idx_表名_字段名` | `idx_clubs_status` |
| 外键名 | `fk_表名_引用表` | `fk_bookings_resource` |

### 字段规范

所有表必须包含:
- `id`: 主键，BIGSERIAL
- `created_at`: 创建时间
- `updated_at`: 更新时间
- `version`: 乐观锁版本号

### 索引策略

1. **主键索引**: 所有表的主键自动创建索引
2. **外键索引**: 所有外键字段必须创建索引
3. **查询索引**: WHERE 条件常用字段添加索引
4. **联合索引**: 组合查询字段考虑联合索引

### 数据类型选择

| 场景 | 推荐类型 | 说明 |
|------|----------|------|
| 主键 | BIGSERIAL | 自增64位整数 |
| 金额 | DECIMAL(10,2) | 精确小数 |
| 分数 | DECIMAL(5,2) | 0-100分 |
| JSON数据 | JSONB | PostgreSQL JSONB |
| 状态枚举 | VARCHAR(20) | 可读性好 |
| 时间戳 | TIMESTAMP | 无时区 |

---

## 变更日志

### 2024-04-15
- 新增 `fund_applications` 资金申请表
- 新增 `feedbacks` 活动反馈表 NLP相关字段

### 2024-04-14
- 新增 `resource_bookings` 资源预约表
- 新增 `evaluations` 活动评估表

### 2024-04-13
- 初始化数据库设计
