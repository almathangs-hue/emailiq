# EmailIQ

A personal email intelligence dashboard that automatically extracts and tracks job applications from Gmail — with a roadmap to cover spam, bills, subscriptions, and AI-powered interview prep.

## What It Is

EmailIQ connects to your Gmail account via Google OAuth and scans your inbox to detect job application emails automatically. It uses a confidence-scoring system (not simple keyword matching) to classify emails accurately, presents them in a clean dashboard, and lets you filter by date range, status, and company. You can confirm or dismiss detections with one click to improve accuracy over time.

Built to be modular — job tracking is V1, but the architecture supports adding spam management, subscription/bill tracking, and an AI interview prep planner on top.

## Problem It Solves

Job seekers applying to dozens of roles struggle to track where they've applied, what stage each application is at, and what needs follow-up. The information already exists in your inbox — confirmation emails, recruiter messages, rejection notices — but it's unstructured and scattered. EmailIQ extracts and organises it automatically so you don't have to maintain a spreadsheet.

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18, TypeScript, Tailwind CSS, Vite, React Query, Zustand |
| Backend | Python 3.11, FastAPI |
| Auth | Google OAuth 2.0 (Authlib) |
| Gmail | Google API Python Client (read-only scope) |
| Database | PostgreSQL, SQLAlchemy 2.0, Alembic |
| Background jobs | APScheduler |
| Logging | Loguru (structured, JSON in prod) |
| Containerisation | Docker, docker-compose |
| Future: AI prep planner | Claude API |
| Future: analysis | pandas, plotly |

## Architecture

### System Overview

```mermaid
flowchart TD
    User["User (any device)"]
    React["React + TypeScript Frontend\nVite · Tailwind · React Query · Zustand"]
    FastAPI["FastAPI Backend\n/api/v1/..."]
    Auth["Google OAuth 2.0"]
    Gmail["Gmail API\n(read-only)"]
    DB[("PostgreSQL")]
    Scheduler["APScheduler\n(auto-sync every 6h)"]

    subgraph Modules
        Jobs["Jobs Module · V1"]
        Spam["Spam Module · Future"]
        Bills["Bills Module · Future"]
        Prep["AI Prep Planner · Future"]
    end

    User -->|HTTPS| React
    React -->|REST /api/v1| FastAPI
    FastAPI --> Auth
    FastAPI --> Gmail
    FastAPI --> DB
    FastAPI --> Scheduler
    Scheduler --> Gmail
    FastAPI --> Jobs
    FastAPI --> Spam
    FastAPI --> Bills
    FastAPI --> Prep
```

### Backend Layer Architecture

The backend is structured in strict layers — each layer only talks to the one directly below it.

```mermaid
flowchart LR
    A["API Router\n/api/v1/...\nHTTP only — validation,\nstatus codes, auth"] -->|calls| B["Service\nBusiness logic\nOrchestrates operations"]
    B -->|calls| C["Repository\nData access layer\nAll DB queries live here"]
    C -->|queries| D["SQLAlchemy Model\nORM mapping"]
    D --> E[("PostgreSQL")]
```

#### Before vs After — Why This Structure

**Before (initial scaffold):** Routes directly ran DB queries and mixed HTTP logic with business logic, making the code hard to test, reuse, or extend.

```mermaid
flowchart LR
    R["Router\nHTTP + Business logic\n+ DB queries mixed"] --> DB[("PostgreSQL")]
    S["Service\nAlso queried DB\ndirectly"] --> DB
```

**After (enterprise layering):** Each concern has exactly one home. Routes are pure HTTP. Services are pure logic. Repositories are the only place that touches the database.

```mermaid
flowchart LR
    R["Router\nHTTP only"] --> S["Service\nLogic only"]
    S --> Repo["Repository\nDB only"]
    Repo --> M["Model"]
    M --> DB[("PostgreSQL")]
```

**What this gives you:**
- **Testability** — repositories can be mocked; services unit-tested without a DB
- **Replaceability** — swap PostgreSQL for another DB by rewriting only the repository layer
- **Readability** — every file has a clear, single responsibility
- **Extensibility** — adding a new module (spam, bills) means adding a new repo + service + router, not modifying existing code

### Project Structure

