-- 添加乐观锁版本号和唯一约束

-- 1. activities 表添加 version 字段
ALTER TABLE activities ADD COLUMN IF NOT EXISTS version BIGINT DEFAULT 0;

-- 2. activity_participants 表添加 version 字段
ALTER TABLE activity_participants ADD COLUMN IF NOT EXISTS version BIGINT DEFAULT 0;

-- 3. activity_participants 表添加唯一约束（防止重复报名）
DO $$
BEGIN
    -- 先删除可能存在的旧约束
    IF EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'uk_activity_user'
        AND conrelid = 'activity_participants'::regclass
    ) THEN
        ALTER TABLE activity_participants DROP CONSTRAINT uk_activity_user;
    END IF;

    -- 删除已存在的重复记录（保留最新的）
    DELETE FROM activity_participants a
    USING activity_participants b
    WHERE a.id < b.id
    AND a.activity_id = b.activity_id
    AND a.user_id = b.user_id;

    -- 添加唯一约束
    ALTER TABLE activity_participants
    ADD CONSTRAINT uk_activity_user
    UNIQUE (activity_id, user_id);
END $$;

-- 4. 创建索引优化查询
CREATE INDEX IF NOT EXISTS idx_activity_participants_user_id ON activity_participants(user_id);
CREATE INDEX IF NOT EXISTS idx_activity_participants_activity_id ON activity_participants(activity_id);
CREATE INDEX IF NOT EXISTS idx_activity_participants_status ON activity_participants(status);

COMMENT ON COLUMN activities.version IS '乐观锁版本号';
COMMENT ON COLUMN activity_participants.version IS '乐观锁版本号';
COMMENT ON CONSTRAINT uk_activity_user ON activity_participants IS '防止用户重复报名同一活动';
