#!/usr/bin/env python3
"""Bootstrap local Codex assets, including the global tester subagent."""

from __future__ import annotations

import argparse
from datetime import datetime
import os
from pathlib import Path
import shutil
import sys
import tomllib


ROLE_NAME = "tester"
ROLE_DESCRIPTION = (
    "Manual linked-worktree tester that runs apps through portless and verifies "
    "flows with agent-browser."
)
ROLE_NICKNAMES = ["Verifier", "Runner"]
ROLE_MODEL = "gpt-5.4"
ROLE_REASONING = "medium"
ROLE_SANDBOX = "workspace-write"
ROLE_NETWORK_ACCESS = True
PORTLESS_STATE_DIR = "/tmp/portless"
LEGACY_SKILL_NAME = "personal-agent-test"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Install local Codex skills and register the global tester subagent in "
            "~/.codex."
        )
    )
    parser.add_argument(
        "--repo-root",
        default=Path(__file__).resolve().parents[1],
        type=Path,
        help="Repository root containing .agents and scripts.",
    )
    parser.add_argument(
        "--codex-home",
        type=Path,
        help="Codex home directory (defaults to $CODEX_HOME or ~/.codex).",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace already installed skills in the destination.",
    )
    return parser.parse_args()


def default_codex_home() -> Path:
    return Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")).expanduser()


def load_toml(path: Path) -> dict:
    if not path.exists():
        return {}
    with path.open("rb") as handle:
        return tomllib.load(handle)


def backup_file(path: Path) -> Path | None:
    if not path.exists():
        return None
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    backup = path.with_name(f"{path.name}.bak.{timestamp}")
    shutil.copy2(path, backup)
    return backup


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


def install_skill(source: Path, destination_root: Path, overwrite: bool) -> str:
    destination = destination_root / source.name
    if destination.exists():
        if not overwrite:
            return f"Skipped {source.name}: already exists at {destination}"
        shutil.rmtree(destination)

    shutil.copytree(source, destination)
    return f"Installed {source.name} -> {destination}"


def install_skills(repo_root: Path, codex_home: Path, overwrite: bool) -> list[str]:
    skills_root = repo_root / ".agents" / "skills"
    destination_root = codex_home / "skills"
    destination_root.mkdir(parents=True, exist_ok=True)

    messages = []
    for skill_dir in find_skills(skills_root):
        messages.append(install_skill(skill_dir, destination_root, overwrite))

    legacy_skill = destination_root / LEGACY_SKILL_NAME
    if legacy_skill.exists():
        shutil.rmtree(legacy_skill)
        messages.append(f"Removed legacy installed skill -> {legacy_skill}")

    messages.append(f"Installed {len(find_skills(skills_root))} skill(s) into {destination_root}")
    return messages


def strip_frontmatter(text: str) -> str:
    if not text.startswith("---\n"):
        return text.strip()

    _, _, remainder = text.partition("\n---\n")
    if not remainder:
        return text.strip()
    return remainder.strip()


def load_agent_instructions(repo_root: Path) -> str:
    agent_path = repo_root / ".agents" / "subagents" / "personal-agent-tester" / "AGENT.md"
    if not agent_path.is_file():
        raise FileNotFoundError(f"Tester subagent source not found: {agent_path}")
    return strip_frontmatter(agent_path.read_text(encoding="utf-8"))


def escape_basic_string(value: str) -> str:
    return (
        value.replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\b", "\\b")
        .replace("\f", "\\f")
        .replace("\n", "\\n")
        .replace("\r", "\\r")
        .replace("\t", "\\t")
    )


def format_key(key: str) -> str:
    if key and all(ch.isalnum() or ch in "-_" for ch in key):
        return key
    return f'"{escape_basic_string(key)}"'


def format_value(value):
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, str):
        return f'"{escape_basic_string(value)}"'
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        return repr(value)
    if isinstance(value, list):
        if any(isinstance(item, dict) for item in value):
            raise TypeError("Array-of-table values must be handled separately")
        return "[" + ", ".join(format_value(item) for item in value) + "]"
    raise TypeError(f"Unsupported TOML value type: {type(value)!r}")


