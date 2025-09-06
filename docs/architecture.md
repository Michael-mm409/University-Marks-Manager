# Architecture Overview

## High-Level
The application is a server-rendered FastAPI app using Jinja2 templates plus light progressive enhancement (vanilla JS) for inline editing. Data is persisted in SQLite via SQLModel models.

```
Browser (HTML + minimal JS)
        │
FastAPI Routers (presentation/web/*_views.py)
        │
 Jinja2 Templates (templates/*.html)
        │
 SQLModel ORM (infrastructure/db/models.py)
        │
 SQLite (data/marks.db)
```

## Layers
| Layer | Purpose | Location |
|-------|---------|----------|
| Presentation (Routing) | HTTP endpoints (HTML + AJAX) | `src/presentation/web/` |
| Templates | UI rendering | `src/templates/` |
| Infrastructure | DB engine + models | `src/infrastructure/db/` |
| Domain / Core (future) | Business services (expandable) | `src/core/` / `src/model/` |

## Routers
Each concern split into its own router:
- `semester_views.py`: list / create / update / delete semesters
- `subject_views.py`: subject detail + create
- `assignment_views.py`: assignment CRUD + inline editing endpoints
- `exam_views.py`: target total saving, exam deletion
- `views.py`: aggregates routers and defines home route

## Models (SQLModel)
| Model | Key Fields | Notes |
|-------|------------|-------|
| Semester | `name`, `year` | Container for subjects |
| Subject | `subject_code`, `subject_name`, `semester_name`, `year`, `total_mark?`, `sync_subject?` | Holds assignments + exam |
| Assignment | `assessment`, `weighted_mark?`, `unweighted_mark?`, `mark_weight?`, `grade_type` | Independent numeric fields (weighted & weight) |
| Examination | `exam_mark?`, `exam_weight?` | Single exam per subject |
| ExamSettings | `ps_exam`, `ps_factor` | Progressive scaling settings per subject |

## Assignment Calculation Flow
1. User submits/create assignment form (some numeric fields optional).
2. Backend parses `weighted_mark` and `mark_weight` independently.
3. If both numeric and weight > 0 ⇒ compute `unweighted_mark`.
4. For S/U grades ⇒ null numeric fields.
5. Page render recomputes aggregated assignment sums and derived weights.

## Target Total / Exam Solver
Given `goal` (target total %):
```
needed_exam = ((goal/100) * (assignment_weight_percent + scoring_weight) - assignment_weighted_sum) * 100 / scoring_weight
```
- `scoring_weight = exam_weight * (ps_factor/100)` if PS enabled else `exam_weight`.
- Result clamped to [0, 100].

## Inline Editing (AJAX)
Sequence:
1. User clicks Edit → GET `/assignment/{id}/edit` returns `<td>` inputs.
2. User modifies fields → POST `/assignment/{id}/update` with form data.
3. Server validates, updates DB, recalculates row HTML, returns JSON `{ success, row_html }`.
4. JS replaces the row contents without reloading page.

## Progressive Scaling (PS)
When enabled (`ps_exam=True`): only a fraction of the original exam weight contributes toward the average; original weight is retained for display and inference (remaining weight after assignments when absent).

## Error Handling Choices
- Inline edit returns JSON with `error` message; frontend replaces row with alert cell.
- Numeric parsing uses safe float casting; invalid inputs short-circuit with 400 JSON response.
- Missing entities return 404 (HTML or JSON).

## Performance Considerations
Current dataset is small (manual academic records). Simple `select(..).all()` queries acceptable. For scale-up:
- Add indexes on `(semester_name, year)` and `(subject_code, semester_name, year)`.
- Batch aggregation queries instead of Python iteration.

## Future Extensions
| Feature | Notes |
|---------|------|
| Auth & Users | Per-user isolation of data |
| REST API | Parallel JSON API for SPA / mobile |
| Caching | Memoize computed aggregates |
| Test Suite | Pytest for calculators & endpoints |
| Import/Export | CSV or JSON bulk operations |
| Role-based Permissions | Staff vs student views |

## Static Assets Pipeline
Currently optional Tailwind CLI generation. Could migrate to Vite for modular JS if complexity grows.

## Design Principles
- Keep server logic explicit and readable (no hidden magic).
- Avoid coupling calculation logic to templates (pre-compute in views before render).
- Minimize JS; progressive enhancement style.
- Independent field parsing for resilience to partial inputs.

---
Covers current architecture; update this file when refactoring core logic or introducing major subsystems.
