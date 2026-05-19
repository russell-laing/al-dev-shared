# AL Dev Skill Quality Audit

**Last run:** 2026-05-19
**Skills audited:** 16

## Summary

| Severity | Count |
|----------|-------|
| High     | 10    |
| Medium   | 15    |
| Low      | 21    |

## Findings

### /commit-learn

**[High] Lens 3 — Description Drift**
Observation: `description` says "Analyze commit semantics and learn from code review feedback" but the entire body is about recovering corrupted files from `.dev/commit-integrity.log`. These are unrelated purposes.
Fix: Rewrite description to: "Analyze and recover corrupted AL files flagged in `.dev/commit-integrity.log` using learned fallback strategies."

**[High] Lens 1 — Prompt Clarity**
Observation: "Spawn **verifier subagent** with incident details" is the only instruction for the dispatch step — no Agent tool invocation, no agent type, no prompt structure. Every other skill specifies the agent type and prompt template.
Fix: Add a concrete Agent tool block specifying `subagent_type: commit-learn-verifier` and the expected prompt fields (incident file path, baseline lines, git history, learnings.md content).

**[High] Lens 1 — Prompt Clarity**
Observation: No numbered step-by-step procedure — the "How It Works" section is descriptive prose only. The orchestrator has no runnable path to follow.
Fix: Convert "How It Works" into numbered Steps 1–4 matching the bullet structure, with concrete bash commands and Agent tool calls.

**[Medium] Lens 2 — Structural Conventions**
Observation: Output file is `learnings.md` and `commit-integrity.log` with no `.dev/YYYY-MM-DD-*` date-prefix convention and no absolute path specified.
Fix: Specify full output paths: `.dev/commit-integrity.log` (input), `.dev/learnings.md` (output).

**[Medium] Lens 2 — Structural Conventions**
Observation: No numbered phases or steps — skill body uses informal section headers ("How It Works", "Output (Read-Only Mode)", "Internal Workflow"). Inconsistent with all other skills.
Fix: Restructure into Step 1 / Step 2 / Step 3 convention matching the rest of the plugin.

---

### /al-dev-commit

**[High] Lens 1 — Prompt Clarity**
Observation: Step 7 says `yes → continue to Step 6` (already completed) and Step 8 says `yes → continue to Step 7` (already completed). Both cross-references point backward and will cause infinite re-execution loops if followed literally.
Fix: Step 7 `yes` → `continue to Step 8`; Step 8 `yes` → `continue to Step 9`.

**[High] Lens 4 — Bloat**
Observation: 11 effective steps including Steps 5.5 and 9.5 — exceeds the 8-step ceiling. The decimal sub-steps are real workflow gates, not formatting artifacts.
Fix: Merge Step 5.5 into Step 5 (gitmoji + alignment check are one setup block); merge Step 9.5 into Step 9 confirmation flow.

**[Medium] Lens 1 — Prompt Clarity**
Observation: Step 2 says "Load the project instructions file from your harness's standard locations (earlier files provide defaults, later files override): 1. Global defaults location (if present, per harness mapping) 2. AL profile defaults location (if present, per harness mapping)" — "per harness mapping" is undefined. No fallback if the mapping table isn't available.
Fix: Either inline the three concrete paths (global CLAUDE.md, profile CLAUDE.md, `./CLAUDE.md`) or reference a knowledge file that defines the mapping.

**[Low] Lens 1 — Prompt Clarity**
Observation: `AL_DEV_SHARED_PLUGIN_ROOT` is used in Step 5.5 but never documented as a harness-injected environment variable. Developers reading the skill without harness context won't know its source.
Fix: Add a one-line note: "`AL_DEV_SHARED_PLUGIN_ROOT` is set by the harness to the plugin root directory."

---

### /al-dev-document

**[High] Lens 1 — Prompt Clarity**
Observation: Step 1 reads `.dev/01-requirements.md` and `.dev/02-solution-plan.md`, Step 3 checks `.dev/03-code-review.md` — these are an old sequential naming scheme. All other skills write dated files (`$(date +%Y-%m-%d)-al-dev-interview-requirements.md`, etc.). These files will never be found.
Fix: Replace with glob patterns matching the dated naming convention used by the skills that write them.

