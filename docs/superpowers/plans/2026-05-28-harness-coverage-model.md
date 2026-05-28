# Harness Coverage Model Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a maintainer-facing harness coverage model that maps shared-profile behaviors to guides, sensors, enforcement strength, ownership, and gaps.

**Architecture:** Keep the first durable artifact under `docs/` so it is maintainer guidance, not a new distributed runtime contract. Use three fixed enforcement labels and add only focused regression coverage on existing test surfaces: projection generator tests and the skill-test trigger corpus.

**Tech Stack:** Markdown documentation, YAML trigger corpus, Python 3 script tests, existing projection and neutrality validation scripts.

---

## File Structure

| File | Responsibility |
|---|---|
| `docs/harness-coverage-model.md` | New maintainer-facing coverage model, seed rows, review checklist, and failure-to-rule ratchet |
| `profile-al-dev-shared/knowledge/rubber-duck.md` | Short shared-profile reference from suggestion-of-merit review to the maintainer coverage model |
| `profile-al-dev-shared/knowledge/skill-test-trigger-corpus.yaml` | One review-only ratchet prompt using the existing trigger-corpus test surface |
| `scripts/tests/test_generate_agent_projections.py` | Focused projection-policy regression for shared MCP capability mappings |

Do not create `profile-al-dev-shared/knowledge/harness-coverage-model.md` in this pass. The design intentionally starts in `docs/` until repeated reviews prove which parts belong in the distributed shared profile.

---

## Task 1: Create Maintainer Coverage Model

**Files:**
- Create: `docs/harness-coverage-model.md`

- [ ] **Step 1: Verify the target file does not already exist**

Run:

```bash
test ! -e docs/harness-coverage-model.md && echo "missing as expected"
```

Expected:

```text
missing as expected
```

- [ ] **Step 2: Create the coverage model document**

Create `docs/harness-coverage-model.md` with exactly this content:

