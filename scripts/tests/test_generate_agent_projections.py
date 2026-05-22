import inspect
from pathlib import Path
import importlib.util
import re
import tempfile

spec = importlib.util.spec_from_file_location(
    "generate_agent_projections",
    Path(__file__).resolve().parent.parent / "generate-agent-projections.py",
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def test_policy_exposes_documented_translation_tables():
    policy = mod.default_projection_policy()
    assert policy["claude"]["USER_GATE"] == "AskUserQuestion"
    assert policy["copilot"]["Read"] == "read"
    assert policy["codex"]["USER_GATE"]["developer_instruction"] == "request_user_input"


def test_shared_agent_tools_use_normalized_vocabulary():
    agent_paths = sorted(Path("profile-al-dev-shared/agents").glob("*.md"))
    allowed = {
        "Read",
        "Write",
        "Edit",
        "Glob",
        "Grep",
        "Bash",
        "USER_GATE",
        "MCP: al-mcp-server",
        "MCP: bc-code-intelligence",
        "MCP: microsoft-docs",
    }
    legacy_hits = []
    for path in agent_paths:
        text = path.read_text(encoding="utf-8")
        match = re.search(r"tools:\s*\[(.*?)\]", text, re.DOTALL)
        if not match:
            continue
        tokens = [
            token.strip().strip('"')
            for token in match.group(1).replace("\n", " ").split(",")
            if token.strip()
        ]
        bad = [token for token in tokens if token not in allowed]
        if bad:
            legacy_hits.append((path.name, bad))
    assert legacy_hits == [], legacy_hits


def test_shared_agents_do_not_use_askuserquestion_literal():
    text = Path("profile-al-dev-shared/agents/al-dev-interview.md").read_text(encoding="utf-8")
    assert "AskUserQuestion" not in text
    assert "USER_GATE" in text


def test_project_claude_preserves_supported_shared_tools():
    agent = {
        "name": "al-dev-interview",
        "description": "Collect requirements",
        "tools": ["Read", "Write", "USER_GATE"],
        "body": "# Agent: al-dev-interview\nUse USER_GATE when blocked.\n",
    }
    rendered = mod.render_claude_projection(agent, mod.default_projection_policy())
    assert 'tools: ["Read", "Write", "AskUserQuestion"]' in rendered


def test_project_copilot_translates_aliases():
    agent = {
        "name": "al-dev-interview",
        "description": "Collect requirements",
        "tools": ["Read", "Write", "USER_GATE"],
        "body": "# Agent: al-dev-interview\nUse USER_GATE when blocked.\n",
    }
    rendered = mod.render_copilot_projection(agent, mod.default_projection_policy())
    assert 'tools: ["read", "edit", "ask_user"]' in rendered


def test_project_codex_emits_toml():
    agent = {
        "name": "al-dev-interview",
        "description": "Collect requirements",
        "tools": ["Read", "Write", "USER_GATE"],
        "body": "# Agent: al-dev-interview\nUse USER_GATE when blocked.\n",
    }
    rendered = mod.render_codex_projection(agent, mod.default_projection_policy())
    assert 'name = "al-dev-interview"' in rendered
    assert 'developer_instructions = """' in rendered
    assert "request_user_input" in rendered
    assert "projected_tools" not in rendered


def test_unsupported_mapping_fails_closed():
    agent = {
        "name": "al-dev-script-engineer",
        "description": "Run scripts",
        "tools": ["ImaginaryTool"],
        "body": "# Agent: al-dev-script-engineer\n",
    }
    try:
        mod.render_copilot_projection(agent, mod.default_projection_policy())
    except ValueError as exc:
        assert "ImaginaryTool" in str(exc)
    else:
        raise AssertionError("Expected ValueError for unsupported mapping")


def test_generate_all_writes_expected_files(tmp_path):
    output_root = tmp_path / "generated" / "agents"
    agents = [
        {
            "name": "al-dev-interview",
            "description": "Collect requirements",
            "tools": ["Read", "Write", "USER_GATE"],
            "body": "# Agent: al-dev-interview\nUse USER_GATE when blocked.\n",
        },
        {
            "name": "al-dev-explore",
            "description": "Explore a codebase",
            "tools": ["Read", "Bash"],
            "body": "# Agent: al-dev-explore\nUse shell execution when needed.\n",
        },
    ]
    mod.write_all_projections(output_root, agents, mod.default_projection_policy())
    assert (output_root / "claude" / "al-dev-interview.md").exists()
    assert (output_root / "copilot" / "al-dev-explore.md").exists()
    assert (output_root / "codex" / "al-dev-explore.toml").exists()


def test_generate_all_is_deterministic(tmp_path):
    output_root = tmp_path / "generated" / "agents"
    agents = [
        {
            "name": "al-dev-interview",
            "description": "Collect requirements",
            "tools": ["Read", "Write", "USER_GATE"],
            "body": "# Agent: al-dev-interview\nUse USER_GATE when blocked.\n",
        }
    ]
    mod.write_all_projections(output_root, agents, mod.default_projection_policy())
    first = (output_root / "copilot" / "al-dev-interview.md").read_text(encoding="utf-8")
    mod.write_all_projections(output_root, agents, mod.default_projection_policy())
    second = (output_root / "copilot" / "al-dev-interview.md").read_text(encoding="utf-8")
    assert first == second


def _run_test(func):
    signature = inspect.signature(func)
    if not signature.parameters:
        func()
        return
    if list(signature.parameters) == ["tmp_path"]:
        with tempfile.TemporaryDirectory() as td:
            func(Path(td))
        return
    raise TypeError(f"Unsupported test signature: {func.__name__}{signature}")


if __name__ == "__main__":
    tests = sorted(
        (name, value)
        for name, value in globals().items()
        if name.startswith("test_") and callable(value)
    )
    failures = []
    for name, func in tests:
        try:
            _run_test(func)
        except Exception as exc:  # noqa: BLE001
            failures.append(f"{name}: {exc}")
    if failures:
        for failure in failures:
            print(failure)
        raise SystemExit(1)
    print(f"{len(tests)} tests passed")
