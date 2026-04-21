from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import json
from pathlib import Path
import shutil
import tomllib

from skill_install import default_codex_home, default_opencode_home, normalize_cli


SUBAGENT_CONFIG_FILENAME = "config.toml"
SUBAGENT_PROMPT_FILENAME = "AGENT.md"
CODEX_AGENT_DEFAULTS = {
    "max_threads": 6,
    "max_depth": 2,
    "job_max_runtime_seconds": 1800,
}
LEGACY_CODEX_AGENT_NAMES = ("tester",)
OPENCODE_SCHEMA_URL = "https://opencode.ai/config.json"

CODEX_MCP_SNIPPETS = {
    "openaiDeveloperDocs": [
        "[mcp_servers.openaiDeveloperDocs]",
        'url = "https://developers.openai.com/mcp"',
        "",
        "[mcp_servers.openaiDeveloperDocs.tools.fetch_openai_doc]",
        'approval_mode = "approve"',
        "",
        "[mcp_servers.openaiDeveloperDocs.tools.search_openai_docs]",
        'approval_mode = "approve"',
    ],
    "context7": [
        "[mcp_servers.context7]",
        'command = "npx"',
        'args = ["-y", "@upstash/context7-mcp"]',
    ],
}

OPENCODE_MCP_DEFINITIONS = {
    "openaiDeveloperDocs": {
        "type": "remote",
        "url": "https://developers.openai.com/mcp",
        "enabled": True,
    },
    "context7": {
        "type": "remote",
        "url": "https://mcp.context7.com/mcp",
        "enabled": True,
    },
}

OPENCODE_PROFILE_OVERRIDES = {
    "review": {
        "tools": {"write": False, "edit": False},
        "permission": {"bash": "ask", "webfetch": "allow"},
    },
    "advisory": {
        "tools": {"write": False, "edit": False},
        "permission": {"bash": "ask", "webfetch": "allow"},
    },
}


@dataclass(frozen=True)
class SubagentDefinition:
    name: str
    description: str
    model: str
    reasoning_effort: str | None
    sandbox_mode: str
    network_access: bool
    nickname_candidates: list[str]
    skills: list[str]
    mcp_servers: list[str]
    opencode_profile: str
    instructions: str

    @property
    def codex_name(self) -> str:
        return self.name.replace("-", "_")

    @property
    def codex_model(self) -> str:
        if "/" in self.model:
            return self.model.split("/", 1)[1]
        return self.model


def find_subagents(subagents_root: Path) -> list[Path]:
    if not subagents_root.is_dir():
        raise FileNotFoundError(f"Subagents directory not found: {subagents_root}")

    subagents = []
    for entry in sorted(subagents_root.iterdir()):
        if not entry.is_dir():
            continue
        if (entry / SUBAGENT_CONFIG_FILENAME).is_file() and (
            entry / SUBAGENT_PROMPT_FILENAME
        ).is_file():
            subagents.append(entry)
    if not subagents:
        raise FileNotFoundError(f"No subagents found under: {subagents_root}")
    return subagents


def load_subagent(path: Path) -> SubagentDefinition:
    config_path = path / SUBAGENT_CONFIG_FILENAME
    with config_path.open("rb") as handle:
        raw = tomllib.load(handle)

    name = raw["name"]
    if name != path.name:
        raise ValueError(f"Subagent name mismatch for {path}: {name} != {path.name}")

    instructions = (path / SUBAGENT_PROMPT_FILENAME).read_text(encoding="utf-8").strip()
    return SubagentDefinition(
        name=name,
        description=raw["description"],
        model=raw["model"],
        reasoning_effort=raw.get("reasoning_effort"),
        sandbox_mode=raw["sandbox_mode"],
        network_access=raw.get("network_access", False),
        nickname_candidates=list(raw.get("nickname_candidates", [])),
        skills=list(raw.get("skills", [])),
        mcp_servers=list(raw.get("mcp_servers", [])),
        opencode_profile=raw.get("opencode_profile", "general"),
        instructions=instructions,
    )


def load_subagents(subagents_root: Path) -> list[SubagentDefinition]:
    return [load_subagent(path) for path in find_subagents(subagents_root)]


