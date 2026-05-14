# Design: Trim md-mermaid-helper.md Context Cost

**Date:** 2026-05-14
**Status:** Draft
**File:** `profile-al-dev-shared/markdown/md-mermaid-helper.md`

---

## Problem

`md-mermaid-helper.md` carries `applyTo: "**/*.{md,mmd}"` in its frontmatter, causing it to
auto-load in every markdown and Mermaid session — ~800 tokens added to every session
where any `.md` file is open, regardless of whether Mermaid diagrams are involved.

## File Content Analysis

Reading the file reveals that **nearly all content is Mermaid-specific**:

- Numbered rules 1–12: Mermaid syntax constraints
- "Rules for All Diagrams" section: still diagram-specific (classDef, node labels, color palette)
- Color palette table: purely Mermaid styling
- Flowchart, Sequence, ERD sections: diagram-type-specific syntax
- Error Prevention Checklist: all Mermaid-specific items

There is no content that applies to general markdown but not to Mermaid diagrams. The
"universal" subset from Option B (split) is effectively empty.

## Usage Context

This repo contains no standalone `.mmd` files; Mermaid diagrams appear as fenced blocks
inside `.md` files (skills, knowledge docs, agent definitions). Verify during implementation
with `grep -rl '```mermaid' profile-al-dev-shared/`. Narrowing `applyTo` to `*.mmd` would
therefore miss the actual usage pattern.

## Options

| Option | Mechanism | Tokens saved | Trade-off |
|--------|-----------|-------------|-----------|
| A: Narrow to `*.mmd` | `applyTo: "**/*.mmd"` | ~800 in most sessions | Misses diagrams embedded in `.md` files — the common case |
| B: Split file | Keep 2–3 "universal" rules in auto-load; move rest to on-demand | same as C (~800) — universal subset is empty, so nothing remains in auto-load | Splitting is artificial — no content qualifies as truly universal |
| C: Pure on-demand | Remove frontmatter; agents load explicitly | ~800 in all sessions | Requires explicit load convention; agents may omit it |

## Recommendation: Option C (Pure On-Demand)

Option B collapses to Option C once the file is analyzed — there is nothing worth keeping
in an always-load subset. Option A saves tokens in most sessions but silently degrades
quality for inline diagram work (the primary use case). Option C is the cleanest solution.

**Risk mitigation for Option C:** the explicit load convention must be documented clearly
enough that agents reliably load the file when writing diagrams. This is the only failure
mode worth guarding against.

## Implementation

### Step 1: Remove the auto-load frontmatter

Remove `applyTo: "**/*.{md,mmd}"` from `md-mermaid-helper.md`. The file becomes a pure
knowledge document.

### Step 2: Add discoverability reference

The file now has no auto-load trigger, so agents must know it exists. The right hook point
depends on the environment:

- **Copilot CLI**: add a one-line reference in `AGENTS.md` under a "Diagram guidance" entry
  (Copilot CLI reads `AGENTS.md`, not `CLAUDE.md`)
- **Claude Code**: add the same reference in `CLAUDE.md`

```
Mermaid diagram rules: profile-al-dev-shared/markdown/md-mermaid-helper.md
```

### Step 3: Update agent and skill instructions

Find all agents and skills that write or review diagrams:

```bash
grep -rlE 'mermaid|diagram' profile-al-dev-shared/agents/ profile-al-dev-shared/skills/
grep -rl 'md-mermaid-helper' profile-al-dev-shared/ .github/
```

For each match that produces diagram output, add an explicit read instruction before the
diagram-writing step:

> When writing or reviewing Mermaid diagrams, read
> `profile-al-dev-shared/markdown/md-mermaid-helper.md` before writing any diagram blocks.

## Success Criteria

- [ ] Frontmatter removed from `md-mermaid-helper.md`
- [ ] All agent/skill files that write diagrams have an explicit load instruction
- [ ] No regression: at least one diagram produced in a new session correctly applies classDef rules and the color palette when the agent follows the Step 3 explicit load instruction
- [ ] ~800 tokens no longer added to non-diagram markdown sessions

## Related

- `docs/superpowers/specs/2026-05-14-mermaid-helper-enforcement-design.md` — companion
  spec on enforcement; both share the same file as their subject
- `profile-al-dev-shared/markdown/md-mermaid-helper.md` — the file being modified
- `.github/prompts/trim-md-mermaid-helper.md` — the prompt this spec supersedes
