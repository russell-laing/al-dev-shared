# Scripts Review Watch List

Recurring `scripts/` bug classes distilled from git history. A `review-scripts`
run MUST check every new/changed file against this list. Each entry cites the
commit that established the pattern.

## 1. Ledger fork from stale or relative paths

- **Symptom:** disposition store/history diverges into two ledgers.
- **Check:** every `docs/health/` path is built from a `REPO_ROOT`-anchored
  helper in `al_dev_tools/health/paths.py`, uses **underscore** directory names
  (`dispositions_events`, `dispositions_history`), and no CLI default resolves a
  path relative to the current working directory.
- **Provenance:** `74cd5cd6`, `bc12f4cb`.

## 2. Non-atomic / non-idempotent writes

- **Symptom:** a re-run duplicates rows, or a crash mid-write truncates a file.
- **Check:** view/index writes go through `write_text_atomic`/`write_json_atomic`;
  any append path (`sync_shard`, migrations) dedups against existing content so a
  re-run is a no-op.
- **Provenance:** `33b29185`, `ebf98227`.

## 3. Disposition/findings parse fragility

- **Symptom:** findings silently dropped or miscounted; casing mismatch.
- **Check:** parsers tolerate both bullet and table formats, normalize casing on
  read AND write, split JSONL on `"\n"` (not `splitlines()`), and warn when the
  parsed count is below the candidate-line count.
- **Provenance:** `f0050742`, `094502c1`, `d78d2769`, `3ad6f37f`, `9be8139c`.

## 4. Fail-open validators

- **Symptom:** a validator prints PASS / exits 0 when its target is empty,
  missing, or relocated.
- **Check:** a validator asserts its scanned tree EXISTS and is non-empty before
  reporting clean; a swallowed subprocess/`git` error is a hard failure, not an
  empty result; regexes are proven to match at least one intended input.
- **Provenance:** `21d4480b`, `982830c2`, `563777d5`, `8b64684d`.

## 5. Stale skill/agent name references in generators

- **Symptom:** generated docs/diagrams reference a renamed or archived skill.
- **Check:** every skill/agent name a generator emits resolves to a live
  directory under `profile-al-dev-shared/skills|agents/` or `.claude/skills/`;
  rename maps are remapped (not deleted) so fallbacks don't resurrect old names.
- **Provenance:** `7f549fe9`, `84c58f82`, `6ae773da`, `4deeb0f4`.

## 6. Closure / dedup logic

- **Symptom:** a decline closes the wrong finding, or a dangling reference bricks
  materialization.
- **Check:** ambiguous closes leave candidates open and warn; `closes_event_ids`
  targets are validated at append time; membership/dedup uses the intended key.
- **Provenance:** `a5dc30b7`, `a0d000a9`, `42ad4dd7`.

## 7. Duplication / copied-contract drift

- **Symptom:** the same helper is re-implemented in two modules, or a script
  embeds command/contract text whose canonical source is a knowledge file — so
  the two copies drift apart silently.
- **Check:** a helper used by 2+ modules lives in one shared location, not
  copy-pasted (e.g. `_mermaid_block`, `_wrap`, `_read_text`, node-id builders);
  a script's help/command/error text that restates a canonical contract points
  at that contract rather than duplicating it. Cross-check with the repo's
  duplicate-text scanner
  (`.codex/skills/generate-duplicate-text-report/scripts/generate_duplicate_text_report.py`),
  whose findings are triaged in `docs/reviews/2026-07-02-duplicate-text-*.md`.
- **Provenance:** duplicate-text review pipeline; round-2 Tier 2 items 11–12.
