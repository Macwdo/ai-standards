from __future__ import annotations

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import tempfile
import textwrap
import tomllib
import unittest


def load_bootstrap_module():
    repo_root = Path(__file__).resolve().parents[1]
    module_path = repo_root / "scripts" / "bootstrap-codex.py"
    spec = spec_from_file_location("bootstrap_codex", module_path)
    module = module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    spec.loader.exec_module(module)
    return module


class BootstrapCodexTests(unittest.TestCase):
    def create_repo(self, root: Path) -> Path:
        (root / ".agents" / "skills" / "sample-skill").mkdir(parents=True)
        (root / ".agents" / "skills" / "sample-skill" / "SKILL.md").write_text(
            "---\nname: sample-skill\n---\nSample\n",
            encoding="utf-8",
        )
        (root / ".agents" / "skills" / "personal-agent-tester" / "agents").mkdir(
            parents=True
        )
        (root / ".agents" / "skills" / "personal-agent-tester" / "SKILL.md").write_text(
            textwrap.dedent(
                """\
                ---
                name: personal-agent-tester
                description: Test stuff
                ---

                Test the linked worktree carefully.
                """
            ),
            encoding="utf-8",
        )
        return root

    def test_bootstrap_installs_skills_and_tester_role(self):
        module = load_bootstrap_module()
        with tempfile.TemporaryDirectory() as repo_dir, tempfile.TemporaryDirectory() as codex_dir:
            repo_root = self.create_repo(Path(repo_dir))
            codex_home = Path(codex_dir)
            (codex_home / "skills" / module.LEGACY_SKILL_NAME).mkdir(parents=True)

            messages = module.bootstrap(repo_root, codex_home, overwrite=True)

            self.assertTrue((codex_home / "skills" / "sample-skill" / "SKILL.md").is_file())
            self.assertFalse((codex_home / "skills" / module.LEGACY_SKILL_NAME).exists())
            self.assertTrue((codex_home / "agents" / "tester.toml").is_file())
            config = tomllib.loads((codex_home / "config.toml").read_text(encoding="utf-8"))
            self.assertTrue(config["features"]["multi_agent"])
            self.assertEqual(config["agents"]["tester"]["config_file"], "agents/tester.toml")
            self.assertIn("Installed tester role config", "\n".join(messages))

    def test_bootstrap_preserves_existing_config_and_creates_backup(self):
        module = load_bootstrap_module()
        with tempfile.TemporaryDirectory() as repo_dir, tempfile.TemporaryDirectory() as codex_dir:
            repo_root = self.create_repo(Path(repo_dir))
            codex_home = Path(codex_dir)
            (codex_home / "config.toml").write_text(
                textwrap.dedent(
                    """\
                    model = "gpt-5.4"

                    [projects."/tmp/example"]
                    trust_level = "trusted"

                    [mcp_servers.docs]
                    url = "https://example.com/mcp"
                    """
                ),
                encoding="utf-8",
            )

            module.bootstrap(repo_root, codex_home, overwrite=True)

            config = tomllib.loads((codex_home / "config.toml").read_text(encoding="utf-8"))
            self.assertEqual(config["model"], "gpt-5.4")
            self.assertEqual(config["projects"]["/tmp/example"]["trust_level"], "trusted")
            self.assertEqual(config["mcp_servers"]["docs"]["url"], "https://example.com/mcp")
            backups = list(codex_home.glob("config.toml.bak.*"))
            self.assertEqual(len(backups), 1)

    def test_bootstrap_is_idempotent(self):
        module = load_bootstrap_module()
        with tempfile.TemporaryDirectory() as repo_dir, tempfile.TemporaryDirectory() as codex_dir:
            repo_root = self.create_repo(Path(repo_dir))
            codex_home = Path(codex_dir)

            module.bootstrap(repo_root, codex_home, overwrite=True)
            module.bootstrap(repo_root, codex_home, overwrite=True)

            config = tomllib.loads((codex_home / "config.toml").read_text(encoding="utf-8"))
            self.assertEqual(config["agents"]["tester"]["description"], module.ROLE_DESCRIPTION)
            self.assertEqual(config["agents"]["max_threads"], 6)
            self.assertTrue(config["features"]["multi_agent"])


if __name__ == "__main__":
    unittest.main()
