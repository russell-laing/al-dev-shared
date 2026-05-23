# Context Bloat Prevention Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prevent context window bloat from unredirected compiler and build tool output in investigation sessions by adding output capture guidance and safeguards to exploration and investigation workflows.

**Architecture:** Three targeted updates to the al-dev-shared plugin:
1. Enhance `al-dev-explore` agent with explicit Bash output redirection guidance
2. Update `al-dev-investigate` skill to require output handling in hypothesis-testing prompts
3. Add a post-tool safeguard in the explore agent to prevent session-bloating output

**Tech Stack:** AL/Business Central plugin (markdown-based skill and agent definitions)

---

## File Structure

**Files to modify:**
- `profile-al-dev-shared/agents/al-dev-explore.md` — Add Bash output capture section + safeguard
- `profile-al-dev-shared/skills/al-dev-investigate/SKILL.md` — Update Step 4 hypothesis-testing prompt template

**No new files created** — all changes are targeted additions to existing documentation.

---

### Task 1: Add Bash Output Capture Guidance to al-dev-explore Agent

**Files:**
- Modify: `profile-al-dev-shared/agents/al-dev-explore.md:39-46`

- [ ] **Step 1: Read the current agent file**

Read the full agent to understand its structure and where to insert the new section.

```bash
cat /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-explore.md
```

Expected: File shows tool declaration at line 7: `tools: ["Read", "Glob", "Grep", "Write"]`

- [ ] **Step 2: Understand tool declaration scope**

The current tools list does not include Bash. However, the safeguard is needed to prevent any agent (including future variants) from letting large output flow to stdout. We are adding guidance that applies if Bash or similar tools producing verbose output are ever used.

The new section should go **immediately after the Constraints section** (after line 46) to establish output safety norms before any agent execution.

- [ ] **Step 3: Add Bash Output Capture section**

Using the Edit tool, add this section after the Constraints (before "## Findings File Format"):

```markdown
## Tool: Bash Output Capture

When running build, compile, test, or other tools that produce verbose output:

- Always redirect stderr to a file: `2>>.dev/investigate-errors.log`
- Always redirect stdout to the same file: `>>.dev/investigate-errors.log`
- Alternatively, use `2>&1 | tee -a .dev/investigate-errors.log` to capture while seeing summary
- Never let compiler output flow to session stdout
- Extract findings from the error log; return only summaries to the agent output

**Example patterns:**

✅ GOOD:  `al-compile 2>>.dev/investigate-errors.log && echo "✓ Compiled"`

✅ GOOD:  `al-compile 2>&1 | grep -E "^error|^warn" | head -10`

❌ WRONG: `al-compile` (unredirected output bloats session)

❌ WRONG: `al-compile > /dev/null 2>&1` (silent failure, no evidence)

**Critical:** Bash commands that produce >100 lines of output (compilers, large file operations, verbose diagnostics) MUST redirect to a `.dev/` file or pipe through grep/awk for summarization. Session bloat from unredirected output will exhaust the context window and make the investigation unusable for follow-up turns.
```

- [ ] **Step 4: Verify the edit and check structure**

Read the file again to confirm the new section is inserted correctly and the overall structure is maintained:

```bash
wc -l /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-explore.md
```

Expected: Line count increased by ~25 lines (the new section).

---

### Task 2: Update al-dev-investigate Skill with Output Handling Requirement

**Files:**
- Modify: `profile-al-dev-shared/skills/al-dev-investigate/SKILL.md:156-195` (Step 4 hypothesis-testing prompt)

- [ ] **Step 1: Review the current hypothesis-testing prompt**

Read Step 4 in the investigate skill to locate the exact prompt template:

```bash
sed -n '156,195p' /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-investigate/SKILL.md
```

Expected: Shows the prompt starting with "You are investigating a bug..." and containing hypothesis sections and VERDICT/EVIDENCE/REASONING fields.

- [ ] **Step 2: Locate insertion point in the prompt**

The output handling requirement should be inserted **after** the "For EACH hypothesis report:" section, right before the verdict field instructions. This ensures agents read the requirement before building their response structure.

Exact insertion point: After the line containing `"For EACH hypothesis report:"` (around line 189) and before the line containing `VERDICT: CONFIRMED | REJECTED | INCONCLUSIVE`.

- [ ] **Step 3: Add output handling requirement to the prompt**

Edit the file to insert this text after line 189 (in the prompt section):

