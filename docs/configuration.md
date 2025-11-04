# Configuration Guide

## Environment Variables

Currently the app runs with default in-code settings. Introduce a `.env` file (and load via [python-dotenv on PyPI](https://pypi.org/project/python-dotenv/)) if you need externalized config:

| Variable       | Purpose                          | Default                     |
| -------------- | -------------------------------- | --------------------------- |
| `APP_ENV`      | Environment name (`dev`, `prod`) | `dev`                       |
| `DATABASE_URL` | Override SQLite path             | `sqlite:///./data/marks.db` |
| `LOG_LEVEL`    | Logging verbosity                | `INFO`                      |

(Variables above are suggestions; add when implemented.)

## Paths

- Database file: `data/marks.db`
- Static assets: `static/`
- Templates: `src/templates/`

## Theming

- DaisyUI theme toggled via checkbox (`cupcake` vs `dark`).
- Persisted in `localStorage` key `uom-theme`.

## Progressive Scaling (PS) Factor

Stored per subject in `ExamSettings` table:

- `ps_exam` (boolean) enables scaling.
- `ps_factor` (float) percentage (default 40). Applied to exam weight.

## Assignment Calculation Rules

- `weighted_mark` is the contribution (mark \* weight / 100) the user directly enters (design choice).
- `unweighted_mark` computed as `weighted_mark / mark_weight` when both present.
- Non-numeric grades (`S`,`U`) nullify numeric fields.

## Exam Target Logic

When saving target total:

```
needed_exam = ((goal/100) * (assignment_weight_percent + scoring_weight) - assignment_weighted_sum) * 100 / scoring_weight
```

Capped to [0,100]. If PS enabled: `scoring_weight = exam_weight * (ps_factor/100)`, else `exam_weight`.

## Router Structure

| File                  | Purpose                            |
| --------------------- | ---------------------------------- |
| `semester_views.py`   | Semester CRUD + listing            |
| `subject_views.py`    | Subject detail + create            |
| `assignment_views.py` | Assignment CRUD + AJAX inline edit |
| `exam_views.py`       | Exam / target total logic          |
| `template_helpers.py` | `_render` helper                   |

## Static Build (Tailwind)

- Input: `static/css/tailwind.input.css`
- Output: `static/css/tailwind.css`
- Build: `npx tailwindcss -i ./static/css/tailwind.input.css -o ./static/css/tailwind.css --minify`

## Suggested Future Config

- Add `.env` loader.
- Add logging configuration file.
- Add feature flags (e.g., enable inline edit, PS mode) via environment.
