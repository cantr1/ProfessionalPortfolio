# FitByte API Documentation

This API is served by the Go application in `main.go`. JSON endpoints are mounted under `/api`, while the static frontend is served under `/web/`.

## Base URL

Local development usually uses:

```text
http://localhost:8080
```

Use the host and port configured by the `PORT` environment variable.

## Authentication

Most API endpoints use bearer tokens:

```http
Authorization: Bearer <token>
```

There are four credential types in the project:

| Token | Used By | Source |
| --- | --- | --- |
| User creation token | `POST /api/users` | `USER_CREATION_TOKEN` env var |
| Access token | Sleep, exercise, and meditation endpoints | Returned by `POST /api/login` or `POST /api/refresh` |
| Refresh token | `POST /api/refresh`, `POST /api/revoke` | Returned by `POST /api/login` |
| Admin key | Reset/delete endpoints | `ADMIN_KEY` env var |

Access tokens are JWTs signed with `TOKEN_SECRET`. Refresh tokens are random strings stored in the database and expire after 60 days.

## Common Data Formats

- Time fields use JSON strings parseable by Go's `time.Time`, such as ISO 8601/RFC3339 values: `2026-07-12T15:00:00Z`.
- IDs are UUID strings.
- Error responses are plain text created with `http.Error`.
- Successful JSON responses use `Content-Type: application/json`.

Note: Sleep duration fields are named as minutes. The request handler currently decodes them as `time.Duration` values and stores the integer conversion in minute-named database columns. Clients should send whole numbers, as shown in the examples.

## Health

### `GET /api/healthy`

Returns a basic service health response.

**Auth:** None

**Success:** `200 OK`

```json
{
  "string": "online/healthy"
}
```

## Users and Sessions

### `POST /api/users`

Creates a user.

**Auth:** `Authorization: Bearer <USER_CREATION_TOKEN>`

**Request body:**

```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Success:** `201 Created`

```json
{
  "user_id": "uuid",
  "email": "user@example.com",
  "created_at": "timestamp",
  "updated_at": "timestamp"
}
```

**Common errors:**

| Status | Cause |
| --- | --- |
| `400 Bad Request` | Invalid JSON or missing `email`/`password` |
| `401 Unauthorized` | Missing/malformed authorization header |
| `403 Forbidden` | User creation token does not match |
| `500 Internal Server Error` | Password hashing, database, or JSON encoding failure |

### `POST /api/login`

Authenticates a user and returns an access token plus refresh token.

**Auth:** None

**Request body:**

```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Success:** `200 OK`

```json
{
  "id": "uuid",
  "created_at": "timestamp",
  "updated_at": "timestamp",
  "email": "user@example.com",
  "token": "jwt-access-token",
  "refresh_token": "refresh-token"
}
```

**Common errors:**

| Status | Cause |
| --- | --- |
| `400 Bad Request` | Invalid JSON or missing `email`/`password` |
| `401 Unauthorized` | Password does not match |
| `404 Not Found` | No user exists for the supplied email |
| `500 Internal Server Error` | Token creation, database, or JSON encoding failure |

### `POST /api/refresh`

Creates a new JWT access token from a valid refresh token.

**Auth:** `Authorization: Bearer <refresh_token>`

**Request body:** None

**Success:** `200 OK`

```json
{
  "token": "new-jwt-access-token"
}
```

**Common errors:**

| Status | Cause |
| --- | --- |
| `400 Bad Request` | Missing bearer token |
| `401 Unauthorized` | Refresh token is invalid, revoked, or expired |
| `500 Internal Server Error` | Database, token creation, or JSON encoding failure |

### `POST /api/revoke`

Revokes a refresh token.

**Auth:** `Authorization: Bearer <refresh_token>`

**Request body:** None

**Success:** `204 No Content`

**Common errors:**

| Status | Cause |
| --- | --- |
| `400 Bad Request` | Missing bearer token or token already revoked |
| `401 Unauthorized` | Refresh token does not exist |
| `500 Internal Server Error` | Database failure |

