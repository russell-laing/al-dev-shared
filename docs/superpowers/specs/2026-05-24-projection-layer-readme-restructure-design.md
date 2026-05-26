# Design: Projection Layer README Restructure

**Date:** 2026-05-24  
**Audience:** Project maintainers (primary), with auxiliary content for contributors and harness developers  
**Goal:** Improve document structure and flow to be task-driven and maintainer-focused

---

## Problem Statement

The current `docs/projection-layer-readme.md` is structured around architectural concepts and technical details. While conceptually accurate, it doesn't serve the primary audience—project maintainers—well because it doesn't flow around the tasks maintainers actually perform. Readers struggle to find:

- When and how to regenerate projections
- What they can edit vs. what's generated (boundary rules)
- How to add a new agent or skill safely
- How to validate harness neutrality

The document feels disjointed because it jumps between abstract mechanics, deep implementation details, and specific examples without a clear narrative that serves a maintainer's workflow.

---

## Solution: Task-Driven Narrative

Restructure around the four core maintenance workflows:

1. **Adding a new agent/skill** — from authored source through validation
2. **Regenerating projections safely** — when, why, how, verification
3. **Validating harness neutrality** — the safety check and common pitfalls
4. **Understanding boundaries** — what's sacred, what's yours to edit

This structure ensures a maintainer can:
- Navigate to the task they need to perform
- Understand the concepts in context, not in isolation
- Use diagrams to visualize workflows, not just architecture
- Know when and why to use validator scripts

---

## New Structure

### Section 1: Conceptual Foundation
**Purpose:** Establish why the projection layer exists and the mental model

- **What problem does it solve?** One canonical authored surface, three harnesses needing native tools
- **The solution:** Projection layer translates generic capabilities to harness-native names
- **Key insight:** Shared source stays neutral; generated artifacts are harness-specific

**Content:**
- Brief problem/solution explanation (2-3 paragraphs)
- **Diagram (kept):** End-to-end flow showing Shared → Policy → Generator → Claude/Copilot/Codex outputs
  - This diagram establishes the conceptual model and defines the three core pieces

### Section 2: Boundary Rules (Critical for Maintainers)
**Purpose:** Make explicit what maintainers can and cannot edit

- **Sacred files:** `profile-al-dev-shared/agents/*.md`, `profile-al-dev-shared/knowledge/agent-tool-projection-policy.md`
  - These are canonical authored source—edit directly
- **Generated files:** `profile-al-dev-shared/generated/agents/**` (claude, copilot, codex subdirs)
  - Never hand-edit—only regenerate via script
- **Why this boundary exists:** Prevents manual edits from being lost on regeneration, ensures all three harnesses stay in sync
- **Validation:** Neutrality validator catches leakage of harness-specific tokens into shared source

**Content:**
- Clear, concise boundary statement
- List of files in each category
- Explanation of why the boundary matters

### Section 3: Workflow — Adding a New Agent or Skill
**Purpose:** Walk a maintainer through the full process of adding new content safely

**Steps:**
1. Author the shared source file (`profile-al-dev-shared/agents/<name>.md` or `profile-al-dev-shared/skills/<name>/SKILL.md`)
   - Use generic capability names (no harness-specific tokens like `AskUserQuestion`, `ask_user`, etc.)
   - Follow the frontmatter and body conventions
2. Regenerate projections
   - Run: `python3 scripts/generate-agent-projections.py`
   - This creates harness-native versions in `generated/agents/claude/`, `generated/agents/copilot/`, `generated/agents/codex/`
3. Validate harness neutrality
   - Run: `python3 scripts/validate_harness_neutrality.py profile-al-dev-shared`
   - Ensures no harness-specific tokens leaked into shared source
4. Commit the changes
   - Staged: shared source file + generated projection files
   - Message notes what was added and why

**Example:**
- Walk through adding a hypothetical new agent or skill (concrete, not abstract)
- Show the authored source, regeneration output, validation success

**Diagram (new or adjusted):**
- Simple flow: Author Shared Source → Regenerate Projections → Validate Harness Neutrality → Commit
- This is the maintainer's workflow, not the architecture

### Section 4: Regenerating Projections Safely
**Purpose:** Help maintainers understand when and how to regenerate, and verify results

**When to regenerate:**
- After editing any file in `profile-al-dev-shared/agents/*.md`
- After editing the projection policy in `profile-al-dev-shared/knowledge/agent-tool-projection-policy.md`
- After editing shared knowledge that affects tool descriptions

**How:**
- Run: `python3 scripts/generate-agent-projections.py`
- The script reads shared source and policy, outputs generated artifacts in-place

