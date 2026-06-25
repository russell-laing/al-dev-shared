# Static-Lens Carve-Out

> Canonical procedure for skipping the LLM `verify-health-finding` agent on
> findings that are **true by construction**. Cited by `report-input-gates.md`
> §1c (evidence-mode application) and `plan-plugin-findings/SKILL.md` Phase 3
> (rubber-duck-mode application). Both consumers apply this same procedure and
> add only their consumer-specific rule below.

## Which lenses are deterministic

Findings from these four lenses are produced by an exact rule match in
`scripts/health_static_lenses.py`, so their *claim* needs no LLM re-reading:

- `quality-agent-lens-structure`
- `quality-skill-lens-structure`
- `naming-convention-lens`
- `design-agent-lens-tool-hygiene`

## Identify a finding's source lens

Read the `<!-- lens: <name> -->` marker the assembler writes above each block in
the findings file. If a findings file has no markers (predates the assembler),
fall back to the block heading:

| Block heading | Source lens |
| --- | --- |
| `Structural Conventions` | `quality-agent-lens-structure` / `quality-skill-lens-structure` |
| `Naming Convention` | `naming-convention-lens` |
| `Tool Hygiene` | `design-agent-lens-tool-hygiene` |

## Re-verify deterministically (do not dispatch an agent)

Do **not** dispatch a `verify-health-finding` agent for a static-lens finding.
Re-run the static runner for the finding's surface and dimension, then check the
finding reappears:

```bash
python3 scripts/health_static_lenses.py \
  --surface <surface> --dimension <dimension> \
  --date <findings-date> --out-dir .dev
```

Read the regenerated `.dev/<findings-date>-plugin-health-lens-<lens>.json`. The
finding's `object` plus observation reappears → the claim still holds. It does
not reappear → the subject was already fixed; drop the finding as stale.

## Consumer-specific application

- **`/report-plugin-health` (evidence mode):** the carve-out replaces the
  evidence-mode `verify-health-finding` agent. A reappearing finding enters the
  dossier normally; a non-reappearing one is dropped under "Stale (dropped)".

- **`/plan-plugin-findings` (rubber-duck mode):** the rubber-duck agent normally
  does two things — confirm the claim **and** scope the fix
  (proceed/modify/skip). For a static-lens finding the deterministic re-run
  replaces the *claim confirmation*, and the fix is the lens's own canned
  remediation (the `fix` cell the static runner emitted — e.g. "split the mixed
  heading", "drop the empty `tools: []` array"). This is sound only because
  those fixes are mechanical. **Do not extend the carve-out to reasoning-class
  lenses** — Bloat, Prompt Clarity, Description Drift, Name Fit, and every design
  lens other than `design-agent-lens-tool-hygiene` still require a full
  rubber-duck, because their fix needs judgement the static runner cannot supply.
