# Harness Improvement Research

## Research Question

Should `al-dev-shared` add XML tagging to its repo-local self-healing tooling to
improve prompt structure, handoff clarity, and loop correctness?

## Scope And Method

- In scope: repo-local self-healing tooling only, especially prompt
  segmentation, checkpoint semantics, loop-state handoffs, and machine-readable
  orchestration boundaries.
- Compared ecosystems: the live `al-dev-shared` repo, Anthropic prompt
  engineering guidance, and OpenAI prompt and structured-output guidance.
- Recency window: current first-party documentation accessed on 2026-06-14.
- Exclusions: shared-profile projection changes, broad harness audits, AL app
  workflows, and non-self-healing maintainer tooling.
- Method:
  - established a protected-surface baseline for the repo
  - searched the live repo for existing structured contracts and XML-related
    patterns
  - gathered first-party vendor evidence on XML tags, delimiters, and
    schema-enforced outputs
  - compared those patterns with the current self-healing implementation

## Live Repository Baseline

Existing repo coverage is `partial`, not `none found`.

- `.claude/knowledge/health-loop-state-contract.md` already defines a durable
  YAML schema for `.dev/health-loop-state.md`, including `next_command`,
  `next_inputs`, and `fresh_session_recommended`. This already solves the main
  cross-session state problem with a committed on-disk contract.
- `.claude/knowledge/skill-workflow-contract.md` already defines a frontmatter
  schema for workflow metadata used by repo-local tooling.
- `profile-al-dev-shared/knowledge/workflow-resilience.md` already treats
  `.dev/progress.md` as the authoritative checkpoint and requires overwrite,
  resume prompts, and explicit next-step tracking.
- `profile-al-dev-shared/knowledge/artifact-contracts.md` already defines exact
  handoff artifacts and forbids guessing when required evidence is missing.
- `profile-al-dev-shared/knowledge/script-engineer-conventions.md` already
  prefers machine-parseable structured output, explicitly favoring JSON first
  and typed/schema-validated boundaries over prose.

Inference: the current repo’s self-healing correctness model is centered on
durable state files and explicit contracts, not on prompt-formatting alone.

## Evidence-Backed Findings

1. Anthropic explicitly recommends XML tags for complex prompts.
   - Anthropic’s current prompting guide says XML tags help parse prompts that
     mix instructions, context, examples, and variable inputs, and recommends
     consistent tag names plus nesting where the content has hierarchy.
   - Source:
     `https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices#structure-prompts-with-xml-tags`

2. Anthropic also recommends XML structure for long multi-document inputs.
   - The same guide recommends wrapping multiple documents and their metadata in
     XML tags for clarity in long-context prompting.
   - Source:
     `https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices#structure-prompts-with-xml-tags`

3. OpenAI treats XML as one useful delimiter, not as the main reliability
   mechanism.
   - OpenAI’s reasoning guidance says to use delimiters such as markdown, XML
     tags, and section titles to separate distinct input parts.
   - Source:
     `https://developers.openai.com/api/docs/guides/reasoning-best-practices#how-to-prompt-reasoning-models-effectively`

4. OpenAI’s stronger recommendation for reliable machine-readable output is
   schema-enforced structured output.
   - OpenAI’s Structured Outputs guide says JSON-schema-constrained output gives
     reliable type safety, explicit refusals, and simpler prompting. It also
     recommends Structured Outputs over JSON mode when possible.
   - Source:
     `https://developers.openai.com/api/docs/guides/structured-outputs`

5. The repo’s own conventions align more closely with schema-backed output than
   with XML-first prompting.
   - `script-engineer-conventions.md` explicitly says scripts should emit
     machine-parseable output and prefer JSON first, with typed/schema-validated
     boundaries.
   - Source:
     local repo evidence only.

6. The loop-state contract is enforced by prose plus a static-text guard, not by
   a content validator.
   - `scripts/check_health_loop_handoffs.py` is, by its own docstring, a STATIC
     TEXT guard: it counts breadcrumb-path references per loop skill and checks
     the writing-plans override position. It states plainly: “A PASS means the
     wiring text is in place; confirm actual loop closure in a live run.”
   - Nothing validates the *content* of `.dev/health-loop-state.md` against the
     schema in `health-loop-state-contract.md` — required fields present, a
     `next_command` valid against the lifecycle table, a boolean
     `fresh_session_recommended`. The contract is prose-specified but not
     machine-checked.
   - Source:
     local repo evidence only.

Inference: XML tags are most justified when the failure mode is prompt-section
confusion inside one model call. They are less justified when the dominant
failure mode is stale state, missing handoff artifacts, or missing validation.
The one concrete, repo-aligned improvement this run surfaced is a content
validator for `.dev/health-loop-state.md` — independent of XML and consistent
with the repo’s JSON-first convention.

## Repository Comparison

| Pattern | External Evidence | Existing Repo Coverage | Gap | Portability |
| --- | --- | --- | --- | --- |
| XML tags for separating instructions, context, examples, and inputs inside one prompt | Anthropic recommends this directly; OpenAI allows XML as a useful delimiter | Partial: some repo prompts use explicit sections and schemas, but no consistent XML convention for prompt segments | Small gap for prompt readability only | repo-local |
| Nested XML for long multi-document context | Anthropic recommends this for large document inputs | Low coverage in self-healing loop specifically | Limited relevance; self-healing loop is more stateful than document-centric | reject |
| Schema-enforced machine-readable output | OpenAI recommends JSON-schema-enforced outputs for reliable type safety; repo already prefers JSON-first structured output | Strong coverage in repo conventions, moderate coverage in live self-healing artifacts | Main gap is validation and stricter enforcement, not lack of XML | repo-local |
| Durable on-disk checkpoint and handoff contracts | Repo already does this with `.dev/progress.md`, `.dev/health-loop-state.md`, and artifact contracts | Complete enough in design, partial in enforcement discipline | The improvement target is stronger validation and narrower contracts | repo-local |

