# Research Source Policy

Research outputs should be evidence-driven, curated-first, and explicit about
what was verified versus inferred. The same policy applies across harnesses and
across both inline responses and durable files.

## Evidence Hierarchy

Use the strongest available evidence first and do not skip a higher tier when
it is available and relevant.

1. `repo-verified` - local repository evidence such as source files, docs,
   manifests, tests, or other workspace-resident artifacts
2. `mcp-verified` - semantic or knowledge evidence returned by an available MCP
   source
3. `curated-secondary` - curated guidance, maintained examples, or source
   material that is not the primary system of record but is still controlled and
   intentionally selected
4. `broad-web` - wider web sources used only when the curated set is
   insufficient for the question

If multiple evidence tiers support the same conclusion, label the strongest
tier that directly supports the claim and note any weaker supporting tiers
separately.

## Curated-First Rules

- Start with local repository evidence when the question is anchored to the
  current workspace.
- Use MCP-backed evidence before falling back to broad web research when an MCP
  source can answer the question.
- Prefer curated secondary sources over open-ended web search for language,
  product, or ecosystem guidance.
- Treat curated guidance as the default expansion path for greenfield or
  ecosystem questions.
- Keep the source set narrow until the evidence shows that broader coverage is
  required.

## When Broader Sources Are Allowed

Broader sources are allowed only when the curated set does not adequately
answer the question or would leave a material gap in the conclusion.

Examples:

- official product or API guidance is missing from curated sources
- version history requires additional context beyond local evidence and curated
  references
- the question crosses into adjacent Microsoft ecosystem areas that the
  curated set does not cover well enough
- the available evidence conflicts and a broader corroborating source is needed

When broader sources are used, state why the curated set was insufficient and
keep the broader search tightly scoped to the gap.

## Source Labeling Expectations

Every material claim should carry an evidence label:

- `repo-verified` for claims supported directly by the current workspace
- `mcp-verified` for claims supported by an available MCP source
- `curated-secondary` for claims supported by curated but non-primary sources
- `broad-web` for claims that depend on broader web evidence

If a single conclusion depends on mixed evidence, show the mix rather than
collapsing it into an unlabeled statement. A brief qualifier such as "repo-
verified with curated-secondary support" is preferred over an unqualified
assertion.

For Microsoft Docs URLs in research notes, `[verified]` and `[unverified]`
describe fetch status only. They are a transport marker layered on top of the
core evidence labels above and must not replace `mcp-verified`,
`curated-secondary`, or `broad-web`.

When AL symbol evidence matters, use the most specific available sublabel in
the evidence note and keep the core tier visible:

- `AL LSP` for workspace-semantic verification
- `AL MCP` for object/member/package symbol verification through MCP
- `text search` for tightly scoped text evidence when no semantic provider is
  available
- `unverified` when required symbol evidence was not established

## Confidence Downgrade Rules

Missing evidence should lower confidence, not trigger speculation.

- If the strongest expected source is unavailable, say so and continue with the
  best available lower tier.
- If the answer is only partially supported, mark the conclusion as tentative
  or likely rather than confirmed.
- If the evidence is indirect, incomplete, or contradictory, explicitly name
  the gap and avoid presenting the result as settled.
- If a claim cannot be supported by any available source tier, label it
  unverified and stop short of a definitive recommendation.

Confidence language should track the evidence:

- confirmed: direct support from the strongest relevant source tier
- likely: partial but reasonable support from available evidence
- tentative: the available evidence points in a direction, but the gap is
  material
- unverified: insufficient evidence to support a substantive claim
