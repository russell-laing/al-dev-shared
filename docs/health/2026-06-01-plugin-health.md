# Plugin Health — 2026-06-01

## Summary

| Severity | Design | Quality | Naming | Total |
|----------|--------|---------|--------|-------|
| High     | 1      | 31      | 0      | 32    |
| Medium   | 8      | 38      | 1      | 47    |
| Low      | 7      | 116     | 0      | 123   |

**Top 5 ranked actions:**

1. **[High / Structure]** Remove stray `# test` headers from `al-dev-fix/SKILL.md` (lines 444–445) — structural corruption that will confuse all readers and tools immediately
2. **[High / Design]** Atomise `/al-dev-plan` (9 phases): add `--resume-from=phase2` or split into preflight + architect phases — pre-planning (phases 0–1.6) and architect debate (phases 2–7) are independently invocable units; full re-runs waste token budget
3. **[High / Name-fit]** Rename `al-dev-commit-recover-verifier` → `al-dev-commit-recover-fixer` — "verifier" is misleading; the agent applies active recovery strategies (git restore, regex reconstruction, schema rebuild), not passive verification
4. **[High / Name-fit]** Rename `plan-map-changes` → `al-dev-map-suggestions-verify` and `plan-with-critic-swarm` → `al-dev-plan-swarm-validate` — both names misrepresent primary behavior as plan-creation when primary behavior is review/verification of an existing plan
5. **[High / Bloat]** Extract identical "Compile Output — Critical Safeguard" block from `al-dev-developer-tdd` and `al-dev-developer-traditional` into `knowledge/compile-output-safeguard.md` — two agents with identical 20-line blocks will diverge; each skill currently references the other's behavior independently

Failed lenses: None.

---

## Design suggestions

### Trim (Tool Hygiene)

- **al-dev-developer-tdd** | Low | `Grep` declared in frontmatter but no grep usage in body; workflow uses Read/Write/Bash | Remove `Grep` from tools list or add explicit symbol search step
- **al-dev-developer-traditional** | Low | Same issue — `Grep` declared but no grep usage in workflow | Remove `Grep` from tools list or add explicit grep usage

### Remodel (Model Fit)

- **al-dev-support-reply-drafter** | Medium | `sonnet` assigned for mechanical format transformation (parse findings → write two-section reply, no novel reasoning) | Downgrade to `haiku` — task is structured rewrite with tight constraints, not synthesis
- **al-dev-code-review** | Low | `haiku` assigned for multi-file review requiring cross-file severity judgment; however this was an intentional 2026-06-01 remodel decision | Verify if haiku quality is acceptable; upgrade to `sonnet` if calibration issues surface

### Split (Scope Isolation)

- **al-dev-commit-agent-execute** | Medium | Combines git commit execution (success path) with hook-failure retry recovery (error path); both produce unrelated outputs (COMMITS block vs HOOK_FAILURES block) | Extract hook-failure retry into `al-dev-commit-hook-fixer`; agent handles only success path
- **al-dev-support-researcher** | Medium | Combines (1) multi-source research and (2) synthesis of findings into structured block | Extract synthesis into a separate agent or fold into reply drafter
- **al-dev-support-reply-drafter** | Medium | Combines validation of researcher findings (step 1.5 tone/framing constraints) with draft-writing | Separate into validator + drafter, or collapse validation into researcher's synthesis step

### Align (Caller Alignment)

- **al-dev-support-reply-drafter** | Medium | `RESEARCHER_FINDINGS` must be an inline text block in dispatch prompt; if `/al-dev-ticket` Phase 7 omits it, parsing fails silently | Verify `/al-dev-ticket` Phase 7 explicitly passes full `RESEARCHER_FINDINGS` block as text in dispatch prompt
- **al-dev-developer-tdd / al-dev-developer-traditional** | Low | Inputs table implies caller passes explicit file paths but agents locate files via glob | Clarify Inputs: "Files auto-located via glob in `.dev/`; callers do not pass explicit paths"
- **al-dev-solution-architect** | Low | Inputs table implies explicit requirements file path passing but agent uses glob discovery | Same clarification needed in Inputs table

### Connect (Shared Backbone)