## Sleep Sessions

### `POST /api/sleeps`

Creates a sleep session for the authenticated user.

**Auth:** `Authorization: Bearer <access_token>`

**Request body:**

```json
{
  "sleep_start": "2026-07-11T22:30:00Z",
  "sleep_end": "2026-07-12T06:45:00Z",
  "rem_duration_mins": 105,
  "light_duration_mins": 265,
  "deep_duration_mins": 125
}
```

**Validation:**

- `sleep_start` and `sleep_end` are required.
- `sleep_end` must be after `sleep_start`.
- Sleep stage durations are required and cannot be negative.

**Success:** `201 Created`

Returns the created sleep session.

### `GET /api/sleeps`

Lists sleep sessions for the authenticated user.

**Auth:** `Authorization: Bearer <access_token>`

**Success:** `202 Accepted`

```json
[
  {
    "id": "uuid",
    "created_at": "timestamp",
    "updated_at": "timestamp",
    "sleep_start": "timestamp",
    "sleep_end": "timestamp",
    "rem_duration_mins": 105,
    "light_duration_mins": 265,
    "deep_duration_mins": 125,
    "user_id": "uuid"
  }
]
```

### `DELETE /api/sleeps`

Deletes all sleep sessions.

**Auth:** `Authorization: Bearer <ADMIN_KEY>`

**Success:** `204 No Content`

## Exercise Sessions

### `POST /api/exercises`

Creates an exercise session for the authenticated user.

**Auth:** `Authorization: Bearer <access_token>`

**Request body:**

```json
{
  "workout_start": "2026-07-12T15:00:00Z",
  "workout_end": "2026-07-12T15:45:00Z",
  "workout_name": "Zone 2 Run",
  "zone1_mins": 5,
  "zone2_mins": 35,
  "zone3_mins": 5,
  "strain": 6
}
```

**Validation:**

- `workout_start`, `workout_end`, and `workout_name` are required.
- `workout_end` must be after `workout_start`.
- Heart-rate zone minutes are required and cannot be negative.
- `strain` is required and must be between `0` and `10`.

**Success:** `201 Created`

Returns the created exercise session.

### `GET /api/exercises`

Lists exercise sessions for the authenticated user.

**Auth:** `Authorization: Bearer <access_token>`

**Success:** `200 OK`

Returns an array of exercise sessions.

### `DELETE /api/exercises`

Deletes all exercise sessions.

**Auth:** `Authorization: Bearer <ADMIN_KEY>`

**Success:** `204 No Content`

## Meditation Sessions

### `POST /api/meditations`

Creates a meditation session for the authenticated user.

**Auth:** `Authorization: Bearer <access_token>`

**Request body:**

```json
{
  "meditation_start": "2026-07-12T13:00:00Z",
  "meditation_end": "2026-07-12T13:20:00Z",
  "starting_hr": 78,
  "ending_hr": 62
}
```

**Validation:**

- `meditation_start` and `meditation_end` are required.
- `meditation_end` must be after `meditation_start`.
- `starting_hr` and `ending_hr` are required.
- Heart rates must be between `40` and `180`.

**Success:** `201 Created`

Returns the created meditation session.

### `GET /api/meditations`

Lists meditation sessions for the authenticated user.

**Auth:** `Authorization: Bearer <access_token>`

**Success:** `200 OK`

Returns an array of meditation sessions.

### `DELETE /api/meditations`

Deletes all meditation sessions.

**Auth:** `Authorization: Bearer <ADMIN_KEY>`

**Success:** `204 No Content`

## Admin Reset

### `DELETE /api/users`

Deletes all users. Because session tables reference users with `ON DELETE CASCADE`, deleting users also removes their associated refresh tokens and fitness sessions.

**Auth:** `Authorization: Bearer <ADMIN_KEY>`

**Success:** `204 No Content`

## Static Web Routes

| Route | Purpose |
| --- | --- |
| `GET /` | Redirects to `/web/` |
| `GET /web/` | Serves the static frontend from `FILEPATH_ROOT` |
