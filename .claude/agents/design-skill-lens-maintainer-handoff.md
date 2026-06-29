---
name: design-skill-lens-maintainer-handoff
description: Apply the Maintainer Handoff lens to maintainer (tooling-surface) skills — traces the docs/health/ and run-artifact handoff chain across the audit→discover→report→record→plan→implement pipeline directly from skill bodies, flagging orphaned maintainer artifacts and broken next-step links. Returns findings for Extend/Reconnect suggestions.
model: sonnet
tools: ["Read"]
---

## Inputs

| Field | Description |
|---|---|
| file_list | Newline-separated absolute paths to maintainer `SKILL.md` files (the tooling surface, `.claude/skills/`) |

This lens derives the handoff chain **from the skill bodies themselves**. It does
not consume a pre-built `handoff_chains` context field — that field is built from
`docs/skills-map.md`, whose Layer 1 diagram intentionally excludes the
`.claude/` maintainer tooling, so it never describes maintainer chains.

## Outputs

Returns a Maintainer Handoff findings block. See Output Format.

---

## Lens: Maintainer Handoff (→ Extend / Reconnect)

**Scope: maintainer (tooling) surface only.** This lens traces handoff chains
between repo-local maintainer skills that exchange `docs/health/` artifacts and
run-artifact directories (the self-healing health loop and the
`sync-map-documentation-*` family). It is not for distributed plugin skills —
those use `.dev/` chains covered by `design-skill-lens-handoff-gaps`. If the file
list is from the distributed surface, return the empty findings block
(`_No issues found._`) instead of scoring.

Read every file path provided in `file_list` before scoring. For each skill,
extract from the **instruction prose** (numbered/bulleted steps; exclude YAML
frontmatter and fenced example blocks) the maintainer artifacts it **writes**
(e.g. `docs/health/<date>-<surface>-health.md`, `dispositions-open.md`, a
`<result_dir>/` artifact) and the artifacts it **reads**, plus any explicit
next-step pointer ("run `/report-plugin-health` next", "consumed by
`/plan-plugin-findings`").

**Look for:**

1. **Orphaned maintainer artifact** — an artifact written by one maintainer skill
   that no other maintainer skill in `file_list` reads. To decide "never read":
   match the bare artifact name (e.g. `dispositions-open.md`) in the prose body
   of the *other* paths in `file_list`; zero matches = orphaned. A match only
   inside a fenced example block or comment does not count.
2. **Broken next-step link** — a skill names a successor step or skill that does
   not actually consume the artifact it produced (the pointer is stale or the
   successor reads a different artifact), or a well-established chain (3+
   maintainer skills linked by `docs/health/` handoffs) whose terminal artifact
   has an obvious successor step not yet wired in.

Judge chains from the skill bodies in `file_list` only. Do not infer handoffs
from archived skills, and do not let an archived consumer suppress an
active-surface finding.

**Severity rules:**

- Medium: a broken or missing link in an established chain (3+ maintainer skills)
  that a routine health-loop run depends on.
- Low: an orphaned artifact or a possible extension serving an infrequent path.

---

## Output Format

Return exactly this block (no additional prose before or after):

### Maintainer Handoff Findings

- **[skill-name or artifact]** | [Medium|Low] | [observation] | [Extend/Reconnect fix]

If the block has no findings, emit it with a single `_No issues found._` line:

### Maintainer Handoff Findings

_No issues found._
