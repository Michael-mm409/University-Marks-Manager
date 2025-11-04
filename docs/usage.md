# Usage Guide (FastAPI)

## Starting the server

- Install dependencies:
  - Python: use the project's supported version (see pyproject.toml or README).
  - pip: pip install -r requirements.txt
- Using Uvicorn (typical):
  - uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
  - If your entrypoint differs, replace `app.main:app` with the module that exposes the FastAPI `app`.
- If a frontend or npm assets are included, follow its README (e.g., npm install && npm start).

## Accessing the web UI and API docs

- Open the application in a browser:
  - Main UI: http://localhost:8000/ (if provided)
  - Swagger UI: http://localhost:8000/docs
  - ReDoc: http://localhost:8000/redoc

## Key API endpoints (examples)

Note: adapt paths to the actual API prefix in your code (e.g., /api/...). Replace host/port as needed.

- List subjects

  - GET /subjects
  - curl: curl -sS http://localhost:8000/subjects

- Create a subject

  - POST /subjects
  - curl:
    curl -X POST http://localhost:8000/subjects \
     -H "Content-Type: application/json" \
     -d '{"code":"COMP101","name":"Intro to Programming","sync":false}'

- Get subject by id

  - GET /subjects/{subject_id}
  - curl: curl http://localhost:8000/subjects/1

- Update subject

  - PUT or PATCH /subjects/{subject_id}
  - curl:
    curl -X PATCH http://localhost:8000/subjects/1 \
     -H "Content-Type: application/json" \
     -d '{"name":"Programming I"}'

- Delete subject

  - DELETE /subjects/{subject_id}
  - curl: curl -X DELETE http://localhost:8000/subjects/1

- List assessments for a subject

  - GET /subjects/{subject_id}/assessments
  - curl: curl http://localhost:8000/subjects/1/assessments

- Add assessment entry

  - POST /subjects/{subject_id}/assessments
  - curl:
    curl -X POST http://localhost:8000/subjects/1/assessments \
     -H "Content-Type: application/json" \
     -d '{"name":"Assignment 1","weighted_mark":85,"weight":10}'

- Update/delete assessment

  - PATCH /assessments/{assessment_id} DELETE /assessments/{assessment_id}

- Calculate exam mark / set total (if provided by API)
  - POST /subjects/{subject_id}/calculate_exam
  - POST /subjects/{subject_id}/set_total
  - Check /docs for exact payloads.

Always inspect /docs for precise request/response schemas and available endpoints.

## Example workflows

- Create subject → add assessment:

  1. POST /subjects
  2. POST /subjects/{id}/assessments

- Update marks or set totals:
  1. PATCH /assessments/{id} or POST /subjects/{id}/set_total

Refer to interactive docs for example bodies.

## Configuration

- Primary environment variables

  - DATABASE_URL — e.g. sqlite: sqlite:///data/app.db or PostgreSQL: postgresql+asyncpg://user:pass@host/db
  - HOST — hostname to bind (default 0.0.0.0)
  - PORT — port to bind (default 8000)
  - SECRET_KEY — app secret for any signed data
  - DEBUG — enable debug behavior

- Example .env
  DATABASE_URL=sqlite:///data/app.db
  HOST=0.0.0.0
  PORT=8000
  SECRET_KEY=change-me
  DEBUG=true

- Load .env using python-dotenv or the project's configuration loader.

## Database setup & migrations (SQLModel/SQLAlchemy)

- If using migrations (Alembic):
  - Initialize (one-time): alembic init alembic (if not present)
  - Generate migration: alembic revision --autogenerate -m "init"
  - Apply migrations: alembic upgrade head
- If no migrations and the app auto-creates tables:
  - Start the app; on first run it may create tables based on SQLModel models.
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
