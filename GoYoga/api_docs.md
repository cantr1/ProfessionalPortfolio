# API Docs

Base URL during local development depends on `PORT`.

All request and response bodies are JSON unless otherwise noted.

For repeatable local testing and seed data, see [yoga_project.http](yoga_project.http). It contains requests for reset, instructor creation, login, session creation, class registration, and unregistering.

## Authentication

The API currently uses bearer tokens in the `Authorization` header:

```text
Authorization: Bearer <token>
```

Some endpoints use setup/admin tokens from environment variables. Session creation uses a user JWT and checks that the authenticated user is an instructor.

## Health

### `GET /api/health`

Returns API health status.

#### Response `200`

```json
{
  "status": "online"
}
```

## Metrics

### `GET /api/metrics`

Returns API usage counters.

Requires `ADMIN_KEY` as a bearer token.

#### Response `200`

```json
{
  "file_server_hits": 0,
  "user_creation_hits": 0,
  "instructor_creation_hits": 0,
  "session_creation_hits": 0,
  "class_registration_hits": 0,
  "user_logins": 0,
  "token_refreshes": 0,
  "token_revokes": 0
}
```

#### Errors

- `401 Unauthorized`: missing or invalid bearer token
- `403 Forbidden`: bearer token does not match `ADMIN_KEY`

## Users

### `POST /api/users`

Creates a standard user.

#### Request Body

```json
{
  "email": "student@example.com",
  "password": "example-password",
  "name": "Student Name"
}
```

#### Response `201`

```json
{
  "user_id": "00000000-0000-0000-0000-000000000000",
  "email": "student@example.com",
  "created_at": "2026-07-18T12:00:00Z",
  "updated_at": "2026-07-18T12:00:00Z"
}
```

#### Errors

- `400 Bad Request`: invalid JSON or missing required fields
- `500 Internal Server Error`: password hashing, database, or response encoding failure

## Instructors

### `POST /api/instructors`

Creates an instructor account.

Requires `INSTRUCTOR_CREATION_TOKEN` as a bearer token.

#### Request Body

```json
{
  "email": "teacher@example.com",
  "password": "example-password",
  "name": "Teacher Name"
}
```

#### Response `201`

```json
{
  "user_id": "00000000-0000-0000-0000-000000000000",
  "email": "teacher@example.com",
  "instructor_name": "Teacher Name",
  "created_at": "2026-07-18T12:00:00Z",
  "updated_at": "2026-07-18T12:00:00Z"
}
```

#### Errors

- `400 Bad Request`: invalid JSON or missing required fields
- `401 Unauthorized`: missing bearer token
- `403 Forbidden`: bearer token does not match `INSTRUCTOR_CREATION_TOKEN`
- `500 Internal Server Error`: password hashing, database, or response encoding failure

## Sessions

### `GET /api/sessions`

Returns all yoga class sessions.

Requires a valid user JWT as a bearer token.

#### Response `200`

```json
[
  {
    "id": "00000000-0000-0000-0000-000000000000",
    "created_at": "2026-07-18T12:00:00Z",
    "updated_at": "2026-07-18T12:00:00Z",
    "start_time": "2026-07-18T14:00:00Z",
    "end_time": "2026-07-18T15:00:00Z",
    "instructor_id": "00000000-0000-0000-0000-000000000000",
    "instructor_name": "Teacher Name",
    "difficulty": 3,
    "class_size": 12,
    "description": "Vinyasa flow focused on balance and breath."
  }
]
```

#### Errors

- `401 Unauthorized`: missing or invalid JWT
- `500 Internal Server Error`: database or response encoding failure

### `GET /api/sessions/{session_id}`

Returns one yoga class session by ID.

Requires a valid user JWT as a bearer token.

#### Response `200`

```json
{
  "id": "00000000-0000-0000-0000-000000000000",
  "created_at": "2026-07-18T12:00:00Z",
  "updated_at": "2026-07-18T12:00:00Z",
  "start_time": "2026-07-18T14:00:00Z",
  "end_time": "2026-07-18T15:00:00Z",
  "instructor_id": "00000000-0000-0000-0000-000000000000",
  "instructor_name": "Teacher Name",
  "difficulty": 3,
  "class_size": 12,
  "description": "Vinyasa flow focused on balance and breath."
}
```

#### Errors

- `400 Bad Request`: invalid `session_id`
- `401 Unauthorized`: missing or invalid JWT
- `404 Not Found`: session does not exist
- `500 Internal Server Error`: database or response encoding failure

### `POST /api/sessions`

Creates a yoga class session.

Requires a valid user JWT as a bearer token. The authenticated user must have `is_instructor = true`.

#### Request Body

```json
{
  "start_time": "2026-07-18T14:00:00Z",
  "end_time": "2026-07-18T15:00:00Z",
  "difficulty": 3,
  "class_size": 12,
  "description": "Vinyasa flow focused on balance and breath."
}
```

