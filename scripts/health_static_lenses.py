#!/usr/bin/env python3
"""Deterministic static-lens runner for the plugin health sweep.

Runs the four fully/mostly-deterministic health lenses as a single zero-LLM
Python pass and writes their findings in the **exact** per-lens artifact shape
the LLM lenses use, so discover Phase 4 assembly and `--resume` need no changes.

Converted lenses (each emits one ``.dev/<date>-plugin-health-lens-<name>.json``):

- ``naming-convention-lens`` (naming) — filename + documented-output-path patterns
  against docs/al-dev-naming-convention.md, with the grandfather list read from
  that doc's ``## Grandfathered exceptions`` section.
- ``quality-agent-lens-structure`` (quality, agents) — frontmatter field presence,
  tool canonicality (canonical set read from the projection policy, not a marker),
  Inputs/Outputs sections, header numbering, skill-only-field rejection.
- ``quality-skill-lens-structure`` (quality, skills) — frontmatter ``name``/
  ``description``, the conditional ``argument-hint`` rule, output-file naming,
  header numbering.
- ``design-agent-lens-tool-hygiene`` (design, agents) — declared ``tools`` vs body
  usage verbs.

Output schema (identical to the LLM lenses):
``{lens, findings, suggestion_count, completed_at}`` where ``findings`` is the
same markdown block (``### <Lens> Findings`` + ``- **obj** | sev | obs | fix``
rows, or ``_No issues found._``) the agent returned.

Scope reductions vs. the prior LLM lenses (deliberate, to stay
false-positive-free; mirrored in
profile-al-dev-shared/knowledge/lens-invocation-patterns.md):

- **Tool-hygiene** flags only high-confidence cases: ``Write``/``Edit`` on a
  read-only agent (High), and a declared ``MCP:`` capability whose specific
  capability name is *never* mentioned in the body (Medium). The ambiguous
  negative-context case (e.g. "Do not use Bash") is **not flagged**, and neither
  is a generic ``Read``/``Glob``/``Grep``/``Bash`` "zero literal mention" — those
  tools are routinely exercised through synonym verbs ("create", "append",
  "search") rather than the literal capability word, so a literal-word scan
  over-fires. Only ``MCP:`` capabilities carry a reliable named-usage signal.
- **argument-hint** (in ``quality-skill-lens-structure``) is conditional, keyed on
  concrete patterns only: a literal ``If an argument was passed`` mention, or a
  ``[arg]``-style token appearing **outside** frontmatter and fenced code blocks.
  Any fuzzier "the prose implies an argument" inference is **not flagged**.
- **Output-file naming** (the prior LLM skill-structure check) is **not flagged**
  deterministically. Established non-dated ``.dev/`` handoff files (``progress.md``,
  ``project-context.md``, ``commit-preflight.md``, …) are conventional, and no
  reliable pattern distinguishes a legitimate established handoff file from a
  genuinely mis-named new output; a regex check over-fires. This matches the raw
  LLM lens, which flagged none of these files.

The output filename carries **no surface token** (matching the LLM-lens outputs);
this is only safe because discover serializes surfaces — it runs the script once
per surface, inside the per-surface loop, never with ``--surface both``.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import yaml


REPO = Path(__file__).resolve().parents[1]
POLICY_PATH = REPO / "profile-al-dev-shared/knowledge/agent-tool-projection-policy.md"
CONVENTION_DOC = REPO / "docs/al-dev-naming-convention.md"

# Surface → corpus roots (mirrors discover Phase 0/1; do not re-derive).
SURFACE_ROOTS = {
    "plugin": REPO / "profile-al-dev-shared",
    "tooling": REPO / ".claude",
}

# Dimension membership for each converted lens.
LENS_DIMENSION = {
    "naming-convention-lens": "naming",
    "quality-agent-lens-structure": "quality",
    "quality-skill-lens-structure": "quality",
    "design-agent-lens-tool-hygiene": "design",
}

LENS_HEADING = {
    "naming-convention-lens": "Naming Convention",
    "quality-agent-lens-structure": "Structural Conventions",
    "quality-skill-lens-structure": "Structural Conventions",
    "design-agent-lens-tool-hygiene": "Tool Hygiene",
}

NO_ISSUES = "_No issues found._"


# ---------------------------------------------------------------------------
# Frontmatter / corpus helpers
# ---------------------------------------------------------------------------

def _split_frontmatter(text: str) -> tuple[dict, str]:
    """Return (frontmatter dict, body) for a markdown file. Empty dict if none."""
    m = re.match(r"^---\n(.*?)\n---\n?(.*)$", text, re.DOTALL)
    if not m:
        return {}, text
    try:
        data = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError:
        data = {}
    if not isinstance(data, dict):
        data = {}
    return data, m.group(2)


def _strip_code_and_frontmatter(text: str) -> str:
    """Return body text with YAML frontmatter and fenced code blocks removed."""
    _, body = _split_frontmatter(text)
    # Drop fenced code blocks (``` or ~~~).
    return re.sub(r"(?ms)^[ \t]*(```|~~~).*?^[ \t]*\1[ \t]*$", "", body)


def canonical_tools() -> set[str]:
    """Canonical source-vocabulary tool set = projection_rules.claude keys.

    Same source validate-lens-agents.py uses; no marker-comment coupling.
    """
    data, _ = _split_frontmatter(POLICY_PATH.read_text(encoding="utf-8"))
    return set(data["projection_rules"]["claude"].keys())


def grandfathered_skill_names() -> set[str]:
    """Read the grandfather list from the convention doc's exceptions section."""
    if not CONVENTION_DOC.exists():
        return set()
    text = CONVENTION_DOC.read_text(encoding="utf-8")
    m = re.search(r"##\s+Grandfathered exceptions\s*\n(.*?)(?:\n##\s|\Z)", text, re.DOTALL)
    if not m:
        return set()
    return set(re.findall(r"^-\s+`([^`]+)`", m.group(1), re.MULTILINE))