```
emailiq/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── router.py          ← aggregates all v1 routes
│   │   │       └── routers/
│   │   │           ├── auth.py        ← HTTP: OAuth flow
│   │   │           ├── applications.py← HTTP: CRUD + feedback
│   │   │           └── sync.py        ← HTTP: trigger sync
│   │   ├── core/
│   │   │   ├── config.py              ← pydantic-settings env config
│   │   │   ├── auth.py                ← JWT + token encryption
│   │   │   ├── exceptions.py          ← domain exception hierarchy
│   │   │   └── logging.py             ← loguru structured logging
│   │   ├── db/
│   │   │   ├── session.py             ← SQLAlchemy engine + get_db
│   │   │   └── base.py                ← DeclarativeBase + model imports
│   │   ├── models/                    ← SQLAlchemy ORM models
│   │   ├── repositories/              ← all DB queries (one class per model)
│   │   │   ├── base.py                ← generic CRUD base repository
│   │   │   ├── user.py
│   │   │   ├── account.py
│   │   │   ├── email_record.py
│   │   │   └── application.py
│   │   ├── schemas/                   ← Pydantic request/response shapes
│   │   ├── services/                  ← business logic only
│   │   │   ├── gmail_service.py       ← Gmail API calls
│   │   │   ├── detection_service.py   ← confidence scoring
│   │   │   └── sync_service.py        ← orchestrates scan + classify
│   │   └── main.py                    ← FastAPI app, middleware, lifespan
│   ├── tests/
│   │   ├── conftest.py                ← test DB, fixtures
│   │   ├── unit/                      ← pure logic tests (no DB)
│   │   └── integration/               ← full request/response tests
│   ├── alembic/                       ← DB migrations
│   ├── pyproject.toml                 ← deps + ruff + mypy config
│   └── Dockerfile
├── frontend/
│   └── src/
│       ├── api/                       ← typed axios wrappers per resource
│       ├── hooks/                     ← React Query hooks
│       ├── pages/                     ← Login, Dashboard, ApplicationDetail
│       ├── store/                     ← Zustand auth store
│       └── types/                     ← shared TypeScript interfaces
├── docker-compose.yml                 ← postgres + backend + frontend
└── .pre-commit-config.yaml            ← ruff lint/format on commit
```

### Detection — Confidence Scoring

Each email is scored across multiple signals. Emails scoring ≥ 50 are classified as job applications.

| Signal | Score |
|---|---|
| Known ATS sender domain (Greenhouse, Lever, Workday, etc.) | +40 |
| Sender prefix: `careers@`, `recruiting@`, `talent@` | +20 |
| Subject line job keywords | +30 |
| Body job keywords | +15 |
| `no-reply@` prefix | +5 |
| Email in existing classified thread | +25 |

### Data Model

```
User
 └── ConnectedAccount     ← built for multi-account from day one
      └── EmailRecord      ← raw Gmail message + confidence score
           ├── Application  ← parsed job application
           └── EmailFeedback← confirm / reject per detection
```

## Google Authentication

EmailIQ uses **Google OAuth 2.0 (Authorization Code Flow)** to securely connect to a user's Gmail account without ever handling their Google password.

### How the flow works

```mermaid
sequenceDiagram
    participant U as User (Browser)
    participant F as React Frontend
    participant B as FastAPI Backend
    participant G as Google OAuth

    U->>F: Clicks "Sign in with Google"
    F->>B: GET /api/v1/auth/login
    B->>G: Redirect to Google consent screen
    G->>U: User approves access
    G->>B: Callback with auth code
    B->>G: Exchange code for tokens
    G->>B: access_token + refresh_token
    B->>B: Encrypt tokens, store in DB
    B->>B: Issue JWT for session
    B->>F: Redirect to /dashboard?token=JWT
    F->>F: Store JWT in Zustand (localStorage)
    F->>B: All future requests: Authorization: Bearer JWT
```

### Scope requested

EmailIQ requests the **minimum necessary permissions**:

| Scope | Why |
|---|---|
| `openid` | Verify identity with Google |
| `email` | Know which Gmail account is connected |
| `profile` | Show user's name and avatar in the UI |
| `gmail.readonly` | Read inbox to detect job application emails |

