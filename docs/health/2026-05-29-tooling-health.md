# Tooling Health — 2026-05-29

## Summary

| Severity | Design | Quality | Naming | Total |
|----------|--------|---------|--------|-------|
| High     | 2      | 12      | 0      | 14    |
| Medium   | 8      | 16      | 0      | 24    |
| Low      | 7      | 9       | 0      | 16    |

Top 5 ranked actions:
1. **Trim Glob from 20 lens agents** — All 20 have `Glob` declared but never used in body; agents receive explicit file paths via dispatch prompt (Tool Hygiene, Low, systemic)
2. **plan-map-changes clarity & bloat** — High: `$ARGUMENTS` undefined, Phase 2 exceeds 30 lines, incomplete conditional for Merge check, missing $FILTER_TYPE definition (Clarity + Bloat, High)
3. **Merge near-duplicate pairs** — `analyze-agent-design` + `analyze-skill-design` → `/analyze-design --type`; `review-agent-map` + `review-skill-map` → `/review-map --type` (Near-Duplicates, Medium)
4. **audit-quality Phase 4 bloat + pseudo-code** — 90-line Phase 4 step with repetitive Full/Scoped blocks; pseudo-code Python at lines 32–49 with no indication of execution intent (Bloat + Clarity, High)
5. **Extract lens invocation patterns to knowledge/** — design-agent-lens-* dispatch context diverges between `/analyze-agent-design` (5 fields) and `/plugin-health` (10 fields); same gap for design-skill-lens-* (Shared Backbone, Medium)

Implementation context:

- The ranking above mixes correctness, leverage, and hygiene. For execution, prioritize the items that can block or mislead future work first, then do the broad cleanup.
- `plan-map-changes` is the first fix to land. The real problem is not just length: the skill references undefined state (`$ARGUMENTS`, `$FILTER_TYPE`) and has an incomplete Merge branch, so implementation should focus on making the control flow explicit and mechanically safe before any consolidation work.
- `audit-quality` comes next. The major issue is reader trust: the report mixes pseudo-code and prose without stating whether the block is illustrative or executable. Split the oversized report phase while also making the code-intent boundary explicit.
- The `Glob` trim is low risk and wide impact, but it is still a hygiene pass. Remove only the unused `Glob` declarations; keep the one lens that genuinely relies on pattern search.
- The lens-invocation extraction is an infrastructure fix, not a behavior fix. Capture the exact context contract in `knowledge/lens-invocation-patterns.md`, then update the dispatchers so they pass only the fields each lens type actually consumes.
- The near-duplicate merges should be treated as candidates, not automatic refactors. Confirm that the paired skills are truly equivalent in output shape and caller expectations before collapsing them behind a type flag.

---

## Design suggestions

### Trim — Glob unused across all lens agents

- **All 20 lens agents** | Low | `Glob` declared in `tools` frontmatter but the body never uses it — agents receive an explicit file list in the dispatch prompt and have no need for pattern-based discovery | Remove `Glob` from every lens agent's `tools` list; only `design-agent-lens-caller-alignment` keeps `Grep` as it searches skill files for invocation patterns

### Trim — naming-convention-lens is single-use with documented contract

- **naming-convention-lens** | Low | Called only by `/plugin-health` (not by `/analyze-*` skills), meaning it has usage-count 1; however the body has documented `## Inputs` / `## Outputs` tables so it fails the third inline criterion — retain as a maintained lens agent | No action required unless the contract tables are removed; inline only if it becomes genuinely trivial

### Atomise — analyze-agent-design and analyze-skill-design at 9 phases (limit 8)

- **analyze-agent-design** | High | 9 phases exceeding the 8-phase guideline; Phases 1–2 (map discovery, context extraction) and Phases 3–9 (analysis, suggestion drafting, diagram dispatch, output) form two separable concerns with a clean handoff point | Consolidate Phases 6–9 into a single "Finalize" phase (complete inventory, dispatch diagram generator, write Observations, present); reduces to 6 phases with no logic loss
- **analyze-skill-design** | High | Same pattern as analyze-agent-design — identical 9-phase structure, same two-concern split | Same fix: collapse Phases 6–9 into a single Finalize phase

### Merge — near-duplicate skill pairs

- **analyze-agent-design + analyze-skill-design** | Medium | Both dispatch 5 parallel design lenses to different artifact types (agents vs. skills), share identical Phase 1 context-build and Phase 2 dispatch logic, and differ only in target map file and lens set; could unify as `/analyze-design --type agent|skill` | Create `/analyze-design` with `--type` flag; archive both current skills. Trade-off: single entry point reduces maintenance; `--type` makes the agent/skill distinction explicit to callers
- **review-agent-map + review-skill-map** | Medium | Both scan artifact directories, extract profiles, cross-reference callers, compare against documentation maps, and update them — identical 7-phase structure differing only in artifact type (agents vs. skills) | Create `/review-map --type agent|skill`; archive both current skills. Same trade-off as above

### Connect — extract lens invocation patterns to knowledge/

- **design-agent-lens-* (5 lenses)** | Medium | `/analyze-agent-design` dispatches these with 5 context fields (`tool_inventory`, `model_assignments`, `caller_map`, `single_use_agents`, `already_inline_candidates`); `/plugin-health` dispatches the same lenses with all 10 context fields — the extra 5 are inert for agent-design lenses but maintenance burden and drift risk | Write `knowledge/lens-invocation-patterns.md` documenting which context fields each lens type actually requires; update `/plugin-health` Phase 2.1 to pass only required fields per lens class
- **design-skill-lens-* (5 lenses)** | Medium | Same pattern: `/analyze-skill-design` and `/plugin-health` Phase 2.1 both dispatch these with rich context; dispatch prompt template is not canonically documented anywhere | Include skill-lens invocation contract in the same `knowledge/lens-invocation-patterns.md` file

### Extend — audit outputs are orphaned; no skill consumes them

- **audit-quality + audit-knowledge-quality outputs** | Medium | Both skills write findings to `docs/` (skill-quality.md, agent-quality.md, knowledge-quality.md) but neither output is consumed by a downstream skill; the audit→action loop is manual — users read reports, then separately invoke `/plan-map-changes` without formal handoff | Create `/audit-remediate` that reads the latest audit findings by severity, rubber-ducks each High finding against the live codebase, and writes a focused remediation plan to `docs/superpowers/plans/YYYY-MM-DD-audit-remediation.md`; limit initial scope to High findings only

### Atomise — plugin-health Phase 6 (graph refresh) is separable

- **plugin-health** | Medium | Phase 6 runs `generate-plugin-graph.py` after dossier write; this is separable from the lens dispatch pipeline (Phases 1–5) and blocks dossier delivery when the graph script is slow or absent | Consider moving graph refresh to a post-dossier hook or optional `/plugin-health --refresh-graph` flag; no functional impact on finding quality

### Caller Alignment — design lenses have underdocumented Inputs tables

- **design-agent-lens-caller-alignment, tool-hygiene, usage-patterns, model-fit** | Medium | Inputs tables document fewer context fields than callers actually pass — e.g., caller-alignment documents only `file_list` + `caller_map` but receives 5 fields from `/analyze-agent-design` and 10 from `/plugin-health` | Update each lens's Inputs table to list all fields passed in dispatch prompts; mark which are required vs. available-but-unused
- **design-skill-lens-complexity, handoff-gaps, near-duplicates, preplanning, shared-backbone** | Medium | Same gap for skill design lenses — Inputs tables understate what callers actually provide | Same fix: expand Inputs tables; note required vs. supplementary fields
- **quality-agent-lens-* and quality-skill-lens-*** | Low | Quality lenses document only `file_list` in Inputs; dispatchers pass additional context that quality lenses don't use but should acknowledge | Add a note row: "Additional context structures passed by dispatcher — not required by this lens"

### Pre-planning — audit skills not positioned in the documented tooling flow

- **audit-quality** | Low | Writes quality findings that could inform `/plan-map-changes` but is not documented as a pre-planning input to that skill | Optional: document in `/plan-map-changes` Phase 1 that running `/audit-quality --type skill` and `--type agent` first provides additional context for quality-driven plan items
- **audit-knowledge-quality** | Low | Not positioned in the documented tooling flow at all; knowledge quality issues can block architectural changes but the skill is discoverable only by name | Add a sentence to `/plan-map-changes` Phase 1 noting this as an optional pre-planning step when the plan includes Promote or knowledge-document changes

---

## Quality findings

### Bloat

- **analyze-agent-design** | High | 9 top-level phases (limit 8); same two-concern split as noted in Design Atomise suggestion | Collapse Phases 6–9 into one "Finalize" phase
- **analyze-skill-design** | High | 9 top-level phases (limit 8); identical structure to analyze-agent-design | Same fix
- **audit-quality** | High | Phase 4 (Report) contains ~90 lines — three times the 30-line guideline — with heavily duplicated Full-run and Scoped-run sub-blocks | Split Phase 4 into distinct "Full run report" and "Scoped run report" phases; extract shared report template into a referenced block
- **plan-map-changes** | High | Phase 2 (Rubber Duck) exceeds 30 lines with 9 type-specific check sections each ~8–10 lines of near-identical pattern (read X in full, list/quote usage, confirm existence) | Extract the per-type checks into a lookup table in `knowledge/map-change-rubber-duck-checks.md`; Phase 2 becomes a loop over the table rather than 9 inline blocks
- **plugin-health** | High | Phase 2 aggregated (sub-phases 2.0 + 2.1) exceeds 30 lines; context-extraction and lens-dispatch logic are entangled in one large phase | Consolidate Phase 2.0 and Phase 2.1 into "Prepare and dispatch"; extract dispatch prompt template to a reusable reference block
- **review-skill-map** | High | Phase 7 (Detect Move Candidates) contains ~60 lines with nested detection signals, output templates, and candidate write logic | Split Phase 7 into "Detect candidates" (signals + decision) and a commit step; move output formatting to a reusable block
- **audit-quality** | Medium | Repetitive instruction blocks between Full-run and Scoped-run variants in Phase 4 (~70 lines of duplication) | Extract shared report structure to a reusable template definition; parameterize audit_type and object_name
- **plan-map-changes** | Medium | Highly repetitive check patterns across all 9 suggestion types (Connect, Merge, Promote, Move, Extend, Trim, Remodel, Split, Inline, Align) | Same fix as High finding above: extract to knowledge/ lookup table
- **plugin-health** | Medium | Repetitive dispatch prompt structure and dossier template appear inline multiple times | Extract to template blocks; reference by name

### Clarity

- **audit-quality** | High | Pseudo-code block at lines 32–49 presents Python argparse-style logic with no indication of whether it should execute or is illustrative; `args` is referenced before being confirmed populated | Add a comment: "Reference only — this logic is embedded in the skill's runtime; do not execute directly" OR extract to a runnable script at `scripts/audit-quality-args.py`
- **plan-map-changes** | High | `$ARGUMENTS` referenced in Phase 2 without being defined or populated; no instruction in Phase 1 for how to capture the user's argument into this variable | Define in Phase 1: "If the user passed a suggestion type (`connect`, `trim`, etc.), capture it as `FILTER_TYPE`; if none, set to `all`"; replace `$ARGUMENTS` with `$FILTER_TYPE` throughout
- **plan-map-changes** | High | Phase 2 Merge check: "If skill B has a validator script, confirm it exists with `ls`" — no instruction for what to do when the script is absent | Add: "If the validator script is absent, note in the rubber-duck record: 'Scope gap: validator missing; plan must include manual validation or script creation'"
- **review-skill-map** | High | Phase 6 grep for archived skills uses a hardcoded list `(al-dev-test|al-dev-unit-test|...)` — will silently miss newly archived skills | Replace with dynamic discovery: `ls profile-al-dev-shared/archived/skills/` to build the grep pattern at runtime
- **audit-knowledge-quality** | High | Phase 2 dispatches parallel agents but the todo naming convention and exact location (`.dev/` path) are never defined; `superpowers:dispatching-parallel-agents` invocation contract not documented | Specify todo naming: `knowledge-audit-[filename]`; document the argument contract for the parallel dispatch (file paths, format, return structure)
- **quality-agent-lens-structure** | High | Frontmatter check states "must not contain skill-only fields (`argument-hint`, `triggers`)" but doesn't define whether ALL non-listed fields are forbidden or whether agent-only fields appearing in skills (e.g., `model` in a skill) are also in scope | Add: "Agent frontmatter allowed fields: `name`, `description` (single sentence), `model`, `tools`; skill frontmatter allowed fields: `name`, `description`, `argument-hint`; no other fields permitted"
- **design-agent-lens-caller-alignment** | Medium | "compares documented Inputs/Outputs against how spawning skills actually invoke each agent" — no operative definition of mismatch threshold (how different is different enough?) | Clarify: "Align candidate = table contradicts caller OR table says '(none)' but caller passes structured context blocks"
- **design-agent-lens-tool-hygiene** | Medium | "Any tool listed in frontmatter with no corresponding usage verb or code block in body" — ambiguous whether tool name must appear literally or just be logically invoked | Clarify: "Tool listed in frontmatter but never invoked by any instruction in body — check for tool name in code blocks, explicit invocation steps, or references to tool output"
- **design-agent-lens-usage-patterns** | Medium | Inline criterion 2 "fewer than 15 lines" does not define what counts as a line (frontmatter? blank lines? headers?) | Specify: "fewer than 15 lines of system prompt body (everything after closing `---` of frontmatter, excluding blank lines and section headers)"
- **design-skill-lens-handoff-gaps** | Medium | "commonly useful for a task not yet in the plugin" — vague; contradicts "well-established chain" (if established, why is the next step missing?) | Clarify: "Established chain = 3+ skills connected sequentially; next-step candidate = obvious downstream consumer serving a frequent user request not yet implemented"
- **design-skill-lens-preplanning** | Medium | Instruction to check for "dashed tributary arrow (`-.->`) vs. main-spine node" assumes Mermaid familiarity without defining the distinction operationally | Add: "Tributary = skill shown with dashed arrow (`-.->`), optional entry point; main-spine = solid arrow (`-->`), sequential step in critical path"
- **design-skill-lens-shared-backbone** | Medium | "Identical patterns" subpoints lack definition of "same" — byte-for-byte identity, semantic equivalence, or parameterized equivalence? | Clarify: "Identical = same agent name, same context field names, same output file names; variable placeholders allowed but no semantic rewording"
- **naming-convention-lens** | Medium | "A documented output path that violates either pattern" — "either pattern" is ambiguous (living docs pattern OR dated artifact pattern) | Clarify: "any output path that fails to match its applicable pattern (living docs or dated artifact, whichever applies) is a Medium finding"
- **quality-skill-lens-structure** | Medium | "argument-hint is present when body references optional argument (look for `If an argument was passed` or `[arg]` patterns)" — two different patterns with no definition of which or both to match | Clarify: "look for any of: 'if an argument was passed', `[arg]` in headers, 'optional argument', `${arg}` variable references; any match → `argument-hint` required"
- **review-agent-map** | Medium | "Union the file lists from both passes" — no deduplication or ordering rule | Specify: "Union, remove duplicates, extract skill directory names, sort alphabetically"
- **review-skill-map** | Medium | Phase 2: "Count top-level phases" — no rule for whether `### Phase N: Substep` counts separately | Specify: "Count only `## Phase N` headers; ignore `### Phase N: ...` subsections (they belong to their parent phase)"
- **plugin-health** | Medium | "`--dimension all` means" — never defined what "all" encompasses | Define: "`--dimension all` dispatches: design (5 lenses) + quality (5 lenses) + naming (1 lens) per object type"
- **plugin-health** | Medium | Phase 3 "malformed" block undefined — is a correct-heading zero-finding block malformed? | Define: "Malformed = block doesn't start with `### [Lens Name] Findings` heading OR contains zero lines after correct heading is absent; zero findings with correct heading = valid"

### Structure

- **align-harness-repos** | Medium | `argument-hint: ""` is an empty string rather than omitted or populated with a meaningful hint | Remove the empty field or replace with `argument-hint: "[no arguments]"` if none accepted
- **audit-knowledge-quality** | Medium | Missing `argument-hint` in frontmatter; body has optional path argument pattern but frontmatter doesn't declare it | Add `argument-hint: "[path/to/file.md]"` to frontmatter
- **All 10 skills** | Low | Code blocks throughout are missing language tags (`bash`, `yaml`, `python`, etc.) — systematic across all skill files | Add language tags: `bash` to all shell command blocks; `yaml` to YAML examples; `python` to Python snippets

### Description

- **analyze-agent-design** | Medium | Description promises "Trim / Remodel / Split / Inline / Align suggestions" but omits diagram generation (Phase 7 writes `docs/al-dev-workflow-diagrams.md`) as an output | Add: "Also regenerates workflow diagram to `docs/al-dev-workflow-diagrams.md`"
- **analyze-skill-design** | Medium | Description omits "Extend" as a fifth suggestion type (present in Phase 5 templates); also omits diagram output | Add "Extend" to suggestion type list; add diagram output mention
- **audit-knowledge-quality** | Medium | Description says "audit knowledge files for stub sections" but omits: (a) output file `docs/al-dev-knowledge-quality.md`, (b) that the skill dispatches parallel agents in Phase 2, (c) that it offers targeted fixes in Phase 4 | Expand description to include output file name and the agent-dispatch + fix-offer steps
- **audit-quality** | Medium | Description says "Reads each agent/skill .md directly and writes findings" but omits the core action: dispatching five parallel lens agents | Add "Dispatches five parallel lens agents" as the primary action verb
- **plan-map-changes** | Medium | Description says "rubber-ducks suggestions before any plan is written" but omits the output file path (`docs/superpowers/plans/YYYY-MM-DD-plugin-map-<label>.md`) | Add "writes plan to `docs/superpowers/plans/`" to description
- **plugin-health** | Medium | Description omits the dependency graph refresh (Phase 6 writes `docs/al-dev-plugin-graph.md`) | Add "also regenerates dependency graph to `docs/al-dev-plugin-graph.md`" to description
- **review-agent-map** | Medium | Description focuses on accuracy verification but omits Phase 7 inline-candidate detection, which appends strategic findings to the Observations section | Clarify that the skill also detects and writes inline candidates
- **review-skill-map** | Medium | Same pattern: description omits Phase 7 Move Candidate detection | Clarify that the skill also detects and writes Move candidates

### Name Fit

- **audit-quality** | High | Name implies a unified quality audit but requires `--type agent|skill` — a caller invoking `/audit-quality` without arguments gets an ambiguous entry point; name does not communicate the mandatory type parameter | Add clear `--type` guidance in description frontmatter; or rename to make type scope visible (e.g., note: "use `--type agent` or `--type skill`")
- **align-harness-repos** | Medium | Name "align" implies two-way coordination between repositories; actual scope is one-directional token validation and remediation | Rename to `validate-harness-neutrality` to match the Python script name and the actual action verb
- **plan-map-changes** | Medium | Name implies the skill plans changes to maps; actual role is rubber-ducking and validating suggestions already written by other skills — it consumes, not creates, suggestions | Rename to `validate-map-suggestions` or `rubber-duck-map-suggestions` to reflect the verification role
- **design-skill-lens-preplanning** | Low | Filename "preplanning" is vaguer than the formal lens title "Pre-planning and Brainstorming Skills" in the body | Rename to `design-skill-lens-prebrainstorm` or align body title to match filename

---

## Naming violations

_No issues found._ (naming-convention-lens checked all 21 agents and 10 skills against `docs/al-dev-naming-convention.md`)

> Note: `quality-agent-lens-structure` flagged missing `al-dev-` prefixes on all lens agents. This finding is overridden by the authoritative `naming-convention-lens` result. The convention doc permits the `{design|quality}-{agent|skill}-lens-{aspect}` naming pattern without an `al-dev-` prefix for tooling lens agents.

---

## Lens notes

All 21 lenses returned valid findings blocks. No `lens <name>: no result` failures.
