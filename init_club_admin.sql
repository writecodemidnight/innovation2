-- Create club admin user and club
-- Password: admin123 (for reference, actual auth may use WeChat)

-- 1. Create club admin user
INSERT INTO users (openid, username, nickname, role, status, deleted, created_at, updated_at)
VALUES ('club_admin_1', 'clubadmin', 'Club Manager', 'CLUB_MANAGER', 'ACTIVE', false, NOW(), NOW());

-- Get the user ID
DO $$
DECLARE
    admin_id BIGINT;
BEGIN
    SELECT id INTO admin_id FROM users WHERE username = 'clubadmin';

    -- 2. Create a club with this user as president
    INSERT INTO clubs (name, description, category, status, president_id, created_at, updated_at, member_count)
    VALUES ('Computer Science Club', 'Programming and tech activities', 'ACADEMIC', 'ACTIVE', admin_id, NOW(), NOW(), 1);

    RAISE NOTICE 'Created club admin user ID: %', admin_id;
END $$;

-- Verify
SELECT u.id, u.username, u.nickname, u.role, c.id as club_id, c.name as club_name
FROM users u
LEFT JOIN clubs c ON c.president_id = u.id
WHERE u.username = 'clubadmin';
