# Intent Preflight

Intent preflight prevents a skill from silently acting on a different intent
than the user asked for.

Run this preflight before a non-trivial workflow dispatches agents, edits
files, writes workflow artifacts or reports, stages files, compiles with
auto-fix behavior, or commits.

## Intent Classes

Classify the user's request as exactly one of:

| Intent | Meaning | Allowed Work |
|---|---|---|
| `REVIEW` | Analyze, inspect, summarize, audit, or critique only. | Read files, run non-mutating inspection commands, write an explicitly requested report artifact. Do not edit project/runtime files. Do not commit. |
| `EDIT` | Modify files, implement a fix, or generate changed artifacts. | Edit files inside the approved scope. Do not commit unless the user separately asks for a commit. |
| `COMMIT` | Stage and commit explicitly approved changes. | Inspect and commit staged or approved changes after all commit gates pass. Do not add unrelated files. |

## Mismatch Rule

If the invoked skill and detected intent disagree, stop before agent dispatch or any mutating action and ask for confirmation.

Use this prompt:

```text
Intent mismatch: this request appears to be [REVIEW|EDIT|COMMIT], but [skill-name] normally performs [expected intent]. Confirm the intended action before I continue.
```

Continue only after the user confirms the intended action.

## Skill Defaults

| Skill | Default Intent |
|---|---|
| `al-dev-commit` | `COMMIT` |
| `al-dev-develop-orchestrate` | `EDIT` |
| `al-dev-fix` | `EDIT` |
| `al-dev-lint` | `EDIT` |
| `al-dev-plan-preflight` | `REVIEW` for reusable planning-context assembly; writing the requested `.dev/preflight-context.md` artifact is allowed within that review workflow |
| `al-dev-plan` | `REVIEW` for design, planning, or architecture output; writing the requested `.dev/` plan artifact is allowed within that review workflow |

## Examples

| User Request | Intent | Result |
|---|---|---|
| "review this usage report and suggest possible plugin improvements" | `REVIEW` | Do not invoke implementation or commit workflows. |
| "audit the validation output and tell me what failed" | `REVIEW` | Do not route to implementation planning. |
| "fix the posting bug" | `EDIT` | A fix workflow may edit files after normal scope checks. |
| "implement the approved plan" | `EDIT` | A develop workflow may proceed after confirming the plan exists. |
| "commit the staged changes" | `COMMIT` | A commit workflow may proceed through commit gates. |

## Artifact Mismatch Checks

Before continuing, compare the user's wording with the artifact they pointed to:

- design/spec document + "implement/execute" → confirm whether the user wants planning output or implementation
- plan document + "review/audit only" → treat as `REVIEW` unless the user confirms implementation
- code or diagnostics + "summarize what failed" → treat as `REVIEW`, not `EDIT`
- staged changes or commit diff + "explain/review only" → treat as `REVIEW`, not `COMMIT`
- compile log or lint report + "assess/explain only" → treat as `REVIEW`, not `EDIT`

Use existing shared-profile skills when clarifying. Do not route through external skill names that are outside this profile's published surface.
