# AL Dev Agent Quality Audit

**Last run:** 2026-05-19
**Agents audited:** 17

## Summary

| Severity | Count |
|----------|-------|
| High     | 29    |
| Medium   | 26    |
| Low      | 10    |

## Findings

### al-dev-developer

**[High] Lens 2 — Structural Conventions**
Observation: 24 top-level `##` sections in the body (far exceeds the 6-section limit). Sections include: Your Mission, Inputs, Outputs, Workflow, TDD Implementation Process, Governance Tokens, Standard AL Patterns, Compilation Strategy, Error Handling Rules, Session Log Updates, Compilation Output Handling, Code Review Iteration Mode, When to Deviate from Plan, Anti-Patterns to Avoid, Code Quality Checklist, Handling Missing Information, Multi-File Coordination, Performance Best Practices, Chat Response Format, Session Log Final Entry, Testing During Implementation, Common AL Mistakes to Avoid, Handoff to code-reviewer, Git Commands.
Fix: Move AL code templates (Standard AL Patterns, Common AL Mistakes, Performance Best Practices) to a knowledge file; collapse remaining sections to ≤6.

**[High] Lens 1 — Prompt Clarity**
Observation: The TDD workflow extensively instructs the agent to use `USER_GATE` (AskUserQuestion) and `TaskCreate`/`TaskUpdate`, but the agent's tools list is `["Read", "Write", "Edit", "Glob", "Grep", "Bash"]` — neither AskUserQuestion nor any Task tool is present. An agent following the TDD instructions will silently fail at every hard-stop gate.
Fix: Either add `AskUserQuestion` to the tools list or remove all TDD gate instructions (and the TDD workflow section) from this agent — it cannot enforce TDD gates without the tool.

**[High] Lens 4 — Bloat**
Observation: The `## TDD Implementation Process` section alone spans ~200 lines, dwarfing the 30-line limit. It duplicates content already referenced from `tdd-workflow.md`.
Fix: Replace the TDD Implementation Process section with a single pointer to `tdd-workflow.md`; keep only the governance token table and the hard-stop rule.

**[Medium] Lens 1 — Prompt Clarity**
Observation: `bc-publish` is referenced in multiple code blocks but is not a standard AL CLI tool and is never defined. An agent reading this cannot know whether to run it or skip it.
Fix: Remove `bc-publish` references or annotate them as project-specific and conditional on its availability.

**[Medium] Lens 2 — Structural Conventions**
Observation: The TDD workflow body references `tdd-workflow.md` as an authoritative external file ("See `tdd-workflow.md` for complete TDD discipline"), but this file is not in the agent's tools list and is not a knowledge file the agent can load.
Fix: Either inline the required TDD content or add a step that reads the file path explicitly via the Read tool.

**[Medium] Lens 4 — Bloat**
Observation: Historical version annotations ("Legacy - Still Supported", "v2.18+", "as of v2") are embedded in section headings and body text — context that belongs in git history.
Fix: Remove historical commentary; keep only the current expected behavior.

**[Low] Lens 4 — Bloat**
Observation: The Chat Response Format section contains emoji-heavy response templates that mix AL-specific formatting conventions (🟢, 🧪, 💻) not described elsewhere in the file.
Fix: Remove or simplify response format templates; a plain text output contract is sufficient.

---

### al-dev-docs-writer

**[High] Lens 2 — Structural Conventions**
Observation: 20 top-level `##` sections in the body (exceeds the 6-section limit). Sections include: Your Mission, Inputs, Outputs, Workflow, Documentation Folder Structure, RTM Status Inference, RTM Token Parsing, RTM Documentation Output, Diagram Rules, RTM Rules, API Documentation Template, CHANGELOG.md Format, When to Create Each Type, Documentation Guidelines, Output, Chat Response Format, Detecting Documentation Location, README.md Template, Best Practices, What NOT to Document.
Fix: Collapse RTM sections (Status Inference, Token Parsing, Documentation Output, RTM Rules) into one `## RTM Handling` section; move template examples to a knowledge file.