```markdown
# Harness Coverage Model

> Maintainer reference for mapping shared-profile behavior to guidance, sensors, enforcement strength, ownership, and known gaps.

**Last updated:** 2026-05-28

---

## Purpose

`profile-al-dev-shared` is a shared outer harness for AL/BC development workflows. It shapes agent behavior through skills, agents, knowledge files, projection generation, scenario coverage, and validation scripts.

This model makes coverage explicit. Each row answers:

- what behavior the profile wants
- where the behavior is described
- how drift or failure is detected
- how strongly the behavior is enforced today
- who owns the control
- what control is still missing

Use this document when reviewing report-driven suggestions, repeated workflow failures, projection changes, and new shared-profile rules.

---

## Enforcement Labels

Use exactly these labels in the coverage table:

| Label | Meaning |
|---|---|
| `guide only` | The behavior is documented, but no automated test or blocking validation currently detects drift. |
| `guide + test` | The behavior is documented and covered by a regression test, trigger-corpus case, scenario, or deterministic review check. |
| `guide + blocking enforcement` | The behavior is documented and a validator, generator failure, workflow gate, or commit gate blocks known failure modes. |

Do not introduce ad hoc labels. If a row does not fit, improve the row instead of changing the vocabulary.

---

## Ownership Labels

Use one of these owners unless the row has a concrete reason to name a narrower owner:

| Owner | Scope |
|---|---|
| Shared profile | Authored files under `profile-al-dev-shared/skills`, `profile-al-dev-shared/agents`, `profile-al-dev-shared/knowledge`, `profile-al-dev-shared/markdown`, or `profile-al-dev-shared/bc-code-intel-knowledge`. |
| Generated projection | Files under `profile-al-dev-shared/generated/agents` and the generator that writes them. |
| Repo-local maintainer tooling | Repository-only instructions, scripts, docs, or local maintainer workflows that are not distributed as shared plugin behavior. |
| Harness runtime | Behavior supplied by Claude Code, Copilot CLI, Codex, or their local session/tool permissions. |

---

## Coverage Table

| Behavior | Category | Guide | Sensor | Enforcement strength | Owner | Gap |
|---|---|---|---|---|---|---|
| Shared agent tool intent projects correctly to each harness | Architecture/projection fitness | `profile-al-dev-shared/knowledge/agent-tool-projection-policy.md`; `docs/projection-layer-readme.md` | `scripts/tests/test_generate_agent_projections.py`; generated projection diff review | `guide + test` | Shared profile plus generated projection | Keep this row aligned with `scripts/generate-agent-projections.py`, because the generator is the runtime source of truth. |
| Harness-specific terms do not leak into shared authored files | Architecture/projection fitness | `profile-al-dev-shared/knowledge/harness-concepts.md`; `profile-al-dev-shared/knowledge/agent-tool-projection-policy.md` | `scripts/validate_harness_neutrality.py`; `scripts/tests/test_validate_harness_neutrality.py` | `guide + blocking enforcement` | Shared profile plus repo-local validation script | Make intentional allowlisted mapping documents visible in this model. |
| Long-running workflows resume from compact durable state | Workflow behavior | `profile-al-dev-shared/knowledge/workflow-resilience.md`; `profile-al-dev-shared/skills/al-dev-develop/tests/scenarios.yaml` | `develop-writes-resume-artifacts` scenario; manual resume review | `guide + test` | Shared profile | Add new rows only when additional resume artifacts become durable contracts. |
| Review-only, plan-only, edit, and commit intents are not conflated | Workflow behavior | `profile-al-dev-shared/knowledge/intent-preflight.md` | `profile-al-dev-shared/knowledge/skill-test-trigger-corpus.yaml`; per-skill review-only scenarios | `guide + test` | Shared profile | Add trigger-corpus cases for repeated misroutes before changing skill wording. |
| Compile and lint claims are evidence-backed | Workflow behavior | `profile-al-dev-shared/knowledge/compile-lint-procedure.md`; relevant skill instructions | Compile log review; skill-specific compile summary scenarios where present | `guide only` | Shared profile | Mark each skill that has no blocking gate before describing compile checks as enforced. |
| Repo-local maintainer tooling is not treated as distributed plugin surface | Ownership boundary | `AGENTS.md`; `CODEX.md`; `docs/projection-layer-readme.md` | Neutrality validation; manual generated-output review | `guide + test` | Repo-local maintainer tooling | Keep `.claude`, `.codex`, local plans, and maintainer docs out of generated plugin expectations. |
| Repeated agent failures become durable controls only after merit review | Maintainability | `profile-al-dev-shared/knowledge/rubber-duck.md`; this document | Maintainer review of the coverage row, trigger corpus, scenarios, or validator deltas | `guide only` | Repo-local maintainer tooling plus shared profile when accepted | Promote only proven rules into shared-profile files; keep one-off or harness-specific issues in repo-local docs. |

---

## Failure-to-Rule Ratchet

When a repeated failure, usage-report finding, or maintainer observation looks useful, apply this ratchet before changing shared-profile behavior:

1. Capture the concrete failure mode.
2. Name the behavior the shared profile should regulate.
3. Check the coverage table for existing guide and sensor coverage.
4. Choose the smallest durable control:
   - wording clarification
   - trigger-corpus case
   - per-skill scenario
   - validator or structural test
   - workflow gate
   - projection generator change
5. Update or add the coverage row in this document.

Do not turn every interesting recommendation into shared runtime policy. If the failure is one-off, harness-specific, repo-local, or not testable yet, document it outside the distributed shared profile.

---

## Review Checklist

Before accepting a shared-profile change that claims to improve harness behavior, verify:

- the changed behavior appears in the coverage table
- the row names a real guide file
- the row names a real sensor or explicitly says the sensor is missing
- the enforcement label is one of `guide only`, `guide + test`, or `guide + blocking enforcement`
- the owner does not confuse shared profile, generated projection, repo-local maintainer tooling, and harness runtime
- validation commands in the implementation report match the files changed

---

## Validation Commands

Use these commands when coverage changes touch shared-profile files or projection behavior:

```bash
python3 scripts/validate_harness_neutrality.py profile-al-dev-shared
python3 scripts/validate-lens-agents.py --path profile-al-dev-shared/agents
python3 scripts/tests/test_generate_agent_projections.py
python3 scripts/tests/test_validate_harness_neutrality.py
```

If authored agents under `profile-al-dev-shared/agents` change, regenerate projections:

```bash
python3 scripts/generate-agent-projections.py
```

If only `docs/`, shared knowledge, or test files change, projection regeneration is not required unless `git diff --name-only HEAD -- profile-al-dev-shared/agents` shows authored agent changes.
```

