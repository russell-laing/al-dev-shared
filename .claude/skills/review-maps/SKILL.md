---
name: review-maps
description: >-
  Map accuracy sync — asks whether to run in-session or async at start.
  In-session runs /review-skill-map + /review-agent-map now; async dispatches
  /sync-documentation-maps and frees this session (collect results later with
  /sync-documentation-maps-collect). Pass --no-update to skip the mode prompt
  and audit both maps in-session without modifying them.
  Triggers on: "review maps", "update maps", "sync maps", "are the maps
  accurate", "check the maps".
argument-hint: "[--no-update]"
---

# Review Maps

Keeps both `docs/al-dev-skills-map.md` and `docs/al-dev-agent-map.md` factually
current against the plugin surface. Does not emit design suggestions — all
findings come from `/plugin-health-audit`.

## Phase 0 — Choose sync mode

Skip this phase if `--no-update` was passed; proceed directly to Phase 1.

Otherwise, ask:

> How do you want to sync the maps?
>
> 1. In-session — run both map reviews now (~1–2 min, session stays active)
> 2. Async — dispatch `/sync-documentation-maps` and free this session
>    (collect results later with `/sync-documentation-maps-collect`)

If [1] → proceed to Phase 1.
If [2] → invoke `/sync-documentation-maps` and exit.

## Phase 1 — Review skill map

Run `/review-skill-map`, passing through any `--no-update` flag received.

## Phase 2 — Review agent map

Run `/review-agent-map`, passing through any `--no-update` flag received.

## Phase 3 — Handoff

Print:

> Maps reviewed. Run `/plugin-health-audit` to find improvements.
