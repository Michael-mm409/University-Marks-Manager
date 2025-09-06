# API Reference

Base URL: `/`

## Conventions
- All HTML form endpoints use `application/x-www-form-urlencoded`.
- JSON responses are only returned by AJAX endpoints (assignment inline edit).
- Query parameter `year` is required for all semester/subject scoped GET views.

## Semester Endpoints
| Method | Path | Description | Form Fields |
|--------|------|-------------|-------------|
| GET | `/` | Home page listing semesters (optional year filter) | `year` (query) |
| POST | `/semester/create` | Create semester if it doesn't exist | `name`, `year` |
| POST | `/semester/{semester}/update` | Rename a semester | `year`, `new_name` |
| POST | `/semester/{semester}/delete` | Delete semester and related data | `year` |
| GET | `/semester/{semester}?year=YYYY` | Semester detail (subjects + summary) | `year` (query) |

## Subject Endpoints
| Method | Path | Description | Form Fields |
|--------|------|-------------|-------------|
| POST | `/semester/{semester}/subject/create` | Create subject | `year`, `subject_code`, `subject_name`, `sync_subject?` |
| GET | `/semester/{semester}/subject/{code}?year=YYYY` | Subject detail (assignments + summary + exam) | `year` (query) |
| POST | `/semester/{semester}/subject/{code}/update` | Update subject code/name | `year`, `subject_code`, `subject_name` |
| POST | `/semester/{semester}/subject/{code}/delete` | Delete subject + children | `year` |

## Assignment Endpoints
| Method | Path | Description | Form Fields |
|--------|------|-------------|-------------|
| POST | `/semester/{semester}/subject/{code}/assignment/create` | Create assignment | `year`, `assessment`, `weighted_mark?`, `mark_weight?`, `grade_type` |
| POST | `/semester/{semester}/subject/{code}/assignment/{id}/delete` | Delete assignment | `year` |
| GET | `/semester/{semester}/subject/{code}/assignment/{id}/edit?year=YYYY` | AJAX: fetch inline edit cells | `year` (query) |
| POST | `/semester/{semester}/subject/{code}/assignment/{id}/update` | AJAX: update assignment | `year`, `assessment`, `weighted_mark?`, `mark_weight?`, `grade_type` |

### Assignment Field Rules
- `grade_type` values: `numeric`, `S`, `U`.
- When `numeric`: `weighted_mark` and `mark_weight` independent; `unweighted_mark = weighted_mark / mark_weight` if both provided and weight > 0.
- When `S` or `U`: all numeric fields are null.

## Exam / Total Mark Endpoints
| Method | Path | Description | Form Fields |
|--------|------|-------------|-------------|
| POST | `/semester/{semester}/subject/{code}/totalMark/save` | Derive/store exam mark from target total OR set explicit exam mark | `year`, `total_mark?`, `exam_mark?`, `ps_exam?`, `ps_factor?` |
| POST | `/semester/{semester}/subject/{code}/exam/{exam_id}/delete` | Delete exam | `year` |

### PS (Progressive Scaling) Settings
Persisted per subject in `ExamSettings`:
- `ps_exam` (checkbox) enables scaling.
- `ps_factor` (percentage) scales effective exam weight: `effective_weight = exam_weight * (ps_factor/100)`.

## Computed Values on Subject Page
| Name | Description |
|------|-------------|
| `assignment_weighted_sum` | Sum of assignment weighted marks (numeric) |
| `assignment_weight_percent` | Sum of assignment mark_weight percentages |
| `effective_exam_weight` | Actual exam weight stored or inferred remaining |
| `effective_scoring_exam_weight` | After PS scaling |
| `average` | Overall weighted % (assignments + scaled exam) |
| `required_exam_mark` | Calculated exam % needed for target final total |

## JSON Responses
`POST /.../assignment/{id}/update`:
```json
{ "success": true, "row_html": "<td>...</td>..." }
```
Errors:
```json
{ "success": false, "error": "Message" }
```

## Error Codes
| Code | Meaning |
|------|---------|
| 400 | Validation failure (duplicate name, invalid numeric) |
| 404 | Not found (subject/assignment/exam) |
| 500 | Unhandled server error (trace returned in JSON during dev) |

## Versioning
Currently unversioned; stable route contracts assumed for UI. Introduce prefix (e.g. `/api/v1`) before exposing externally.
