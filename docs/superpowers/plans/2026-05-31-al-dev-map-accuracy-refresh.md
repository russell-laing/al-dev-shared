# AL Dev Map Accuracy Refresh Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Bring `docs/al-dev-skills-map.md`, `docs/al-dev-agent-map.md`, and `docs/al-dev-plugin-graph.md` back into technical alignment with the current `profile-al-dev-shared` source after today's agent and skill changes.

**Architecture:** Treat source files under `profile-al-dev-shared/skills/`, `profile-al-dev-shared/agents/`, and `profile-al-dev-shared/knowledge/` as authoritative. Fix the graph generator first so generated claims are mechanically safer, then refresh the two manual maps from the same source evidence. Keep maintainer-only observations separate from distributed plugin inventory claims.

**Tech Stack:** Python 3 standard library, markdown, Mermaid, existing repo scripts under `scripts/`, existing projection validation tests under `scripts/tests/`.

---

## Rubber-Duck Assessment

The current maps contain several technically inaccurate or stale claims:

- `docs/al-dev-agent-map.md` claims **21 agents**, but `profile-al-dev-shared/agents/*.md` currently contains **22 agent files** because `al-dev-developer` has been split into `al-dev-developer-tdd` and `al-dev-developer-traditional`.
- `docs/al-dev-agent-map.md` still documents a single `al-dev-developer` agent and caller list. That agent file no longer exists; current callers route to `al-dev-developer-tdd` or `al-dev-developer-traditional`.
- `docs/al-dev-skills-map.md` still shows `/al-dev-fix` and `/al-dev-develop` spawning `al-dev-developer`. Current skill source spawns `al-dev-developer-traditional` for trivial/error-correction paths and routes between `al-dev-developer-tdd` and `al-dev-developer-traditional` based on test-plan presence.
- `docs/al-dev-plugin-graph.md` includes `al-dev-developer` as an agent node, which is stale. The generated projections already contain `al-dev-developer-tdd` and `al-dev-developer-traditional`.
- `scripts/generate-plugin-graph.py` uses the same Mermaid node id for same-named skills and agents, for example `al_dev_explore` and `al_dev_interview`. Mermaid merges duplicate IDs, so the rendered graph cannot distinguish skill nodes from agent nodes with identical names.
- `scripts/generate-plugin-graph.py` only detects agent references matching `al-dev-shared:(al-dev-[a-z0-9-]+)`. It misses current real dispatch references that are unqualified in prose, such as `Spawn \`al-dev-diagnostics-fixer\`` in `/al-dev-lint`, and therefore produces false orphan-agent health callouts.
- `docs/al-dev-agent-map.md` model claims are stale for at least `al-dev-code-review` and `al-dev-diagnostics-fixer`: current frontmatter says both are `sonnet`, while the map says `haiku`.
- `profile-al-dev-shared/agents/al-dev-diagnostics-fixer.md` still says it is dispatched by both `al-dev-lint` and `al-dev-fix`; current skill source only has a direct diagnostics-fixer spawn in `/al-dev-lint`. This is source drift, not just map drift.
- `docs/al-dev-skills-map.md` says `/al-dev-diagram-generator` is maintainer-only and not counted as a distributed skill, but it lives under `profile-al-dev-shared/skills/` and the plugin manifest exposes `skills/` wholesale. Unless packaging excludes it elsewhere, count it as part of the profile surface and label it "maintenance-oriented" rather than "not distributed".
- `docs/al-dev-plugin-graph.md` is marked generated and "Do not hand-edit", so corrections should be made through `scripts/generate-plugin-graph.py` and then regenerated.

## File Structure

| Path | Responsibility |
|---|---|
| `scripts/generate-plugin-graph.py` | Generate dependency graph, workflow overlays, and health callouts from current source. Must use typed Mermaid node ids and broader dispatch extraction. |
| `scripts/tests/test_generate_plugin_graph.py` | Fixture tests for graph extraction, node ids, and rendered output safety. |
| `docs/al-dev-plugin-graph.md` | Generated graph output. Regenerate only after generator tests pass. |
| `docs/al-dev-agent-map.md` | Manual agent catalog and profile notes. Refresh counts, model/tool claims, caller claims, and developer split sections. |
| `docs/al-dev-skills-map.md` | Manual skill lifecycle and drill-down diagrams. Refresh developer dispatch labels, skill counts, maintainer/distributed wording, and observations. |
| `profile-al-dev-shared/agents/al-dev-diagnostics-fixer.md` | Source frontmatter/body description. Align caller statement with actual direct skill dispatches. |
| `profile-al-dev-shared/generated/agents/` | Generated projections. Regenerate after agent source wording changes. |