def dump_table(table: dict, prefix: list[str] | None = None) -> list[str]:
    prefix = prefix or []
    lines: list[str] = []
    scalars = []
    tables = []
    array_tables = []

    for key, value in table.items():
        if isinstance(value, dict):
            tables.append((key, value))
        elif isinstance(value, list) and value and all(isinstance(item, dict) for item in value):
            array_tables.append((key, value))
        else:
            scalars.append((key, value))

    if prefix:
        lines.append(f"[{'.'.join(format_key(part) for part in prefix)}]")
    for key, value in scalars:
        lines.append(f"{format_key(key)} = {format_value(value)}")

    if prefix and (tables or array_tables):
        lines.append("")

    for index, (key, value) in enumerate(tables):
        lines.extend(dump_table(value, [*prefix, key]))
        if index != len(tables) - 1 or array_tables:
            lines.append("")

    for table_index, (key, values) in enumerate(array_tables):
        table_path = ".".join(format_key(part) for part in [*prefix, key])
        for value_index, value in enumerate(values):
            lines.append(f"[[{table_path}]]")
            lines.extend(dump_table(value, []).copy())
            if value_index != len(values) - 1 or table_index != len(array_tables) - 1:
                lines.append("")

    return lines


def write_toml(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = dump_table(data)
    content = "\n".join(line for line in lines if line is not None).rstrip() + "\n"
    path.write_text(content, encoding="utf-8")


def render_tester_role_toml(instructions: str) -> str:
    escaped_instructions = instructions.replace('"""', '\\"""')
    return (
        f'model = "{ROLE_MODEL}"\n'
        f'model_reasoning_effort = "{ROLE_REASONING}"\n'
        f'sandbox_mode = "{ROLE_SANDBOX}"\n'
        "\n"
        'developer_instructions = """\n'
        f"{escaped_instructions}\n"
        '"""\n'
        "\n"
        "[sandbox_workspace_write]\n"
        f"network_access = {'true' if ROLE_NETWORK_ACCESS else 'false'}\n"
        "\n"
        "[shell_environment_policy.set]\n"
        f'PORTLESS_STATE_DIR = "{PORTLESS_STATE_DIR}"\n'
    )


def install_tester_role(repo_root: Path, codex_home: Path) -> Path:
    instructions = load_agent_instructions(repo_root)
    role_path = codex_home / "agents" / f"{ROLE_NAME}.toml"
    role_path.parent.mkdir(parents=True, exist_ok=True)
    role_path.write_text(render_tester_role_toml(instructions), encoding="utf-8")
    return role_path


def merge_codex_config(config: dict) -> dict:
    merged = dict(config)

    features = dict(merged.get("features", {}))
    features["multi_agent"] = True
    merged["features"] = features

    agents = dict(merged.get("agents", {}))
    agents.setdefault("max_threads", 6)
    agents.setdefault("max_depth", 2)
    agents.setdefault("job_max_runtime_seconds", 1800)
    agents[ROLE_NAME] = {
        "description": ROLE_DESCRIPTION,
        "config_file": f"agents/{ROLE_NAME}.toml",
        "nickname_candidates": ROLE_NICKNAMES,
    }
    merged["agents"] = agents
    return merged


def bootstrap(repo_root: Path, codex_home: Path, overwrite: bool) -> list[str]:
    messages = install_skills(repo_root, codex_home, overwrite)
    role_path = install_tester_role(repo_root, codex_home)
    messages.append(f"Installed tester role config -> {role_path}")

    config_path = codex_home / "config.toml"
    existing = load_toml(config_path)
    backup = backup_file(config_path)
    merged = merge_codex_config(existing)
    write_toml(config_path, merged)
    if backup is not None:
        messages.append(f"Backed up existing config -> {backup}")
    messages.append(f"Updated Codex config -> {config_path}")
    return messages


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.expanduser().resolve()
    codex_home = (args.codex_home or default_codex_home()).expanduser().resolve()

    try:
        messages = bootstrap(repo_root, codex_home, args.overwrite)
    except Exception as exc:  # pragma: no cover - top-level CLI guard
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    for message in messages:
        print(message)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