**[Medium] Lens 1 — Prompt Clarity**
Observation: Step 2 sets `TEMPLATE_PATH = knowledge/doc-templates/[AUDIENCE].md` but the skill never verifies these template files exist. If absent, the docs-writer has no template to follow.
Fix: Add a check: `ls $AL_DEV_SHARED_PLUGIN_ROOT/knowledge/doc-templates/ 2>/dev/null` and fallback to inline structure if missing.

**[Medium] Lens 2 — Structural Conventions**
Observation: Two conflicting output paths — Step 2 spawn prompt says `docs/Features/[FeatureName]-[AUDIENCE].md`, but the `## Output Files` section at the bottom says `docs/[FeatureName].md`.
Fix: Pick one path and apply it consistently; the audience-suffixed form is more precise.

**[Medium] Lens 1 — Prompt Clarity**
Observation: Step 5 instructs `"Docs-writer, shut down"` — agents in the Agent tool model run to completion and cannot receive follow-up messages. This is a no-op instruction.
Fix: Remove Step 5 entirely; note that the docs-writer agent terminates when it returns its result.

**[Low] Lens 4 — Bloat**
Observation: "How This Command Works (v3.0)" — version label in a heading is historical commentary that belongs in git history.
Fix: Remove the `(v3.0)` suffix.

**[Low] Lens 2 — Structural Conventions**
Observation: The `## Usage` section shows `/document` but the skill's registered name is `/al-dev-document`.
Fix: Update to `/al-dev-document`.

---

### /al-dev-help

**[High] Lens 1 — Prompt Clarity**
Observation: Steps 2B and 2C scan for `.dev/01-requirements.md`, `.dev/02-solution-plan.md`, `.dev/03-code-review.md` — old sequential naming. Dated files written by current skills (e.g., `*-al-dev-interview-requirements.md`) will never be detected, so pipeline state will always show "not found".
Fix: Replace with glob patterns: `ls .dev/*-al-dev-interview-requirements.md`, `ls .dev/*-al-dev-plan-solution-plan.md`, `ls .dev/*-al-dev-develop-code-review.md`.

**[Medium] Lens 3 — Description Drift**
Observation: Step 2A agent table lists `python-script-engineer` — the current plugin registers `al-dev-script-engineer`. Table will mislead users looking to spawn the script engineer.
Fix: Update agent name to `al-dev-script-engineer`.

**[Low] Lens 4 — Bloat**
Observation: The `commands` and `skills` argument modes produce nearly identical tables (same skills listed), creating a distinction without a difference.
Fix: Merge into a single `skills` mode; remove the `commands` alias or have it output a shorter command-only list.

---

### /al-dev-develop

**[High] Lens 4 — Bloat**
Observation: 12+ phases including 1A and 4A sub-phases. Phase 3 spawn prompt, Phase 5 review template, and Phase 9 code review template each exceed 30 lines individually.
Fix: Extract the Phase 9 code review template to `knowledge/code-review-template.md` and reference it inline. Consider extracting Phase 3 spawn prompt to a knowledge file too.

**[Medium] Lens 2 — Structural Conventions**
Observation: Phase numbering mixes integers and letter suffixes (Phase 1, Phase 1A, Phase 2, Phase 4, Phase 4A) — the letter suffix convention is not established by the rest of the plugin's Phase numbering.
Fix: Rename 1A → Phase 1.5 and 4A → Phase 4.5 to match the decimal sub-phase convention used elsewhere (or use consistent note-boxes inside Phase 1/4 with `--autonomous only` guards).

**[Low] Lens 2 — Structural Conventions**
Observation: `argument-hint` shows `[optional: specific module or scope override]` but the description prominently documents `--autonomous` flag — a user reading only the hint wouldn't know about it.
Fix: Update to `[--autonomous] [module or scope override]`.

---

### /al-dev-plan

**[High] Lens 4 — Bloat**
Observation: 11+ phases/steps including decimal sub-phases (0.5, 1.5, 1.5.5). Phase 5 solution plan template and Phase 1.5 external claims table each exceed 30 lines.
Fix: Extract Phase 5 template to `knowledge/solution-plan-template.md`; reference it with a single line.

**[Medium] Lens 2 — Structural Conventions**
Observation: "Step 0: Target Confirmation (Phase 1.5.5)" — a Step inside a Phase inside a sub-Phase. The three nesting levels (Phase / decimal sub-Phase / Step) are unique in the plugin and cognitively heavy.
Fix: Flatten to "Phase 1.5 — Verify External Claims" with "Phase 1.6 — Target Confirmation", preserving the decimal convention already used.

