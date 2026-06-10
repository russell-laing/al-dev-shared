# Map Change Rubber-Duck Checks

This document defines the verification checks that duck agents perform when
evaluating suggestions from the plugin health sweep and architecture analysis
phases. Each suggestion is rubber-ducked against the live codebase before any
implementation plan is written.

This guide applies after a suggestion has already entered rubber-duck review; it
does not replace the initial analysis or sweep that produced the suggestion.

## Universal Checks (All Suggestion Types)

All suggestions must pass three universal validation gates before proceeding to
type-specific checks.

### U1: File Parseability and Basic Access

**Goal:** Verify the referenced artifact exists on disk and is parseable.

**Procedure:**

1. **File existence:** Run `ls -la <path>` for each file referenced in the suggestion
   - If a file does not exist, mark as **REJECT** with reason "artifact missing"
   - If the path is a directory, verify it contains expected child files
2. **Syntax validation:**
   - For markdown files: Attempt to read and parse YAML frontmatter if present
   - For skill/agent markdown: Verify required frontmatter keys exist (name, description)
   - If parse fails, mark as **REJECT** with reason "malformed artifact"

**Example pass:** A Trim suggestion references skill
`profile-al-dev-shared/skills/skill-x/SKILL.md`. File exists, frontmatter parses,
`name:` key present.

**Example fail:** A Merge suggestion references agent
`profile-al-dev-shared/agents/agent-y.md` that does not exist on disk.

### U2: Live Artifact Presence

**Goal:** Verify all artifacts named in the suggestion are still present in the
codebase (not deleted between analysis and duck check).

**Procedure:**

1. **For skills:** Verify skill file exists at correct path
2. **For agents:** Verify agent file exists at correct path
3. **For knowledge files:** Verify knowledge file exists
4. **For generated projections:** Verify generated projection file exists

If any artifact is missing:

- Mark as **REJECT** with reason "artifact deleted since analysis"

**Example pass:** Split suggestion targets agent `al-dev-plan`. File exists on disk.

**Example fail:** Inline suggestion targets skill `temp-skill-x` that was deleted
before check ran.

### U3: Reference and Dependency Validity

**Goal:** Verify all inter-artifact references are valid and resolvable:
skill to agent, agent to knowledge, and skill to skill.

**Procedure:**

1. **Read the artifact:** Load the full markdown file content
2. **Extract references:**
   - Agent invocations: `al-dev-shared:<name>`
   - Knowledge links: `../../knowledge/<file>.md` or `../knowledge/<file>.md`
   - Skill references: `/skill-name` in prose
3. **Validate each reference:**
   - For agents: Verify target agent file exists
   - For knowledge: Verify target file exists in the knowledge directory
   - For skills: Verify target skill directory and SKILL.md exist
4. **If a reference is broken:**
   - Mark as **REJECT** with reason "broken reference: REF"

**Example pass:** Agent `al-dev-develop` invokes agent `al-dev-shared:al-dev-review-develop`.
Target file exists at `profile-al-dev-shared/agents/al-dev-review-develop.md`.

**Example fail:** Skill reads `../../../nonexistent-knowledge.md`. Target file does
not exist.

---

## Type-Specific Checks

After passing U1-U3, each suggestion type receives specialized verification.

### Trim Check

**Suggestion format:**

```text
TRIM: Remove <artifact> (tool/agent/skill) from <surface> — tool/feature is unused
```

**Duck verification procedure:**

1. **Reference scan:** Search the entire codebase for any reference to the target
   artifact:
   - Search agents for invocations: `profile-al-dev-shared/agents/*.md`
   - Search skills for invocations: `profile-al-dev-shared/skills/*/SKILL.md`
   - Search knowledge references: `profile-al-dev-shared/knowledge/**/*.md`
   - Search generated projections for remaining references
   - Use: `rg -n "NAME" profile-al-dev-shared/`

2. **Actual usage verification:**
   - If `grep` finds zero references, the artifact is truly unused → ACCEPT
   - If `grep` finds references, extract the context (2 lines before/after)
   - For each reference, verify it is not a comment, example, or template placeholder
   - If all references are in comments/examples only, functionally unused → ACCEPT
   - If references indicate active use, mark as REJECT with reason "artifact is
     actively used"

3. **Tool-specific checks (if artifact is a Tool):**
   - If the tool is a built-in MCP or bash tool, verify no dependency
   - If the tool is custom-generated, check if removing it breaks workflow

