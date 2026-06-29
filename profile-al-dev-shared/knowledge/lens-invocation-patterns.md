# Lens Invocation Patterns

Canonical context requirements for design lens agents. Use this reference when
building dispatch prompts in skills that invoke design lenses. Quality lenses
need only a file list.

See also: `knowledge/architect-invocation-patterns.md` (parallel pattern for
`solution-architect`).

## Deterministic lenses (static runner — not dispatched as agents)

Four lenses are fully/mostly deterministic and are produced by a single static
runner, `scripts/health_static_lenses.py`, instead of LLM agents. They are
**not** dispatched and need no context fields or dispatch prompt:

- `naming-convention-lens` — filename and documented-output-path patterns, with
  the grandfather list read from the convention doc's exceptions section.
- `quality-agent-lens-structure` — frontmatter field presence, tool canonicality
  (canonical set read from the projection policy), Inputs/Outputs sections,
  header numbering, skill-only-field rejection.
- `quality-skill-lens-structure` — frontmatter `name`/`description`, the
  conditional `argument-hint` rule, header numbering.
- `design-agent-lens-tool-hygiene` — declared `tools` vs body usage.

The runner writes the same per-lens findings artifacts the LLM lenses wrote, so
downstream assembly is unchanged. Three deliberate scope reductions keep the
deterministic checks false-positive-free:

- **Tool-hygiene** flags only high-confidence cases: a write/edit capability on a
  read-only agent, and a declared MCP capability whose specific name never
  appears in the body. The ambiguous negative-context case (e.g. "Do not use" a
  named capability) and generic read/search-capability "zero literal mention"
  are **not** flagged — those capabilities are routinely exercised through
  synonym verbs rather than the literal capability word.
- **argument-hint** (in the skill structure check) is conditional and keyed on
  concrete patterns only: a literal `If an argument was passed` mention, or a
  `[arg]`-style token outside frontmatter and fenced code blocks. Fuzzier "the
  prose implies an argument" inference is **not** flagged. (An empty-string
  `argument-hint: ""` is a separate, unconditional finding and is still flagged.)
- **Output-file naming** (a check the prior skill structure lens carried) is
  **not** flagged deterministically. A regex over conventional, non-dated `.dev/`
  handoff filenames over-fires, and no reliable pattern distinguishes a
  legitimate established handoff file from a genuinely mis-named output; the raw
  lens flagged none of these, so the check is kept out to preserve the
  false-positive-free mandate.

---

## Finding evidence contract

Append this contract to every lens prompt, regardless of lens class. It is the
first-line defence against false-positive findings: a lens that must quote the
offending text cannot flag a problem that is not actually present.

Every finding a lens returns must include:

- the subject location as `file:line`,
- a short quoted snippet of the offending text at that location, and
- a one-line reason the snippet is a real issue (not a stylistic preference).

A lens must **omit** any finding it cannot ground in a quoted snippet — drop
speculative "consider whether…" or "it may be worth…" observations rather than
emitting them. Unverifiable findings are downstream-dropped at the report stage,
so emitting them only adds noise.

**Per-lens precision metric:** Each lens reply **should** include `verified_count`
and `raw_count` at the bottom of its findings block:

    verified_count: N  <!-- findings with file:line citations that resolve -->
    raw_count: N       <!-- total findings drafted before self-review -->

The report phase reads these fields to track per-lens precision (verified/raw)
across sweeps. A lens that consistently produces a low ratio is a candidate for
prompt refinement. If a lens does not emit these fields, the assembler uses
`suggestion_count` as a proxy and sets `verified_count = suggestion_count` (no
precision signal).

**Structured snippet field:** When a finding cites a code or text snippet,
include a structured `snippet:` block immediately after the `file:line` citation:

    snippet:
      file: path/to/subject.md
      line: 42
      text: "exact text from the file at that line"

The `text` field must be copied verbatim from the cited file and line — do not
paraphrase. The discover phase pre-checks that `text` matches the cited
`file:line` before writing the finding to the findings JSON; a non-matching
snippet causes the finding to be dropped at discover time rather than surviving
to the evidence gate.

---

## Response format contract

Append this to every lens prompt alongside the finding evidence contract. It
keeps each lens return small so a parallel multi-lens sweep does not flood the
dispatching session's context (the dominant cost is verbose per-lens narration,
not the findings themselves).

- Your entire reply must be **only** the findings block defined in your Output
  Format — nothing before or after it. Do not narrate your analysis, do not list
  the files you read, do not emit an "Analysis Summary" or per-file "OK"
  verdicts, and do not restate the task.
- If you find no issues, reply with exactly the lens heading followed by
  `_No issues found._` and nothing else.
