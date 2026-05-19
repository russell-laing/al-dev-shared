---
name: al-dev-release-notes
description: Generate release notes from git diff between two versions.
argument-hint: "<start-hash> <end-hash> [uat|prod] [version]"
---

# Release Notes Skill

Thin orchestrator. Resolves inputs, reads project context, then
dispatches `al-dev-release-notes-agent` to do the git analysis
and writing.

---

## Phase 1: Parse Arguments

From `$ARGUMENTS`, extract:

- `start_hash` — the earlier commit (exclusive lower bound)
- `end_hash` — the later commit (inclusive upper bound)
- `release_type` — `uat` or `prod` (default: `prod`)
- `version` — optional label (e.g. `v2.1.0` or `April 2026`);
  if omitted, use the short form of `end_hash`

If `start_hash` or `end_hash` is missing, ask the user before
continuing.

---

## Phase 1.5: Read Project Context

Check for `.dev/project-context.md`. If it exists, read these
sections to pass to the agent:

- App name and short identifier (e.g., "Kembla AU" → "Kembla-AU")
- Functional area descriptions
- Related apps or dependencies

If it does not exist, pass an empty string for project context and
ask the agent to infer a short identifier from the git metadata or
app.json name field.

---

## Phase 2: Dispatch al-dev-release-notes-agent

```text
Agent tool:
  agent: al-dev-shared:al-dev-release-notes-agent
  description: "Generate release notes [VERSION]: [start]..[end]"

Prompt:
  "Generate release notes from the git diff between two commits.

   START_HASH: [start_hash]
   END_HASH: [end_hash]
   RELEASE_TYPE: [uat or prod]
   VERSION: [version label]

   PROJECT_CONTEXT:
   [paste content from .dev/project-context.md, or 'none']

   Follow the instructions in your agent definition exactly.
   Return output in this format:

   RELEASE_NOTES_WRITTEN: .dev/YYYY-MM-DD-[app-id]-al-dev-release-notes-[short-hash].md
   VERSION: <version label>
   CHANGES: <N> (<X features, Y fixes, Z other>)
   SUMMARY: <2-3 sentence overview>
   EXCLUDED: <commit (reason)>, ... (or NONE)
   DIAGRAMS: <change title(s)> (or NONE)
   AMBIGUOUS: <change title(s)> (or NONE)"
```

---

## Phase 3: Present to User

Parse the agent output. Present:

```text
Release notes → [FILE path]

[VERSION] — [RELEASE_TYPE]
[CHANGES breakdown]

[SUMMARY]

[If EXCLUDED is not NONE:]
Excluded commits:
  [list from agent output]

[If DIAGRAMS is not NONE:]
Diagrams included for: [list]
```

If `AMBIGUOUS` is not `NONE`, ask the user to decide on each
flagged change before considering the notes final:

```text
These changes were uncertain to classify — include or exclude?
  [list from agent output]
```

If the user changes any classification, re-dispatch the agent
with explicit classification instructions appended to the prompt.
