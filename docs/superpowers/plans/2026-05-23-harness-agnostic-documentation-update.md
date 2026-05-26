# Harness-Agnostic Documentation Update Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Update CLAUDE.md and related documentation to accurately reflect that `al-dev-shared` is a multi-harness plugin consumed by Claude Code, Copilot CLI, and Codex, with equal projection support across all three.

**Architecture:** The plugin uses a projection layer that maintains one canonical authored surface (shared agents, skills, knowledge) and generates harness-native artifacts for three consumers. CLAUDE.md must be rewritten from a "Claude Code plugin" perspective to a "multi-harness shared plugin" perspective. Supporting docs will be added to clarify the multi-harness validation workflow.

**Tech Stack:** Markdown documentation; no code changes required.

---

## Validation Summary

✅ **Harness Neutrality:** `python3 scripts/validate_harness_neutrality.py profile-al-dev-shared` passes — no harness-specific tokens in shared source.

✅ **Projection Completeness:** 19 agents in source → 19 Claude projections, 19 Copilot projections, 19 Codex projections.

✅ **Projection Policy:** Documented in `knowledge/agent-tool-projection-policy.md` with clear mappings for Claude, Copilot, and Codex.

✅ **Harness Concepts:** Generic vocabulary defined in `knowledge/harness-concepts.md` with concrete translations per harness.

**Findings requiring documentation updates:**

❌ CLAUDE.md describes the plugin as "Claude Code plugin marketplace" but does not mention Copilot CLI or Codex as first-class consumers.

❌ "Repo-Local Maintainer Tooling" section doesn't clarify that `.claude/` outputs must remain harness-agnostic (no harness-specific tokens in shared files or `.dev/` documents).

❌ "Development Commands" section lacks guidance on multi-harness validation.

❌ No cross-reference to `projection-layer-readme.md` which explains the three-harness architecture.

---

## File Structure

- **Modify:** `CLAUDE.md` — Rewrite to reflect multi-harness architecture
- **Create:** `CODEX.md` — Codex-specific guidance (parallel to CLAUDE.md)
- **Create:** `AGENTS.md` — Copilot CLI-specific guidance (parallel to CLAUDE.md)
- **Modify:** `docs/projection-layer-readme.md` — Add section on documentation boundaries

---

## Tasks

### Task 1: Rewrite CLAUDE.md Header and Overview

**Files:**
- Modify: `CLAUDE.md` (header section, lines 1-16)

- [ ] **Step 1: Read current CLAUDE.md header section**

```bash
sed -n '1,20p' CLAUDE.md
```

Expected: Header describes "Claude Code plugin marketplace"; "## Structure" appears around line 17

- [ ] **Step 2: Find the exact line where "## Structure" begins**

```bash
grep -n "^## Structure" CLAUDE.md
```

Expected: Returns a line number (should be 17)

- [ ] **Step 3: Create a temporary file with the new header**

```bash
cat > /tmp/new_header.md << 'EOF'
# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with this repository.

## What This Repo Is

`al-dev-shared` is a **shared AI development plugin** — a unified library of AL/BC development skills, agents, and knowledge documents consumed by three AI coding harnesses:

- **Claude Code** (claude.ai/code) — Desktop app, CLI, and IDE extensions
- **Copilot CLI** — Autonomous command-line agent (see `AGENTS.md`)
- **Codex** — Autonomous development system (see `CODEX.md`)

It maintains one canonical authored surface (`profile-al-dev-shared/`) and generates harness-native projection artifacts for each consumer. This document covers Claude Code registration and usage; refer to `AGENTS.md` (Copilot CLI) and `CODEX.md` (Codex) for harness-specific guidance.

This repository is not itself an AL project; it contains no `.al` source files.

### Claude Code Registration

`al-dev-shared` is registered in `~/.claude/settings.json` as:

```json
"al-dev-shared": {
  "source": { "source": "directory", "path": "/Users/russelllaing/al-dev-shared" }
}
```

Claude Code consumes:
- **Shared skills** from `profile-al-dev-shared/skills/`
- **Generated agent projections** from `profile-al-dev-shared/generated/agents/claude/`
- **Shared knowledge** from `profile-al-dev-shared/knowledge/` and `bc-code-intel-knowledge/`
EOF
```