- **al-dev-plan** | Low | Phase 2 spawns `al-dev-solution-architect` competitively but does not reference `knowledge/architect-invocation-patterns.md` (only `/al-dev-fix` references it) | Add reference to `knowledge/architect-invocation-patterns.md` in `/al-dev-plan` Phase 2

### Atomise / Absorb (Complexity)

- **al-dev-plan** | High | 9 phases split cleanly at phase 1.6 boundary: pre-planning (phases 0–1.6) is context gathering; architect debate (phases 2–7) is synthesis | Add `--resume-from=phase2` flag to skip preflight; or split into `al-dev-plan-preflight` + `al-dev-plan-architect`
- **al-dev-ticket** | Medium | 8 phases with mode gate at phase 5; phases 0.5–4 are complete self-contained context-fetch; phases 6–8 are optional extension | Consider split: `al-dev-ticket` (phases 0.5–4) + `al-dev-support-reply` (phases 6–8); or add `--resume-from=phase5`
- **verify-commits** | Medium | 2–3 steps, no agents, logic is thin (count expected commits, compare git log, reset if mismatch); overlaps with `/al-dev-commit` post-execution responsibilities | Absorb into `/al-dev-commit` as post-commit verification phase or optional `--verify` flag

### Extend (Handoff Gaps)

- **Commit → deploy chain gap** | Medium | Release notes chain (`al-dev-commit` → `verify-commits` → git → `al-dev-release-notes`) ends with no downstream consumer; release notes are a complete deliverable with no publish/deploy step | Add optional `/al-dev-deploy` skill consuming `*-al-dev-release-notes-*.md` for deployment orchestration; deferred pending scope clarity
- **al-dev-consolidate output orphaned** | Low | `.dev/sessions/` output has no downstream consumer; intentional terminal utility | Document as standalone archival terminal or add note in Layer 1 diagram

---

## Quality findings

### Bloat

**Agents:**

- **al-dev-ticket-agent** | High | "Workflow" section is 87 lines; inline-image detection embedded without boundary | Extract image-detection block (lines 55–68); move context file template to `knowledge/`
- **al-dev-commit-message-drafter** | High | "Phase: message-drafting" is 110 lines; gitmoji table and guidelines consume most of it | Extract gitmoji table to `knowledge/`; keep only grouping logic in agent
- **al-dev-developer-tdd + al-dev-developer-traditional** | High | "Standards" section is 51 lines each; "Compile Output — Critical Safeguard" block is identical in both (20 lines) | Extract to `knowledge/compile-output-safeguard.md`; reference from both agents
- **al-dev-commit-lint-fixer** | High | "Phase: lint-preflight" is 47 lines | Split into "Line Count Capture" and "Lint & Whitespace Fixing" subsections
- **al-dev-security-reviewer** | High | "Review Focus" is 47 lines with inline vulnerability taxonomy | Extract taxonomy to `knowledge/`
- **al-dev-solution-architect** | High | "Workflow" is 40 lines with Symbol Evidence hierarchy and MCP tools table inline | Extract both to `knowledge/`
- **al-dev-diagnostics-fixer** | High | "Process" is 39 lines with judgment-required rules reference table inline | Extract reference table to separate section
- **al-dev-interview** | High | "Interview Process" is 38 lines with question categories inline | Extract categories to `knowledge/`
- **al-dev-commit-agent-analysis** | High | "Manifest Extraction (Steps 1–3)" is 31 lines | Extract extraction patterns into reference table
- **al-dev-script-engineer** | High | "Standards" is 32 lines with language-specific patterns inline | Extract to `knowledge/`

**Skills:**

