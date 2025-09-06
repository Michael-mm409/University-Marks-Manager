# University Marks Manager

FastAPI + SQLModel + Jinja2 web application for managing university subjects, assignments, and exam mark projections across semesters and academic years.

## ✅ Key Features
**Academic Structure**
- Multi-year + semester organisation
- Subject CRUD
- Assignment CRUD with inline (AJAX) editing

**Grading & Calculation**
- Numeric and S / U grade types
- Independent `weighted_mark` and `mark_weight` entry (unweighted auto-derived)
- Target total mark → required exam mark solver (with progressive scaling mode)
- Real-time recomputation on add/update

**UX**
- Clean Tailwind/DaisyUI interface
- Inline row editing (no full page refresh)
- Dark / light theme toggle (persisted in localStorage)

**Persistence**
- SQLite (via SQLModel / SQLAlchemy engine) in `data/marks.db`
- Exam scaling settings preserved per subject

## 📂 Current Stack
| Layer | Tech |
|-------|------|
| Web framework | FastAPI |
| Templates | Jinja2 |
| ORM | SQLModel / SQLAlchemy |
| Styling | Tailwind CSS (+ DaisyUI) |
| JS Enhancements | Vanilla + small inline helpers |

## 🚀 Quick Start
```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn src.app.main:app --reload
```
Visit: http://127.0.0.1:8000

## 🧪 Optional Tailwind Build (Local Compilation)
If you want to remove CDN usage:
```powershell
npm init -y
npm install -D tailwindcss daisyui
npx tailwindcss -i ./static/css/tailwind.input.css -o ./static/css/tailwind.css --watch
```
Then include `<link rel="stylesheet" href="/static/css/tailwind.css" />` in `base.html` and remove CDN script.

See `docs/tailwind-cli-install.md` for full details.

## 🗂 Project Layout (Relevant Parts)
```
src/
   app/main.py            # FastAPI app factory & router include
   presentation/web/
      views.py             # Aggregated router registration
      assignment_views.py  # Assignment endpoints (CRUD + AJAX)
      subject_views.py     # Subject detail & create
      semester_views.py    # Semester CRUD/listing
      exam_views.py        # Exam + target total logic
      template_helpers.py  # _render wrapper
   infrastructure/db/
      engine.py            # SQLModel engine/session
      models.py            # ORM models (Semester, Subject, Assignment, Examination, ExamSettings)
   core/ / services/      # (Future business logic layering)
static/
   css/tailwind.input.css
   custom.css
templates/
   base.html
   index.html
   subject.html
data/
   marks.db
docs/
   api-reference.md
   configuration.md
   troubleshooting.md
   tailwind-cli-install.md
```

## 🔢 Calculation Highlights
- `weighted_mark` stored directly (user-supplied contribution)
- `unweighted_mark = weighted_mark / mark_weight` (if both numeric)
- When grade type in (S, U) ⇒ numeric fields nulled
- Target total exam requirement:
```
needed_exam = ((goal/100) * (assignment_weight_percent + scoring_weight) - assignment_weighted_sum) * 100 / scoring_weight
```
`scoring_weight` optionally scaled by PS factor: `exam_weight * (ps_factor / 100)`

## 🔄 Inline Editing Flow
1. User clicks Edit → JS fetches `/assignment/{id}/edit` (returns row cells with inputs)
2. User changes values → Save triggers POST `/assignment/{id}/update`
3. Backend validates & recomputes, returns rendered row HTML
4. Row swapped seamlessly

## 🧩 Progressive Scaling (PS) Mode
Stored per subject (ExamSettings): reduces effective exam contribution while leaving original exam weight intact for inference & UI clarity.

## 🧪 Testing (Placeholder)
Add tests under `tests/` (not yet populated). Suggested:
- Assignment numeric parsing
- Exam target solver edge cases (0, impossible, negative required)
- S/U path does not retain numeric data

## 🔧 Configuration
See `docs/configuration.md` for environment suggestions & future extensibility (env vars, feature flags).

## 📘 Additional Documentation
| Doc | Purpose |
|-----|---------|
| `docs/api-reference.md` | Endpoints & form fields |
| `docs/configuration.md` | Settings, calculations, structure |
| `docs/troubleshooting.md` | Common issues & fixes |
| `docs/tailwind-cli-install.md` | Local Tailwind build steps |
| `docs/architecture.md` | (Created in this update) High-level design |

## 🤝 Contributing
PRs welcome. Keep changes small & focused. Follow PEP 8, use type hints, prefer explicitness.

## 🗺 Roadmap Ideas
- REST/JSON API layer (separate from HTML views)
- Authentication / multi-user separation
- Test suite & CI
- Export (CSV / PDF)
- Bulk import of historical marks

## 🪪 License
MIT – see `LICENSE`.

## 📣 Support
Open an issue with reproduction steps and environment details.

---
Generated README reflects current FastAPI-based implementation (replacing legacy Streamlit description).
