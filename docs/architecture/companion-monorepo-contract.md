# Companion Monorepo Contract

## Purpose

`al-dev-shared` owns two authored layers:

- `profile-al-dev-shared/` for shared harness-agnostic plugin content
- `companions/<harness>/<package>/` for harness-specific installable companion packages

The scratch design under `docs/superpowers/specs/` is review evidence only. This
document is the tracked source of truth for implementation and follow-on health work.

## Canonical companion surface IDs

- `companion-codex-al-dev`
- `companion-claude-al-dev`
- `companion-copilot-al-dev`

Aggregate aliases:

- `companions` = all canonical companion package surfaces
- `everything` = `plugin` + `tooling` + `companions` (surface-axis aggregate; do not reuse the
  token `all`, which is already reserved for `--dimension all` and must never double as a
  `--surface` value — see the cross-surface/cross-dimension token rule below)
- `both` = legacy alias for `plugin` + `tooling` only

## Cross-axis token rule

`--surface` and `--dimension` are separate axes with separate vocabularies. No token may be
valid as both a surface value and a dimension value. `all` is reserved exclusively for
`--dimension all`; the surface-axis aggregate is spelled `everything`.

## Cross-surface dependency rule

Shared workflows may suggest companion capabilities, but they must degrade cleanly
when the companion package is not installed. Co-location in this monorepo does not
create an implicit runtime dependency.

## Embedded manifest decision

`profile-al-dev-shared/.claude-plugin/plugin.json` and
`profile-al-dev-shared/.plugin/plugin.json` remain thin distribution adapters until
their companion replacements are proven. They may contain packaging metadata only,
never harness-specific workflow behavior.
