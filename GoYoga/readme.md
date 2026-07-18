# GoYoga

GoYoga is a Go web API and plain JavaScript frontend for a yoga class booking application. Users can create accounts, instructors can publish class sessions, and students can browse, register for, and unregister from sessions.

This is also a portfolio learning project focused on backend design fundamentals: HTTP routing, authentication, relational modeling, generated SQL access, middleware-style handler organization, and small admin/dev support endpoints.

## Current Features

- Student account creation and login
- Instructor account creation gated by a setup token
- Instructor-only yoga session creation
- Session listing and session detail lookup
- Student class registration and unregistering
- JWT access tokens and database-backed refresh tokens
- Argon2id password hashing
- Browser UI for signup, login, calendar browsing, and registration
- API health check and in-memory usage metrics
- Dev-only database reset endpoint
- PostgreSQL schema managed with Goose-style migrations
- SQL query code generated with sqlc

## Tech Stack

- Go 1.26
- Standard library `net/http`
- PostgreSQL
- sqlc
- Goose-style SQL migrations
- Argon2id password hashing
- JWT bearer authentication
- Plain HTML, CSS, and JavaScript frontend

## Project Structure

```text
GoYoga/
├── api.go                  # HTTP server, routes, handlers, and response models
├── api_docs.md             # Detailed endpoint documentation
├── yoga_project.http       # REST Client requests for local testing
├── web/                    # Static frontend served by the Go API
├── internal/
│   ├── auth.go             # Password hashing, JWT, and bearer-token helpers
│   └── database/           # sqlc-generated database package
├── sql/
│   ├── queries/            # SQL queries used by sqlc
│   └── schema/             # Goose-style database migrations
├── sqlc.yaml
└── go.mod
```

## Environment

The server reads configuration from environment variables. A local `.env` file is supported through `godotenv`.

```env
PORT=:8080
FILEPATH_ROOT=web
DB_URL=postgres://postgres:postgres@localhost:5432/goyoga?sslmode=disable
TOKEN_DURATION=3600
TOKEN_SECRET=replace-with-a-long-random-secret
INSTRUCTOR_CREATION_TOKEN=replace-with-a-local-setup-token
ADMIN_KEY=replace-with-a-local-admin-key
IN_DEV=true
```

Notes:

- `PORT` should include the leading colon, for example `:8080`.
- `TOKEN_DURATION` is interpreted in seconds.
- `FILEPATH_ROOT` defaults to `web` when omitted.
- `IN_DEV=true` enables the dev-only `/api/reset` endpoint.
- Do not commit real secrets in `.env`.

## Database Setup

Create a local PostgreSQL database, then run the migrations in `sql/schema` with Goose or a compatible migration runner.

Example using Goose:

```sh
goose postgres "$DB_URL" up
```

After changing SQL queries or schema files, regenerate the database package:

```sh
sqlc generate
```

## Run Locally

From the `GoYoga` directory:

```sh
go mod download
go run .
```

Then open:

```text
http://localhost:8080/
```

The Go server serves the frontend from `/` and the API from `/api/...`, so browser requests and API requests use the same local origin.

## API Overview

Detailed request and response examples are in [api_docs.md](api_docs.md).

Core endpoints:

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/api/health` | Health check |
| `GET` | `/api/metrics` | Admin-only usage metrics |
| `POST` | `/api/reset` | Dev-only database reset |
| `POST` | `/api/users` | Create a student user |
| `POST` | `/api/instructors` | Create an instructor user |
| `POST` | `/api/login` | Log in and receive access and refresh tokens |
| `POST` | `/api/refresh` | Exchange a refresh token for a new access token |
| `POST` | `/api/revoke` | Revoke a refresh token |
| `GET` | `/api/sessions` | List sessions |
| `GET` | `/api/sessions/{session_id}` | Get one session |
| `POST` | `/api/sessions` | Create an instructor-owned session |
| `POST` | `/api/sessions/{session_id}/registrations` | Register for a session |
| `DELETE` | `/api/sessions/{session_id}/registrations` | Unregister from a session |

Use [yoga_project.http](yoga_project.http) with a REST Client extension or compatible IDE HTTP runner for repeatable local testing and seed data.

## Domain Model

The current schema centers on four tables:

- `users`: student and instructor accounts, with instructors represented by `is_instructor`
- `sessions`: scheduled yoga classes owned by instructor users
- `class_registrations`: the join table between users and sessions
- `refresh_tokens`: long-lived refresh tokens tied to users and revocation state

Important domain rules currently enforced:

- Only users with `is_instructor = true` can create sessions.
- Session difficulty must be between 1 and 5.
- A session end time must be after its start time.
- A user cannot register for the same session twice.
- Registration is blocked once the number of active registrations reaches `class_size`.

## Development Workflow

Run tests:

```sh
go test ./...
```

Common local workflow:

```sh
goose postgres "$DB_URL" up
sqlc generate
go test ./...
go run .
```

## Design Notes

- The current implementation keeps routing and handlers in `api.go`. That is workable at this size, but the next architectural step would be separating route registration, request decoding/validation, and domain operations as the feature set grows.
- Database access goes through sqlc-generated methods, which keeps query behavior explicit while avoiding hand-written row scanning.
- The database owns durable relationships and simple constraints; handlers own request-specific validation and authorization decisions.
- Refresh tokens are persisted so they can be revoked independently of short-lived JWT access tokens.
- The frontend is intentionally dependency-free, keeping the first version easy to inspect and deploy.
