# Research Output Format

Research responses should use the same section structure inline and in durable
markdown artifacts so the answer can move between live output and a saved file
without reformatting.

## Inline Response Structure

Every inline `/research` response must include these top-level sections in this
order:

1. `MODE`
2. `SCOPE`
3. `SOURCES`
4. `SUMMARY`
5. `FINDINGS`
6. `UNCERTAINTIES`
7. `NEXT STEPS`

## Durable File Structure

Durable artifacts should use the same section order and labels in markdown.
The default artifact path is:

```text
.dev/YYYY-MM-DD-research-findings.md
```

## Required Headings and Labels

Use the following headings exactly, or the closest markdown equivalent if the
consumer requires different heading levels:

```markdown
# Research Findings

## MODE
- Mode: [repo | greenfield | version-history | ecosystem-wide]
- Scope: [short scope statement]

## SOURCES
- repo-verified: [what was verified in the workspace]
- mcp-verified: [what was verified through MCP]
- curated-secondary: [what curated source supported the claim]
- broad-web: [what broader source was needed, if any]

## SUMMARY
[one short paragraph]

## FINDINGS
### [short finding title]
- Claim: [the finding]
- Evidence: [source label and brief support]
- Confidence: [confirmed | likely | tentative | unverified]

## UNCERTAINTIES
- [gap, constraint, or open question]

## NEXT STEPS
- [recommended next action]
```

The `SOURCES` section should identify each source tier that materially
contributed to the answer. The `FINDINGS` section should keep source labels
visible next to the claim or evidence note.

## Recommended Next-Step Section

The `NEXT STEPS` section should be present by default, even when the answer is
mostly complete. Keep it brief and actionable.

- Prefer one to three concrete follow-up actions.
- Use it to narrow the next research pass, validate a risky assumption, or
  point to the next useful artifact.
- If no follow-up is needed, state that the current evidence is sufficient and
  keep the section to a single sentence or a single bullet.

## Structural Rules

- Keep the inline and durable shapes aligned.
- Do not add extra top-level sections that would obscure the required contract
  sections.
- When evidence is mixed, keep the source label visible in the relevant
  finding.
- When evidence is incomplete, preserve the section order and lower the stated
  confidence instead of widening the conclusion.