def agent_files(surface_root: Path) -> list[Path]:
    """Agent .md files for a surface (exclude archived)."""
    root = surface_root / "agents"
    if not root.is_dir():
        return []
    return sorted(
        p for p in root.rglob("*.md") if "archived" not in p.relative_to(root).parts
    )


def skill_files(surface_root: Path) -> list[Path]:
    """SKILL.md files for a surface (exclude archived)."""
    root = surface_root / "skills"
    if not root.is_dir():
        return []
    return sorted(
        p for p in root.rglob("SKILL.md")
        if "archived" not in p.relative_to(root).parts
    )


def changed_paths(since_ref: str) -> set[Path]:
    """Resolved-to-absolute set of files changed since ``since_ref``.

    Uses the SAME normalization Change A introduced into the discover SKILL:
    ``git diff --name-only <ref>`` emits repo-root-relative paths; prepend the
    repo root so the intersection with absolute corpus paths is correct.
    """
    repo_root = Path(
        subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=REPO, capture_output=True, text=True, check=True,
        ).stdout.strip()
    )
    out = subprocess.run(
        ["git", "diff", "--name-only", since_ref],
        cwd=REPO, capture_output=True, text=True, check=True,
    ).stdout.splitlines()
    return {(repo_root / line.strip()).resolve() for line in out if line.strip()}


def _line_of(text: str, needle: str) -> int:
    """1-based line number of the first line containing ``needle`` (or 1)."""
    for i, line in enumerate(text.splitlines(), start=1):
        if needle in line:
            return i
    return 1


# ---------------------------------------------------------------------------
# Findings rendering
# ---------------------------------------------------------------------------

def _render_findings(heading: str, rows: list[str]) -> str:
    """Render the canonical findings block (heading + rows or No-issues)."""
    if not rows:
        return f"### {heading} Findings\n\n{NO_ISSUES}"
    return f"### {heading} Findings\n\n" + "\n".join(rows)


def _row(obj: str, sev: str, obs: str, fix: str) -> str:
    return f"- **{obj}** | {sev} | {obs} | {fix}"


# ---------------------------------------------------------------------------
# Lens: naming-convention-lens
# ---------------------------------------------------------------------------

_LENS_NAME_RE = re.compile(r"^(design|quality)-(agent|skill)-lens-[a-z0-9-]+$")
_MAINTAINER_SKILL_RE = re.compile(r"^[a-z][a-z0-9-]*$")


