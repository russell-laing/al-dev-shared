# Al-Dev-Develop Session Resilience Improvements Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `/al-dev-develop` resume cleanly after context loss, keep review scope and git state explicit, and prevent compile-log context bloat.

**Architecture:** Treat the review findings as one workflow-hardening pass, not five isolated tweaks. Update the skill instructions where the behavior is orchestrated, align the shared resilience and compile procedures that the skill delegates to, then add golden scenarios that lock the new requirements into the skill test surface.

**Tech Stack:** Markdown skill/knowledge docs, YAML scenario fixtures, shell validation commands.

---

## File Structure

```text
docs/superpowers/plans/
  2026-05-25-al-dev-develop-session-resilience-improvements.md   [CREATE: this implementation plan]

profile-al-dev-shared/
  skills/al-dev-develop/SKILL.md                                 [UPDATE: concrete checkpoint, scope, git, and compile rules]
  skills/al-dev-develop/tests/scenarios.yaml                     [UPDATE: golden coverage for new behavior]
  knowledge/workflow-resilience.md                               [UPDATE: durable progress/checklist/scope artifacts]
  knowledge/compile-lint-procedure.md                            [UPDATE: compile-log inspection discipline]
  markdown/compile-output-best-practices.md                      [UPDATE: summary-only inspection guidance]
```

---

### Task 1: Make Resume State Concrete and Cheap to Rehydrate

**Files:**
- Modify: `profile-al-dev-shared/skills/al-dev-develop/SKILL.md`
- Modify: `profile-al-dev-shared/knowledge/workflow-resilience.md`
- Test: `profile-al-dev-shared/skills/al-dev-develop/tests/scenarios.yaml`

**Why:** The current skill mentions `.dev/resume-context.md` and `.dev/progress.md`, but the review findings show that state is still too vague to restore implementation quickly after compaction. The fix is to require three explicit artifacts: a dated progress snapshot, an implementation checklist extracted from the approved plan, and a scope boundary file that reviewers can enforce.

- [ ] **Step 1: Re-read the current resume and phase instructions**

Run:

```bash
sed -n '110,230p' /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-develop/SKILL.md
sed -n '1,120p' /Users/russelllaing/al-dev-shared/profile-al-dev-shared/knowledge/workflow-resilience.md
```

Expected: you can point to the existing `.dev/resume-context.md` and `.dev/progress.md` guidance that will be tightened rather than replaced.

- [ ] **Step 2: Replace the generic Phase 0.5 checkpoint with concrete dated artifacts**

In `profile-al-dev-shared/skills/al-dev-develop/SKILL.md`, replace the broad resume example with instructions that require these exact files and responsibilities:

~~~markdown
## Phase 0.5: Context Preservation Checkpoint

**Purpose:** Before development starts, create durable, low-token artifacts that survive context compaction and session hand-off.

**Required artifacts:**
- `.dev/progress.md` — latest phase checkpoint, overwritten each phase
- `.dev/$(date +%Y-%m-%d)-al-dev-develop-progress.md` — dated session snapshot
- `.dev/$(date +%Y-%m-%d)-al-dev-develop-checklist.md` — implementation checklist extracted from plan
- `.dev/$(date +%Y-%m-%d)-al-dev-develop-scope.md` — file-level scope contract

If resuming:
1. Read `.dev/progress.md`
2. Read the latest dated `*-al-dev-develop-progress.md`
3. Read the latest dated `*-al-dev-develop-checklist.md`
4. Read the latest dated `*-al-dev-develop-scope.md`
5. Resume from the recorded next step; do not re-scan the full plan unless one of these artifacts is missing
~~~

- [ ] **Step 3: Add a checklist extraction step to Phase 2**

Insert this block under Phase 2 in `profile-al-dev-shared/skills/al-dev-develop/SKILL.md`:

~~~markdown
### Phase 2.5: Extract Implementation Checklist

Write `.dev/$(date +%Y-%m-%d)-al-dev-develop-checklist.md` from the approved solution plan.

