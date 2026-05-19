# Skill-Test Harness — Phase A Design

**Date:** 2026-05-17
**Status:** Ready for plan authoring
**Scope:** Cross-repo. Data + schema in `al-dev-shared` (harness-agnostic); orchestrator + `/skill-test` skill in `claude-configs` (Claude Code-specific). Phase A = findings-only (no auto-fix loop).

## Goal

Build a maintenance harness that exercises every skill in
`profile-al-dev-shared` against representative scenarios, detects four
classes of failure, and writes a coverage report, findings report, and
draft fix plan to `.dev/`. The fix plan is consumable by
`superpowers:writing-plans` without manual reformatting.

Phase A explicitly STOPS at writing the draft fix plan. The autonomous
"execute fix + re-test until green" loop is deferred to a separate
Phase B spec.

## Non-Goals

- No auto-execution of fix plans (Phase B).
- No regression-gate logic (Phase B).
- No telemetry on skill invocations across user sessions.
- No coverage for the four superpowers skills, claude-api, init,
  review, security-review, obsidian, update-config, etc. — harness
  targets `profile-al-dev-shared` skills only.
- No bootstrap-testing of the harness itself.

## Placement Decision

The harness is split across two repos to preserve the harness-agnostic
contract of `al-dev-shared`. The orchestrator dispatches real
subagents — an inherently harness-specific act — so it lives in
`claude-configs`. The per-skill test data is pure declarative content
(user prompts, expected artifact globs) — harness-agnostic — so it
lives next to each skill in `al-dev-shared`. A future
`copilot-configs` orchestrator will consume the same shared data.

### Repo split

**`al-dev-shared/profile-al-dev-shared/`** — harness-agnostic
(subject to `check-alignment.py`):

```
profile-al-dev-shared/
  skills/
    al-dev-plan/
      SKILL.md
      tests/
        scenarios.yaml           # per-skill test data
        expected-artifacts.txt   # union of expected-artifact globs
    ...
  knowledge/
    skill-test-format.md         # scenarios.yaml + trigger-corpus.yaml schema
    skill-test-trigger-corpus.yaml  # shared NL → expected-skill mappings
```

**`claude-configs/profile-claude-al-dev/skills/skill-test/`** —
Claude Code-specific:

```
profile-claude-al-dev/
  skills/
    skill-test/
      SKILL.md              # /skill-test skill body (Claude Code dispatch)
      run.py                # orchestrator (uses Claude Code Agent tool)
      gen_scenarios.py      # LLM-drafts scenarios.yaml for a skill
      detectors/
        forbidden.py        # Path 4 regex scanner (pure Python)
        validators.py       # Path 3 validator runner (pure Python)
```

**`copilot-configs/`** — out of scope for Phase A. Parity
implementation is a follow-up effort that mirrors the
`claude-configs/profile-claude-al-dev/skills/skill-test/` directory
under `copilot-configs/profile-copilot-al-dev/skills/skill-test/`
with Copilot-specific dispatch.

### Cross-repo dependency

The Claude Code orchestrator reads test data from
`al-dev-shared` via the `AL_DEV_SHARED_PLUGIN_ROOT` concept already
defined in `harness-concepts.md` and resolved by each harness profile:

- Per-skill scenarios: `$AL_DEV_SHARED_PLUGIN_ROOT/skills/<skill>/tests/scenarios.yaml`
- Trigger corpus: `$AL_DEV_SHARED_PLUGIN_ROOT/knowledge/skill-test-trigger-corpus.yaml`
- Schema reference: `$AL_DEV_SHARED_PLUGIN_ROOT/knowledge/skill-test-format.md`

The detectors that operate on artifacts in `.dev/` (Paths 3 and 4)
run inside the orchestrator process; they do not need to be installed
into `al-dev-shared`.

### Why not project-local under `al-dev-shared/.claude/skills/`?

The pattern used by `/review-plugin-map` and `/analyze-plugin-design`
(both in `al-dev-shared/.claude/skills/`) is acceptable for purely
local maintenance tooling. The skill-test harness is heavier: it
ships with a Python orchestrator, detectors, and a per-skill data
contract that other harnesses (Copilot) will need to consume.
Placing the orchestrator in `claude-configs` aligns it with the
existing rule that harness-specific implementations live in the
harness profile repos and keeps the long-term Copilot parity path
clean.

## Phase A Deliverables

Files land in two repos. Commits in each repo are independent.

### In `al-dev-shared` (harness-agnostic)

1. `profile-al-dev-shared/knowledge/skill-test-format.md` — schema
   reference for `scenarios.yaml` and `skill-test-trigger-corpus.yaml`.