def check_naming(agent_paths: list[Path], skill_paths: list[Path]) -> list[str]:
    rows: list[str] = []
    grandfathered = grandfathered_skill_names()

    for path in agent_paths:
        name = path.stem
        # Lens agents (filename matches *-lens-*) MUST match the lens pattern,
        # with the single allowed exception of naming-convention-lens.
        if "-lens-" in name and name != "naming-convention-lens":
            if not _LENS_NAME_RE.match(name):
                rows.append(_row(
                    name, "High",
                    f"`{path.name}:1` lens-agent filename does not match "
                    "`{design|quality}-{agent|skill}-lens-{aspect}`",
                    "rename to the enforced lens pattern (see docs/al-dev-naming-convention.md)",
                ))

    for path in skill_paths:
        name = path.parent.name
        # Maintainer skills SHOULD match {verb}-{object}-{aspect}; a non-kebab
        # name not in the grandfather set is a Low advisory finding.
        if not _MAINTAINER_SKILL_RE.match(name) and name not in grandfathered:
            rows.append(_row(
                name, "Low",
                f"`{path.parent.name}/SKILL.md:1` skill name is not kebab-case "
                "`{verb}-{object}-{aspect}`",
                "rename to the advisory pattern or add to "
                "`## Grandfathered exceptions` in docs/al-dev-naming-convention.md",
            ))

    return rows


# ---------------------------------------------------------------------------
# Lens: quality-agent-lens-structure
# ---------------------------------------------------------------------------

_AL_DEV_PREFIX_RE = re.compile(r"^al-dev-")
_KEBAB_RE = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")
SKILL_ONLY_FIELDS = ("argument-hint", "triggers")


def _has_phase_numbering_mix(body: str) -> bool:
    """True if the body mixes 'Phase N' and 'Step N' header numbering."""
    has_phase = bool(re.search(r"^#{1,4}\s+Phase\s+\d", body, re.MULTILINE))
    has_step = bool(re.search(r"^#{1,4}\s+Step\s+\d", body, re.MULTILINE))
    return has_phase and has_step


def check_agent_structure(agent_paths: list[Path], surface: str) -> list[str]:
    rows: list[str] = []
    tools_canonical = canonical_tools()

    for path in agent_paths:
        name = path.stem
        text = path.read_text(encoding="utf-8")
        fm, body = _split_frontmatter(text)

        # High: missing model / tools frontmatter.
        if "model" not in fm:
            rows.append(_row(
                name, "High", f"`{path.name}:1` missing `model` frontmatter field",
                "add a `model:` field (haiku/sonnet/opus)",
            ))
        if "tools" not in fm:
            rows.append(_row(
                name, "High", f"`{path.name}:1` missing `tools` frontmatter field",
                "add a `tools:` field listing canonical capability names",
            ))

        # Medium: filename convention (surface-aware).
        if surface == "plugin":
            if not _AL_DEV_PREFIX_RE.match(name):
                rows.append(_row(
                    name, "Medium",
                    f"`{path.name}:1` distributed agent filename lacks the `al-dev-` prefix",
                    "rename with the distributed `al-dev-<name>` prefix",
                ))
        else:  # tooling
            # Enforced rule: a lens-agent filename (matches *-lens-*) must follow
            # the lens pattern. Other maintainer names are advisory/kebab-case
            # (handled by the naming lens), so only malformed kebab names flag here.
            if "-lens-" in name and name != "naming-convention-lens":
                if not _LENS_NAME_RE.match(name):
                    rows.append(_row(
                        name, "Medium",
                        f"`{path.name}:1` lens-agent filename does not match "
                        "`{design|quality}-{agent|skill}-lens-{aspect}`",
                        "rename to the enforced lens pattern (see docs/al-dev-naming-convention.md)",
                    ))
            elif not _KEBAB_RE.match(name):
                rows.append(_row(
                    name, "Medium",
                    f"`{path.name}:1` maintainer agent filename is not kebab-case",
                    "rename to a kebab-case maintainer name (see docs/al-dev-naming-convention.md)",
                ))

        # Medium: description present.
        if "description" not in fm:
            rows.append(_row(
                name, "Medium", f"`{path.name}:1` missing `description` frontmatter field",
                "add a single-sentence `description:` field",
            ))

        # Medium: non-canonical tool names.
        declared = fm.get("tools")
        if isinstance(declared, list):
            for tool in declared:
                if tool not in tools_canonical:
                    rows.append(_row(
                        name, "Medium",
                        f"`{path.name}:1` declares non-canonical tool `{tool}`",
                        "use a canonical source-vocabulary capability name "
                        "(projection_rules.claude keys in agent-tool-projection-policy.md)",
                    ))

        # Medium: skill-only fields in agent frontmatter.
        for field in SKILL_ONLY_FIELDS:
            if field in fm:
                rows.append(_row(
                    name, "Medium",
                    f"`{path.name}:1` contains skill-only frontmatter field `{field}`",
                    f"remove `{field}` — it is invalid in agent frontmatter",
                ))

        # Medium: Inputs/Outputs sections present.
        if "## Inputs" not in body:
            rows.append(_row(
                name, "Medium", f"`{path.name}` missing `## Inputs` section",
                "add an `## Inputs` section or state why it is absent",
            ))
        if "## Outputs" not in body:
            rows.append(_row(
                name, "Medium", f"`{path.name}` missing `## Outputs` section",
                "add an `## Outputs` section or state why it is absent",
            ))

        # Low: numbering inconsistency.
        if _has_phase_numbering_mix(body):
            rows.append(_row(
                name, "Low",
                f"`{path.name}` mixes `Phase N` and `Step N` header numbering",
                "use one numbering scheme consistently",
            ))

    return rows


