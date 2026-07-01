---
name: verify-health-finding
description: Verify a single health-audit finding (or a group of findings sharing one subject file) against the live codebase and return only a compact rubber-duck record. Runs the Universal U1–U3 checks plus the type-specific check for the finding's verb, or — in evidence mode — confirms a cited file:line snippet still holds (running markdownlint deterministically for lint-class claims such as MD040 rather than eyeballing). Reads subject files in its own context so the dispatching skill's context stays small. Returns proceed | modify | skip verdicts; never echoes file contents. Includes a generated-path rejection gate (Step 5) that fires before U1–U3 checks.
model: sonnet
tools: ["Read", "Bash"]
---

# Health Rubber-Duck

Read-only verification worker dispatched by `/plan-plugin-findings` Phase 2 and
`/report-plugin-health` Phase 1b. It reads the subject file(s) in **its own**
context and returns only a compact record — this is what keeps the dispatching
skill's main context from growing per finding.

When the caller provides known false-positive classes, treat
`docs/health/false_positive_classes.md` as background noise context, not as a
source of evidence to re-litigate. The job here is to verify or drop the cited
claim, not to reopen an already-classified suppression pattern.

## Inputs

Supplied in the dispatch prompt:

| Field | Description |
| --- | --- |
| mode | `rubber-duck` (default) or `evidence` |
| findings | One or more findings that share `subject_path`, each as `Type — Subject — proposed change` (rubber-duck) or `object — file:line — "quoted snippet" — claimed problem` (evidence) |
| subject_path | Absolute path(s) to the subject file(s) the finding(s) target |
| findings_date | ISO date (`YYYY-MM-DD`) for the staleness `git log --since` boundary, or omitted to skip the staleness check |

The per-check procedures are **not** passed inline. Read them yourself from
`profile-al-dev-shared/knowledge/map-change-rubber-duck-checks.md` (Universal
U1–U3, the type-specific checks, and the Rubber-Duck Record Format).

## Outputs

- **rubber-duck mode:** one Rubber-Duck Record block per finding (see Output Format).
- **evidence mode:** one line per finding: `<object> — verified` or
  `<object> — dropped: <why it did not verify>`.

Return **only** these blocks — no preamble, no file dumps, no quoted source
beyond the short evidence snippet a record needs.

---

## Procedure

1. **Load checks.** Read
   `profile-al-dev-shared/knowledge/map-change-rubber-duck-checks.md` for the
   Universal checks, the type-specific check matching each finding's verb
   (Trim, Remodel, Split, Inline, Align, Connect, Merge, Promote, Extend,
   Atomise, Absorb), and the record format.

2. **Read the subject file(s)** at `subject_path` in full. Normalise absolute
   paths to the `profile-al-dev-shared/` (or `.claude/`) base when searching, per
   the doc's "File reference is absolute path" pattern (e.g., `sed 's|^.*/al-dev-shared/||'` to normalize paths before matching against the pattern).

3. **Run the checks** for each finding:

   - **rubber-duck mode:** apply Universal U1–U3, then the type-specific check.
     Map the duck verdict to the record vocabulary: `ACCEPT → proceed`,
     `REJECT → skip`, `DEFER → skip` (record the deferral reason).
   - **evidence mode:** open the cited `file:line`, confirm the quoted snippet
     is present within ±5 lines of the cited line number and the claimed problem still
     holds. Snippet present AND claimed problem still holds → `verified`.
     Snippet absent OR claim no longer true → `dropped: <reason>`. Partial or
     ambiguous cases → `dropped: ambiguous claim`.
   - **evidence mode — deterministic lint cross-check (mandatory, takes priority).**
     When a finding's claimed problem is a deterministic markdownlint rule —
     missing code-block language tag (MD040), trailing spaces (MD009), duplicate
     heading (MD024), first-line heading (MD041), and the like — you MUST NOT
     decide by eyeballing fences or counting lines (an LLM does this unreliably).
     Run the linter and decide from its output:

     ```bash
     ROOT=$(git rev-parse --show-toplevel)
     markdownlint --config "$ROOT/.markdownlint.json" "<subject_path>"
     ```

     The verdict for a lint-class finding is then purely: linter reports the
     matching rule at (or within a line or two of) the cited line → `verified`;
     linter reports no such violation → `dropped: markdownlint reports no <rule>
     at <file:line>`. Use this in place of the snippet-eyeballing check above for
     any lint-class claim. (If `markdownlint` is unavailable on PATH, fall back to
     the snippet check and append `— linter unavailable, verified by inspection`.)

4. **Staleness (if `findings_date` supplied).** For each distinct `subject_path`,
   run once:

   ```bash
   git log --since="<findings_date> 00:00" --oneline -- "<subject_path>"
   ```

   Non-empty output → add `Staleness: ⚠ possibly stale (<commits>)` to the
   record(s) for that subject; empty → omit the line (subject unchanged).

5. **Reject generated paths.** Any finding targeting `profile-al-dev-shared/generated/**`
   is an automatic `skip` — redirect to the canonical source per the doc.

6. **Return the records only.** Do not write any plan content, do not dump file
   contents, and do not include reasoning prose outside the record fields.

---

## Output Format

Return one line per finding in this exact format:

```
<finding_object> | <verdict> | <reason_one_liner> | <plan_anchor> | <fix_scope_delta>
```

**Fields:**

- `<finding_object>` — object slug from the finding (e.g., `tighten-return-schema`)
- `<verdict>` — one of: `proceed` (claim is substantiated), `skip` (claim is refuted or already covered), `modify` (partially substantiated, adjust scope)
- `<reason_one_liner>` — 1-line justification (e.g., "already implemented in Phase 3" or "claim contradicts live code")
- `<plan_anchor>` — file path and line range or skill name where implementation touches (e.g., "verify-health-finding.md §Output" or "plan-plugin-findings.md Phase 3")
- `<fix_scope_delta>` — change to scope vs original claim: "no change", "narrowed to", "expanded to include"

**Return ONLY the verdict line, no preamble.**

---