---

### Task 1: Add Failing Graph-Generator Coverage

**Files:**
- Modify: `scripts/tests/test_generate_plugin_graph.py`

- [ ] **Step 1: Add tests for typed node ids and unqualified agent references**

Add these tests below `test_node_id_sanitizes_hyphens()`:

```python
def test_node_id_supports_typed_prefixes() -> None:
    assert _mod.node_id("skill", "al-dev-explore") == "skill_al_dev_explore"
    assert _mod.node_id("agent", "al-dev-explore") == "agent_al_dev_explore"
    assert _mod.node_id("knowledge", "workflow-routing.md") == "knowledge_workflow_routing_md"


def test_extract_edges_finds_namespaced_and_unqualified_agent_refs() -> None:
    with tempfile.TemporaryDirectory() as td:
        plugin = Path(td) / "profile-al-dev-shared"
        (plugin / "skills" / "al-dev-lint").mkdir(parents=True)
        (plugin / "agents").mkdir(parents=True)
        (plugin / "knowledge").mkdir(parents=True)
        (plugin / "skills" / "al-dev-lint" / "SKILL.md").write_text(
            "Spawn `al-dev-diagnostics-fixer`.\n"
            "Agent: al-dev-shared:al-dev-developer-traditional\n",
            encoding="utf-8",
        )
        (plugin / "agents" / "al-dev-diagnostics-fixer.md").write_text("fixer\n", encoding="utf-8")
        (plugin / "agents" / "al-dev-developer-traditional.md").write_text("dev\n", encoding="utf-8")

        skills, _, _ = _mod.discover(plugin)
        edges = _mod.extract_edges(plugin, skills)

        assert ("al-dev-lint", "al-dev-diagnostics-fixer") in edges["skill_agent"]
        assert ("al-dev-lint", "al-dev-developer-traditional") in edges["skill_agent"]


def test_render_dependency_graph_does_not_merge_same_named_skill_and_agent() -> None:
    rendered = _mod.render_dependency_graph(
        skills=["al-dev-explore"],
        agents=["al-dev-explore"],
        edges={
            "skill_agent": {("al-dev-explore", "al-dev-explore")},
            "skill_skill": set(),
            "skill_knowledge": set(),
            "agent_knowledge": set(),
            "skill_artifact": set(),
        },
    )

    assert "skill_al_dev_explore[al-dev-explore]" in rendered
    assert "agent_al_dev_explore[al-dev-explore]" in rendered
    assert "skill_al_dev_explore --> agent_al_dev_explore" in rendered
```

- [ ] **Step 2: Run the targeted tests and verify failure**

Run:

```bash
python3 scripts/tests/test_generate_plugin_graph.py
```

Expected: FAIL before implementation. Representative failures should mention `node_id()` argument mismatch or missing `al-dev-diagnostics-fixer` edge.

- [ ] **Step 3: Commit test coverage**

```bash
git add scripts/tests/test_generate_plugin_graph.py
git commit -m "test(graph): cover typed nodes and direct agent refs"
```

---

### Task 2: Fix `generate-plugin-graph.py`

**Files:**
- Modify: `scripts/generate-plugin-graph.py`
- Modify: `scripts/tests/test_generate_plugin_graph.py`

- [ ] **Step 1: Replace `node_id` with a typed helper**

Change the function signature and body:

```python
def node_id(kind: str, name: str) -> str:
    """Mermaid-safe node id with type prefix to avoid skill/agent collisions."""
    normalized = re.sub(r"[^A-Za-z0-9_]", "_", name)
    return f"{kind}_{normalized}"
```

- [ ] **Step 2: Update existing test expectation**

Change:

```python
def test_node_id_sanitizes_hyphens() -> None:
    assert _mod.node_id("al-dev-worker") == "al_dev_worker"
```

to:

```python
def test_node_id_sanitizes_hyphens() -> None:
    assert _mod.node_id("agent", "al-dev-worker") == "agent_al_dev_worker"
```

- [ ] **Step 3: Add agent-reference extraction helper**

