---
title: Frequently Asked Questions
---

# Frequently Asked Questions (FAQ)

This page collects common questions about installing, running, and using University Marks Manager. If you don’t see your question here, check the other docs or open an issue.

## Installation and Startup

- How do I install dependencies?

  - Follow the steps in [Installation](installation.md). If you’re on Windows and use Conda, see the README section about `StartMarkManager.bat`.

- How do I run the application?
  - See [Usage](usage.md) for a walkthrough. For the web app, you can also use Docker (see `docker-compose.yml`) or run the FastAPI app with Uvicorn as documented in the README.

## Data and Persistence

- Where is my data stored?

  - By default, local data is under the `data/` directory. If you’re using Postgres (via Docker), data persists in the configured volume.

- Can I migrate from SQLite to Postgres?
  - Yes. See `scripts/migrate_sqlite_to_postgres.py`. Review it for idempotency and run it after configuring your Postgres connection.

## Subjects, Assignments, and Exams

- Can total marks be blank or decimals?

  - Yes. The assignment form accepts blank values, and decimals are parsed safely server-side.

- How are S/U (Satisfactory/Unsatisfactory) grades handled?

  - Enter `S` or `U` where indicated. These are treated distinctly from numeric marks in calculations.

- I can’t delete an exam by ID—what’s the correct identifier?
  - Exams use a composite key: subject code, semester name, and year. Deletions require all three.

## Troubleshooting

- The UI doesn’t update after changes

  - Try a hard refresh and check server logs. Verify the FastAPI app is running and your browser console has no JavaScript errors.

- I get a validation error creating a course with an empty code

  - Empty or whitespace-only course codes are rejected. Provide a non-empty code.

- Something’s broken and I don’t know where to look
  - Start with [Troubleshooting](troubleshooting.md) and the server logs. If needed, open an issue with steps to reproduce.

## Contributing and Governance

- How do I contribute?

  - See [Contributing](contributing.md) for branch, style, and PR guidance.

- Is there a Code of Conduct?
  - Yes. See the repository root [`CODE_OF_CONDUCT.md`](../CODE_OF_CONDUCT.md).

---

Last updated: November 2025