- **al-dev-commit** | High | Phase 0 is 160+ lines with 7 sub-steps; compile-gate instructions repeated in multiple sections | Consolidate Phase 0; extract compile-gate to reusable knowledge reference
- **al-dev-consolidate** | High | Phase 2 is 74 lines with bash patterns repeated for groups A–D | Extract to `knowledge/consolidate-extraction-patterns.md`; use single parameterized step
- **al-dev-develop** | High | Phase 1 signature verification spans 58 lines; Phase 4 static validation adds 70+ lines | Extract verification and validation to dedicated knowledge files
- **al-dev-fix** | High | Step 3 alone is 100+ lines; compile-lint references duplicated across trivial and non-trivial paths | Extract complexity classification to `knowledge/fix-complexity-classifier.md`
- **al-dev-plan** | High | Phase 1 is 50+ lines; Phase 1.5 (External Claims) adds 38 lines repeating symbol verification | Extract input validation and claims verification to reusable `knowledge/` patterns
- **al-dev-review-develop** | Medium | Phase 2 and Phase 4 have identical agent dispatch template headers; Phase 5 repeats artifact-contracts.md contract | Extract review-panel dispatch template to knowledge file
- **al-dev-ticket** | Medium | Steps 1–2 have overlapping auto-detection and credential verification blocks | Consolidate into single "Resolve & Load" step
- **al-dev-document** | Medium | Step 0 and Step 2 both include identical documentation structure outline (22 lines); RTM instructions appear twice | Extract to external template file
- **al-dev-perf** | Medium | Step 1a (40+ lines) overlaps with Step 2 agent prompt on performance entry-point classification | Extract to `knowledge/perf-anti-patterns-prompt.md`
- **plan-map-changes** | Medium | Phase 1, 2, 3 each define same validation pattern (35+ lines each) | Extract universal checks to knowledge file
- **plugin-health** | Medium | Phase 1 and Phase 3 both include identical checkpoint loading and status-checking patterns | Consolidate checkpoint logic to single knowledge file

### Clarity

**Agents — High severity:**

