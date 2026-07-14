# FitByte Fitness Tracker

FitByte (a play on FitBit, of course :^]) is a small Go fitness-tracking application with a JSON API, PostgreSQL persistence, and a static web client. The app lets users log in, track sleep sessions, exercise sessions, and meditation sessions, then view their data through pages under `/web/`.

## Project Structure

```text
.
├── main.go                 # HTTP server, route handlers, app configuration
├── internal/
│   ├── auth.go             # Password hashing, JWTs, bearer token helpers
│   └── database/           # sqlc-generated database access code
├── sql/
│   ├── schema/             # Goose-style migration files
│   └── queries/            # sqlc query definitions
├── tests/                  # Go tests
├── web/                    # Static frontend pages and shared JS/CSS
├── images/                 # Project screenshots/assets
├── sqlc.yaml               # sqlc configuration
└── api_doc.md              # API reference
```

## Features

- User creation guarded by a server-side creation token.
- Password hashing with Argon2id.
- Login with short-lived JWT access tokens and 60-day refresh tokens.
- Refresh token revocation.
- Authenticated creation and retrieval of:
  - Sleep sessions
  - Exercise sessions
  - Meditation sessions
- Admin-only reset endpoints for development/testing data cleanup.
- Static web client served by the Go server.

## Technology

- Go 1.26.2
- PostgreSQL
- `net/http` routing with method-aware patterns
- `sqlc` for generated database code
- Goose-style SQL migration files
- JWT authentication via `github.com/golang-jwt/jwt/v4`
- Argon2id password hashing via `github.com/alexedwards/argon2id`

## Configuration

The app reads configuration from environment variables. A local `.env` file is loaded during startup if present.

| Variable | Purpose |
| --- | --- |
| `DB_URL` | PostgreSQL connection string |
| `PORT` | HTTP server address, for example `:8080` |
| `FILEPATH_ROOT` | Directory served at `/web/`, typically `web` |
| `USER_CREATION_TOKEN` | Bearer token required by `POST /api/users` |
| `ADMIN_KEY` | Bearer token required by destructive reset endpoints |
| `TOKEN_DURATION` | Access-token lifetime in seconds |
| `TOKEN_SECRET` | Secret used to sign JWT access tokens |

## Running Locally

1. Create and configure a PostgreSQL database.
2. Apply the SQL schema files in `sql/schema/` in order.
3. Set the required environment variables in `.env`.
4. Start the server:

```bash
go run .
```

5. Open the web client at:

```text
http://localhost:8080/web/
```

Use the port that matches your `PORT` value.

## Development Notes

- The database access layer is generated from `sql/queries/*.sql` using `sqlc`.
- Authentication tests currently cover password hashing and hash comparison.
- The `.http` file contains local request examples for manual API testing.
- API details, including request bodies and auth requirements, live in `api_doc.md`.

## What I Learned
- SQLC and Goose are an increadible stack for managing databases and are going to becomea regular part of my workflow.
- I really enjoyed the flexibility that came with using Go for the backend of this project and find myself prefering
Go over something like FastAPI in Python.
- Keys as well as tokens allow for secure designs and are a must have in any backend.


## Use of AI in This Project
I think that AI is an incredibly useful tool and is fundamentally reshaping the world of software development. However, I think it is still very important that we as developers pride ourselves on really understanding programming (not just syntax, but a deep level of understanding of how things work) and AI, when used incorrectly, can be quite detrimental to this notion.

For this project, I used AI to help me create the frontend of this application. I have never really built any frontend projects before, so AI allowed me to ship something quickly while also explaining the design choices that it was making - helping my learning overall. It isn't perfect, but it was fun to put together and gives me a solid baseline so that with my next project I can code more of it by hand and deepen my understanding.

As for the backend, that was hand coded by yours truly. I have found a deep love and joy for programming projects such as this one.