Expected: Temporary file created

- [ ] **Step 4: Replace the header section in CLAUDE.md**

```bash
LINE_NUM=$(grep -n "^## Structure" CLAUDE.md | cut -d: -f1) && \
{ cat /tmp/new_header.md; tail -n +$LINE_NUM CLAUDE.md; } > CLAUDE.md.tmp && \
mv CLAUDE.md.tmp CLAUDE.md
```

Expected: Lines 1-16 replaced; "## Structure" now begins the section after the new header

- [ ] **Step 5: Verify changes by reading the modified section**

```bash
head -50 CLAUDE.md
```

Expected: Header now mentions Claude Code, Copilot CLI, and Codex as co-consumers; "## Structure" appears below.

- [ ] **Step 6: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: update CLAUDE.md header to acknowledge multi-harness plugin model"
```

---

### Task 2: Update Structure Section to Clarify Shared vs Generated

**Files:**
- Modify: `CLAUDE.md` (Structure section)

- [ ] **Step 1: Find the Structure section boundaries**

```bash
STRUCT_START=$(grep -n "^## Structure" CLAUDE.md | cut -d: -f1) && \
REPO_LOCAL_START=$(grep -n "^## Repo-Local Maintainer Tooling" CLAUDE.md | cut -d: -f1) && \
echo "Structure: lines $STRUCT_START to $((REPO_LOCAL_START - 1))"
```

Expected: Returns line numbers for the Structure section (should be around 17-28)

- [ ] **Step 2: Read the current Structure section**

```bash
STRUCT_START=$(grep -n "^## Structure" CLAUDE.md | cut -d: -f1) && \
REPO_LOCAL_START=$(grep -n "^## Repo-Local Maintainer Tooling" CLAUDE.md | cut -d: -f1) && \
sed -n "${STRUCT_START},$((REPO_LOCAL_START - 1))p" CLAUDE.md
```

Expected: Shows current directory structure

- [ ] **Step 3: Create a temporary file with the new sections**

```bash
cat > /tmp/new_structure.md << 'EOF'
## Shared Plugin Surface (All Harnesses)

All three harnesses consume the same authored source:

```text
profile-al-dev-shared/          # Canonical authored plugin surface
  skills/<name>/SKILL.md        # Skill definitions (invoked as /name)
  agents/<name>.md              # Agent definitions (harness-neutral)
  knowledge/                    # Generic workflow knowledge
  bc-code-intel-knowledge/      # BC Code Intelligence specialist knowledge
  markdown/                     # Markdown and Mermaid style guides
.claude-plugin/marketplace.json # Marketplace registration (Claude Code only)
```

## Generated Projection Artifacts (Per-Harness Native Formats)

For harness-native tool execution, the projection layer generates harness-specific artifacts:

```text
profile-al-dev-shared/generated/agents/
  claude/                       # Claude Code-native agent projections (Markdown)
  copilot/                      # Copilot CLI-native agent projections (Markdown)
  codex/                        # Codex-native agent projections (TOML)
```

Each projection applies the mappings from `knowledge/agent-tool-projection-policy.md` to translate generic capability names (e.g., `USER_GATE`, `Read`, `Bash`) into harness-native tool names (e.g., `AskUserQuestion`, `read`, `execute`).

**Key rule:** Shared source is canonical; generated artifacts are derived output and must never be hand-edited.

