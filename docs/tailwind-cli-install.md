# Tailwind CSS CLI Installation Guide

This guide explains how to install and use the Tailwind CSS CLI for building your CSS files.

## Recommended: Docker build (production)

The project uses a multi-stage Docker build to compile Tailwind CSS automatically. Run the project with:

```sh
docker-compose up --build
```

This is the primary and recommended method for production and CI builds.

## Alternative: Local CLI (development)

For local development without Docker, you can install the Tailwind CLI manually. This is optional — use it only if you prefer building CSS locally.

See the [Tailwind CSS CLI Docs](https://tailwindcss.com/docs/installation/tailwind-cli) for more details.

### Prerequisites

- Node.js (v14, v16, v18, or v20 recommended)
- npm (comes with Node.js)

### Installation steps

1. Install Tailwind CSS CLI as a dev dependency:

   ```sh
   npm install -D tailwindcss
   ```

2. Create your input CSS file:
   Create `src/static/css/input.css` with:

   ```css
   @tailwind base;
   @tailwind components;
   @tailwind utilities;
   ```

3. Build your CSS with the CLI:

   ```sh
   npx tailwindcss -i ./src/static/css/input.css -o ./src/static/css/tailwind.css --minify
   ```

   - `-i` specifies the input file (`src/static/css/input.css`)
   - `-o` specifies the output file (`src/static/css/tailwind.css`)
   - `--minify` reduces file size for production

4. Include the generated CSS in your HTML (example base template):

   ```html
   <link rel="stylesheet" href="/static/css/tailwind.css" />
   ```

### Watch mode (development)

Automatically rebuild when editing:

```sh
npx tailwindcss -i ./src/static/css/input.css -o ./src/static/css/tailwind.css --watch
```

## Troubleshooting

- If the Docker build compiles Tailwind already, prefer using Docker instead of local builds to avoid mismatches.
- If you see CLI missing errors, ensure Tailwind is installed in the project root and Node.js is compatible.
- On PowerShell, if you get permission errors:

  ```powershell
  Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned -Force
  ```

## References

- [Tailwind CSS CLI Docs](https://tailwindcss.com/docs/installation/tailwind-cli)
