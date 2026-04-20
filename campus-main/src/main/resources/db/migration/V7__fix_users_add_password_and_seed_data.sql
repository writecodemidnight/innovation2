-- ============================================
-- 修复用户表结构并添加种子数据
-- 版本: V7
-- ============================================

-- 添加 password 字段（如果不存在）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'users' AND column_name = 'password') THEN
        ALTER TABLE users ADD COLUMN password VARCHAR(255);
    END IF;
END $$;

-- 添加 real_name 字段（如果不存在）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'users' AND column_name = 'real_name') THEN
        ALTER TABLE users ADD COLUMN real_name VARCHAR(50);
    END IF;
END $$;

-- 删除可能存在的冲突唯一约束
ALTER TABLE users DROP CONSTRAINT IF EXISTS users_username_key;
ALTER TABLE users DROP CONSTRAINT IF EXISTS uk_username;

-- 添加唯一约束（如果不存在）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint
                   WHERE conname = 'uk_username' AND conrelid = 'users'::regclass) THEN
        ALTER TABLE users ADD CONSTRAINT uk_username UNIQUE (username);
    END IF;
END $$;

-- 插入测试用户数据（密码均为 'admin123' 的 BCrypt 加密）
-- 密码明文: admin123
-- BCrypt加密值: $2a$10$N.zmdr9k7uOCQb376NoUnuTJ8iAt6Z5EHsM8lE9lBOsl7iAt6Z5EO
INSERT INTO users (username, password, email, real_name, student_id, role, status, deleted, created_at)
VALUES
    ('admin', '$2a$10$N.zmdr9k7uOCQb376NoUnuTJ8iAt6Z5EHsM8lE9lBOsl7iAt6Z5EO', 'admin@campus.edu', '系统管理员', 'ADMIN001', 'ADMIN', 'ACTIVE', false, NOW()),
    ('club1', '$2a$10$N.zmdr9k7uOCQb376NoUnuTJ8iAt6Z5EHsM8lE9lBOsl7iAt6Z5EO', 'club1@campus.edu', '社团管理员1', '2021001', 'CLUB_PRESIDENT', 'ACTIVE', false, NOW()),
    ('student1', '$2a$10$N.zmdr9k7uOCQb376NoUnuTJ8iAt6Z5EHsM8lE9lBOsl7iAt6Z5EO', 'stu1@campus.edu', '张三', '2021002', 'STUDENT', 'ACTIVE', false, NOW()),
    ('student2', '$2a$10$N.zmdr9k7uOCQb376NoUnuTJ8iAt6Z5EHsM8lE9lBOsl7iAt6Z5EO', 'stu2@campus.edu', '李四', '2021003', 'STUDENT', 'ACTIVE', false, NOW())
ON CONFLICT (username) DO UPDATE SET
    password = EXCLUDED.password,
    email = EXCLUDED.email,
    real_name = EXCLUDED.real_name,
    role = EXCLUDED.role,
    status = EXCLUDED.status,
    updated_at = NOW();
