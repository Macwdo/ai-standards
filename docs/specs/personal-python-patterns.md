# Personal Python Patterns

## Requirements

**User Story:** As a Codex user working in Python repositories, I want one personal umbrella skill for my default Python implementation style, so framework-specific work starts from consistent coding, testing, and architectural patterns.

**Acceptance Criteria:**
1. WHEN Codex is asked to write or refactor Python code in a repo that should follow my defaults THEN the skill SHALL provide framework-agnostic Python patterns that apply before framework-specific rules.
2. WHEN the task involves Python module design THEN the skill SHALL instruct Codex to prefer typed functions, explicit boundaries, dependency injection, and repo-first conventions over generic examples.
3. WHEN the task involves Python tests THEN the skill SHALL instruct Codex to keep tests behavior-focused, setup-visible, and aligned with existing helpers or fixtures instead of opaque abstractions.
4. WHEN the task becomes Django- or LangGraph-specific THEN the skill SHALL direct Codex to compose with the existing personal Django or LangGraph skills rather than duplicating those rules.
5. WHEN the skill is installed or listed in compatible UIs THEN it SHALL expose human-readable OpenAI interface metadata that matches the skill purpose.

## Design

### Overview

Create a new `personal-python-patterns` skill as a lightweight umbrella for Python code shape, boundaries, and validation defaults. Keep the main `SKILL.md` concise, then offload concrete guidance into two references: one for implementation patterns and one for testing and validation defaults.

### Components and Interfaces

- `.agents/skills/personal-python-patterns/SKILL.md`
  - defines the trigger-rich description
  - provides the core workflow and composition rules
- `.agents/skills/personal-python-patterns/references/implementation.md`
  - captures Python code structure, typing, dependency, and module-boundary defaults
- `.agents/skills/personal-python-patterns/references/testing.md`
  - captures testing, helper reuse, and validation defaults
- `.agents/skills/personal-python-patterns/agents/openai.yaml`
  - provides UI-facing `display_name`, `short_description`, and `default_prompt`

### Data Rules

- The skill remains framework-agnostic and should not restate Django or LangGraph details already covered elsewhere.
- The skill should define repo-first rules that can apply to plain Python modules, services, orchestration code, CLIs, and tests.
- References should stay one level deep from `SKILL.md` and be directly linked from it.

### Error Handling

- If a repo already establishes a stronger local convention, the skill should tell Codex to follow the repo instead of forcing a generic pattern.
- If a task is clearly framework-specific, the skill should redirect to the matching personal framework skill.
- Validation should fail fast if the skill metadata or frontmatter becomes invalid.

## Tasks

- [ ] Draft the requirements-backed umbrella workflow and composition rules for `personal-python-patterns`.
- [ ] Add implementation and testing reference files with reusable Python defaults.
- [ ] Generate or update OpenAI interface metadata for the new skill.
- [ ] Validate the new skill with the skill-creator validation script.
