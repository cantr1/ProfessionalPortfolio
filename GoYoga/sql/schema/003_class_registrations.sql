-- +goose Up
CREATE TABLE class_registrations (
    user_id UUID NOT NULL REFERENCES users(id),
    session_id UUID NOT NULL REFERENCES sessions(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status TEXT NOT NULL,
    PRIMARY KEY (user_id, session_id)
);

-- +goose Down
DROP TABLE class_registrations;