```markdown
   **Output handling:** If your investigation requires running compile,
   build, or test commands, redirect all output to `.dev/investigate-errors.log`
   (use `2>>.dev/investigate-errors.log`). Extract only relevant error summaries
   or findings to report back — do not let verbose compiler output flow to the
   session. If a compilation error is significant to the investigation, include
   the error message but not the full compiler trace.

```

The updated prompt section should read:

```text
   ...
   For EACH hypothesis report:

   **Output handling:** If your investigation requires running compile,
   build, or test commands, redirect all output to `.dev/investigate-errors.log`
   (use `2>>.dev/investigate-errors.log`). Extract only relevant error summaries
   or findings to report back — do not let verbose compiler output flow to the
   session. If a compilation error is significant to the investigation, include
   the error message but not the full compiler trace.

   VERDICT: CONFIRMED | REJECTED | INCONCLUSIVE
   ...
```

- [ ] **Step 4: Verify the change**

Read the modified section to confirm the requirement is in place:

```bash
sed -n '185,200p' /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-investigate/SKILL.md
```

Expected: The output handling block appears between "For EACH hypothesis report:" and "VERDICT: CONFIRMED..." on separate lines.

---

### Task 3: Commit Changes

**Files:**
- `profile-al-dev-shared/agents/al-dev-explore.md`
- `profile-al-dev-shared/skills/al-dev-investigate/SKILL.md`

- [ ] **Step 1: Check git status to see all modified files**

```bash
cd /Users/russelllaing/al-dev-shared && git status
```

Expected: Both modified files appear in "Changes not staged for commit".

- [ ] **Step 2: Verify line counts are preserved**

Both files should have increased line counts only by the exact number of lines added (no unintended deletions):

```bash
cd /Users/russelllaing/al-dev-shared && \
wc -l profile-al-dev-shared/agents/al-dev-explore.md profile-al-dev-shared/skills/al-dev-investigate/SKILL.md
```

Expected: 
- `al-dev-explore.md`: original 73 lines → ~98 lines (added ~25)
- `al-dev-investigate/SKILL.md`: original 338 lines → ~345 lines (added ~7)

- [ ] **Step 3: Scan for forbidden patterns**

Check that no forbidden patterns (TODO, TBD, [date], Co-Authored-By in code) are present in the modified sections:

```bash
cd /Users/russelllaing/al-dev-shared && \
grep -n "TODO\|TBD\|\[202[0-9]-\|Co-Authored-By\|claude:" profile-al-dev-shared/agents/al-dev-explore.md profile-al-dev-shared/skills/al-dev-investigate/SKILL.md || echo "No forbidden patterns found"
```

Expected: "No forbidden patterns found"

- [ ] **Step 4: Create the commit**

Stage both files and create a single atomic commit:

```bash
cd /Users/russelllaing/al-dev-shared && \
git add profile-al-dev-shared/agents/al-dev-explore.md profile-al-dev-shared/skills/al-dev-investigate/SKILL.md && \
git commit -m "fix: add bash output redirection guidance to prevent context bloat in investigations

- al-dev-explore agent: new 'Tool: Bash Output Capture' section with patterns for
  redirecting compiler/build output to .dev/ files instead of letting verbose output
  inflate session context
- al-dev-investigate skill: add output handling requirement to Step 4 hypothesis-testing
  prompt, requiring agents to redirect build/compile commands and summarize findings
- safeguard: agents must not let >100 lines of compiler output flow to session stdout

Prevents context window bloat observed in BrighterDays sync investigation where
1.2MB of unredirected AL compiler output inflated session from 300K to 1.5MB.

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>"
```

- [ ] **Step 5: Verify commit was created**

Check that the commit was created successfully with both files:

```bash
cd /Users/russelllaing/al-dev-shared && git log --oneline -n 1 && git show --name-only HEAD
```

Expected: Shows the commit message and lists both modified files.

---

## Self-Review Checklist

**Spec Coverage:**
- ✅ Fix 1 (al-dev-explore output guidance): Task 1
- ✅ Fix 2 (al-dev-investigate prompt update): Task 2  
- ✅ Fix 3 (safeguard against bloat): Included in Task 1
- ✅ Commit verification: Task 3

**Placeholder Scan:**
- ✅ All code examples are complete (GOOD/WRONG patterns shown)
- ✅ All file paths are exact
- ✅ No "TBD", "TODO", or vague instructions
- ✅ Commit message includes Co-Authored-By trailer

**Type/Name Consistency:**
- ✅ Output file path consistent: `.dev/investigate-errors.log`
- ✅ Bash redirection pattern consistent: `2>>.dev/investigate-errors.log`
- ✅ Section naming consistent: "Tool: Bash Output Capture"
