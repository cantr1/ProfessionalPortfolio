-- +goose Up
CREATE TABLE meditation_sessions (
    id UUID PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
 
    meditation_start TIMESTAMPTZ NOT NULL,
    meditation_end TIMESTAMPTZ NOT NULL,
 
    starting_hr INTEGER NOT NULL CHECK (starting_hr <= 180 AND starting_hr >= 40),
    ending_hr INTEGER NOT NULL CHECK (ending_hr <= 180 AND ending_hr >= 40),
 
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE
);
 
-- +goose Down
DROP TABLE meditation_sessions;
