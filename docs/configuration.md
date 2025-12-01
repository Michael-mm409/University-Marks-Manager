# Configuration Guide

## Environment Variables (.env)

The app loads environment variables from a `.env` file at the repo root (via `python-dotenv`) and from the process environment. Key variables:

| Variable              | Purpose                                           | Default / Notes                                 |
| --------------------- | ------------------------------------------------- | ----------------------------------------------- |
| `SESSION_SECRET_KEY`  | Required. Secret for server-side sessions         | no default — must be set                        |
| `ENABLE_DEBUG_ROUTES` | Enable debug endpoints (`/api/<ver>/_debug`)      | `false`                                         |
| `DEBUG_TOKEN`         | Optional token required to access debug routes    | unset                                           |
| `DATABASE_URL`        | SQLAlchemy URL for Postgres                       | unset ➜ falls back to SQLite at `data/marks.db` |
| `APP_VERSION`         | Version string shown in footer                    | `dev` if unset                                  |
| `ENV`                 | Environment label in footer (`dev/prod/...`)      | `dev`                                           |
| `API_VERSION`         | API version prefix (used as `/api/<API_VERSION>`) | `v1`                                            |

Docker Compose also uses `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` from `.env` to provision Postgres.

## Paths

- Database file (SQLite fallback): `data/marks.db`
- Static assets: `static/`
- Templates: `src/templates/`

## Theming

- DaisyUI theme toggled via the header switch (`cupcake` vs `dark`).
- Persisted in `localStorage` under `uom-theme`.

## Progressive Scaling (PS) Factor

Stored per subject in `ExamSettings`:

- `ps_exam` (boolean) enables scaling.
- `ps_factor` (float) percentage (default 40). Applied to exam weight.

## Assignment Calculation Rules

- `weighted_mark` is entered directly (mark × weight ÷ 100).
- `unweighted_mark = weighted_mark / mark_weight` when both provided and weight > 0.
- Non-numeric grades (`S`, `U`) nullify numeric fields.

## Exam Target Logic

When saving target total:

```
needed_exam = ((goal/100) * (assignment_weight_percent + scoring_weight) - assignment_weighted_sum) * 100 / scoring_weight
```

Clamp result to [0,100]. If PS enabled: `scoring_weight = exam_weight * (ps_factor/100)`, else `exam_weight`.

## Router Structure (Web)

| File                  | Purpose                       |
| --------------------- | ----------------------------- |
| `semester_views.py`   | Semester pages                |
| `subject_views.py`    | Subject detail                |
| `assignment_views.py` | Assignment CRUD + inline edit |
| `exam_views.py`       | Exam / target total logic     |
| `template_helpers.py` | `_render` helper              |

## Static Build (Tailwind)

- Input: `static/css/input.css`
- Output: `static/css/tailwind.css`
- Build: `npx tailwindcss -i ./static/css/input.css -o ./static/css/tailwind.css --minify`
