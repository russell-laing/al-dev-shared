# AL Dev Lint Review-Only Regression Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add one regression scenario that prevents `/al-dev-lint` from silently mutating files when the user only asked to inspect compile failures or diagnostics.

**Architecture:** Keep the change entirely inside the skill-test scenario surface. The skill already documents intent preflight in prose; this plan adds the missing regression sensor so the review-only path is enforced by test data, not just guidance. No runtime behavior changes are needed unless the new scenario exposes a real gap.

**Tech Stack:** YAML scenario fixtures, existing skill-test harness, repository validation scripts.

---

## File Structure

| File | Responsibility |
|---|---|
| `profile-al-dev-shared/skills/al-dev-lint/tests/scenarios.yaml` | New golden scenario that proves a review-only lint request does not enter the diagnostics-fixer path |
| `profile-al-dev-shared/knowledge/skill-test-format.md` | Reference schema for scenario fields and artifact expectations |
| `profile-al-dev-shared/skills/al-dev-lint/SKILL.md` | Existing intent-preflight behavior the new scenario is protecting |

---

### Task 1: Add the `/al-dev-lint` review-only regression scenario

**Files:**
- Create: `profile-al-dev-shared/skills/al-dev-lint/tests/scenarios.yaml`

- [ ] **Step 1: Write the scenario file**

Create `profile-al-dev-shared/skills/al-dev-lint/tests/scenarios.yaml` with a single golden scenario in the existing shared-test format:

```yaml
skill: al-dev-lint
scenarios:
  - id: lint-rejects-review-only-misfire
    status: golden
    user_prompt: "Summarize the compile failures without fixing anything."
    expected_artifacts: []
    must_not_invoke_agent: al-dev-shared:al-dev-diagnostics-fixer
    notes: "Intent preflight regression. A review-only lint request must not silently enter the compile/fix path."
```

Use the exact field names from `profile-al-dev-shared/knowledge/skill-test-format.md`. Keep the scenario review-only and make sure it does not expect any artifacts.

- [ ] **Step 2: Make sure the prompt is unambiguous**

Before committing, re-read the scenario text and confirm it clearly asks for diagnosis only, not a fix. The prompt must remain review-only even if the harness has compile output available.

Expected result:

```text
The scenario clearly requests summary-only behavior and forbids the diagnostics-fixer agent.
```

- [ ] **Step 3: Commit the new scenario**

Run:

```bash
git add profile-al-dev-shared/skills/al-dev-lint/tests/scenarios.yaml
git commit -m "test(skill): add al-dev-lint review-only regression"
```

Expected: commit succeeds with only the new scenario file staged for this task.

---

### Task 2: Validate the shared-profile change

**Files:**
- Verify: `profile-al-dev-shared/skills/al-dev-lint/tests/scenarios.yaml`

- [ ] **Step 1: Validate the shared profile remains harness-neutral**

Run:

```bash
python3 scripts/validate_harness_neutrality.py profile-al-dev-shared
```

Expected:

```text
No harness-specific leakage found.
```

- [ ] **Step 2: Confirm the scenario file matches the shared test format**

Run:

```bash
sed -n '1,80p' profile-al-dev-shared/skills/al-dev-lint/tests/scenarios.yaml
```

Check that the file contains:

- `skill: al-dev-lint`
- one `golden` scenario
- `expected_artifacts: []`
- `must_not_invoke_agent: al-dev-shared:al-dev-diagnostics-fixer`

Expected result:

```text
The scenario matches the established shared skill-test schema.
```

- [ ] **Step 3: Review the final diff**

Run:

```bash
git diff -- profile-al-dev-shared/skills/al-dev-lint/tests/scenarios.yaml
```

Expected:

```text
Only the new lint review-only scenario is present.
```

