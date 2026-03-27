# Skills Naming Convention

Use `.agents/skills/` only for project skills.

## Skill layout

Every skill must live in its own directory and expose `SKILL.md` as the entrypoint:

- `.agents/skills/<skill-name>/SKILL.md`

Examples:

- `.agents/skills/django-patterns/SKILL.md`
- `.agents/skills/personal-test-writer/SKILL.md`

## Generic or imported skills

Skills copied from the internet or meant to stay reusable and generic should keep a regular name:

- `.agents/skills/<skill-name>/SKILL.md`

## Personal skills

Skills that define personal conventions, preferences, or private coding standards should use the `personal-` prefix:

- `.agents/skills/personal-<skill-name>/SKILL.md`

Examples:

- `.agents/skills/personal-python-convention/SKILL.md`
- `.agents/skills/personal-test-writer/SKILL.md`
- `.agents/skills/personal-new-model/SKILL.md`

This keeps generic skills easy to spot and makes personal conventions clearly identifiable.

## Not a skill

If a capability is primarily a specialist agent persona rather than a reusable workflow, do not place it in `.agents/skills/`.

Use `.agents/subagents/` instead.
