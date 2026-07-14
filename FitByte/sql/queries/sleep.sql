-- name: CreateSleepSession :one
INSERT INTO sleep_sessions (id, created_at, updated_at, sleep_start, sleep_end, rem_duration_mins, light_duration_mins, deep_duration_mins, user_id)
VALUES (
    gen_random_uuid(),
    NOW(),
    NOW(),
    $1,
    $2,
    $3,
    $4,
    $5,
    $6
)
RETURNING *;

-- name: RemoveSleeps :exec
DELETE FROM sleep_sessions;

-- name: QuerySleepSession :one
SELECT * FROM sleep_sessions WHERE id = $1;

-- name: QueryUserSleepSessions :many
SELECT * FROM sleep_sessions WHERE user_id = $1;