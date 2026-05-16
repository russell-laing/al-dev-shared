# Archived Skills and Agents

Files here are inactive — not loaded by the plugin. Move them back to
`skills/` or `agents/` to reinstate.

## What is here

| Item | Type | Archived reason |
|------|------|-----------------|
| `skills/al-dev-test/` | Skill | Test codeunit workflow not yet in use |
| `agents/al-dev-unit-test-engineer.md` | Agent | Spawned by al-dev-test |
| `agents/al-dev-integration-test-engineer.md` | Agent | Spawned by al-dev-test |
| `agents/al-dev-scenario-test-engineer.md` | Agent | Spawned by al-dev-test |
| `agents/al-dev-edge-case-test-engineer.md` | Agent | Spawned by al-dev-test |
| `agents/al-dev-test-coverage-reviewer.md` | Agent | Spawned by al-dev-develop/al-dev-autonomous |

## Reinstatement steps

1. `git mv archived/skills/al-dev-test skills/al-dev-test`
2. `git mv archived/agents/al-dev-unit-test-engineer.md agents/`
3. `git mv archived/agents/al-dev-integration-test-engineer.md agents/`
4. `git mv archived/agents/al-dev-scenario-test-engineer.md agents/`
5. `git mv archived/agents/al-dev-edge-case-test-engineer.md agents/`
6. `git mv archived/agents/al-dev-test-coverage-reviewer.md agents/`
7. Revert all edits described in the spec:
   `docs/superpowers/specs/2026-05-16-archive-test-skills-design.md`