- [ ] **Step 3: Verify the fixed enforcement labels are present**

Run:

```bash
rg -n "`guide only`|`guide \\+ test`|`guide \\+ blocking enforcement`" docs/harness-coverage-model.md
```

Expected: matches in the enforcement label table, coverage table, and review checklist.

- [ ] **Step 4: Verify the coverage table names real existing files**

Run:

```bash
test -f profile-al-dev-shared/knowledge/agent-tool-projection-policy.md
test -f profile-al-dev-shared/knowledge/harness-concepts.md
test -f profile-al-dev-shared/knowledge/workflow-resilience.md
test -f profile-al-dev-shared/knowledge/intent-preflight.md
test -f profile-al-dev-shared/knowledge/compile-lint-procedure.md
test -f scripts/tests/test_generate_agent_projections.py
test -f scripts/tests/test_validate_harness_neutrality.py
test -f scripts/validate_harness_neutrality.py
echo "coverage references exist"
```

Expected:

```text
coverage references exist
```

- [ ] **Step 5: Commit**

Run:

```bash
git -C /Users/russelllaing/al-dev-shared add docs/harness-coverage-model.md
git -C /Users/russelllaing/al-dev-shared commit -m "docs: add harness coverage model"
```

Expected: commit succeeds with only `docs/harness-coverage-model.md` staged for this task.

---

## Task 2: Link Rubber-Duck Merit Review to the Coverage Model

**Files:**
- Modify: `profile-al-dev-shared/knowledge/rubber-duck.md`

- [ ] **Step 1: Locate the insertion point**

Run:

```bash
rg -n "Suggestion-of-Merit Gate|If any answer is missing" profile-al-dev-shared/knowledge/rubber-duck.md
```

Expected: one heading match and one sentence after the merit gate table.

- [ ] **Step 2: Add the coverage model ratchet section**

Insert this section immediately after the paragraph that starts `If any answer is missing`:

```markdown
## Coverage Model Ratchet

When a suggestion passes the gate and becomes shared-profile scope, update or check `docs/harness-coverage-model.md` before changing distributed guidance.

The coverage row must name:

- the behavior being regulated
- the existing guide or the new guide being added
- the sensor, test, scenario, validator, or manual review path
- the enforcement strength
- the owner
- the remaining gap

Choose the smallest durable control. Prefer a wording clarification, trigger-corpus case, focused scenario, or existing validator/test update before adding a broader workflow gate.
```

- [ ] **Step 3: Verify the reference is present**

Run:

```bash
rg -n "Coverage Model Ratchet|docs/harness-coverage-model.md|smallest durable control" profile-al-dev-shared/knowledge/rubber-duck.md
```

Expected: three matches from the inserted section.

- [ ] **Step 4: Validate harness neutrality**

Run:

```bash
python3 scripts/validate_harness_neutrality.py profile-al-dev-shared
```

Expected:

```text
PASS: no harness-specific leakage in shared authored surface
```

- [ ] **Step 5: Commit**

Run:

