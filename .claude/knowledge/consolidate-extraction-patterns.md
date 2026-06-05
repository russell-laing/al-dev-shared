# Consolidate Extraction Patterns

Reusable extraction patterns for `al-dev-consolidate` Phase 2 session
extraction. The extracted output feeds later consolidation and vault-formatting
steps without reading full file bodies into context.

## Pattern: Heading Extraction (all groups)

Extract all headings from a file. Used as the first extraction in every group.

```bash
grep '^#' "$file"
```

## Pattern: First-N-Lines-Per-Section (Groups A and C)

Extract the first N non-heading lines under each `##` heading.
Set `remaining=N` for the desired line count (Group A, the core workflow
group, uses 3; Group C, the ticket-context group, uses 5).

```bash
awk '
  /^## / { in_section=1; remaining=N; next }
  /^#/   { in_section=0 }
  in_section && remaining > 0 { print; remaining-- }
' "$file"
```

Replace `N` with `3` for Group A (core workflow) or `5` for Group C (ticket
context).

## Pattern: Governance Token Count (Group A only)

Count governance tokens used for traceability reporting.

```bash
for token in REQ ACC TEST DEC IMP DEP RISK; do
  n=$(grep -c "${token}-\|${token}:" "$file" 2>/dev/null || true)
  n=${n:-0}
  [ "$n" -gt 0 ] && echo "${token}: $n"
done
```

## Pattern: Verdict / Phase Lines (Groups D and Persistent)

Extract verdict lines, phase markers, and status headers.

```bash
grep -E \
  '^✅|^❌|^Phase [0-9]|^Status:|^Outcome:|\*\*(Verdict|Decision|Result)\*\*' \
  "$file" | head -20
```

## Pattern: Mermaid Diagram Extraction (all groups — high-value for later promote/connect review)

Run after the group's base extraction if the file contains ` ```mermaid `.

```bash
awk '
  /^#/ { last_heading = $0 }
  /^```mermaid/ { in_block=1; print last_heading; print; next }
  in_block { print; if (/^```$/) in_block=0 }
' "$file"
```

## Pattern: Image Reference Extraction (all groups — high-value for later promote/connect review)

Run after the group's base extraction if the file contains `![`.

```bash
grep -B2 -A2 '!\[' "$file"
```
