---
name: al-dev-handoff
description: >-
  Package investigation context and generate a session-continuation prompt
  for cross-repo root-cause migration. Use when investigation confirms the
  root cause lives in a different repository.
argument-hint: "[path to target repository]"
---

# Skill: /al-dev-handoff

Cross-repo investigation migration — moves context from this
session into another repository's session without re-running
the investigation.

## Artifact Contract

This skill is governed by `knowledge/artifact-contracts.md`.

Do not claim the handoff is complete or ready until the success evidence named in `knowledge/artifact-contracts.md` for this skill has been produced and read in the current run.

---

## When to Use

| Situation | Use |
| --- | --- |
| Investigation shows root cause is in another repo | ✅ |
| User says "continue this in [other repo]" | ✅ |
| `explore-findings.md` lists a different repo as fix owner | ✅ |
| Single-repo fix (root cause is here) | ❌ Use `/al-dev-plan` |

---

## Implementation

### Step 1 — Identify Target Repository

From user args or `.dev/explore-findings.md` "Affected Repositories"
table:

- If user provided a path: verify it exists
- If findings list a specific repo path: use that
- If ambiguous: ask the user for the full path

```bash
[ -d "[target-repo-path]" ] || {
  echo "Path not found — verify target repo path" >&2
  exit 1
}
```

---

### Step 2 — Inventory Context Files to Copy

List existing `.dev/` files:

```bash
ls .dev/*.md 2>/dev/null
```

Copy these files if they exist:

| Source (this repo) | Target (destination repo) |
| --- | --- |
| `$(ls .dev/*-al-dev-ticket-ticket-context.md 2>/dev/null \| sort \| tail -1)` | `.dev/source-ticket-context.md` |
| `$(ls .dev/*-al-dev-explore-findings.md 2>/dev/null \| sort \| tail -1)` | `.dev/source-explore-findings.md` |
| `.dev/project-context.md` | `.dev/source-project-context.md` |
| `$(ls .dev/*-al-dev-plan-solution-plan.md 2>/dev/null \| sort \| tail -1)` | `.dev/source-solution-plan.md` |
| `$(ls .dev/*-al-dev-interview-requirements.md 2>/dev/null \| sort \| tail -1)` | `.dev/source-requirements.md` |
| `$(ls .dev/*-plugin-release-notes.md 2>/dev/null \| sort \| tail -1)` | `.dev/source-release-notes.md` |

Rename `project-context.md` → `source-project-context.md` to avoid
overwriting the target repo's own context document.

Exclude: `compile-errors.log`, `test-results.txt`,
`progress.md` — these are repo-specific artefacts.

---

### Step 3 — Copy the Files

```bash
TARGET="[target-repo-path]"
mkdir -p "$TARGET/.dev"

TICKET=$(ls .dev/*-al-dev-ticket-ticket-context.md 2>/dev/null | \
  sort | tail -1)
[ -n "$TICKET" ] && \
  cp "$TICKET" "$TARGET/.dev/source-ticket-context.md" && \
  echo "✅ source-ticket-context.md" || \
  echo "⏭ source-ticket-context.md (not found)"

EXPLORE=$(ls .dev/*-al-dev-explore-findings.md 2>/dev/null | \
  sort | tail -1)
[ -n "$EXPLORE" ] && \
  cp "$EXPLORE" "$TARGET/.dev/source-explore-findings.md" && \
  echo "✅ source-explore-findings.md" || \
  echo "⏭ source-explore-findings.md (not found)"

[ -f .dev/project-context.md ] && \
  cp .dev/project-context.md \
  "$TARGET/.dev/source-project-context.md" && \
  echo "✅ project-context.md → source-project-context.md" || \
  echo "⏭ project-context.md (not found)"

PLAN=$(ls .dev/*-al-dev-plan-solution-plan.md 2>/dev/null | \
  sort | tail -1)
[ -n "$PLAN" ] && cp "$PLAN" \
  "$TARGET/.dev/source-solution-plan.md" && \
  echo "✅ solution-plan.md → source-solution-plan.md" || \
  echo "⏭ solution-plan.md (not found)"

REQUIREMENTS=$(ls .dev/*-al-dev-interview-requirements.md \
  2>/dev/null | sort | tail -1)
[ -n "$REQUIREMENTS" ] && cp "$REQUIREMENTS" \
  "$TARGET/.dev/source-requirements.md" && \
  echo "✅ requirements.md → source-requirements.md" || \
  echo "⏭ requirements.md (not found)"

RELEASE_NOTES=$(ls .dev/*-plugin-release-notes.md 2>/dev/null | \
  sort | tail -1)
[ -n "$RELEASE_NOTES" ] && \
  cp "$RELEASE_NOTES" "$TARGET/.dev/source-release-notes.md" && \
  echo "✅ source-release-notes.md" || \
  echo "⏭ source-release-notes.md (not found)"

ls "$TARGET/.dev/"
```

---

### Step 4 — Generate the Session Continuation Prompt

Read `explore-findings.md` and write
`.dev/$(date +%Y-%m-%d)-al-dev-handoff-handoff-prompt.md`:

```markdown
# Handoff Prompt — [date]

Paste this into a new session in your AI coding harness, opened in [target repo name].

---

## Context

I am continuing an investigation that started in **[source repo name]**.
Investigation context files are in `.dev/`.

**Bug symptom:** [Root Cause section from explore-findings.md — 2-3 sentences]

**What was confirmed in the source repo:**

| Hypothesis | Status |
| --- | --- |
| [H1 text] | ✅ CONFIRMED |
| [H2 text] | ❌ REJECTED |
| ... | ... |

**Why we are now in this repo:** [1-2 sentences — e.g., "The root
cause is in Cod50741.al in this repo. The source repo
(MM_Kembla_Price_App) only displays the computed value."]

## Context files available in `.dev/`

- `source-ticket-context.md` — original ticket ([FDxxxxx])
- `source-explore-findings.md` — hypothesis results with evidence
- `source-project-context.md` — context from [source repo name]
- `source-solution-plan.md` — prior solution plan from [source repo name], if copied
- `source-requirements.md` — prior requirements/context from [source repo name], if copied
- `source-release-notes.md` — release notes for the version shipped from [source repo name], if copied

## Key objects to examine in this repo

[From explore-findings.md Evidence sections]

- `[file path]:[line]` — [why relevant]
- `[file path]:[line]` — [why relevant]

## Suggested first command

~~~text
/al-dev-plan [specific fix description based on confirmed root cause]
~~~

Or if more investigation of this repo is needed first:

~~~text
/al-dev-investigate [specific question about this repo's code]
~~~
```

Write this to `.dev/$(date +%Y-%m-%d)-al-dev-handoff-handoff-prompt.md`
in the current (source) repo.

---

### Step 5 — Present to User

```text
Handoff ready → [target-repo-path]/.dev/

Files copied:
  ✅ source-ticket-context.md
  ✅ source-explore-findings.md
  ✅ project-context.md → source-project-context.md

Session prompt → .dev/[date]-al-dev-handoff-handoff-prompt.md

To continue in [target repo name]:
1. Open a new session rooted at: [target-repo-path]
2. Paste the prompt from .dev/[date]-al-dev-handoff-handoff-prompt.md
   (preview: cat .dev/[date]-al-dev-handoff-handoff-prompt.md)
```

---

## Notes

- `project-context.md` is always renamed to `source-project-context.md`
  in the target — preserves the target repo's own context if it exists
- The handoff prompt is self-contained: the new session needs no prior
  conversation history
- Verify the target path exists before running any copy commands
- If the target repo has no `.dev/` directory it will be created
