# Contributing Guide

Thank you for considering contributing to University Marks Manager!

## How to Contribute

1. **Fork the Repository**  
   Click "Fork" at the top right of the GitHub page and clone your fork:

   ```sh
   git clone https://github.com/Michael-mm409/university-marks-manager.git
   cd university-marks-manager
   ```

2. **Create a Branch**

   ```sh
   git checkout -b feature/your-feature-name
   ```

3. **Make Your Changes**

   - Follow the existing code style (PEP8 for Python).
   - Add or update docstrings for new functions/classes.
   - Add tests if possible.

4. **Commit and Push**

   ```sh
   git add .
   git commit -m "Describe your changes"
   git push origin feature/your-feature-name
   ```

5. **Open a Pull Request**
   - Go to the GitHub page for your fork.
   - Click "Compare & pull request".
   - Describe your changes and submit.

## Code Style

- Use clear, descriptive variable and function names.
- Write docstrings for all public functions and classes.
- Keep functions short and focused.

### CSS changes (Tailwind)

- Edit styles in `src/static/css/input.css`.
- Run the build before committing: `npm run build:css`.
- A Git pre-commit hook (Husky) will also build CSS and prevent commits if `src/static/css/tailwind.css` changes during the hook; if it does, the hook stages the updated file and asks you to re-run the commit.

## Reporting Issues

- Use the [GitHub Issues](https://github.com/Michael-mm409/university-marks-manager/issues) page.
- Include steps to reproduce, expected behavior, and screenshots if possible.

## Code of Conduct

- Be respectful and constructive.
- See [CODE_OF_CONDUCT.md](../CODE_OF_CONDUCT.md) for details.

---

Thank you for helping improve University Marks Manager!
