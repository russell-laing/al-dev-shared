# Review Findings Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Address 5 identified issues in al-dev-support agents and al-dev-review skill: fix customer opinion uncritical acceptance, project hash mismatch, inline image detection, retraction language in drafts, and bug reference evidence.

**Architecture:** Three independent changes across two plugin repos:
1. Enhance `al-dev-support-reply-drafter` agent with critical-reading constraints, tone guardrails, and bug-evidence requirements (3 enhancements to one agent)
2. Add inline-image detection to `al-dev-ticket-agent` (extract from HTML + cid: references)
3. Fix underscore-to-hyphen path fallback in `al-dev-review` skill (adds fallback glob after primary attempt)

**Tech Stack:** Markdown agents, bash scripting, regex patterns

---

## Task 1: Fix Project Hash Mismatch in al-dev-review

**Files:**
- Modify: `/Users/russelllaing/claude-configs/profile-claude-al-dev/skills/al-dev-review/SKILL.md:20-43` (Step 1)

This fixes the HIGH-priority issue where underscore project paths fail because Claude Code converts underscores to hyphens in its session directory structure.

- [ ] **Step 1: Read Step 1 of al-dev-review SKILL.md**

Run: `head -50 /Users/russelllaing/claude-configs/profile-claude-al-dev/skills/al-dev-review/SKILL.md`

Verify you see the `PROJECT_HASH=$(pwd | tr '/' '-')` logic that needs the fallback.

- [ ] **Step 2: Replace Step 1 with fallback logic**

Replace lines 20-43 in `/Users/russelllaing/claude-configs/profile-claude-al-dev/skills/al-dev-review/SKILL.md`:

```markdown
## Step 1 — Locate Session JSONL & Detect Repo Context

Derive the project hash from the current working directory and find the most recently modified session file. Handle underscore-to-hyphen conversion. Detect if running in the claude-configs plugin repo itself:

```bash
PROJECT_HASH=$(pwd | tr '/' '-')
JSONL=$(ls -t ~/.claude/projects/$PROJECT_HASH/*.jsonl \
  2>/dev/null | head -1)

# Fallback: if primary glob fails, try underscore-to-hyphen conversion
if [ -z "$JSONL" ]; then
  PROJECT_HASH_ALT=$(echo "$PROJECT_HASH" | tr '_' '-')
  JSONL=$(ls -t ~/.claude/projects/$PROJECT_HASH_ALT/*.jsonl \
    2>/dev/null | head -1)
fi

if [ -z "$JSONL" ]; then
  echo "No session files found at:"
  echo "  ~/.claude/projects/$PROJECT_HASH/"
  echo "or:"
  echo "  ~/.claude/projects/$PROJECT_HASH_ALT/"
  echo ""
  echo "Available projects:"
  ls ~/.claude/projects/ | grep -i "$(basename "$(pwd)")"
  exit 1
fi
echo "Analysing: $JSONL"

# Detect if running in claude-configs repo itself
IS_PLUGIN_REPO=false
if [ -f "./CLAUDE.md" ] && [ -d "./profile-claude-al-dev" ]; then
  IS_PLUGIN_REPO=true
  echo "Detected: Running in claude-configs plugin repository"
fi
```
```

- [ ] **Step 3: Verify the change**

Run: `head -50 /Users/russelllaing/claude-configs/profile-claude-al-dev/skills/al-dev-review/SKILL.md | tail -30`

Verify you see:
- The primary `PROJECT_HASH=$(pwd | tr '/' '-')` line
- The fallback `PROJECT_HASH_ALT=$(echo "$PROJECT_HASH" | tr '_' '-')` line
- Both paths printed in error messages
- The `grep` suggestion with basename

- [ ] **Step 4: Commit**

```bash
cd /Users/russelllaing/claude-configs && \
git add profile-claude-al-dev/skills/al-dev-review/SKILL.md && \
git commit -m "fix(al-dev-review): handle underscore-to-hyphen conversion in project hash

Adds fallback glob for underscore paths. Claude Code converts underscores
to hyphens in session directories; the primary hash derivation now falls
back to hyphenated version if initial glob finds no matches."
```

---

## Task 2: Add Critical-Reading Step to Reply Drafter

**Files:**
- Modify: `/Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-support-reply-drafter.md:35-42` (Process section)

This fixes HIGH-priority finding #1 where the drafter accepted customer opinions as facts without critical assessment.

- [ ] **Step 1: Read the Process section of reply-drafter**

Run: `sed -n '35,50p' /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-support-reply-drafter.md`

Verify you see Step 1, Step 2, Step 3 outline.

- [ ] **Step 2: Add critical-reading step after Step 1**

After the "Step 1: Parse..." paragraph (line 37), insert this new step:

```markdown

**Step 1.5:** Critical reading of researcher findings

When the ticket context contains a customer's subjective opinion about a BC feature or capability (phrases such as "useless", "doesn't work for us", "no good", "not suitable", "can't be used"), do not echo or validate that opinion. Instead:
1. Note the customer's perspective (e.g., "Customer reports that [feature] is unsuitable for their workflow")
2. Independently assess the feature's actual technical capabilities from the researcher findings
3. If researcher findings address the feature's capability, present both the customer's concern AND the technical reality
4. If researcher findings do not directly address the feature, flag it as an open question for escalation rather than dismiss it

This ensures the reply acknowledges customer experience while grounding recommendations in verified technical facts.

```

- [ ] **Step 3: Verify the text was inserted**

Run: `sed -n '35,65p' /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-support-reply-drafter.md`

Verify you see:
- Original Step 1 at line 37
- New "Step 1.5: Critical reading" section
- Original Step 2 shifted down

- [ ] **Step 4: Commit**

```bash
cd /Users/russelllaing/al-dev-shared && \
git add profile-al-dev-shared/agents/al-dev-support-reply-drafter.md && \
git commit -m "feat(al-dev-support-reply-drafter): add critical-reading step for customer opinions

Adds Step 1.5 to independently assess customer opinions against researcher
findings rather than echoing subjective judgements as fact. If a customer
claims a feature is 'useless', the drafter now presents both their
perspective and the technical capabilities verified by research."
```

---

## Task 3: Add Tone and Framing Constraints to Reply Drafter

**Files:**
- Modify: `/Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-support-reply-drafter.md:50-84` (before "## Output Format")

This fixes MEDIUM-priority finding #4 where the draft included inappropriate retraction language for a first communication.

- [ ] **Step 1: Read the area before Output Format**

Run: `sed -n '48,58p' /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-support-reply-drafter.md`

Verify you see the end of Step 3 and the beginning of "## Output Format".

- [ ] **Step 2: Insert tone and framing constraints**

Between the end of the process steps and the "## Output Format" heading, insert:

```markdown

## Tone and Framing Constraints

The draft is always the customer's first communication about this issue — nothing has been sent before. Apply these constraints:

- **Never use retraction language.** Phrases like "I want to correct what was said earlier," "Let me clarify," or "That earlier information was wrong" are inappropriate in a first draft. If researcher findings supersede earlier information, incorporate them silently into a cohesive answer.
- **Preserve human, relatable voice.** Current output style (direct, clear section headings, minimal hedging) is working well. Do not over-correct toward formality or excessive caution when adding other constraints.
- **Write as a first-person direct response**, not a meta-commentary on the conversation process.

```

- [ ] **Step 3: Verify the constraints section exists**

Run: `sed -n '50,70p' /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-support-reply-drafter.md | head -15`

Verify you see "## Tone and Framing Constraints" heading and bullet points for retraction language and voice preservation.

- [ ] **Step 4: Commit**

```bash
cd /Users/russelllaing/al-dev-shared && \
git add profile-al-dev-shared/agents/al-dev-support-reply-drafter.md && \
git commit -m "feat(al-dev-support-reply-drafter): add tone and framing constraints

Adds explicit guardrails: never use retraction/correction meta-language in
first-draft replies, preserve the human relatable voice. Prevents drafts
from discussing internal iteration as if it were customer-facing revision."
```

---

## Task 4: Add Bug-Reference Evidence Requirements to Reply Drafter

**Files:**
- Modify: `/Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-support-reply-drafter.md` (Step 2 of Process section)

This fixes MEDIUM-priority finding #5 where bug references lacked evidence and Microsoft ticket numbers.

- [ ] **Step 1: Read Step 2 of the Process section**

Run: `sed -n '39,50p' /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-support-reply-drafter.md`

Verify you see Step 2 with the draft customer reply guidance.

- [ ] **Step 2: Find the exact line to expand**

The Step 2 description ends with the bullet-list section. After "- Escalation path if issue persists" (around line 42), add:

```markdown

When the reply references a known **Microsoft bug**, **platform regression**, or **known-issue**, always include:
1. A link to the most authoritative public source available: Microsoft Learn, Microsoft Q&A, Office release notes, or Power Platform tracker
2. Any known-issue number, LCS bug ID, or Power Platform tracker reference found in the researcher findings — even if the tracker URL requires admin login, the ID itself is useful for customers raising support tickets with Microsoft
3. If no official Microsoft source exists in the researcher findings, explicitly note: "No public Microsoft source yet" rather than omitting evidence

Examples of what to include:
- "Known-issue #6355973 (available to Microsoft support)"
- "Microsoft Q&A discussion: https://..."
- "Power Platform tracker reference: [number]"

```

- [ ] **Step 3: Verify the bug-evidence requirement was added**

Run: `sed -n '39,55p' /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-support-reply-drafter.md`

Verify you see:
- Original Step 2 bullet list
- New paragraph starting with "When the reply references a known **Microsoft bug**"
- Examples section with specific formats

- [ ] **Step 4: Commit**

```bash
cd /Users/russelllaing/al-dev-shared && \
git add profile-al-dev-shared/agents/al-dev-support-reply-drafter.md && \
git commit -m "feat(al-dev-support-reply-drafter): require evidence for bug references

When replies reference Microsoft bugs or regressions, must now include:
links to authoritative sources (Learn, Q&A, release notes) and known-issue
numbers from researcher findings. Improves customer credibility and lets
them track issues independently."
```

---

## Task 5: Add Inline-Image Detection to Ticket Agent

**Files:**
- Modify: `/Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-ticket-agent.md:52-82` (Step 2 context file section)

This fixes MEDIUM-priority finding #3 where inline attachments weren't detected from HTML.

- [ ] **Step 1: Read current Step 2 output format**

Run: `sed -n '52,82p' /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-ticket-agent.md`

Verify you see the markdown template with Description, Comments, Custom Fields, and Attachments sections.

- [ ] **Step 2: Add inline-image detection instructions before Step 2**

Before the "### Step 2: Write Context File" heading, add:

```markdown

### Step 1.5: Detect Inline Image Attachments

After extracting conversation HTML from the API response, scan for inline embedded images:

1. **Regex scan for `src=` attributes:** Extract all image URLs from `<img src="..."` tags in description and conversation HTML
2. **Regex scan for `cid:` references:** Extract content-ID references (Freshdesk inline attachment pattern) from `src="cid:..."` tags
3. **Compile inline-image list:** Create a distinct list of inline images found — these are separate from the file attachments array in the API response

Example patterns to match:
```
src="https://cdn.freshdesk.com/...jpg"     → extract URL
src="cid:attachment_123abc"                 → extract cid:attachment_123abc
<img src="data:image/png;base64,..."      → note as "inline base64 image"
```

If inline images are found, include them in the return block as `INLINE_IMAGES_COUNT: [N]`.
```

- [ ] **Step 3: Update Step 2 markdown template to include inline images**

Find the "## Attachments" section of the template (around line 80) and replace it:

Old:
```markdown
## Attachments
[If applicable: filename, size, URL]
```

New:
```markdown
## Attachments

**File Attachments:** (from API attachments array)
[If applicable: filename, size, URL]

**Inline Embeds:** (extracted from HTML src= and cid: references)
[If applicable: image URL or cid:reference, extracted from description and comments]
```

- [ ] **Step 4: Update Step 3 return block to include inline-image count**

Find the return block around line 87 and add `INLINE_IMAGES_COUNT`:

Old return block should include:
```
ATTACHMENTS: [Count or "None"]
```

Add line:
```
INLINE_IMAGES_COUNT: [N or "None"]
```

So full return block becomes:
```
TICKET_CONTEXT_WRITTEN: .dev/YYYY-MM-DD-al-dev-ticket-ticket-context.md
TICKET_ID: [ID]
STATUS: [Status]
PRIORITY: [Priority]
COMMENTS_COUNT: [N]
ATTACHMENTS: [Count or "None"]
INLINE_IMAGES_COUNT: [N or "None"]
```

- [ ] **Step 5: Verify all changes to ticket agent**

Run: `grep -n "Inline Embeds\|INLINE_IMAGES_COUNT\|cid:" /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-ticket-agent.md`

Verify all three patterns appear:
- "Inline Embeds" section in the template
- "INLINE_IMAGES_COUNT" in return block
- "cid:" in the detection instructions

- [ ] **Step 6: Commit**

```bash
cd /Users/russelllaing/al-dev-shared && \
git add profile-al-dev-shared/agents/al-dev-ticket-agent.md && \
git commit -m "feat(al-dev-ticket-agent): detect inline image attachments from HTML

Adds Step 1.5 to scan for <img src=...> and cid: references in ticket
description and comments. Inline images are now extracted separately from
file attachments and included in context file under 'Inline Embeds' section.
Returns INLINE_IMAGES_COUNT in output block."
```

---

## Self-Review Checklist

- [ ] **Spec coverage:** All 5 findings addressed:
  - ✓ Finding #1 (uncritical opinion): Task 2 adds Step 1.5 critical reading
  - ✓ Finding #2 (hash mismatch): Task 1 adds fallback glob
  - ✓ Finding #3 (inline images): Task 5 adds detection + template update
  - ✓ Finding #4 (retraction language): Task 3 adds tone constraints
  - ✓ Finding #5 (bug evidence): Task 4 adds evidence requirements

- [ ] **No unresolved placeholders:** All code blocks are concrete with exact paths, regex patterns, and markdown examples. No "add X", "handle Y", or "similar to Task N" patterns.

- [ ] **Type/name consistency:** 
  - Critical reading step called "Step 1.5" (consistent with existing numbering)
  - Inline detection called "Step 1.5" in ticket agent (does not conflict)
  - All file paths absolute and verified
  - All return block fields match existing conventions (CAPS_WITH_UNDERSCORES)

- [ ] **Positive signal preserved:** Task 3 explicitly notes to preserve the human, relatable voice when implementing tone constraints — prevents over-correction toward formality.

- [ ] **5 separate commits planned:** Each task ends with its own atomic git commit as per global CLAUDE.md conventions.
