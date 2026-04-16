-- 初始化测试数据
-- 运行方式: F:\PostgreSQL\bin\psql -h localhost -p 5432 -U postgres -d campus_club -f init_test_data.sql

-- 清空现有数据（可选，谨慎使用）
-- TRUNCATE TABLE activity_participants, evaluations, resources, resource_applications, activities, club_members, clubs, users CASCADE;

-- 插入测试用户
INSERT INTO users (id, openid, nickname, avatar_url, role, student_id, phone, created_at, updated_at)
VALUES
(1, 'test_openid_1', '社团管理员1', 'https://example.com/avatar1.jpg', 'CLUB_MANAGER', '2021001001', '13800138001', NOW(), NOW()),
(2, 'test_openid_2', '社团管理员2', 'https://example.com/avatar2.jpg', 'CLUB_MANAGER', '2021001002', '13800138002', NOW(), NOW()),
(3, 'test_openid_3', '学生用户1', 'https://example.com/avatar3.jpg', 'STUDENT', '2021001003', '13800138003', NOW(), NOW()),
(4, 'test_openid_4', '学生用户2', 'https://example.com/avatar4.jpg', 'STUDENT', '2021001004', '13800138004', NOW(), NOW()),
(5, 'test_openid_5', '系统管理员', 'https://example.com/avatar5.jpg', 'ADMIN', '2021001005', '13800138005', NOW(), NOW())
ON CONFLICT (id) DO NOTHING;

-- 重置序列
SELECT setval('users_id_seq', (SELECT MAX(id) FROM users));

-- 插入测试社团
INSERT INTO clubs (id, name, description, category, logo_url, status, president_id, teacher_id, created_at, updated_at, member_count)
VALUES
(1, '计算机协会', '致力于计算机技术学习和交流，定期举办编程比赛和技术分享会。', '学术科技', 'https://example.com/club1.jpg', 'ACTIVE', 1, NULL, NOW(), NOW(), 50),
(2, '音乐社', '热爱音乐的同学们聚集的地方，有合唱团、乐队等多个分支。', '文化艺术', 'https://example.com/club2.jpg', 'ACTIVE', 2, NULL, NOW(), NOW(), 80),
(3, '篮球社', '篮球爱好者的天堂，定期组织训练和友谊赛。', '体育竞技', 'https://example.com/club3.jpg', 'ACTIVE', 1, NULL, NOW(), NOW(), 60)
ON CONFLICT (id) DO NOTHING;

SELECT setval('clubs_id_seq', (SELECT MAX(id) FROM clubs));

-- 插入社团成员关系
INSERT INTO club_members (club_id, user_id, role, joined_at)
VALUES
(1, 1, 'PRESIDENT', NOW()),
(1, 3, 'MEMBER', NOW()),
(1, 4, 'MEMBER', NOW()),
(2, 2, 'PRESIDENT', NOW()),
(2, 3, 'MEMBER', NOW()),
(3, 1, 'PRESIDENT', NOW())
ON CONFLICT DO NOTHING;

-- 插入测试活动
INSERT INTO activities (id, club_id, title, description, location, start_time, end_time, max_participants, status, created_by, created_at, updated_at, participant_count)
VALUES
(1, 1, '编程马拉松大赛', '24小时编程挑战赛，展示你的编程实力！', '计算机楼301', NOW() + INTERVAL '7 days', NOW() + INTERVAL '8 days', 100, 'APPROVED', 1, NOW(), NOW(), 45),
(2, 1, '技术分享会：AI前沿', '邀请业界专家分享人工智能最新进展', '图书馆报告厅', NOW() + INTERVAL '14 days', NOW() + INTERVAL '14 days' + INTERVAL '2 hours', 200, 'APPROVED', 1, NOW(), NOW(), 120),
(3, 2, '春季音乐会', '音乐社年度大型演出活动', '大礼堂', NOW() + INTERVAL '30 days', NOW() + INTERVAL '30 days' + INTERVAL '3 hours', 500, 'PENDING', 2, NOW(), NOW(), 0),
(4, 3, '篮球友谊赛', '与兄弟院校的友谊比赛', '体育馆', NOW() - INTERVAL '7 days', NOW() - INTERVAL '7 days' + INTERVAL '2 hours', 50, 'COMPLETED', 1, NOW(), NOW(), 48)
ON CONFLICT (id) DO NOTHING;

