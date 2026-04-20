CREATE TABLE IF NOT EXISTS activities (
    id BIGSERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    activity_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'PLANNING',
    CHECK (status IN ('PLANNING', 'PENDING_APPROVAL', 'APPROVED', 'REJECTED', 'REGISTERING', 'ONGOING', 'COMPLETED', 'CANCELLED')),
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    location VARCHAR(200),
    capacity INT,
    current_participants INT DEFAULT 0,
    club_id BIGINT REFERENCES clubs(id),
    created_by BIGINT REFERENCES users(id),
    cover_image_url VARCHAR(500),
    budget DECIMAL(10,2),
    required_resources JSONB,
    approval_status VARCHAR(20) DEFAULT 'NONE',
    approval_comment TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    deleted BOOLEAN DEFAULT FALSE,
    CHECK (end_time > start_time)
);

CREATE TABLE IF NOT EXISTS activity_participants (
    id BIGSERIAL PRIMARY KEY,
    activity_id BIGINT NOT NULL REFERENCES activities(id),
    user_id BIGINT NOT NULL REFERENCES users(id),
    status VARCHAR(20) DEFAULT 'REGISTERED',
    registered_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    checked_in_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    deleted BOOLEAN DEFAULT FALSE,
    UNIQUE(activity_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_activities_status ON activities(status);
CREATE INDEX IF NOT EXISTS idx_activities_club_id ON activities(club_id);
CREATE INDEX IF NOT EXISTS idx_activities_start_time ON activities(start_time);
CREATE INDEX IF NOT EXISTS idx_activities_type ON activities(activity_type);
CREATE INDEX IF NOT EXISTS idx_participants_activity_id ON activity_participants(activity_id);
CREATE INDEX IF NOT EXISTS idx_participants_user_id ON activity_participants(user_id);
