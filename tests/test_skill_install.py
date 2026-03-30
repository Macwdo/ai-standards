from __future__ import annotations

from contextlib import redirect_stdout
from importlib.util import module_from_spec, spec_from_file_location
import io
from pathlib import Path
import sys
import tempfile
import textwrap
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
    spec.loader.exec_module(module)
    return module


def create_skill(root: Path, name: str, with_metadata: bool = False) -> Path:
    skill_dir = root / ".agents" / "skills" / name
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: Example\n---\nBody\n",
        encoding="utf-8",
    )
    if with_metadata:
        (skill_dir / "agents").mkdir()
        (skill_dir / "agents" / "openai.yaml").write_text(
            textwrap.dedent(
                """\
                interface:
                  display_name: "Custom Name"
                """
            ),
            encoding="utf-8",
        )
    return skill_dir


class SkillInstallTests(unittest.TestCase):
    def test_display_name_from_slug_title_cases_personal_skill(self):
        module = load_module("skill_install", "scripts/skill_install.py")
        self.assertEqual(
            module.display_name_from_slug("personal-my-skill"),
            "Personal My Skill",
        )
        self.assertEqual(
            module.display_name_from_slug("personal-django-tdd"),
            "Personal Django TDD",
        )

    def test_install_skill_generates_metadata_for_personal_skill_when_missing(self):
        module = load_module("skill_install", "scripts/skill_install.py")
        with tempfile.TemporaryDirectory() as repo_dir, tempfile.TemporaryDirectory() as dest_dir:
            source = create_skill(Path(repo_dir), "personal-test-writer")
            destination_root = Path(dest_dir)

            module.install_skill(source, destination_root, overwrite=True)

            metadata_path = (
                destination_root
                / "personal-test-writer"
                / "agents"
                / "openai.yaml"
            )
            self.assertTrue(metadata_path.is_file())
            self.assertIn('display_name: "Personal Test Writer"', metadata_path.read_text())

    def test_install_skill_preserves_existing_openai_metadata(self):
        module = load_module("skill_install", "scripts/skill_install.py")
        with tempfile.TemporaryDirectory() as repo_dir, tempfile.TemporaryDirectory() as dest_dir:
            source = create_skill(Path(repo_dir), "personal-new-model", with_metadata=True)
            destination_root = Path(dest_dir)

            module.install_skill(source, destination_root, overwrite=True)

            metadata_path = destination_root / "personal-new-model" / "agents" / "openai.yaml"
            self.assertEqual(
                metadata_path.read_text(encoding="utf-8"),
                "interface:\n  display_name: \"Custom Name\"\n",
            )

    def test_install_all_skills_uses_generated_display_metadata(self):
        module = load_module("install_all_skills", "scripts/install-all-skills.py")
        with tempfile.TemporaryDirectory() as repo_dir, tempfile.TemporaryDirectory() as dest_dir:
            repo_root = Path(repo_dir)
            create_skill(repo_root, "personal-new-service")
            create_skill(repo_root, "start-work")

            original_argv = sys.argv[:]
            stdout = io.StringIO()
            try:
                sys.argv = [
                    "install-all-skills.py",
                    "--repo-root",
                    str(repo_root),
                    "--dest",
                    str(Path(dest_dir)),
                    "--overwrite",
                ]
                with redirect_stdout(stdout):
                    exit_code = module.main()
            finally:
                sys.argv = original_argv

            self.assertEqual(exit_code, 0)
            metadata_path = Path(dest_dir) / "personal-new-service" / "agents" / "openai.yaml"
            self.assertTrue(metadata_path.is_file())
            self.assertIn('display_name: "Personal New Service"', metadata_path.read_text())


if __name__ == "__main__":
    unittest.main()
