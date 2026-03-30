- [ ] 1. Create the spec-backed skill scaffold
- [ ] 1.1 Initialize `.agents/skills/personal-django-patterns` with `references/` and generated UI metadata
  - Use the repo as the target location instead of the global Codex skill directory.
  - _Requirements: 6, 7_

- [ ] 2. Author the main skill workflow
- [ ] 2.1 Replace the initializer template in `SKILL.md`
  - Describe the umbrella use case and the inspect-first workflow.
  - Reference the model, endpoint, and testing documents.
  - _Requirements: 1, 2, 6_

- [ ] 3. Add reference documentation
- [ ] 3.1 Create `references/models.md`
  - Capture base classes, field patterns, `fmt_model_str`, admin registration, and migrations.
  - _Requirements: 3, 6_
- [ ] 3.2 Create `references/endpoints.md`
  - Capture APIView/action, serializer, service, permission, and response rules.
  - _Requirements: 4, 6_
- [ ] 3.3 Create `references/testing.md`
  - Capture helper-first pytest/DRF workflow and forbidden patterns.
  - _Requirements: 5, 6_

- [ ] 4. Validate and finish
- [ ] 4.1 Run quick validation and inspect the generated metadata
  - _Requirements: 7, 8_
- [ ] 4.2 Review diff, stage only intended files, commit, merge into `master`, and push
  - _Requirements: 8_
