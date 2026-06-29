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
| --- | --- |
| `guide only` | The behavior is documented, but no automated test or blocking validation currently detects drift. |
| `guide + test` | The behavior is documented and covered by a regression test, trigger-corpus case, scenario, or deterministic review check. |
| `guide + blocking enforcement` | The behavior is documented and a validator, generator failure, workflow gate, or commit gate blocks known failure modes. |

Do not introduce ad hoc labels. If a row does not fit, improve the row instead of changing the vocabulary.

---

## Ownership Labels

Use one of these owners unless the row has a concrete reason to name a narrower owner:

| Owner | Scope |
| --- | --- |
| Shared profile | Authored files under `profile-al-dev-shared/skills`, `profile-al-dev-shared/agents`, `profile-al-dev-shared/knowledge`, `profile-al-dev-shared/markdown`, or `profile-al-dev-shared/bc-code-intel-knowledge`. |
| Generated projection | Files under `profile-al-dev-shared/generated/agents` and the generator that writes them. |
| Repo-local maintainer tooling | Repository-only instructions, scripts, docs, or local maintainer workflows that are not distributed as shared plugin behavior. |
| Harness runtime | Behavior supplied by Claude Code, Copilot CLI, Codex, or their local session/tool permissions. |

---

## Coverage Table

| Behavior | Category | Guide | Sensor | Enforcement strength | Owner | Gap |
| --- | --- | --- | --- | --- | --- | --- |
| Shared agent tool intent projects correctly to each harness | Architecture/projection fitness | `profile-al-dev-shared/knowledge/agent-tool-projection-policy.md`; `docs/projection_layer_readme.md` | `scripts/tests/test_generate_agent_projections.py`; generated projection diff review | `guide + test` | Shared profile plus generated projection | Keep this row aligned with `scripts/generate_agent_projections.py`, because the generator is the runtime source of truth. |
| Harness-specific terms do not leak into shared authored files | Architecture/projection fitness | `profile-al-dev-shared/knowledge/harness-concepts.md`; `profile-al-dev-shared/knowledge/agent-tool-projection-policy.md` | `scripts/validate_harness_neutrality.py`; `scripts/tests/test_validate_harness_neutrality.py` | `guide + blocking enforcement` | Shared profile plus repo-local validation script | Make intentional allowlisted mapping documents visible in this model. |
| Long-running workflows resume from compact durable state | Workflow behavior | `profile-al-dev-shared/knowledge/workflow-resilience.md`; `profile-al-dev-shared/skills/al-dev-develop-orchestrate/tests/scenarios.yaml` | `develop-writes-resume-artifacts` scenario; manual resume review | `guide + test` | Shared profile | Add new rows only when additional resume artifacts become durable contracts. |
| Review-only, plan-only, edit, and commit intents are not conflated | Workflow behavior | `profile-al-dev-shared/knowledge/intent-preflight.md` | `profile-al-dev-shared/knowledge/skill-test-trigger-corpus.yaml`; per-skill review-only scenarios | `guide + test` | Shared profile | Add trigger-corpus cases for repeated misroutes before changing skill wording. |
| Compile and lint claims are evidence-backed | Workflow behavior | `profile-al-dev-shared/knowledge/compile-lint-procedure.md`; relevant skill instructions | Manual compile log review; automated sensor missing for skills without scenarios | `guide only` | Shared profile | Mark each skill that has no blocking gate before describing compile checks as enforced. |
| Repo-local maintainer tooling is not treated as distributed plugin surface | Ownership boundary | `AGENTS.md`; `CODEX.md`; `docs/projection_layer_readme.md` | Manual generated-output review | `guide only` | Repo-local maintainer tooling | Add a deterministic boundary test before describing this as enforced. Keep `.claude`, `.codex`, local plans, and maintainer docs out of generated plugin expectations. |
| Repeated agent failures become durable controls only after merit review | Maintainability | `profile-al-dev-shared/knowledge/rubber-duck.md`; this document | Maintainer review of the coverage row, trigger corpus, scenarios, or validator deltas | `guide only` | Repo-local maintainer tooling plus shared profile when accepted | Promote only proven rules into shared-profile files; keep one-off or harness-specific issues in repo-local docs. |
| Skills honour the artifact-contract matrix | Workflow behavior | `profile-al-dev-shared/knowledge/artifact-contracts.md` | `scripts/validate_artifact_contracts.py`; `scripts/tests/test_validate_artifact_contracts.py` | `guide + blocking enforcement` | Shared profile plus repo-local validation script | Promote new contract rows by adding the SKILL.md cross-reference and final-gate wording together — the validator will catch omissions on the next run. |

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
python3 scripts/validate_lens_agents.py --path profile-al-dev-shared/agents
python3 scripts/tests/test_generate_agent_projections.py
```

If authored agents under `profile-al-dev-shared/agents` change, regenerate projections:

```bash
python3 scripts/generate_agent_projections.py
```

If only `docs/`, shared knowledge, or test files change, projection regeneration is not required unless `git diff --name-only HEAD -- profile-al-dev-shared/agents` shows authored agent changes.