EOF
```

- [ ] **Step 4: Replace the Structure section**

```bash
STRUCT_START=$(grep -n "^## Structure" CLAUDE.md | cut -d: -f1) && \
REPO_LOCAL_START=$(grep -n "^## Repo-Local Maintainer Tooling" CLAUDE.md | cut -d: -f1) && \
{ head -n $((STRUCT_START - 1)) CLAUDE.md; cat /tmp/new_structure.md; tail -n +$REPO_LOCAL_START CLAUDE.md; } > CLAUDE.md.tmp && \
mv CLAUDE.md.tmp CLAUDE.md
```

Expected: Structure section replaced; "## Repo-Local Maintainer Tooling" still follows

- [ ] **Step 5: Verify by reading the modified sections**

```bash
grep -n "^## " CLAUDE.md | head -10
```

Expected: Section headers in correct order (Structure, then Repo-Local, then Skill File Format, etc.)

- [ ] **Step 6: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: clarify shared plugin surface and projection layer in CLAUDE.md"
```

---

### Task 3: Update Repo-Local Maintainer Tooling Section

**Files:**
- Modify: `CLAUDE.md` (Repo-Local Maintainer Tooling section)

- [ ] **Step 1: Find the Repo-Local section boundaries**

```bash
REPO_START=$(grep -n "^## Repo-Local Maintainer Tooling" CLAUDE.md | cut -d: -f1) && \
SKILL_START=$(grep -n "^## Skill File Format" CLAUDE.md | cut -d: -f1) && \
echo "Repo-Local: lines $REPO_START to $((SKILL_START - 1))"
```

Expected: Returns line numbers for the Repo-Local section

- [ ] **Step 2: Read the current Repo-Local section**

```bash
REPO_START=$(grep -n "^## Repo-Local Maintainer Tooling" CLAUDE.md | cut -d: -f1) && \
SKILL_START=$(grep -n "^## Skill File Format" CLAUDE.md | cut -d: -f1) && \
sed -n "${REPO_START},$((SKILL_START - 1))p" CLAUDE.md
```

Expected: Only mentions `.claude/agents/` and `.claude/skills/`

- [ ] **Step 3: Create a temporary file with the expanded section**

```bash
cat > /tmp/new_repo_local.md << 'EOF'
## Repo-Local Maintainer Tooling

`profile-al-dev-shared/` is the shared authored plugin surface distributed to all three harnesses.

`.claude/agents/` and `.claude/skills/` contain Claude Code-specific maintainer tooling used to review, audit, and improve the shared plugin surface. This tooling is currently Claude-specific; future harnesses may have parallel tooling (`.agents/`, `.codex/`, etc.).

**Output boundary rule:** While the maintainer tooling is harness-specific, its **outputs must be harness-agnostic**:
- Any documents written to the shared surface or `.dev/` directory must not contain harness-specific tokens
- Changes made to shared files must use generic vocabulary (from `knowledge/harness-concepts.md`)
- Generated artifacts remain the output of the projection layer, never hand-edited by maintainer tooling

Repo-local tooling may *inspect* shared source and generated projection outputs for analysis, but its modifications or documents must maintain neutrality across all three harnesses.

EOF
```

- [ ] **Step 4: Replace the Repo-Local section**

```bash
REPO_START=$(grep -n "^## Repo-Local Maintainer Tooling" CLAUDE.md | cut -d: -f1) && \
SKILL_START=$(grep -n "^## Skill File Format" CLAUDE.md | cut -d: -f1) && \
{ head -n $((REPO_START - 1)) CLAUDE.md; cat /tmp/new_repo_local.md; tail -n +$SKILL_START CLAUDE.md; } > CLAUDE.md.tmp && \
mv CLAUDE.md.tmp CLAUDE.md
```

- [ ] **Step 5: Verify by reading the updated section**

```bash
grep -n "^## " CLAUDE.md | head -8
```

Expected: Section headers show Repo-Local updated correctly

