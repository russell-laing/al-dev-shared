---
name: review-maps
description: >-
  Combined in-session accuracy sync of both docs/al-dev-skills-map.md and
  docs/al-dev-agent-map.md. Shorthand for running /review-skill-map followed
  by /review-agent-map. Use after adding, removing, or restructuring skills
  or agents. Pass --no-update to audit both maps without modifying them.
  Triggers on: "review maps", "update maps", "sync maps", "are the maps
  accurate", "check the maps".
argument-hint: "[--no-update]"
---

# Review Maps

Runs both map-accuracy skills in sequence. Keeps both
`docs/al-dev-skills-map.md` and `docs/al-dev-agent-map.md` factually current
against the plugin surface. Does not emit design suggestions — all findings
come from `/plugin-health-audit`.

## Phase 1 — Review skill map

Run `/review-skill-map`, passing through any `--no-update` flag received.

## Phase 2 — Review agent map

Run `/review-agent-map`, passing through any `--no-update` flag received.

## Phase 3 — Handoff

Print:

> Maps reviewed. Run `/plugin-health-audit` to find improvements.
