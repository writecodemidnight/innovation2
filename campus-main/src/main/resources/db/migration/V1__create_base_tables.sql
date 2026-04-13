-- ============================================
-- 校园社团活动评估系统数据库表结构
-- 版本: V1
-- 创建时间: 2024-01-01
-- ============================================

-- 用户表
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    real_name VARCHAR(50),
    student_id VARCHAR(20),
    phone VARCHAR(20),
    avatar_url VARCHAR(255),
    role_id BIGINT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    deleted BOOLEAN NOT NULL DEFAULT FALSE
);

-- 角色表
CREATE TABLE roles (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description VARCHAR(255),
    permissions TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    deleted BOOLEAN NOT NULL DEFAULT FALSE
);

-- 社团表
CREATE TABLE clubs (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    logo_url VARCHAR(255),
    president_id BIGINT NOT NULL,
    advisor_id BIGINT,
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    member_count INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    deleted BOOLEAN NOT NULL DEFAULT FALSE
);

-- 活动表
CREATE TABLE activities (
    id BIGSERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    club_id BIGINT NOT NULL,
    organizer_id BIGINT NOT NULL,
    activity_type VARCHAR(50) NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    location VARCHAR(200),
    max_participants INTEGER,
    current_participants INTEGER NOT NULL DEFAULT 0,
    status VARCHAR(20) NOT NULL DEFAULT 'PLANNING',
    cover_image_url VARCHAR(255),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    deleted BOOLEAN NOT NULL DEFAULT FALSE
);

-- 活动参与者表
CREATE TABLE activity_participants (
    id BIGSERIAL PRIMARY KEY,
    activity_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    participation_status VARCHAR(20) NOT NULL DEFAULT 'REGISTERED',
    check_in_time TIMESTAMP,
    check_out_time TIMESTAMP,
    feedback TEXT,
    rating INTEGER,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    deleted BOOLEAN NOT NULL DEFAULT FALSE
);

-- 资源表
CREATE TABLE resources (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    resource_type VARCHAR(50) NOT NULL,
    location VARCHAR(200),
    capacity INTEGER,
    status VARCHAR(20) NOT NULL DEFAULT 'AVAILABLE',
    club_id BIGINT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    deleted BOOLEAN NOT NULL DEFAULT FALSE
);

-- 资源预约表
CREATE TABLE resource_reservations (
    id BIGSERIAL PRIMARY KEY,
    resource_id BIGINT NOT NULL,
    activity_id BIGINT,
    user_id BIGINT NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    purpose TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    deleted BOOLEAN NOT NULL DEFAULT FALSE
);

-- 评估指标表
CREATE TABLE evaluation_metrics (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    metric_type VARCHAR(50) NOT NULL,
    weight DECIMAL(5,2) NOT NULL DEFAULT 1.00,
    max_score INTEGER NOT NULL DEFAULT 100,
    min_score INTEGER NOT NULL DEFAULT 0,
    activity_type VARCHAR(50),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    deleted BOOLEAN NOT NULL DEFAULT FALSE
);

-- 非结构化数据表（用于存储图片、文档等）
CREATE TABLE unstructured_data (
    id BIGSERIAL PRIMARY KEY,
    file_name VARCHAR(255) NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    file_size BIGINT NOT NULL,
    storage_path VARCHAR(500) NOT NULL,
    uploader_id BIGINT NOT NULL,
    related_entity_type VARCHAR(50),
    related_entity_id BIGINT,
    metadata JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    deleted BOOLEAN NOT NULL DEFAULT FALSE
);

-- ============================================
-- 索引创建
-- ============================================

-- 用户表索引
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role_id ON users(role_id);
CREATE INDEX idx_users_deleted ON users(deleted);

-- 角色表索引
CREATE INDEX idx_roles_name ON roles(name);
CREATE INDEX idx_roles_deleted ON roles(deleted);

