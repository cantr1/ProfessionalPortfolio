-- +goose Up
CREATE TABLE sleep_sessions (
    id UUID PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    sleep_start TIMESTAMPTZ NOT NULL,
    sleep_end TIMESTAMPTZ NOT NULL,

    rem_duration_mins INT NOT NULL CHECK (rem_duration_mins >= 0),
    light_duration_mins INT NOT NULL CHECK (light_duration_mins >= 0),
    deep_duration_mins INT NOT NULL CHECK (deep_duration_mins >= 0),

    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE
);

-- +goose Down
DROP TABLE sleep_sessions;