SELECT setval('activities_id_seq', (SELECT MAX(id) FROM activities));

-- 插入活动参与记录
INSERT INTO activity_participants (activity_id, user_id, status, registered_at, check_in_time)
VALUES
(1, 3, 'REGISTERED', NOW(), NULL),
(1, 4, 'REGISTERED', NOW(), NULL),
(4, 3, 'ATTENDED', NOW() - INTERVAL '7 days', NOW() - INTERVAL '7 days'),
(4, 4, 'ATTENDED', NOW() - INTERVAL '7 days', NOW() - INTERVAL '7 days')
ON CONFLICT DO NOTHING;

-- 插入资源数据
INSERT INTO resources (id, name, type, location, capacity, description, status, manager_id, created_at, updated_at)
VALUES
(1, '大礼堂', 'VENUE', '活动中心一楼', 800, '配备音响、灯光、舞台的大型活动场地', 'AVAILABLE', 5, NOW(), NOW()),
(2, '计算机楼301', 'CLASSROOM', '计算机楼3楼', 120, '多媒体教室，配备投影仪和电脑', 'AVAILABLE', 5, NOW(), NOW()),
(3, '图书馆报告厅', 'VENUE', '图书馆2楼', 300, '中型报告厅，适合讲座和会议', 'AVAILABLE', 5, NOW(), NOW()),
(4, '体育馆', 'VENUE', '体育馆主馆', 1000, '标准篮球场，可进行各类体育赛事', 'AVAILABLE', 5, NOW(), NOW()),
(5, '投影仪', 'EQUIPMENT', '设备仓库', 10, '便携式投影仪，需提前预约', 'AVAILABLE', 5, NOW(), NOW())
ON CONFLICT (id) DO NOTHING;

SELECT setval('resources_id_seq', (SELECT MAX(id) FROM resources));

-- 插入资源预约申请
INSERT INTO resource_applications (id, resource_id, club_id, activity_id, applicant_id, start_time, end_time, purpose, status, created_at, updated_at)
VALUES
(1, 2, 1, 1, 1, NOW() + INTERVAL '7 days', NOW() + INTERVAL '8 days', '编程马拉松比赛场地', 'APPROVED', NOW(), NOW()),
(2, 3, 1, 2, 1, NOW() + INTERVAL '14 days', NOW() + INTERVAL '14 days' + INTERVAL '2 hours', '技术分享会场地', 'PENDING', NOW(), NOW()),
(3, 1, 2, 3, 2, NOW() + INTERVAL '30 days', NOW() + INTERVAL '30 days' + INTERVAL '3 hours', '春季音乐会演出场地', 'PENDING', NOW(), NOW())
ON CONFLICT (id) DO NOTHING;

SELECT setval('resource_applications_id_seq', (SELECT MAX(id) FROM resource_applications));

-- 插入评价数据
INSERT INTO evaluations (id, activity_id, user_id, overall_score, organization_score, content_score, interaction_score, satisfaction_score, comment, created_at)
VALUES
(1, 4, 3, 4.5, 4.0, 4.5, 5.0, 4.5, '比赛组织得很好，下次还想参加！', NOW() - INTERVAL '6 days'),
(2, 4, 4, 4.0, 4.0, 4.0, 4.0, 4.0, '体验不错，就是场地有点热', NOW() - INTERVAL '6 days')
ON CONFLICT (id) DO NOTHING;

SELECT setval('evaluations_id_seq', (SELECT MAX(id) FROM evaluations));

-- 验证数据
SELECT 'Users count:' as info, COUNT(*) FROM users
UNION ALL
SELECT 'Clubs count:', COUNT(*) FROM clubs
UNION ALL
SELECT 'Activities count:', COUNT(*) FROM activities
UNION ALL
SELECT 'Resources count:', COUNT(*) FROM resources;
