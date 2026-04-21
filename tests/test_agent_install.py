from __future__ import annotations

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import json
import sys
import tempfile
import textwrap
import tomllib
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


def create_subagent(root: Path, name: str, *, profile: str = "review") -> Path:
    subagent_dir = root / ".agents" / "subagents" / name
    subagent_dir.mkdir(parents=True)
    (subagent_dir / "config.toml").write_text(
        textwrap.dedent(
            f"""\
            name = "{name}"
            description = "Example {name}"
            model = "openai/gpt-5.4"
            reasoning_effort = "high"
            sandbox_mode = "workspace-write"
            network_access = true
            nickname_candidates = ["Example"]
            skills = ["personal-react-patterns", ".system/openai-docs"]
            mcp_servers = ["openaiDeveloperDocs", "context7"]
            opencode_profile = "{profile}"
            """
        ),
        encoding="utf-8",
    )
    (subagent_dir / "AGENT.md").write_text(
        "Use the installed skills and report what matters.\n",
        encoding="utf-8",
    )
    return subagent_dir


class AgentInstallTests(unittest.TestCase):
    def test_render_codex_subagent_injects_skill_paths(self):
        module = load_module("agent_install", "scripts/agent_install.py")
        with tempfile.TemporaryDirectory() as repo_dir, tempfile.TemporaryDirectory() as codex_dir:
            repo_root = Path(repo_dir)
            create_subagent(repo_root, "code-reviewer")
            subagent = module.load_subagent(repo_root / ".agents" / "subagents" / "code-reviewer")

            rendered = module.render_codex_subagent(subagent, Path(codex_dir))

            self.assertIn('name = "code_reviewer"', rendered)
            self.assertIn(
                f'path = "{Path(codex_dir) / "skills" / "personal-react-patterns"}"',
                rendered,
            )
            self.assertIn(
                f'path = "{Path(codex_dir) / "skills" / ".system/openai-docs"}"',
                rendered,
            )
            self.assertIn("[mcp_servers.openaiDeveloperDocs]", rendered)

    def test_render_opencode_subagent_adds_frontmatter_and_restrictions(self):
        module = load_module("agent_install", "scripts/agent_install.py")
        with tempfile.TemporaryDirectory() as repo_dir:
            repo_root = Path(repo_dir)
            create_subagent(repo_root, "code-reviewer", profile="review")
            subagent = module.load_subagent(repo_root / ".agents" / "subagents" / "code-reviewer")

            rendered = module.render_opencode_subagent(subagent)

            self.assertIn('model: "openai/gpt-5.4"', rendered)
            self.assertIn("tools:", rendered)
            self.assertIn("write: false", rendered)
            self.assertIn('bash: "ask"', rendered)

    def test_install_opencode_subagents_writes_agents_and_mcp_config(self):
        module = load_module("agent_install", "scripts/agent_install.py")
        with tempfile.TemporaryDirectory() as repo_dir, tempfile.TemporaryDirectory() as opencode_dir:
            repo_root = Path(repo_dir)
            create_subagent(repo_root, "code-reviewer")

            messages = module.install_opencode_subagents(
                repo_root,
                Path(opencode_dir),
                overwrite=True,
            )

            agent_path = Path(opencode_dir) / "agents" / "code-reviewer.md"
            config_path = Path(opencode_dir) / "opencode.json"
            self.assertTrue(agent_path.is_file())
            self.assertTrue(config_path.is_file())
            config = json.loads(config_path.read_text(encoding="utf-8"))
            self.assertEqual(config["$schema"], module.OPENCODE_SCHEMA_URL)
            self.assertEqual(
                config["mcp"]["context7"]["url"],
                "https://mcp.context7.com/mcp",
            )
            self.assertIn("Installed 1 subagent(s)", "\n".join(messages))

    def test_install_codex_subagents_updates_config(self):
        module = load_module("agent_install", "scripts/agent_install.py")
        with tempfile.TemporaryDirectory() as repo_dir, tempfile.TemporaryDirectory() as codex_dir:
            repo_root = Path(repo_dir)
            create_subagent(repo_root, "code-reviewer")
            (Path(codex_dir) / "config.toml").write_text(
                textwrap.dedent(
                    """\
                    model = "gpt-5.4"

                    [projects."/tmp/example"]
                    trust_level = "trusted"
                    """
                ),
                encoding="utf-8",
            )

            module.install_codex_subagents(repo_root, Path(codex_dir), overwrite=True)

            config = tomllib.loads((Path(codex_dir) / "config.toml").read_text(encoding="utf-8"))
            self.assertEqual(config["projects"]["/tmp/example"]["trust_level"], "trusted")
            self.assertEqual(
                config["agents"]["code_reviewer"]["config_file"],
                "agents/code_reviewer.toml",
            )


if __name__ == "__main__":
    unittest.main()