- [ ] **Step 6: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: clarify repo-local maintainer tooling boundaries in CLAUDE.md"
```

---

### Task 4: Update Development Commands Section

**Files:**
- Modify: `CLAUDE.md` (Development Commands section)

- [ ] **Step 1: Find the Development Commands and following sections**

```bash
DEV_START=$(grep -n "^## Development Commands" CLAUDE.md | cut -d: -f1) && \
UPDATE_START=$(grep -n "^## Updating Documentation Maps" CLAUDE.md | cut -d: -f1) && \
echo "Development Commands: lines $DEV_START to $((UPDATE_START - 1))"
```

Expected: Returns line numbers for the Development Commands section

- [ ] **Step 2: Read the current section**

```bash
DEV_START=$(grep -n "^## Development Commands" CLAUDE.md | cut -d: -f1) && \
UPDATE_START=$(grep -n "^## Updating Documentation Maps" CLAUDE.md | cut -d: -f1) && \
sed -n "${DEV_START},$((UPDATE_START - 1))p" CLAUDE.md
```

Expected: Shows Python validators and plugin health daemon

- [ ] **Step 3: Create a temporary file with the new multi-harness guidance**

```bash
cat > /tmp/new_dev_commands.md << 'EOF'
## Development Commands

Common commands for maintaining the shared plugin surface:

### Validation (All Harnesses)

```bash
# Validate that shared source has no harness-specific leakage
python3 scripts/validate_harness_neutrality.py profile-al-dev-shared

# Validate agent structure (frontmatter, tools, model assignment)
python3 scripts/validate-lens-agents.py --path profile-al-dev-shared/agents

# Validate knowledge file quality
python3 scripts/validate-knowledge-quality.py --path profile-al-dev-shared/knowledge
```

### Projection (Harness-Native Artifacts)

```bash
# Regenerate all harness projections after shared agent/policy changes
python3 scripts/generate-agent-projections.py

# Verify generated artifacts match shared source across all three harnesses
# (run after any projection policy or agent updates)
```

### Plugin Health and Documentation

```bash
# Run plugin health daemon (audit sweep with auto-fix)
bash scripts/plugin-health-daemon.sh --dry-run    # preview changes
bash scripts/plugin-health-daemon.sh --execute    # apply changes and create PR
```

EOF
```

- [ ] **Step 4: Replace the Development Commands section**

```bash
DEV_START=$(grep -n "^## Development Commands" CLAUDE.md | cut -d: -f1) && \
UPDATE_START=$(grep -n "^## Updating Documentation Maps" CLAUDE.md | cut -d: -f1) && \
{ head -n $((DEV_START - 1)) CLAUDE.md; cat /tmp/new_dev_commands.md; tail -n +$UPDATE_START CLAUDE.md; } > CLAUDE.md.tmp && \
mv CLAUDE.md.tmp CLAUDE.md
```

Expected: Development Commands section replaced with multi-harness guidance

- [ ] **Step 5: Verify by checking the section headers**

```bash
grep -n "^## Updating Documentation Maps" CLAUDE.md
```

Expected: Section follows Development Commands

- [ ] **Step 6: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: add multi-harness validation guidance to Development Commands"
```

---

### Task 5: Create AGENTS.md for Copilot CLI

**Files:**
- Create: `AGENTS.md`

- [ ] **Step 1: Create AGENTS.md with Copilot CLI guidance**

```bash
cat > AGENTS.md << 'EOF'
# AGENTS.md

This file provides guidance to Copilot CLI when working with this repository.

## What This Repo Is

`al-dev-shared` is a **shared AI development plugin** — a unified library of AL/BC development skills, agents, and knowledge documents consumed by three AI coding harnesses:

- **Claude Code** (claude.ai/code) — Desktop app, CLI, and IDE extensions (see `CLAUDE.md`)
- **Copilot CLI** — Autonomous command-line agent (you are here)
- **Codex** — Autonomous development system (see `CODEX.md`)

It maintains one canonical authored surface (`profile-al-dev-shared/`) and generates harness-native projection artifacts for each consumer. This document covers Copilot CLI registration and usage; refer to `CLAUDE.md` (Claude Code) and `CODEX.md` (Codex) for harness-specific guidance.

This repository is not itself an AL project; it contains no `.al` source files.

### Copilot CLI Registration

`al-dev-shared` is registered in `~/.copilot/settings.json` as:

```json
"al-dev-shared": {
  "source": { "source": "directory", "path": "/Users/russelllaing/al-dev-shared" }
}
```

Copilot CLI consumes:

- **Shared skills** from `profile-al-dev-shared/skills/` (invoked as `/name`)
- **Generated agent projections** from `profile-al-dev-shared/generated/agents/copilot/`
- **Shared knowledge** from `profile-al-dev-shared/knowledge/` and `bc-code-intel-knowledge/`

## Shared Plugin Surface (All Harnesses)

All three harnesses consume the same authored source:

```text
profile-al-dev-shared/          # Canonical authored plugin surface
  skills/<name>/SKILL.md        # Skill definitions
  agents/<name>.md              # Agent definitions (harness-neutral)
  knowledge/                    # Generic workflow knowledge
  bc-code-intel-knowledge/      # BC Code Intelligence specialist knowledge
  markdown/                     # Markdown and Mermaid style guides
