-- PostgreSQL数据库初始化脚本
-- 在psql中运行: \i init-database.sql 或复制粘贴执行

-- 1. 创建数据库（如果不存在）
SELECT 'CREATE DATABASE campus_club_dev'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'campus_club_dev');

-- 2. 创建用户（如果不存在）
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'campus_user') THEN
        CREATE USER campus_user WITH PASSWORD 'dev_password_123';
    END IF;
END
$$;

-- 3. 授权（需要在连接到campus_club_dev数据库后执行）
-- \c campus_club_dev
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO campus_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO campus_user;
-- ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO campus_user;
-- ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO campus_user;