**[High] Lens 1 — Prompt Clarity**
Observation: Workflow Step 1 instructs "If neither [wiki/ nor docs/] exists, ask user which to create" but the agent's tools are `["Read", "Write", "Glob", "Grep", "Bash"]` — AskUserQuestion is absent. The agent cannot fulfill this conditional branch.
Fix: Replace "ask user" with a default action (e.g., "create `docs/` by default and note this in the session log").

**[High] Lens 4 — Bloat**
Observation: The `## API Documentation Template` section contains a multi-section markdown template exceeding 40 lines with nested code blocks.
Fix: Move the API documentation template to a knowledge file; reference it via a Read call in the Workflow.

**[Medium] Lens 4 — Bloat**
Observation: `## Output` and `## Chat Response Format` both describe end deliverables with overlapping content (files produced, session log entry). One could be removed.
Fix: Merge the two into a single `## Output & Response` section.

---

### al-dev-script-engineer

**[High] Lens 1 — Prompt Clarity**
Observation: The Toolkit Reference section hardcodes the absolute path `/Users/russelllaing/Documents/Repositories/al-analysis-toolkit`. This path is machine-specific and will silently fail for any other user or machine.
Fix: Replace with a relative lookup (`find ~ -name "al-analysis-toolkit" -maxdepth 5 -type d | head -1`) or document that the toolkit is optional and skip gracefully if not found.

**[High] Lens 2 — Structural Conventions**
Observation: 9 top-level `##` sections (exceeds the 6-section limit): Language Selection, Error Handling Standards, CLI Output, Common Script Types, Inputs & Outputs, Toolkit Reference, Script Conventions, Token Generation, Chat Response Format.
Fix: Collapse Error Handling Standards and CLI Output into a single `## Standards` section; merge Token Generation into Script Conventions.

**[High] Lens 4 — Bloat**
Observation: `## Script Conventions (follow strictly)` is ~45 lines with multiple Python code examples and protocol references that could live in a knowledge file.
Fix: Move code examples to a knowledge file; keep only the rule list (async-first, protocol-based, strict typing) in the agent body.

**[Medium] Lens 2 — Structural Conventions**
Observation: The Inputs table references `.dev/02-solution-plan.md` — this does not match the project's standard filename pattern `.dev/YYYY-MM-DD-al-dev-plan-solution-plan.md`.
Fix: Update to use the correct glob pattern or describe as "latest `*-al-dev-plan-solution-plan.md`".

**[Low] Lens 1 — Prompt Clarity**
Observation: "Always match the language to the project's existing stack when possible" — "when possible" has no definition of when it is not possible.
Fix: Remove "when possible" or specify the condition ("when the project has an existing `package.json`, `go.mod`, etc.").

---

### al-dev-solution-architect

**[High] Lens 2 — Structural Conventions**
Observation: 18 top-level `##` sections in the body (exceeds the 6-section limit): Your Mission, Inputs, Outputs, CRITICAL: Proportional Output, Diagram Standards, Workflow, MCP Tools Available, Decision Tree, Examples of MCP Usage, CRITICAL: NO COMPLETE AL CODE, Output Format, Testability Architecture Standards, Assumptions and Verification, Implementation Sequence, Chat Response Format, Session Log Entry, Design & Planning Best Practices, Rubber Duck.
Fix: Move MCP tool examples and the full Output Format template to a knowledge file; collapse CRITICAL headers into the relevant sections they annotate.

**[High] Lens 4 — Bloat**
Observation: `## Output Format` spans ~200 lines — it is effectively the complete solution plan template including a full Testability Architecture section, Implementation Sequence example with 4 phases, Design Review Checklist, Rollback Plan, etc. This is implementation documentation, not agent instruction.
Fix: Move the full template to `knowledge/solution-plan-template.md` and replace with a single Read call in the Workflow.

**[Medium] Lens 3 — Description Drift**
Observation: The body H1 reads `# Solution Planner` but the file is `al-dev-solution-architect.md` and the description uses "architect". The mismatched internal title would appear in any context where the agent identifies itself.
Fix: Change the body H1 to `# Agent: al-dev-solution-architect`.

