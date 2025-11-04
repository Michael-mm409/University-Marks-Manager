# Contributing Guidelines

This document outlines the workflow and contribution guidelines for this project.

## Git Workflow

We follow a modified version of the [Git Flow](https://nvie.com/posts/a-successful-git-branching-model/) workflow.

### Branch Naming Convention

All branches should follow this naming format:
```
<type>/<jira-ticket>
```

Where:
- `<type>` is one of the following:
  - `feature`: New features or improvements
  - `doc`: Documentation changes
  - `chore`: Maintenance tasks
  - `bugfix`: Bug fixes
- `<jira-ticket>` is the Jira ticket number (e.g., VEAI-34)

Example: `feature/VEAI-34`

## Pull Request Process

1. Create a branch following the naming convention above
2. Make your changes and commit them 
3. Create a Pull Request to the `dev` branch
4. Ensure at least two approving reviews before merging

### Pull Request Title Format

Pull Request titles should follow this format:
```
[<type>] [<jira-ticket>] Brief Description
```

Example: `[feature] [VEAI-34] Implement user authentication`

### Pull Request Description

All Pull Requests should use the template provided in `.github/PULL_REQUEST_TEMPLATE.md`, which includes:

- Overview of changes
- Detailed list of changes made
- Testing information
- Jira ticket link
- Reviewer notes

## Merging

- All PRs should target the `dev` branch
- Use "Squash commit" when merging
- The merge commit message should match the PR title
- Work branches should never be deleted after merging

Feel free to add directories as needed, following the established pattern.

## Questions

If you have any questions about the contribution process, please reach out to the project technical lead @hmxmghl or team lead @dvorakman 