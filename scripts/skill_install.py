from __future__ import annotations

import os
from pathlib import Path
import shutil


DISPLAY_NAME_OVERRIDES = {
    "ai": "AI",
    "api": "API",
    "cli": "CLI",
    "drf": "DRF",
    "id": "ID",
    "langgraph": "LangGraph",
    "orm": "ORM",
    "sdk": "SDK",
    "tdd": "TDD",
    "ui": "UI",
    "url": "URL",
    "ux": "UX",
}
OPENAI_METADATA_FILENAMES = ("openai.yaml", "openai.yml")
PERSONAL_SKILL_PREFIX = "personal-"
LEGACY_CODEX_SKILL_NAMES = ("personal-agent-test",)


def default_codex_home() -> Path:
    return Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")).expanduser()


def default_opencode_home() -> Path:
    return Path(
        os.environ.get("OPENCODE_CONFIG_DIR", Path.home() / ".config" / "opencode")
    ).expanduser()


def normalize_cli(cli: str) -> str:
    normalized = cli.strip().lower()
    if normalized not in {"codex", "opencode"}:
        raise ValueError(f"Unsupported CLI target: {cli}")
    return normalized


def default_skills_destination(cli: str) -> Path:
    normalized = normalize_cli(cli)
    if normalized == "codex":
        return default_codex_home() / "skills"
    return default_opencode_home() / "skills"


def find_skills(skills_root: Path) -> list[Path]:
    if not skills_root.is_dir():
        raise FileNotFoundError(f"Skills directory not found: {skills_root}")

    skills = []
    for entry in sorted(skills_root.iterdir()):
        if entry.is_dir() and (entry / "SKILL.md").is_file():
            skills.append(entry)
    if not skills:
        raise FileNotFoundError(f"No skills found under: {skills_root}")
    return skills


def display_name_from_slug(slug: str) -> str:
    words = []
    for word in slug.split("-"):
        if not word:
            continue
        words.append(DISPLAY_NAME_OVERRIDES.get(word, word.capitalize()))
    return " ".join(words)


def ensure_personal_skill_display_metadata(skill_dir: Path) -> None:
    if not skill_dir.name.startswith(PERSONAL_SKILL_PREFIX):
        return

    agents_dir = skill_dir / "agents"
    for filename in OPENAI_METADATA_FILENAMES:
        if (agents_dir / filename).exists():
            return

    agents_dir.mkdir(parents=True, exist_ok=True)
    metadata_path = agents_dir / "openai.yaml"
    metadata_path.write_text(
        "interface:\n"
        f'  display_name: "{display_name_from_slug(skill_dir.name)}"\n',
        encoding="utf-8",
    )


def install_skill(source: Path, destination_root: Path, overwrite: bool) -> str:
    destination = destination_root / source.name
    if destination.exists():
        if not overwrite:
            return f"Skipped {source.name}: already exists at {destination}"
        shutil.rmtree(destination)

    shutil.copytree(source, destination)
    ensure_personal_skill_display_metadata(destination)
    return f"Installed {source.name} -> {destination}"


def cleanup_legacy_codex_skills(destination_root: Path) -> list[str]:
    messages: list[str] = []
    for legacy_name in LEGACY_CODEX_SKILL_NAMES:
        legacy_path = destination_root / legacy_name
        if legacy_path.exists():
            shutil.rmtree(legacy_path)
            messages.append(f"Removed legacy installed skill -> {legacy_path}")
    return messages


def install_skills(
    repo_root: Path,
    cli: str,
    overwrite: bool,
    destination_root: Path | None = None,
) -> list[str]:
    skills_root = repo_root / ".agents" / "skills"
    destination = (destination_root or default_skills_destination(cli)).expanduser().resolve()
    skills = find_skills(skills_root)
    destination.mkdir(parents=True, exist_ok=True)

    messages = [install_skill(skill_dir, destination, overwrite) for skill_dir in skills]
    if normalize_cli(cli) == "codex":
        messages.extend(cleanup_legacy_codex_skills(destination))
    messages.append(f"Installed {len(skills)} skill(s) into {destination}")
    return messages