2. `profile-al-dev-shared/knowledge/skill-test-trigger-corpus.yaml` —
   starter set of ~24 NL prompts covering the 5 priority skills.
3. Populated `tests/scenarios.yaml` and `tests/expected-artifacts.txt`
   under each of the five blast-radius skills (`al-dev-plan`,
   `al-dev-develop`, `al-dev-autonomous`, `al-dev-fix`,
   `al-dev-commit`).

These additions must pass `check-alignment.py` — no harness-specific
tokens anywhere.

### In `claude-configs` (Claude Code-specific)

4. `profile-claude-al-dev/skills/skill-test/SKILL.md` — `/skill-test`
   skill body.
5. `profile-claude-al-dev/skills/skill-test/run.py` — orchestrator
   that dispatches Claude Code Agent subagents.
6. `profile-claude-al-dev/skills/skill-test/gen_scenarios.py` — LLM
   draft helper.
7. `profile-claude-al-dev/skills/skill-test/detectors/forbidden.py`,
   `detectors/validators.py` — Path 3/4 detectors.

### In whichever repo the run happens

8. One committed test run: coverage report, findings, fix plan in
   `.dev/`. The run is performed from the user's working directory;
   the `.dev/` directory is the working directory's `.dev/`.

## Architecture

### Detection paths

Four detection paths, run in this order per run:

#### Path 1 — Skill execution test (per scenario)

For each `scenario` in each targeted skill's `tests/scenarios.yaml`:

```python
Agent({
  subagent_type: "general-purpose",
  isolation:     "worktree",
  prompt:        <SKILL.md body, frontmatter stripped>
              + "\n---\nUser request: " + scenario.user_prompt
})
```

On return:

- If a worktree path is returned, harness reads files from there and
  matches against scenario's `expected_artifacts` glob list.
- Greps the agent's final message for error markers (`Error:`,
  `cannot`, refusal patterns from a small allowlist).
- If `must_invoke_agent` is set, harness greps the transcript for an
  Agent tool call naming that subagent type.

**Fail conditions:**
- Missing expected artifact.
- Unexpected artifact present when `expected_artifacts: []`.
- Error marker in final message.
- `must_invoke_agent` set but no matching Agent dispatch found.
- `must_not_invoke_agent` set and a matching Agent dispatch found.

#### Path 2 — Description-trigger test (per trigger-corpus entry)

Tests whether skill `description:` fields are good enough that Claude
routes the right skill for a natural-language prompt:

```python
Agent({
  subagent_type: "general-purpose",
  prompt: "Available skills:\n"
        + <every active skill's name + description, no bodies>
        + "\nUser said: " + trigger_prompt
        + "\nWhich single skill should be invoked?"
          " Output JUST the skill name on one line, or NONE."
})
```

**Fail conditions:**
- Wrong skill named.
- `NONE` returned when an expected skill exists.
- Output unparseable.

#### Path 3 — Output validity

Run existing Python validators against artifacts produced in Path 1:

- `validate-plan.py` against `*-al-dev-plan-solution-plan.md`.
- `validate-code-review.py` against `*-al-dev-develop-code-review.md`.
- `validate-requirements.py` against
  `*-al-dev-interview-*.md`.
- `check-alignment.py` if the run modified any active skill body
  (defence against the harness silently breaking alignment).

**Fail condition:** non-zero exit from any validator.

#### Path 4 — Forbidden-pattern scan

Regex-scan all artifacts produced in Path 1 for the patterns specified
in `CLAUDE.md` Plan Task Verification Standard:

- `\[\d{4}-\d{2}-\d{2}\]` — unrendered date templates.
- Literal `YYYY-MM-DD` (case-sensitive) — placeholder leakage.
- `TODO`, `TBD` (case-insensitive, word-boundary).
- `Co-Authored-By` inside fenced code blocks (allowed in commit
  trailers only — scanner walks AST of markdown to distinguish).
- Line-comment prefixes `claude:` / `copilot:` (`//`, `#`, `--` prefix
  forms; AL is `//`).

**Fail condition:** any hit. Allowlist file
`profile-claude-al-dev/skills/skill-test/forbidden-allowlist.yaml`
(in `claude-configs`) covers documented exceptions (e.g., a
`scenarios.yaml` glob like `.dev/*-al-dev-plan-solution-plan.md` is
not a forbidden-pattern hit because the literal text is `*`, not
the date-placeholder string).

### Orchestration

`run.py` flow:

1. Parse args (`--skills`, `--max-scenarios`, `--paths`,
   `--skip-gen`).