Required sections:
- `File` — each in-scope file path
- `Module Variables / Objects` — concrete additions expected
- `Procedures / Triggers` — concrete additions or edits expected
- `Integration Points` — exact existing procedures or trigger locations to touch
- `Verification` — compile, review, and artifact checks

Developers and reviewers must reference this checklist instead of repeatedly re-reading the full solution plan.
~~~

- [ ] **Step 4: Add a scope boundary artifact to Phase 3**

Insert this block before the developer spawn prompt in `profile-al-dev-shared/skills/al-dev-develop/SKILL.md`:

~~~markdown
### Phase 3.0: Write Scope Boundary Document

Before spawning developers, write `.dev/$(date +%Y-%m-%d)-al-dev-develop-scope.md` with:
- `Files in scope`
- `Permitted change types per file`
- `Files explicitly out of scope`
- `Escalation rule if an out-of-scope edit appears necessary`

Reviewers validate the implementation against this scope file, not memory alone.
~~~

- [ ] **Step 5: Tighten the shared resilience doc to match the skill**

Update `profile-al-dev-shared/knowledge/workflow-resilience.md` so the write protocol explicitly requires overwriting `.dev/progress.md` and refreshing the dated `*-al-dev-develop-progress.md` after each named phase. Add this exact structure:

~~~markdown
### Develop-Specific Resume Pack

For `/al-dev-develop`, maintain these files together:
- `.dev/progress.md` — latest checkpoint
- `.dev/YYYY-MM-DD-al-dev-develop-progress.md` — dated session narrative
- `.dev/YYYY-MM-DD-al-dev-develop-checklist.md` — extracted implementation checklist
- `.dev/YYYY-MM-DD-al-dev-develop-scope.md` — approved scope boundary

Resume order:
1. `.dev/progress.md`
2. latest dated progress file
3. latest checklist
4. latest scope file

Only re-read the full solution plan if one of the above files is missing or contradictory.
~~~

- [ ] **Step 6: Add a golden scenario that asserts resume artifacts are written**

Append this scenario to `profile-al-dev-shared/skills/al-dev-develop/tests/scenarios.yaml`:

```yaml
  - id: develop-writes-resume-artifacts
    status: golden
    user_prompt: "Implement the latest approved solution plan and preserve resume artifacts for hand-off."
    expected_artifacts:
      - ".dev/*-al-dev-develop-checklist.md"
      - ".dev/*-al-dev-develop-scope.md"
      - ".dev/*-al-dev-develop-progress.md"
      - ".dev/*-al-dev-develop-code-review.md"
    must_invoke_agent:
      - al-dev-shared:al-dev-developer
      - al-dev-shared:al-dev-security-reviewer
      - al-dev-shared:al-dev-expert-reviewer
      - al-dev-shared:al-dev-performance-reviewer
    notes: "Locks in the dated resume pack so compaction recovery reads artifacts instead of re-parsing the full plan."
```

- [ ] **Step 7: Validate the shared content stays harness-neutral**

Run:

```bash
python3 /Users/russelllaing/al-dev-shared/scripts/validate_harness_neutrality.py /Users/russelllaing/al-dev-shared/profile-al-dev-shared
```

Expected: exit code `0` and no harness-specific leakage reported.

- [ ] **Step 8: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add \
  profile-al-dev-shared/skills/al-dev-develop/SKILL.md \
  profile-al-dev-shared/knowledge/workflow-resilience.md \
  profile-al-dev-shared/skills/al-dev-develop/tests/scenarios.yaml
