-- +goose Up
CREATE TABLE exercise_sessions (
    id UUID PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    workout_start TIMESTAMPTZ NOT NULL,
    workout_end TIMESTAMPTZ NOT NULL,
    workout_name TEXT NOT NULL,

    zone1_mins INT NOT NULL CHECK (zone1_mins >= 0),
    zone2_mins INT NOT NULL CHECK (zone2_mins >= 0),
    zone3_mins INT NOT NULL CHECK (zone3_mins >= 0),

    strain INT NOT NULL CHECK (strain >= 0 AND strain <= 10),

    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE
);

-- +goose Down
DROP TABLE exercise_sessions;