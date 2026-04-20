-- ============================================
-- 添加测试社团和成员数据（简化版）
-- ============================================

-- 插入测试社团
INSERT INTO clubs (id, name, description, category, status, created_at, updated_at, deleted)
VALUES
    (1, '科技创新社', '专注于科技创新和编程开发的社团', 'TECHNOLOGY', 'ACTIVE', NOW(), NOW(), false)
ON CONFLICT DO NOTHING;

-- 插入测试活动
INSERT INTO activities (id, club_id, title, description, location, start_time, end_time, capacity, activity_type, status, approval_status, created_by, created_at, updated_at, deleted)
VALUES
    (1, 1, '编程入门工作坊', '面向新生的编程基础培训', '教学楼A101', NOW() + INTERVAL '7 days', NOW() + INTERVAL '8 days', 50, 'WORKSHOP', 'APPROVED', 'APPROVED', 1, NOW(), NOW(), false)
ON CONFLICT DO NOTHING;
