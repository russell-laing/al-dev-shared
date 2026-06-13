---
name: research-harness-improvements
description: Use when researching current AI skills, agents, prompts, MCP/tooling, memory, context management, evaluation, or other harness components to identify evidence-backed improvements for this repository.
---

# Research Harness Improvements

## Overview

Research external AI-harness practices and compare them with the live repository
before recommending further assessment. Produce a source-backed briefing only;
do not edit shared plugin files.

## Use When

- The user asks to research skills, agents, prompts, MCP, hooks, memory,
  context management, evaluations, orchestration, or harness configuration.
- The goal is to improve AI harness files in this repository.
- Current vendor capabilities or ecosystem practices may have changed.

Use `review-improvement-reports` after this skill when the user wants candidate
findings classified as shared-plugin changes. Use `maintain-shared-knowledge`
only after a reviewed change has been approved.

## Output

Write one briefing to:

- `.dev/YYYY-MM-DD-harness-improvement-research.md`

If that path already exists, add a short topic suffix:

- `.dev/YYYY-MM-DD-harness-improvement-research-agent-evaluation.md`

Never overwrite an unrelated same-day briefing.

Create the output directory before writing a briefing or progress checkpoint:

```bash
mkdir -p .dev
```

## Scope Contract

At the start, state:

- the research question
- the harness components in scope
- the harnesses or ecosystems being compared
- the recency window, when relevant
- explicit exclusions

Keep the scope bounded to the user's question. Do not turn a request about one
component into a general audit of every harness surface.

## Workflow

### Startup And Resume

Before starting or resuming:

```bash
mkdir -p .dev
if [ -f .dev/progress.md ]; then
  cat .dev/progress.md
fi
```

If `.dev/progress.md` exists, display its contents and ask exactly:

```text
Resume from checkpoint? (yes / restart)
```

Do not begin later phase work until the user answers.

- `yes` — continue from the recorded next step. Restore
  `HARNESS_RESEARCH_TMP` from `.dev/progress.md`, then validate it before reuse.
- `restart` — remove or overwrite `.dev/progress.md`, ignore prior dated
  research progress files unless the user explicitly reuses one, and write a
  fresh checkpoint before continuing to Phase 1.

For `yes`, trust the recorded temp directory only when it is inside the
workflow-owned namespace and all baseline files still exist:

```bash
export HARNESS_RESEARCH_TMP="<recorded-temp-directory>"
TMP_ROOT=${TMPDIR:-/tmp}
TMP_ROOT=${TMP_ROOT%/}
case "$HARNESS_RESEARCH_TMP" in
  "$TMP_ROOT"/harness-research.*) ;;
  *) false ;;
esac
test -d "$HARNESS_RESEARCH_TMP"
test -f "$HARNESS_RESEARCH_TMP/protected-before.txt"
test -f "$HARNESS_RESEARCH_TMP/index-before.txt"
test -f "$HARNESS_RESEARCH_TMP/status-before.txt"
```

If any namespace, directory, or baseline-file check fails, create a fresh
directory with:

```bash
export HARNESS_RESEARCH_TMP
TMP_ROOT=${TMPDIR:-/tmp}
TMP_ROOT=${TMP_ROOT%/}
HARNESS_RESEARCH_TMP=$(mktemp -d "$TMP_ROOT/harness-research.XXXXXX")
```

Rebuild the Phase 1 baseline manifests there before continuing, and record the
rebuild and new path in `.dev/progress.md`.

Use `.dev/progress.md` as the authoritative resume state. The dated
`.dev/YYYY-MM-DD-harness-improvement-research-progress*.md` file is a durable
narrative only and does not override `.dev/progress.md`.

### Phase 1: Establish The Live Repo Baseline

Before external research:

1. Record authoritative path and Git index manifests for the protected
   surfaces, plus human-readable Git status evidence:

   ```bash
   export HARNESS_RESEARCH_TMP
   TMP_ROOT=${TMPDIR:-/tmp}
   TMP_ROOT=${TMP_ROOT%/}
   HARNESS_RESEARCH_TMP=$(mktemp -d "$TMP_ROOT/harness-research.XXXXXX")
   python3 - <<'PY' > "$HARNESS_RESEARCH_TMP/protected-before.txt"
   from hashlib import sha256
   from pathlib import Path

   roots = [
       Path("AGENTS.md"),
       Path("CODEX.md"),
       Path("profile-al-dev-shared"),
       Path(".codex/skills"),
       Path(".claude/skills"),
       Path(".claude/agents"),
       Path(".claude/hooks"),
       Path(".claude/knowledge"),
   ]
   excluded = Path(".codex/skills/research-harness-improvements")
   paths = []
   for root in roots:
       candidates = [root] if not root.is_dir() else [root, *root.rglob("*")]
       paths.extend(
           path for path in candidates
           if path != excluded and excluded not in path.parents
       )
   for path in sorted(paths, key=lambda item: item.as_posix()):
       label = "." if path == Path("profile-al-dev-shared") else path.as_posix()
       mode = path.lstat().st_mode & 0o7777
       if path.is_symlink():
           value = f"symlink\t{path.readlink()}"
       elif path.is_dir():
           value = "directory"
       elif path.is_file():
           value = f"file\t{sha256(path.read_bytes()).hexdigest()}"
       else:
           value = "other"
       print(f"{label}\t{mode:o}\t{value}")
   PY
   git ls-files -s -- \
     AGENTS.md CODEX.md profile-al-dev-shared .codex/skills \
     .claude/skills .claude/agents .claude/hooks .claude/knowledge \
     | awk -F '\t' \
       '$2 !~ /^\.codex\/skills\/research-harness-improvements\//' \
     > "$HARNESS_RESEARCH_TMP/index-before.txt"
   git status --short -- \
     AGENTS.md CODEX.md profile-al-dev-shared .codex/skills \
     .claude/skills .claude/agents .claude/hooks .claude/knowledge \
     | awk \
       'index($0, ".codex/skills/research-harness-improvements/") == 0' \
     > "$HARNESS_RESEARCH_TMP/status-before.txt"
   cat "$HARNESS_RESEARCH_TMP/status-before.txt"
   ```

   The path manifest covers every present path, type, mode, regular-file bytes,
   symlink target, and empty directory under `profile-al-dev-shared` and
   existing `.codex/skills`, `.claude/skills`, `.claude/agents`,
   `.claude/hooks`, and `.claude/knowledge`, plus `AGENTS.md` and `CODEX.md`.
   These repo-local maintainer surfaces are read-only during the run. The
   current skill directory is excluded from the repo-local-skill invariant. The
   index manifest covers staged blob, mode, and path state. Git status is
   supporting human-readable evidence. Preserve pre-existing changes; do not
   revert or modify them.
2. Read `AGENTS.md` and `CODEX.md`.
3. Search current repo-local skills and agents across `.codex/` and `.claude/`,
   plus shared skills, agents, knowledge, tests, generators, and validators for
   the requested concepts.
4. Read:
   - `profile-al-dev-shared/knowledge/harness-concepts.md`
   - `profile-al-dev-shared/knowledge/agent-tool-projection-policy.md`
5. Record existing coverage as `complete`, `partial`, or `none found`.

Start with:

```bash
rg -n -i "<topic terms>" \
  .codex/skills \
  .claude/skills \
  .claude/agents \
  .claude/hooks \
  .claude/knowledge \
  profile-al-dev-shared/skills \
  profile-al-dev-shared/agents \
  profile-al-dev-shared/knowledge \
  scripts
```

Do not call an external idea new until this search has ruled out equivalent
current behavior.

After Phase 1, overwrite the authoritative checkpoint and refresh the durable
narrative:

- `.dev/progress.md`
- `.dev/YYYY-MM-DD-harness-improvement-research-progress.md`

Run `mkdir -p .dev` before writing the checkpoint.
Keep both files short and aligned. Record the scope, completed phases, current
state, exact next step, `HARNESS_RESEARCH_TMP` path, baseline snapshot paths,
and open questions or pending decisions. Overwrite `.dev/progress.md`; do not
append. Use the same topic suffix as the briefing for the dated narrative when
needed to avoid a same-day collision.

### Phase 2: Build A Source Plan

Use sources in this order:

1. Current first-party harness documentation and release notes.
2. Primary specifications and official implementation repositories.
3. Original research papers or technical reports.
4. Maintainer-authored technical articles with reproducible evidence.
5. Aggregators, social posts, and popularity signals only for discovery.

For OpenAI, Microsoft, or other vendors with dedicated documentation tools,
prefer those tools over generic web search. For current claims, verify the
publication or update date and record the access date.

Cover at least two independent primary sources for a cross-vendor conclusion.
One source is sufficient only for a claim about that source's own product or
specification.

### Phase 3: Gather And Track Evidence

Maintain an evidence ledger while researching:

| ID | Claim | Source | Source Type | Published or Updated | Accessed | Confidence |
| --- | --- | --- | --- | --- | --- | --- |

Rules:

- Cite only sources actually opened during the current run.
- Quote sparingly; paraphrase the evidence and preserve the source URL.
- Label synthesis that is not stated directly by a source as `inference`.
- Mark unresolved conflicts between sources instead of choosing silently.
- Treat install counts, stars, rankings, and ecosystem popularity as weak
  quality signals, not proof that a pattern is correct.
- Stop after three consecutive source-access failures and report the incomplete
  areas.

After evidence gathering, overwrite `.dev/progress.md` and refresh the same
dated research progress file with the completed phases, current state, exact
next step, temp and baseline paths, and remaining open questions. Do not turn
either checkpoint into a duplicate evidence ledger or a workflow engine.

### Phase 4: Compare Findings With The Repository

For each external pattern, record:

| Pattern | External Evidence | Existing Repo Coverage | Gap | Portability |
| --- | --- | --- | --- | --- |

Use these portability values:

- `shared` — durable harness-neutral behavior may belong in
  `profile-al-dev-shared`.
- `repo-local` — useful maintainer tooling but not distributed plugin behavior.
- `harness-specific` — concrete wiring belongs in a harness-specific surface.
- `reject` — duplicate, weakly evidenced, incompatible, or unnecessary.

Keep shared capability intent separate from harness-native wiring. Never
recommend hand-editing `profile-al-dev-shared/generated/agents/`.

### Phase 5: Write The Briefing

Run `mkdir -p .dev` before writing the briefing.

Use this exact structure:

```markdown
# Harness Improvement Research

## Research Question

## Scope And Method

## Live Repository Baseline

## Evidence-Backed Findings

## Repository Comparison

## Candidate Patterns

## Rejected Or Non-Portable Patterns

## Evidence Ledger

## Gaps And Uncertainty

## Recommended Next Step
```

`Candidate Patterns` are research leads, not accepted requirements. For each
candidate state the evidence, likely repository surface, portability value, and
the concrete risk it may reduce.

The recommended next step must be exactly one of:

- no action
- gather more evidence
- run `review-improvement-reports` on this briefing
- update an already-approved implementation plan

## Guardrails

- Do not edit `AGENTS.md`, `CODEX.md`, `profile-al-dev-shared`, generated
  projections, root inventories, existing repo-local skills, or the protected
  `.claude` maintainer skills, agents, hooks, and knowledge surfaces.
- Do not install external skills, packages, plugins, or MCP servers.
- Do not convert vendor-specific setup directly into shared guidance.
- Do not treat a research paper, popular repository, or skill registry result
  as proof that this repo should adopt a pattern.
- Do not present stale memory or training knowledge as current evidence.
- Do not commit unless the user separately requests it.

## Validation

Before reporting completion:

```bash
set -euo pipefail
: "${HARNESS_RESEARCH_TMP:?Phase 1 baseline temp directory is required}"
TMP_ROOT=${TMPDIR:-/tmp}
TMP_ROOT=${TMP_ROOT%/}
case "$HARNESS_RESEARCH_TMP" in
  "$TMP_ROOT"/harness-research.*) ;;
  *) false ;;
esac
test -d "$HARNESS_RESEARCH_TMP"
test -f "$HARNESS_RESEARCH_TMP/protected-before.txt"
test -f "$HARNESS_RESEARCH_TMP/index-before.txt"
test -f "$HARNESS_RESEARCH_TMP/status-before.txt"
test -f <briefing>
rg -n "^# Harness Improvement Research$" <briefing>
rg -n "^## (Research Question|Scope And Method|Live Repository Baseline|Evidence-Backed Findings|Repository Comparison|Candidate Patterns|Rejected Or Non-Portable Patterns|Evidence Ledger|Gaps And Uncertainty|Recommended Next Step)$" <briefing>
python3 - "<briefing>" <<'PY'
from pathlib import Path
import re
import sys

expected = [
    "## Research Question",
    "## Scope And Method",
    "## Live Repository Baseline",
    "## Evidence-Backed Findings",
    "## Repository Comparison",
    "## Candidate Patterns",
    "## Rejected Or Non-Portable Patterns",
    "## Evidence Ledger",
    "## Gaps And Uncertainty",
    "## Recommended Next Step",
]
lines = Path(sys.argv[1]).read_text(encoding="utf-8").splitlines()
assert [line for line in lines if line.startswith("# ")] == [
    "# Harness Improvement Research"
]
assert not any(re.fullmatch(r"(={3,}|-{3,})", line.strip()) for line in lines)
assert [line for line in lines if line.startswith("## ")] == expected
PY
python3 - <<'PY' > "$HARNESS_RESEARCH_TMP/protected-after.txt"
from hashlib import sha256
from pathlib import Path

roots = [
    Path("AGENTS.md"),
    Path("CODEX.md"),
    Path("profile-al-dev-shared"),
    Path(".codex/skills"),
    Path(".claude/skills"),
    Path(".claude/agents"),
    Path(".claude/hooks"),
    Path(".claude/knowledge"),
]
excluded = Path(".codex/skills/research-harness-improvements")
paths = []
for root in roots:
    candidates = [root] if not root.is_dir() else [root, *root.rglob("*")]
    paths.extend(
        path for path in candidates
        if path != excluded and excluded not in path.parents
    )
for path in sorted(paths, key=lambda item: item.as_posix()):
    label = "." if path == Path("profile-al-dev-shared") else path.as_posix()
    mode = path.lstat().st_mode & 0o7777
    if path.is_symlink():
        value = f"symlink\t{path.readlink()}"
    elif path.is_dir():
        value = "directory"
    elif path.is_file():
        value = f"file\t{sha256(path.read_bytes()).hexdigest()}"
    else:
        value = "other"
    print(f"{label}\t{mode:o}\t{value}")
PY
git ls-files -s -- \
  AGENTS.md CODEX.md profile-al-dev-shared .codex/skills \
  .claude/skills .claude/agents .claude/hooks .claude/knowledge \
  | awk -F '\t' \
    '$2 !~ /^\.codex\/skills\/research-harness-improvements\//' \
  > "$HARNESS_RESEARCH_TMP/index-after.txt"
git status --short -- \
  AGENTS.md CODEX.md profile-al-dev-shared .codex/skills \
  .claude/skills .claude/agents .claude/hooks .claude/knowledge \
  | awk \
    'index($0, ".codex/skills/research-harness-improvements/") == 0' \
  > "$HARNESS_RESEARCH_TMP/status-after.txt"
cat "$HARNESS_RESEARCH_TMP/status-after.txt"
cmp -s \
  "$HARNESS_RESEARCH_TMP/protected-before.txt" \
  "$HARNESS_RESEARCH_TMP/protected-after.txt"
cmp -s \
  "$HARNESS_RESEARCH_TMP/index-before.txt" \
  "$HARNESS_RESEARCH_TMP/index-after.txt"
cmp -s \
  "$HARNESS_RESEARCH_TMP/status-before.txt" \
  "$HARNESS_RESEARCH_TMP/status-after.txt"
git status --short
```

The before and after path, index, and status manifests must all match exactly.
The path manifest proves equality for every protected present path, type, mode,
regular-file byte content, symlink target, and empty directory, including
untracked paths. The index manifest proves staged blob, mode, and path equality.
Status remains human-readable evidence. Any pre-existing changes must remain
untouched.

Confirm that:

- every substantive current claim has a source in the evidence ledger
- every candidate is mapped to existing repo coverage
- inference is labeled
- protected shared, root-instruction, and existing repo-local-skill surfaces
  match their Phase 1 baselines
