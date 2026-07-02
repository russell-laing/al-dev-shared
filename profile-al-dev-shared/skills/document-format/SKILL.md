---
name: document-format
description: >-
  Format and bold terminology across existing documentation. Enumerates target
  occurrences, excludes code fences/inline code, spawns docs-writer for consistent
  formatting, and verifies completion.
argument-hint: "[document path] [term1] [term2] ..."
---

# Format and Bold Terms in Documentation

Format and bold terminology across existing documentation with precision.

---

## Purpose

Apply consistent formatting (bolding) to terms across existing documents:

- Enumerate all candidate occurrences before editing
- Exclude code fences, inline code, blockquotes
- Spawn single docs-writer specialist
- Verify all prose occurrences are bolded

**Usage:** `/document-format path/to/file.md "Term One" "Term Two" "Term Three"`

---

## How This Command Works

**Your Role:** Coordinator
**Teammate:** docs-writer specialist (single agent)
**You:** Verify occurrences, verify exclusions, verify completion

---

## Formatting-Sweep Workflow

### Step FS-1: Enumerate all targets before editing (grep-first — mandatory)

Before spawning the docs-writer, enumerate every candidate location **and** compute which
lines fall inside fenced code blocks, so code-fence hits are excluded with certainty rather
than guessed from a context-free grep line:

```bash
# 1. Candidate hits (replace the term list with the user's actual target terms)
grep -n "Term One\|Term Two\|Term Three" docs/Features/YourFile.md

# 2. Compute fenced-code line numbers (no literal backticks, so this block stays valid)
python3 - <<'PY'
fence = chr(96) * 3
path = "docs/Features/YourFile.md"
inside = False
for n, line in enumerate(open(path), 1):
    if line.lstrip().startswith(fence):
        inside = not inside
        print(n, "fence-boundary")
        continue
    if inside:
        print(n, "in-fence")
PY
```

Classify each candidate hit using BOTH outputs:

- Line number appears in the fenced-code output (step 2) → **excluded** (code fence)
- Already bold (the term is wrapped in `**...**`) → skip
- Inside inline backticks → **excluded**
- Inside a blockquote line (starts with `>`) → **excluded**
- Otherwise prose → apply bold

Record two explicit lists before spawning: **prose hits** (line numbers to bold) and
**excluded hits** (line numbers + reason). Do not begin editing until both lists are
complete.

### Step FS-2: Spawn docs-writer with explicit formatting rules

Include a `**Formatting rules**` block in the spawn prompt. Omitting it causes mid-sweep
clarification interruptions. Pass the prose-hit list to edit and the excluded-hit list so
the docs-writer never has to re-derive code-fence context it cannot see:

```text
Spawn single docs-writer teammate:

"Format the following terms in [docs/Features/YourFile.md].

**Formatting rules (apply exactly — do not stop to ask):**
- Bold these exact terms wherever they appear in prose: [list every term]
- Also bold these variant forms: [list abbreviations / shortened names]
- Do NOT bold inside: AL code fences, inline backticks, tester blockquotes (> lines)
- When in doubt about a variant form, apply bold — do not ask.

Target locations — PROSE HITS ONLY (edit only these line numbers):
[paste the prose-hit line numbers from FS-1]

Excluded hits — do NOT edit these (code fence / inline code / blockquote):
[paste the excluded line numbers with their reason from FS-1]

Re-run the FS-4 verification after all edits and report any line still unbolded."
```

### Step FS-3: Long-running sweep protocol (150+ lines or multiple files)

If the sweep covers more than 150 lines or more than one file, include a checkpoint
instruction in the spawn prompt:

```text
"Before starting, write .dev/format-sweep-progress.md:
- [ ] File 1: <path> — 0/<N> targets
- [ ] File 2: <path> — not started

After each target is applied, tick it off in the progress file.
On any resumption (after a 'continue' prompt), read .dev/format-sweep-progress.md
before attempting any edit — this prevents 'no changes to make' errors on
already-formatted content.
Delete the progress file when all targets are confirmed complete."
```

### Step FS-4: Verify sweep is complete (per-occurrence — do not use a `grep -v` filter)

After the docs-writer finishes, re-list every candidate occurrence and inspect each one:

```bash
grep -n "Term One\|Term Two\|Term Three" docs/Features/YourFile.md
```

For **each line printed**, confirm that every prose occurrence of every target term on that
line is wrapped in `**...**`. Do **not** filter the output with `grep -v` on the bold
marker: a line passes such a filter as soon as it contains any bold text, even when another
target term on the same line is still plain — exactly the mixed-format state this sweep
exists to clean up. The sweep is complete only when no unbolded prose occurrence of any
target term remains across all printed lines (excluded code-fence / inline-code / blockquote
hits from FS-1 stay plain by design).