**[Medium] Lens 1 — Prompt Clarity**
Observation: MCP tool calls throughout the Workflow use informal notation (`al-mcp-server MCP tool: al_get_object_definition`) that is neither actual tool-call syntax nor clearly labelled as pseudo-code. An agent following this would not know whether to call the tool directly or interpret it differently.
Fix: Either show actual tool-call format or add a note: "The following shows which MCP tool to call; use it via the standard tool-call mechanism."

---

### al-dev-commit-analyzer

**[High] Lens 1 — Prompt Clarity**
Observation: Steps 4.5 and 6.7 reference `$REPO` (e.g., `git -C "$REPO" diff ...`, `GITATTR="$REPO/.gitattributes"`) but `$REPO` is never defined in the agent instructions or the ## Inputs table. The Inputs list only `PROJECT_CONTEXT` and `FD_TICKET`.
Fix: Add `REPO` (the project root path) to the ## Inputs table and specify it is provided in the dispatch prompt, or replace `$REPO` with `.` (current directory) if the agent always runs from the project root.

**[High] Lens 4 — Bloat**
Observation: `## Phase: analysis` is a single section spanning ~290 lines (Steps 1–7 with 9 sub-steps). This far exceeds the 30-line limit.
Fix: Split into meaningful sub-sections: `### Manifest Extraction` (Steps 1–3), `### Validation Checks` (Steps 4–6.8), `### Return Format` (Step 7), keeping them under the one Phase heading.

**[Medium] Lens 4 — Bloat**
Observation: The input description `PROJECT_CONTEXT` and `FD_TICKET` appears identically in both the ## Inputs table and the first bullet list inside `## Phase: analysis` — duplicate content.
Fix: Remove the duplicate bullet list from the Phase body; the ## Inputs table is the authoritative source.

**[Medium] Lens 2 — Structural Conventions**
Observation: Step numbers use decimal notation inconsistently: Step 4, Step 4.5, Step 5, Step 6, Step 6.5, Step 6.7, Step 6.8, Step 7. The decimal steps are inserted additions and disrupt sequential readability.
Fix: Renumber sequentially: Step 1–9, with short descriptive headings instead of decimal point notation.

---

### al-dev-security-reviewer

**[High] Lens 2 — Structural Conventions**
Observation: 9 top-level `##` sections (exceeds the 6-section limit): Role, Inputs, Outputs, Spawn Context, Review Focus, Review Process, Common Security Issues in AL/BC, Output Format, Success Criteria.
Fix: Merge Spawn Context into Role; merge Success Criteria into Output Format.

**[High] Lens 4 — Bloat**
Observation: `## Common Security Issues in AL/BC` contains 3 code example pairs (~60 lines total), exceeding the 30-line section limit.
Fix: Move code examples to a knowledge file and reference with a single Read call, or reduce to one representative example.

**[Medium] Lens 1 — Prompt Clarity**
Observation: Review Process Step 3 says "When other reviewers present findings" — but the agent only has `Read`, `Grep`, `Glob` tools and no mechanism to receive real-time findings from other agents. Other reviewers' findings only reach this agent via the dispatch prompt.
Fix: Change to "When other reviewers' findings are included in the dispatch prompt" to accurately reflect how cross-reviewer information arrives.

**[Medium] Lens 1 — Prompt Clarity**
Observation: Output Format says "Write your findings (or message lead if that's the team pattern)" — "message lead" is undefined; the agent has no messaging tool.
Fix: Remove "or message lead" — findings are always returned as the agent's text response.

**[Low] Lens 2 — Structural Conventions**
Observation: The body has no `# Agent: al-dev-security-reviewer` H1 heading; it starts directly with a bold description line `**Specialist teammate for security...**`.
Fix: Add `# Agent: al-dev-security-reviewer` as the first line of the body.

---

### al-dev-interview

**[High] Lens 2 — Structural Conventions**
Observation: 11 top-level `##` sections (exceeds the 6-section limit): Your Mission, Tool Usage, Inputs, Outputs, Interview Process, Question Categories, Interview Guidelines, Write Refined Spec, Completion, Session Log Entry, Tips for BC/AL Interviews.
Fix: Collapse Interview Guidelines and Tips into Interview Process; move Question Categories to a knowledge file referenced by the agent.

