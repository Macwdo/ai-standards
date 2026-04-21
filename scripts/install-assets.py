#!/usr/bin/env python3
"""Interactive installer for repo skills and subagents."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from agent_install import install_codex_subagents, install_opencode_subagents
from skill_install import (
    default_codex_home,
    default_opencode_home,
    install_skills,
    normalize_cli,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Install this repo's skills and subagents for Codex or OpenCode."
    )
    parser.add_argument(
        "--repo-root",
        default=Path(__file__).resolve().parents[1],
        type=Path,
        help="Repository root containing .agents and scripts.",
    )
    parser.add_argument(
        "--cli",
        choices=("codex", "opencode"),
        help="CLI target to install for.",
    )
    parser.add_argument(
        "--assets",
        choices=("skills", "agents", "both"),
        help="Which assets to install.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace already installed skills and agents.",
    )
    parser.add_argument(
        "--codex-home",
        type=Path,
        help="Codex home directory (defaults to $CODEX_HOME or ~/.codex).",
    )
    parser.add_argument(
        "--opencode-home",
        type=Path,
        help="OpenCode config directory (defaults to $OPENCODE_CONFIG_DIR or ~/.config/opencode).",
    )
    return parser.parse_args()


def prompt_choice(prompt: str, options: list[tuple[str, str]]) -> str:
    print(prompt)
    for index, (_, label) in enumerate(options, start=1):
        print(f"{index}. {label}")

    while True:
        response = input("Select an option: ").strip()
        if response.isdigit():
            index = int(response)
            if 1 <= index <= len(options):
                return options[index - 1][0]
        print("Invalid selection. Enter the number of the desired option.")


def prompt_yes_no(prompt: str, default: bool = False) -> bool:
    suffix = "[Y/n]" if default else "[y/N]"
    while True:
        response = input(f"{prompt} {suffix}: ").strip().lower()
        if not response:
            return default
        if response in {"y", "yes"}:
            return True
        if response in {"n", "no"}:
            return False
        print("Invalid selection. Enter y or n.")


def resolve_cli(cli: str | None) -> str:
    if cli is not None:
        return normalize_cli(cli)
    return prompt_choice(
        "Which CLI are you using?",
        [("codex", "Codex"), ("opencode", "OpenCode")],
    )


def resolve_assets(assets: str | None) -> str:
    if assets is not None:
        return assets
    return prompt_choice(
        "What do you want to install?",
        [
            ("both", "Skills and agents"),
            ("skills", "Skills only"),
            ("agents", "Agents only"),
        ],
    )


def resolve_overwrite(overwrite: bool, prompted: bool) -> bool:
    if prompted:
        return overwrite
    return prompt_yes_no("Overwrite existing installed assets?", default=False)


def install_assets(
    repo_root: Path,
    cli: str,
    assets: str,
    overwrite: bool,
    codex_home: Path | None = None,
    opencode_home: Path | None = None,
) -> list[str]:
    messages: list[str] = []

    if cli == "codex":
        target_root = (codex_home or default_codex_home()).expanduser().resolve()
        if assets in {"skills", "both"}:
            messages.extend(install_skills(repo_root, "codex", overwrite, target_root / "skills"))
        if assets in {"agents", "both"}:
            messages.extend(install_codex_subagents(repo_root, target_root, overwrite))
        return messages

    target_root = (opencode_home or default_opencode_home()).expanduser().resolve()
    if assets in {"skills", "both"}:
        messages.extend(install_skills(repo_root, "opencode", overwrite, target_root / "skills"))
    if assets in {"agents", "both"}:
        messages.extend(install_opencode_subagents(repo_root, target_root, overwrite))
    return messages


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.expanduser().resolve()
    cli = resolve_cli(args.cli)
    assets = resolve_assets(args.assets)
    overwrite = resolve_overwrite(args.overwrite, args.overwrite)

    try:
        messages = install_assets(
            repo_root=repo_root,
            cli=cli,
            assets=assets,
            overwrite=overwrite,
            codex_home=args.codex_home,
            opencode_home=args.opencode_home,
        )
    except Exception as exc:  # pragma: no cover - top-level CLI guard
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    for message in messages:
        print(message)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
