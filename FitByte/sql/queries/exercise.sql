-- name: CreateExerciseSession :one
INSERT INTO exercise_sessions (id, created_at, updated_at, workout_start, workout_end, workout_name, zone1_mins, zone2_mins, zone3_mins, strain, user_id)
VALUES (
    gen_random_uuid(),
    NOW(),
    NOW(),
    $1,
    $2,
    $3,
    $4,
    $5,
    $6,
    $7,
    $8
)
RETURNING *;

-- name: RemoveExercises :exec
DELETE FROM exercise_sessions;

-- name: QueryExerciseSessions :one
SELECT * FROM exercise_sessions WHERE id = $1;

-- name: QueryUserExercieSessions :many
SELECT * FROM exercise_sessions WHERE user_id = $1;