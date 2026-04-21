from __future__ import annotations

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys
import tempfile
import textwrap
import tomllib
import unittest


def load_bootstrap_module():
    repo_root = Path(__file__).resolve().parents[1]
    module_path = repo_root / "scripts" / "bootstrap-codex.py"
    script_dir = str(module_path.parent)
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)
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
        (root / ".agents" / "skills" / "personal-agent-tester").mkdir(parents=True)
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
        (root / ".agents" / "subagents" / "code-reviewer").mkdir(parents=True)
        (root / ".agents" / "subagents" / "code-reviewer" / "config.toml").write_text(
            textwrap.dedent(
                """\
                name = "code-reviewer"
                description = "Review code carefully."
                model = "openai/gpt-5.4"
                reasoning_effort = "high"
                sandbox_mode = "workspace-write"
                network_access = true
                nickname_candidates = ["Reviewer"]
                skills = ["personal-agent-tester"]
                mcp_servers = []
                opencode_profile = "review"
                """
            ),
            encoding="utf-8",
        )
        (root / ".agents" / "subagents" / "code-reviewer" / "AGENT.md").write_text(
            "Review the code and report issues.\n",
            encoding="utf-8",
        )
        return root

    def test_bootstrap_installs_skills_and_subagents(self):
        module = load_bootstrap_module()
        with tempfile.TemporaryDirectory() as repo_dir, tempfile.TemporaryDirectory() as codex_dir:
            repo_root = self.create_repo(Path(repo_dir))
            codex_home = Path(codex_dir)
            (codex_home / "skills" / "personal-agent-test").mkdir(parents=True)
            (codex_home / "agents" / "tester.toml").parent.mkdir(parents=True)
            (codex_home / "agents" / "tester.toml").write_text("legacy\n", encoding="utf-8")

            messages = module.bootstrap(repo_root, codex_home, overwrite=True)

            self.assertTrue((codex_home / "skills" / "sample-skill" / "SKILL.md").is_file())
            self.assertFalse((codex_home / "skills" / "personal-agent-test").exists())
            self.assertTrue((codex_home / "agents" / "code_reviewer.toml").is_file())
            self.assertFalse((codex_home / "agents" / "tester.toml").exists())
            config = tomllib.loads((codex_home / "config.toml").read_text(encoding="utf-8"))
            self.assertTrue(config["features"]["multi_agent"])
            self.assertEqual(
                config["agents"]["code_reviewer"]["config_file"],
                "agents/code_reviewer.toml",
            )
            self.assertIn("Installed code_reviewer", "\n".join(messages))

    def test_bootstrap_generates_display_metadata_for_personal_skill_when_missing(self):
        module = load_bootstrap_module()
        with tempfile.TemporaryDirectory() as repo_dir, tempfile.TemporaryDirectory() as codex_dir:
            repo_root = self.create_repo(Path(repo_dir))
            codex_home = Path(codex_dir)

            module.bootstrap(repo_root, codex_home, overwrite=True)

            metadata_path = (
                codex_home
                / "skills"
                / "personal-agent-tester"
                / "agents"
                / "openai.yaml"
            )
            self.assertTrue(metadata_path.is_file())
            self.assertIn('display_name: "Personal Agent Tester"', metadata_path.read_text())

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
            self.assertEqual(config["agents"]["code_reviewer"]["description"], "Review code carefully.")
            self.assertEqual(config["agents"]["max_threads"], 6)
            self.assertTrue(config["features"]["multi_agent"])


if __name__ == "__main__":
    unittest.main()
