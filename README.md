# Neko Track API

[![CI](https://github.com/jacsonsouza/neko-track-api/actions/workflows/ci.yml/badge.svg)](https://github.com/jacsonsouza/neko-track-api/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.133-009688.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-18-336791.svg)](https://www.postgresql.org/)

Backend of **Neko Track**, the anime tracking app. It authenticates users through **AniList OAuth**, proxies the **AniList GraphQL API**, and stores users and their tokens locally so the Flutter client never talks to AniList directly or handles raw credentials.

## Table of contents

- [Why this project](#why-this-project)
- [How it works](#how-it-works)
- [Getting started](#getting-started)
- [Configuration](#configuration)
- [Testing](#testing)
- [API overview](#api-overview)
- [Using it with the Flutter app](#using-it-with-the-flutter-app)
- [Getting help](#getting-help)
- [Maintainers and contributors](#maintainers-and-contributors)

## Why this project

- **Single auth entry point** — the mobile app only ever sees a short-lived app JWT issued by this API, never the AniList token.
- **Tokens are encrypted at rest** — AniList access tokens are stored with Fernet (`TOKEN_ENC_KEY`) in `anilist_tokens`, never in plaintext and never logged.
- **GraphQL proxy with local cache of identity** — search, profile, activity, lists, and details requests go through typed services and DTOs, so the client gets a stable JSON contract even if AniList changes.
- **Stateless-friendly and small** — FastAPI + SQLAlchemy 2 (typed mappings) + Alembic, with a `router → service → repo` convention that keeps modules independent.
- **Testable by design** — external HTTP is always mocked with `respx`; the suite runs in CI against a throwaway Postgres 18 database.

## How it works

```
Flutter app ──► Neko Track API ──► AniList (OAuth + GraphQL)
                    │
                    └──► PostgreSQL (users, anilist_tokens)
```

Every module follows the same shape:

```
router.py   # HTTP layer: APIRouter, Depends(get_claims), Depends(get_db)
service.py  # business rules / AniList calls (async, httpx)
repo.py     # pure database access (SQLAlchemy Session)
dto/        # pydantic response models
queries.py  # GraphQL operation strings
```

Routers are registered in [`app/main.py`](app/main.py) — a router that is not `include_router`-ed simply does not exist (it 404s).

## Getting started

### Prerequisites

- Python **3.12**
- Docker + Docker Compose
- AniList OAuth app credentials (<https://anilist.co/apps>) — only needed for the login flow

### 1. Clone and configure the environment

```bash
git clone https://github.com/jacsonsouza/neko-track-api.git
cd neko-track-api
cp .env.example .env
```

Edit `.env` and fill in the values described in [Configuration](#configuration). `.env` is gitignored — **never commit it**.

Generate the two secrets with:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(48))"                      # JWT_SECRET
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"  # TOKEN_ENC_KEY
```

### 2. Start the database

```bash
docker compose up -d db     # PostgreSQL 18 on port 5432, container neko_track_db
docker compose ps           # wait for "healthy"
```

### 3. Install the dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

> If `python3-venv` is unavailable on your distro, [`uv`](https://docs.astral.sh/uv/) works too: `uv venv .venv && uv pip install -r requirements.txt --python .venv/bin/python`.

### 4. Run the migrations

```bash
alembic upgrade head
```

### 5. Start the server

```bash
uvicorn app.main:app --reload
# API on http://localhost:8000 — interactive docs at /docs
```

Verify everything is wired up:

```bash
curl http://localhost:8000/health
# {"status":"ok","db":"ok"}

curl http://localhost:8000/routes   # every registered route
```

## Configuration

All settings live in [`app/core/config.py`](app/core/config.py) and are read from `.env` via `pydantic-settings`.

| Variable | Description | Example |
| :--- | :--- | :--- |
| `ANILIST_CLIENT_ID` | Client ID of your AniList OAuth app | `1234` |
| `ANILIST_CLIENT_SECRET` | Client secret of your AniList OAuth app | `xxxx` |
| `JWT_SECRET` | HS256 secret for app JWTs | random 48-byte URL-safe string |
| `TOKEN_ENC_KEY` | Fernet key used to encrypt AniList tokens | `Fernet.generate_key()` |
| `APP_BASE_URL` | Public base URL of this API (used as OAuth `redirect_uri`) | `http://localhost:8000` |
| `MOBILE_DEEPLINK` | Deep link the callback redirects to | `nekotrack://auth` |
| `DATABASE_URL_POOLED` | Engine URL used by the running app | `postgresql+psycopg://neko:neko@localhost:5432/neko_track` |
| `DATABASE_URL_DIRECT` | URL used by Alembic and the test suite (no pooler) | `postgresql+psycopg://neko:neko@localhost:5432/neko_track` |

Local defaults for the Docker database: user `neko`, password `neko`, database `neko_track`.

## Testing

```bash
pytest -q                 # full suite (same command as the CI)
pytest tests/unit -q      # fast feedback: crypto, JWT claims, OAuth state
pytest tests/integration/test_auth_me.py -q
```

The suite expects a **separate** database and runs `drop_all/create_all` on it:

```bash
docker compose exec -T db psql -U neko -d postgres -c "CREATE DATABASE neko_test;"
export DATABASE_URL_DIRECT="postgresql+psycopg://neko:neko@localhost:5432/neko_test"
alembic upgrade head
pytest -q
```

Conventions enforced by the tests:

- external HTTP is mocked with `respx` — **no real call to `anilist.co` ever happens**;
- objects are built with `UserFactory` / `AnilistTokenFactory` (registered in [`tests/conftest.py`](tests/conftest.py)).

CI (`.github/workflows/ci.yml`) runs on pull requests to `main` and on pushes to `production`: Postgres 18 service → `pip install -r requirements.txt` → `alembic upgrade head` → `pytest -q`.

## API overview

Full interactive documentation is served at **`/docs`** (Swagger UI) and `/redoc` once the server is up.

| Method | Path | Auth | Description |
| :--- | :--- | :--- | :--- |
| GET | `/health` | — | Liveness + database check |
| GET | `/routes` | — | Debug listing of registered routes |
| GET | `/auth/anilist/start` | — | Redirects to the AniList authorize URL (signed `state`) |
| GET | `/auth/anilist/callback` | — | Exchanges `code` for a token, redirects to `nekotrack://auth?token=<jwt>` |
| GET | `/auth/anilist/me` | Bearer | Current user claims + profile |
| GET | `/anilist/anime/search` | Bearer | Anime search |
| GET | `/anilist/viewer` · `/anilist/profile` | Bearer | Authenticated user's AniList profile |
| GET | `/anilist/user/activities` | Bearer | User activity feed (paginated) |
| POST | `/anilist/user/activities/{id}/like` | Bearer | Toggle like on an activity |
| GET/POST | `/anilist/user/activities/{id}/replies` | Bearer | List / create replies |
| DELETE | `/anilist/replies/{id}` | Bearer | Delete a reply |
| POST | `/anilist/replies/{id}/toggle-like` | Bearer | Toggle like on a reply |
| GET | `/anilist/user/{user_id}/watch-lists` · `/watching` | Bearer | User's AniList lists |
| GET/PATCH | `/anilist/animes/{anime_id}` | Bearer | Anime details and progress updates |
| PATCH | `/anilist/animes/{anime_id}/episodes` | Bearer | Increment watched episodes |

**Authentication:** everything except `/health`, `/routes`, and the two OAuth endpoints requires `Authorization: Bearer <app JWT>`; missing or invalid tokens return `401`. See [`app/core/auth_dep.py`](app/core/auth_dep.py).

**OAuth sequence:**

1. `GET /auth/anilist/start` → API signs a `state` (HMAC-SHA256, 10-minute TTL) and 302s to AniList.
2. User authorizes → AniList redirects to `GET /auth/anilist/callback?code=...&state=...`.
3. API validates `state`, exchanges `code` for an access token, upserts `users` + encrypted `anilist_tokens`, and 302s to `nekotrack://auth?token=<app JWT>`.

## Using it with the Flutter app

The client is the `neko_track` Flutter app. Point it at your local API:

```bash
flutter run --dart-define=API_URL=http://10.0.2.2:8000   # Android emulator
flutter run --dart-define=API_URL=http://localhost:8000   # iOS simulator / desktop
```

Route paths are mirrored in `lib/core/config/api_routes.dart` — when you add or rename an endpoint here, update that file too.

## Getting help

- **Interactive API docs:** `http://localhost:8000/docs` (generated from the code — the fastest reference).
- **AniList:** [OAuth documentation](https://github.com/AniList/ApiV2-GraphQL-Docs/wiki/OAuth-Documentation) · [GraphQL API](https://docs.anilist.co/) · [your apps](https://anilist.co/apps).
- **FastAPI / SQLAlchemy / Alembic:** official docs linked from their homepages; the architecture follows the standard `router → service → repo` pattern.
- **Bugs and feature requests:** open an issue on the [issue tracker](https://github.com/jacsonsouza/neko-track-api/issues).

## Maintainers and contributors

Maintained by **[@jacsonsouza](https://github.com/jacsonsouza)**.

Contributions are welcome:

1. Fork and create a feature branch — never commit directly to `main`, `development`, or `production`.
2. Follow the module layout above and keep secrets in `.env` only.
3. Add or update tests (`pytest -q` must pass; mock AniList with `respx`).
4. Open a pull request against `main` and make sure CI is green.

Commit messages follow [Conventional Commits](https://www.conventionalcommits.org/) (`feat:`, `fix:`, `chore:`…).