**[Low] Lens 2 — Structural Conventions**
Observation: Phase 5 body says `YYYY-MM-DD-al-dev-plan-solution-plan.md` as a literal string placeholder. Other skills use `$(date +%Y-%m-%d)`. Reader may copy the literal string.
Fix: Replace with `$(date +%Y-%m-%d)-al-dev-plan-solution-plan.md`.

---

### /al-dev-perf

**[High] Lens 4 — Bloat**
Observation: Step 2 spawn prompt is ~55 lines — well above the 30-line ceiling. The P1–P8 anti-pattern descriptions and "Do NOT flag" exclusions are both long and partially duplicate the catalogue defined before the Implementation section.
Fix: Extract the P1–P8 prompt text to `knowledge/perf-anti-patterns-prompt.md` and reference it with one line in the spawn prompt.

**[Low] Lens 2 — Structural Conventions**
Observation: Step "1b" uses a letter suffix — the rest of the skill uses integers. Minor inconsistency.
Fix: Rename to Step 1.5 or fold 1b into Step 1 as a sub-section.

**[Low] Lens 1 — Prompt Clarity**
Observation: The escalation rule in Step 2 states "For any P1–P7 finding" — P8 (Full Table Scan, added later) is not included in the escalation scope, but it warrants the same severity boost in hot paths.
Fix: Update to "For any P1–P8 finding" or add an explicit note for P8.

---

### /al-dev-fix

**[Medium] Lens 1 — Prompt Clarity**
Observation: Spawn instructions use informal agent names — "spawn single al-developer", "spawn solution-architect" — not the actual agent type strings (`al-dev-shared:al-dev-developer`, `al-dev-shared:al-dev-solution-architect`). A reader implementing a new dispatch will use the wrong type.
Fix: Use the fully-qualified agent type names in all spawn instructions.

**[Medium] Lens 2 — Structural Conventions**
Observation: Step numbering uses letter suffixes (Step 2a, Step 2b) — inconsistent with the integer-only or decimal convention used by most other skills.
Fix: Rename to Step 2 (Trivial) and Step 3 (Non-Trivial), or use Step 2 with sub-sections.

**[Low] Lens 1 — Prompt Clarity**
Observation: "Clean up (shut down developer)" and "Clean up (shut down architect, developer)" — agents in the Agent tool model run to completion and cannot be shut down via follow-up message. No-op instructions.
Fix: Remove these cleanup lines.

**[Low] Lens 1 — Prompt Clarity**
Observation: `knowledge/architect-invocation-patterns.md` is referenced for the "Quick Analysis" pattern, then the full pattern is also defined inline. If the knowledge file and inline definition drift, the inline version silently wins.
Fix: Either remove the inline definition and trust the knowledge file, or remove the knowledge file reference and rely on the inline definition.

---

### /al-dev-handoff

**[Medium] Lens 1 — Prompt Clarity**
Observation: Step 0.5 uses `AL_DEV_SHARED_PLUGIN_ROOT` in the alignment script path without any note that it is a harness-injected variable. A developer reading this cold won't know its source.
Fix: Add a one-line note (same fix as for `/al-dev-commit`): "`AL_DEV_SHARED_PLUGIN_ROOT` is set by the harness to the plugin root."

**[Low] Lens 1 — Prompt Clarity**
Observation: Step 2 table shows source file globs truncated with `…` (`$(ls .dev/*-al-dev-ticket-… ...)`) — the truncation is ambiguous and not runnable.
Fix: Show the full glob pattern on one line, or collapse to the pattern `ls .dev/*-al-dev-ticket-ticket-context.md`.

---

### /al-dev-interview

**[Medium] Lens 1 — Prompt Clarity**
Observation: Phase 3 validator uses `$AL_DEV_SHARED_PLUGIN_ROOT` without documenting it as a harness env var. Silent failure if unset (the `[ -f "$VALIDATOR" ]` guard saves it, but the variable source is opaque).
Fix: Add a one-line note that `AL_DEV_SHARED_PLUGIN_ROOT` is harness-injected.

