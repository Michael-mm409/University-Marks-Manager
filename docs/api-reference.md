# API Reference

This project exposes a server-rendered web UI and a JSON API.

## Web UI (HTML)

Pretty, human-friendly routes:

| Method | Path                                              | Description                               |
| ------ | ------------------------------------------------- | ----------------------------------------- |
| GET    | `/`                                               | Home; redirects to current year or `/all` |
| GET    | `/all`                                            | All years                                 |
| GET    | `/year/{year}`                                    | Year overview                             |
| GET    | `/year/{year}/semester/{semester}`                | Semester overview                         |
| GET    | `/year/{year}/semester/{semester}/subject/{code}` | Subject detail (assignments + exam)       |

Notes:

- Some actions return fragments for HTMX swaps (inline edits, selectors).
- Legacy URLs with `?year=` are redirected to the pretty routes above.

## JSON API (`/api/v1`)

Base path: `/api/v1`. Selected endpoints (see Swagger `/docs` for full list):

| Method | Path                              | Description                       |
| ------ | --------------------------------- | --------------------------------- |
| GET    | `/api/v1/semesters`               | List semesters (optional `year`)  |
| POST   | `/api/v1/semesters`               | Create semester                   |
| GET    | `/api/v1/semesters/{semester_id}` | Get semester                      |
| PUT    | `/api/v1/semesters/{semester_id}` | Update semester                   |
| DELETE | `/api/v1/semesters/{semester_id}` | Delete semester                   |
| GET    | `/api/v1/subjects`                | List subjects (filters supported) |
| POST   | `/api/v1/subjects`                | Create subject                    |
| GET    | `/api/v1/subjects/{subject_id}`   | Get subject                       |
| PUT    | `/api/v1/subjects/{subject_id}`   | Update subject                    |
| DELETE | `/api/v1/subjects/{subject_id}`   | Delete subject                    |
| GET    | `/api/v1/_health`                 | API health check                  |

Assignments and exams have additional endpoints under `/api/v1/subjects/...` — consult `/docs` for schemas and request bodies.

### Assignment Field Rules

- `grade_type` values: `numeric`, `S`, `U`.
- When `numeric`: `weighted_mark` and `mark_weight` are independent; `unweighted_mark = weighted_mark / mark_weight` when both provided and weight > 0.
- When `S` or `U`: numeric fields are null.

### PS (Progressive Scaling) Settings

Persisted per subject in `ExamSettings`:

- `ps_exam` (checkbox) enables scaling.
- `ps_factor` (percentage) scales effective exam weight: `effective_weight = exam_weight * (ps_factor/100)`.

### Computed Values on Subject Page

| Name                            | Description                                     |
| ------------------------------- | ----------------------------------------------- |
| `assignment_weighted_sum`       | Sum of assignment weighted marks (numeric)      |
| `assignment_weight_percent`     | Sum of assignment mark_weight percentages       |
| `effective_exam_weight`         | Actual exam weight stored or inferred remaining |
| `effective_scoring_exam_weight` | After PS scaling                                |
| `average`                       | Overall weighted % (assignments + scaled exam)  |
| `required_exam_mark`            | Calculated exam % needed for target final total |

## Error Codes

| Code | Meaning                                                    |
| ---- | ---------------------------------------------------------- |
| 400  | Validation failure (duplicate name, invalid numeric)       |
| 404  | Not found (subject/assignment/exam)                        |
| 500  | Unhandled server error (trace returned in JSON during dev) |

## Versioning

API is versioned under `/api/v1`. Legacy `/api/*` requests are redirected with HTTP 308.