Add this helper near the regex constants:

```python
def extract_agent_refs(text: str, known_agents: set[str]) -> set[str]:
    """Find namespaced and explicit unqualified agent references in skill text."""
    refs = set(AGENT_REF.findall(text))
    for agent in known_agents:
        if re.search(rf"(?<![A-Za-z0-9_-]){re.escape(agent)}(?![A-Za-z0-9_-])", text):
            refs.add(agent)
    return refs
```

- [ ] **Step 4: Pass known agents into `extract_edges`**

Change:

```python
def extract_edges(plugin_dir: Path, skills: list[str]) -> dict[str, set[tuple[str, str]]]:
```

to:

```python
def extract_edges(
    plugin_dir: Path,
    skills: list[str],
    agents: list[str] | None = None,
) -> dict[str, set[tuple[str, str]]]:
```

Then add:

```python
    known_agents = set(agents or [p.stem for p in (plugin_dir / "agents").glob("*.md")])
```

before the skill loop.

- [ ] **Step 5: Use the helper in the skill loop**

Replace:

```python
        for dst in AGENT_REF.findall(text):
            edges["skill_agent"].add((src, dst))
```

with:

```python
        for dst in extract_agent_refs(text, known_agents):
            edges["skill_agent"].add((src, dst))
```

- [ ] **Step 6: Update all renderer node id calls**

In `render_dependency_graph`, use:

```python
node_id("skill", s)
node_id("agent", a)
node_id("knowledge", k)
```

Use typed source/target ids for edge rendering:

```python
    for src, dst in sorted(edges["skill_skill"]):
        lines.append(f"    {node_id('skill', src)} --> {node_id('skill', dst)}")
    for src, dst in sorted(edges["skill_agent"]):
        lines.append(f"    {node_id('skill', src)} --> {node_id('agent', dst)}")
    for src, dst in sorted(edges["skill_knowledge"]):
        if dst in referenced_knowledge:
            lines.append(f"    {node_id('skill', src)} --> {node_id('knowledge', dst)}")
    for src, dst in sorted(edges["agent_knowledge"]):
        if dst in referenced_knowledge:
            lines.append(f"    {node_id('agent', src)} --> {node_id('knowledge', dst)}")
```

- [ ] **Step 7: Update workflow overlay node ids**

In `render_workflow_overlays`, use skill node ids:

```python
lines.append(
    f"    {node_id('skill', path[i])}[{path[i]}] --> "
    f"{node_id('skill', path[i + 1])}[{path[i + 1]}]"
)
```

For single-node overlays:

```python
lines.append(f"    {node_id('skill', path[0])}[{path[0]}]")
```

- [ ] **Step 8: Pass agents into `extract_edges` in `main`**

Change:

```python
edges = extract_edges(PLUGIN, skills)
```

to:

```python
edges = extract_edges(PLUGIN, skills, agents)
```

- [ ] **Step 9: Run graph tests**

Run:

```bash
python3 scripts/tests/test_generate_plugin_graph.py
```

Expected: all tests pass.

- [ ] **Step 10: Commit generator fix**

```bash
git add scripts/generate-plugin-graph.py scripts/tests/test_generate_plugin_graph.py
git commit -m "fix(graph): distinguish node types and direct agent refs"
```

---

### Task 3: Align Source Agent Caller Claim

**Files:**
- Modify: `profile-al-dev-shared/agents/al-dev-diagnostics-fixer.md`
- Modify: `profile-al-dev-shared/generated/agents/claude/al-dev-diagnostics-fixer.md`
- Modify: `profile-al-dev-shared/generated/agents/copilot/al-dev-diagnostics-fixer.md`
- Modify: `profile-al-dev-shared/generated/agents/codex/al-dev-diagnostics-fixer.toml`

- [ ] **Step 1: Update diagnostics-fixer description**

In `profile-al-dev-shared/agents/al-dev-diagnostics-fixer.md`, change:

```yaml
  Dispatched by al-dev-lint and al-dev-fix skills.
```

to:

```yaml
  Dispatched directly by the al-dev-lint skill.
```

- [ ] **Step 2: Regenerate projections**

Run:

```bash
python3 scripts/generate-agent-projections.py
```

Expected: generated diagnostics-fixer projection descriptions no longer mention `al-dev-fix`.

