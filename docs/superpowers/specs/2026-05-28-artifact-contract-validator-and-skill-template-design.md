# Design: Artifact-Contract Conformance Validator and Skill Scaffold Template

**Date:** 2026-05-28
**Goal:** Lock in the artifact-contract structure that landed earlier today by adding a structural sensor (validator) and lowering the cost of future compliance (template)
**Scope:** Two paired, bounded improvements to `profile-al-dev-shared` maintainer tooling
**Effort:** ~120 minutes total

---

## Background

Earlier today the repository shipped:

- `profile-al-dev-shared/knowledge/artifact-contracts.md` — declares required inputs, durable outputs, resume read-order, handoff artefacts, and success evidence per core skill
- Cross-references and final-gate wording in `al-dev-plan`, `al-dev-develop`, `al-dev-review-develop`, `al-dev-fix`, `al-dev-commit`, `al-dev-lint`
- A canonical example bundle under `docs/example-runs/al-dev-core/`
- A `harness-coverage-model.md` row mapping behaviour → guide → sensor → enforcement strength

The structural rule is now documented, but nothing prevents drift between the matrix and the skill bodies, and there is no template that bakes the structure into new skills written tomorrow. This design closes both gaps using two reinforcing controls.

The article basis is explicit:

- Osmani — *Agent Harness Engineering* — the **Ratchet Principle**: every documented rule eventually needs a sensor that promotes it from `guide only` to `guide + blocking enforcement`
- Fowler — *Harness Engineering* — **architecture-fitness harness** (ArchUnit-style structural tests) and **topology standardization** (templates for repeated structural patterns)

Both controls live in repo-local maintainer tooling, not in the distributed shared surface. They modify nothing under `profile-al-dev-shared/skills/` or `profile-al-dev-shared/agents/`.

---

## Existing Coverage Reviewed

The following recently-shipped designs were reviewed to avoid duplication:

- `docs/superpowers/specs/2026-05-28-shared-artifact-contracts-and-gates-design.md` — produced the artifact contract document and final-gate wording
- `docs/superpowers/specs/2026-05-28-profile-al-dev-shared-hybrid-improvements.md` — produced the pre-commit compile gate, investigation tightening, intent-preflight completion
- `docs/superpowers/specs/2026-05-28-harness-coverage-model-design.md` — produced the coverage table this design will update

Already in place:

- `scripts/validate_harness_neutrality.py` — neutrality sensor
- `scripts/validate-lens-agents.py` — agent structural sensor
- `scripts/validate-knowledge-quality.py` — knowledge sensor
- `scripts/tests/test_validate_harness_neutrality.py` — unittest harness

This design adds a fourth validator alongside the existing three, using the same conventions.

---

## Problem Statement

Two narrow gaps remain after today's work:

1. **No structural test enforces the artifact contract.** The matrix in `artifact-contracts.md` can disagree with skill bodies without any automated signal. The covered skills can each drift independently. New skill bodies added to the matrix can omit the final-gate rule entirely.
2. **No template exists for authoring a new skill.** A new skill is currently written by copy-pasting an arbitrary existing one, which means the artifact-contract structure has no default path of least resistance. Drift will compound as new skills are added.

These gaps are bounded, observable, and addressable without changing distributed behaviour.

---

## Recommended Design

Implement two reinforcing controls:

| Change | Type | Detects | Prevents |
|---|---|---|---|
| **A. Artifact-contract conformance validator** | New maintainer script + test | Drift between `artifact-contracts.md` and the cross-referencing skills | Silent regression of the just-shipped contract structure |
| **C. Skill scaffold template** | New repo-local templates directory | n/a | Future skills bypassing the contract structure at authoring time |

Why both: A is the sensor after the fact; C is the guide before the fact. Both reference the same source of truth (`artifact-contracts.md`), so updating the contract is the single signal to update both.

---

## Change A: Artifact-Contract Conformance Validator