# ---------------------------------------------------------------------------
# Lens: quality-skill-lens-structure
# ---------------------------------------------------------------------------

_ARG_TOKEN_RE = re.compile(r"\[[a-z][a-z0-9 _-]*\]")


def _references_optional_argument(text: str) -> bool:
    """Concrete-pattern detection of an instruction-prose argument reference.

    Keyed on: a literal "If an argument was passed" mention, OR a [arg]-style
    token appearing OUTSIDE frontmatter and fenced code blocks. Fuzzy "the prose
    implies an argument" inference is intentionally NOT detected.
    """
    stripped = _strip_code_and_frontmatter(text)
    if "if an argument was passed" in stripped.lower():
        return True
    return bool(_ARG_TOKEN_RE.search(stripped))


def check_skill_structure(skill_paths: list[Path]) -> list[str]:
    rows: list[str] = []

    for path in skill_paths:
        skill_name = path.parent.name
        text = path.read_text(encoding="utf-8")
        fm, body = _split_frontmatter(text)

        # Medium: name matches parent directory.
        fm_name = fm.get("name")
        if fm_name != skill_name:
            rows.append(_row(
                skill_name, "Medium",
                f"`{skill_name}/SKILL.md:1` frontmatter `name` "
                f"({fm_name!r}) does not match parent directory `{skill_name}`",
                "set `name:` to the parent directory name",
            ))

        # Medium: description present.
        if "description" not in fm:
            rows.append(_row(
                skill_name, "Medium",
                f"`{skill_name}/SKILL.md:1` missing `description` frontmatter field",
                "add a `description:` field",
            ))

        # Medium: conditional argument-hint (concrete patterns only).
        if "argument-hint" not in fm and _references_optional_argument(text):
            rows.append(_row(
                skill_name, "Medium",
                f"`{skill_name}/SKILL.md:1` body references an optional argument "
                "but frontmatter has no `argument-hint`",
                "add an `argument-hint:` field describing the optional argument",
            ))

        # Low: numbering inconsistency.
        if _has_phase_numbering_mix(body):
            rows.append(_row(
                skill_name, "Low",
                f"`{skill_name}/SKILL.md` mixes `Phase N` and `Step N` numbering",
                "use one numbering scheme consistently",
            ))

    return rows


# ---------------------------------------------------------------------------
# Lens: design-agent-lens-tool-hygiene
# ---------------------------------------------------------------------------

# Source-vocabulary tools that have observable body usage signals.
_WRITE_EDIT = {"Write", "Edit"}

# Body verbs that evidence a writing/editing action (so the agent is NOT
# read-only). Synonyms are included because agents rarely name the literal
# `Write`/`Edit` capability word.
_WRITE_VERB_RE = re.compile(
    r"\b(write|writes|writing|edit|edits|editing|modif|create|creates|creating|"
    r"append|appends|appending|overwrit|update the|save to|emit to)\b",
    re.IGNORECASE,
)


