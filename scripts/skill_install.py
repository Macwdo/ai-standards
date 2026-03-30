from __future__ import annotations

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
