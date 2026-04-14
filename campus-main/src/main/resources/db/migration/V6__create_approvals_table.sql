CREATE TABLE IF NOT EXISTS approval_records (
    id BIGSERIAL PRIMARY KEY,
    target_type VARCHAR(50) NOT NULL,
    target_id BIGINT NOT NULL,
    applicant_id BIGINT NOT NULL REFERENCES users(id),
    approver_id BIGINT REFERENCES users(id),
    status VARCHAR(20) NOT NULL,
    submit_data JSONB,
    comment TEXT,
    submitted_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_approvals_target ON approval_records(target_type, target_id);
CREATE INDEX IF NOT EXISTS idx_approvals_status ON approval_records(status);
CREATE INDEX IF NOT EXISTS idx_approvals_applicant ON approval_records(applicant_id);