2. For each targeted skill without a `scenarios.yaml`, invoke
   `gen_scenarios.py` (LLM draft, status: `draft`). Skip if
   `--skip-gen` set.
3. Dispatch all Path 1 invocations in parallel (one Agent call per
   scenario). Cap by `--max-scenarios` (default 15).
4. Dispatch all Path 2 invocations in parallel (one Agent call per
   trigger-corpus entry).
5. Wait for all subagents. Collect transcripts, artifact paths, agent
   tool-call traces.
6. Run Path 3 + Path 4 detectors on collected artifacts (local Python,
   sequential, fast).
7. Write coverage report, findings, and fix-plan to `.dev/`.

### Cost guards

- `--max-scenarios N` caps total Path 1 dispatches (default 15).
- `--skills foo,bar` targets a subset.
- `--paths 1,3,4` selects which detection paths to run (handy for
  iterating on Path 4 regex without re-spending Path 1 budget).

## File Formats

### `tests/scenarios.yaml`

```yaml
skill: al-dev-plan
scenarios:
  - id: plan-new-feature
    status: golden            # golden | draft
    user_prompt: "Design how I'd add a tax-exemption certificate validation feature to the Sales Order workflow."
    expected_artifacts:
      - ".dev/*-al-dev-plan-solution-plan.md"
    must_invoke_agent: al-dev-shared:al-dev-solution-architect
    notes: "Common entry path; should produce a solution plan with 2-3 architect options."

  - id: plan-trivial-routing
    status: golden
    user_prompt: "Plan a one-line fix to change a Caption from 'Cust' to 'Customer' on the Sales Header."
    expected_artifacts: []
    must_not_invoke_agent: al-dev-shared:al-dev-solution-architect
    notes: "Tests the TRIVIAL classification in workflow-routing.md."
```

Schema fields:

| Field | Type | Required | Notes |
|---|---|---|---|
| `skill` | string | yes | Must match parent directory name. |
| `scenarios` | list | yes | 2-3 entries per skill in v1. |
| `scenarios[].id` | string | yes | Kebab-case, unique per skill. |
| `scenarios[].status` | enum | yes | `golden` or `draft`. |
| `scenarios[].user_prompt` | string | yes | The natural-language input. |
| `scenarios[].expected_artifacts` | list[glob] | yes | Empty list = explicit "no artifacts". |
| `scenarios[].must_invoke_agent` | string | no | Fully-qualified agent name (`<namespace>:<agent-name>`) the harness expects to find dispatched in the transcript. The orchestrator translates this to the harness-specific tool-call shape when grepping. |
| `scenarios[].must_not_invoke_agent` | string | no | Fully-qualified agent name that must NOT appear in the transcript. |
| `scenarios[].notes` | string | no | Free-text rationale. |

### `tests/expected-artifacts.txt`

Plain text. One glob per line. Union of all per-scenario
`expected_artifacts` for the skill. Used by the coverage report to
display claimed outputs per skill. Generated by `run.py`; not
hand-edited.

### `knowledge/skill-test-trigger-corpus.yaml` (in al-dev-shared)

```yaml
corpus:
  - prompt: "design how I'd build a sales-tax exemption feature"
    expected: al-dev-plan
  - prompt: "implement the plan we just wrote"
    expected: al-dev-develop
  - prompt: "squash these commits before pushing"
    expected: al-dev-commit
```

Starter size: 24 entries covering the 5 priority skills (~5
paraphrases each). Growing over time as new mis-routes are discovered.

### Coverage report

Path: `.dev/<date>-skill-test-coverage.md`, where `<date>` is the
current date in ISO format.

```markdown
# Skill-Test Coverage — <run date in ISO format>

| Skill | Scenarios | Golden | Draft | Last run | Pass | Fail |
|---|---|---|---|---|---|---|
| al-dev-plan | 3 | 3 | 0 | <run date> | 2 | 1 |
| ... |

## Description-trigger results
Corpus size: 24 prompts. Correct routing: 21/24 (87.5%).
3 mis-routes — see findings.
```

The date column shows `never` for skills without a scenarios.yaml.

### Findings report

Path: `.dev/<run date>-skill-test-findings.md`.

One section per failure, tagged by detection path:

```markdown
## FAIL · al-dev-plan · plan-trivial-routing · [Path 1: execution]

**Scenario:** Plan a one-line fix to change a Caption …
**Expected:** No solution plan written (TRIVIAL routing).
**Got:** Subagent wrote .dev/<date>-al-dev-plan-solution-plan.md.
**Hypothesis:** Skill's TRIVIAL detection in Phase 0 missing for
caption-only changes.
**Pointer:** profile-al-dev-shared/skills/al-dev-plan/SKILL.md
(Phase 0 routing block)
**Severity:** medium — over-planning trivial work, no data loss.
```

