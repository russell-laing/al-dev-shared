# Skill scaffold template

To add a new shared skill:

1. Copy this directory to `profile-al-dev-shared/skills/<your-skill-name>/`.
2. Rename `SKILL.md.tmpl` → `SKILL.md` and `tests/scenarios.yaml.tmpl` → `tests/scenarios.yaml`.
3. Replace every `{{placeholder}}` value.
4. Add a row for the new skill to `profile-al-dev-shared/knowledge/artifact-contracts.md`
   with the declared inputs, outputs, resume read-order, handoff artefact, and success
   evidence.
5. If user-invocable, register the skill in `.claude-plugin/marketplace.json`.
6. Run the validators:

   ```bash
   python3 scripts/validate_artifact_contracts.py
   python3 scripts/validate-lens-agents.py --path profile-al-dev-shared/agents
   python3 scripts/validate-knowledge-quality.py --path profile-al-dev-shared/knowledge
   ```

7. If the new skill spawns or relies on a new agent, see `profile-al-dev-shared/agents/`
   and regenerate projections:

   ```bash
   python3 scripts/generate-agent-projections.py
   ```
