-- +goose Up
CREATE TABLE users (
    id UUID PRIMARY KEY, 
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    email TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    is_instructor BOOLEAN DEFAULT FALSE
);

-- +goose Down
DROP TABLE users;