- [ ] **Step 3: Validate projections**

Run:

```bash
python3 scripts/tests/test_generate_agent_projections.py
python3 scripts/validate-lens-agents.py --path profile-al-dev-shared/agents
python3 scripts/validate_harness_neutrality.py profile-al-dev-shared
```

Expected: all commands pass.

- [ ] **Step 4: Commit source claim alignment**

```bash
git add profile-al-dev-shared/agents/al-dev-diagnostics-fixer.md profile-al-dev-shared/generated/agents
git commit -m "docs(agent): align diagnostics fixer caller claim"
```

---

### Task 4: Regenerate Plugin Graph

**Files:**
- Modify: `docs/al-dev-plugin-graph.md`

- [ ] **Step 1: Run generator**

Run:

```bash
python3 scripts/generate-plugin-graph.py
```

Expected: `docs/al-dev-plugin-graph.md` is rewritten.

- [ ] **Step 2: Verify graph content**

Run:

```bash
rg -n "al-dev-developer|al-dev-developer-tdd|al-dev-developer-traditional|skill_al_dev_explore|agent_al_dev_explore|Orphan agents" docs/al-dev-plugin-graph.md
```

Expected:

```text
al-dev-developer-tdd
al-dev-developer-traditional
skill_al_dev_explore
agent_al_dev_explore
```

Expected absence: no standalone `al-dev-developer` agent node.

- [ ] **Step 3: Review health callouts**

Run:

```bash
sed -n '/## Health callouts/,$p' docs/al-dev-plugin-graph.md
```

Expected: `al-dev-diagnostics-fixer` should not be listed as an orphan if `/al-dev-lint` is correctly detected. Any remaining orphan claims must be manually checked before they are accepted as health findings.

- [ ] **Step 4: Commit generated graph**

```bash
git add docs/al-dev-plugin-graph.md
git commit -m "docs(graph): regenerate plugin dependency graph"
```

---

### Task 5: Refresh Agent Map

**Files:**
- Modify: `docs/al-dev-agent-map.md`

- [ ] **Step 1: Generate current inventory evidence**

Run:

```bash
find profile-al-dev-shared/agents -maxdepth 1 -name '*.md' | sort
```

Expected: 22 files, including:

```text
profile-al-dev-shared/agents/al-dev-developer-tdd.md
profile-al-dev-shared/agents/al-dev-developer-traditional.md
```

- [ ] **Step 2: Extract current models and tools**

Run:

```bash
for f in profile-al-dev-shared/agents/*.md; do
  printf '%s\n' "--- $f"
  sed -n '1,12p' "$f"
done
```

Use this output as the source of truth for the Layer 1 catalog.

- [ ] **Step 3: Update the document header**

Replace the first status line with:

```markdown
**Last updated:** 2026-05-31 (22 agents; `al-dev-developer` split into `al-dev-developer-tdd` and `al-dev-developer-traditional`; plugin graph generator corrected to use typed Mermaid node ids and broader direct-agent reference extraction)
```

- [ ] **Step 4: Replace `al-dev-developer` catalog row**

Remove:

```markdown
| al-dev-developer | sonnet | Read, Write, Edit, Glob, Grep, Bash | /al-dev-develop, /al-dev-fix, /al-dev-review-develop (autonomous mode) |
```

Add:

