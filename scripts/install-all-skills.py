#!/usr/bin/env python3
"""Install every local project skill into a Codex or OpenCode skills directory."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from skill_install import default_skills_destination, install_skills, normalize_cli


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Install all skills from .agents/skills into a Codex or OpenCode skills directory."
    )
    parser.add_argument(
        "--repo-root",
        default=Path(__file__).resolve().parents[1],
        type=Path,
        help="Repository root containing .agents/skills (defaults to this script's repo).",
    )
    parser.add_argument(
        "--cli",
        choices=("codex", "opencode"),
        default="codex",
        help="CLI target to install for (defaults to codex).",
    )
    parser.add_argument(
        "--dest",
        type=Path,
        help="Destination skills directory (defaults to the selected CLI global skills directory).",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace already installed skills in the destination.",
    )
    return parser.parse_args()
def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.expanduser().resolve()
    cli = normalize_cli(args.cli)
    destination_root = (args.dest or default_skills_destination(cli)).expanduser().resolve()

    try:
        messages = install_skills(repo_root, cli, args.overwrite, destination_root)
    except (FileNotFoundError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    for message in messages:
        print(message)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
