---
name: personal-new-django-project
description: Start a new Django project from Macwdo's SSH cookiecutter template repo `git@github.com:Macwdo/django-cookiecutter-standard.git`. Use when the user wants a fresh Django codebase, a new backend/API project, or a bootstrap flow from the personal template instead of assembling Django manually.
---

# Personal New Django Project

Start a fresh Django project from the personal cookiecutter template repository.

Treat this as a bootstrap-only skill: generate the new project files, confirm the output exists, and stop unless the user explicitly asks for setup or follow-up implementation.

## Defaults

- Template repo: `git@github.com:Macwdo/django-cookiecutter-standard.git`
- Transport: SSH only
- Scope: project generation only
- Output: create a new project directory without editing the template repo
- Follow-up: do not install dependencies, create virtualenvs, run migrations, or start services unless the user asks

## Workflow

1. Derive the project name and target parent directory from the request.
2. Verify SSH access before attempting generation:

```bash
git ls-remote git@github.com:Macwdo/django-cookiecutter-standard.git HEAD
```

3. Prefer invoking Cookiecutter directly against the git URL:

```bash
cookiecutter git@github.com:Macwdo/django-cookiecutter-standard.git
```

4. If `cookiecutter` is not installed but `uvx` is available, use:

```bash
uvx --from cookiecutter cookiecutter git@github.com:Macwdo/django-cookiecutter-standard.git
```

5. Use a local SSH clone only when direct git-URL invocation is blocked or the user wants to inspect the template first:

```bash
git clone git@github.com:Macwdo/django-cookiecutter-standard.git /tmp/django-cookiecutter-standard
cookiecutter /tmp/django-cookiecutter-standard
```

6. If all required template variables are already known, prefer a non-interactive invocation with explicit key/value overrides. Do not invent missing values.
7. If the template prompts for values that were not provided, ask only for the missing project-specific fields.
8. Generate the project in the requested location and verify the expected output directory exists.
9. Stop after bootstrap. Only continue into environment setup or first implementation when the user explicitly asks.

## Rules

- Never switch the template source to HTTPS when the SSH repo is the canonical source.
- Never edit or commit inside the template repository as part of project generation.
- Never add extra libraries, files, or conventions beyond what the template generates by default.
- Surface repository or authentication failures with the exact failing command and error.
- If the user asks to begin coding inside the generated project after bootstrap, treat that as a separate task in the new codebase.

## Example Requests

- `Use $personal-new-django-project to start a Django project called billing-api.`
- `Bootstrap a new Django backend from my cookiecutter template in ./services/payments.`
- `Create a fresh Django app from git@github.com:Macwdo/django-cookiecutter-standard.git and stop after generation.`
