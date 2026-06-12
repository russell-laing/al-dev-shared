# Superpowers Planning History

Current source of truth: active implementation guidance lives in the current shared plugin source and knowledge documents.

## 2026-06-12

### Tooling-Quality Clarity & Bloat Remediation Implementation Plan

- Path: `docs/superpowers/plans/archived/2026-06-12-plugin-map-tooling-quality-clarity.md`
- Kind: plan
- Status: implemented
- Summary: 2026-06-12 | tooling-quality clarity & bloat remediation | implemented; rows closed: [#595, #641, #637, #597, #640, #598, #599, #619, #620, #624, #625, #628, #629, #633, #642, #635, #604, #617, #606, #609, #611, #612, #614, #613, #615, #616, #621, #622, #623, #638]

## 2026-06-11

### Health-Loop Tooling & Plugin Clarity Fixes — 2026-06-11

- Path: `docs/superpowers/plans/archived/2026-06-11-plugin-map-health-loop-tooling-fixes.md`
- Kind: plan
- Status: implemented
- Summary: 2026-06-11 | health-loop tooling and plugin clarity fixes | implemented; rows closed: [#534, #339, #348, #561, #563, #556, #557, #558, #559, #560, #562]

### Tooling Quality — Clarity & Bloat Fixes — 2026-06-11 Implementation Plan

- Path: `docs/superpowers/plans/2026-06-11-tooling-quality-clarity.md`
- Kind: plan
- Status: implemented
- Summary: Closed tooling-surface quality findings #548–#555 (with #553 closed as already satisfied, no source change) after incorporating the 2026-06-11 consolidated plan review; routed eight out-of-scope executor and loop-contract findings to the disposition ledger as accepted rows #556–#563.

## 2026-06-07

### Tooling Health Fixes — 2026-06-07 Implementation Plan

- Path: `docs/superpowers/plans/2026-06-07-plugin-map-tooling-health-fixes.md`
- Kind: plan
- Status: historical
- Summary: Resolve only the 2026-06-07 tooling-surface findings that still reproduce against the live `.claude/` surface, retire stale or false-positive accepted rows before touching source, and close the surviving findings with atomic commits plus same-session ledger write-back.

### Tooling Bloat + Remodel Implementation Plan

- Path: `docs/superpowers/plans/2026-06-07-plugin-map-tooling-bloat-remodel.md`
- Kind: plan
- Status: superseded
- Summary: Reduce structural bloat in five tooling skills and two agents, based on accepted findings from the 2026-06-06 / 2026-06-07 tooling health dossiers, then record ledger closure for every resolved finding.

### Rubber-Duck Commentary: Tooling Health Fixes — 2026-06-07 Implementation Plan

- Path: `docs/superpowers/plans/2026-06-07-plugin-map-tooling-health-fixes-commentary.md`
- Kind: plan
- Status: implemented
- Summary: Source plan: `docs/superpowers/plans/2026-06-07-plugin-map-tooling-health-fixes.md`

### Rubber-Duck Commentary: Tooling Bloat + Remodel Implementation Plan

- Path: `docs/superpowers/plans/2026-06-07-plugin-map-tooling-bloat-remodel-commentary.md`
- Kind: plan
- Status: superseded
- Summary: Source plan: `docs/superpowers/plans/2026-06-07-plugin-map-tooling-bloat-remodel.md`

### Ledger Closure Cleanup Implementation Plan

- Path: `docs/superpowers/plans/2026-06-07-ledger-closure-cleanup.md`
- Kind: plan
- Status: abandoned
- Summary: Reconcile the 2026-06-07 health ledger so every resolved accepted finding has an explicit closure row, genuinely open findings stay open, and the stray local tooling-health dossier does not get bundled into the closure commit.

## 2026-06-06

### Design: Exclude Non-Workflow Tooling Skills from Plugin Health Audit

- Path: `docs/superpowers/specs/2026-06-06-tooling-health-scope-design.md`
- Kind: spec
- Status: historical
- Summary: **Date:** 2026-06-06 **Status:** Approved

### Tooling Quality Findings Implementation Plan

- Path: `docs/superpowers/plans/2026-06-06-plugin-map-tooling-quality.md`
- Kind: plan
- Status: superseded
- Summary: Apply the 27 rubber-duck-verified Quality findings from the 2026-06-06 tooling health dossier to the maintainer-tooling skills (`.claude/skills/`) and agents (`.claude/agents/`), with the dispositions ledger reconciled first as a baseline and per-finding closure recorded as each fix lands.

### Tooling Health Scope Filter Implementation Plan

- Path: `docs/superpowers/plans/2026-06-06-tooling-health-scope-filter.md`
- Kind: plan
- Status: historical
- Summary: Filter the `plugin-health-discover` tooling surface file list to include only skills with a `workflow:` frontmatter block, excluding adjacent tools that are not part of the self-healing loop.

### Rubber-Duck Commentary: Tooling Quality Findings Implementation Plan

- Path: `docs/superpowers/plans/2026-06-06-plugin-map-tooling-quality-commentary.md`
- Kind: plan
- Status: superseded
- Summary: Source plan: `docs/superpowers/plans/2026-06-06-plugin-map-tooling-quality.md`

### Rubber-Duck Commentary: Tooling Health Scope Filter Implementation Plan

- Path: `docs/superpowers/plans/2026-06-06-tooling-health-scope-filter-commentary.md`
- Kind: plan
- Status: implemented
- Summary: Source plan: `docs/superpowers/plans/2026-06-06-tooling-health-scope-filter.md`

### Maintainer Tooling Readability Generator Implementation Plan

- Path: `docs/superpowers/plans/2026-06-06-maintainer-tooling-readability-generator.md`
- Kind: plan
- Status: historical
- Summary: Resolve the readability and accuracy findings in `docs/health/2026-06-06-maintainer-tooling-readability-accuracy.md` by updating the maintainer guide generator, relevant source workflow contracts, and the human-authored guide text that surrounds generated diagrams.

## 2026-06-05

### Self-Healing Maintainer Guide — Design

- Path: `docs/superpowers/specs/2026-06-05-self-healing-maintainer-guide-design.md`
- Kind: spec
- Status: historical
- Summary: Date: 2026-06-05 Status: approved

### Self-Healing Maintainer Guide Implementation Plan

- Path: `docs/superpowers/plans/2026-06-05-self-healing-maintainer-guide.md`
- Kind: plan
- Status: superseded
- Summary: Make `docs/maintainer-tooling.md` largely auto-generated from structured `workflow:` frontmatter contracts in each maintainer SKILL.md, so the guide that documents the self-healing loop self-heals.

### Rubber-Duck Commentary: Self-Healing Maintainer Guide Plan

- Path: `docs/superpowers/plans/2026-06-05-self-healing-maintainer-guide-commentary.md`
- Kind: plan
- Status: historical
- Summary: Source plan: `docs/superpowers/plans/2026-06-05-self-healing-maintainer-guide.md`

### Rename verify-map-suggestions → plan-health-findings Implementation Plan

- Path: `docs/superpowers/plans/2026-06-05-plugin-map-rename-planner.md`
- Kind: plan
- Status: historical
- Summary: Rename the maintainer planning skill to match its actual behaviour (a rubber-duck-to-plan pipeline over health findings), widen its description, and settle the name in the disposition ledger so this third rename is the last.

### Plugin Map Health Findings Implementation Plan

- Path: `docs/superpowers/plans/2026-06-05-plugin-map-health-findings.md`
- Kind: plan
- Status: implemented
- Summary: Implement the 11 accepted-and-open health-audit findings (from `docs/health/dispositions.md`) that survived rubber-ducking against the live codebase, as 10 atomic commits.

### Plugin Health Cleanups (2026-06-05 sweep) Implementation Plan

- Path: `docs/superpowers/plans/2026-06-05-plugin-map-health-cleanups.md`
- Kind: plan
- Status: implemented
- Summary: Implement the accepted, rubber-duck-verified findings from the 2026-06-05 plugin health dossier (`docs/health/2026-06-05-plugin-health.md`) — clarity fixes, bloat→knowledge extractions, structure/language-tag cleanups, a caller-alignment fix, four agent renames, and one breaking skill move.

### Accepted Health Findings (2026-06-05 Top-5) Implementation Plan

- Path: `docs/superpowers/plans/2026-06-05-plugin-map-accepted-health-fixes.md`
- Kind: plan
- Status: implemented
- Summary: Implement the five `accepted` ledger rows from the 2026-06-05 plugin dossier (dispositions ledger rows dated 2026-06-05, appended by `/record-health-dispositions`), each verified against the live codebase by a mandatory rubber-duck pass.

### /record-health-dispositions Maintainer Skill Implementation Plan

- Path: `docs/superpowers/plans/2026-06-05-record-health-dispositions-skill.md`
- Kind: plan
- Status: implemented
- Summary: Add a repo-local maintainer skill that records accept/decline/grandfather/fixed decisions for health-audit findings into `docs/health/dispositions.md`, closing the only phase of the health loop without a skill.

## 2026-06-04

### Plugin Map High-Severity Fixes Implementation Plan

- Path: `docs/superpowers/plans/2026-06-04-plugin-map-high-severity-fixes.md`
- Kind: plan
- Status: implemented
- Summary: Remediate the 9 confirmed-open High-severity findings from the 2026-06-04 plugin + tooling health dossiers, after rubber-ducking each against live code.
2026-06-13 | plugin-quality-commit-agents | implemented; rows closed: [#676, #677, #678, #679, #681, #682, #683, #685, #686, #687, #688, #689, #690, #691, #692]