**[High] Lens 4 — Bloat**
Observation: `## Question Categories for BC/AL Projects` has 11 sub-categories each with 5–8 bullet points and example questions — the section is ~120 lines, far exceeding the 30-line limit.
Fix: Move question categories to `knowledge/interview-question-bank.md` and add a single step: "Read `knowledge/interview-question-bank.md` for question categories."

**[Medium] Lens 2 — Structural Conventions**
Observation: The Tool Usage table lists `USER_GATE` as a tool, but the actual tool name available to this agent is `AskUserQuestion`. `USER_GATE` is used consistently in the body as a pseudo-name, but it conflicts with what the agent sees in its tool list.
Fix: Replace all `USER_GATE` references with `AskUserQuestion` (the real tool name) and remove the Tool Usage table row that maps USER_GATE as if it were a separate tool.

---

### al-dev-performance-reviewer

**[High] Lens 4 — Bloat**
Observation: `## Common Performance Issues` contains 3 code example pairs (~60 lines), exceeding the 30-line section limit.
Fix: Move code examples to a knowledge file or reduce to one representative example with a pointer to the knowledge reference.

**[High] Lens 2 — Structural Conventions**
Observation: 7 top-level `##` sections (exceeds the 6-section limit): Role, Inputs, Outputs, Review Focus, Common Performance Issues, Output Format, Debate with Other Reviewers.
Fix: Merge Debate with Other Reviewers into Output Format as a short paragraph.

**[Medium] Lens 1 — Prompt Clarity**
Observation: The body provides review focus categories and code examples but no step-by-step process for how the agent should proceed — there is no `## Review Process` or equivalent sequential instruction. It is unclear whether the agent should scan all files first, report as it reads, or batch findings.
Fix: Add a brief `## Review Process` section with 3–4 steps mirroring the structure in `al-dev-security-reviewer` (read all code → identify issues → classify → output).

---

### al-dev-expert-reviewer

**[High] Lens 4 — Bloat**
Observation: `## Common AL Issues` contains 4 code example pairs (~70 lines), exceeding the 30-line section limit.
Fix: Move to a knowledge file or reduce to one example pair with a pointer.

**[High] Lens 2 — Structural Conventions**
Observation: 7 top-level `##` sections (exceeds the 6-section limit): Role, Inputs, Outputs, Review Focus, Common AL Issues, Output Format, Debate with Other Reviewers.
Fix: Merge Debate with Other Reviewers into Output Format.

**[Medium] Lens 2 — Structural Conventions**
Observation: The body has no `# Agent: al-dev-expert-reviewer` H1 heading; it starts directly with a bold description line `**Specialist teammate for AL patterns...**`. Inconsistent with other agents in this directory.
Fix: Add `# Agent: al-dev-expert-reviewer` as the first line of the body.

---

### al-dev-code-review

**[High] Lens 2 — Structural Conventions**
Observation: 9 top-level `##` sections (exceeds the 6-section limit): Role, Inputs, Outputs, Spawn Context, Review Focus, Review Process, Output Format, What NOT to Review, Debate with Other Reviewers.
Fix: Merge Spawn Context into Role; merge What NOT to Review into Review Focus as a short subsection.

**[High] Lens 4 — Bloat**
Observation: `## Review Process` Step 3 (Severity Classification) defines four severity bands with examples — the section is ~40 lines, exceeding the 30-line limit.
Fix: Move severity definitions to a knowledge file or inline them in the Output Format section where they are already partially duplicated.

**[Medium] Lens 3 — Description Drift**
Observation: The description explicitly states "For standalone manual use only; not part of the automated /al-dev-develop pipeline (which uses the 3-specialist team: security-reviewer, expert-reviewer, performance-reviewer)." However, the body's Spawn Context section says "You may be spawned as part of a 3-reviewer team" — directly contradicting the description.
Fix: Update the description to remove the "standalone only" qualifier, or remove the team-review instructions from the body.

**[Low] Lens 2 — Structural Conventions**
Observation: The Output Format section contains a code block with no language tag (lines 118–139).
Fix: Add a language tag (e.g., `markdown`) to the Output Format code block.

