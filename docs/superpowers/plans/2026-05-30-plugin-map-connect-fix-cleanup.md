# Plugin Map Connect /al-dev-fix Cleanup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Mark the open "Connect: Clarify `/al-dev-fix` escalation boundaries" suggestion in `docs/al-dev-skills-map.md` as confirmed implemented, consistent with the Extension opportunities #2 entry already present in the same file.

**Architecture:** Single documentation edit. The Architectural suggestions section at line 685 still carries open suggestion text; the Extension opportunities section at line 822 already carries the ✅ confirmed verdict written on 2026-05-29. The edit brings the two sections into agreement. A stale superseded plan file is also deleted as housekeeping.

**Tech Stack:** Markdown only. No source files, skill files, or agent files change.

---

## File Structure

| File | Change |
|---|---|
| `docs/al-dev-skills-map.md` | Replace open Connect block (lines 683–697) with ✅ confirmed entry |
| `docs/superpowers/plans/2026-05-29-plugin-map-stale-observations-cleanup.md` | Delete — superseded; Task 1 already done, Task 2 had wrong filename |

---

### Task 1: Replace open Connect block with ✅ confirmed entry and delete stale plan

**Files:**
- Modify: `docs/al-dev-skills-map.md`
- Delete: `docs/superpowers/plans/2026-05-29-plugin-map-stale-observations-cleanup.md`

- [ ] **Step 1: Confirm the exact text to replace**

```bash
grep -n "Connect.*fix\|routing clarity\|escalation boundaries" \
  docs/al-dev-skills-map.md
```

Expected output:
```
685:**Connect: Clarify `/al-dev-fix` escalation boundaries**
822:2. **✅ Confirmed implemented: `/al-dev-fix` routing clarity** ...
```

If line 685 is absent or shows a different line number, read lines 680–700 of the file and adjust the old_string below to match exactly.

- [ ] **Step 2: Apply the edit**

Use the Edit tool with these exact strings:

**old_string:**
```
---

**Connect: Clarify `/al-dev-fix` escalation boundaries**

Observation: The core propagation work is already present. `/al-dev-fix` now:
- loads prior lint findings on the non-trivial path
- dispatches an architect for non-trivial fixes
- explicitly tells that architect to follow `knowledge/al-symbol-pre-flight.md`

The remaining asymmetry is documentation: `profile-al-dev-shared/knowledge/workflow-routing.md` still describes `/al-dev-fix` as if it were always a direct trivial edit with no planning branch.

Suggestion: Treat symbol pre-flight reuse as implemented for the non-trivial `/al-dev-fix` path. The remaining follow-up is to align routing guidance so `/al-dev-fix` is documented as a fast-fix entrypoint that may escalate to quick architect analysis when the issue is ambiguous, multi-file, or integration-heavy.

Trade-off: Slightly more nuanced routing prose. Improvement: removes false expectations about `/al-dev-fix`, makes existing symbol-rigor behavior discoverable, and avoids adding prompt weight to truly trivial fixes without evidence.
```

**new_string:**
```
---

**✅ Confirmed implemented: Connect `/al-dev-fix` escalation boundaries** (2026-05-29)
`workflow-routing.md` lines 40–46 already document the non-trivial architect escalation path explicitly. No prose update needed.
```

- [ ] **Step 3: Verify the edit**

```bash
grep -n "Connect.*fix\|routing clarity\|escalation" docs/al-dev-skills-map.md
```

Expected: two lines, both containing ✅ (one in Architectural suggestions, one in Extension opportunities).

```bash
grep -c "✅" docs/al-dev-skills-map.md
```

Expected: count increases by 1 vs the pre-edit state (was N, now N+1 — the new ✅ in Architectural suggestions).

- [ ] **Step 4: Delete the stale plan file**

```bash
rm docs/superpowers/plans/2026-05-29-plugin-map-stale-observations-cleanup.md
```

Verify it's gone:

```bash
ls docs/superpowers/plans/2026-05-29-plugin-map-stale-observations-cleanup.md 2>&1
```

Expected: `No such file or directory`.

- [ ] **Step 5: Verify git status**

```bash
git status docs/
```

Expected:
```
modified:   docs/al-dev-skills-map.md
```

The stale plan was untracked, so deleting it produces no git entry. No unexpected modified or new files.

- [ ] **Step 6: Commit**

```bash
git add docs/al-dev-skills-map.md
git commit -m "$(cat <<'EOF'
docs(plugin-map): mark Connect /al-dev-fix suggestion as confirmed implemented

workflow-routing.md lines 40-46 already document the non-trivial architect
escalation path. Extension opportunities #2 in the same file confirmed this
on 2026-05-29; Architectural suggestions block not updated at that time.

Stale plan 2026-05-29-plugin-map-stale-observations-cleanup.md deleted —
superseded and never committed; its Task 1 was already done and Task 2
referenced a non-existent filename.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
)"
```

Verify commit:

```bash
git log --oneline -n 1
```

Expected: commit message starts with `docs(plugin-map): mark Connect /al-dev-fix suggestion`.
