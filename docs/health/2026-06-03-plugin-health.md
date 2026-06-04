# Plugin Health — 2026-06-03

## Summary

| Severity | Design | Quality | Naming | Total |
|----------|--------|---------|--------|-------|
| High     | 0      | 8       | 0      | 8     |
| Medium   | 12     | 15      | 4      | 31    |
| Low      | 10     | 40      | 0      | 50    |

> **Coverage note:** 16 of 21 plugin lenses completed. Five quality skill lenses
> (`quality-skill-lens-bloat/clarity/description/name-fit/structure`) failed due
> to a session limit during dispatch. Quality findings below cover agents only.
> Tooling surface not re-audited this run (unchanged since 2026-06-03 morning run).

**Top 5 ranked actions:**

1. **al-dev-solution-architect** — Two High clarity gaps (ambiguous "best existing analogue" disjunction; undefined "required symbol" operational condition) plus a High bloat issue ("Output Format" ~55 lines). Highest-impact single agent.
2. **al-dev-developer-tdd / al-dev-developer-traditional** — Both have High bloat (9 sections) and an undefined `SYMBOL_PREFLIGHT_GATE` clarity gap affecting execution reliability across two callers.
3. **al-dev-diagnostics-fixer** — High bloat (8 sections) combined with a High clarity issue in Step 3b (ambiguous Edit tool scope). Fix prevents interpretation variance during lint recovery.
4. **al-dev-commit-lint-fixer** — High clarity: restoration command in Step 4 says "restore the file" with no concrete command. Fix: add `git checkout HEAD -- <file>`.
5. **Surface placement (plugin-health-audit, al-dev-consolidate, al-dev-diagram-generator)** — Three skills score all three misplacement signals. Moving them cleans the distributed plugin surface.

---

## Design suggestions

### Trim

- **al-dev-support-researcher** | Medium | MCP tools declared in frontmatter but body contains only aspirational descriptions with no concrete invocation examples. | Add explicit MCP invocation examples (tool name, parameter format) or remove MCP tools from frontmatter and clarify reliance on prompt-based reasoning alone.

### Remodel

- **al-dev-code-review** | Medium | Assigned haiku but task requires multi-file code analysis and severity synthesis — sonnet-level reasoning. | Upgrade to sonnet.

### Align

- **al-dev-commit-message-drafter** | Medium | Inputs table does not state that MANIFESTS, PROJECT_CONTEXT, FD_TICKET arrive as inline structured text blocks (not file paths). | Clarify Inputs table.
- **al-dev-solution-architect** | Medium | Inputs table implies glob-location of requirements file is agent's responsibility, but callers pass requirements inline. | Clarify: either caller glob-locates and passes path, or remove glob expectation from Inputs and add it as optional enhancement in agent's Workflow section.
- **al-dev-support-researcher** | Low | Inputs table does not list `TICKET_FILE` as an input, but `/al-dev-support-reply` Phase 1 passes it. | Add `TICKET_FILE` as `(optional)`.
- **al-dev-interview** | Low | Agent has Read in tools but dispatch contract says skill pre-reads file before dispatch. | Clarify whether agent receives pre-read content inline or reads the file path itself.

### Move (surface placement)

- **plugin-health-audit** | Medium | Scores all three misplacement signals: internal path references, self-audit purpose, no spawned agents. | Move to `.claude/skills/`.
- **al-dev-consolidate** | Medium | Scores all three misplacement signals: internal paths (`.dev/sessions/`, `.claude/settings.json`), self-audit purpose, no spawned agents. | Move to `.claude/skills/`.
- **al-dev-diagram-generator** | Medium | Scores all three misplacement signals: internal path references, self-audit purpose, no spawned agents. | Move to `.claude/skills/`.
- **al-dev-map-suggestions-verify** | Low | Scores two signals: internal path references, no spawned agents. | Move to `.claude/skills/`.

### Atomise

- **al-dev-review-develop** | Medium | 6 phases spanning two separable concerns: pre-review qualification (phases 1–3) and review execution (phases 4–6). Natural split boundary after Phase 3. | Consider extracting phase 4+ into a separate orchestrator if review feedback loops become complex.

### Connect (shared backbone)