4. **Verdict:**
   - ACCEPT if unused and safe to remove
   - DEFER if removal would require refactoring other artifacts
   - REJECT if artifact is in active use

**Example pass:** Trim skill `old-experimental-linter`. Grep finds zero references
in active code. → ACCEPT

**Example fail:** Suggestion to trim tool `LSP`. Grep finds 14 references across
multiple agents. → REJECT

### Merge Check

**Suggestion format:**

```text
MERGE: Combine <artifact-A> and <artifact-B> — overlapping concerns, shared patterns
```

**Duck verification procedure:**

1. **File existence:** Verify both artifacts exist (U2)
2. **Read both artifacts:** Load full content of A and B
3. **Identify overlaps:**
   - Extract description and first section from each
   - Identify shared tool invocations (agents calling same set of tools)
   - Identify shared knowledge references
   - Identify duplicate procedural steps or workflow patterns
4. **Measure overlap:**
   - Count shared tools/knowledge references as percentage of total
   - If overlap ≥ 60%, significant commonality → ACCEPT
   - If overlap < 40%, keep separate → REJECT
   - If overlap 40-60%, borderline → DEFER pending human review

5. **Feasibility check:**
   - Verify merging would not exceed recommended size
   - If merged result would be greater than 400 lines → DEFER

6. **Reference consistency:**
   - If A references B or vice versa, merging is likely safe
   - If A and B are completely decoupled, check if they serve the same caller

7. **Verdict:**
   - ACCEPT if overlap ≥ 60% and merge is feasible
   - DEFER if overlap is borderline or would create oversized artifact
   - REJECT if overlap < 40% or artifacts serve different purposes

**Example pass:** Suggestion to merge two lint-focused artifacts that both invoke
the same validation tools and read the same linting knowledge. Overlap ≈ 75%.
→ ACCEPT

**Example fail:** Suggestion to merge skill `al-dev-interview` and skill
`al-dev-explore`. Different tools and knowledge used. Overlap ≈ 30%. → REJECT

### Split Check

**Suggestion format:**

```text
SPLIT: Separate <artifact> into <artifact-A> and <artifact-B> — distinct concerns
```

**Duck verification procedure:**

1. **File existence and size:** Verify artifact exists and is larger than 250 lines
2. **Concern identification:**
   - Extract section headings (markdown `##`)
   - Identify if sections naturally group into cohesive units
   - Check if split would require code duplication
3. **Tool affinity analysis:**
   - Extract all tool invocations from the artifact
   - Group by which section(s) use each tool
   - If tools cluster into two distinct groups → ACCEPT
   - If tools are spread across all sections → REJECT
4. **Callers and references:**
   - Search for all places that invoke this artifact
   - If most callers only need A or only B → ACCEPT
5. **Verdict:**
   - ACCEPT if > 250 lines, has 2+ cohesive concerns, clean tool clustering
   - DEFER if split is possible but requires caller refactoring
   - REJECT if concerns are too intertwined or artifact is small

**Example pass:** Suggestion to split agent `al-dev-plan` into `al-dev-plan-architect`
and `al-dev-plan-estimator`. Agent is 350 lines with clean tool clustering.
Most skills call only the appropriate half. → ACCEPT

**Example fail:** Suggestion to split skill `al-dev-develop` into `code-write` and
`code-test`. Both concerns require file context from the same sources. → REJECT

### Inline Check

**Suggestion format:**

```text
INLINE: Merge <artifact> into <caller> — wrapper adds no value, single invocation
```

**Duck verification procedure:**

1. **File existence:** Verify both the artifact and caller exist
2. **Invocation count:**
   - Search entire codebase for any invocation of the artifact
   - If invocation count = 1, single-use → ACCEPT
   - If invocation count > 1, reused → REJECT
3. **Value addition check:**
   - Determine if the artifact adds significant abstraction or is a thin wrapper
   - If artifact is 50-100 lines of passthrough logic → ACCEPT
   - If artifact is 200+ lines or provides significant isolation → REJECT
4. **Dependency isolation:**
   - If artifact has dependencies that caller doesn't need → REJECT
5. **Verdict:**
   - ACCEPT if single invocation and minimal value-add
   - DEFER if single invocation but provides useful abstraction
   - REJECT if multiple invocations or provides important isolation

**Example pass:** Suggestion to inline agent `wrapper-validate-config` into its only
caller, skill `al-dev-setup`. Agent is 45 lines of passthrough logic. → ACCEPT

**Example fail:** Suggestion to inline a shared lint helper that is invoked by
multiple skills. The artifact is reused broadly rather than single-use. → REJECT

