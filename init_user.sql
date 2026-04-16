-- Insert test user with all required fields
INSERT INTO users (openid, username, nickname, role, status, deleted, created_at, updated_at)
VALUES ('test_openid_1', 'testuser', 'Manager', 'CLUB_MANAGER', 'ACTIVE', false, NOW(), NOW());

-- Verify
SELECT id, username, nickname, role, status FROM users;