- **Combined multi-lens readers** (`quality-agent-multilens`,
  `quality-skill-multilens`): the "reply with exactly the lens heading" rule
  above does **not** apply. Always emit all four `<!-- lens: … -->` markers and
  headings; for each clean lens emit its heading + `_No issues found._`. A
  marker-less reply breaks the Phase 4 splitter.
- **Roll-up cap:** when four or more findings share the same root cause **and**
  the same fix (for example, the same missing code-block language tag across many
  files), emit a single rolled-up finding whose location field lists the affected
  files, rather than one row per file. Distinct root causes always stay separate.

The dispatching skill includes each returned block verbatim in the findings
file, so a terse, block-only reply is both cheaper and directly usable.

---

## Design Agent Lenses

Agents: `design-agent-lens-caller-alignment`, `design-agent-lens-model-fit`,
`design-agent-lens-scope-isolation`, `design-agent-lens-usage-patterns`

(`design-agent-lens-tool-hygiene` is now a deterministic static-runner check —
see the Deterministic lenses section above.)

### Required context fields per lens (agent lenses)

| Lens | Required context fields |
|------|------------------------|
| `design-agent-lens-model-fit` | `model_assignments` |
| `design-agent-lens-scope-isolation` | *(none — file list only)* |
| `design-agent-lens-caller-alignment` | `caller_map` |
| `design-agent-lens-usage-patterns` | `single_use_agents`, `already_inline_candidates` |

### Dispatch template (agent lenses)

```text
Analyze the following agent files. Apply your lens to every file and return a findings block.

File list:
[one absolute path per line]

Context (include only the fields this lens requires per the table above):

tool_inventory: {mapping of agent → [tools]}
model_assignments: {mapping of agent → model}
caller_map: {mapping of agent → [spawning skills]}
single_use_agents: [list of agents with exactly one spawning skill]
already_inline_candidates: [single-use agents that could be inlined]
```

---

## Design Skill Lenses

Agents: `design-skill-lens-shared-backbone`, `design-skill-lens-complexity`,
`design-skill-lens-near-duplicates`, `design-skill-lens-handoff-gaps`,
`design-skill-lens-preplanning`, `design-skill-lens-surface-placement`,
`design-skill-lens-maintainer-handoff`

### Required context fields per lens (skill lenses)

| Lens | Required context fields |
|------|------------------------|
| `design-skill-lens-shared-backbone` | `agent_usage_counts` |
| `design-skill-lens-complexity` | `phase_counts`, `no_agent_skills` |
| `design-skill-lens-near-duplicates` | `agent_usage_counts`, `phase_counts` |
| `design-skill-lens-handoff-gaps` | `handoff_chains` |
| `design-skill-lens-preplanning` | `preplanning_skills`, `layer1_diagram_content` |
| `design-skill-lens-surface-placement` | `no_agent_skills` |
| `design-skill-lens-maintainer-handoff` | _(none — traces maintainer chains from the skill bodies in `file_list`)_ |

### Effective signal for tooling skills

The cross-surface design-skill lens count overstates *effective* design coverage
for maintainer (tooling-surface) skills. Several cross-surface lenses are
formally dispatched but carry reduced semantic signal there; the
tooling-specific `design-skill-lens-maintainer-handoff` is added to compensate:

| Lens | Tooling-skill signal |
|------|----------------------|
| `design-skill-lens-maintainer-handoff` | Full — tooling-specific; traces `docs/health/` maintainer chains directly from skill bodies |
| `design-skill-lens-complexity` | Full — phase counts and no-agent status are surface-neutral |
| `design-skill-lens-shared-backbone` | Partial — only when the skill spawns agents |
| `design-skill-lens-near-duplicates` | Partial — phase-shape signal transfers, agent-usage signal does not |
| `design-skill-lens-handoff-gaps` | Weak — its `handoff_chains` context is built from the distributed skills map, which excludes maintainer chains |
| `design-skill-lens-preplanning` | Weak — anchored in workflow-diagram placement, which maintainer skills rarely have |
| `design-skill-lens-surface-placement` | Excluded by dispatch for the tooling surface |

The tooling surface now has a dedicated design lens (`maintainer-handoff`) in
place of the excluded `surface-placement`, mirroring how the plugin surface uses
`surface-placement` in place of the excluded `maintainer-handoff`.

### Dispatch template (skill lenses)

```text
Analyze the following SKILL.md files. Apply your lens to every file and return a findings block.

File list:
[one absolute path per line]

Context (include only the fields this lens requires per the table above):

agent_usage_counts: {mapping of agent-type → [skill names that spawn it]}
phase_counts: {mapping of skill → phase count}
no_agent_skills: [list of skills with zero spawned agents]
handoff_chains: {mapping of skill → [output files]}
preplanning_skills: [pre-planning skill names — skills shown with dashed arrows in Layer 1]
layer1_diagram_content: [raw text of the Layer 1 Mermaid diagram from docs/al-dev-skills-map.md]
```

