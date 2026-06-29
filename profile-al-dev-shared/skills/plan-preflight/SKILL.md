---
name: plan-preflight
description: >-
  Gather and verify context before architect debate. Executes phases 0–1.6 of planning:
  resume check, complexity triage, context gathering, claims verification, and target
  confirmation. Outputs PREFLIGHT_CONTEXT block (written to .dev/preflight-context.md) for consumption by plan or other
  workflows. Can be invoked standalone or chained by skills that need reusable context assembly.
argument-hint: "[--resume | requirements file path]"
---

# Plan Preflight Skill

Gather and verify the context needed to begin architect debate, without
performing the debate itself. This skill assembles requirements, triages
complexity, loads project and symbol context, verifies external claims, and
confirms targets — then emits a single `PREFLIGHT_CONTEXT` block (written to
`.dev/preflight-context.md`) that downstream workflows consume.

This skill is reusable: `/plan` chains to it automatically, and other
skills (e.g. `fix`, `investigate`) can invoke it to avoid
duplicating context assembly. It does NOT design the solution or spawn
architects.

## Intent Preflight

Before assembling context or writing the `PREFLIGHT_CONTEXT` artifact, apply
`knowledge/intent-preflight.md`.

Default intent for this skill is `REVIEW` when the user asks for design,
planning, or architecture output. Writing the `.dev/preflight-context.md`
artifact is allowed as part of that planning request.

When shell search or structured-file inspection is required, prefer `rg` and
`jq` before falling back to broader shell text processing.

## Artifact Contract

This skill is governed by `../../knowledge/artifact-contracts.md`.

Do not claim preflight is complete or ready for architect debate until the
success evidence named in `../../knowledge/artifact-contracts.md` for this
skill — `.dev/preflight-context.md` — has been written and read in the current
run.

## Phase 0: Check for Existing Progress

This skill produces the state needed to begin architect debate:
requirements gathering, complexity triage, context loading,
external-claim verification, and target confirmation. The
architect-debate phases (in `plan`) consume only the
`PREFLIGHT_CONTEXT` state listed below — they do not read
intermediate state from these preflight phases directly.

### Resume modes

Decide the mode from `$ARGUMENTS` and the presence of
`.dev/preflight-context.md`:

- **Mode A — `--resume` passed:** the caller asserts context is already
  finalized. If `.dev/preflight-context.md` is missing or unreadable,
  STOP and report: *"No preflight context to resume from. Run
  /plan-preflight without --resume to perform preflight (phases
  0–1.6) first."* Do not fabricate context state. Otherwise run the
  **shared load step** below.
- **Mode B — no `--resume`, but `.dev/preflight-context.md` exists:**
  offer resume via USER_GATE:

  > A prior preflight context exists (saved [timestamp]) for:
  > [one-line requirements summary].
  >
  > - **Resume** — re-emit the existing context block (skip re-gathering)
  > - **Restart** — discard the context and gather fresh

  **Resume** → run the **shared load step** below. **Restart** → delete
  `.dev/preflight-context.md`, then proceed as Mode C.
- **Mode C — no `--resume` and no context file:** apply the standard
  Phase 0 Read Protocol in `knowledge/workflow-resilience.md` (handles
  `.dev/progress.md` mid-run resume), then proceed to Phase 0.5.

**Shared load step (Mode A, and Mode B → Resume):** read
`.dev/preflight-context.md`, load the context fields (see schema below)
into the working state, re-verify any stale code-level claims (see next
paragraph), emit the `PREFLIGHT_CONTEXT` block, and honour
`no_crit_swarm` if set.

**Stale-claim re-verification (resume only):** a stored context file may
predate fixes that have since landed, so before emitting `PREFLIGHT_CONTEXT`
do a lightweight freshness check of the claims carried in
`external_findings_status`. This is a freshness check, not a re-run of
Phase 1.5:

- For each ✅ Verified or ⚠️ Partially verified claim whose evidence cites a
  concrete `file:line` (file-path evidence per Phase 1.5 step 1), confirm the
  file still exists and the described content is still present at that
  location. If the file is gone or the content no longer matches, downgrade
  that claim to `⚠️ Needs re-verification` in `external_findings_status`.
- Symbol/API claims (evidence source `AL LSP` or `AL MCP`) are out of scope
  for this lightweight check — they need a semantic provider; leave their
  stored status unchanged.
- If any claim is downgraded, do not re-run Phase 1.5's decision threshold —
  forward the annotated block so architects treat `⚠️ Needs re-verification`
  claims as hypotheses, not requirements.

### PREFLIGHT_CONTEXT schema

These phases write `.dev/preflight-context.md` once context gathering
and any optional verification phases complete (see the **end of Phase
1.6** write step). The canonical schema and field semantics are defined
in `../../knowledge/preflight-context-schema.md` — read that file before
writing or loading the context file.

When resuming (Mode A or Mode B → Resume), treat these fields as the
authoritative substitute for the corresponding preflight outputs:

- `requirements` + `scope` → the user requirement and scope for the
  architect prompts.
- `architect_model` → the model assignment from Phase 0.5 (do not
  re-triage).