### Align Check

**Suggestion format:**

```text
ALIGN: Mismatched input/output contract — expects <type-A> but called with <type-B>
```

**Duck verification procedure:**

1. **Contract extraction:**
   - Read the artifact and extract the input contract
   - Read the calling context and extract what it actually provides
2. **Type mismatch verification:**
   - If artifact expects file path but caller provides text block → ACCEPT
   - If artifact expects JSON but caller provides markdown → ACCEPT
3. **Impact assessment:**
   - If contract mismatch silently fails, it's a bug → ACCEPT
   - If mismatch is caught by runtime validation → DEFER
4. **Scope of misalignment:**
   - Count how many places call this artifact with mismatched contracts
   - If all calls have same mismatch → DEFER and suggest documentation
5. **Verdict:**
   - ACCEPT if mismatch causes silent failures or data loss
   - DEFER if mismatch is known and handled gracefully
   - REJECT if no actual mismatch is found

**Example pass:** Suggestion to align agent `al-dev-review-develop` output. Agent
documents JSON but returns markdown. Callers expect JSON and parse fails silently.
→ ACCEPT

**Example fail:** Suggestion to align skill input contract. Skill documents "accepts
file path" and all callers provide file paths. No mismatch found. → REJECT

### Connect Check

**Suggestion format:**

```text
CONNECT: Extract shared pattern into reusable agent — <agents> share <pattern>
```

**Duck verification procedure:**

1. **Pattern identification:**
   - Read the agents mentioned in the suggestion
   - Extract the shared procedural steps or tool sequences
   - Treat structural workflow similarity as more important than exact string matches
2. **Pattern frequency:**
   - Search entire codebase for this pattern in other agents/skills
   - Count occurrences
   - If pattern appears in 3+ places → ACCEPT
   - If pattern appears in 2 places → DEFER
   - If pattern appears in 1 place → REJECT
3. **Abstraction value:**
   - Estimate how much code would be deduplicated
   - If extraction saves greater than 200 lines → ACCEPT
   - If extraction saves less than 50 lines → REJECT
4. **Coupling risk:**
   - If extracting would break separation of concerns → DEFER or REJECT
5. **Verdict:**
   - ACCEPT if pattern appears 3+ times and saves 200+ lines
   - DEFER if pattern appears 2 times or saves less than 200 lines
   - REJECT if pattern is unique or appears only in mentioned artifacts

**Example pass:** Extract a shared "compile, classify diagnostics, and write
report" pattern. The same workflow appears in three live validation-oriented
artifacts and would remove 250+ lines of duplicated procedure text. → ACCEPT

**Example fail:** Suggestion to extract "log progress to .dev/progress.md". Grep
finds this pattern only in skill `al-dev-develop`. Overhead > savings. → REJECT

### Promote Check

**Suggestion format:**

```text
PROMOTE: Extract skill to shared surface — pattern repeated, needs canonical form
```

**Duck verification procedure:**

1. **Scope validation:**
   - Verify the artifact is in a harness-specific location (e.g., `.claude/skills/`)
   - If already in `profile-al-dev-shared/skills/`, reject (already promoted)
2. **Reuse count:**
   - Search for callers of this skill/agent across all harnesses
   - If used 2+ times across harnesses → ACCEPT
   - If used only once → REJECT
3. **Harness neutrality check:**
   - Read the artifact for harness-specific tokens
   - If harness-specific tokens present → DEFER
   - If no harness-specific tokens, ready → ACCEPT
4. **Knowledge dependencies:**
   - Verify all knowledge files are in the shared knowledge directory
   - If artifact references harness-specific knowledge → DEFER
   - Treat equivalent shared workflow behavior as reuse even when the caller text differs
5. **Verdict:**
   - ACCEPT if used 2+ times, harness-neutral, dependencies available
   - DEFER if harness-specific tokens or dependencies need removal/migration
   - REJECT if used once or tightly coupled to harness infrastructure

**Example pass:** Skill `.claude/skills/validate-al-syntax/SKILL.md` is used by
Claude Code skills and Copilot CLI. No harness tokens. → ACCEPT

**Example fail:** Agent `.codex/agents/custom-codex-runner.md` invokes
codex-specific hooks. Not safe for shared surface. → REJECT

---

## Verdict Classification Rules

Each suggestion receives one of three verdicts after duck verification:

### ACCEPT

**Definition:** Suggestion passes all applicable checks and should be implemented.

