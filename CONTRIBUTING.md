Thanks for looking — quick contributing tips (short & informal)

This is my personal app, so contributions are relaxed and pragmatic. If you open a PR, here's a tiny guide to make review fast:

- Pick a clear branch name: `feature/short-desc`, `fix/short-desc`, or `refactor/short-desc`.
- Use commit types like `feat(app)`, `fix(api)`, `refactor`, `docs`, `chore`.
- Keep each PR focused — one small change or a cohesive feature.

PR checklist (keep it short)
- Title follows `type(scope): short summary`.
- One-line summary + short motivation in the PR body.
- Tests added or note why none were needed.
- No secrets included.

How to run tests locally
- Python (venv):

  python -m venv .venv
  source .venv/bin/activate
  pip install -r requirements-dev.txt
  pytest

Coding style
- Run the project's linters/formatters before submitting (see `setup.cfg`).

Need help?
- Open an issue describing the goal and any constraints.

References
- See `my-service/CLAUDE.md` for more informal rules and PR examples.

Thanks — quick, friendly reviews preferred. Iterate fast.