- `user_context` → the project-context inputs (object ID range,
  naming prefix, key patterns) and any perf/explore findings.
- `external_findings_status` → the **External findings status:**
  block forwarded to architects (Phase 1.5 output); skip if null.

If a required field is missing from the context block, fall back to
re-running the specific preflight step that produces it rather than
proceeding with empty state.

---

## Phase 0.5: Complexity Triage

Classify the request before gathering full context.
See `knowledge/plan-phase-routing.md` for full complexity classification rules and model assignment logic.

Quick reference:

| Signal | SIMPLE | MEDIUM / COMPLEX |
| --- | --- | --- |
| Estimated file count | ≤ 3 | 4+ or unclear |
| Pattern in codebase (if known) | Yes | No / unclear |
| New architecture needed | No | Yes |
| Requirements ambiguous | No | Yes |

When in doubt, default to `opus` (MEDIUM / COMPLEX tier).

Note `architect_model` for use by the architect debate:

- **SIMPLE** → `sonnet`
- **MEDIUM / COMPLEX** → `opus`

Do not surface this decision to the user.

---

## Phase 1: Gather Context

**Vagueness gate (run before any other step):**

Check whether $ARGUMENTS contains a meaningful feature description. Sufficient context requires all three of: (1) a feature name or description, (2) at least one functional requirement (a descriptive sentence stating what the feature should do — a single sentence suffices), AND (3) at least one concrete anchor — a named BC object (table, page, codeunit, event) or a named user workflow (e.g. "during sales order posting"). Example: "Add a credit limit check during posting."

**VAGUE:** Missing one or more of: (1) a feature name or description, (2) at least one functional requirement, (3) at least one concrete anchor (ticket, file, or behaviour reference).
**SUBSTANTIVE:** All three elements present — proceed.

If $ARGUMENTS is empty, missing, or only a vague word (e.g. "plan", "help", "this") with no feature context, **STOP immediately**. Do **not** proceed to steps 1–4 below, read any files, or spawn any agents until a **substantive answer** supplying all three elements is provided. Escalate across attempts:

| Attempt | Action |
|---------|--------|
| 1st vague | Ask once: "What AL feature or fix should I plan? Please describe the requirement or paste a spec." Required context: (1) business goal, (2) key workflows, (3) affected BC objects. |
| 2nd vague | Ask with explicit scaffold: "Please provide: (1) the business goal (what problem does this solve?), (2) the key user workflows (who does what?), and (3) the BC objects affected (which tables/pages/events?)." |
| 3rd vague | Stop and escalate: "I've asked twice for clarification. To proceed I need: (1) business goal — what problem this solves, (2) key workflows — who does what and when, (3) affected BC objects — which tables/pages/events. Please provide all three, or consider running /interview first for guided discovery." |

Do NOT mark preflight complete if after 2 clarification attempts the description remains too vague (e.g., "make it better", "improve the system"). Once a substantive description is given, resume from step 1 with it as the effective $ARGUMENTS.

1. **Read input from $ARGUMENTS** — Extract the user's feature request and preliminary scope. If missing, gate requires clarification.
2. **Load requirements and context files** — read `.dev/project-context.md` (object ID ranges, naming conventions, architectural patterns, base app integration points) and any prior interview requirements (`$(ls .dev/*-interview-requirements.md 2>/dev/null | sort | tail -1)`). If project context is missing, suggest `/al-dev-init-context` (a companion-layer capability — see `knowledge/companion-context-ownership.md`) and degrade to a minimal inferred context rather than hard-stopping. If requirements are unclear/complex, suggest `/interview`.
3. **Gather symbol evidence** — use the strongest available AL symbol evidence before emitting context: prefer `AL LSP` semantic navigation (go-to-definition, find-references, document symbols, hover/type) when the active harness exposes it; otherwise AL MCP via `al-mcp-server` (`al_search_objects`, `al_get_object_definition`, `al_search_object_members`); otherwise tightly scoped `rg` labeled as `text search`. Include findings and evidence source (`AL LSP`, `AL MCP`, `text search`, or `unverified`) in the `PREFLIGHT_CONTEXT` `user_context`. If no provider/result is available, record general AL knowledge unless a required symbol is `unverified`.
4. **Load performance and exploration findings** — if available, integrate findings from `/explore`, `/perf`, or `/investigate` pre-planning phases:

   ```bash
   PERF=$(ls .dev/*-perf-perf-analysis.md 2>/dev/null | sort | tail -1)
   EXPLORE=$(ls .dev/*-explore-findings.md 2>/dev/null | sort | tail -1)
   INVESTIGATE=$(ls .dev/*-investigate-findings.md 2>/dev/null | sort | tail -1)
   ```

   If a perf file is found, read CRITICAL/HIGH findings and record them as **"Performance constraints from prior analysis:"** in `user_context`. If an explore file is found, read the findings and synthesized recommendations and record them as **"Codebase exploration findings from prior investigation:"** in `user_context`. If an investigate file is found, read the root-cause findings and record them as **"Root cause investigation findings from prior investigation:"** in `user_context`. If none of the three exist, skip silently.