def load_toml(path: Path) -> dict:
    if not path.exists():
        return {}
    with path.open("rb") as handle:
        return tomllib.load(handle)


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def backup_file(path: Path) -> Path | None:
    if not path.exists():
        return None
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    backup = path.with_name(f"{path.name}.bak.{timestamp}")
    shutil.copy2(path, backup)
    return backup


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


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def yaml_scalar(value) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if value is None:
        return "null"
    if isinstance(value, (int, float)):
        return str(value)
    return json.dumps(value)


def dump_yaml(value, indent: int = 0) -> list[str]:
    prefix = " " * indent
    if isinstance(value, dict):
        lines: list[str] = []
        for key, item in value.items():
            if isinstance(item, (dict, list)):
                lines.append(f"{prefix}{key}:")
                lines.extend(dump_yaml(item, indent + 2))
            else:
                lines.append(f"{prefix}{key}: {yaml_scalar(item)}")
        return lines
    if isinstance(value, list):
        lines = []
        for item in value:
            if isinstance(item, (dict, list)):
                lines.append(f"{prefix}-")
                lines.extend(dump_yaml(item, indent + 2))
            else:
                lines.append(f"{prefix}- {yaml_scalar(item)}")
        return lines
    return [f"{prefix}{yaml_scalar(value)}"]


def render_codex_subagent(subagent: SubagentDefinition, codex_home: Path) -> str:
    lines = [
        f'name = "{escape_basic_string(subagent.codex_name)}"',
        f'description = "{escape_basic_string(subagent.description)}"',
    ]
    if subagent.nickname_candidates:
        nicknames = ", ".join(
            f'"{escape_basic_string(nickname)}"'
            for nickname in subagent.nickname_candidates
        )
        lines.append(f"nickname_candidates = [{nicknames}]")

    lines.extend(
        [
            "",
            f'model = "{escape_basic_string(subagent.codex_model)}"',
        ]
    )
    if subagent.reasoning_effort:
        lines.append(
            f'model_reasoning_effort = "{escape_basic_string(subagent.reasoning_effort)}"'
        )
    lines.extend(
        [
            f'sandbox_mode = "{escape_basic_string(subagent.sandbox_mode)}"',
            "",
            'developer_instructions = """',
            subagent.instructions.replace('"""', '\\"""'),
            '"""',
        ]
    )

    for mcp_name in subagent.mcp_servers:
        snippet = CODEX_MCP_SNIPPETS.get(mcp_name)
        if snippet is None:
            raise KeyError(f"Unsupported Codex MCP server: {mcp_name}")
        lines.append("")
        lines.extend(snippet)

    if subagent.sandbox_mode == "workspace-write":
        lines.extend(
            [
                "",
                "[sandbox_workspace_write]",
                f"network_access = {'true' if subagent.network_access else 'false'}",
            ]
        )

    for skill_name in subagent.skills:
        skill_path = codex_home / "skills" / skill_name
        lines.extend(
            [
                "",
                "[[skills.config]]",
                f'path = "{escape_basic_string(str(skill_path))}"',
                "enabled = true",
            ]
        )

    return "\n".join(lines).rstrip() + "\n"


def build_opencode_frontmatter(subagent: SubagentDefinition) -> dict:
    frontmatter: dict = {
        "description": subagent.description,
        "mode": "subagent",
        "model": subagent.model,
    }
    if subagent.reasoning_effort:
        frontmatter["reasoningEffort"] = subagent.reasoning_effort

    overrides = OPENCODE_PROFILE_OVERRIDES.get(subagent.opencode_profile)
    if overrides:
        frontmatter.update(overrides)
    return frontmatter


def render_opencode_subagent(subagent: SubagentDefinition) -> str:
    frontmatter_lines = dump_yaml(build_opencode_frontmatter(subagent))
    return "---\n" + "\n".join(frontmatter_lines) + "\n---\n" + subagent.instructions + "\n"


def merge_codex_config(config: dict, subagents: list[SubagentDefinition]) -> dict:
    merged = dict(config)

    features = dict(merged.get("features", {}))
    features["multi_agent"] = True
    merged["features"] = features

    agents = dict(merged.get("agents", {}))
    for key, value in CODEX_AGENT_DEFAULTS.items():
        agents.setdefault(key, value)
    for legacy_name in LEGACY_CODEX_AGENT_NAMES:
        agents.pop(legacy_name, None)
    for subagent in subagents:
        agents[subagent.codex_name] = {
            "description": subagent.description,
            "config_file": f"agents/{subagent.codex_name}.toml",
        }
    merged["agents"] = agents
    return merged


