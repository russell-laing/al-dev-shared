# Critic Dispatch Template

Used by `/plan-with-critics` and similar multi-critic skills. Documents how critics are assigned, how their outputs are deduplicated, and how severity consensus is resolved.

## Critic Batch Composition (6 critics)

1. **Correctness critic** — Does the implementation behave correctly?
2. **Type-safety critic** — Does the code maintain type contracts?
3. **Test coverage critic** — Are edge cases tested?
4. **Performance critic** — Is the implementation efficient?
5. **API-contract critic** — Does the implementation honor public interfaces?
6. **Rollback-safety critic** — Can this be safely reverted if needed?

## Deduplication by Severity

After all critics return, group findings by severity (Critical, High, Medium, Low) and location (file:line). For duplicates across critics:

- Keep the most specific finding (one with the clearest remediation)
- Record which critics agreed (2-6)
- Discard generic repeats

## Consensus on Disagreements

If critics disagree on severity, use this tiebreaker:

- 5-6 critics agree → accept majority severity
- 4 critics agree → escalate to High (conservative)
- 3 critics agree → escalate to Medium
- <3 critics → record dissent and ask for clarification

## Output Format

Final report groups by severity (Critical, then High, then Medium, then Low) and is reviewable as a single document.