Failures are grouped by skill, then by detection path within skill.
Severity values: `high` (blocks user work), `medium` (degraded
quality, no data loss), `low` (cosmetic / advisory).

### Fix-plan draft

Path: `.dev/<run date>-skill-test-fix-plan.md`.

Pre-structured for `superpowers:writing-plans` to pick up as a spec
input:

```markdown
# Skill-Test Fix Plan Draft — <run date>

Findings file: .dev/<run date>-skill-test-findings.md
Total failures: 4 (severity: 2 medium, 2 low)

## Proposed fixes

### Fix 1 — al-dev-plan TRIVIAL detection
- **Findings:** plan-trivial-routing
- **Target file:** profile-al-dev-shared/skills/al-dev-plan/SKILL.md
- **Change sketch:** Add caption-only / single-property edits to
  TRIVIAL examples in Phase 0.
- **Verification:** Re-run scenario plan-trivial-routing; expect zero
  artifacts.

## Handoff
Run /superpowers:writing-plans with this file as the spec input.
Do NOT auto-execute — Phase B (auto-fix loop) is not yet implemented.
```

## Priority Skills (Phase A Scope)

The five skills receiving curated golden scenarios in this spec are
the highest-blast-radius skills in the plugin:

| Skill | Why blast radius is high |
|---|---|
| `al-dev-plan` | Writes solution plans consumed by other skills. |
| `al-dev-develop` | Writes AL source files; multi-agent pipeline. |
| `al-dev-autonomous` | Autonomous AL implementation + compile loop. |
| `al-dev-fix` | Modifies source files in fast-iteration mode. |
| `al-dev-commit` | Commits to git; can introduce malformed commits. |

The remaining ~13 active skills (`al-dev-align`, `al-dev-document`,
`al-dev-explore`, `al-dev-help`, `al-dev-interview`,
`al-dev-investigate`, `al-dev-lint`, `al-dev-perf`,
`al-dev-release-notes`, `al-dev-support`, `al-dev-ticket`,
`commit-learn`, `al-dev-handoff`) get LLM-drafted scenarios on first
`/skill-test` run but no curated golden scenarios in this spec.

## Phase A Success Criteria

1. `/skill-test` runs cleanly against the 5 blast-radius skills in
   under 10 min wall-clock on a typical workstation.
2. Coverage report, findings, and fix-plan are committed to `.dev/`.
3. The fix plan is parseable as a spec input by
   `/superpowers:writing-plans` without manual reformatting.
4. The harness runs `check-alignment.py` defensively whenever it has
   reason to believe an `al-dev-shared` skill body changed during a
   run.
5. The al-dev-shared deliverables (items 1–3 above)
   pass `check-alignment.py --mode enforce` with exit 0 — no
   harness-specific tokens in any `scenarios.yaml`,
   `expected-artifacts.txt`, `skill-test-format.md`, or
   `skill-test-trigger-corpus.yaml`.
6. The claude-configs deliverables (items 4–7 above) reference
   `al-dev-shared` files exclusively via `AL_DEV_SHARED_PLUGIN_ROOT`
   — never via hardcoded absolute paths.

## Risks & Mitigations

| Risk | Mitigation |
|---|---|
| Cost: each full run is ~16 Agent dispatches. | `--max-scenarios`, `--skills`, `--paths` flags scope runs. Coverage report is incremental. |
| Subagent transcripts may not contain reliable error markers. | Conservative: a missing artifact is the primary signal; transcript greps are secondary. |
| Description-trigger test is judged by an LLM — non-deterministic. | Phrase the routing prompt to demand a single skill name only. Repeat ambiguous prompts up to 3x; majority wins. |
| Worktree isolation may not persist artifact paths if a skill writes outside the worktree. | Document in skill-test README: skills under test must write to relative paths only. |
| Forbidden-pattern scanner false positives on legitimate uses. | `forbidden-allowlist.yaml` for documented exceptions; default deny. |

## Out of Scope (Phase B)

Not part of this spec. Listed for context:

- Autonomous fix-plan execution via `subagent-driven-development`.
- Re-test loop with iteration cap.
- Regression gate: re-run all previously-passing scenarios after a
  fix is applied; rollback on regression.
- CI integration (GitHub Actions, scheduled runs).

## Open Questions

None at spec time. Surface during plan authoring or implementation.
