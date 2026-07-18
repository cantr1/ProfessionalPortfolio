-- name: CreateUser :one
INSERT INTO users (id, created_at, updated_at, email, name, password_hash, is_instructor)
VALUES (
    gen_random_uuid(),
    NOW(),
    NOW(),
    $1,
    $2,
    $3,
    $4
)
RETURNING *;

-- name: RemoveUsers :exec
DELETE FROM users;

-- name: QueryUserEmail :one
SELECT * FROM users WHERE email = $1;

-- name: QueryUserID :one
SELECT * FROM users WHERE id = $1;