-- 添加反馈多维度评分字段（V16版本，因为V15已被修改）
ALTER TABLE feedback
    ADD COLUMN IF NOT EXISTS organization_rating INTEGER,
    ADD COLUMN IF NOT EXISTS content_rating INTEGER;

-- 添加注释
COMMENT ON COLUMN feedback.organization_rating IS '活动组织评分 1-5';
COMMENT ON COLUMN feedback.content_rating IS '活动内容评分 1-5';
