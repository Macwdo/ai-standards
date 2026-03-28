---
name: personal-new-django-project
description: Start a new Django project from Macwdo's cookiecutter template repo `https://github.com/Macwdo/django-cookiecutter-standard`, using SSH only when needed. Use when the user wants a fresh Django codebase, a new backend/API project, or a bootstrap flow from the personal template instead of assembling Django manually.
---

# Personal New Django Project

Start a fresh Django project from the personal cookiecutter template repository.

Treat this as a bootstrap-only skill: generate the new project files, confirm the output exists, and stop unless the user explicitly asks for setup or follow-up implementation.

## Defaults

- Template repo: `https://github.com/Macwdo/django-cookiecutter-standard`
- SSH fallback: `git@github.com:Macwdo/django-cookiecutter-standard.git`
- Transport: prefer HTTPS, use SSH if needed
- Scope: project generation only
- Output: create a new project directory without editing the template repo
- Follow-up: do not install dependencies, create virtualenvs, run migrations, or start services unless the user asks

## Workflow

1. Derive the project name and target parent directory from the request.
2. Start with the HTTPS template URL and prefer invoking Cookiecutter directly against it:

```bash
cookiecutter https://github.com/Macwdo/django-cookiecutter-standard
```

3. If `cookiecutter` is not installed but `uvx` is available, use:

```bash
uvx --from cookiecutter cookiecutter https://github.com/Macwdo/django-cookiecutter-standard
```

4. If the HTTPS path fails because SSH access is required, verify SSH access before retrying:

```bash
git ls-remote git@github.com:Macwdo/django-cookiecutter-standard.git HEAD
```

5. Retry generation with the SSH URL when needed:

```bash
cookiecutter git@github.com:Macwdo/django-cookiecutter-standard.git
```

6. If `cookiecutter` is not installed but `uvx` is available, use:

```bash
uvx --from cookiecutter cookiecutter git@github.com:Macwdo/django-cookiecutter-standard.git
```

7. Use a local clone only when direct git-URL invocation is blocked or the user wants to inspect the template first. Clone over HTTPS by default and switch to SSH only if HTTPS access is the blocking issue:

```bash
git clone https://github.com/Macwdo/django-cookiecutter-standard /tmp/django-cookiecutter-standard
cookiecutter /tmp/django-cookiecutter-standard
```

If HTTPS clone access is blocked, use:

```bash
git clone git@github.com:Macwdo/django-cookiecutter-standard.git /tmp/django-cookiecutter-standard
cookiecutter /tmp/django-cookiecutter-standard
```

8. If all required template variables are already known, prefer a non-interactive invocation with explicit key/value overrides. Do not invent missing values.
9. If the template prompts for values that were not provided, ask only for the missing project-specific fields.
10. Generate the project in the requested location and verify the expected output directory exists.
11. Stop after bootstrap. Only continue into environment setup or first implementation when the user explicitly asks.

## Rules

- Treat `https://github.com/Macwdo/django-cookiecutter-standard` as the canonical template URL and `git@github.com:Macwdo/django-cookiecutter-standard.git` as the SSH fallback.
- Never edit or commit inside the template repository as part of project generation.
- Never add extra libraries, files, or conventions beyond what the template generates by default.
- Surface repository or authentication failures with the exact failing command and error.
- If the user asks to begin coding inside the generated project after bootstrap, treat that as a separate task in the new codebase.

## Example Requests

- `Use $personal-new-django-project to start a Django project called billing-api.`
- `Bootstrap a new Django backend from my cookiecutter template in ./services/payments.`
- `Create a fresh Django app from https://github.com/Macwdo/django-cookiecutter-standard and stop after generation.`
