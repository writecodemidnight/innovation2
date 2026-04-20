-- 创建反馈评价表
CREATE TABLE IF NOT EXISTS feedback (
    id BIGSERIAL PRIMARY KEY,
    activity_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建反馈图片表
CREATE TABLE IF NOT EXISTS feedback_images (
    feedback_id BIGINT NOT NULL,
    image_url VARCHAR(500) NOT NULL,
    FOREIGN KEY (feedback_id) REFERENCES feedback(id) ON DELETE CASCADE
);

-- 创建索引
CREATE INDEX idx_feedback_activity_id ON feedback(activity_id);
CREATE INDEX idx_feedback_user_id ON feedback(user_id);
CREATE INDEX idx_feedback_rating ON feedback(rating);
CREATE INDEX idx_feedback_created_at ON feedback(created_at);

-- 添加表注释
COMMENT ON TABLE feedback IS '活动反馈评价表';
COMMENT ON COLUMN feedback.id IS '评价ID';
COMMENT ON COLUMN feedback.activity_id IS '活动ID';
COMMENT ON COLUMN feedback.user_id IS '用户ID';
COMMENT ON COLUMN feedback.rating IS '评分(1-5星)';
COMMENT ON COLUMN feedback.content IS '评价内容';
COMMENT ON COLUMN feedback.created_at IS '创建时间';
COMMENT ON COLUMN feedback.updated_at IS '更新时间';