-- 社团表索引
CREATE INDEX idx_clubs_name ON clubs(name);
CREATE INDEX idx_clubs_president_id ON clubs(president_id);
CREATE INDEX idx_clubs_status ON clubs(status);
CREATE INDEX idx_clubs_deleted ON clubs(deleted);

-- 活动表索引
CREATE INDEX idx_activities_club_id ON activities(club_id);
CREATE INDEX idx_activities_organizer_id ON activities(organizer_id);
CREATE INDEX idx_activities_start_time ON activities(start_time);
CREATE INDEX idx_activities_status ON activities(status);
CREATE INDEX idx_activities_deleted ON activities(deleted);

-- 活动参与者表索引
CREATE INDEX idx_activity_participants_activity_id ON activity_participants(activity_id);
CREATE INDEX idx_activity_participants_user_id ON activity_participants(user_id);
CREATE INDEX idx_activity_participants_status ON activity_participants(participation_status);
CREATE INDEX idx_activity_participants_deleted ON activity_participants(deleted);

-- 资源表索引
CREATE INDEX idx_resources_club_id ON resources(club_id);
CREATE INDEX idx_resources_resource_type ON resources(resource_type);
CREATE INDEX idx_resources_status ON resources(status);
CREATE INDEX idx_resources_deleted ON resources(deleted);

-- 资源预约表索引
CREATE INDEX idx_resource_reservations_resource_id ON resource_reservations(resource_id);
CREATE INDEX idx_resource_reservations_activity_id ON resource_reservations(activity_id);
CREATE INDEX idx_resource_reservations_user_id ON resource_reservations(user_id);
CREATE INDEX idx_resource_reservations_start_time ON resource_reservations(start_time);
CREATE INDEX idx_resource_reservations_status ON resource_reservations(status);
CREATE INDEX idx_resource_reservations_deleted ON resource_reservations(deleted);

-- 评估指标表索引
CREATE INDEX idx_evaluation_metrics_metric_type ON evaluation_metrics(metric_type);
CREATE INDEX idx_evaluation_metrics_activity_type ON evaluation_metrics(activity_type);
CREATE INDEX idx_evaluation_metrics_deleted ON evaluation_metrics(deleted);

-- 非结构化数据表索引
CREATE INDEX idx_unstructured_data_uploader_id ON unstructured_data(uploader_id);
CREATE INDEX idx_unstructured_data_related_entity ON unstructured_data(related_entity_type, related_entity_id);
CREATE INDEX idx_unstructured_data_file_type ON unstructured_data(file_type);
CREATE INDEX idx_unstructured_data_deleted ON unstructured_data(deleted);

-- ============================================
-- 外键约束
-- ============================================

-- 用户表外键
ALTER TABLE users ADD CONSTRAINT fk_users_role_id
    FOREIGN KEY (role_id) REFERENCES roles(id);

-- 社团表外键
ALTER TABLE clubs ADD CONSTRAINT fk_clubs_president_id
    FOREIGN KEY (president_id) REFERENCES users(id);
ALTER TABLE clubs ADD CONSTRAINT fk_clubs_advisor_id
    FOREIGN KEY (advisor_id) REFERENCES users(id);

-- 活动表外键
ALTER TABLE activities ADD CONSTRAINT fk_activities_club_id
    FOREIGN KEY (club_id) REFERENCES clubs(id);
ALTER TABLE activities ADD CONSTRAINT fk_activities_organizer_id
    FOREIGN KEY (organizer_id) REFERENCES users(id);

-- 活动参与者表外键
ALTER TABLE activity_participants ADD CONSTRAINT fk_activity_participants_activity_id
    FOREIGN KEY (activity_id) REFERENCES activities(id);
ALTER TABLE activity_participants ADD CONSTRAINT fk_activity_participants_user_id
    FOREIGN KEY (user_id) REFERENCES users(id);

-- 资源表外键
ALTER TABLE resources ADD CONSTRAINT fk_resources_club_id
    FOREIGN KEY (club_id) REFERENCES clubs(id);

