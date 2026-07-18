-- name: CreateRegistration :one
INSERT INTO class_registrations (user_id, session_id, created_at, status)
VALUES (
    $1,
    $2,
    NOW(),
    $3
)
RETURNING *;

-- name: RemoveRegistrations :exec
DELETE FROM class_registrations;

-- name: QuerySessionIDRegistrations :many
SELECT * FROM class_registrations WHERE session_id = $1;

-- name: QueryUserIDRegistrations :many
SELECT * FROM class_registrations WHERE user_id = $1;

-- name: DeleteUserSessionRegistration :exec
DELETE FROM class_registrations
WHERE user_id = $1 AND session_id = $2;
