-- name: CreateMeditationSession :one
INSERT INTO meditation_sessions (id, created_at, updated_at, meditation_start, meditation_end, starting_hr, ending_hr, user_id)
VALUES (
    gen_random_uuid(),
    NOW(),
    NOW(),
    $1,
    $2,
    $3,
    $4,
    $5
)
RETURNING *;
 
-- name: RemoveMeditations :exec
DELETE FROM meditation_sessions;
 
-- name: MeditationSession :one
SELECT * FROM meditation_sessions WHERE id = $1;
 
-- name: QueryUserMeditationSessions :many
SELECT * FROM meditation_sessions WHERE user_id = $1;