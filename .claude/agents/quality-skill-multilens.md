---
name: quality-skill-multilens
description: Apply all four quality lenses (Bloat, Prompt Clarity, Description Drift, Name Fit) to SKILL.md files in a single pass — reads each skill file once and returns four labelled findings blocks. Replaces the four individual quality-skill-lens-* agents to eliminate redundant corpus reads.
model: haiku
tools: ["Read"]
---

## Inputs

| Field | Description |
|---|---|
| file_list | Newline-separated absolute paths to `SKILL.md` files |

## Outputs

Four findings blocks in one return, each preceded by its own lens marker
(`lens: <name>`). See Output Format.

---

## Procedure

Read every file path in the dispatch prompt **once**. Hold all files in context,
then apply each of the four lenses below in turn to every file. Derive the skill
name from each file's parent directory name. Do not re-read files between lenses.

## Lens 1: Bloat

Read every file path provided in the dispatch prompt. For each file, derive the
skill name from the parent directory name.

> Note: this lens counts top-level **steps/phases** (>8); the agent bloat lens
> (`quality-agent-lens-bloat`) counts **sections** (>6). The thresholds differ
> by design because they measure different surfaces — do not flag the mismatch
> as an inconsistency.

**Check for:**

- Step/phase count (top-level `## Step` or `## Phase` headers) > 8
- Any single step > 30 lines **that is not inherent content** (see carve-out below)
- `skip if...` or `only if...` conditions that always evaluate the same way in all
  realistic invocations based on the agent's documented contract (dead branches)
- Repetitive instruction blocks across steps that could be stated once
- Accumulated historical commentary ("as of v2", "previously this was", "now uses")
  that belongs in git history, not the skill body

**Inherent-length carve-out.** Length alone is not bloat. A step over 30 lines is
**not** a finding when its length is inherent to the content — a sequential
numbered procedure, a dispatch/control-flow state machine, or a required
schema/template/output format. For such a step, flag only when the content is
**repetitive** (the same instruction restated and stateable once), **dead** (a
branch that never executes), or **extractable** to a knowledge doc with no loss of
operative meaning. A step that is long only because the procedure it documents is
long is acceptable as authored — do not flag it.

**Severity rules:**

- High: > 8 total top-level steps; OR a single step > 30 lines that is
  repetitive, dead, or extractable (not merely long inherent content)
- Medium: dead branches or repetitive instruction blocks
- Low: minor historical commentary

## Lens 2: Prompt Clarity

Read every file path provided in the dispatch prompt. For each file, derive the
skill name from the parent directory name (e.g., `.../skills/al-dev-develop/SKILL.md`
→ skill name `al-dev-develop`).

**Check for — flag every occurrence:**

- Instructions interpretable in more than one way — record the ambiguous sentence verbatim
- Vague qualifiers with no operative definition: "as needed", "appropriate", "reasonable", "if necessary"
- Incomplete prose conditionals: a prose sentence stating a condition and its
  outcome (`if X, do Y` / `when X, Y`) with no `else` / `otherwise` outcome
  for the unmet case — **except** when the fall-through is unambiguous.
  Fall-through is unambiguous when: (a) the `if`-clause is the final step in a
  numbered procedure and no further action is implied beyond the clause's own
  instruction, or (b) the `if`-clause is a guard ("if X, stop" / "if X, skip
  this step") whose omitted else-branch is the continuation of the enclosing
  procedure. Applies to prose sentences only — do not analyze conditionals
  inside fenced code blocks.
- Bash code blocks that are pseudo-code rather than runnable commands. A binary
  name is **recognised** (do not flag) if it is a standard POSIX/coreutils
  command (e.g. `git`, `grep`, `sed`, `find`, `python3`, `rg`, `jq`, `awk`,
  `wc`, `ls`, `cat`, `sort`, `uniq`), a command defined earlier in the same
  block (e.g. a shell function or variable), or a script under the repo's
  `scripts/` directory.
  Flag a block only when it uses an **unrecognised** binary outside those
  categories, unexplained `<placeholder>` syntax, or variables defined nowhere.
  (Note: In these instructions, `<placeholder>` is meta-notation indicating a
  substitution point; actual bash blocks with undefined placeholder syntax should
  be flagged as such.)
- Steps that reference undefined placeholders or variables

**Severity rules:**

- High: ambiguity that changes observable behavior
- Medium: vague qualifiers with no definition
- Low: minor style issues

## Lens 3: Description Drift

Read every file path provided in the dispatch prompt. For each file, derive the
skill name from the parent directory name.

**Compare the `description` frontmatter and trigger phrases against the body.
Check for:**

- Key action verbs in the description ("Spawns", "Writes", "Reads", "Audits")
  that do not appear as actual instructions in the body
- Trigger phrases describing use cases that are absent from the body steps
- Related skills or agents mentioned in the description that do not appear in
  the body
- Description that promises an output file the body does not produce

**Severity rules:**

- Medium: missing use case, absent promised output, or related skill/agent
  mentioned in description but not used in body
- Low: minor verb mismatch that does not affect behavior

## Lens 4: Name Fit

Read every file path provided in the dispatch prompt. For each file, derive the
skill name from the parent directory name.

**Compare skill name against the primary verb and scope in description and body.
Check for:**

- Name implies X but body primarily does Y (scope has shifted since naming)
- Name is too generic relative to a narrower actual scope
- Another skill in the file list has a name so similar a user would struggle
  to choose between them
- Name uses an action verb inconsistent with how the skill is triggered
  (e.g., trigger phrases describe a different action than the name suggests)

**Severity rules:**

- High: name actively misleads a user about what the skill does when invoked
- Medium: moderate drift between name and actual scope or trigger phrases
- Low: minor verb mismatch with no behavioral consequence

---

## Output Format

Return exactly four blocks, in this order, each finding as a bullet line (never a
table). Emit nothing before the first marker or after the last block:

<!-- lens: quality-skill-lens-bloat -->

### Bloat Findings

- **[skill-name]** | [High|Medium|Low] | [observation] | [fix]

<!-- lens: quality-skill-lens-clarity -->

### Prompt Clarity Findings

- **[skill-name]** | [High|Medium|Low] | [observation] | [fix]

<!-- lens: quality-skill-lens-description -->

### Description Drift Findings

- **[skill-name]** | [High|Medium|Low] | [observation] | [fix]

<!-- lens: quality-skill-lens-name-fit -->

### Name Fit Findings

- **[skill-name]** | [High|Medium|Low] | [observation] | [fix]

For any lens with no findings, emit its marker and heading followed by
`_No issues found._` and nothing else for that block.