---

### al-dev-release-notes-agent

**[High] Lens 2 — Structural Conventions**
Observation: 9 top-level `##` sections (exceeds the 6-section limit): Inputs, Outputs, Phase: extract-changes, Phase: filter-changes, Phase: research-context, Phase: identify-diagrams, Phase: write-notes, Phase: uat-instructions, Output Contract.
Fix: Merge Phase: identify-diagrams into Phase: write-notes as a sub-step (it is a single decision point, not a phase requiring its own heading).

**[High] Lens 4 — Bloat**
Observation: `## Phase: write-notes` includes a complete multi-section release notes template (~60 lines) inline in the agent body.
Fix: Move the template to `knowledge/release-notes-template.md` and replace with a Read call in the phase instructions.

**[Medium] Lens 1 — Prompt Clarity**
Observation: Multiple phases reference `$AL_DEV_SHARED_PLUGIN_ROOT/markdown/md-mermaid-helper.md` but `$AL_DEV_SHARED_PLUGIN_ROOT` is an environment variable that may not be set in the agent's execution context.
Fix: Use the MCP/plugin path resolution mechanism or replace with a concrete Read path (e.g., the absolute path used elsewhere in the codebase).

**[Low] Lens 5 — Name Fit**
Observation: The `-agent` suffix in `al-dev-release-notes-agent` is inconsistent with most other agent names in this directory (e.g., `al-dev-developer`, `al-dev-security-reviewer`). Only the commit-agent and ticket-agent also use this suffix.
Fix: Rename to `al-dev-release-notes-writer` (or similar) to align with naming conventions; update the dispatching skill accordingly.

---

### al-dev-diagnostics-fixer

**[High] Lens 4 — Bloat**
Observation: `## Process` Step 4 (Classify and Fix) spans ~80 lines — it contains a judgment-required rules table, scripted-fix instructions, a Python code example, a delegation template, and direct-edit instructions all in one step.
Fix: Split Step 4 into two steps: Step 4a (Judgment-required check and scripted path) and Step 4b (Direct edit path); move the Python example to a knowledge file.

**[Medium] Lens 1 — Prompt Clarity**
Observation: Step 4 instructs the agent to "delegate to `al-dev-python-script-engineer`" — but no agent with that name exists in this plugin. The actual agent is `al-dev-script-engineer`.
Fix: Change `al-dev-python-script-engineer` to `al-dev-script-engineer` and qualify: "delegate to `al-dev-script-engineer` (Python mode)".

---

### al-dev-commit-agent-execute

**[High] Lens 4 — Bloat**
Observation: `## Phase: execute` is a single section spanning ~185 lines (Steps 1–3 with sub-steps 1.5, lint baseline, corruption check, OOXML gate, scrubbing, retry logic, and return block).
Fix: Split the section body into subsections `### Pre-flight Lint`, `### OOXML Gate`, `### Commit & Retry`, `### Return Block` to keep each under 30 lines without adding new top-level headings.

**[Medium] Lens 4 — Bloat**
Observation: The ⚠️ CRITICAL warning block ("Never use Write or Edit on staged source files") appears verbatim twice — once before `## Inputs` (lines 36–41) and again inside `## Phase: execute` (lines 47–52).
Fix: Remove the first occurrence; keep only the one inside the Phase body where it is contextually relevant.

**[Low] Lens 2 — Structural Conventions**
Observation: Step 1.5 uses decimal numbering inconsistently with the otherwise whole-number step sequence (Steps 1, 1.5, 2, 3).
Fix: Renumber as Step 2 (OOXML Gate), pushing subsequent steps to 3 and 4.

---

### al-dev-support-agent

**[High] Lens 4 — Bloat**
Observation: `## Step 2 — Research` is a single section spanning ~90 lines with three sub-sources, each containing bash commands, conditional logic, and retention instructions.
Fix: Split into `### Source 1: AL Symbols`, `### Source 2: MS Docs`, `### Source 3: BC Code History` as sub-sections of Step 2, keeping each sub-section under 30 lines.