```

## Generated Projection Artifacts (Per-Harness Native Formats)

For harness-native tool execution, the projection layer generates harness-specific artifacts in `profile-al-dev-shared/generated/agents/copilot/` that map generic capability names (e.g., `USER_GATE`, `Read`, `Bash`) to Copilot CLI tool names (e.g., `ask_user`, `read`, `execute`).

## Skill File Format

Each skill is a markdown file in `profile-al-dev-shared/skills/<name>/SKILL.md` with YAML frontmatter. Skills use generic capability names; Copilot CLI applies projections automatically.

## Agent File Format

Each agent is a markdown file in `profile-al-dev-shared/agents/<name>.md` with YAML frontmatter. Agents declare generic capabilities in the `tools:` section; Copilot CLI consumes the generated Copilot-native projection.

## Key Architectural Patterns

**Complexity routing** (`knowledge/workflow-routing.md`): All skills classify tasks as TRIVIAL / SIMPLE / MEDIUM / COMPLEX and route accordingly.

**Workflow resilience** (`knowledge/workflow-resilience.md`): Multi-phase skills checkpoint to `.dev/progress.md` after each phase.

**`.dev/` directory convention**: All skill artifacts are written here — progress checkpoints, solution plans, code reviews, lint reports.

## Validation and Projection

To validate the plugin and regenerate Copilot CLI projections after changes to shared source:

```bash
# Validate that shared source has no harness-specific leakage
python3 scripts/validate_harness_neutrality.py profile-al-dev-shared

# Validate agent structure
python3 scripts/validate-lens-agents.py --path profile-al-dev-shared/agents

# Regenerate projections for all harnesses (including Copilot CLI)
python3 scripts/generate-agent-projections.py
```

## Commit Conventions

project-type: tool
Full spec: `profile-al-dev-shared/knowledge/commit-conventions.md`
EOF
```

Expected: File created with Copilot CLI guidance.

- [ ] **Step 2: Verify the file was created**

```bash
wc -l AGENTS.md && head -30 AGENTS.md
```

Expected: File exists, ~150 lines, header mentions Copilot CLI.

- [ ] **Step 3: Commit**

```bash
git add AGENTS.md
git commit -m "docs: add AGENTS.md for Copilot CLI guidance"
```

---

### Task 6: Create CODEX.md for Codex

**Files:**
- Create: `CODEX.md`

- [ ] **Step 1: Create CODEX.md with Codex guidance**

