# Open Health Dispositions

<!-- generated from docs/health/dispositions-events/; do not edit directly -->

| Event ID | Surface | Dimension | Object | Finding | Disposition | Date | Evidence | Closes |
|----------|---------|-----------|--------|---------|-------------|------|----------|--------|
| disp_20260626_000046 | plugin | quality | al-dev-commit-group-drafter | Empty tools: [] array at al-dev-commit-group-drafter.md:1; canonical form omits the field or lists tools | accepted | 2026-06-26 | accepted — omit the tools: field (regressed from fixed disp_20260621_000049; static re-run 2026-06-26 confirms still present) |  |
| disp_20260626_000048 | plugin | quality | al-dev-fix | al-dev-fix/SKILL.md:189-197 says 'execute tests' without naming a test runner | accepted | 2026-06-26 | accepted — name the runner from the test plan (pytest/al-test/project-specific) |  |
| disp_20260626_000049 | plugin | quality | al-dev-interview | al-dev-interview/SKILL.md:78-82 unclear whether uncovered optional interview categories block completion or are noted as gaps | accepted | 2026-06-26 | accepted — clarify mandatory-5 block via failure-recovery, optional-6 best-effort |  |
| disp_20260626_000050 | plugin | quality | al-dev-document | al-dev-document/SKILL.md:4-8 description omits the Formatting-Sweep variant (second use case) | accepted | 2026-06-26 | accepted — add two-modes sentence to the description |  |
| disp_20260626_000051 | plugin | quality | al-dev-commit-lint-fixer | al-dev-commit-lint-fixer.md:62 does not state what [[:blank:]] matches | accepted | 2026-06-26 | accepted — add one-line note that [[:blank:]] matches tab and space only, not newline/carriage-return |  |
| disp_20260626_000052 | plugin | quality | al-dev-ticket-context-writer | al-dev-ticket-context-writer.md:61 embedded-image detection criteria not defined inline | accepted | 2026-06-26 | accepted — state detection criteria inline or name a specific pattern from ticket-image-patterns.md |  |
| disp_20260626_000053 | plugin | quality | al-dev-develop-orchestrate | al-dev-develop-orchestrate/SKILL.md mixes Phase N and Step N numbering | accepted | 2026-06-26 | accepted — use one numbering scheme (regressed from fixed disp_20260624_000067; static re-run 2026-06-26 confirms still present) |  |
| disp_20260626_000054 | plugin | quality | al-dev-review-develop-preflight | al-dev-review-develop-preflight/SKILL.md mixes Phase N and Step N numbering | accepted | 2026-06-26 | accepted — use one numbering scheme consistently |  |
| disp_20260626_000055 | plugin | quality | al-dev-ticket-context-writer | al-dev-ticket-context-writer.md:5 description says 'optionally download attachments' without clarifying who decides | accepted | 2026-06-26 | accepted — rephrase to downloads only when the dispatcher requests a separate download phase |  |