-- 资源预约表外键
ALTER TABLE resource_reservations ADD CONSTRAINT fk_resource_reservations_resource_id
    FOREIGN KEY (resource_id) REFERENCES resources(id);
ALTER TABLE resource_reservations ADD CONSTRAINT fk_resource_reservations_activity_id
    FOREIGN KEY (activity_id) REFERENCES activities(id);
ALTER TABLE resource_reservations ADD CONSTRAINT fk_resource_reservations_user_id
    FOREIGN KEY (user_id) REFERENCES users(id);

-- 非结构化数据表外键
ALTER TABLE unstructured_data ADD CONSTRAINT fk_unstructured_data_uploader_id
    FOREIGN KEY (uploader_id) REFERENCES users(id);

-- ============================================
-- 初始数据
-- ============================================

-- 插入初始角色
INSERT INTO roles (name, description, permissions) VALUES
('ADMIN', '系统管理员', 'ALL'),
('CLUB_PRESIDENT', '社团社长', 'CLUB_MANAGEMENT,ACTIVITY_MANAGEMENT'),
('CLUB_MEMBER', '社团成员', 'ACTIVITY_PARTICIPATION'),
('STUDENT', '普通学生', 'ACTIVITY_VIEW'),
('TEACHER', '教师', 'ACTIVITY_REVIEW,RESOURCE_APPROVAL');

-- 插入初始管理员用户（密码：admin123，实际使用时应加密）
INSERT INTO users (username, password, email, real_name, role_id) VALUES
('admin', '$2a$10$YourEncryptedPasswordHere', 'admin@campus.edu', '系统管理员', 1);

-- 插入初始评估指标
INSERT INTO evaluation_metrics (name, description, metric_type, weight, max_score, min_score) VALUES
('参与度', '活动参与人数和参与质量', 'PARTICIPATION', 0.25, 100, 0),
('组织质量', '活动组织水平和流程安排', 'ORGANIZATION', 0.20, 100, 0),
('内容质量', '活动内容的价值和深度', 'CONTENT', 0.25, 100, 0),
('创新性', '活动的创新程度和独特性', 'INNOVATION', 0.15, 100, 0),
('影响力', '活动对参与者的影响和传播效果', 'IMPACT', 0.15, 100, 0);

-- ============================================
-- 注释说明
-- ============================================

COMMENT ON TABLE users IS '系统用户表，存储所有用户信息';
COMMENT ON TABLE roles IS '角色表，定义用户权限角色';
COMMENT ON TABLE clubs IS '社团表，存储社团基本信息';
COMMENT ON TABLE activities IS '活动表，存储社团活动信息';
COMMENT ON TABLE activity_participants IS '活动参与者表，记录活动参与情况';
COMMENT ON TABLE resources IS '资源表，存储可用资源信息';
COMMENT ON TABLE resource_reservations IS '资源预约表，记录资源预约情况';
COMMENT ON TABLE evaluation_metrics IS '评估指标表，定义活动评估标准';
COMMENT ON TABLE unstructured_data IS '非结构化数据表，存储文件、图片等';

COMMENT ON COLUMN users.password IS '加密后的密码';
COMMENT ON COLUMN users.student_id IS '学号（学生用户）';
COMMENT ON COLUMN clubs.status IS '社团状态：ACTIVE, INACTIVE, SUSPENDED';
COMMENT ON COLUMN activities.status IS '活动状态：PLANNING, REGISTERING, ONGOING, COMPLETED, CANCELLED';
COMMENT ON COLUMN activity_participants.participation_status IS '参与状态：REGISTERED, CHECKED_IN, CHECKED_OUT, ABSENT';
COMMENT ON COLUMN resources.status IS '资源状态：AVAILABLE, IN_USE, MAINTENANCE, RESERVED';
COMMENT ON COLUMN resource_reservations.status IS '预约状态：PENDING, APPROVED, REJECTED, CANCELLED';