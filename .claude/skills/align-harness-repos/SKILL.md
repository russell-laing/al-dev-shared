---
name: align-harness-repos
description: >-
  Validate harness neutrality in the al-dev-shared single shared plugin surface
  by running validate_harness_neutrality.py, which checks for forbidden
  harness-specific tokens across seven classes (Claude tool tokens, dispatch
  tokens, and settings paths; Copilot tool tokens and settings paths; Claude MCP
  tokens; and harness-specific session wording) that could break distributable
  content. Run after changes to skills, agents, or knowledge.
workflow:
  stage: derive
  invoked-by: user
  repeatable: true
  inputs:
    - profile-al-dev-shared/skills/
    - profile-al-dev-shared/agents/
    - profile-al-dev-shared/knowledge/
  outputs: []   # console-only validator; emits findings to the terminal, no .dev artifact
  next: [audit-knowledge-quality]
---

# Skill: /align-harness-repos

Validate that the shared plugin surface (`profile-al-dev-shared/`) contains no
harness-specific tokens or leakage. This ensures the authored content remains
neutral and distributable across Claude Code, Copilot CLI, and Codex harnesses.

The validator scans skills, agents, knowledge documents, and markdown guides
for forbidden patterns in seven classes: Claude tool tokens (e.g. AskUserQuestion,
USER_GATE), Claude dispatch tokens (subagent_type), Copilot tool tokens (e.g.
ask_user), Claude settings paths (~/.claude), Copilot settings paths (~/.copilot),
Claude MCP tokens, and harness-specific session wording.

---

## Phase-proof requirement

This skill follows `../../knowledge/phase-proof-contract.md`: before reporting
any phase complete, advancing to the next phase, or updating
`.dev/health-loop-state.md`, emit a phase-proof block (observed command output
or file-existence check) binding to that phase's deliverable. A restated
intention is not proof.

## Phase 1 — Locate and run the validation script

```bash
SCRIPT="/Users/russelllaing/al-dev-shared/scripts/validate_harness_neutrality.py"
PLUGIN_ROOT="/Users/russelllaing/al-dev-shared/profile-al-dev-shared"
ALIGN_OUTPUT=$(python3 "$SCRIPT" "$PLUGIN_ROOT" 2>&1)
ALIGN_EXIT=$?
```

---

## Phase 2 — Handle exit 0 (clean)

If `ALIGN_EXIT` is 0:

```text
✓ All checks passed — no harness-specific leakage in shared plugin surface.
```

Stop.

---

## Phase 3 — Handle exit 1 (findings found)

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

If `ALIGN_EXIT` is 2 or higher (validator runtime error), stop immediately and
report:

```text
Validator exited with error code ALIGN_EXIT — see output above.
Fix the validator invocation or report a bug before re-running.
```

Do not proceed to Phase 4 on a runtime error.

---

## Phase 4 — USER_GATE: offer fixes

Present a summary and offer to fix:

```text
Found N forbidden token(s) across M file(s).

Want me to attempt fixes?
- Harness-specific tool tokens will be replaced with generic concept names.
- Harness-specific paths will be replaced with role-agnostic equivalents.
- Harness-specific phrasing will be replaced with neutral language.
- Tokens inside fenced code blocks will be flagged for manual review only.

Proceed? (yes / no)
```

USER_GATE — wait for user response. Do not proceed until answered.

---

## Phase 5 — Fix flow (if user consents)

For each finding:

1. Read the file containing the forbidden token.
2. Identify the harness-specific token and its context.
3. Apply the replacement rules in
   `.claude/knowledge/harness-token-map.md`.
4. Preserve line count and visual indentation; accept minor whitespace variance
   that is justified by the replacement token's differing length. Do not reflow
   or re-wrap surrounding lines.

If the token appears inside a fenced code block, flag it for manual review only
rather than auto-replacing it.

---

## Phase 6 — Re-run to confirm

After applying all fixes, re-run the validation:

```bash
ALIGN_OUTPUT=$(python3 "$SCRIPT" "$PLUGIN_ROOT" 2>&1)
ALIGN_EXIT=$?
```

If exit 0, report: "✓ All harness-neutrality issues resolved."

If exit 1, present remaining findings and note which require manual review.

**Knowledge-quality loop:** This is the final step of the
`/audit-knowledge-quality` → `/fix-knowledge-quality` → `/align-harness-repos`
loop. On exit 0, re-run `/audit-knowledge-quality` to confirm the fixes are
clean.