```markdown
| al-dev-developer-tdd | sonnet | Read, Write, Edit, Glob, Grep, Bash | /al-dev-develop and /al-dev-fix when `.dev/*-al-dev-test-test-plan.md` exists |
| al-dev-developer-traditional | sonnet | Read, Write, Edit, Glob, Grep, Bash | /al-dev-develop and /al-dev-fix when no test plan exists; /al-dev-review-develop autonomous compile-error correction |
```

- [ ] **Step 5: Correct stale model rows**

Ensure these rows match current frontmatter:

```markdown
| al-dev-code-review | sonnet | Read | (none found) |
| al-dev-diagnostics-fixer | sonnet | Read, Edit, Glob, Grep, Bash | /al-dev-lint |
```

- [ ] **Step 6: Replace the `### al-dev-developer` profile with two profiles**

Delete the old `### al-dev-developer` section and add:

```markdown
### al-dev-developer-tdd

**Description:** Implement AL code using test-driven development with RED-GREEN-REFACTOR cycle gates.
**Model:** sonnet
**Tools:** Read, Write, Edit, Glob, Grep, Bash
**Spawned by:** /al-dev-develop and /al-dev-fix when `.dev/*-al-dev-test-test-plan.md` exists

**Inputs:**

| Input | Required | Description |
|-------|----------|-------------|
| `.dev/*-al-dev-plan-solution-plan.md` or confirmed fix scope | **Yes** | Implementation scope |
| `.dev/*-al-dev-test-test-plan.md` | **Yes** | Test behaviours driving RED-GREEN-REFACTOR cycles |
| `.dev/project-context.md` | No | Project memory |

**Outputs:**

| Output | Description |
|--------|-------------|
| AL source files | Implemented code |
| Test codeunits | Test implementation |
| `.dev/$(date +%Y-%m-%d)-al-dev-developer-tdd-log.md` | TDD cycle log |
| `.dev/session-log.md` | Session entry |

### al-dev-developer-traditional

**Description:** Implement AL code using a build-verify workflow when no test plan exists, and perform minimal compile-error correction in review autonomous mode.
**Model:** sonnet
**Tools:** Read, Write, Edit, Glob, Grep, Bash
**Spawned by:** /al-dev-develop, /al-dev-fix, /al-dev-review-develop (autonomous mode)

**Inputs:**

| Input | Required | Description |
|-------|----------|-------------|
| `.dev/*-al-dev-plan-solution-plan.md` or confirmed fix scope | **Yes** | Implementation scope |
| `.dev/compile-errors.log` | **Yes** for review autonomous mode | Compile errors to correct |
| `.dev/project-context.md` | No | Project memory |

**Outputs:**

| Output | Description |
|--------|-------------|
| AL source files | Implemented or corrected code |
| `.dev/session-log.md` | Session entry |
| Return summary | Files changed, verification, blockers |
```

- [ ] **Step 7: Update observations**

Replace references to `al-dev-developer` in "Potential shared agents" with:

```markdown
- **al-dev-developer-tdd** — used by /al-dev-develop and /al-dev-fix when a test plan exists
- **al-dev-developer-traditional** — used by /al-dev-develop and /al-dev-fix when no test plan exists; used by /al-dev-review-develop for autonomous compile-error correction
```

Remove or rewrite any "Confirmed implemented: Align al-dev-developer TDD activation" text so it describes the current split, not the removed unified agent.

- [ ] **Step 8: Validate no stale standalone developer claims remain**

Run:

```bash
rg -n "al-dev-developer(\\W|$)" docs/al-dev-agent-map.md
```

Expected: matches only historical notes that explicitly say the old unified agent was split, or no matches. There must be no active catalog/profile row for `al-dev-developer`.

- [ ] **Step 9: Commit agent map refresh**

```bash
git add docs/al-dev-agent-map.md
git commit -m "docs(agent-map): refresh current agent inventory"
```

---

### Task 6: Refresh Skills Map

**Files:**
- Modify: `docs/al-dev-skills-map.md`

- [ ] **Step 1: Update skill count and scope wording**

Replace the "Last updated" line with:

```markdown
**Last updated:** 2026-05-31 (21 profile skills on disk: 20 workflow/support skills plus maintenance-oriented `/al-dev-diagram-generator`; `/al-dev-support` remains a deprecated alias for `/al-dev-ticket --mode=full`)
```

Replace any claim that `/al-dev-diagram-generator` is "not distributed" with:

```markdown
`/al-dev-diagram-generator` is maintenance-oriented and called from repo-local analysis workflows, but it currently lives under the profile `skills/` directory and is part of the plugin skill surface unless packaging adds an explicit exclusion.
```

- [ ] **Step 2: Update notation example**

Change:

```markdown
Agents are referenced by their full type name (e.g., `al-dev-shared:al-dev-developer`).
```

to:

```markdown
Agents are referenced by their full type name (e.g., `al-dev-shared:al-dev-developer-traditional`).
```

- [ ] **Step 3: Update `/al-dev-fix` diagram labels**

Replace both `al-dev-developer ×1` labels in the `/al-dev-fix` drill-down with:

```mermaid
DevAgent["al-dev-developer-traditional ×1"]
```

for the trivial path, and:

```mermaid
DevAgent2["al-dev-developer-tdd<br/>or traditional ×1"]
```

for the non-trivial path.

- [ ] **Step 4: Update `/al-dev-develop` diagram labels**

Replace:

```mermaid
DevAgent["al-dev-developer ×1-4<br/>(scaled by object count)"]
```

with:

```mermaid
DevAgent["al-dev-developer-tdd<br/>or traditional ×1-4<br/>(scaled by module count)"]
```

- [ ] **Step 5: Update `/al-dev-review-develop` diagram**

In the compile-error branch description, add that autonomous compile-error correction uses `al-dev-developer-traditional`. If there is no explicit branch in the diagram, add a note below the diagram:

```markdown
In `--autonomous` mode, compile-error correction before the review panel dispatches `al-dev-developer-traditional`; TDD is not used for compile-error repair.
```

- [ ] **Step 6: Update shared-agent observations**

Replace:

```markdown
- **al-dev-developer** — spawned by /al-dev-fix, /al-dev-develop; patterns in `knowledge/architect-invocation-patterns.md` ← implemented
```

with:

```markdown
- **Developer agents** — `/al-dev-develop` and `/al-dev-fix` route to `al-dev-developer-tdd` when a test plan exists and `al-dev-developer-traditional` otherwise; `/al-dev-review-develop --autonomous` uses `al-dev-developer-traditional` for compile-error correction. Dispatch patterns live in `knowledge/developer-invocation-patterns.md`.
```

- [ ] **Step 7: Validate no stale active developer labels remain**

Run:

```bash
rg -n "al-dev-developer(\\W|$)" docs/al-dev-skills-map.md
```

Expected: no active diagram or current-state observation uses bare `al-dev-developer`.

- [ ] **Step 8: Commit skills map refresh**

```bash
git add docs/al-dev-skills-map.md
git commit -m "docs(skill-map): refresh developer split and skill scope"
```

---

### Task 7: Final Validation

**Files:**
- Validate only; no planned edits unless validation fails.

- [ ] **Step 1: Run map and projection validation**

Run:

```bash
python3 scripts/tests/test_generate_plugin_graph.py
python3 scripts/tests/test_generate_agent_projections.py
python3 scripts/validate_harness_neutrality.py profile-al-dev-shared
python3 scripts/validate-lens-agents.py --path profile-al-dev-shared/agents
```

Expected: all commands pass.

- [ ] **Step 2: Run drift checks for stale removed agent**

Run:

```bash
rg -n "al-dev-shared:al-dev-developer(\\W|$)|\\bal-dev-developer\\b" docs/al-dev-skills-map.md docs/al-dev-agent-map.md docs/al-dev-plugin-graph.md profile-al-dev-shared/skills profile-al-dev-shared/agents scripts/tests
```

Expected: no active source or map reference to a bare `al-dev-developer` agent. Historical plans or health reports outside this command scope may still mention it.

- [ ] **Step 3: Check working tree scope**

Run:

```bash
git status --short
```

Expected changed paths for this implementation only:

```text
M scripts/generate-plugin-graph.py
M scripts/tests/test_generate_plugin_graph.py
M profile-al-dev-shared/agents/al-dev-diagnostics-fixer.md
M profile-al-dev-shared/generated/agents/claude/al-dev-diagnostics-fixer.md
M profile-al-dev-shared/generated/agents/copilot/al-dev-diagnostics-fixer.md
M profile-al-dev-shared/generated/agents/codex/al-dev-diagnostics-fixer.toml
M docs/al-dev-plugin-graph.md
M docs/al-dev-agent-map.md
M docs/al-dev-skills-map.md
```

If unrelated pre-existing modified or untracked files remain, leave them untouched and call them out in the final summary.

- [ ] **Step 4: Commit final validation if needed**

If any validation-only cleanup was required:

```bash
git add <validated-files>
git commit -m "chore(map): finalize map accuracy validation"
```

If no cleanup was required, do not create an empty commit.

---

## Self-Review

**Spec coverage:** The plan covers all three requested docs and assesses the claims made in them against current source evidence. It also covers the generator because `docs/al-dev-plugin-graph.md` is generated and should not be hand-edited.

**Placeholder scan:** No planned step depends on "TBD", "TODO", or unspecified testing. Commands and expected outcomes are stated.

**Type consistency:** The plan consistently uses `al-dev-developer-tdd` and `al-dev-developer-traditional` for current developer agents and reserves bare `al-dev-developer` only for stale/historical drift checks.

