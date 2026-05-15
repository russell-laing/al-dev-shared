# Commit-Learn: .docx ZIP Corruption Incident — 2026-05-15

## Incident Classification

- **Type:** Binary file corruption — OOXML ZIP central directory inconsistency
- **Severity:** High — blocks AL compile (AL0444), requires git revert + manual Word re-save
- **Recurrence risk:** High — no guard exists; any future automated edit of a `.docx` file will repeat this

---

## What Happened

Commit `a70567b` removed `GlobalLocationNumber` columns from the AL report object `StdSalesInvoice.Report.al` [50005] and simultaneously modified the two `.docx` Word layout files for that report. The tool that wrote back the `.docx` files left the ZIP central directory in an inconsistent state (entry count mismatch of 31 bytes in each file). DOCX files are OOXML format — they are ZIP archives containing XML parts. Programmatic modification that does not use a ZIP-aware library with correct central directory rewriting produces a structurally invalid archive that the BC AL compiler rejects with `AL0444: Malformed Word report layout`. The ProForma equivalents of both files, which were not touched in the commit, pass ZIP validation. The AL report column deletion in the `.al` source file did not require any matching edit to the `.docx` layout files — Word layout templates are independent rendering templates and do not mirror the AL column list.

---

## Recovery Procedure

1. Restore both files from the last-good commit (`8c1b410`, the commit before `a70567b`):

   ```bash
   git -C /Users/russelllaing/Repositories/BioScience checkout 8c1b410 -- \
     Layouts/ACUStandardSalesInvoiceByCategory.docx \
     Layouts/ACUStandardSalesInvoiceByLine.docx
   ```

2. Verify both files pass ZIP validation after restore:

   ```bash
   for f in Layouts/ACUStandardSalesInvoiceByCategory.docx \
             Layouts/ACUStandardSalesInvoiceByLine.docx; do
     python3 -c "import zipfile, sys; zipfile.ZipFile(sys.argv[1]).testzip(); print('OK')" \
       /Users/russelllaing/Repositories/BioScience/$f
   done
   ```

3. If the `.docx` layout files genuinely need the GLN columns removed (verify this — they likely do not, because Word layout columns are bound by name/field ID, not position), open each file in Microsoft Word, make the column removal manually, then save and close. Do not use any programmatic ZIP/XML manipulation.

4. Re-run ZIP validation on any Word-saved files before staging.

5. Commit the restored (or Word-corrected) files:

   ```bash
   git -C /Users/russelllaing/Repositories/BioScience add \
     Layouts/ACUStandardSalesInvoiceByCategory.docx \
     Layouts/ACUStandardSalesInvoiceByLine.docx
   ```

6. Run `al-compile` to confirm AL0444 is gone before pushing.

**Key insight:** In the vast majority of cases, deleting a report column from an `.al` file does not require editing the Word layout. The `.docx` template will simply not render that column's data field — it will not error. Only if the layout explicitly references the deleted dataset column by name (using a field binding) does the layout need updating, and that update must be done through Word.

---

## Plugin Improvements Required

### 1. al-dev-commit: OOXML ZIP validation pre-check

**Where:** Phase 2 (execute) of the `al-dev-commit` skill, before any `git add` or `git commit` call.

**Description:** For every staged file with extension `.docx`, `.xlsx`, `.pptx`, or `.odt`, run a ZIP integrity check. If the check fails, abort the commit and report the corrupted file path. Do not allow a structurally invalid binary to enter git history.

**Implementation — shell one-liner per file:**

```bash
python3 -c "
import zipfile, sys, os
path = sys.argv[1]
try:
    with zipfile.ZipFile(path) as z:
        bad = z.testzip()
        if bad:
            print(f'CORRUPT: {path} — first bad entry: {bad}')
            sys.exit(1)
    print(f'OK: {path}')
except Exception as e:
    print(f'CORRUPT: {path} — {e}')
    sys.exit(1)
" "$FILE_PATH"
```

**Gate logic for the commit agent:**

```bash
OOXML_CORRUPT=0
for f in $(git -C "$REPO" diff --cached --name-only | grep -E '\.(docx|xlsx|pptx|odt)$'); do
  result=$(python3 -c "
import zipfile, sys
try:
    zipfile.ZipFile(sys.argv[1]).testzip()
    print('OK')
except Exception as e:
    print(f'CORRUPT: {e}')
    sys.exit(1)
" "$REPO/$f" 2>&1)
  if [[ $? -ne 0 ]]; then
    echo "BLOCKED: $f failed ZIP validation — $result"
    OOXML_CORRUPT=1
  fi
done
[[ $OOXML_CORRUPT -ne 0 ]] && exit 1
```

**Error message to user when blocked:**