### Files

- `scripts/validate_artifact_contracts.py` (new)
- `scripts/tests/test_validate_artifact_contracts.py` (new)

### What it parses

The validator reads `profile-al-dev-shared/knowledge/artifact-contracts.md` and extracts each row of the contract matrix. The expected columns are:

- `Skill` — the skill name (e.g. `al-dev-fix`)
- `Required inputs`
- `Durable outputs`
- `Resume read order`
- `Handoff artifact`
- `Success evidence` — the named artefact, log, or review result

### Conformance rules

Each rule is independent and reports its own failures. Exit code is non-zero if any rule fails.

1. **Row resolution.** Every `Skill` value resolves to an existing `profile-al-dev-shared/skills/<name>/SKILL.md`.
2. **Cross-reference present.** Each such SKILL.md contains a literal reference to `knowledge/artifact-contracts.md` (substring match on the file path).
3. **Final-gate rule present.** Each such SKILL.md contains a recognisable final-gate phrase. The canonical phrase from today's design is `success evidence named in` — this is the locked match string for the validator.
4. **Success-evidence path alignment.** Each row's `Success evidence` value names a path or file class (for example `.dev/compile-errors.log`, `.dev/al-dev-develop-code-review.md`). The validator extracts path-like tokens and checks that at least one of them appears in the corresponding SKILL.md body. Match is permissive (substring + path normalisation) so that wording drift on prose around the path does not trigger a failure.
5. **No orphan references.** Any SKILL.md under `profile-al-dev-shared/skills/` that references `knowledge/artifact-contracts.md` must appear as a row in the matrix. Catches the case where a skill claims to honour the contract but was never added to the table.

### Output shape

The validator emits agent-actionable messages. Each violation names the file, the rule, and the fix.

```text
profile-al-dev-shared/skills/al-dev-fix/SKILL.md
  rule: artifact-contract-cross-reference
  issue: contract row exists in artifact-contracts.md but body has no reference to knowledge/artifact-contracts.md
  fix: add the standard cross-reference block under the intent-preflight section

profile-al-dev-shared/knowledge/artifact-contracts.md
  rule: success-evidence-alignment
  issue: row al-dev-lint names success evidence ".dev/al-dev-lint-lint-report.md" but skill body never references it
  fix: either update the row to match the skill body, or update the skill body to name the artefact
```

Successful runs print a single line: `OK: N skills conform to artifact-contracts.md`.

### Test coverage

`scripts/tests/test_validate_artifact_contracts.py` follows the existing `test_validate_harness_neutrality.py` pattern. Tests:

1. **Happy path** — fixture matrix + matching skill stubs → exit 0.
2. **Missing cross-reference** — fixture skill body lacks the `knowledge/artifact-contracts.md` reference → exit 1 with rule 2 violation.
3. **Missing final-gate rule** — fixture skill body lacks the canonical phrase → exit 1 with rule 3 violation.
4. **Path mismatch** — fixture row names a success-evidence path the body never mentions → exit 1 with rule 4 violation.
5. **Orphan reference** — fixture skill body references the contract doc but is not in the matrix → exit 1 with rule 5 violation.
6. **Unresolved row** — fixture row names a skill whose SKILL.md does not exist → exit 1 with rule 1 violation.

Tests use a `tmp_path` fixtures directory so the live `profile-al-dev-shared/` tree is never mutated.

### Integration

1. Add to repo `CLAUDE.md` under `## Development Commands → Validation`:

   ```bash
   python3 scripts/validate_artifact_contracts.py
   ```

2. Update `docs/harness-coverage-model.md` — add a new row:

   ```text
   | Skills honour the artifact-contract matrix | Workflow behavior | knowledge/artifact-contracts.md | scripts/validate_artifact_contracts.py; scripts/tests/test_validate_artifact_contracts.py | guide + blocking enforcement | Shared profile plus repo-local validation script | Promote new contract rows by adding the corresponding SKILL.md cross-reference and final-gate wording together. |
   ```

