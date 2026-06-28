#!/usr/bin/env python3
"""Validate that skills listed in artifact-contracts.md honour the contract structure."""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
_CROSS_REF_TOKEN = "knowledge/artifact-contracts.md"
_FINAL_GATE_PHRASE = "success evidence named in"


@dataclass(frozen=True)
class Violation:
    path: str
    rule: str
    issue: str
    fix: str


# ---------------------------------------------------------------------------
# Table parsing
# ---------------------------------------------------------------------------

def _table_cells(line: str) -> list[str]:
    """Return stripped cell values from a markdown pipe-table line."""
    parts = line.strip().split("|")
    return [c.strip() for c in parts[1:-1]]


def _is_separator(cells: list[str]) -> bool:
    return bool(cells) and all(re.match(r"^:?-+:?$", c) for c in cells)


def parse_contract_matrix(text: str) -> list[dict[str, str]]:
    """Parse the Contract Matrix table rows into dicts keyed by column header."""
    rows: list[dict[str, str]] = []
    headers: list[str] | None = None

    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            if headers is not None:
                break  # blank or prose line ends the table
            continue
        cells = _table_cells(stripped)
        if _is_separator(cells):
            continue
        if headers is None:
            headers = cells
        elif len(cells) >= len(headers):
            rows.append(dict(zip(headers, cells)))

    return rows


# ---------------------------------------------------------------------------
# Skill-name extraction and path-token extraction
# ---------------------------------------------------------------------------

def extract_skill_name(raw: str) -> str:
    """Extract skill name from a cell value like '`al-dev-plan`'."""
    m = re.search(r"`([^`]+)`", raw)
    return m.group(1) if m else raw.strip()


def extract_path_tokens(text: str) -> list[str]:
    """Return .dev/ path-like tokens found in text (used for rule 4)."""
    return re.findall(r"\.dev/[a-zA-Z0-9*._-]+", text)


# ---------------------------------------------------------------------------
# Per-row conformance checks (rules 1–4)
# ---------------------------------------------------------------------------

def check_row(
    row: dict[str, str],
    skill_name: str,
    skills_root: Path,
) -> list[Violation]:
    rel_skill = f"profile-al-dev-shared/skills/{skill_name}/SKILL.md"
    rel_contract = "profile-al-dev-shared/knowledge/artifact-contracts.md"
    skill_path = skills_root / skill_name / "SKILL.md"

    # Rule 1: row resolution
    if not skill_path.is_file():
        return [Violation(
            rel_contract,
            "row-resolution",
            f"row '{skill_name}' does not resolve to an existing SKILL.md at {rel_skill}",
            "create the SKILL.md or remove the row from the matrix",
        )]

    try:
        body = skill_path.read_text(encoding="utf-8")
    except OSError as exc:
        return [Violation(
            rel_skill,
            "row-resolution",
            f"SKILL.md is unreadable: {exc}",
            "fix file permissions or encoding",
        )]

    violations: list[Violation] = []

    # Rule 2: cross-reference present
    if _CROSS_REF_TOKEN not in body:
        violations.append(Violation(
            rel_skill,
            "artifact-contract-cross-reference",
            f"contract row exists but body has no reference to '{_CROSS_REF_TOKEN}'",
            "add the standard cross-reference block under the intent-preflight section",
        ))

    # Rule 3: final-gate rule present
    if _FINAL_GATE_PHRASE not in body:
        violations.append(Violation(
            rel_skill,
            "artifact-contract-final-gate",
            f"body lacks the canonical final-gate phrase '{_FINAL_GATE_PHRASE}'",
            f"add final-gate wording containing '{_FINAL_GATE_PHRASE}' before any completion claim",
        ))

    # Rule 4: success-evidence path alignment
    evidence = row.get("Success evidence", "")
    tokens = extract_path_tokens(evidence)
    if tokens and not any(tok in body for tok in tokens):
        violations.append(Violation(
            rel_contract,
            "success-evidence-alignment",
            f"row '{skill_name}' names success-evidence path(s) {tokens} "
            f"but the skill body never references them",
            "update the matrix row or the skill body so the path appears in both",
        ))

    return violations


# ---------------------------------------------------------------------------
# Orphan check (rule 5)
# ---------------------------------------------------------------------------