```
COMMIT BLOCKED: One or more staged OOXML files failed ZIP integrity validation.

Corrupted files:
  - Layouts/ACUStandardSalesInvoiceByCategory.docx (Invalid argument — ZIP entry seek failure)
  - Layouts/ACUStandardSalesInvoiceByLine.docx (Invalid argument — ZIP entry seek failure)

These files were likely written by a tool that did not correctly rewrite the ZIP
central directory. Do NOT commit them — BC will reject them with AL0444.

Recovery options:
  1. Restore from git: git checkout HEAD -- <file>
  2. If a change is needed, make it in Microsoft Word and save from there.
  3. Re-validate: python3 -c "import zipfile; zipfile.ZipFile('<file>').testzip(); print('OK')"
```

---

### 2. .gitattributes gap detection

**Where:** Phase 1 (analysis) of the `al-dev-commit` skill — report as a warning, not a hard block.

**Description:** If OOXML files are staged but the repository has no `.gitattributes` file (or the file exists but does not contain `*.docx binary`), emit a warning. Without the `binary` attribute, git may attempt line-ending normalization on `.docx` files, which would corrupt them independently of any tool-based modification.

**Detection:**

```bash
STAGED_OOXML=$(git -C "$REPO" diff --cached --name-only | grep -E '\.(docx|xlsx|pptx)$')
if [[ -n "$STAGED_OOXML" ]]; then
  GITATTR="$REPO/.gitattributes"
  if [[ ! -f "$GITATTR" ]] || ! grep -qE '^\*\.(docx|xlsx|pptx).*binary' "$GITATTR"; then
    echo "WARNING: OOXML files staged but .gitattributes does not mark them as binary."
    echo "Recommend adding to .gitattributes:"
    echo "  *.docx binary"
    echo "  *.xlsx binary"
    echo "  *.pptx binary"
  fi
fi
```

**Recommended `.gitattributes` entry to add to this repository:**

```gitattributes
# OOXML binary formats — prevent git line-ending normalization
*.docx  binary
*.xlsx  binary
*.pptx  binary
*.rdlc  binary
```

This does not prevent corruption from programmatic writes, but it eliminates a second class of corruption (CRLF injection) and makes diffs cleaner.

---

### 3. Mixed .al + .docx commit warning

**Where:** Phase 1 (analysis) of the `al-dev-commit` skill — manifest review step.

**Description:** When a commit includes both `.al` source files and `.docx` layout files, the commit agent should flag this combination for human review before proceeding. Most AL report column changes do not require a matching `.docx` edit. When they are both present, it is a high-probability signal that a tool made a programmatic modification to the `.docx` rather than a developer making the change manually in Word.

**Flag logic:**

```bash
STAGED_AL=$(git -C "$REPO" diff --cached --name-only | grep '\.al$')
STAGED_DOCX=$(git -C "$REPO" diff --cached --name-only | grep '\.docx$')
if [[ -n "$STAGED_AL" && -n "$STAGED_DOCX" ]]; then
  echo "FLAG: This commit modifies both .al source files and .docx layout files."
  echo ""
  echo "AL files:   $STAGED_AL"
  echo "DOCX files: $STAGED_DOCX"
  echo ""
  echo "Verify: Was each .docx saved from Microsoft Word (not written by a script or tool)?"
  echo "If uncertain, run ZIP validation before proceeding."
fi
```

This flag should be presented to the developer in the Phase 1 analysis summary and require explicit acknowledgement before Phase 2 (execute) continues.

---

## Implementation Notes

| Improvement | Skill file | Phase | Action |
|---|---|---|---|
| OOXML ZIP validation | `al-dev-commit` skill | Phase 2, pre-commit | Hard block — exit 1 if any OOXML fails |
| `.gitattributes` gap | `al-dev-commit` skill | Phase 1, analysis | Warning only — no block |
| Mixed .al + .docx flag | `al-dev-commit` skill | Phase 1, manifest | User acknowledgement gate |

The ZIP validation check has no external dependencies beyond Python 3 (standard library `zipfile`), which is available on all macOS and Linux environments where this toolchain runs.

The pre-commit hook equivalent (for direct git usage outside the `al-dev-commit` skill):

```bash
# .git/hooks/pre-commit — OOXML ZIP validation
#!/usr/bin/env bash
set -euo pipefail
git diff --cached --name-only | grep -E '\.(docx|xlsx|pptx)$' | while read -r f; do
  python3 -c "
import zipfile, sys
try:
    zipfile.ZipFile(sys.argv[1]).testzip()
except Exception as e:
    print(f'CORRUPT OOXML: {sys.argv[1]} — {e}', file=sys.stderr)
    sys.exit(1)
" "$f" || exit 1
done
```

Install: `cp <above> .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit`

---

## Recurrence Risk

**High without intervention.** The `.gitattributes` file does not exist; `.docx` files have no protection. The `al-dev-commit` skill has no OOXML validation step. Any future automated or tool-assisted modification of a `.docx` file carries the same corruption risk. The AL report layout workflow (modifying `.docx` alongside `.al` report files) will recur with every report layout change. Priority: add the pre-commit hook and `.gitattributes` entries before the next report modification.
