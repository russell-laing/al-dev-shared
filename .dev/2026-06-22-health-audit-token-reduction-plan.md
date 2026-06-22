# Reduce token usage in the plugin health-audit sweep

## Context

`/audit-plugin-health` feels token-heavy even when filtered by `--surface` and
`--dimension`. The router itself spawns nothing — the cost lives in
`/discover-plugin-health`, and the dominant driver is **redundant full-corpus
reads multiplied across lenses**:

- A full audit dispatches **22 lens agents per surface (44 for `both`)**.
- `--surface`/`--dimension` filtering genuinely cuts the lens *count* (e.g.
  `--surface plugin --dimension quality` → 10 lenses), but **each remaining lens
  still opens every file in the surface in full**. With ~40 agent files + ~24
  skill files, even a 10-lens quality run reads the agent corpus 5× and the skill
  corpus 5×. That redundancy is why filtered runs still feel heavy.
- The Phase 2 run manifest already de-duplicates the *context mappings*, but
  **not the file bodies** — lenses read those directly.
- Discovery **always re-globs the entire corpus** every run; there is no
  changed-files scoping.

Two highest-leverage, lowest-risk levers address this: (A) add `--since <ref>`
git-diff scoping so per-file lenses read only changed files, and (B) convert the
4 fully/mostly-deterministic lenses to a single Python pass that emits the same
findings artifacts at zero LLM cost. One-lens-one-agent is preserved for every
remaining LLM lens. Expected outcome: an order-of-magnitude reduction on
incremental re-runs via scoping (A), plus a flat per-run reduction of 4 LLM
dispatches and 4 full-corpus passes (B).

This is al-dev-shared's own maintainer tooling, so it is planned/executed inline
and kept light (no `/al-dev-plan`).

## Sequencing — two independent changes, shipped in order

The two levers have very different blast radius, so they ship as **two separate
atomic commits**, not one combined pass:

- **Change A (`--since` scoping)** is low-risk — it touches mainly
  `discover-plugin-health/SKILL.md` and adds no new files. It delivers the
  largest win (the incremental-rerun reduction). **Ship and verify it first.**
- **Change B (deterministic conversion)** is the heaviest edit to the lens
  architecture — a new script, fixtures, validator surgery, 4 agent archives, and
  a multi-file doc sweep. **Ship it second**, after Change A is committed and
  green, so a problem in B never blocks A.

Change B depends on Change A: B's static-lens script honors the `--since`
scoping and the scopability classification that A introduces. Do not start B
until A is committed.

---

## Change A — `--since <ref>` changed-files scoping

Ship and commit this **first**.

### A1. Lens scopability classification (drives `--since`)

`--since` narrows the `file_list` only for lenses whose findings are strictly
per-file/per-object. Corpus-comparison lenses always get the full list.

- **Scopable (narrow to changed files):** all `quality-agent-lens-*`,
  all `quality-skill-lens-*`, `design-agent-lens-scope-isolation`,
  `design-agent-lens-model-fit`, `design-agent-lens-caller-alignment`,
  `design-agent-lens-usage-patterns`, `design-agent-lens-tool-hygiene`,
  `design-skill-lens-complexity`, `design-skill-lens-surface-placement`,
  `design-skill-lens-maintainer-handoff`, and `naming-convention-lens`. (The
  mapping context still encodes cross-file facts, so per-object findings remain
  correct.) Note: the last four named here — `tool-hygiene`, the two
  `*-lens-structure` lenses, and `naming-convention-lens` — are the four that
  Change B later converts to the deterministic script; in Change A they are still
  LLM lenses and are scoped like any other per-file lens.
- **NOT scopable (always full corpus):** `design-skill-lens-near-duplicates`,
  `design-skill-lens-shared-backbone`, `design-skill-lens-handoff-gaps`,
  `design-skill-lens-preplanning` — these compare *across* the corpus and would
  produce wrong results on a partial list.

