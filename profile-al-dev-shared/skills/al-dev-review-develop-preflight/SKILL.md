---
name: al-dev-review-develop-preflight
description: >-
  Pre-review qualification for al-dev-review-develop. Locates the develop
  handoff, identifies changed AL files, verifies compile success, and writes
  a preflight context file for the reviewer dispatch phase.
argument-hint: "[optional: path to develop handoff]"
---

# Review-Develop Preflight Skill

Pre-review qualification for `/al-dev-review-develop`. Run this first to locate
the develop handoff, identify changed AL files, verify compile status, and write
the preflight context file that the reviewer dispatch phase reads.

## Phase 0: Resume Check

Read `.dev/progress.md`.

If it contains a `review-preflight` checkpoint at Phase 1, 2, or 3 complete:

- Ask the user: "Preflight partially complete (Phase N done). Resume from Phase N+1, or restart from Phase 1?"
- Wait for the answer before proceeding.

If no checkpoint or answer is restart: proceed to Phase 1.

---

## Phase 1: Locate Develop Handoff

**Goal:** Find the Phase 4 handoff artifact written by `/al-dev-develop`.

1. Search for the handoff artifact:

   ```bash
   ls .dev/*-al-dev-develop-phase4-handoff.md 2>/dev/null | sort | tail -1
   ```

2. If no handoff artifact is found, stop and tell the user:

   ```text
   No develop handoff found.

   Expected: .dev/*-al-dev-develop-phase4-handoff.md
   Action required: Run /al-dev-develop first and wait for it to complete Phase 4.
   ```

3. If `$ARGUMENTS` contains a path override (e.g. `/al-dev-review-develop-preflight path/to/handoff.md`),
   use that path instead of the glob search.

4. Read the handoff artifact in full. Note the developer module assignments and implementation status.

5. Write progress checkpoint:

   ```bash
   echo "review-preflight Phase 1 complete — $(date +%Y-%m-%d %H:%M): handoff located" >> .dev/progress.md
   ```

---

## Phase 2: Identify Changed AL Files

**Goal:** Build the `CHANGED_FILES` list that reviewers will use.

Combine two sources:

1. Files listed in the handoff's module assignments section.

2. Git working tree state:

   ```bash
   git diff --cached --name-only --diff-filter=ACMR
   git ls-files --others --exclude-standard
   ```

   Filter both commands to: `*.al`, `app.json`, `*.al.json`

Deduplicate the combined list into `CHANGED_FILES`.

If `CHANGED_FILES` is empty after deduplication: stop and tell the user:

```text
No changed AL files detected.

Sources checked:
- Handoff module assignments
- git diff --cached (staged)
- git ls-files --others (untracked)

Confirm that developer changes are staged or that the handoff lists file paths.
```

Write progress checkpoint:

```bash
echo "review-preflight Phase 2 complete — $(date +%Y-%m-%d %H:%M): CHANGED_FILES identified ($(echo "$CHANGED_FILES" | wc -l | tr -d ' ') files)" >> .dev/progress.md
```

---

## Phase 3: Verify Compile Status and Write Preflight File

**Goal:** Confirm compile passes and write the preflight context file.

### Step 1: Run Compile

```bash
al-compile --output .dev/compile-errors.log
```

Check for errors:

```bash
grep -c "error AL" .dev/compile-errors.log 2>/dev/null || echo "0"
```

Set `COMPILE_STATUS`:

- `pass` — zero `error AL` lines
- `fail` — one or more `error AL` lines

### Step 2: Set PREREQUISITES_MET

| Check | Pass condition |
|-------|---------------|
| Handoff found | Phase 1 succeeded |
| CHANGED_FILES non-empty | Phase 2 succeeded |
| Compile | COMPILE_STATUS = pass |

`PREREQUISITES_MET = yes` if all three checks pass.
`PREREQUISITES_MET = no — [detail of which check failed]` otherwise.

### Step 3: Write Preflight Context File

```bash
PREFLIGHT_FILE=".dev/$(date +%Y-%m-%d)-plugin-review-preflight.md"
```

Write the file with this structure:

```markdown
# Review-Develop Preflight

**Generated:** [ISO timestamp]
**Handoff:** [handoff filename]

## CHANGED_FILES

[one file path per line]

## COMPILE_STATUS

[pass / fail]

[If fail: include the first 20 lines of .dev/compile-errors.log]

## PREREQUISITES_MET

[yes / no — detail]
```

Read the file back to confirm it was written:

```bash
cat "$PREFLIGHT_FILE"
```

Write final progress checkpoint:

```bash
echo "review-preflight Phase 3 complete — $(date +%Y-%m-%d %H:%M): preflight written to $PREFLIGHT_FILE" >> .dev/progress.md
```

### Step 4: Present Result

If `PREREQUISITES_MET = yes`:

```text
Preflight complete.

Changed files: [N]
Compile: pass
Prerequisites: all met

Preflight context: [PREFLIGHT_FILE]

Run /al-dev-review-develop now to dispatch reviewers.
```

If `PREREQUISITES_MET = no`:

```text
Preflight blocked.

[Detail of which check failed and what to do]

Fix the issue above, then re-run /al-dev-review-develop-preflight.
Do not run /al-dev-review-develop until preflight reports "Prerequisites: all met".
```