- **al-dev-developer-traditional** | Medium | Identical spawn pattern across al-dev-develop, al-dev-fix, and al-dev-review-develop — drift risk if invocation pattern changes. | Verify all three skills reference `knowledge/developer-invocation-patterns.md` explicitly and pass identical context structure.
- **al-dev-commit-agent-*** (6 agents) | Medium | Identical sequential dispatch with strong coupling — drift risk across six phase prompt templates. | Extract six-phase commit orchestration pattern to `knowledge/commit-workflow-orchestration.md`.
- **al-dev-al-pattern-reviewer, al-dev-security-reviewer, al-dev-performance-reviewer** | Medium | Three parallel reviewers share identical dispatch template and severity taxonomy — synchronized change requirement. | Extract `knowledge/review-panel-invocation-pattern.md` to lock dispatch template and severity scale.
- **al-dev-developer-tdd** | Low | Similar but intentionally different spawn patterns in al-dev-develop vs al-dev-fix. | Document both TDD routing contexts in `knowledge/developer-invocation-patterns.md`.

### Extend (handoff gaps)

- **post-commit-release-deployment** | Medium | al-dev-commit → al-dev-release-notes chain ends at release notes. Natural next step (deploy to UAT/Prod, verify, promote) has no skill. | Create `/al-dev-deploy` skill.
- **vault-sync-from-consolidate** | Low | al-dev-consolidate produces vault-ready artifacts with no downstream import skill. | Create `/al-dev-vault-import` skill or enhance al-dev-consolidate.
- **perf-findings-to-fix** | Low | al-dev-perf produces prioritized findings but does not orchestrate handoff to /al-dev-plan or /al-dev-fix. | Create optional `/al-dev-perf-fix-bridge` skill.

### Pre-planning label gaps

- **al-dev-explore** | Low | Dashed tributary arrow to al-dev-plan has no handoff label. | Add label `-.->|explore-findings.md|`.
- **al-dev-interview** | Low | Dashed tributary arrow to al-dev-plan has no handoff label. | Add label `-.->|interview-requirements.md|`.
- **al-dev-perf** | Low | Dashed tributary arrow to al-dev-plan has no handoff label. | Add label `-.->|perf-analysis.md|`.
- **al-dev-plan-preflight** | Low | Dashed tributary arrow to al-dev-plan has no handoff label despite contract in artifact-contracts.md. | Add label `-.->|preflight-context.md|`.

---

## Quality findings

### Bloat — agents

- **al-dev-developer-tdd** | High | 9 top-level sections (limit: 6). | Consolidate "Standards" subsections into a single "Code Quality Standards" section.
- **al-dev-developer-traditional** | High | 9 top-level sections (limit: 6). | Same as al-dev-developer-tdd.
- **al-dev-solution-architect** | High | "Output Format" section spans ~55 lines (schema mapping decision guide). | Move to referenced knowledge file; keep inline instruction to use the 5-column table structure only.
- **al-dev-diagnostics-fixer** | High | 8 top-level sections (limit: 6). | Consolidate "Process" + "Step 1"–"Step 5" + "Judgment-Required Rules Reference" into a unified "Fix Process" section.
- **al-dev-security-reviewer** | Medium | Repetitive "document file:line, severity, issue" pattern shared across all four specialist reviewer agents. | Extract common reviewer output instructions to shared knowledge template.
- **al-dev-code-review** | Medium | Repetitive instruction blocks shared with al-dev-al-pattern-reviewer and al-dev-performance-reviewer. | Cross-reference shared "reviewer-findings-template.md" in knowledge.
- **al-dev-interview** | Medium | Fallback condition block for missing "INTERVIEW COMPLETE" belongs in the calling skill's dispatch logic. | Move to `/al-dev-interview` skill.
- **al-dev-ticket-agent** | Medium | "Detect Inline Image Attachments" subsection contains 3+ regex patterns that belong in a reference guide. | Extract to companion knowledge file.
- **al-dev-commit-agent-analysis** | Medium | Manifest extraction instructions contain diff-parsing regex implementation details. | Move to `knowledge/commit-analysis-patterns.md`.
- **al-dev-performance-reviewer** | Medium | "Performance Patterns Reference" section duplicates knowledge file reference. | Remove "Key patterns to look for" list; keep single reference.