## Phase 1.5: Verify and Confirm (Optional)

**Phase 1.5 (Optional):** Run when the user request references a findings file, codeburn output, lint report, or third-party analysis (steps 1.5.1–1.5.5), or when Phase 1 discovers a target ambiguity or resource constraint (steps 1.5.6–1.5.8). Skip both if neither condition applies.

1. **File path verification:** For each file path mentioned in findings:
   - Confirm the file exists at that exact path with `test -f <path>`
   - Spot-check content: open the file and verify the described issue/content is present
   - If path doesn't exist → mark as **unverified**, note the missing path
   - If content differs from description → mark as **partially verified**, note the discrepancy
2. **Symbol/API verification:** For each function, procedure, field, or table mentioned:
   - Prefer `AL semantic navigation` (`AL LSP`) when the active
     harness exposes it: go-to-definition, find-references,
     document symbols, and hover/type information.
   - If unavailable, use AL MCP (`al_search_objects`,
     `al_search_object_members`, `al_get_object_definition`, or
     `al_find_references`).
   - If no semantic provider is available, use scoped text search:
     `rg -n "symbol_name" src/ --glob "*.al"`.
   - Record evidence source as `AL LSP`, `AL MCP`, `text search`,
     or `unverified`.
   - If not found → mark as **unverified**.
   - If found but context differs → mark as **partially verified**.
3. **Build evidence summary** as Markdown table:

   | Claim | Type | Status | Evidence Source | Evidence |
   | --- | --- | --- | --- | --- |
   | "Field X exists on table Y" | symbol | Verified | text search | `src/TableY.al:42` contains field declaration; semantic provider unavailable |
   | "Procedure Q exists" | procedure | Unverified | unverified | No `AL LSP`, `AL MCP`, or scoped `rg` result found |
   | "Event R has parameter S" | event signature | Verified | AL MCP | `al_search_object_members` found publisher signature with parameter S |

4. **Record findings** in `external_findings_status` under `**External findings status:**`
   - ✅ Verified — treat as design input
   - ⚠️ Unverified — treat as hypothesis to test, not requirement
   - ⚠️ Partially verified — details differ; assume claims are approximate
5. **Decision threshold:**
   - ≥75% verified → proceed
   - 50–74% verified → proceed with explicit caveat in `external_findings_status`
   - <50% verified → gate with USER_GATE decision (proceed as hypotheses / re-run investigation / proceed anyway)

   Formula: score = (verified_count + 0.5 × partial_count) / total_count
   - verified: claim confirmed against a live file or reference
   - partial: claim partially corroborated (one supporting reference found, not all)
   - unverified: no corroborating evidence found

   Note: This formula is consistent with the resume re-verification logic at Phase 0 stale-claim re-verification.

### 1.5.6–1.5.8: Target Confirmation

If Phase 1 discovers a target ambiguity or a specific resource constraint (e.g., a .dev/findings-file.md or external lint output that references a particular subsystem), cross-check the target interpretation before emitting context — run the steps below before acting on any findings file or context document. Otherwise, skip to the context write.

1. **Identify targets:**
   - Findings reference: Extract the target name/path from the document
   - Your request: Extract target from user message (skill, repo, file, or project)
   - Output path: Absolute path where work will land
2. **Validate match:**

   ```text
   > **Target check:**
   > - Findings reference: [extracted from findings]
   > - Your request: [extracted from your message]
   > - Output path: [absolute path where work will land]
   >
   > Do these match? If findings and request disagree, stop and confirm before proceeding.
   ```

3. **Decision:**
   - If all align → continue
   - If findings/request disagree → flag mismatch and wait
   - If mismatch is fundamental → stop and escalate to user

## Emit PREFLIGHT_CONTEXT

Once preflight (phases 0.5–1.6) is complete, write
`.dev/preflight-context.md` using the schema in Phase 0. This captures
the full state the architect debate needs so a later run can resume
with `--resume`:

```bash
mkdir -p .dev
```

Attempt to Read `.dev/preflight-context.md` before writing (the harness
requires a file path to have been read in the current session before it
can be written). If the Read returns a "file not found" error, treat that
as the expected fresh-run state and proceed with the Write immediately.

Populate `requirements`, `scope`, `architect_model`, `user_context`,
`external_findings_status` (or `null` if Phase 1.5 was skipped),
`timestamp` (ISO 8601), and `no_crit_swarm`. Set `phase` to `2`.
Overwrite any existing context file — latest state wins.

After writing, emit the `PREFLIGHT_CONTEXT` block so a chaining skill
(e.g. `plan`) or the user can consume it directly:

```text
PREFLIGHT_CONTEXT (.dev/preflight-context.md)
- requirements: [user requirement + preliminary scope]
- scope: [file count, affected BC objects, patterns]
- architect_model: [sonnet | opus]
- user_context: [object ID range, naming prefix, key patterns, perf/explore findings]
- external_findings_status: [verified/unverified summary, or null]
- no_crit_swarm: [true | false]
```

When invoked standalone, present the block to the user and stop. When
chained by `/plan`, hand the block to Phase 2 (architect debate)
without re-gathering.
