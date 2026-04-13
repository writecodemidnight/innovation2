-- ============================================
-- V5: 外部数据与算法特征表
-- 精简版 - 仅保留算法必需的表结构
-- ============================================

-- 1. 学生特征表（供K-Means聚类使用）
CREATE TABLE IF NOT EXISTS student_features (
    id BIGSERIAL PRIMARY KEY,
    student_id VARCHAR(20) UNIQUE NOT NULL REFERENCES students(student_id),
    -- 五维评估特征（0-1标准化）
    participation_score DECIMAL(3,2) DEFAULT 0.0,      -- 参与度
    influence_score DECIMAL(3,2) DEFAULT 0.0,          -- 影响力
    satisfaction_score DECIMAL(3,2) DEFAULT 0.0,       -- 满意度
    activity_diversity_score DECIMAL(3,2) DEFAULT 0.0, -- 活动多样性
    leadership_score DECIMAL(3,2) DEFAULT 0.0,         -- 组织力
    -- 聚类结果
    cluster_id INTEGER DEFAULT -1,                      -- K-Means聚类标签
    cluster_confidence DECIMAL(3,2) DEFAULT 0.0,       -- 聚类置信度
    persona_type VARCHAR(50),                          -- 角色类型
    -- 元数据
    feature_vector JSONB,                              -- 原始特征向量（备用）
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_student_features_cluster ON student_features(cluster_id);
CREATE INDEX idx_student_features_persona ON student_features(persona_type);

-- 2. 社团评分表（供AHP层次分析使用）
CREATE TABLE IF NOT EXISTS club_evaluation_ahp (
    id BIGSERIAL PRIMARY KEY,
    club_id VARCHAR(20) UNIQUE NOT NULL REFERENCES clubs(club_id),
    -- AHP准则层权重计算结果
    activity_quality_score DECIMAL(4,2) DEFAULT 0.0,   -- 活动质量得分
    member_satisfaction_score DECIMAL(4,2) DEFAULT 0.0, -- 成员满意度
    organization_score DECIMAL(4,2) DEFAULT 0.0,       -- 组织建设得分
    influence_score DECIMAL(4,2) DEFAULT 0.0,          -- 影响力得分
    sustainability_score DECIMAL(4,2) DEFAULT 0.0,     -- 可持续发展得分
    -- AHP结果
    comprehensive_score DECIMAL(4,2) DEFAULT 0.0,      -- 综合得分
    rating_level VARCHAR(20) CHECK (rating_level IN ('A', 'B', 'C', 'D')),
    evaluation_period VARCHAR(20),                      -- 评估周期（如：2024-S1）
    -- 元数据
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_club_evaluation_rating ON club_evaluation_ahp(rating_level);

-- 3. 时间序列预测特征（供LSTM使用）
CREATE TABLE IF NOT EXISTS activity_timeseries_features (
    id BIGSERIAL PRIMARY KEY,
    activity_id BIGINT REFERENCES activities(id),
    -- 时间特征
    year INTEGER,
    month INTEGER,
    week_of_year INTEGER,
    day_of_week INTEGER,
    is_weekend BOOLEAN DEFAULT FALSE,
    is_exam_period BOOLEAN DEFAULT FALSE,
    semester VARCHAR(20),                              -- 学期标识
    time_slot VARCHAR(20),                             -- 时段（morning/afternoon/evening）
    -- 历史统计特征（滑动窗口）
    avg_participants_4w DECIMAL(8,2),                  -- 近4周平均参与人数
    activity_count_4w INTEGER DEFAULT 0,               -- 近4周活动数
    participation_trend DECIMAL(4,2),                  -- 参与趋势（上升/下降）
    -- 预测结果
    predicted_participants INTEGER,                    -- LSTM预测参与人数
    prediction_confidence DECIMAL(3,2),                -- 预测置信度
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_timeseries_activity ON activity_timeseries_features(activity_id);
CREATE INDEX idx_timeseries_semester ON activity_timeseries_features(semester, year);

-- 4. 资源调度优化记录（供GA遗传算法使用）
CREATE TABLE IF NOT EXISTS resource_schedule_optimization (
    id BIGSERIAL PRIMARY KEY,
    batch_id VARCHAR(50) NOT NULL,                      -- 批次ID
    activity_id BIGINT REFERENCES activities(id),
    -- 资源分配结果
    assigned_resource VARCHAR(100),                    -- 分配的资源
    scheduled_start_time TIMESTAMP,                    -- 优化后的开始时间
    scheduled_end_time TIMESTAMP,                      -- 优化后的结束时间
    -- GA优化指标
    conflict_score INTEGER DEFAULT 0,                  -- 冲突评分（越低越好）
    utilization_rate DECIMAL(4,2),                     -- 资源利用率
    satisfaction_score DECIMAL(4,2),                   -- 满意度评分
    -- 算法参数
    ga_generation INTEGER DEFAULT 0,                   -- 进化代数
    population_size INTEGER DEFAULT 0,                 -- 种群大小
    -- 状态
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'optimized', 'applied', 'cancelled')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    optimized_at TIMESTAMP
);

CREATE INDEX idx_resource_schedule_batch ON resource_schedule_optimization(batch_id);
CREATE INDEX idx_resource_schedule_status ON resource_schedule_optimization(status);

-- 5. 数据导入任务记录（简化版）
CREATE TABLE IF NOT EXISTS data_import_jobs (
    id BIGSERIAL PRIMARY KEY,
    job_type VARCHAR(50) NOT NULL CHECK (job_type IN ('simulation', 'historical')),
    source_info VARCHAR(500),                          -- 数据来源描述
    records_count INTEGER DEFAULT 0,                   -- 导入记录数
    quality_score INTEGER CHECK (quality_score BETWEEN 0 AND 100),
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'running', 'success', 'failed')),
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 触发器：自动更新 updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS update_student_features_modtime ON student_features;
CREATE TRIGGER update_student_features_modtime
    BEFORE UPDATE ON student_features
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_club_evaluation_modtime ON club_evaluation_ahp;
CREATE TRIGGER update_club_evaluation_modtime
    BEFORE UPDATE ON club_evaluation_ahp
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- 插入测试数据提示
COMMENT ON TABLE student_features IS '学生特征表 - 供K-Means聚类使用';
COMMENT ON TABLE club_evaluation_ahp IS '社团AHP评估表 - 五维综合评价';
COMMENT ON TABLE activity_timeseries_features IS '时间序列特征表 - 供LSTM预测使用';
COMMENT ON TABLE resource_schedule_optimization IS '资源调度优化表 - 供GA算法使用';
