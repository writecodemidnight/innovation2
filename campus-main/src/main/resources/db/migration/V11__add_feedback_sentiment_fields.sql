-- 添加反馈评价的情感分析字段

-- 1. 添加情感分析相关字段
ALTER TABLE feedback
    ADD COLUMN IF NOT EXISTS sentiment_score DECIMAL(3, 2),
    ADD COLUMN IF NOT EXISTS sentiment_level VARCHAR(20),
    ADD COLUMN IF NOT EXISTS sentiment_confidence DECIMAL(3, 2);

-- 2. 创建关键词表（用于存储NLP提取的关键词）
CREATE TABLE IF NOT EXISTS feedback_keywords (
    feedback_id BIGINT NOT NULL REFERENCES feedback(id) ON DELETE CASCADE,
    keyword VARCHAR(100) NOT NULL,
    PRIMARY KEY (feedback_id, keyword)
);

-- 3. 创建索引优化查询
CREATE INDEX IF NOT EXISTS idx_feedback_sentiment_score ON feedback(sentiment_score);
CREATE INDEX IF NOT EXISTS idx_feedback_sentiment_level ON feedback(sentiment_level);

-- 4. 添加注释
COMMENT ON COLUMN feedback.sentiment_score IS 'NLP情感分析得分 0-1';
COMMENT ON COLUMN feedback.sentiment_level IS '情感等级: 非常正面/正面/中性/负面/非常负面';
COMMENT ON COLUMN feedback.sentiment_confidence IS '情感分析置信度';