git -C /Users/russelllaing/al-dev-shared commit -m "docs: add durable resume artifacts to al-dev-develop"
```

---

### Task 2: Gate Review Entry on Explicit Git and Scope Verification

**Files:**
- Modify: `profile-al-dev-shared/skills/al-dev-develop/SKILL.md`
- Test: `profile-al-dev-shared/skills/al-dev-develop/tests/scenarios.yaml`

**Why:** One review finding showed the workflow could claim completion while unstaged changes still existed. The skill needs a hard pre-review cleanliness gate that stages only plan-approved files, checks for unexpected residue, and stops if scope drift remains.

- [ ] **Step 1: Re-read the current Phase 4 and Phase 9 instructions**

Run:

```bash
sed -n '330,410p' /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-develop/SKILL.md
sed -n '500,590p' /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-develop/SKILL.md
```

Expected: Phase 4 verifies ownership/naming, while Phase 9 writes the review but does not yet enforce a clean pre-review git state.

- [ ] **Step 2: Add a pre-review staging gate to Phase 9**

Insert this block before the code-review write instructions in `profile-al-dev-shared/skills/al-dev-develop/SKILL.md`:

~~~markdown
### Phase 8.5: Pre-Review File Staging

Before review synthesis:
1. Read `.dev/$(date +%Y-%m-%d)-al-dev-develop-scope.md`
2. Stage only the files listed as in scope:
   `git -C <repo> add <in-scope-files>`
3. Run:
   `git -C <repo> status --porcelain`
4. If output is non-empty:
   - Compare each path to the scope file
   - If any path is unexpected, stop and report the exact file list to the user
   - If paths are expected but unstaged, stage them and re-run status
5. Do not spawn reviewers or claim completion while unexpected working-tree changes remain
~~~

- [ ] **Step 3: Add a required report note for unexpected files**

Add this text to the Phase 9 report instructions in `profile-al-dev-shared/skills/al-dev-develop/SKILL.md`:

~~~markdown
If Phase 8.5 found unexpected files, do not write a success review.
Instead, write a blocking note that lists:
- file path
- why it is outside the approved scope
- whether the user approved, rejected, or deferred it
~~~

- [ ] **Step 4: Add a golden scenario for working-tree cleanliness**

Append this scenario to `profile-al-dev-shared/skills/al-dev-develop/tests/scenarios.yaml`:

```yaml
  - id: develop-stops-on-unexpected-working-tree-changes
    status: golden
    user_prompt: "Implement the approved plan, but stop if any modified file falls outside the approved scope."
    expected_artifacts:
      - ".dev/*-al-dev-develop-scope.md"
    must_invoke_agent:
      - al-dev-shared:al-dev-developer
    notes: "Asserts the orchestrator performs a git-status scope gate before review and does not silently continue with unexpected files."
```

- [ ] **Step 5: Validate the scenario YAML remains parseable**

Run:

```bash
python3 - <<'PY'
from pathlib import Path
import yaml
path = Path('/Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-develop/tests/scenarios.yaml')
data = yaml.safe_load(path.read_text())
assert data['skill'] == 'al-dev-develop'
assert any(s['id'] == 'develop-stops-on-unexpected-working-tree-changes' for s in data['scenarios'])
print('scenario yaml ok')
PY
```

Expected: `scenario yaml ok`

- [ ] **Step 6: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add \
  profile-al-dev-shared/skills/al-dev-develop/SKILL.md \
  profile-al-dev-shared/skills/al-dev-develop/tests/scenarios.yaml
git -C /Users/russelllaing/al-dev-shared commit -m "docs: add pre-review git cleanliness gate"
```

---

### Task 3: Enforce Summary-Only Compile Log Handling Across Skill and Knowledge Docs

**Files:**
- Modify: `profile-al-dev-shared/skills/al-dev-develop/SKILL.md`
- Modify: `profile-al-dev-shared/knowledge/compile-lint-procedure.md`
- Modify: `profile-al-dev-shared/markdown/compile-output-best-practices.md`
- Test: `profile-al-dev-shared/skills/al-dev-develop/tests/scenarios.yaml`

**Why:** The compile-log issue is already documented, but the findings show the workflow still permits context-bloating inspection habits. The fix is to make summary-only inspection an explicit rule in the skill and in both supporting references.

- [ ] **Step 1: Re-read the current compile guidance**

Run:

```bash
sed -n '420,540p' /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-develop/SKILL.md
sed -n '1,180p' /Users/russelllaing/al-dev-shared/profile-al-dev-shared/knowledge/compile-lint-procedure.md
sed -n '1,220p' /Users/russelllaing/al-dev-shared/profile-al-dev-shared/markdown/compile-output-best-practices.md
```