3. Optionally append the validator to `scripts/plugin-health-daemon.sh` audit sweep so the daily run catches regressions.

### Deliberate non-goals

- **No mutation.** The validator never edits files. It reports.
- **No projection involvement.** The contract is shared-profile behaviour; the validator does not touch `profile-al-dev-shared/generated/`.
- **No new contract rules.** The validator enforces today's contract structure; it does not invent new constraints.

---

## Change C: Skill Scaffold Template

### Location

`templates/skill-template/` at repo root.

Repo-local maintainer tooling, *not* in `profile-al-dev-shared/`. New skills are copied *from* the template into the distributed surface. Keeping templates outside `profile-al-dev-shared/` matches the boundary stated in repo `CLAUDE.md` (*"While the maintainer tooling is harness-specific, its outputs must be harness-agnostic"*) — the template is maintainer tooling; the copied output lives in the distributed surface.

### Files

```text
templates/skill-template/
  SKILL.md.tmpl
  tests/scenarios.yaml.tmpl
  README.md
```

### `SKILL.md.tmpl` structure

Sections in order, with placeholder values marked as `{{...}}`:

1. **Frontmatter**

   ```yaml
   ---
   name: {{skill-name}}
   description: >-
     {{one-paragraph trigger description; used for auto-invocation routing}}
   argument-hint: "{{optional args | leave empty}}"
   ---
   ```

2. **Intent Preflight**

   ```markdown
   ## Intent Preflight

   Before any mutating action, apply `knowledge/intent-preflight.md`.

   Default intent for this skill is `{{REVIEW | EDIT | COMMIT}}`.
   ```

3. **Artifact Contract**

   ```markdown
   ## Artifact Contract

   This skill is governed by `knowledge/artifact-contracts.md`.

   Do not claim the work is complete, validated, clean, or ready for the next workflow step
   until the success evidence named in `knowledge/artifact-contracts.md` for this skill has
   been produced and read for the current run.
   ```

4. **Inputs / Phases / Outputs** — three labelled placeholder blocks for skill-specific behaviour.

5. **Resume Behaviour**

   ```markdown
   ## Resume Behaviour

   Follow `knowledge/workflow-resilience.md`. Read `.dev/progress.md` first; reconcile against the resume read-order declared in `knowledge/artifact-contracts.md`.
   ```

The template body deliberately keeps boilerplate sections minimal — the goal is to bake in the contract structure, not to over-constrain the skill author.

### `tests/scenarios.yaml.tmpl`

```yaml
# scenarios for {{skill-name}} — see knowledge/skill-test-format.md
scenarios:
  - name: {{skill-name}}-trigger-canonical
    request: "{{phrasing that should trigger this skill}}"
    expected: trigger
    rationale: "{{why this phrasing must trigger}}"

  - name: {{skill-name}}-no-trigger-review-only
    request: "{{phrasing that resembles this skill but should not trigger}}"
    expected: no-trigger
    rationale: "{{why this phrasing must NOT trigger — typically a REVIEW/audit framing}}"
```

### `README.md` checklist

Plain-English steps a maintainer follows when adding a skill. Keep under 20 lines:

```markdown
# Skill scaffold template

To add a new shared skill:

1. Copy this directory to `profile-al-dev-shared/skills/<your-skill-name>/`.
2. Rename `SKILL.md.tmpl` → `SKILL.md` and `tests/scenarios.yaml.tmpl` → `tests/scenarios.yaml`.
3. Replace every `{{placeholder}}` value.
4. Add a row for the new skill to `profile-al-dev-shared/knowledge/artifact-contracts.md`
   with the declared inputs, outputs, resume read-order, handoff artefact, and success
   evidence.
5. If user-invocable, register the skill in `.claude-plugin/marketplace.json`.
6. Run the validators:

   ```bash
   python3 scripts/validate_artifact_contracts.py
   python3 scripts/validate-lens-agents.py --path profile-al-dev-shared/agents
   python3 scripts/validate-knowledge-quality.py --path profile-al-dev-shared/knowledge
   ```

7. If the new skill spawns or relies on a new agent, see `profile-al-dev-shared/agents/`
   and regenerate projections with `python3 scripts/generate-agent-projections.py`.
```

