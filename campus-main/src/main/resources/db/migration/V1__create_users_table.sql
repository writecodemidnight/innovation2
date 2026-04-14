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