#### Response `201`

```json
{
  "id": "00000000-0000-0000-0000-000000000000",
  "created_at": "2026-07-18T12:00:00Z",
  "updated_at": "2026-07-18T12:00:00Z",
  "start_time": "2026-07-18T14:00:00Z",
  "end_time": "2026-07-18T15:00:00Z",
  "instructor_id": "00000000-0000-0000-0000-000000000000",
  "difficulty": 3,
  "class_size": 12,
  "description": "Vinyasa flow focused on balance and breath."
}
```

#### Validation

- `start_time` is required.
- `end_time` is required and must be after `start_time`.
- `difficulty` must be between `1` and `5`.
- `class_size` must be greater than `0`.
- `description` is required.

#### Errors

- `400 Bad Request`: invalid JSON or validation failure
- `401 Unauthorized`: missing or invalid JWT
- `403 Forbidden`: authenticated user is not an instructor
- `404 Not Found`: token subject does not match a user
- `500 Internal Server Error`: database or response encoding failure

## Class Registrations

### `POST /api/sessions/{session_id}/registrations`

Registers the authenticated user for a yoga class session.

Requires a valid user JWT as a bearer token. The user is derived from the token; clients do not submit a `user_id`.

#### Request Body

No request body is required.

#### Response `201`

```json
{
  "user_id": "00000000-0000-0000-0000-000000000000",
  "session_id": "00000000-0000-0000-0000-000000000000",
  "created_at": "2026-07-18T12:00:00Z",
  "status": "registered"
}
```

#### Errors

- `400 Bad Request`: invalid `session_id`
- `401 Unauthorized`: missing or invalid JWT
- `404 Not Found`: token subject does not match a user, or session does not exist
- `409 Conflict`: user is already registered, or session is full
- `500 Internal Server Error`: database or response encoding failure

### `DELETE /api/sessions/{session_id}/registrations`

Unregisters the authenticated user from a yoga class session.

Requires a valid user JWT as a bearer token. The user is derived from the token; clients do not submit a `user_id`.

#### Response `204`

No response body.

#### Errors

- `400 Bad Request`: invalid `session_id`
- `401 Unauthorized`: missing or invalid JWT
- `404 Not Found`: token subject does not match a user, session does not exist, or user is not registered for the session
- `500 Internal Server Error`: database failure

## Login

### `POST /api/login`

Authenticates a user and returns an access token plus refresh token.

#### Request Body

```json
{
  "email": "student@example.com",
  "password": "example-password"
}
```

#### Response `200`

```json
{
  "id": "00000000-0000-0000-0000-000000000000",
  "created_at": "2026-07-18T12:00:00Z",
  "updated_at": "2026-07-18T12:00:00Z",
  "email": "student@example.com",
  "token": "access-token",
  "refresh_token": "refresh-token"
}
```

#### Errors

- `400 Bad Request`: invalid JSON or missing required fields
- `401 Unauthorized`: password does not match
- `404 Not Found`: user does not exist
- `500 Internal Server Error`: password check, token generation, database, or response encoding failure

## Tokens

### `POST /api/refresh`

Returns a new access token from a valid refresh token.

Requires the refresh token as a bearer token.

#### Response `200`

```json
{
  "token": "new-access-token"
}
```

#### Errors

- `401 Unauthorized`: missing, invalid, revoked, or expired refresh token
- `500 Internal Server Error`: database, token generation, or response encoding failure

### `POST /api/revoke`

Revokes a refresh token.

Requires the refresh token as a bearer token.

#### Response `204`

No response body.

#### Errors

- `400 Bad Request`: refresh token is already revoked
- `401 Unauthorized`: missing or invalid refresh token
- `500 Internal Server Error`: database failure

## Dev Reset

### `POST /api/reset`

Deletes development data and resets API metrics.

Requires:

- `IN_DEV=true`
- `ADMIN_KEY` as a bearer token

#### Response `204`

No response body.

#### Reset Order

The endpoint deletes dependent records before parent records:

```text
class_registrations
sessions
users
```

#### Errors

- `401 Unauthorized`: missing bearer token
- `403 Forbidden`: not in dev mode or invalid admin key
- `500 Internal Server Error`: database reset failure

## Planned Endpoints

These are likely next additions as the project grows:

- `GET /api/users/{id}/registrations`

## Local Seed Flow

For local development, a useful order is:

1. `POST /api/reset` with `ADMIN_KEY`
2. `POST /api/instructors` with `INSTRUCTOR_CREATION_TOKEN`
3. `POST /api/login` as the instructor
4. `POST /api/sessions` with the instructor JWT
5. `POST /api/users` for a student account
6. `POST /api/login` as the student
7. `GET /api/sessions` with the student JWT
8. `POST /api/sessions/{session_id}/registrations` with the student JWT

The included `.http` file follows this sequence and reuses response values between requests where supported.