```bash
git -C /Users/russelllaing/al-dev-shared add profile-al-dev-shared/knowledge/rubber-duck.md
git -C /Users/russelllaing/al-dev-shared commit -m "docs(rubber-duck): reference harness coverage ratchet"
```

Expected: commit succeeds with only `profile-al-dev-shared/knowledge/rubber-duck.md` staged for this task.

---

## Task 3: Add a Trigger-Corpus Ratchet Regression

**Files:**
- Modify: `profile-al-dev-shared/knowledge/skill-test-trigger-corpus.yaml`

- [ ] **Step 1: Read the current intent-preflight corpus block**

Run:

```bash
sed -n '/intent preflight and near-miss prompts/,/expected to route elsewhere/p' profile-al-dev-shared/knowledge/skill-test-trigger-corpus.yaml
```

Expected: the existing review-only and near-miss prompt entries are shown.

- [ ] **Step 2: Add the review-only ratchet prompt**

Add this YAML entry at the end of the `intent preflight and near-miss prompts` block, before the `expected to route elsewhere or to NONE` comment:

```yaml
  - prompt: "review these repeated agent failures and tell me which ones deserve shared-profile rules"
    expected: NONE
```

This is intentionally review-only. It prevents report and failure analysis prompts from being treated as implementation, planning, or commit intent.

- [ ] **Step 3: Validate YAML syntax**

Run:

```bash
python3 -c "import yaml; yaml.safe_load(open('profile-al-dev-shared/knowledge/skill-test-trigger-corpus.yaml'))" && echo "YAML valid"
```

Expected:

```text
YAML valid
```

- [ ] **Step 4: Verify the new prompt exists exactly once**

Run:

```bash
rg -n "review these repeated agent failures" profile-al-dev-shared/knowledge/skill-test-trigger-corpus.yaml
```

Expected: one match.

- [ ] **Step 5: Validate harness neutrality**

Run:

```bash
python3 scripts/validate_harness_neutrality.py profile-al-dev-shared
```

Expected:

```text
PASS: no harness-specific leakage in shared authored surface
```

- [ ] **Step 6: Commit**

Run:

```bash
git -C /Users/russelllaing/al-dev-shared add profile-al-dev-shared/knowledge/skill-test-trigger-corpus.yaml
git -C /Users/russelllaing/al-dev-shared commit -m "test(trigger-corpus): add failure ratchet review prompt"
```

Expected: commit succeeds with only `profile-al-dev-shared/knowledge/skill-test-trigger-corpus.yaml` staged for this task.

---

## Task 4: Add Focused Projection Mapping Regression

**Files:**
- Modify: `scripts/tests/test_generate_agent_projections.py`

- [ ] **Step 1: Run the existing projection tests before editing**

Run:

```bash
python3 scripts/tests/test_generate_agent_projections.py
```

Expected:

```text
9 tests passed
```

- [ ] **Step 2: Add a failing test for MCP capability mappings**

Insert this test immediately after `test_policy_exposes_documented_translation_tables`:

```python
def test_policy_exposes_mcp_capability_mappings():
    policy = mod.default_projection_policy()

    assert policy["claude"]["MCP: al-mcp-server"].startswith("mcp__plugin_profile-claude")
    assert policy["copilot"]["MCP: bc-code-intelligence"] == "bc-code-intelligence-mcp-<tool>"
    assert (
        policy["codex"]["MCP: microsoft-docs"]["native_capability"]
        == "use the Microsoft Docs MCP capability available in the active Codex session"
    )
```

This test documents the projection coverage row with an existing deterministic test surface. It does not introduce a new schema or validator.

- [ ] **Step 3: Run the projection tests**

Run:

```bash
python3 scripts/tests/test_generate_agent_projections.py
```

Expected:

```text
10 tests passed
```

If this fails, inspect `scripts/generate-agent-projections.py` before changing the assertion. The generator is the runtime source of truth for this row.

