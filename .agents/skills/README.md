# Skills Naming Convention

Use `.agents/skills/` as the single place for project skills.

## Generic or imported skills

Skills copied from the internet or meant to stay reusable and generic should keep a regular name:

- `.agents/skills/<skill-name>`
- `.agents/skills/<skill-name>.md`

Examples:

- `.agents/skills/django-patterns/`
- `.agents/skills/test-writer.md`

## Personal skills

Skills that define personal conventions, preferences, or private coding standards should use the `personal-` prefix:

- `.agents/skills/personal-<skill-name>`
- `.agents/skills/personal-<skill-name>.md`

Examples:

- `.agents/skills/personal-python-convention.md`
- `.agents/skills/personal-test-writer.md`
- `.agents/skills/personal-new-model.md`

This keeps generic skills easy to spot and makes personal conventions clearly identifiable.