### Clarity — agents

- **al-dev-commit-lint-fixer** | High | Step 4 "restore the file" lacks explicit restoration command. | Add: `git checkout HEAD -- <file>`.
- **al-dev-diagnostics-fixer** | High | Ambiguous instruction in Step 3b: 3+ vs 1–2 occurrences scope is unclear. | Clarify: "For 3+, use single Edit call; for 1–2, use separate Edit calls per instance."
- **al-dev-solution-architect** | High | "Best existing analogue" — same business function OR same pattern creates ambiguous disjunction. | Clarify: require both criteria; document rationale if only one is met.
- **al-dev-solution-architect** | High | "Required external symbol" — "required" not operationally defined. | Define: "A symbol is 'required' if the implementation plan explicitly references it in code."
- **al-dev-commit-agent-analysis** | Medium | No `else` branch for non-AL files in manifest extraction. | Add: "Non-AL files: emit a simple one-liner manifest."
- **al-dev-commit-hook-fixer** | Medium | "As needed" in Step 3 recovery actions lacks decision criteria. | Clarify: "Apply scripted fixes ONLY if fix can be validated immediately via re-compile or lint check."
- **al-dev-developer-tdd** | Medium | `SYMBOL_PREFLIGHT_GATE` "unverified" not defined operationally. | Define: "Cannot be located via AL LSP, AL MCP, or text search with exact file:line evidence."
- **al-dev-developer-traditional** | Medium | Same `SYMBOL_PREFLIGHT_GATE` gap as al-dev-developer-tdd. | Same fix.
- **al-dev-interview** | Medium | No `else` branch if USER_GATE fails or user declines. | Add: "Document stopping point and return findings from completed question groups."
- **al-dev-support-reply-drafter** | Medium | "Independently assess actual technical capabilities" lacks framework. | Specify: cross-reference AL symbols, MS Docs, BC code history; note "unverified capability" if not documented.
- **al-dev-ticket-agent** | Medium | No explicit handling for `data:image` URIs vs external URLs. | Clarify: "For base64 embeds, note as 'inline base64 image (not downloaded)'."
- _(13 Low clarity findings — see findings file for full detail)_

### Description drift — agents

- **al-dev-release-notes-writer** | Medium | Description says agent "researches AL object context" but tools list omits MCP tools despite body referencing AL MCP Server. | Add `MCP: bc-code-intelligence` to tools, or clarify MCP unavailable.
- **al-dev-support-researcher** | Medium | Description does not mention agent writes no output file (body says "no file writes"). | Clarify: "Produces internal technical findings only (no file output)."
- _(6 Low description-drift findings — see findings file for full detail)_

### Structure — agents

_(21 Low findings — all agents are missing language tags on at least one code block. See findings file for per-agent detail.)_

### Quality skill lenses — not available this run

The five quality skill lenses (`bloat`, `clarity`, `description`, `name-fit`, `structure`) hit the session limit and did not complete. Re-run with `--resume --surface plugin` to add skill quality findings.

---

## Naming violations

- **al-dev-release-notes-writer output path** | Medium | `.dev/$(date +%Y-%m-%d)-al-dev-release-notes-<VERSION>.md` — includes agent name and VERSION suffix; violates `YYYY-MM-DD-{surface}-{kind}.md`. | Rename to `.dev/YYYY-MM-DD-plugin-release-notes.md`.
- **al-dev-support-reply-drafter output path** | Medium | `.dev/<date>-support-<slug>.md` — `<slug>` placeholder; not `{surface}-{kind}` format. | Rename to `.dev/YYYY-MM-DD-plugin-support-reply.md`.
- **al-dev-ticket-agent output path** | Medium | `.dev/<date>-al-dev-ticket-ticket-context.md` — includes agent name prefix and repeated "ticket". | Rename to `.dev/YYYY-MM-DD-plugin-ticket.md`.
- **al-dev-commit-recover-fixer output path** | Medium | `.dev/YYYY-MM-DD-al-dev-commit-recover-report.md` — includes agent name. | Rename to `.dev/YYYY-MM-DD-plugin-recover.md`.

---

## Graph deltas

_No orphaned skills or dead links detected. Four skills flagged for surface-placement Move (see Design suggestions); these are misplaced content, not broken links._
