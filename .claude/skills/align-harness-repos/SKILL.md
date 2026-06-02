---
name: align-harness-repos
description: >-
  Validate harness neutrality in the al-dev-shared single shared plugin surface.
  Scans for forbidden harness-specific tokens (Claude Code, Copilot, etc.) that
  could break distributable content. Run after changes to skills, agents, or
  knowledge.
argument-hint: ""
---

# Skill: /align-harness-repos

Validate that the shared plugin surface (`profile-al-dev-shared/`) contains no
harness-specific tokens or leakage. This ensures the authored content remains
neutral and distributable across Claude Code, Copilot CLI, and Codex harnesses.

The command name is grandfathered from an earlier alignment-oriented workflow;
the actual behavior is a harness-neutrality validation pass.

The validator scans skills, agents, knowledge documents, and markdown guides
for forbidden patterns like "AskUserQuestion", "subagent_type", "Claude Code",
"Copilot", and harness-specific settings paths.

---

## Step 1 — Locate and run the validation script

```bash
SCRIPT="/Users/russelllaing/al-dev-shared/scripts/validate_harness_neutrality.py"
PLUGIN_ROOT="/Users/russelllaing/al-dev-shared/profile-al-dev-shared"
ALIGN_OUTPUT=$(python3 "$SCRIPT" "$PLUGIN_ROOT" 2>&1)
ALIGN_EXIT=$?
```

---

## Step 2 — Handle exit 0 (clean)

If `ALIGN_EXIT` is 0 and the output contains "PASS":

```text
✓ All checks passed — no harness-specific leakage in shared plugin surface.
```

Stop.

---

## Step 3 — Handle exit 1 (findings found)

If `ALIGN_EXIT` is 1, parse the output line-by-line. Each line has format:

```text
path/to/file.md: Rule Name: forbidden_token_or_excerpt
```

Group findings by file, then by rule. Present them:

```text
Harness-specific tokens found in shared files:

  skills/al-dev-foo/SKILL.md
    - Claude tool token: "AskUserQuestion"
    - Claude dispatch token: "subagent_type"

  agents/example.md
    - Claude settings path: "~/.claude"

  knowledge/workflow.md
    - Copilot tool token: "ask_user"
```

Also list the forbidden rules being checked:
- "Claude tool token" (AskUserQuestion, USER_GATE, etc.)
- "Claude dispatch token" (subagent_type)
- "Copilot tool token" (ask_user, etc.)
- "Claude settings path" (~/.claude)
- "Copilot settings path" (~/.copilot)
- "Claude MCP token" (mcp__plugin_profile-claude)
- "Claude/Copilot session wording" (phrases like "Open Claude Code")

---

## Step 4 — USER_GATE: offer fixes

Present a summary and offer to fix:

```text
Found N forbidden token(s) across M file(s).

Want me to attempt fixes?
- Harness-specific tool tokens will be replaced with generic concept names.
- Harness-specific paths will be replaced with role-agnostic equivalents.
- Harness-specific phrasing will be replaced with neutral language.
- Manual review will be needed for tokens in code blocks or unique contexts.

Proceed? (yes / no)
```

USER_GATE — wait for user response. Do not proceed until answered.

---

## Step 5 — Fix flow (if user consents)

For each finding:

1. Read the file containing the forbidden token.
2. Identify the harness-specific token and its context.
3. Replace with the generic equivalent:
   - `AskUserQuestion` → `USER_GATE` (concept name)
   - `subagent_type` → `agent_spawn` (concept name)
   - `ask_user` → `USER_GATE`
   - `agent_type:` → `agent_spawn:`
   - `~/.claude` → `~/.harness-config` or similar neutral path
   - `~/.copilot` → `~/.harness-config` or similar neutral path
   - "Open Claude Code" → "Invoke the harness" or "Start a session"
   - "start a new Copilot CLI session" → "Start a new harness session"
4. Preserve all surrounding text and formatting exactly.

If a token appears in a code example (code block), flag it for manual review
rather than auto-replacing, as the example may be illustrative.

---

## Step 6 — Re-run to confirm

After applying all fixes, re-run the validation:

```bash
ALIGN_OUTPUT=$(python3 "$SCRIPT" "$PLUGIN_ROOT" 2>&1)
ALIGN_EXIT=$?
```

If exit 0, report: "✓ All harness-neutrality issues resolved."

If exit 1, present remaining findings and note which require manual review.
