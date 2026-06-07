---
name: review-maps
description: >-
  Map accuracy sync — dispatches /sync-documentation-maps as the maintained
  path for verifying and refreshing the documentation maps. Pass --no-update
  to stop after printing the async sequence instead of starting it.
  Triggers on: "review maps", "update maps", "sync maps", "are the maps
  accurate", "check the maps".
argument-hint: "[--no-update]"
workflow:
  stage: map-sync
  invoked-by: user
  repeatable: true
  next: [sync-documentation-maps]
---

# Review Maps

Keeps both `docs/al-dev-skills-map.md` and `docs/al-dev-agent-map.md` factually
current against the plugin surface. Does not emit design suggestions — all
findings come from `/plugin-health-audit`.

## Phase 0 — Parse Arguments

If `--no-update` is present, print the maintained async sequence and stop:

1. `/sync-documentation-maps`
2. `/sync-documentation-maps-collect --team-ids <skill-id>,<agent-id>`
3. `/sync-documentation-maps-apply --team-ids <id>[,<id>]`
4. `/sync-documentation-maps-write`

Do not invoke any map-review skill from this wrapper.

## Phase 1 — Dispatch

Invoke `/sync-documentation-maps` and exit.

Print:

> Map sync dispatched. Run `/plugin-health-audit` to find improvements after the
> async write completes.