Encode this as a small table in the SKILL (or in `lens-invocation-patterns.md`)
so the dispatcher knows which lists to narrow.

### A2. `discover-plugin-health/SKILL.md` — `--since` plumbing

- **Phase 0 / Phase 1 (`--since` scoping):** add `--since <ref>` to Phase 0 arg
  parsing and Phase 1 globbing. When present, intersect each globbed list with
  `git diff --name-only <ref>` (working-tree-vs-`<ref>`, which captures committed,
  staged, and unstaged changes in a single pass; use two-dot `<ref>..HEAD` if
  only *committed* changes since `<ref>` are wanted) — but **only for scopable
  lenses** (see A1). The manifest (Phase 2) is always built from the **full**
  corpus so cross-file mappings stay correct.
- **Path normalization (load-bearing — silent-failure trap):** Phase 1 globbed
  paths are **absolute** (the SKILL states "All paths are absolute"), while
  `git diff --name-only` emits **repo-root-relative** paths. A naive set
  intersection of the two yields the **empty set** — and an empty file list reads
  as "nothing to check → no findings," a correctness bug that masquerades as a
  clean pass. The intersection MUST normalize one side to the other (resolve the
  git output to absolute against the repo root, or strip the repo-root prefix from
  the globbed paths) before comparing. State this explicitly so it is built right
  the first time.
- **Empty-intersection behavior:** if a scopable lens's narrowed list comes back
  empty (the surface had no changed files), **skip dispatching that lens and log
  the skip** (e.g. `naming-convention-lens: skipped (no changed files in scope)`)
  rather than dispatching it against an empty list — a no-file dispatch wastes a
  call and can emit a spurious "no findings" block. Non-scopable lenses are never
  skipped.
- Update the `argument-hint` frontmatter to include `[--since <ref>]`.

### Change A — critical files

- `.claude/skills/discover-plugin-health/SKILL.md`
- `profile-al-dev-shared/knowledge/lens-invocation-patterns.md` (if the
  scopability table lives there rather than inline in the SKILL)

### Change A — verification

1. **`--since` scoping (also proves path normalization):** touch one agent file,
   run `/discover-plugin-health --surface plugin --since HEAD~1`, and confirm
   scopable lenses receive **exactly that one changed file** (not an empty list —
   an empty list here means the absolute-vs-relative normalization is broken)
   while `near-duplicates`/`shared-backbone` still receive the full list (inspect
   the manifest / dispatch prompts).
2. **Empty-intersection skip:** run `--since HEAD` (no changes since HEAD) on a
   clean tree and confirm scopable lenses are **skipped with a logged note**, not
   dispatched against an empty list, and non-scopable lenses still run.
3. **No-`--since` regression:** run `/discover-plugin-health --surface plugin`
   without `--since` and confirm every lens still receives the full corpus (the
   flag is purely additive — absence changes nothing).
4. **Neutrality + markdownlint:** run `validate_harness_neutrality.py` and
   markdownlint on every changed markdown file before commit.

### Change A — commit

One atomic commit covering only the `--since` plumbing and scopability
classification. Verify the commit is green before starting Change B.

---

## Change B — deterministic static-lens conversion

Ship and commit this **second**, after Change A is committed.

### Conversion set (the 4 deterministic lenses)

| Lens | Dimension | Surface(s) | Why deterministic |
|------|-----------|-----------|-------------------|
| `naming-convention-lens` | naming | agents + skills | Pure filename regex + output-path patterns + grandfather list read from `docs/al-dev-naming-convention.md`. Already ~100%. |
| `quality-agent-lens-structure` | quality | agents | Frontmatter field presence, tool canonicality (the canonical set is machine-validated today), Inputs/Outputs sections, header numbering. |
| `quality-skill-lens-structure` | quality | skills | Frontmatter `name`/`description`, `argument-hint` conditional rule (see scope note), output-file naming, header numbering. |
| `design-agent-lens-tool-hygiene` | design | agents | Frontmatter `tools` vs body usage verbs. The unambiguous majority is deterministic; see scope note below. |

