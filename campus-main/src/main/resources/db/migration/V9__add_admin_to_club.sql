-- ============================================
-- 添加管理员到社团成员表 (修复版)
-- 目的：让管理员账号可以访问社团仪表盘
-- ============================================

-- 先删除可能存在的重复记录，确保干净
DELETE FROM club_members WHERE club_id = 1 AND user_id IN (SELECT id FROM users WHERE username = 'admin');

-- 将 admin 用户添加到科技创新社，设置为社长角色
INSERT INTO club_members (club_id, user_id, role, joined_at, created_at, updated_at, deleted)
SELECT 1, id, 'PRESIDENT', NOW(), NOW(), NOW(), false
FROM users
WHERE username = 'admin';
