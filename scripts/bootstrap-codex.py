#!/usr/bin/env python3
"""Install local Codex skills and subagents into the global Codex config."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from agent_install import install_codex_subagents
from skill_install import default_codex_home, install_skills


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Install local skills and subagents into ~/.codex."
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
        help="Replace already installed skills and subagents in the destination.",
    )
    return parser.parse_args()


def bootstrap(repo_root: Path, codex_home: Path, overwrite: bool) -> list[str]:
    messages = install_skills(repo_root, "codex", overwrite, codex_home / "skills")
    messages.extend(install_codex_subagents(repo_root, codex_home, overwrite))
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
