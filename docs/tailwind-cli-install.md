# Tailwind CSS CLI Installation Guide

This guide explains how to install and use the Tailwind CSS CLI for building your CSS files, based on the official documentation: https://tailwindcss.com/docs/installation/tailwind-cli

## Prerequisites
- Node.js (v14, v16, v18, or v20 recommended)
- npm (comes with Node.js)

## Installation Steps

1. **Install Tailwind CSS CLI as a dev dependency:**
   Open your terminal in the project root and run:
   ```sh
   npm install -D tailwindcss
   ```

2. **Create your input CSS file:**
   Create a file (e.g., `static/css/tailwind.input.css`) with the following content:
   ```css
   @tailwind base;
   @tailwind components;
   @tailwind utilities;
   ```

3. **Build your CSS with the CLI:**
   Run the following command to generate your output CSS file:
   ```sh
   npx tailwindcss -i ./static/css/tailwind.input.css -o ./static/css/tailwind.css --minify
   ```
   - `-i` specifies the input file
   - `-o` specifies the output file
   - `--minify` reduces file size for production

4. **Include the generated CSS in your HTML:**
   In your base template (e.g., `base.html`), add:
   ```html
   <link rel="stylesheet" href="/static/css/tailwind.css" />
   ```

## Optional: Watch for changes during development
To automatically rebuild your CSS when you edit your input file, run:
```sh
npx tailwindcss -i ./static/css/tailwind.input.css -o ./static/css/tailwind.css --watch
```

## Troubleshooting
- If you see errors about missing CLI, make sure you installed Tailwind in your project root and have a compatible Node.js version.
- If you get permission errors in PowerShell, set the execution policy:
  ```powershell
  Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned -Force
  ```

## References
- [Tailwind CSS CLI Docs](https://tailwindcss.com/docs/installation/tailwind-cli)
