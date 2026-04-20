-- 在 pgAdmin 中执行此脚本清理 Flyway 状态

-- 1. 删除失败的 V9 迁移记录
DELETE FROM flyway_schema_history WHERE version = '9';

-- 2. 手动添加 admin 到社团（如果不存在）
INSERT INTO club_members (club_id, user_id, role, joined_at, created_at, updated_at, deleted)
SELECT 1, id, 'PRESIDENT', NOW(), NOW(), NOW(), false
FROM users WHERE username = 'admin'
ON CONFLICT DO NOTHING;

-- 3. 验证
SELECT * FROM club_members WHERE user_id IN (SELECT id FROM users WHERE username = 'admin');
