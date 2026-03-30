# Personal Skill Display Names

## Requirements

**User Story:** As a Codex user, I want personal skills with slug names like `personal-my-skill` to appear with a human-readable title, so the installed skill list is easier to scan.

**Acceptance Criteria:**
1. WHEN a personal skill is installed and it does not already define OpenAI UI metadata THEN the installer SHALL create UI metadata with a title-cased `display_name`.
2. WHEN a personal skill slug contains hyphen-separated words THEN the generated `display_name` SHALL render those words as a spaced title, such as `personal-my-skill` -> `Personal My Skill`.
3. IF a skill already defines `agents/openai.yaml` or `agents/openai.yml` THEN the installer SHALL preserve that file without overwriting it.
4. WHEN a non-personal skill is installed THEN the installer SHALL leave its UI metadata unchanged.
5. WHEN the bootstrap or install-all-skills workflow runs THEN both SHALL apply the same display-name generation rule.

## Design

### Overview

Add a shared installer helper that copies skills and, after copying, ensures personal skills have OpenAI UI metadata with a generated `display_name` when none already exists.

### Components and Interfaces

- `scripts/skill_install.py`
  - discovers skill directories
  - installs copied skills
  - generates display names from personal skill slugs
  - writes minimal `agents/openai.yaml` metadata only when missing
- `scripts/bootstrap-codex.py`
  - reuses the shared installer helper
- `scripts/install-all-skills.py`
  - reuses the shared installer helper

### Data Rules

- Source of truth for invocation stays the directory slug and existing `SKILL.md`.
- Generated UI metadata is limited to:

```yaml
interface:
  display_name: "Personal My Skill"
```

- Existing custom metadata files remain authoritative.

### Error Handling

- Missing `.agents/skills` continues to raise the current file-not-found error.
- Existing installed skills still honor `--overwrite`.
- Metadata generation should only create parent directories when needed.

## Tasks

- [ ] Add shared skill installation helpers and personal display-name generation.
- [ ] Update bootstrap and install-all-skills scripts to use the shared helper.
- [ ] Add regression tests for generated metadata and preservation of existing metadata.
- [ ] Document the installed display-name behavior in the README.
