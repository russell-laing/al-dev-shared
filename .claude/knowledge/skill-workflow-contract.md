# Skill Workflow Contract

The `workflow:` frontmatter block in `.claude/skills/*/SKILL.md` is a
**repo-local extension** consumed by `python3 scripts/generate_maintainer_guide.py`.
It is not consumed by Claude Code or any distributed harness.

## Schema

```yaml
workflow:
  stage: map-sync | discover | decide | implement | derive | support
  invoked-by: user | both | skill:<name>
  repeatable: true | false
  inputs:                       # optional — list of input path templates
    - some/path/<placeholder>
  outputs:                      # optional — list of output path templates
    - some/path/<placeholder>
  next:                         # optional — skill names that follow in the loop
    - skill-name
  manual-followup: "string"     # optional — human step that follows automatically
```

Required fields: `stage` and `invoked-by`. All others are optional.
`repeatable` defaults to `false` when omitted.

## Stage Meanings

| Stage | Description |
| --- | --- |
| `map-sync` | Synchronises documentation maps with the plugin surface |
| `discover` | Dispatches lenses and gathers raw findings |
| `decide` | Presents findings to the user for disposition or planning |
| `implement` | Executes implementation tasks and closes the disposition ledger |
| `derive` | Generates or validates derived artifacts from the plugin surface |
| `support` | Adjacent tooling — not in the core self-healing loop |

## `invoked-by` Values

| Value | Meaning |
| --- | --- |
| `user` | Triggered directly by the user |
| `both` | Triggered by the user AND internally by another skill |
| `skill:<name>` | Triggered only internally by skill `<name>` |

## Skills Without a Contract

Skills with no `workflow:` block appear in the "Missing contract" gap table
of `docs/maintainer_tooling.md`. If a skill genuinely has no place in the
self-healing loop, it should remain uncontracted — adding a `workflow:` block
(even with `stage: support`) would cause it to be included in health audit
lens runs by `discover-plugin-health`.

## Generator

`python3 scripts/generate_maintainer_guide.py` reads all `workflow:` blocks from
`.claude/skills/*/SKILL.md` (excluding `archived/`) and rewrites the
`<!-- BEGIN GENERATED: ... -->` sections of `docs/maintainer_tooling.md` and
`docs/maintainer_tooling/*.md`.

Validation rules (fail-closed):

- Unknown keys → error naming the offending skill and key
- `stage` not in the allowed set → error
- `invoked-by` not in `user | both | skill:<name>` pattern → error
- `next` references a skill name not found in the active set → error
