Welcome — quick rules for this repo

Purpose
- Short, informal guidance for commits, PRs, and basic conventions.
- This is a personal app, so the tone is casual and practical.

Commits
- Use conventional-ish types and include scope when useful: `feat(app)`, `fix(api)`, `refactor`, `docs`, `test`, `chore`, `perf`, `style`, `ci`.
- Keep subject lines short (<=72 chars) and use present tense: `feat(app): add grade import`.
- Use the body to explain the "why" when it's not obvious; bullet points are fine.
- Small housekeeping commits can be `chore:`; breaking changes should mention `BREAKING CHANGE:`.

Commit examples
- `feat(app): add CSV import for assignment marks`
- `fix(api): return 404 when course not found`
- `refactor(store): simplify repository interface`
- `docs: update README with setup steps`

Branches & PRs
- Branch names: `feature/short-desc`, `fix/short-desc`, `refactor/short-desc` (or `feat/` / `fix/` if you prefer).
- PR title: mirror the commit style: `feat(app): nicer semester UI`.
- PR body: quick summary, motivation, testing notes, and manual steps if any.

Suggested PR template (keep it short)
- Title: `type(scope): short summary`
- Summary: One-liner about the change.
- Why: One paragraph about motivation/impact.
- How I tested: Steps, or `automated tests`.
- Notes: any manual migration or follow-ups.

Code style
- Keep things readable over clever. Run the project's linters/formatters (if configured).
- Prefer explicitness; name things so the next-you understands them without explanation.

Testing
- Add a test when a behavior changes or a bug is fixed.
- Aim for small, focused tests. Mock external calls where it reduces flakiness.

Releases & versioning
- For this personal app, semantic versioning is optional — use it if you publish releases.
- Tag notable snapshots like `v1.0.0` when you want to preserve a milestone.

Sensitive info
- Never commit secrets, passwords, or API keys. Use environment variables or a local secrets file excluded by `.gitignore`.

When in doubt
- Leave a short note in the PR and ping me. This is informal — iterate fast and be pragmatic.

Extras you might like
- Add a `CONTRIBUTING.md` later if external contributions start showing up.
- If you want, I can add a small PR template file to `.github/PULL_REQUEST_TEMPLATE.md`.

