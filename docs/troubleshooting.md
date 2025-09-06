# Troubleshooting & FAQ

## PowerShell npm Security Error
```
npm : File ... npm.ps1 cannot be loaded because running scripts is disabled
```
Fix:
```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned -Force
```
Or run with `cmd` / use `npm.cmd`.

## `npx tailwindcss init` fails: "could not determine executable"
Causes:
- Ran command before installing dependencies.
- Using unsupported Node version (v22). Tailwind supports 14/16/18/20.

Fix:
1. Install LTS Node (e.g. 20).
2. Reinstall: `rm -r node_modules package-lock.json` then `npm install -D tailwindcss daisyui`.
3. Retry: `npx tailwindcss init`.

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
