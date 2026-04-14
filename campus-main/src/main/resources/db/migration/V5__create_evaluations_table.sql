CREATE TABLE IF NOT EXISTS evaluations (
    id BIGSERIAL PRIMARY KEY,
    activity_id BIGINT NOT NULL UNIQUE REFERENCES activities(id),
    participant_count INT,
    satisfaction_score DECIMAL(3,2),
    participation_score DECIMAL(5,2),
    educational_score DECIMAL(5,2),
    innovation_score DECIMAL(5,2),
    influence_score DECIMAL(5,2),
    sustainability_score DECIMAL(5,2),
    overall_score DECIMAL(5,2),
    algorithm_version VARCHAR(50),
    radar_chart_data JSONB,
    generated_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS activity_feedbacks (
    id BIGSERIAL PRIMARY KEY,
    activity_id BIGINT NOT NULL REFERENCES activities(id),
    user_id BIGINT NOT NULL REFERENCES users(id),
    rating INT NOT NULL CHECK (rating >= 1 AND rating <= 5),
    content TEXT,
    sentiment_score DECIMAL(3,2),
    photos JSONB,
    is_anonymous BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(activity_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_evaluations_activity_id ON evaluations(activity_id);
CREATE INDEX IF NOT EXISTS idx_feedbacks_activity_id ON activity_feedbacks(activity_id);
CREATE INDEX IF NOT EXISTS idx_feedbacks_user_id ON activity_feedbacks(user_id);