**Conditions:**

- All universal checks (U1-U3) pass
- All type-specific checks pass (or are not applicable)
- No blocking issues identified
- Implementation is feasible within scope

**Action:** Add to implementation plan queue (ready to implement).

### DEFER

**Definition:** Suggestion is valid but requires additional context, human judgment,
or preparatory work before implementation.

**Conditions:**

- Universal checks pass
- Type-specific checks indicate feasibility but with uncertainties
- Implementation may have side effects requiring broader review
- Preparatory work needed

**Examples:**

- Merge suggestion where overlap is borderline (40-60%)
- Split suggestion that would require caller refactoring
- Connect suggestion where pattern saves 50-200 lines
- Align suggestion where contract mismatch is handled gracefully

**Action:** Flag as "deferred pending REASON"; hold for human review.

### REJECT

**Definition:** Suggestion should not be implemented; either the problem doesn't
exist or implementation would cause issues.

**Conditions:**

- Universal checks fail (artifact missing, broken references)
- Type-specific checks identify blockers (artifact in active use, no actual mismatch)
- Implementation is infeasible or would break existing functionality
- Suggestion is based on stale analysis

**Examples:**

- Trim suggestion where artifact is in active use
- Merge suggestion where artifacts serve distinct purposes
- Split suggestion where concerns are too intertwined
- Promote suggestion with harness-specific tokens and no refactoring plan

**Action:** Remove from implementation queue; report reason in findings.

---

## Duck Verification Output Format

After evaluating a suggestion, duck agents report:

```markdown
### Suggestion: [ORIGINAL SUGGESTION TEXT]

Verdict: ACCEPT / DEFER / REJECT

Checks passed:
- [Check name]: [Result]

Checks that blocked (if REJECT/DEFER):
- [Check name]: [Finding]

Evidence:
- [File location or grep output]
- [Specific line numbers or references]

Recommendation (if DEFER): [What would make this work]
```

---

## Common Duck Check Patterns

These patterns help duck agents recognize types of issues:

### Pattern: File reference is absolute path

- Duck check must handle both relative paths and absolute paths
- Relativize to `profile-al-dev-shared/` base when searching

**Examples:**

A finding may reference a file using an absolute path from the developer's environment:

```
Suggestion found: TRIM skill located at /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/old-skill/SKILL.md
```

Normalize this for searching and verification by stripping the environment prefix:

```
Normalized path: profile-al-dev-shared/skills/old-skill/SKILL.md
Search command: ls -la profile-al-dev-shared/skills/old-skill/SKILL.md
```

This matters because ducks run in different environments and may see different absolute prefixes. Relativizing ensures the finding is reproducible across runs and harnesses.

### Pattern: Tool invocation syntax varies

- Agent invocation: `al-dev-shared:<agent-name>`
- Skill invocation: `/skill-name`
- Tool invocation: Tool name in YAML frontmatter `tools:` list

**Example invocations:**

```markdown
# Agent SKILL.md file invoking another agent:
## Procedure
1. Gather requirements
2. Run `/al-dev-plan` to create the solution plan
3. Dispatch the plan to al-dev-shared:al-dev-develop for implementation

# Agent frontmatter with tools list:
---
name: al-dev-review-develop
description: Review a completed code implementation
tools:
  - Read
  - Bash
  - Edit
---

# Generated agent YAML (Copilot CLI format) invoking tools:
tools:
  - bash
  - file_read
  - file_write
```

### Pattern: Knowledge reference paths vary

Knowledge is referenced in multiple contexts with differing relative paths and syntax
patterns. Verify references during duck checks by understanding how paths are expressed
in each artifact type.

**In skill files** (from `profile-al-dev-shared/skills/<name>/SKILL.md`):

```markdown
## Intent Preflight

Before dispatching architect agents or writing a plan artifact, apply
`knowledge/intent-preflight.md`.

## Artifact Contract

Use `knowledge/artifact-contracts.md` as the source of truth for this skill's
durable outputs and success evidence.

See `../../knowledge/commit-workflow-orchestration.md` — keep phase templates in sync.
```

**In agent files** (from `profile-al-dev-shared/agents/<name>.md`):

```markdown
Extract change manifests using the patterns in `knowledge/commit-analysis-patterns.md`.

All sequences follow the validation loop outlined in `knowledge/compile-lint-procedure.md`.
```

**In generated projections** (from `profile-al-dev-shared/generated/agents/claude/<name>.md`):