def check_orphans(
    skills_root: Path,
    matrix_skill_names: set[str],
) -> list[Violation]:
    violations: list[Violation] = []
    if not skills_root.exists():
        return violations

    for skill_md in sorted(skills_root.rglob("SKILL.md")):
        try:
            body = skill_md.read_text(encoding="utf-8")
        except OSError:
            continue
        if _CROSS_REF_TOKEN not in body:
            continue
        skill_name = skill_md.parent.name
        if skill_name not in matrix_skill_names:
            rel = f"profile-al-dev-shared/skills/{skill_name}/SKILL.md"
            violations.append(Violation(
                rel,
                "orphan-contract-reference",
                f"skill '{skill_name}' references '{_CROSS_REF_TOKEN}' "
                f"but has no row in the Contract Matrix",
                f"add a row for '{skill_name}' to artifact-contracts.md",
            ))
    return violations


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def validate(
    repo_root: Path | None = None,
) -> tuple[list[Violation], int]:
    """
    Run all five conformance rules against the live tree.

    Returns (violations, skill_count) where skill_count is the number of
    rows found in the contract matrix (zero if the matrix could not be parsed).
    """
    root = repo_root if repo_root is not None else _REPO_ROOT
    contract_path = root / "profile-al-dev-shared" / "knowledge" / "artifact-contracts.md"
    skills_root = root / "profile-al-dev-shared" / "skills"

    if not contract_path.exists():
        return [Violation(
            str(contract_path),
            "contract-missing",
            "artifact-contracts.md not found",
            "create the contract document",
        )], 0

    try:
        text = contract_path.read_text(encoding="utf-8")
    except OSError as exc:
        return [Violation(
            "profile-al-dev-shared/knowledge/artifact-contracts.md",
            "contract-unreadable",
            str(exc),
            "fix file permissions or encoding",
        )], 0

    rows = parse_contract_matrix(text)

    if not rows:
        return [Violation(
            "profile-al-dev-shared/knowledge/artifact-contracts.md",
            "empty-contract",
            "the contract document exists but has no rows in its Contract Matrix table",
            "add rows to the Contract Matrix table in artifact-contracts.md",
        )], 0

    violations: list[Violation] = []
    matrix_skill_names: set[str] = set()

    for row in rows:
        skill_name = extract_skill_name(row.get("Skill", ""))
        if not skill_name:
            continue
        matrix_skill_names.add(skill_name)
        violations.extend(check_row(row, skill_name, skills_root))

    violations.extend(check_orphans(skills_root, matrix_skill_names))
    return violations, len(matrix_skill_names)


def _format_violation(v: Violation) -> str:
    return (
        f"{v.path}\n"
        f"  rule: {v.rule}\n"
        f"  issue: {v.issue}\n"
        f"  fix: {v.fix}"
    )


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    repo_root = Path(args[0]) if args else None
    violations, skill_count = validate(repo_root)

    if violations:
        blocks = "\n\n".join(_format_violation(v) for v in violations)
        print(blocks)
        return 1

    print(f"OK: {skill_count} skills conform to artifact-contracts.md")
    print("\nRunning artifact contract tests...")
    all_passed = run_artifact_tests(repo_root)
    if all_passed:
        print("\n✓ All artifact contract tests passed")
        return 0

    print("\n✗ Some artifact contract tests failed")
    return 1


# ---------------------------------------------------------------------------
# Runtime artifact tests (verify actual .dev/ files exist and contain markers)
# ---------------------------------------------------------------------------

def test_al_dev_ticket_contracts(repo_root: Path | None = None) -> bool:
    """Verify al-dev-ticket produces required artifacts with completion markers.

    Checks for latest .dev/*-al-dev-ticket-ticket-context.md file and validates
    it contains ticket metadata markers (TICKET_ID, STATUS, PRIORITY sections).

    Returns True if test passes, False if artifacts don't exist (acceptable in
    sessions where ticket skill hasn't run).
    """
    import glob

    # Find latest ticket context file using glob
    root = _REPO_ROOT if repo_root is None else repo_root
    ticket_files = glob.glob(str(root / ".dev" / "*-al-dev-ticket-ticket-context.md"))

    if not ticket_files:
        # Artifact doesn't exist yet; acceptable for sessions where skill hasn't run
        return True

    latest_file = max(ticket_files, key=lambda p: Path(p).stat().st_mtime)

    try:
        content = Path(latest_file).read_text(encoding="utf-8")
        # Check for metadata markers: ticket ID, status, or priority section
        has_metadata = any(marker in content for marker in [
            "TICKET_ID", "STATUS", "PRIORITY", "**Ticket ID**", "**Status**", "**Priority**"
        ])

        if not has_metadata:
            print(f"⚠ {latest_file}: Missing ticket metadata markers (TICKET_ID, STATUS, PRIORITY)")
            return False

        return True
    except OSError as e:
        print(f"⚠ {latest_file}: Cannot read file ({e})")
        return False


def test_al_dev_interview_contracts(repo_root: Path | None = None) -> bool:
    """Verify al-dev-interview produces required artifacts with completion markers.

    Checks for latest .dev/*-al-dev-interview-requirements.md file and validates
    it contains REQ tokens (REQ-NNN format) indicating formal requirements extracted.

    Returns True if test passes, False if artifacts don't exist (acceptable in
    sessions where interview skill hasn't run).
    """
    import glob

    # Find latest interview requirements file
    root = _REPO_ROOT if repo_root is None else repo_root
    req_files = glob.glob(str(root / ".dev" / "*-al-dev-interview-requirements.md"))

    if not req_files:
        # Artifact doesn't exist yet; acceptable for sessions where skill hasn't run
        return True

    latest_file = max(req_files, key=lambda p: Path(p).stat().st_mtime)

    try:
        content = Path(latest_file).read_text(encoding="utf-8")
        # Check for REQ tokens (formal requirement markers)
        has_req_tokens = "REQ:" in content or "REQ-" in content or "ACC:" in content

        if not has_req_tokens:
            print(f"⚠ {latest_file}: Missing REQ/ACC tokens (formal requirements)")
            return False

        return True
    except OSError as e:
        print(f"⚠ {latest_file}: Cannot read file ({e})")
        return False