### Cross-link from the contract document

Add a single line near the top of `profile-al-dev-shared/knowledge/artifact-contracts.md`:

```markdown
> New skills should be scaffolded from `templates/skill-template/` so this contract is honoured by default.
```

This keeps the template discoverable from the contract doc, which is the source of truth for both controls.

### Deliberate non-goals

- **No `/scaffold-skill` automation skill.** Just the template files this pass. Easy to add later if usage warrants it.
- **No agent template.** Agents have different drift surfaces (tool declarations, model assignment, projection mappings) and warrant a separate design.
- **No template for repo-local `.claude/skills/`.** Maintainer-tooling skills do not have to honour the artifact contract.

---

## Architecture Summary

This design adds:

- one new validator script and its test
- one new templates directory with three files
- one new row in the harness coverage table
- one cross-link line in `artifact-contracts.md`
- one new line in repo `CLAUDE.md` validation block

This design does **not** add:

- any change to distributed shared-profile skill or agent files
- any change to the projection layer
- any runtime hook or harness-specific wiring
- any new contract rules beyond today's structure

---

## Data Flow

### Validator path

1. Validator reads `profile-al-dev-shared/knowledge/artifact-contracts.md`.
2. Validator walks the listed skill paths.
3. Validator applies the five conformance rules.
4. Validator emits a single OK line on success, or one block per violation on failure.

### Template path

1. Maintainer copies `templates/skill-template/` into `profile-al-dev-shared/skills/<name>/`.
2. Maintainer fills placeholders, adds the row to the contract matrix, registers the skill if user-invocable.
3. Maintainer runs the validator suite. Validator confirms the new skill conforms by construction.

### Reinforcement

A produces fail-fast feedback on a skill written without C. C produces a skill that passes A on the first try. Both reference `artifact-contracts.md` so the contract document remains the single source of truth.

---

## Error Handling

Expected failure handling for the validator:

- **Malformed contract table** — emit a single error naming the line of the matrix where parsing failed; do not attempt partial conformance checks.
- **Skill path resolves to a non-file** — emit a rule 1 violation and continue with other rows.
- **Unreadable SKILL.md** — emit a rule 1 violation, name the OS-level error, continue.
- **No rows in the matrix** — emit a single error: the contract document exists but has no rows; the validator has no work to do; exit 1.

Template path has no error handling — the files are inert markdown.

---

## Testing Strategy

### Validator unit tests

`scripts/tests/test_validate_artifact_contracts.py` — six tests listed under *Change A → Test coverage*, all run via the existing unittest pattern used by `test_validate_harness_neutrality.py`.

### Live tree sanity run

After implementation, run the validator once against the live tree:

```bash
python3 scripts/validate_artifact_contracts.py
```

