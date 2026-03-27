# AI Standards

This repository is the working home for my Codex skills.

## Install all local skills

Run the installer from the repository root:

```bash
python3 scripts/install-all-skills.py
```

By default it installs every directory in `.agents/skills/` that contains `SKILL.md` into `${CODEX_HOME:-~/.codex}/skills`.

Use `--overwrite` to replace already installed copies:

```bash
python3 scripts/install-all-skills.py --overwrite
```
