from __future__ import annotations

from contextlib import redirect_stdout
from importlib.util import module_from_spec, spec_from_file_location
import io
from pathlib import Path
import sys
import tempfile
from unittest.mock import patch
import unittest


def load_module(name: str, relative_path: str):
    repo_root = Path(__file__).resolve().parents[1]
    module_path = repo_root / relative_path
    script_dir = str(module_path.parent)
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)
    spec = spec_from_file_location(name, module_path)
    module = module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def create_skill(root: Path, name: str) -> None:
    skill_dir = root / ".agents" / "skills" / name
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: Example\n---\nBody\n",
        encoding="utf-8",
    )


def create_subagent(root: Path, name: str) -> None:
    subagent_dir = root / ".agents" / "subagents" / name
    subagent_dir.mkdir(parents=True)
    (subagent_dir / "config.toml").write_text(
        "\n".join(
            [
                f'name = "{name}"',
                'description = "Example subagent"',
                'model = "openai/gpt-5.4"',
                'reasoning_effort = "medium"',
                'sandbox_mode = "workspace-write"',
                'network_access = true',
                'nickname_candidates = []',
                'skills = []',
                'mcp_servers = []',
                'opencode_profile = "general"',
                "",
            ]
        ),
        encoding="utf-8",
    )
    (subagent_dir / "AGENT.md").write_text("Handle delegated work.\n", encoding="utf-8")


class InstallAssetsTests(unittest.TestCase):
    def test_install_assets_noninteractive_for_opencode(self):
        module = load_module("install_assets", "scripts/install-assets.py")
        with tempfile.TemporaryDirectory() as repo_dir, tempfile.TemporaryDirectory() as opencode_dir:
            repo_root = Path(repo_dir)
            create_skill(repo_root, "personal-new-model")
            create_subagent(repo_root, "subagent")

            messages = module.install_assets(
                repo_root=repo_root,
                cli="opencode",
                assets="both",
                overwrite=True,
                opencode_home=Path(opencode_dir),
            )

            self.assertTrue((Path(opencode_dir) / "skills" / "personal-new-model" / "SKILL.md").is_file())
            self.assertTrue((Path(opencode_dir) / "agents" / "subagent.md").is_file())
            self.assertIn("Installed 1 skill(s)", "\n".join(messages))
            self.assertIn("Installed 1 subagent(s)", "\n".join(messages))

    def test_resolve_cli_prompts_for_missing_cli(self):
        module = load_module("install_assets_prompt", "scripts/install-assets.py")
        with patch("builtins.input", side_effect=["2"]):
            with redirect_stdout(io.StringIO()):
                self.assertEqual(module.resolve_cli(None), "opencode")


if __name__ == "__main__":
    unittest.main()
