CREATE TABLE IF NOT EXISTS resources (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    description TEXT,
    capacity INT,
    available_count INT DEFAULT 0,
    total_count INT NOT NULL,
    unit VARCHAR(20),
    location VARCHAR(200),
    manager_id BIGINT REFERENCES users(id),
    constraints JSONB,
    status VARCHAR(20) DEFAULT 'AVAILABLE',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    deleted BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS resource_reservations (
    id BIGSERIAL PRIMARY KEY,
    resource_id BIGINT NOT NULL REFERENCES resources(id),
    activity_id BIGINT REFERENCES activities(id),
    applicant_id BIGINT NOT NULL REFERENCES users(id),
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    quantity INT DEFAULT 1,
    status VARCHAR(20) DEFAULT 'PENDING',
    purpose TEXT,
    approval_comment TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    CHECK (end_time > start_time)
);

CREATE INDEX IF NOT EXISTS idx_resources_type ON resources(resource_type);
CREATE INDEX IF NOT EXISTS idx_resources_status ON resources(status);
CREATE INDEX IF NOT EXISTS idx_reservations_resource_id ON resource_reservations(resource_id);
CREATE INDEX IF NOT EXISTS idx_reservations_activity_id ON resource_reservations(activity_id);
CREATE INDEX IF NOT EXISTS idx_reservations_time_range ON resource_reservations(start_time, end_time);
