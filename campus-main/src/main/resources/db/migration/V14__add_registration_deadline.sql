-- 添加报名截止时间字段到活动表
ALTER TABLE activities ADD COLUMN IF NOT EXISTS registration_deadline TIMESTAMP;