**Tool-hygiene scope note:** the script flags only high-confidence cases —
`Write`/`Edit` on a read-only agent (High), and a declared tool with *zero* body
mention (Medium/Low). The genuinely ambiguous negative-context case
("Do not use Bash") is simply **not flagged** — historically low-signal, and
dropping it keeps the check false-positive-free. State this reduction explicitly
in the script docstring and in `lens-invocation-patterns.md`.

**Structure-check scope note (argument-hint):** the `argument-hint` rule in
`quality-skill-lens-structure` is *conditional*, not a pure presence check — the
agent only flags a missing hint **when the body references an optional argument
in instruction prose**. To keep this deterministic and false-positive-free, the
script keys the "body references an argument" condition on concrete patterns
only — a literal `If an argument was passed` mention or a `[arg]`-style token
appearing **outside** frontmatter and fenced code blocks. Any fuzzier "the prose
implies an argument" inference is **not flagged**. State this reduction in the
script docstring and `lens-invocation-patterns.md`, the same way the tool-hygiene
note does.

### B1. New deterministic static-lens runner — `scripts/health_static_lenses.py`

A single script that runs the 4 checks above and writes findings in the
**existing per-lens artifact shape** so the rest of the pipeline is unchanged.

- **Args:** `--surface plugin|tooling` (single surface only — **no `both`**; see
  the per-surface serialization note in B2), `--dimension
  design|quality|naming|all`, `--since <ref>` (optional), `--out-dir .dev`
  (default), `--date <YYYY-MM-DD>`.