def test_al_dev_explore_contracts(repo_root: Path | None = None) -> bool:
    """Verify al-dev-explore produces required artifacts with completion markers.

    Checks for latest .dev/*-al-dev-explore-findings.md file and validates it
    contains structured sections (ANSWER, FILES, SNIPPETS) indicating complete
    exploration findings.

    Returns True if test passes, False if artifacts don't exist (acceptable in
    sessions where explore skill hasn't run).
    """
    import glob

    # Find latest exploration findings file
    root = _REPO_ROOT if repo_root is None else repo_root
    findings_files = glob.glob(str(root / ".dev" / "*-al-dev-explore-findings.md"))

    if not findings_files:
        # Artifact doesn't exist yet; acceptable for sessions where skill hasn't run
        return True

    latest_file = max(findings_files, key=lambda p: Path(p).stat().st_mtime)

    try:
        content = Path(latest_file).read_text(encoding="utf-8")
        # Check for structured section markers
        has_sections = any(section in content for section in [
            "## ANSWER", "## FILES", "## SNIPPETS", "## Findings"
        ])

        if not has_sections:
            print(f"⚠ {latest_file}: Missing structured sections (ANSWER/FILES/SNIPPETS)")
            return False

        return True
    except OSError as e:
        print(f"⚠ {latest_file}: Cannot read file ({e})")
        return False


def test_al_dev_investigate_contracts(repo_root: Path | None = None) -> bool:
    """Verify al-dev-investigate produces required artifacts with completion markers.

    Checks for latest .dev/*-al-dev-investigate-findings.md and validates it
    contains a Root Cause section and at least one hypothesis verdict.

    Returns True if test passes, False if artifacts don't exist (acceptable in
    sessions where investigate skill hasn't run).
    """
    import glob

    root = _REPO_ROOT if repo_root is None else repo_root
    findings_files = glob.glob(str(root / ".dev" / "*-al-dev-investigate-findings.md"))

    if not findings_files:
        return True

    latest_file = max(findings_files, key=lambda p: Path(p).stat().st_mtime)

    try:
        content = Path(latest_file).read_text(encoding="utf-8")
        has_markers = any(marker in content for marker in [
            "Root Cause", "Hypothes", "VERDICT", "CONFIRMED", "REJECTED"
        ])

        if not has_markers:
            print(f"⚠ {latest_file}: Missing investigation markers (Root Cause/Hypotheses/VERDICT)")
            return False

        return True
    except OSError as e:
        print(f"⚠ {latest_file}: Cannot read file ({e})")
        return False


def test_al_dev_handoff_contracts(repo_root: Path | None = None) -> bool:
    """Verify al-dev-handoff produces a handoff prompt with required sections.

    Checks for latest .dev/*-al-dev-handoff-handoff-prompt.md and validates it
    contains a Context section and a Suggested first command section.

    Returns True if test passes, False if artifacts don't exist (acceptable in
    sessions where handoff skill hasn't run).
    """
    import glob

    root = _REPO_ROOT if repo_root is None else repo_root
    prompt_files = glob.glob(str(root / ".dev" / "*-al-dev-handoff-handoff-prompt.md"))

    if not prompt_files:
        return True

    latest_file = max(prompt_files, key=lambda p: Path(p).stat().st_mtime)

    try:
        content = Path(latest_file).read_text(encoding="utf-8")
        has_sections = any(section in content for section in [
            "## Context", "Context files available", "Suggested first command", "Handoff Prompt"
        ])

        if not has_sections:
            print(f"⚠ {latest_file}: Missing handoff sections (Context/Context files available/Suggested first command)")
            return False

        return True
    except OSError as e:
        print(f"⚠ {latest_file}: Cannot read file ({e})")
        return False


def run_artifact_tests(repo_root: Path | None = None) -> bool:
    """Run all runtime artifact contract tests.

    Returns True if all tests pass (or skip due to missing artifacts).
    Returns False if any test fails.
    """
    tests = [
        ("al-dev-ticket", test_al_dev_ticket_contracts),
        ("al-dev-interview", test_al_dev_interview_contracts),
        ("al-dev-explore", test_al_dev_explore_contracts),
        ("al-dev-investigate", test_al_dev_investigate_contracts),
        ("al-dev-handoff", test_al_dev_handoff_contracts),
    ]

    results = []
    for skill_name, test_func in tests:
        try:
            passed = test_func(repo_root)
            results.append((skill_name, passed))
            status = "✓" if passed else "✗"
            print(f"{status} {skill_name}")
        except Exception as e:
            print(f"⚠ {skill_name}: Unexpected error ({e})")
            results.append((skill_name, False))

    return all(passed for _, passed in results)

if __name__ == "__main__":
    raise SystemExit(main())
