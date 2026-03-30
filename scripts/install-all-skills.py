#!/usr/bin/env python3
"""Install every local project skill into a Codex skills directory."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys

from skill_install import find_skills, install_skill


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Install all skills from .agents/skills into a Codex skills directory."
    )
    parser.add_argument(
        "--repo-root",
        default=Path(__file__).resolve().parents[1],
        type=Path,
        help="Repository root containing .agents/skills (defaults to this script's repo).",
    )
    parser.add_argument(
        "--dest",
        type=Path,
        help="Destination skills directory (defaults to $CODEX_HOME/skills or ~/.codex/skills).",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace already installed skills in the destination.",
    )
    return parser.parse_args()


def default_dest() -> Path:
    codex_home = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")).expanduser()
    return codex_home / "skills"


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.expanduser().resolve()
    skills_root = repo_root / ".agents" / "skills"
    destination_root = (args.dest or default_dest()).expanduser().resolve()

    try:
        skills = find_skills(skills_root)
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    destination_root.mkdir(parents=True, exist_ok=True)

    for skill_dir in skills:
        print(install_skill(skill_dir, destination_root, args.overwrite))

    print(f"Installed {len(skills)} skill(s) into {destination_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