Expected: all three files already discourage piping `al-compile`, but none of them clearly require summary-only reporting back into the session.

- [ ] **Step 2: Tighten Phase 5 and Phase 8 in the skill**

Update `profile-al-dev-shared/skills/al-dev-develop/SKILL.md` so the compile instructions include this exact rule:

~~~markdown
Compile result reporting rules:
- Run `al-compile --output .dev/compile-errors.log` with no pipes
- Inspect the file after compile; never pipe the compile command into `head`, `tail`, or `grep`
- In conversation, report only:
  - error count
  - warning count
  - 2-3 representative examples
  - affected files
- Reference `.dev/compile-errors.log` for the full log
- Do not paste raw tail output into the session
~~~

- [ ] **Step 3: Align the shared compile-lint procedure**

Add this subsection under the existing anti-pattern guidance in `profile-al-dev-shared/knowledge/compile-lint-procedure.md`:

~~~markdown
### Session Reporting Rule

After parsing `.dev/compile-errors.log`, summarize the result instead of replaying raw log lines into the session.

Required summary fields:
- `Errors:` count
- `Warnings:` count
- `Representative diagnostics:` up to 3
- `Files affected:` unique file list
- `Detailed log:` `.dev/compile-errors.log`

Do not use `tail`, `head`, or bulk `cat` output as a status update.
~~~

- [ ] **Step 4: Align the best-practices reference**

Append this block near the summary table in `profile-al-dev-shared/markdown/compile-output-best-practices.md`:

~~~markdown
## Reporting Back Into the Session

Safe compile inspection is not enough; the session update must also stay compact.

Use this pattern:

```text
Compilation summary:
- Errors: 2
- Warnings: 5
- Representative diagnostics:
  - AL0118 in src/Foo.al:42
  - AA0231 in src/Bar.al:88
- Detailed log: .dev/compile-errors.log
```

Avoid this pattern:
- pasting `tail -20 .dev/compile-errors.log`
- dumping repeated grep output for the same error family
- reproducing diagnostics already persisted to disk
~~~

- [ ] **Step 5: Add a golden scenario for compile-log discipline**

Append this scenario to `profile-al-dev-shared/skills/al-dev-develop/tests/scenarios.yaml`:

```yaml
  - id: develop-summarizes-compile-results
    status: golden
    user_prompt: "Implement the approved plan and keep compile feedback concise by summarizing the log instead of replaying it."
    expected_artifacts:
      - ".dev/*-al-dev-develop-code-review.md"
    must_invoke_agent:
      - al-dev-shared:al-dev-developer
      - al-dev-shared:al-dev-security-reviewer
      - al-dev-shared:al-dev-expert-reviewer
      - al-dev-shared:al-dev-performance-reviewer
    notes: "Locks in summary-only compile reporting and references `.dev/compile-errors.log` as the full source of diagnostics."
```

- [ ] **Step 6: Re-run shared-content validation**

Run:

```bash
python3 /Users/russelllaing/al-dev-shared/scripts/validate_harness_neutrality.py /Users/russelllaing/al-dev-shared/profile-al-dev-shared
```

Expected: exit code `0`.

- [ ] **Step 7: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add \
  profile-al-dev-shared/skills/al-dev-develop/SKILL.md \
  profile-al-dev-shared/knowledge/compile-lint-procedure.md \
  profile-al-dev-shared/markdown/compile-output-best-practices.md \
  profile-al-dev-shared/skills/al-dev-develop/tests/scenarios.yaml