**[Medium] Lens 1 — Prompt Clarity**
Observation: The Phase: write-notes step references `$AL_DEV_SHARED_PLUGIN_ROOT/markdown/md-mermaid-helper.md` — same undefined environment variable issue as al-dev-release-notes-agent.
Fix: Use an absolute known path or a Read tool call with a fallback.

**[Low] Lens 5 — Name Fit**
Observation: The `-agent` suffix in `al-dev-support-agent` is inconsistent with most other agent names. The description says "Dispatched by /al-dev-support" which parallels the commit-agent pattern, but most dispatched agents omit the suffix.
Fix: Minor inconsistency; consider renaming to `al-dev-support-researcher` to align with naming convention.

---

### al-dev-ticket-agent

**[High] Lens 4 — Bloat**
Observation: `## Phase: fetch` is a single section spanning ~120 lines (Steps 1–3 with two parallel curl calls, jq parsing, status/priority mapping table, and the full output file template).
Fix: Split into `### Step 1 — Fetch`, `### Step 2 — Write context file`, `### Step 3 — Return output` as sub-sections within the Phase to keep each under 30 lines.

**[Medium] Lens 2 — Structural Conventions**
Observation: The agent body has no `## Inputs` or `## Outputs` tables. Input fields (TICKET_ID, FRESHDESK_API_KEY, FRESHDESK_DOMAIN) and outputs (.dev/ context file) are described only implicitly in the Phase body.
Fix: Add `## Inputs` and `## Outputs` tables at the top of the body before the ## Phases section.

**[Low] Lens 1 — Prompt Clarity**
Observation: Step 1 is titled "Fetch ticket and conversations in parallel" but the bash commands are sequential — there is no background execution (`&`) or parallel subshell. "In parallel" is aspirational and may mislead.
Fix: Change the title to "Fetch ticket and conversations" and note they are sequential API calls.

---

### commit-learn-verifier

**[Medium] Lens 2 — Structural Conventions**
Observation: File name `commit-learn-verifier.md` does not follow the `al-dev-<name>` prefix convention used by all other agents in this directory.
Fix: Rename to `al-dev-commit-learn-verifier.md` (and update any dispatching skill reference) or add a note in the frontmatter that this agent intentionally omits the prefix.

**[Medium] Lens 1 — Prompt Clarity**
Observation: The `## Input` section states "Git history: last 3-5 commits" but `## Analysis Process` Step 1 says "Examine the git diff of the last commit" — inconsistency in how much history the agent is expected to use.
Fix: Align both sections: specify "last N commits" consistently (suggest 3) in both Input and Step 1.

**[Medium] Lens 1 — Prompt Clarity**
Observation: `## Analysis Process` Step 3 is gated on `--auto-fix` (e.g., "if --auto-fix") but this flag is never defined in the `## Input` section. The dispatch prompt format is unspecified.
Fix: Add `auto_fix` (boolean) to the `## Input` section and specify how it is passed in the dispatch prompt.

**[Low] Lens 2 — Structural Conventions**
Observation: `## Input` uses singular; all other agents in this directory use `## Inputs`.
Fix: Rename to `## Inputs` for consistency.

---

### al-dev-explore

**[Medium] Lens 3 — Description Drift**
Observation: The description says "Complements the al-dev-explore skill" — but this agent IS `al-dev-explore`. The sentence is self-referential and meaningless. The intended contrast is likely with the `/al-dev-explore` skill (which does not write files), while this agent does persist output.
Fix: Replace with "Used when exploration results need to persist beyond the current session context."

**[Medium] Lens 3 — Description Drift**
Observation: The description says "Use when exploration results need to persist as a file for later reference" but the agent's body has no Write tool and no instruction to write output files. The agent can only return findings as a text response.
Fix: Either add the Write tool to the frontmatter and add a final step to write findings to `.dev/explore-<date>.md`, or remove the "persist as a file" qualifier from the description.

**[Low] Lens 2 — Structural Conventions**
Observation: The body uses `## Input` and `## Output` (singular) rather than `## Inputs` and `## Outputs` (plural) as used throughout other agents.
Fix: Rename headings to `## Inputs` and `## Outputs` for consistency.

---