Expected outcome: exit 0 with `OK: 6 skills conform to artifact-contracts.md` (the six skills documented by today's commits). Any failure at this stage is a real drift signal and should be triaged before merging.

### Template smoke test

After implementation, follow the template README once to scaffold a throwaway skill in a scratch path, run the validator against it, and confirm the validator reports OK without manual intervention. Delete the scratch skill.

### No new trigger-corpus scenarios required

This change does not modify any user-invocable behaviour, so no trigger-corpus update is needed.

---

## Files Changed Summary

| File | Type | Change |
|---|---|---|
| `scripts/validate_artifact_contracts.py` | New script | Validator entry point |
| `scripts/tests/test_validate_artifact_contracts.py` | New test | Six conformance scenarios |
| `templates/skill-template/SKILL.md.tmpl` | New template | Canonical skill structure |
| `templates/skill-template/tests/scenarios.yaml.tmpl` | New template | Canonical scenario file |
| `templates/skill-template/README.md` | New doc | Maintainer checklist |
| `profile-al-dev-shared/knowledge/artifact-contracts.md` | Doc | Add one-line cross-link to the template |
| `CLAUDE.md` | Doc | Add the validator to the validation command list |
| `docs/harness-coverage-model.md` | Doc | New row covering artifact-contract enforcement |

**Total:** 8 files changed
**New files:** 5
**Modified files:** 3

---

## Success Criteria

This design is successful when:

1. **Validator behaviour**
   - `python3 scripts/validate_artifact_contracts.py` exits 0 on the current tree.
   - Each of the six rules has at least one unit test that exercises a failure path.
   - Validator output names the file, the rule, and a one-line fix per violation.

2. **Template behaviour**
   - A maintainer can scaffold a new skill from `templates/skill-template/` and pass the validator with no further structural changes.
   - The template references all canonical knowledge documents (`intent-preflight.md`, `artifact-contracts.md`, `workflow-resilience.md`).

3. **Coverage model**
   - The harness coverage table contains a new row labelled `guide + blocking enforcement` for artifact-contract honour.
   - The row names the new validator script and its test as the sensor.

4. **Neutrality preserved**
   - `python3 scripts/validate_harness_neutrality.py profile-al-dev-shared` continues to exit 0 — the template lives at repo root, not in the distributed surface.

---

## Implementation Order

1. Author `scripts/validate_artifact_contracts.py` with all five rules and the agent-actionable message format.
2. Author `scripts/tests/test_validate_artifact_contracts.py` with the six failure scenarios.
3. Run the validator against the live tree; if it surfaces real drift, fix the drift before continuing.
4. Add the validator command to repo `CLAUDE.md`.
5. Add the new row to `docs/harness-coverage-model.md`.
6. Author the `templates/skill-template/` files (`SKILL.md.tmpl`, `tests/scenarios.yaml.tmpl`, `README.md`).
7. Add the one-line cross-link in `profile-al-dev-shared/knowledge/artifact-contracts.md`.
8. Smoke-test the template by scaffolding and validating a throwaway skill, then delete the scratch.

### Reason for this order

- Validator must work on the live tree before the template lands, otherwise the template's promise ("scaffold and pass") is unverified.
- The template depends on the validator existing to satisfy step 6 of its README.
- The coverage-model row depends on both controls existing so it can name them accurately.

---

## Timeline

- Validator script + agent-actionable messages: ~30 min
- Validator unittest: ~20 min
- CLAUDE.md + coverage-model updates: ~10 min
- Template files + README: ~30 min
- Cross-link + smoke test: ~10 min
- Buffer for fixing any drift surfaced by the validator on the live tree: ~20 min

**Total:** ~120 min

---

## Rejected Alternatives

### Hook-based enforcement

Rejected: the validator runs as a standalone script invokable by maintainers, CI, or the plugin-health daemon. Wiring it into a harness-specific pre-commit hook belongs in the consumer's settings, not in the shared authored surface.

### Extending an existing validator

Rejected: `validate_harness_neutrality.py` checks vocabulary; `validate-lens-agents.py` checks agent frontmatter; `validate-knowledge-quality.py` checks knowledge document quality. The artifact-contract rules cross both skills and knowledge in a domain-specific way, and merging the logic would obscure each validator's purpose. The four scripts stay parallel and focused.

### Generating skills from the template programmatically

Rejected for this pass: the template is inert markdown plus a README checklist, which keeps the surface small. A `/scaffold-skill` automation is a follow-up if usage shows the manual checklist is a real friction point.

### Including agents in the template

Rejected: agents carry tool declarations, model assignments, and projection mappings that interact with the projection layer. They deserve a separate template designed around those concerns.
