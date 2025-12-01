# Usage Guide (FastAPI)

## Starting the server

- Install dependencies:
  - Python: use the project's supported version (see pyproject.toml or README).
  - pip: pip install -r requirements.txt
- Using Uvicorn (typical):
  - uvicorn src.app.main:app --reload --host 0.0.0.0 --port 8000
  - If your entrypoint differs, replace `src.app.main:app` with the module that exposes the FastAPI `app`.
- If a frontend or npm assets are included, follow its README (e.g., npm install && npm start).

## Accessing the web UI and API docs

- Open the application in a browser:
  - Main UI: http://localhost:8000/
  - Swagger UI: http://localhost:8000/docs
  - ReDoc: http://localhost:8000/redoc

## Key API endpoints (examples)

JSON API is mounted under `/api/<API_VERSION>` (default `/api/v1`). Replace host/port as needed.

### List subjects

- GET /api/v1/subjects
- curl: curl -sS http://localhost:8000/api/v1/subjects

### Create a subject

- POST /api/v1/subjects
- curl:
  curl -X POST http://localhost:8000/api/v1/subjects \
   -H "Content-Type: application/json" \
   -d '{"code":"COMP101","name":"Intro to Programming","sync":false}'

### Get subject by id

- GET /api/v1/subjects/{subject_id}
- curl: curl http://localhost:8000/api/v1/subjects/1

### Update subject

- PUT /api/v1/subjects/{subject_id}
- curl:
  curl -X PUT http://localhost:8000/api/v1/subjects/1 \
   -H "Content-Type: application/json" \
   -d '{"name":"Programming I"}'

### Delete subject

- DELETE /api/v1/subjects/{subject_id}
- curl: curl -X DELETE http://localhost:8000/api/v1/subjects/1

### List assessments for a subject (API routes under /api/<API_VERSION>)

- See /api docs at http://localhost:8000/docs for exact paths.

### Add assessment entry

- Refer to the Swagger docs for the schema and paths.

### Update/delete assessment

- See Swagger for exact endpoints.

- Exam-related endpoints are grouped under `/api/<API_VERSION>/subjects/...`; check Swagger for payloads.

Always inspect /docs for precise request/response schemas and available endpoints.

## Web UI pretty routes (HTML)

- Year overview: `GET /year/{year}`
- Semester overview: `GET /year/{year}/semester/{semester}`
- Subject detail: `GET /year/{year}/semester/{semester}/subject/{code}`

For JSON workflows and request bodies, use the interactive docs at `/docs`.

## Configuration

- Primary environment variables

  - SESSION_SECRET_KEY — required for sessions
  - DATABASE_URL — Postgres URL; otherwise falls back to SQLite file at `data/marks.db`
  - APP_VERSION — footer version string (e.g., 0.6.0+<sha>)
  - ENV — footer environment label (dev|staging|prod)
  - ENABLE_DEBUG_ROUTES — optional debug endpoints
  - API_VERSION — versioned API prefix (e.g., v1)

- Example .env (local)
  SESSION_SECRET_KEY=change-me

  # DATABASE_URL=postgresql://user:pass@host/db # optional

  APP_VERSION=0.6.0
  ENV=dev
  ENABLE_DEBUG_ROUTES=false
  API_VERSION=v1

- Load .env using python-dotenv or the project's configuration loader.

## Database setup & migrations (SQLModel/SQLAlchemy)

- If using migrations (Alembic):
  - Initialize (one-time): alembic init alembic (if not present)
  - Generate migration: alembic revision --autogenerate -m "init"
  - Apply migrations: alembic upgrade head
- If no migrations and the app auto-creates tables:
  - Start the app; on first run it will create tables based on SQLModel models.
  - Or run a small init script if provided, e.g. python -m app.db.init (check repo).
- Connection strings:
  - SQLite local file: sqlite:///data/app.db
  - Postgres: postgresql+asyncpg://user:pass@host:port/dbname

## Persistence & backups

- For SQLite: the DB is the single file (e.g., data/app.db). Backup by copying the file:
  - cp data/app.db backups/app-$(date +%F-%T).db
- For Postgres/MySQL: use pg_dump / mysqldump or managed DB backups.
- Keep regular backups and store them off-instance (S3, network storage, etc.).
- Consider migration/version control (Alembic) to safely evolve schema.

## Troubleshooting

- Server does not start / port conflict:
  - Check if another process uses the port (lsof -i :8000) or change PORT.
- Missing env vars:
  - Ensure DATABASE_URL and SECRET_KEY are set; the app will error on missing critical config.
- DB connection errors:
  - Verify DATABASE_URL and DB is reachable. For remote DBs, check firewall and credentials.
- Migrations not applied:
  - Run alembic upgrade head or the project-specific migration command.
- CORS issues (frontend cannot access API):
  - Ensure CORS middleware is configured with the correct origins in the FastAPI app.
- Check logs (console) and the interactive /docs endpoint for schema and validation errors.

If further detail or repo-specific commands are needed, point to the project README or share the relevant files (entrypoint path, migration setup, and configuration loader).

- Ensure all dependencies are installed and you are using the correct Python version.
- For missing features or bugs, see [FAQ](faq.md) or report an issue.
