-- +goose Up
CREATE TABLE sessions (
    id UUID PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    start_time TIMESTAMPTZ NOT NULL,
    end_time TIMESTAMPTZ NOT NULL,
    instructor_id UUID NOT NULL REFERENCES users(id),
    difficulty INT NOT NULL CHECK (difficulty BETWEEN 1 AND 5),
    class_size INT NOT NULL,
    description TEXT NOT NULL
);

-- +goose Down
DROP TABLE sessions;
