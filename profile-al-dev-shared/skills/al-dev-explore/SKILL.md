---
name: al-dev-explore
description: Explore codebases fast with persistent output.
argument-hint: "[question or area to explore]"
---

# Command: /explore

Fast codebase exploration with structured, persistent output.
Delegates to an Explore subagent, writes findings to `.dev/`, and
integrates with `project-context.md`.

---

## Usage

```text
/explore Where is the posting logic?
/explore Find all event subscribers
/explore How does validation work for sales orders?
/explore What tables extend Customer?
/explore How is error handling implemented?
```text

---

## When to Use

| Situation | Use |
| ----------- | ----- |
| Before `/al-dev-plan` — understand what already exists | ✅ |
| Before `/al-dev-interview` — understand existing code context | ✅ |
| Finding where a specific pattern is implemented | ✅ |
| Understanding how a BC integration works | ✅ |
| General codebase orientation on a new project | ✅ |

---

## Implementation

### Step 1 — Load Context

Check for `.dev/project-context.md`:

- If it **exists**: Read the relevant sections (directory structure,
  key objects, architectural patterns). Pass this to the Explore agent
  to narrow the search scope and avoid redundant discovery.
- If it **does not exist**: Suggest `/al-dev-init-context`
  and continue without it.

Optionally load ticket context (if available):

- If `.dev/*-al-dev-ticket-ticket-context.md` exists (from
  `/al-dev-ticket`), read the latest:
  `$(ls .dev/*-al-dev-ticket-ticket-context.md 2>/dev/null | sort | tail -1)`

Classify the user's question type to guide the agent:

| Type | Signal phrases | Approach |
| ------ | --------------- | -------- |
| **Structural** | "where is", "how is organized", "find the" | Directory scan + targeted reads |
| **Pattern search** | "find all uses of", "what subscribes to", "which objects" | Grep + Glob |
| **Conceptual** | "how does X work", "explain the flow" | Read + synthesize |

---

### Step 2 — Spawn Explore Subagent

> Pattern: `knowledge/explore-subagent-pattern.md` — Steps A–D.
> Domain-specific prompt content is below.

Spawn an Explore subagent via the Agent tool:

```text
Spawn an explore agent:
  purpose: Explore [user's question]
  prompt: [user's question in full]
  output: structured findings summary

Prompt:
  "Answer this question about the codebase: [USER_QUESTION]

   Project context (if available):
   [Paste relevant sections from project-context.md — directory structure,
   key objects, architectural patterns]

   Requirements:
   1. Use Glob to find candidate files first, then Read selectively
   2. Use Grep for pattern searches (event subscribers, field usage, etc.)
   3. Do NOT read entire files unless the question requires full context
   4. Provide concrete, specific answers with file paths and line numbers

   Structure your findings as:

   ANSWER: Direct answer to the question (2-5 sentences)

   FILES:
   - path/to/file.al — one-line description of relevance

   SNIPPETS:
   [Max 3 key code excerpts, kept brief]

   CONNECTIONS:
   [How the discovered pieces relate to each other]

   GAPS:
   [What could not be determined from the code alone, if any]"
```

---

### Step 3 — Write Findings to `.dev/`

Write structured findings to
`.dev/$(date +%Y-%m-%d)-al-dev-explore-findings.md`.
**Date-prefixed** — preserves exploration history, does not overwrite.
The permanent record is `project-context.md`.

```markdown
# Exploration: [User's Question]

**Date:** [timestamp]

## Answer

[ANSWER section from agent]

## Relevant Files

| File | Relevance |
|------|-----------|
| [path] | [description] |

## Key Code

[SNIPPETS section from agent]

## Connections

[CONNECTIONS section from agent]

## Next Steps

[Suggested next action based on findings]
```

---

### Step 4 — Context Integration

After writing findings, check if exploration revealed objects or patterns
missing from `project-context.md`:

**If `project-context.md` exists and new items were found:**

```text
"These findings include [N] objects/patterns not yet in project-context.md.
 Update project-context.md to capture them? [Yes/No]
 If yes: append under a `## Recent Discoveries — [date]` section at the end of the file."
```text

If yes, append under a `## Recent Discoveries — [date]` section at the end of the file.

**If `project-context.md` does not exist and the project has AL files:**

```text
"Run /al-dev-init-context to create a project context document.
 Future explorations will be significantly faster."
```text

---

### Step 5 — Present to User

Show the ANSWER inline. Reference the file for full details.
Suggest a next command based on what was found.

```text
Exploration complete →
.dev/2026-05-19-al-dev-explore-findings.md

[ANSWER section, inline]

Key files:
  - path/to/file1.al — [relevance]
  - path/to/file2.al — [relevance]

[Suggest next command if applicable — e.g., "Ready to design
a solution? Run /plan." or "Start requirements gathering with
/interview."]
```text

---

## Notes

- Findings are date-prefixed (YYYY-MM-DD prefix) and preserved — they are
  exploration history, not a scratch pad
- For permanent knowledge capture, use `/al-dev-init-context` or accept the
  context integration prompt after exploration
- For deep multi-angle exploration, use the Explore agent with
  `thoroughness: very thorough` in the spawn prompt