- **Surface → corpus mapping (mirror discover Phase 0, don't re-derive):**
  `plugin` → `profile-al-dev-shared/{agents,skills}`, `tooling` →
  `.claude/{agents,skills}`. All 4 converted checks run on **both** surfaces
  (none of them is among the two per-surface design-lens exclusions), only the
  corpus root differs.
- **Behavior:** for each check whose dimension is in `--dimension` scope, glob the
  relevant corpus (same `find` rules as discover Phase 1, honoring `--since` for
  the scopable checks per Change A's classification — including the same
  absolute-vs-relative path normalization), run the deterministic logic,
  and write `.dev/<date>-plugin-health-lens-<lens-name>.json` with the **exact
  schema the LLM lenses use**: `{lens, findings, suggestion_count, completed_at}`.
  The `findings` value is the same markdown block (`### <Lens> Findings` + rows,
  or `_No issues found._`) the agent would have returned. The filename carries
  **no surface token** — matching the existing LLM-lens outputs — which is only
  safe because discover serializes surfaces (B2).
- **Canonical tools source:** derive the canonical tool set directly from
  `profile-al-dev-shared/knowledge/agent-tool-projection-policy.md`
  (`projection_rules.claude` keys) — the same source `validate-lens-agents.py`
  uses today — rather than a marker comment. This removes the marker-sync
  coupling.
- **Why this shape:** discover Phase 4 globs `.dev/*-plugin-health-lens-*.json`
  and `--resume` parses the `"lens"` field. Writing the same files means **Phase 4
  assembly and resume need zero changes** and treat deterministic findings
  identically to agent findings.
- Pattern to reuse: model the JSONL/IO and arg-parsing style on existing scripts
  (`scripts/health_disposition_store.py`, `scripts/select_health_artifacts.py`).
- **Tests:** add `scripts/tests/` fixtures or an inline test (per the CLAUDE.md
  libexpat workaround) asserting each check fires on a known-bad fixture and is
  silent on a known-good one.

### B2. `discover-plugin-health/SKILL.md` — wire in the runner + remove converted lenses

- **Phase 3 step 1 (`ALL_LENSES`):** remove the 4 converted lenses from the LLM
  lens set. Per-surface LLM dispatch count drops 22 → 18.
  - **Two counts, reconciled (they are not a typo for each other):** 23 lens
    agents exist on disk; one design lens is excluded per surface (Phase 3:
    `tooling` drops `surface-placement`, `plugin` drops `maintainer-handoff`), so
    **22 dispatch per surface**. After this change, **18 dispatch per surface**
    and **19 agents remain on disk** — the on-disk 19 is the count
    `validate-lens-agents.py` asserts (B3 / Verification step 3).
- **New Phase 2.5 — Deterministic static lenses (runs before the parallel
  dispatch):** invoke `python3 scripts/health_static_lenses.py --surface <s>
  --dimension <d> [--since <ref>] --date <today>`. It writes its lens `.json`
  files into `.dev/` alongside (eventually) the agent outputs. Idempotent on
  `--resume` (re-running overwrites its own JSON; cheap) and **always runs on
  resume** — Phase 4 cleanup deletes the `.dev/` JSONs at the end of a completed
  run, so a fresh resume after interruption must re-emit them.
- **Per-surface serialization (load-bearing — do not break it):** the lens-output
  filename and the Phase 2 manifest carry **no surface token**, so `--surface
  both` only works because discover processes surfaces **one at a time**, running
  Phase 1→4 (including the Phase 4 `.dev/` cleanup) for `plugin` before starting
  `tooling`. Phase 2.5 must therefore run **once per requested surface, inside
  that per-surface loop, immediately before that surface's dispatch** — and the
  script is called with a single `--surface`, **never `both`**. Calling it once
  for both surfaces, or before the surface loop, would collide the surface-less
  JSON filenames (e.g. two `…-lens-naming-convention-lens.json`).
- **Ordering vs. the empty-`remaining_lenses` short-circuit (Phase 3 step 2):**
  Phase 2.5 must run **before** Phase 3's "if `remaining_lenses` is empty, skip to
  Phase 4" check. This matters most for `--dimension naming`: after conversion the
  only naming lens is the (now-removed) `naming-convention-lens`, so
  `remaining_lenses` is **empty and zero LLM lenses dispatch** — the entire
  dimension is served by the script. Phase 4 then assembles via its existing
  "case (a) — empty + lens `.json` files on disk" branch. So the script having
  already written its naming JSON in Phase 2.5 is what makes a `--dimension
  naming` run produce findings at all. Confirm Phase 3's empty-list branch still
  routes to Phase 4 case (a) rather than treating empty as "nothing ran."

### B3. Contract & validator updates

- **`scripts/validate-lens-agents.py`:** remove the 4 converted lenses from
  `EXPECTED_AGENTS`; retire the canonical-tools marker check
  (`_canonical_tools_from_lens` / `STRUCTURE_LENS` block) since the script now
  reads the policy directly **and `quality-agent-lens-structure.md` is being
  archived — leaving the `STRUCTURE_LENS` path reference would crash the
  validator**; add a check that `scripts/health_static_lenses.py` exists and is
  executable. Update the trailing PASS count message.
- **`profile-al-dev-shared/knowledge/lens-invocation-patterns.md`:** drop the 4
  converted lenses from the agent/skill lens lists and the per-lens context
  tables; add a short "Deterministic lenses" subsection naming the script and the
  two scope reductions (tool-hygiene and argument-hint). Fix the
  `naming-convention-lens` caller-contract note (it is now a script step, not a
  dispatched agent).
- **Archive the 4 agent `.md` files** to `.claude/agents/archived/` (consistent
  with how `al-dev-test` etc. were handled) rather than deleting, so history and
  the prior prompt text are preserved.
- Grep for other references to the 4 lens names and update counts/lists:
  `docs/al-dev-agent-map.md`, `docs/maintainer-tooling*`, and any
  `.claude/knowledge/health-*.md` that enumerates lenses. Use `git grep -n` for
  each converted lens name. (Note: no literal "23 lenses"/"NN lens agents" count
  string exists in any tracked `.md` today — verified by `git grep -nEi`. The
  only maintained total is `len(EXPECTED_AGENTS)` in `validate-lens-agents.py`,
  already handled above. Do not add a phantom count-update task; if `git grep`
  surfaces a count string later, update it then.)

### Change B — critical files

- `scripts/health_static_lenses.py` (new)
- `scripts/validate-lens-agents.py`
- `.claude/skills/discover-plugin-health/SKILL.md`
- `profile-al-dev-shared/knowledge/lens-invocation-patterns.md`
- `.claude/agents/{naming-convention-lens,quality-agent-lens-structure,quality-skill-lens-structure,design-agent-lens-tool-hygiene}.md` → archived
- Reference-only updates: `docs/al-dev-agent-map.md`, `.claude/knowledge/health-discover-aggregation.md` (lens enumeration), maintainer docs

### Change B — verification

1. **Static-lens script correctness (deterministic):** run
   `python3 scripts/health_static_lenses.py --surface plugin --dimension all
   --date 2026-06-22 --out-dir /tmp/healthtest` and confirm it writes one
   `.json` per converted check with the correct schema and findings blocks that
   match the format the LLM lenses produced. Run the inline fixture tests
   (good/bad cases) per the CLAUDE.md libexpat workaround.
2. **Parity spot-check:** on the current corpus, compare the script's findings
   against the most recent **raw discover findings file**
   (`docs/health/<date>-<surface>-findings.md`) — *not* the ranked,
   disposition-filtered dossier. The dossier strips grandfathered/declined
   findings and re-ranks, so comparing raw script output to it produces phantom
   "regressions" that are really just suppression. Against the raw findings file,
   confirm no regressions for the structure/naming/tool-hygiene findings (same
   known issues surface; no new false positives).
3. **Validator:** `python3 scripts/validate-lens-agents.py` → PASS with the
   updated expected count (19 LLM lens agents).
4. **End-to-end discover (filtered):** run
   `/discover-plugin-health --surface plugin --dimension quality` and confirm:
   both structure findings (agent + skill) appear in the assembled findings file
   (sourced from the script's `.json`), only 8 LLM lenses dispatch (not 10 — the
   quality dimension on `plugin` is 5 quality-agent + 5 quality-skill lenses, of
   which `quality-agent-lens-structure` and `quality-skill-lens-structure` are now
   the script's), and Phase 4 assembly + cleanup work unchanged.
5. **Resume integrity:** interrupt after the script step, re-run with `--resume`,
   confirm Phase 2.5 re-emits the deterministic `.json` files and only missing
   LLM lenses re-dispatch (the converted lens names are no longer in `ALL_LENSES`,
   so they never appear as "remaining"; they are picked up at Phase 4 assembly).
6. **`--since` still works under conversion:** run
   `/discover-plugin-health --surface plugin --since HEAD~1` and confirm the
   script honors `--since` for its scopable checks (touched file only) while the
   non-scopable LLM lenses still receive the full corpus — i.e. Change A's
   behavior is preserved after the conversion.
7. **`--surface both` serialization (no filename collision):** run
   `/discover-plugin-health --surface both` and confirm **both**
   `docs/health/<date>-plugin-findings.md` and `<date>-tooling-findings.md` are
   written with the converted checks present in each, and that the tooling run
   reads the `.claude/{agents,skills}` corpus (not the plugin corpus). This is the
   step that proves the surface-less script JSON is safe under the per-surface
   loop — all other steps are plugin-only.
8. **`--dimension naming` zero-LLM-dispatch:** run
   `/discover-plugin-health --surface plugin --dimension naming` and confirm
   **zero LLM lenses dispatch**, yet the assembled findings file still contains the
   `naming-convention-lens` block (sourced from the script's `.json` via Phase 4
   case (a)). Proves the Phase 2.5-before-empty-check ordering.
9. **Neutrality + markdownlint:** run `validate_harness_neutrality.py` and
   markdownlint on every changed markdown file before commit.

### Change B — commit

One atomic commit covering the script, the SKILL wiring, the validator/contract
updates, and the 4 agent archives.
