-- 添加学生端测试用户
-- 用于微信小程序联调测试
-- 密码明文: 123456
-- BCrypt加密值: $2a$10$N.zmdr9k7uOCQb376NoUnuTJ8iAt6Z5EHsM8lE9lBOsl7iAt6Z5EO

INSERT INTO users (username, password, email, real_name, student_id, role, status, deleted, created_at)
VALUES
    ('test_student', '$2a$10$N.zmdr9k7uOCQb376NoUnuTJ8iAt6Z5EHsM8lE9lBOsl7iAt6Z5EO', 'test@campus.edu', '测试学生', '2024001001', 'STUDENT', 'ACTIVE', false, NOW())
ON CONFLICT (username) DO UPDATE SET
    password = EXCLUDED.password,
    email = EXCLUDED.email,
    real_name = EXCLUDED.real_name,
    role = EXCLUDED.role,
    status = EXCLUDED.status,
    updated_at = NOW();