def _mcp_capability_mentioned(capability: str, body: str) -> bool:
    """Whether an MCP capability's specific name appears in the body.

    Keys on the concrete capability token (e.g. ``al-mcp-server``,
    ``bc-code-intelligence``, ``microsoft-docs``) — NOT the generic word "mcp" —
    so the signal is reliable.
    """
    return capability.lower() in body.lower()


def check_tool_hygiene(agent_paths: list[Path]) -> list[str]:
    rows: list[str] = []

    for path in agent_paths:
        name = path.stem
        text = path.read_text(encoding="utf-8")
        fm, body = _split_frontmatter(text)
        declared = fm.get("tools")
        if not isinstance(declared, list):
            continue

        # Read-only judged from the body: does it only read and return findings?
        read_only = not bool(_WRITE_VERB_RE.search(body))

        for tool in declared:
            # High-confidence case 1: Write/Edit on a read-only agent.
            if tool in _WRITE_EDIT and read_only:
                rows.append(_row(
                    name, "High",
                    f"`{path.name}:1` declares `{tool}` but the body is read-only "
                    "(only reads and returns findings, no write/edit verbs)",
                    f"remove `{tool}` from the tools list",
                ))
                continue
            # High-confidence case 2: an MCP capability never named in the body.
            # (Generic Read/Glob/Grep/Bash zero-mention is intentionally NOT
            # flagged — see the scope-reduction note in the module docstring.)
            if isinstance(tool, str) and tool.startswith("MCP:"):
                capability = tool.split(":", 1)[1].strip()
                if not _mcp_capability_mentioned(capability, body):
                    rows.append(_row(
                        name, "Medium",
                        f"`{path.name}:1` declares `{tool}` but the `{capability}` "
                        "capability is never used in the body",
                        f"remove `{tool}` (Trim) or document its use in the body",
                    ))

    return rows


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------

def run_lens(
    lens: str, agent_paths: list[Path], skill_paths: list[Path], surface: str
) -> list[str]:
    if lens == "naming-convention-lens":
        return check_naming(agent_paths, skill_paths)
    if lens == "quality-agent-lens-structure":
        return check_agent_structure(agent_paths, surface)
    if lens == "quality-skill-lens-structure":
        return check_skill_structure(skill_paths)
    if lens == "design-agent-lens-tool-hygiene":
        return check_tool_hygiene(agent_paths)
    raise ValueError(f"unknown lens: {lens}")


def lenses_in_scope(dimension: str) -> list[str]:
    if dimension == "all":
        return list(LENS_DIMENSION)
    return [lens for lens, dim in LENS_DIMENSION.items() if dim == dimension]


def write_lens_json(out_dir: Path, date: str, lens: str, findings: str, count: int) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{date}-plugin-health-lens-{lens}.json"
    payload = {
        "lens": lens,
        "findings": findings,
        "suggestion_count": count,
        "completed_at": datetime.now(timezone.utc).isoformat(),
    }
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--surface", choices=("plugin", "tooling"), required=True,
                        help="single surface only — never `both` (see module docstring)")
    parser.add_argument("--dimension", choices=("design", "quality", "naming", "all"),
                        default="all")
    parser.add_argument("--since", default=None,
                        help="git ref; narrows scopable checks to changed files")
    parser.add_argument("--out-dir", type=Path, default=Path(".dev"))
    parser.add_argument("--date", required=True, help="YYYY-MM-DD for output filenames")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    surface_root = SURFACE_ROOTS[args.surface]
    agents = agent_files(surface_root)
    skills = skill_files(surface_root)

    # All four converted lenses are SCOPABLE (Change A classification) — honor
    # --since by narrowing the corpus to changed files using the same absolute
    # path normalization the discover SKILL uses.
    if args.since:
        changed = changed_paths(args.since)
        agents = [p for p in agents if p.resolve() in changed]
        skills = [p for p in skills if p.resolve() in changed]

    written: list[Path] = []
    for lens in lenses_in_scope(args.dimension):
        rows = run_lens(lens, agents, skills, args.surface)
        findings = _render_findings(LENS_HEADING[lens], rows)
        path = write_lens_json(args.out_dir, args.date, lens, findings, len(rows))
        written.append(path)
        print(f"{lens}: {len(rows)} finding(s) -> {path}")

    if not written:
        print(f"No static lenses in scope for dimension '{args.dimension}'.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