git -C /Users/russelllaing/al-dev-shared commit -m "docs: enforce summary-only compile log handling"
```

---

### Task 4: Final Consistency Pass and Plan-to-Findings Traceability Check

**Files:**
- Modify: `profile-al-dev-shared/skills/al-dev-develop/SKILL.md`
- Modify: `profile-al-dev-shared/skills/al-dev-develop/tests/scenarios.yaml`

**Why:** The findings are clustered, but they all land in one skill. This final pass ensures the instruction order is coherent after the edits and that the test scenarios cover each review finding without introducing contradictory guidance.

- [ ] **Step 1: Review the edited skill end-to-end**

Run:

```bash
sed -n '1,680p' /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-develop/SKILL.md
```

Expected: phase numbering still reads cleanly, new checkpoints appear before the phases that rely on them, and there is no conflicting advice about resume files, scope, git status, or compile log handling.

- [ ] **Step 2: Review the scenario file end-to-end**

Run:

```bash
sed -n '1,220p' /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-develop/tests/scenarios.yaml
```

Expected: existing golden scenarios still exist, and the new scenarios cover:
- resume artifact creation
- out-of-scope/working-tree stop behavior
- compile-log summary behavior

- [ ] **Step 3: Do a findings-to-plan coverage check**

Create this scratch checklist locally while reviewing, then delete it before commit:

```text
Finding 1: compaction recovery -> covered by dated progress + checklist + scope artifacts
Finding 2: git status ambiguity -> covered by Phase 8.5 pre-review staging gate
Finding 3: compile output bloat -> covered by summary-only compile reporting
Finding 4: repeated plan reads -> covered by checklist extraction and resume order
Finding 5: implicit scope boundary -> covered by scope artifact and review enforcement
```

If any finding lacks a matching instruction or scenario, fix the skill or scenario file before continuing.

- [ ] **Step 4: Run the final validators**

Run:

```bash
python3 /Users/russelllaing/al-dev-shared/scripts/validate_harness_neutrality.py /Users/russelllaing/al-dev-shared/profile-al-dev-shared
python3 - <<'PY'
from pathlib import Path
import yaml
path = Path('/Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-develop/tests/scenarios.yaml')
data = yaml.safe_load(path.read_text())
required = {
    'develop-implement-plan-with-full-panel',
    'develop-requires-plan',
    'develop-writes-resume-artifacts',
    'develop-stops-on-unexpected-working-tree-changes',
    'develop-summarizes-compile-results',
}
seen = {s['id'] for s in data['scenarios']}
missing = sorted(required - seen)
assert not missing, missing
print('scenario coverage ok')
PY
```

Expected:
- harness-neutrality validation passes
- `scenario coverage ok`

- [ ] **Step 5: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add \
  profile-al-dev-shared/skills/al-dev-develop/SKILL.md \
  profile-al-dev-shared/knowledge/workflow-resilience.md \
  profile-al-dev-shared/knowledge/compile-lint-procedure.md \
  profile-al-dev-shared/markdown/compile-output-best-practices.md \
  profile-al-dev-shared/skills/al-dev-develop/tests/scenarios.yaml
git -C /Users/russelllaing/al-dev-shared commit -m "docs: harden al-dev-develop recovery and review discipline"
```

---

## Self-Review

### Spec Coverage

- Finding 1 (compaction recovery) maps to Task 1.
- Finding 2 (git status ambiguity) maps to Task 2.
- Finding 3 (compile output bloat) maps to Task 3.
- Finding 4 (repeated plan reads) maps to Task 1.
- Finding 5 (implicit scope boundary) maps to Task 1 and Task 2.

No finding from `/Users/russelllaing/Repositories/Wight_Aluminium_Core/.dev/2026-05-25-al-dev-review-findings.md` is left without a remediation task.

### Placeholder Scan

- No `TODO`, `TBD`, or "implement later" markers remain.
- Every task names exact files and explicit commands.
- Every behavior change includes concrete snippet text to add.

### Type Consistency

- Artifact names consistently use:
  - `.dev/progress.md`
  - `.dev/YYYY-MM-DD-al-dev-develop-progress.md`
  - `.dev/YYYY-MM-DD-al-dev-develop-checklist.md`
  - `.dev/YYYY-MM-DD-al-dev-develop-scope.md`
  - `.dev/compile-errors.log`
- Scenario IDs are unique and consistently prefixed with `develop-`.