def merge_opencode_config(
    config: dict,
    required_mcp_servers: set[str],
    overwrite: bool,
) -> dict:
    merged = dict(config)
    merged.setdefault("$schema", OPENCODE_SCHEMA_URL)

    mcp = dict(merged.get("mcp", {}))
    for mcp_name in sorted(required_mcp_servers):
        definition = OPENCODE_MCP_DEFINITIONS.get(mcp_name)
        if definition is None:
            raise KeyError(f"Unsupported OpenCode MCP server: {mcp_name}")
        if overwrite or mcp_name not in mcp:
            mcp[mcp_name] = definition
    if mcp:
        merged["mcp"] = mcp
    return merged


def install_codex_subagents(
    repo_root: Path,
    codex_home: Path | None = None,
    overwrite: bool = False,
) -> list[str]:
    resolved_home = (codex_home or default_codex_home()).expanduser().resolve()
    subagents = load_subagents(repo_root / ".agents" / "subagents")
    destination_root = resolved_home / "agents"
    destination_root.mkdir(parents=True, exist_ok=True)

    messages: list[str] = []
    for subagent in subagents:
        destination = destination_root / f"{subagent.codex_name}.toml"
        if destination.exists() and not overwrite:
            messages.append(f"Skipped {subagent.codex_name}: already exists at {destination}")
            continue
        destination.write_text(
            render_codex_subagent(subagent, resolved_home),
            encoding="utf-8",
        )
        messages.append(f"Installed {subagent.codex_name} -> {destination}")

    for legacy_name in LEGACY_CODEX_AGENT_NAMES:
        legacy_path = destination_root / f"{legacy_name}.toml"
        if legacy_path.exists():
            legacy_path.unlink()
            messages.append(f"Removed legacy installed agent -> {legacy_path}")

    config_path = resolved_home / "config.toml"
    existing = load_toml(config_path)
    backup = backup_file(config_path)
    merged = merge_codex_config(existing, subagents)
    write_toml(config_path, merged)
    if backup is not None:
        messages.append(f"Backed up existing config -> {backup}")
    messages.append(f"Updated Codex config -> {config_path}")
    messages.append(f"Installed {len(subagents)} subagent(s) into {destination_root}")
    return messages


def install_opencode_subagents(
    repo_root: Path,
    opencode_home: Path | None = None,
    overwrite: bool = False,
) -> list[str]:
    resolved_home = (opencode_home or default_opencode_home()).expanduser().resolve()
    subagents = load_subagents(repo_root / ".agents" / "subagents")
    destination_root = resolved_home / "agents"
    destination_root.mkdir(parents=True, exist_ok=True)

    messages: list[str] = []
    for subagent in subagents:
        destination = destination_root / f"{subagent.name}.md"
        if destination.exists() and not overwrite:
            messages.append(f"Skipped {subagent.name}: already exists at {destination}")
            continue
        destination.write_text(render_opencode_subagent(subagent), encoding="utf-8")
        messages.append(f"Installed {subagent.name} -> {destination}")

    required_mcp_servers = {
        mcp_name for subagent in subagents for mcp_name in subagent.mcp_servers
    }
    config_path = resolved_home / "opencode.json"
    existing = load_json(config_path)
    backup = backup_file(config_path)
    merged = merge_opencode_config(existing, required_mcp_servers, overwrite)
    write_json(config_path, merged)
    if backup is not None:
        messages.append(f"Backed up existing config -> {backup}")
    messages.append(f"Updated OpenCode config -> {config_path}")
    messages.append(f"Installed {len(subagents)} subagent(s) into {destination_root}")
    return messages


def install_subagents(
    repo_root: Path,
    cli: str,
    overwrite: bool,
    destination_root: Path | None = None,
) -> list[str]:
    normalized = normalize_cli(cli)
    if normalized == "codex":
        return install_codex_subagents(repo_root, destination_root, overwrite)
    return install_opencode_subagents(repo_root, destination_root, overwrite)
