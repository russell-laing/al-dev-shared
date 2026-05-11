---
name: al-dev-align
description: >-
  Check alignment between al-dev-shared and harness repos. Audits for forbidden
  harness-specific tokens in shared skill/agent bodies and verifies harness
  mapping tables are complete. Run after changes to al-dev-shared or harness profiles.
argument-hint: ""
---

# Skill: /al-dev-align

Audit alignment between `al-dev-shared` and the two harness profile repos.
Checks for forbidden harness-specific tokens in shared files, and verifies
the Harness Mapping tables are complete in both harness profile instruction files.

---

## Step 1 — Locate and run the script

```bash
SCRIPT="$AL_DEV_SHARED_PLUGIN_ROOT/skills/al-dev-align/check-alignment.py"
if [ ! -f "$SCRIPT" ]; then
  echo "Script not found at $SCRIPT — is AL_DEV_SHARED_PLUGIN_ROOT set?"
  exit 1
fi
ALIGN_OUTPUT=$(python3 "$SCRIPT" --mode enforce)
ALIGN_EXIT=$?
```

`ALIGN_OUTPUT` holds the JSON; `ALIGN_EXIT` holds the exit code.

---

## Step 2 — Handle exit 0 (clean)

If `ALIGN_EXIT` is 0:

```
All checks passed — no forbidden tokens or mapping gaps found.
```

Stop.

---

## Step 3 — Handle exit 2 (runtime error)

If `ALIGN_EXIT` is 2:

Attempt to parse `$ALIGN_OUTPUT` as JSON. If it is valid JSON, report the `"error"` field; otherwise report `$ALIGN_OUTPUT` verbatim:

```
Alignment check failed with a configuration error:
  [error message from JSON]

Possible causes:
- AL_DEV_SHARED_PLUGIN_ROOT is not set or points to wrong directory
- harness-concepts.md is missing from knowledge/
- Harness profile paths are wrong (use --profile-a / --profile-b flags to override)
```

Stop.

---

## Step 4 — Present findings (exit 1)

Parse the JSON output. Present findings in two sections:

**Section A — Forbidden tokens** (grouped by file):

```
Forbidden tokens found in shared files:

  skills/al-dev-foo/SKILL.md
    Line 12 [error, autofixable]: token "X"
      Context: "...surrounding text..."
    Line 34 [warning, code_block]: token "Y"
      Context: "...surrounding text..."
    Line 56 [manual_review, prohibition_rule]: token "Z"
      Context: "...surrounding text..."
```

**Section B — Coverage gaps** (grouped by type):

```
Harness mapping gaps:

  Missing mappings (concept exists in harness-concepts.md but has no row in a mapping table):
    - "USER_GATE": missing in [harness-a, harness-b]
    - "explore agent": missing in [harness-b]

  Orphaned mappings (row exists in a mapping table but concept is not in harness-concepts.md):
    - "old concept": present in [harness-a]  <- may be intentional
```

---

## Step 5 — USER_GATE: offer fixes

Present a summary count and offer to fix:

```
Found N forbidden token(s) across M file(s), and P mapping gap(s).

Want me to attempt fixes?
- Autofixable prose hits will be substituted with the generic concept name from harness-concepts.md.
- code_block and prohibition_rule hits will be flagged for manual review (not auto-changed).
- Missing mapping rows will be added to the appropriate harness profile instruction file.
- Orphaned rows will be flagged for manual review (not auto-deleted).

Proceed? (yes / no)
```

USER_GATE — wait for user response. Do not proceed until answered.

---

## Step 6 — Fix flow (if user consents)

### 6a — Auto-fix prose hits (`autofixable: true`)

For each `forbidden_tokens` entry where `autofixable` is `true`:

1. Read the vocabulary table in `knowledge/harness-concepts.md`.
2. Find the row where the harness-specific concrete value matches the reported token.
3. Replace the forbidden token in the file with the generic concept name from column 1 of that row.
4. Preserve all surrounding text exactly.

### 6b — Flag non-autofixable hits

For each `code_block` or `prohibition_rule` hit, output:

```
Manual review needed:
  [file]:[line] — token "[X]" appears in a [context_type] context.
  Suggestion: verify this is intentional or replace with the generic concept name.
```

Do not modify these lines automatically.

### 6c — Fix missing mapping rows

For each entry in `missing_mappings`:

1. Open the harness profile instruction file for each harness listed in `missing_in`.
2. Locate the `## Harness Mapping` section.
3. Append a new stub row at the end of the table:
   `| **[concept name]** | _(fill in concrete value)_ |`
4. Tell the user: "Added stub row for '[concept]' — fill in the concrete harness value."

### 6d — Flag orphaned rows

For each entry in `orphaned_mappings`, output:

```
Orphaned mapping "[concept]" present in [harness] profile — concept not found in harness-concepts.md.
Verify this is intentional. If the concept was renamed, update harness-concepts.md.
```

Do not auto-delete orphaned rows.

---

## Step 7 — Re-run to confirm

After applying all fixes, re-run the script:

```bash
ALIGN_OUTPUT=$(python3 "$SCRIPT" --mode enforce)
ALIGN_EXIT=$?
```

If exit 0, report: "All alignment issues resolved."

If exit 1, present remaining issues and note which require manual review.