**[Low] Lens 1 — Prompt Clarity**
Observation: Phase 2 GATE says "Only after you have asked questions across all relevant categories AND received answers may you proceed to Phase 3" — this instruction is in the orchestrator's Phase 2 body, addressed to the spawned interview agent, but Phase 3 is in the orchestrator context, not the agent's. The gate is in the right place conceptually but the framing implies the agent controls Phase 3 progression.
Fix: Rephrase to: "The interview agent must complete all categories before signalling completion. Upon agent return, proceed to Phase 3."

---

### /al-dev-investigate

**[Medium] Lens 2 — Structural Conventions**
Observation: Step 4 writes `.dev/$(date +%Y-%m-%d)-al-dev-explore-findings.md` — the `explore` name is carried from `/al-dev-explore`, not this skill. Running both `/al-dev-explore` and `/al-dev-investigate` on the same day will overwrite each other's output.
Fix: Rename output to `.dev/$(date +%Y-%m-%d)-al-dev-investigate-findings.md`.

**[Low] Lens 2 — Structural Conventions**
Observation: Steps are numbered 0, 1, 1.5, 2, 3, 4, 5 — the 1.5 decimal sub-step appears alongside a Step 0, making the ordering inconsistent with the decimal-only convention.
Fix: Renumber as Step 0, Step 1, Step 2 (Regression Timeline), Step 3, Step 4, Step 5, Step 6 for clarity.

**[Low] Lens 1 — Prompt Clarity**
Observation: Step 3 spawns "2 Explore agents in parallel, assigning 2 hypotheses each" — hardcoded for 4 hypotheses. Step 2 says 2–4. If only 2 hypotheses exist, the second agent has no work; if 3, one agent gets 2 and the other gets 1.
Fix: Add a routing note: "If ≤2 hypotheses, spawn 1 agent with all of them."

---

### /al-dev-ticket

**[Medium] Lens 1 — Prompt Clarity**
Observation: Step 3 dispatch prompt body includes the literal string `$(date +%Y-%m-%d)` embedded in the output filename. If the orchestrator passes this as a text string rather than evaluating the shell expression, the agent receives the unexpanded placeholder.
Fix: Evaluate the date expression before constructing the dispatch prompt: `DATE=$(date +%Y-%m-%d)` in step preamble; use `$DATE` in the prompt string.

**[Low] Lens 2 — Structural Conventions**
Observation: Steps are numbered 1, 1S, 2, 3, 4 — the letter suffix `S` (for Search) is not consistent with the integer-or-decimal convention used elsewhere.
Fix: Rename Step 1S to Step 1.5 to match the decimal sub-step convention.

---

### /al-dev-explore

**[Low] Lens 1 — Prompt Clarity**
Observation: Step 5 output example shows `` `.dev/$(date +%Y-%m-%d)-al-dev-explore-findings.md` `` as a literal template string — in the user-facing message this should be the rendered path, not the shell expression.
Fix: Show the rendered date in the example or instruct: "Replace `$(date +%Y-%m-%d)` with today's date in the presented path."

**[Low] Lens 1 — Prompt Clarity**
Observation: Step 4 asks "Update project-context.md to capture them? [Yes/No]" but gives no instruction on WHERE in the file to append or what format to use for the "Recent Discoveries" entry.
Fix: Add: "Append under a `## Recent Discoveries — [date]` section at the end of the file."

---

### /al-dev-lint

**[Low] Lens 3 — Description Drift**
Observation: `description` says "Run ALCops analyzers" — the body runs `al-compile`, not a product called ALCops. Minor brand/implementation mismatch.
Fix: Update to "Run AL compile and auto-fix AL code diagnostics."

---

### /al-dev-release-notes

**[Low] Lens 2 — Structural Conventions**
Observation: Phase 2 prompt uses `{curly-brace}` placeholders (`{app-id}`, `{short-hash}`) for the output filename while all other skills use `[bracket]` placeholders. Inconsistent within the plugin.
Fix: Normalise to `[bracket]` style: `[app-id]`, `[short-hash]`.

**[Low] Lens 2 — Structural Conventions**
Observation: Step "1b" uses a letter suffix — the rest of the skill uses integers.
Fix: Rename to Phase 1.5 to match decimal convention.

---

### /al-dev-support

**[Low] Lens 2 — Structural Conventions**
Observation: Step "1A" uses a letter suffix — consistent within this skill but inconsistent with the decimal convention used elsewhere.
Fix: Rename to Step 1.5 (Branch Auto-Detect).

---