**Verification:**
- Check `git status` to see what changed
- Review diffs to ensure changes are expected (no accidental deletions, no mysterious additions)
- Run validation (see Section 5)

**Diagram (recontextualized from current "Skill Execution Flow"):**
- Show what happens when regenerate runs: policy maps capabilities to harness names, generator outputs claude/*.md, copilot/*.md, codex/*.toml
- This diagram is now in the context of "how projections get created" not "how Claude Code executes"

### Section 5: Validating Harness Neutrality
**Purpose:** Explain the safety check and how to resolve violations

**The check:**
- `python3 scripts/validate_harness_neutrality.py profile-al-dev-shared`
- Scans shared source files for forbidden harness-specific tokens (e.g., `AskUserQuestion`, `ask_user`, `mcp__`, TOML keys)
- Ensures the shared surface stays generic

**Common pitfalls:**
- Accidentally naming a tool `AskUserQuestion` in shared source instead of the generic `USER_GATE`
- Including harness-specific prefixes in agent descriptions
- Copying a generated projection back into shared source by mistake

**How to fix violations:**
- Replace harness-specific names with generic equivalents (reference `knowledge/harness-concepts.md`)
- Re-run validation to confirm
- Regenerate projections to update outputs

---

## Appendices

### Appendix A: Files Reference
Quick lookup table:
- Shared source locations
- Projection policy location
- Generated artifact locations (per harness)
- Generator script
- Validator script
- Tests

### Appendix B: Claude Code Worktree Integration
**For context and advanced usage; not required for basic maintenance**

- How Claude Code discovers and loads projections
- Worktree lifecycle (creation, execution, cleanup)
- How the regeneration script works *within* a worktree
- Concrete example: adding a feature to al-dev-shared and testing in a worktree

**Includes (recontextualized):**
- The existing Claude Code worktree integration example section (moved here)
- The skill execution flow diagram (now in context of "how Claude Code runs a skill in the worktree")

### Appendix C: Harness Developer Reference
**For contributors adding new harnesses or consuming the plugin**

- What each harness consumes
  - Claude Code: `generated/agents/claude/*.md`
  - Copilot CLI: `generated/agents/copilot/*.md`
  - Codex: `generated/agents/codex/*.toml`
- Tool projection examples (from existing "What Each Harness Uses" section)
- How the projection policy defines the mapping
- Common questions for harness developers

---

## Diagram Treatment

**Kept as-is:**
- End-to-end flow (Shared → Policy → Generator → outputs) — now in Section 1 to establish the mental model
- Skill execution flow — moved to Appendix B, recontextualized to show worktree execution

**New or adjusted:**
- Maintainer workflow diagram (Author → Regenerate → Validate → Commit) — Section 3
- Optional: visual representation of boundary rules (what's editable, what's generated)

**Rationale:** Diagrams stay; context changes so they serve the primary audience.

---

## Benefits of This Structure

1. **Task-driven:** Maintainers see their workflows, not just architecture
2. **Boundary-first:** Rules are stated clearly and early, not scattered
3. **Procedural:** Each section includes concrete steps and commands
4. **Layered for audience:** Appendices serve contributors and harness developers without interrupting the main narrative
5. **Diagrams in context:** Mermaid diagrams illustrate workflows and architecture, not abstract concepts alone

---

## Content Checklist

- [ ] Section 1: Conceptual foundation (2-3 paragraphs, end-to-end flow diagram)
- [ ] Section 2: Boundary rules (clear, list files, explain why)
- [ ] Section 3: Adding agent/skill workflow (steps, example, diagram)
- [ ] Section 4: Regenerating projections (when, how, verify)
- [ ] Section 5: Validating harness neutrality (check, pitfalls, fixes)
- [ ] Appendix A: Files reference (quick lookup)
- [ ] Appendix B: Worktree integration (recontextualized sections)
- [ ] Appendix C: Harness developer reference (what each harness consumes)
- [ ] All existing Mermaid diagrams preserved and repositioned

---

## Scope Boundaries

**In scope:**
- Restructure current content into task-driven narrative
- Reposition diagrams for better context
- Clarify boundary rules and validator scripts
- Add maintainer-focused workflows

**Out of scope:**
- Adding new features or capabilities to the projection system
- Changing the projection policy itself
- Rewriting agent/skill requirements

---

## Success Criteria

1. A maintainer can find how to add a new agent or skill in one place
2. Boundary rules are stated clearly and early
3. The document flows around maintenance tasks, not abstract architecture
4. Diagrams illustrate workflows, not just mechanics
5. The document remains a conceptual explanation (not a reference only)
6. Contributors and harness developers have auxiliary sections without interrupting the main narrative
