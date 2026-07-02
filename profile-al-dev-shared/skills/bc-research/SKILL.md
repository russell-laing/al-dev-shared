---
name: bc-research
description: >-
  Research a BC/AL question using curated-first evidence, local repo
  discovery, and specialist research synthesis. Use for greenfield
  research, repo-focused research, version-history research, and
  broader Microsoft ecosystem questions.
argument-hint: "[question] [--repo] [--greenfield] [--version-history] [--ecosystem-wide]"
tools: ["Read", "Glob", "Grep", "Write", "Bash", "USER_GATE"]
---

# Research Skill

Research a question by classifying scope, dispatching the smallest useful set
of specialist researchers, and synthesizing one evidence-labeled answer.

## Intent

Use `/research` when the user wants evidence-driven exploration rather than an
implementation plan or direct code changes. The skill is intentionally thin:
it infers mode, narrows scope when needed, delegates deep research, and then
combines the results into a single response or durable markdown artifact.

This skill is governed by:

- `knowledge/research-source-policy.md`
- `knowledge/research-output-format.md`

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| User question | **Yes** | The research prompt or problem statement |
| Flags | No | `--repo`, `--greenfield`, `--version-history`, `--ecosystem-wide` |
| Current repo context | No | Local files, docs, tests, or known subsystem hints |

## Outputs

| Output | Description |
|--------|-------------|
| Inline response | Required; must follow the shared research output format |
| Durable artifact | `.dev/YYYY-MM-DD-research-findings.md` when warranted |

## Phase 0: Classify the Request

Determine:

- requested mode, if explicit
- inferred mode, if implicit
- whether the request is repo-focused, exploratory, version-history driven, or
  ecosystem-wide
- intended source breadth before deep work begins

Before deep research starts, report:

- `MODE`
- initial `SCOPE`
- intended source breadth

Explicit flags override inference. If no flag is supplied, infer the mode from
the wording of the request and state the inference before continuing.

## Phase 1: Narrow Repo Scope When Needed

If the run is repo-focused and the scope is not explicit:

1. inspect the current repo
2. identify likely relevant files, directories, or subsystems
3. restate the inferred scope
4. continue only with that declared scope

This pass is intentionally shallow. It exists to prevent silent research against
the wrong surface, not to replace the actual research.

## Phase 2: Dispatch Specialist Research

Dispatch only the specialists the question needs. Do not dispatch extra agents
by default.

- `repo` -> `Dispatch agent: al-dev-shared:repo-researcher`
- `repo` -> `Dispatch agent: al-dev-shared:ecosystem-researcher` when the
  question also needs external BC/AL validation, official guidance, or version
  history confirmation
- `greenfield` -> usually `Dispatch agent: al-dev-shared:ecosystem-researcher`
- `version-history` -> usually `Dispatch agent: al-dev-shared:ecosystem-researcher`
- `ecosystem-wide` -> `Dispatch agent: al-dev-shared:ecosystem-researcher`

If repo context matters for `greenfield`, `version-history`, or
`ecosystem-wide`, also dispatch `Dispatch agent: al-dev-shared:repo-researcher`
with the same question and a narrower local scope.

When dispatching specialists, provide:

- `RESEARCH_QUESTION`
- `RESEARCH_SCOPE`
- `CONTEXT_PATHS` when relevant
- `VERSION_SCOPE` when relevant
- `PRIOR_FINDINGS` or `LOCAL_FINDINGS` when another lane already produced them

## Phase 3: Synthesize Results

Combine the specialist outputs into one answer. Do not return parallel
transcripts. The final response and any durable artifact must follow
`knowledge/research-output-format.md`.

When evidence strength is mixed, keep the strongest label visible and explain
the gap rather than flattening the result.

## Phase 4: Decide on Durable Output

Default artifact policy:

- repo-focused research writes a durable artifact by default
- lightweight greenfield research may remain inline-only when it does not need
  repo discovery or a saved handoff
- the user may request persistence for any mode

Write a durable artifact whenever the run needed repo discovery or the user
explicitly requested persistence. Otherwise, keep the answer inline-only.

When writing a durable artifact, use:

```text
.dev/YYYY-MM-DD-research-findings.md
```

Keep the inline response and durable artifact structurally aligned so the
answer can move between them without reformatting.

## Degradation

If the question stays too broad after the shallow discovery pass, stop and
propose narrower research tracks instead of fabricating a comprehensive answer.
Missing evidence should lower confidence, not trigger speculation.