- **al-dev-ticket-agent** | High | "Detect Inline Image Attachments" specifies regex patterns but does not define what tool/language to use | Specify: "Use bash `grep -oE` to extract `src="[^"]+"` from HTML; filter for `cdn.freshdesk.com` or `cid:` patterns"
- **al-dev-interview** | High | "INTERVIEW COMPLETE" gate has no terminal failure condition after retry | Add: "After 2 retry rounds with uncovered categories, escalate to user with list of missing categories"
- **al-dev-interview** | High | "Ask 40+ questions (typical)" uses vague qualifier | Clarify: "40+ for COMPLEX features, 25–35 for MEDIUM, 10–15 for SIMPLE"
- **al-dev-solution-architect** | High | Schema mapping requires UNVERIFIED → BLOCKED but "verification" is undefined | Clarify: "VERIFIED = found via AL LSP, AL MCP, or exact text search with file:line"
- **al-dev-commit-agent-analysis** | High | Diff extraction logic ("names on both `-` and `+` lines") is ambiguous for modified vs added procedures | Define: "procs_modified = names in both `-` and `+` hunks; procs_added = `+` only; procs_removed = `-` only"
- **al-dev-commit-lint-fixer** | High | "`\s` is dangerous in sed" warning lacks context for when the risk applies | Clarify: "Never use `\s` in sed regex on any platform; `[ \t]` is the safe portable form"

**Skills — High severity:**

- **al-dev-plan** | High | Phase 1 incomplete conditional: "STOP immediately" if vague input, no terminal condition after retry | Add terminal: "After second vague response, offer user: (1) provide specific context, (2) run /interview first, (3) cancel"
- **al-dev-fix** | High | Step 2 "spawn traditional (trivial, no test plan)" contradicts Step 3 "check for a test plan" for non-trivial | Clarify: "TRIVIAL: skip test plan check; always use traditional. NON-TRIVIAL: dispatch TDD if test plan present, else traditional"
- **al-dev-interview** | High | "Fallback if INTERVIEW COMPLETE not received" — retry logic exists but no terminal condition | Add terminal condition after 2 retry rounds
- **al-dev-commit** | High | "If `$AL_STAGED` is non-empty, run compile gate" lacks `else` clause for non-AL-only staged changes | Add: "If `$AL_STAGED` is empty, skip compile gate and proceed to Phase 1"
- **plan-map-changes** | High | Phase 2 decision tree has no failure handling for either inline or remote verification path | Add: "If inline fails: write error record, offer (skip / retry / abort). If remote fails: offer (inline verify / abort)"

**Medium severity (selection):** vague qualifiers in al-dev-commit "representative diagnostics", al-dev-fix "minimal", al-dev-help "multiple", al-dev-perf "high-volume"; missing `else` clauses in al-dev-consolidate, al-dev-develop, al-dev-release-notes, commit-recover; case-sensitivity ambiguity in al-dev-ticket mode flag; `verify-commits` `<N>` placeholder undefined.

### Description drift

**Medium severity:**
- **al-dev-diagnostics-fixer** | Medium | Description says "applies auto-fixes" but body documents judgment-required rules NOT auto-fixed as core output | Add: judgment-required rule identification to description
- **al-dev-interview** | Medium | Description omits INTERVIEW_COMPLETE signal requirement and mandatory 11-category coverage gate | Add gate requirement to description
- **al-dev-solution-architect** | Medium | Description omits that testability architecture is mandatory | Add: "Testability architecture is mandatory; plan must include structured RTM acceptance criteria"
- **al-dev-commit-recover-verifier** | Medium | Description names all three fallback strategies but body only documents git restore in detail | Expand body to detail all three strategies
- **al-dev-support-reply-drafter** | Medium | Description omits independent customer-claim assessment and mandatory Microsoft source citation | Add both to description
- **al-dev-ticket-agent** | Medium | Description omits inline image detection via `src=` and `cid:` HTML scanning | Add to description
- **al-dev-commit-lint-fixer** | Medium | Description omits line-count corruption detection and baseline capture | Add to description
- **al-dev-fix (skill)** | Medium | Description promises "lightweight workflow" but body includes architect dispatch for non-trivial fixes | Clarify dual-path nature
- **al-dev-ticket (skill)** | Medium | "optionally research" misleads — attachment download is conditional, `--mode=full` controls research | Clarify both gates

### Name fit

**High severity:**
- **al-dev-commit-recover-verifier** | High | "Verifier" implies passive check; agent applies active recovery strategies (git restore, regex, schema rebuild) | Rename to `al-dev-commit-recover-fixer`
- **plan-map-changes** | High | "Plan" implies plan creation; primary behavior is rubber-duck verification of existing suggestions | Rename to `al-dev-map-suggestions-verify`
- **plan-with-critic-swarm** | High | "Plan" implies creation; primary behavior is red-teaming/critiquing an existing plan | Rename to `al-dev-plan-swarm-validate`

**Medium severity:**
- **al-dev-commit-agent-analysis** | Medium | "agent-analysis" is generic; scope is narrowly parsing staged git diffs into per-file manifests | Rename to `al-dev-commit-manifest-analyzer`
- **al-dev-ticket-agent** | Medium | "agent" provides no scope information; scope is fetching Freshdesk tickets and writing context files | Rename to `al-dev-ticket-fetcher`
- **al-dev-diagram-generator** | Medium | Name implies user-facing but skill is dispatched exclusively by analyze-\* maintainer tools | Clarify as internal tool or rename to signal internal dispatch
- **commit-recover** | Medium | "Recover" implies active remediation but execution is inspection-first (recovery only with `--auto-fix`) | Rename to `al-dev-commit-integrity-verify` or clarify `--auto-fix` requirement

### Structure

**High severity:**
- **al-dev-fix/SKILL.md** | High | Lines 444–445 contain stray `# test` headers — debugging artifacts | Remove immediately

**Low severity (widespread):**
- **al-dev-explore/SKILL.md** | Low | `argument-hint: ""` (empty string) but body references argument `[question or area to explore]` | Correct to `argument-hint: "[question or area to explore]"`
- All 22 agents and 22 skills | Low | Missing code block language tags (`text` instead of `bash`, `al`, `markdown`, `yaml`) throughout | Apply correct language specifiers to all code blocks

---

## Naming violations

- **plugin-health-discover (SKILL.md) output path** | Medium | Intermediate lens output `.dev/YYYY-MM-DD-plugin-health-lens-{name}.json` uses `-lens-` separator, `.json` extension, and `plugin-health` as surface identifier — doesn't match pattern `{dir}/YYYY-MM-DD-{surface}-{kind}.md` | Change to `.dev/YYYY-MM-DD-plugin-{name}-findings.json` or consolidate all lens results into single findings file
- All other agents and skills | ✓ No violations | All names follow established conventions

---

## Graph deltas

Dependency graph refreshed → `docs/al-dev-plugin-graph.md` (exit 0). Review that file for any newly detected orphans or dead links.