- [ ] **Step 4: Commit**

Run:

```bash
git -C /Users/russelllaing/al-dev-shared add scripts/tests/test_generate_agent_projections.py
git -C /Users/russelllaing/al-dev-shared commit -m "test(projection): cover MCP capability mappings"
```

Expected: commit succeeds with only `scripts/tests/test_generate_agent_projections.py` staged for this task.

---

## Task 5: Final Validation and Projection Decision

**Files:**
- Inspect: `docs/harness-coverage-model.md`
- Inspect: `profile-al-dev-shared/knowledge/rubber-duck.md`
- Inspect: `profile-al-dev-shared/knowledge/skill-test-trigger-corpus.yaml`
- Inspect: `scripts/tests/test_generate_agent_projections.py`

- [ ] **Step 1: Confirm no authored agents changed**

Run:

```bash
git -C /Users/russelllaing/al-dev-shared diff --name-only HEAD -- profile-al-dev-shared/agents
```

Expected: no output.

If this command prints any `profile-al-dev-shared/agents/*.md` path, stop and run:

```bash
python3 scripts/generate-agent-projections.py
```

Then include generated projection diffs in the final validation.

- [ ] **Step 2: Run shared-profile neutrality validation**

Run:

```bash
python3 scripts/validate_harness_neutrality.py profile-al-dev-shared
```

Expected:

```text
PASS: no harness-specific leakage in shared authored surface
```

- [ ] **Step 3: Run lens-agent validation**

Run:

```bash
python3 scripts/validate-lens-agents.py --path profile-al-dev-shared/agents
```

Expected: command exits `0`. If it prints warnings, capture the warnings in the implementation report and verify they are unrelated to this change.

- [ ] **Step 4: Run projection tests**

Run:

```bash
python3 scripts/tests/test_generate_agent_projections.py
```

Expected:

```text
10 tests passed
```

- [ ] **Step 5: Run neutrality unit tests**

Run:

```bash
python3 -m unittest scripts.tests.test_validate_harness_neutrality
```

Expected:

```text
OK
```

- [ ] **Step 6: Review changed file set**

Run:

```bash
git -C /Users/russelllaing/al-dev-shared status --short
```

Expected: either a clean tree, or only changes produced by the tasks in this plan:

```text
?? docs/harness-coverage-model.md
 M profile-al-dev-shared/knowledge/rubber-duck.md
 M profile-al-dev-shared/knowledge/skill-test-trigger-corpus.yaml
 M scripts/tests/test_generate_agent_projections.py
```

The exact status depends on whether the worker committed after each task. Do not stage unrelated files.

- [ ] **Step 7: Final implementation report**

Report:

```text
Implemented harness coverage model.

Files changed:
- docs/harness-coverage-model.md
- profile-al-dev-shared/knowledge/rubber-duck.md
- profile-al-dev-shared/knowledge/skill-test-trigger-corpus.yaml
- scripts/tests/test_generate_agent_projections.py

Validation:
- python3 scripts/validate_harness_neutrality.py profile-al-dev-shared: PASS
- python3 scripts/validate-lens-agents.py --path profile-al-dev-shared/agents: PASS
- python3 scripts/tests/test_generate_agent_projections.py: 10 tests passed
- python3 -m unittest scripts.tests.test_validate_harness_neutrality: OK

Projection regeneration:
- Not required because no authored agent files changed.
```

---

## Self-Review

- Spec coverage: The plan implements the requested `docs/`-first coverage artifact, fixed enforcement labels, failure-to-rule ratchet, rubber-duck reference, and focused scenario/test additions only on existing surfaces.
- Placeholder scan: The executable task text contains no prohibited placeholder wording or unspecified test work.
- Type and naming consistency: The plan consistently uses `docs/harness-coverage-model.md`, the labels `guide only`, `guide + test`, and `guide + blocking enforcement`, and existing command paths from this repository.