### Complexity Outliers — Verdict Field

Lines from the Complexity Outliers lens carry an extra `verdict` field between
severity and the observation:

```text
verdict=[Atomise|Absorb|None]
```

- `verdict=Atomise`: skill has two independently-runnable phase groups separated
  by a USER_GATE or phase boundary; recommend splitting into two skills.
- `verdict=Absorb`: skill has zero core logic (≤2 phases, no agent dispatch);
  recommend folding into its caller.
- `verdict=None`: monitor only; no structural action required.

When parsing Complexity Outliers findings, extract and act on this field before
writing the dossier section.

---

## Quality Lenses

Agents: `quality-agent-multilens`, `quality-skill-multilens` — two combined
readers that each read their corpus once and apply all four quality rubrics
(Bloat, Prompt Clarity, Description Drift, Name Fit), returning four
`<!-- lens: … -->`-delimited blocks split into per-lens JSONs by
`scripts/split_multilens_findings.py`. They take a file list only (no context),
stay on haiku, and replace the eight former individual quality lens agents.

(The two structural-conventions lenses and `naming-convention-lens` remain
deterministic static-runner checks — see the Deterministic lenses section.)

These lenses derive all findings from the file list alone. No context structures
are required.

### Dispatch template (quality-agent-multilens)

```text
Analyze the following agent files. Apply ALL FOUR quality lenses (Bloat,
Prompt Clarity, Description Drift, Name Fit) to every file in a single pass.
Return exactly four findings blocks, each preceded by its
`<!-- lens: quality-agent-lens-<name> -->` marker, in the order bloat, clarity,
description, name-fit. Emit all four markers even when some or all lenses are
clean.

File list:
[one absolute path per line]
```

### Dispatch template (quality-skill-multilens)

```text
Analyze the following SKILL.md files. Apply ALL FOUR quality lenses (Bloat,
Prompt Clarity, Description Drift, Name Fit) to every file in a single pass.
Return exactly four findings blocks, each preceded by its
`<!-- lens: quality-skill-lens-<name> -->` marker, in the order bloat, clarity,
description, name-fit. Emit all four markers even when some or all lenses are
clean.

File list:
[one absolute path per line]
```

> **Caller contract:** the naming check is now produced by the
> `scripts/health_static_lenses.py` runner (a Phase 2.5 step of
> `discover-plugin-health`), not a dispatched agent. Its single downstream
> consumer is `report-plugin-health`, which reads the assembled findings file.
> Changes to the naming check's output format affect only those two skills.

---

## Background

`/audit-plugin-health` Phase 2.1 historically passed all 10 context structures to
every design and quality lens. This created maintenance burden: callers that
needed 2 fields received 8 inert ones. This file canonicalizes the minimum
required context per lens class so dispatchers pass lean, correct prompts.

**Inert fields by lens class (confirmed by rubber-duck 2026-05-29):**

- Design agent lenses receive: `phase_counts`, `handoff_chains`, `preplanning_skills`,
  `agent_usage_counts`, `no_agent_skills` — not used
- Design skill lenses receive: `tool_inventory`, `model_assignments`, `caller_map`,
  `single_use_agents`, `already_inline_candidates` — not used
- Quality lenses: all 10 context structures — not used

---

## Workflow Dispatch Pattern

When dispatching multiple lens agents in parallel, use the canonical in-session
background-dispatch pattern in
[`background-agent-dispatch.md`](background-agent-dispatch.md): dispatch one
background agent per lens, hand off through artifact files, and gate on artifact
presence. This is the canonical orchestration mechanism for multi-lens sweeps.
Individual lens dispatches use the single-lens template above.

### Sequential single-lens dispatch

For one lens or sequentially ordered lenses:

```text
Dispatch: <lens-agent-name>
Context: [fields from the per-lens table above — include only required fields]
```

### Parallel multi-lens dispatch (health sweep)

For 3+ independent lenses (e.g., a full plugin health audit), dispatch all in
one parallel call. Lenses are independent — no lens output is another's input.

Steps:

1. Build the file list for each surface (agents or skills).
2. Build the per-lens context fields (tool_inventory, model_assignments, etc.)
   from the plugin graph and map files.
3. Write the file lists and context blocks **once** to a single run-manifest
   artifact, and point each lens at that manifest instead of inlining the file
   list into every dispatch prompt. With 20+ lenses, re-inlining the file list
   per prompt is a large, avoidable cost in the dispatching session.
4. Dispatch all lenses in a single parallel block; append the finding evidence
   contract and the response format contract above to every prompt.
5. Collect all outputs before synthesising findings.

See `/discover-plugin-health` for the canonical multi-lens dispatch implementation.
