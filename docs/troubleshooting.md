# Troubleshooting & FAQ

## PowerShell npm Security Error

```text
npm : File ... npm.ps1 cannot be loaded because running scripts is disabled
```

Fix:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned -Force
```

Or run with `cmd` / use `npm.cmd`.

## `npx tailwindcss init` fails: "could not determine executable"

Causes:

- Ran the command before installing project dependencies.
- Node version mismatch for the Tailwind release you have installed.

Check which Tailwind your project uses:

- `npm ls tailwindcss` or inspect package.json.

Compatibility summary:

- Tailwind v4+ (current Oxide-based releases) expects a modern Node runtime — Node.js 20 or higher (Node 22 is supported).
- Tailwind v3 works on older Node versions (14/16/18); if you must stay on older Node, stick to v3.x.

Fix:

1. Ensure you have a Node version appropriate for your Tailwind release. Example (use nvm):
   - `nvm install 20 && nvm use 20` (recommended for v4+).
2. Reinstall dependencies:
   - `rm -rf node_modules package-lock.json`
   - `npm install`
   - If Tailwind isn't listed in devDeps: `npm install -D tailwindcss daisyui`
3. Verify and retry:
   - `npx tailwindcss -v` (check CLI version)
   - `npx tailwindcss init`

If npx still fails, run the local binary directly:

- `./node_modules/.bin/tailwindcss init`
- or run via your package scripts (add a script that calls `tailwindcss init`).

## Tailwind directives show lint errors (`@tailwind base;` unknown)

These are editor lint warnings, not build errors. Tailwind CLI processes them correctly.

## 405 Method Not Allowed for HEAD

Add HEAD support to GET routes:

```python
@router.api_route("/path", methods=["GET", "HEAD"])
```

## 404 Subject Not Found

Verify URL parameters: `/semester/{semester}/subject/{code}?year=YYYY` and that row exists in DB.

## Inline Edit Shows Unknown Error

Check JSON response in Network tab. Common causes:

- Duplicate assignment name.
- Invalid numeric input (non-float text). Server returns `{ success:false, error:"..." }`.

## Weighted Mark Resets to 0

Behavior changed: empty fields now leave existing numeric values untouched (edit) or store `None` (create). Ensure you provided either `weighted_mark` or `mark_weight` if expecting recalculated unweighted.

## Exam Mark Not Updating After Adding Assignment

Target total logic only recalculates if `total_mark` parameter (or stored subject total) present. Include hidden `total_mark` in forms if you want recompute.

## Database Locked / In Use

If using SQLite and fast reloads, occasional lock errors can occur. Stop the server, wait a moment, restart. Consider WAL mode for advanced usage.

## How to Rebuild Tailwind CSS

```sh
npx tailwindcss -i ./static/css/tailwind.input.css -o ./static/css/tailwind.css --minify
```

Use `--watch` during development.

## Dark Theme Not Persisting

LocalStorage key: `uom-theme`. Ensure no browser privacy setting is clearing storage between reloads.

## Can't Delete Semester

Ensure `year` form field is posted. Missing year prevents lookup/deletion cascade.

## Add New Docs Section?

Extend by creating Markdown files under `docs/` and linking them in README.
