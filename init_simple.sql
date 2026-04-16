-- Simple test data initialization
-- Run: F:\PostgreSQL\bin\psql -h localhost -p 5432 -U postgres -d campus_club -f init_simple.sql

-- Insert test user
INSERT INTO users (openid, nickname, role, created_at, updated_at)
VALUES ('test_openid_1', 'Manager', 'CLUB_MANAGER', NOW(), NOW());

-- Get the user id
INSERT INTO clubs (name, description, category, status, president_id, created_at, updated_at, member_count)
SELECT 'Test Club', 'A test club for development', 'ACADEMIC', 'ACTIVE', id, NOW(), NOW(), 1
FROM users WHERE openid = 'test_openid_1';

-- Verify
SELECT 'Users:' as item, COUNT(*) as count FROM users
UNION ALL
SELECT 'Clubs:', COUNT(*) FROM clubs;
