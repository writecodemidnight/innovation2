-- 修复测试学生用户 - 使用正确的密码hash（密码：123456）
-- 先删除可能存在的错误用户
DELETE FROM users WHERE username = 'test_student';

-- 插入正确的测试用户
-- 使用 BCrypt 加密 '123456' 的 hash（与 V7 中的密码一致）
INSERT INTO users (username, password, email, real_name, student_id, role, status, deleted, created_at)
VALUES (
    'test_student',
    '$2a$10$N.zmdr9k7uOCQb376NoUnuTJ8iAt6Z5EHsM8lE9lBOsl7iAt6Z5EO',
    'test@campus.edu',
    '测试学生',
    '2024001001',
    'STUDENT',
    'ACTIVE',
    false,
    NOW()
);