```bash
cat > CODEX.md << 'EOF'
# CODEX.md

This file provides guidance to Codex when working with this repository.

## What This Repo Is

`al-dev-shared` is a **shared AI development plugin** — a unified library of AL/BC development skills, agents, and knowledge documents consumed by three AI coding harnesses:

- **Claude Code** (claude.ai/code) — Desktop app, CLI, and IDE extensions (see `CLAUDE.md`)
- **Copilot CLI** — Autonomous command-line agent (see `AGENTS.md`)
- **Codex** — Autonomous development system (you are here)

It maintains one canonical authored surface (`profile-al-dev-shared/`) and generates harness-native projection artifacts for each consumer. This document covers Codex registration and usage; refer to `CLAUDE.md` (Claude Code) and `AGENTS.md` (Copilot CLI) for harness-specific guidance.

This repository is not itself an AL project; it contains no `.al` source files.

### Codex Registration and Plugin Loading

`al-dev-shared` is registered as a Codex plugin and loaded into the active session environment. Codex consumes:

- **Shared skills** from `profile-al-dev-shared/skills/`
- **Generated agent projections** from `profile-al-dev-shared/generated/agents/codex/` (TOML format)
- **Shared knowledge** from `profile-al-dev-shared/knowledge/` and `bc-code-intel-knowledge/`

## Shared Plugin Surface (All Harnesses)

All three harnesses consume the same authored source:

```text
profile-al-dev-shared/          # Canonical authored plugin surface
  skills/<name>/SKILL.md        # Skill definitions
  agents/<name>.md              # Agent definitions (harness-neutral)
  knowledge/                    # Generic workflow knowledge
  bc-code-intel-knowledge/      # BC Code Intelligence specialist knowledge
  markdown/                     # Markdown and Mermaid style guides
```

## Generated Projection Artifacts (Per-Harness Native Formats)

For harness-native task execution, the projection layer generates Codex-specific artifacts in `profile-al-dev-shared/generated/agents/codex/` in TOML format. These apply the mappings from `knowledge/agent-tool-projection-policy.md` to translate generic capability names (e.g., `USER_GATE`, `Read`, `Bash`) into Codex-native behavior directives.

## Skill File Format

Each skill is a markdown file in `profile-al-dev-shared/skills/<name>/SKILL.md` with YAML frontmatter. Skills use generic capability names; Codex applies projections automatically through the active session environment.

## Agent File Format

Each agent is a markdown file in `profile-al-dev-shared/agents/<name>.md` with YAML frontmatter. Agents declare generic capabilities in the `tools:` section; Codex consumes the generated Codex-native TOML projection.

## Key Architectural Patterns

**Complexity routing** (`knowledge/workflow-routing.md`): All skills classify tasks as TRIVIAL / SIMPLE / MEDIUM / COMPLEX and route accordingly.

**Workflow resilience** (`knowledge/workflow-resilience.md`): Multi-phase skills checkpoint to `.dev/progress.md` after each phase. Codex sessions respect these checkpoints for resumable workflows.

**`.dev/` directory convention**: All skill artifacts are written here — progress checkpoints, solution plans, code reviews, lint reports.

## Validation and Projection

To validate the plugin and regenerate Codex projections after changes to shared source:

```bash
# Validate that shared source has no harness-specific leakage
python3 scripts/validate_harness_neutrality.py profile-al-dev-shared

# Validate agent structure
python3 scripts/validate-lens-agents.py --path profile-al-dev-shared/agents

# Regenerate projections for all harnesses (including Codex)
python3 scripts/generate-agent-projections.py
```

## Commit Conventions

project-type: tool
Full spec: `profile-al-dev-shared/knowledge/commit-conventions.md`
EOF
```

Expected: File created with Codex guidance.

- [ ] **Step 2: Verify the file was created**

```bash
wc -l CODEX.md && head -30 CODEX.md
```

Expected: File exists, ~140 lines, header mentions Codex.

- [ ] **Step 3: Commit**

```bash
git add CODEX.md
git commit -m "docs: add CODEX.md for Codex guidance"
```

---

### Task 7: Add Cross-Reference Section to projection-layer-readme.md

**Files:**
- Modify: `docs/projection-layer-readme.md` (add section at end, before closing)

- [ ] **Step 1: Read the end of projection-layer-readme.md**

```bash
tail -20 docs/projection-layer-readme.md
```

Expected: File ends with "Maintainer Checklist"

- [ ] **Step 2: Add documentation section before the final checklist**

Append before the "Maintainer Checklist" section:

```markdown

---

## Documentation Boundaries

This projection layer is described in three parallel harness-specific guidance files:

- `CLAUDE.md` — Claude Code registration and usage
- `AGENTS.md` — Copilot CLI registration and usage
- `CODEX.md` — Codex registration and usage

All three reference this document for understanding the projection mechanism itself. Shared content stays harness-agnostic; harness-specific guidance lives in those three files.

When updating this document, ensure the three guidance files are kept in sync regarding the overall multi-harness architecture (even if implementation details differ per harness).
```

- [ ] **Step 3: Verify the addition**

```bash
tail -30 docs/projection-layer-readme.md
```

Expected: New section appears before Maintainer Checklist.

- [ ] **Step 4: Commit**

```bash
git add docs/projection-layer-readme.md
git commit -m "docs: add documentation boundaries section to projection-layer-readme"
```

---

### Task 8: Verification and Final Summary

**Files:**
- No file modifications; verification only

- [ ] **Step 1: Verify all commits were created**

```bash
git log --oneline -8
```

Expected: Last 8 commits include 7 task commits plus the plans commit from earlier (8 total)

- [ ] **Step 2: Verify file counts and line counts**

```bash
wc -l CLAUDE.md AGENTS.md CODEX.md && echo "---" && grep -c "^## " CLAUDE.md AGENTS.md CODEX.md
```

Expected:
- CLAUDE.md: ~340-360 lines (from original ~316, small net increase due to section replacements)
- AGENTS.md: ~155 lines (new file)
- CODEX.md: ~140 lines (new file)
- Each file has section headers (##) for major divisions

- [ ] **Step 3: Check for forbidden patterns**

```bash
grep -E "TODO|TBD|\[YYYY-MM-DD\]|\[date\]" CLAUDE.md AGENTS.md CODEX.md && echo "FAIL: Forbidden patterns found" || echo "PASS: No forbidden patterns"
```

Expected: PASS output

- [ ] **Step 4: Verify links are consistent**

```bash
echo "Files mentioning parallel guidance:" && \
grep -l "CLAUDE.md\|AGENTS.md\|CODEX.md" CLAUDE.md AGENTS.md CODEX.md docs/projection-layer-readme.md
```

Expected: All four files cross-reference each other appropriately

- [ ] **Step 5: Final commit count check**

```bash
git log --oneline HEAD~7..HEAD | wc -l
```

Expected: 7 (one per task)

- [ ] **Step 6: Re-run harness neutrality validation**

Verify that documentation-only changes didn't break anything:

```bash
python3 scripts/validate_harness_neutrality.py profile-al-dev-shared
```

Expected: PASS output ("no harness-specific leakage in shared authored surface")

- [ ] **Step 7: Create a summary note**

The following changes have been completed:

1. ✅ Rewrote CLAUDE.md header to acknowledge multi-harness architecture
2. ✅ Clarified shared plugin surface vs generated projections
3. ✅ Updated repo-local tooling boundaries
4. ✅ Added multi-harness validation guidance to Development Commands
5. ✅ Created AGENTS.md for Copilot CLI (parallel to CLAUDE.md)
6. ✅ Created CODEX.md for Codex (parallel to CLAUDE.md)
7. ✅ Added documentation boundaries section to projection-layer-readme.md

All files now reflect that `al-dev-shared` is a tri-harness plugin with equal support for Claude Code, Copilot CLI, and Codex. Harness-specific guidance is separated into three parallel documents while the projection mechanism is documented once in the projection-layer-readme.

---

## Acceptance Criteria

✅ CLAUDE.md acknowledges Claude Code, Copilot CLI, and Codex as co-consumers  
✅ AGENTS.md created with equivalent guidance for Copilot CLI  
✅ CODEX.md created with equivalent guidance for Codex  
✅ All three guidance files cross-reference each other  
✅ Development Commands section includes multi-harness validation  
✅ Repo-local maintainer tooling boundaries are clarified  
✅ projection-layer-readme.md adds documentation boundaries section  
✅ No forbidden patterns (TODO, TBD, unrendered dates)  
✅ 7 atomic commits, one per task  