## Candidate Patterns

1. Use XML tags only in a small number of high-complexity prompts.
   - Evidence: Anthropic recommends XML tags for mixed-content prompts, and
     OpenAI accepts XML as a clear delimiter.
   - Likely surface: repo-local self-healing prompts that combine instructions,
     findings, constraints, and expected return blocks in one call.
   - Portability: `repo-local`
   - Risk reduced: prompt-section confusion in large mixed-context prompts.

2. Strengthen schema-backed artifacts instead of introducing XML into durable
   state files.
   - Evidence: OpenAI recommends schema-enforced structured outputs for
     reliability, and the repo already prefers JSON-first structured protocols.
   - Likely surface: `.dev/` checkpoint artifacts, validator scripts, and
     health-loop contract checks.
   - Portability: `repo-local`
   - Risk reduced: stale-state misuse, missing fields, and silent handoff drift.

3. Add validation for existing self-healing contracts before adding any new
   prompt syntax convention.
   - Evidence: repo artifact contracts and workflow-resilience guidance already
     treat missing evidence as a stop condition; this is closer to the current
     failure model than delimiter choice.
   - Likely surface: a content validator for the `.dev/health-loop-state.md`
     breadcrumb that checks it against the schema in
     `health-loop-state-contract.md` (required fields, `next_command` valid per
     the lifecycle table, boolean `fresh_session_recommended`) — sitting
     alongside the existing static-text `scripts/check_health_loop_handoffs.py`,
     which only checks wiring text, not breadcrumb content.
   - Portability: `repo-local`
   - Risk reduced: false-complete claims and loop-closure regressions.

## Rejected Or Non-Portable Patterns

1. Repo-wide XML-tagging migration across all self-healing prompts.
   - Rejected because the evidence does not show XML as a universal best
     practice for all harnessed workflows. OpenAI treats it as one delimiter
     option, not the primary reliability mechanism.

2. Replacing existing YAML/Markdown checkpoint artifacts with XML files.
   - Rejected because the repo already has established contracts around current
     artifact formats, and the local conventions prefer JSON-first
     machine-parseable protocols when stronger structure is needed.

3. Treating XML tags as a substitute for validation.
   - Rejected because the repo’s actual failure modes are more about enforcing
     state and handoff contracts than about nesting syntax alone.

## Evidence Ledger

| ID | Claim | Source | Source Type | Published or Updated | Accessed | Confidence |
| --- | --- | --- | --- | --- | --- | --- |
| E1 | Anthropic recommends XML tags for complex prompts that mix instructions, context, examples, and inputs | `https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices#structure-prompts-with-xml-tags` | first-party vendor docs | not stated on page | 2026-06-14 | high |
| E2 | Anthropic recommends XML structure for long multi-document context with nested metadata | `https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices#structure-prompts-with-xml-tags` | first-party vendor docs | not stated on page | 2026-06-14 | high |
| E3 | OpenAI recommends delimiters such as markdown, XML tags, and section titles for clarity | `https://developers.openai.com/api/docs/guides/reasoning-best-practices#how-to-prompt-reasoning-models-effectively` | first-party vendor docs | not stated on page | 2026-06-14 | high |
| E4 | OpenAI recommends Structured Outputs with JSON Schema for reliable type-safe machine-readable output | `https://developers.openai.com/api/docs/guides/structured-outputs` | first-party vendor docs | not stated on page | 2026-06-14 | high |
| E5 | The repo itself prefers machine-parseable structured protocol output, preferably JSON first | `profile-al-dev-shared/knowledge/script-engineer-conventions.md` | live repo evidence | current repo file | 2026-06-14 | high |
| E6 | The self-healing loop already has explicit durable state and handoff contracts | `.claude/knowledge/health-loop-state-contract.md`, `.claude/knowledge/skill-workflow-contract.md`, `profile-al-dev-shared/knowledge/workflow-resilience.md`, `profile-al-dev-shared/knowledge/artifact-contracts.md` | live repo evidence | current repo files | 2026-06-14 | high |
| E7 | The health-loop handoff guard is a static-text check; no validator parses the `.dev/health-loop-state.md` breadcrumb against its schema | `scripts/check_health_loop_handoffs.py`, `.claude/knowledge/health-loop-state-contract.md` | live repo evidence | current repo files | 2026-06-14 | high |

## Gaps And Uncertainty

- No first-party source in this run claimed that XML tags alone improve
  stateful agent orchestration correctness across sessions.
- The vendor guidance is mostly about prompt clarity inside a model call, not
  about durable workflow artifacts or repo-local self-healing loops.
- This assessment is strongest for the current self-healing tooling shape in
  `al-dev-shared`. A different conclusion could make sense if you were building
  a new prompt-heavy orchestrator with very large mixed-content prompts and weak
  artifact validation.

## Recommended Next Step

No XML action. The evidence does not justify an XML convention for the
self-healing tooling; the dominant failure mode here is stale state and missing
validation, not prompt-section confusion inside one model call.

Separate lever (candidate for separate scoping, not an XML change): add a content
validator for `.dev/health-loop-state.md` that checks it against the schema in
`health-loop-state-contract.md` — required fields present, `next_command` valid
against the lifecycle table, `fresh_session_recommended` boolean. Today the only
guard, `scripts/check_health_loop_handoffs.py`, is static-text-only by its own
docstring and never parses the breadcrumb. This is recorded here as a finding,
not auto-actioned.