```markdown
Extract change manifests using the patterns in `knowledge/commit-analysis-patterns.md`.
```

**Path variations to handle during verification:**

- Backtracking paths from skill subdirectories: `../../knowledge/file.md`
- Direct paths from agent files: `knowledge/file.md`
- Paths in backticks and inline prose: `` `knowledge/artifact-contracts.md` ``
- Paths in generated projections: Updated during projection to match location relative to the generated file

### Pattern: Generated artifacts should not be edited

Generated artifacts under `profile-al-dev-shared/generated/` are pipeline outputs
produced by translating canonical source files into harness-native formats — they are
not authored files. Any hand-edit made directly to a generated artifact will be silently
overwritten the next time `scripts/generate-projections.py` is run, leaving no trace of
the change. Duck agents must therefore redirect all edit suggestions to the canonical
source files in `profile-al-dev-shared/agents/` or `profile-al-dev-shared/skills/`,
and treat a suggestion targeting a path under `generated/` as an automatic REJECT.

```markdown
# SOURCE ARTIFACTS (Edit Here)
profile-al-dev-shared/agents/al-dev-commit-analyzer.md
profile-al-dev-shared/agents/al-dev-developer.md
profile-al-dev-shared/skills/al-dev-develop/SKILL.md
profile-al-dev-shared/knowledge/artifact-contracts.md

# GENERATED ARTIFACTS (Read-Only)
profile-al-dev-shared/generated/agents/claude/al-dev-commit-analyzer.md
profile-al-dev-shared/generated/agents/copilot/al-dev-commit-analyzer.md
profile-al-dev-shared/generated/agents/codex/al-dev-commit-analyzer.md
profile-al-dev-shared/generated/agents/claude/al-dev-developer.md

# REJECTION EXAMPLES
REJECT: "Fix typo in profile-al-dev-shared/generated/agents/claude/al-dev-commit-analyzer.md"
REASON: Edit source file profile-al-dev-shared/agents/al-dev-commit-analyzer.md instead

REJECT: "Reorganize tool list in profile-al-dev-shared/generated/agents/copilot/al-dev-developer-tdd.md"
REASON: Make changes to source profile-al-dev-shared/agents/al-dev-developer-tdd.md; regenerate projections

# CORRECT WORKFLOW
1. Edit the source artifact (e.g., profile-al-dev-shared/agents/al-dev-commit-analyzer.md)
2. Run projection regeneration (scripts/generate-projections.py)
3. Generated artifacts in profile-al-dev-shared/generated/agents/*/ update automatically
```

- Never use ducks to suggest changes to `profile-al-dev-shared/generated/**`
- Generated artifacts are outputs; suggest changes to shared source instead

**Source-to-Generated Mapping:**

| Content Type | Source Path (Edit Here) | Generated Paths (Read-Only) |
| --- | --- | --- |
| Agent | `profile-al-dev-shared/agents/al-dev-commit-analyzer.md` | `profile-al-dev-shared/generated/agents/claude/al-dev-commit-analyzer.md` and similar for copilot/, codex/ |
| Skill | `profile-al-dev-shared/skills/al-dev-develop/SKILL.md` | No generated copies; distributed as-is |
| Knowledge | `profile-al-dev-shared/knowledge/artifact-contracts.md` | No generated copies; distributed as-is |

**Example violations to reject:**

- Duck suggests: "Fix typo in `profile-al-dev-shared/generated/agents/claude/al-dev-commit-analyzer.md`"
  → REJECT: Edit the source file `profile-al-dev-shared/agents/al-dev-commit-analyzer.md` instead
  
- Duck suggests: "Reorganize tool list in `profile-al-dev-shared/generated/agents/copilot/al-dev-developer-tdd.md`"
  → REJECT: Make changes to source `profile-al-dev-shared/agents/al-dev-developer-tdd.md`; regenerate projections afterward

**Correct workflow:**

1. Edit the source artifact (e.g., `profile-al-dev-shared/agents/al-dev-commit-analyzer.md`)
2. Run the projection regeneration step (e.g., `scripts/generate-projections.py`)
3. Generated artifacts in `profile-al-dev-shared/generated/agents/*/` are updated automatically

---

## References

- `docs/al-dev-skills-map.md` — Skill inventory and relationships
- `docs/al-dev-agent-map.md` — Agent inventory and tool assignments
- `profile-al-dev-shared/knowledge/harness-concepts.md` — Shared vocabulary
- `profile-al-dev-shared/knowledge/artifact-contracts.md` — Artifact handoff specs