`gmail.readonly` is intentionally read-only. EmailIQ **cannot** send, delete, or modify emails. Users can revoke access at any time via [Google Account → Security → Third-party apps](https://myaccount.google.com/permissions).

### Implementation pieces

#### Backend — `app/api/v1/routers/auth.py`
Registers the Google OAuth client via **Authlib** and exposes two endpoints:
- `GET /api/v1/auth/login` — builds the Google authorization URL with state parameter (CSRF protection) and redirects the user
- `GET /api/v1/auth/callback` — receives the authorization code from Google, exchanges it for tokens, upserts the user and account in the database, and issues a JWT

#### Token encryption — `app/core/auth.py`
Google access and refresh tokens are sensitive credentials. Before storing them in PostgreSQL, they are **encrypted using Fernet symmetric encryption** (`cryptography` library). Raw tokens never touch the database. On each Gmail API call, the token is decrypted in memory, used, then discarded.

```python
# Tokens are always encrypted before DB write
account.access_token = encrypt_token(raw_access_token)
account.refresh_token = encrypt_token(raw_refresh_token)
```

#### Session management
After OAuth completes, the backend issues a **short-lived JWT** (1 hour expiry) signed with `SECRET_KEY`. The frontend stores this in Zustand (persisted to localStorage) and attaches it as a `Bearer` token on every API request via an Axios interceptor. On 401, the interceptor clears the token and redirects to login.

#### Token refresh
Google access tokens expire after 1 hour. The Gmail service (`app/services/gmail_service.py`) automatically detects expiry using `google-auth` and uses the stored refresh token to obtain a new access token, updating the encrypted value in the database transparently.

#### CSRF protection
Authlib's `SessionMiddleware` stores a `state` parameter in the server-side session during the login redirect. Google echoes it back in the callback. If they don't match, the request is rejected — preventing cross-site request forgery attacks on the OAuth flow.

### Google Cloud setup (one-time)

To run EmailIQ locally or deploy it, you need a Google Cloud project with the Gmail API enabled:

1. Create a project at [console.cloud.google.com](https://console.cloud.google.com)
2. Enable the **Gmail API** under APIs & Services → Library
3. Configure the **OAuth consent screen** (External, add `gmail.readonly` scope)
4. Add your email as a **test user** (required while app is unverified)
5. Create **OAuth 2.0 credentials** → Web application, add authorized redirect URI:
   - Local: `http://localhost:8000/api/v1/auth/callback`
   - Production: `https://your-domain.com/api/v1/auth/callback`
6. Copy the Client ID and Secret into your `.env` file

## Live Demo

> Not deployed yet — in progress.

## How to Run Locally

### Option 1 — Docker (recommended)

```bash
cp .env.example .env   # fill in GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, SECRET_KEY
docker-compose up
```

- API: `http://localhost:8000`
- Frontend: `http://localhost:5173`
- API docs: `http://localhost:8000/api/docs`

### Option 2 — Manual

#### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
cp .env.example .env        # fill in credentials
alembic upgrade head
uvicorn app.main:app --reload
```

#### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Developer Tools

### Docker

Docker packages the app and all its dependencies into isolated **containers** — lightweight, self-contained environments that run the same way on any machine. You don't need to install Python, PostgreSQL, or Node separately. Docker handles it all.

#### How docker-compose works in this project

`docker-compose.yml` defines three services that start together with one command:

```
docker-compose up
```

```mermaid
flowchart LR
    subgraph Docker Network
        DB["db\nPostgreSQL 16\nport 5432"]
        BE["backend\nFastAPI + Uvicorn\nport 8000"]
        FE["frontend\nNode + Vite\nport 5173"]
    end

    BE -->|DATABASE_URL| DB
    FE -->|VITE_API_URL| BE
    You -->|localhost:5173| FE
    You -->|localhost:8000/api/docs| BE
```

#### What each service does

| Service | Image | What it runs | Port |
|---|---|---|---|
| `db` | `postgres:16-alpine` | PostgreSQL database | 5432 |
| `backend` | Built from `./backend/Dockerfile` | FastAPI app via Uvicorn | 8000 |
| `frontend` | `node:20-alpine` | Vite dev server | 5173 |

#### Key Docker features used

**Health check — backend waits for the database to be ready**

```yaml
depends_on:
  db:
    condition: service_healthy
```

Without this, FastAPI would start before PostgreSQL is ready and crash immediately. The health check runs `pg_isready` every 5 seconds until the database accepts connections, then starts the backend.

**Volume mounts — live code reloading without rebuilding**

```yaml
volumes:
  - ./backend:/app
```

Your local `backend/` folder is mounted directly into the container. When you edit a Python file, Uvicorn detects the change and reloads automatically — no need to restart Docker. Same for the frontend with Vite.

**Named volume — PostgreSQL data persists between restarts**

```yaml
volumes:
  postgres_data:
```

Without this, every `docker-compose down` would wipe your database. The named volume keeps data on disk between restarts. To fully reset the database: `docker-compose down -v`.

**Shared network — services find each other by name**

Inside Docker, services don't use `localhost` to talk to each other — they use the service name. That's why `DATABASE_URL` is:

```
postgresql://emailiq:emailiq@db:5432/emailiq
#                             ^^ service name, not localhost
```

#### Useful commands

```bash
docker-compose up --build    # start everything, rebuild images first
docker-compose up            # start without rebuilding
docker-compose down          # stop all services
docker-compose down -v       # stop and delete the database volume (full reset)
docker-compose logs backend  # see logs for one service
docker-compose ps            # see which services are running
```

> **Reference:** [Docker Compose documentation](https://docs.docker.com/compose/) · [Dockerfile reference](https://docs.docker.com/engine/reference/builder/)

---

### Vite

Vite is the build tool and dev server for the React frontend. Browsers can't run TypeScript or understand `import` statements natively — Vite bridges that gap.

#### What Vite does in this project

**1. Runs the development server**

```bash
npm run dev   # starts Vite at http://localhost:5173
```

Vite serves your React app to the browser. Unlike older tools, it serves files on demand using native ES modules — so startup is near-instant regardless of project size.

**2. Compiles TypeScript → JavaScript**

Browsers only understand JavaScript. When you write:

```tsx
// src/components/common/Button.tsx
export default function Button({ children }: { children: React.ReactNode }) {
  return <button>{children}</button>
}
```

Vite strips the TypeScript types and converts JSX to plain JavaScript before sending it to the browser. None of that `.tsx` syntax reaches the browser directly.

**3. Hot Module Replacement (HMR)**

When you edit any file, Vite pushes only the changed module to the browser — the page updates in milliseconds without a full reload, and without losing your app's current state (e.g. which page you're on, what's in a form).

**4. Path aliases — `@/` instead of `../../`**

Without aliases, deeply nested imports look like:

```ts
import Button from "../../../components/common/Button"  // fragile, hard to read
```

We configured `@/` to map to `src/`, so every import is clean and absolute:

```ts
import Button from "@/components/common/Button"  // always works, no matter where the file is
```

This is set up in two places — `vite.config.ts` (for Vite) and `tsconfig.json` (for TypeScript):

```ts
// vite.config.ts
resolve: {
  alias: { "@": path.resolve(__dirname, "./src") }
}
```

**5. Environment variables**

Any variable in `.env` prefixed with `VITE_` is injected into the frontend bundle at build time:

```ts
// .env
VITE_API_URL=http://localhost:8000

// In your code
const api = import.meta.env.VITE_API_URL  // "http://localhost:8000"
```

Variables without the `VITE_` prefix are kept private (backend only). This prevents accidentally exposing secrets like `SECRET_KEY` to the browser.

**6. Production build**

```bash
npm run build   # outputs to frontend/dist/
```

Vite bundles, minifies, and tree-shakes everything into static files (`dist/`) — plain HTML, CSS, and JS. These are what get deployed to a CDN or static host like Vercel. The Vite dev server is never used in production.

#### Vite vs Create React App (what you might see in older tutorials)

| | Vite | Create React App |
|---|---|---|
| Dev server startup | ~300ms | 10–30 seconds |
| Hot reload | ~50ms | 1–3 seconds |
| TypeScript support | Built-in | Needs configuration |
| Still maintained | Yes | No (deprecated 2023) |
| Used by | Vue, React, Svelte | React only |

> **Reference:** [Vite documentation](https://vitejs.dev/guide/) · [Why Vite](https://vitejs.dev/guide/why.html)

## Status

**MVP in progress.** V1 scope:
- [x] Project scaffold — FastAPI + React + TypeScript + PostgreSQL
- [x] Enterprise backend architecture — layered router / service / repository
- [x] Database models (User, ConnectedAccount, EmailRecord, Application, Feedback)
- [x] Confidence-scored email detection engine
- [x] Docker + docker-compose local dev setup
- [x] Structured logging (loguru)
- [x] Test structure (unit + integration)
- [ ] Google OAuth flow (wiring in progress)
- [ ] Gmail sync — auto (APScheduler) + manual trigger
- [ ] Application dashboard UI
- [ ] Deployment
