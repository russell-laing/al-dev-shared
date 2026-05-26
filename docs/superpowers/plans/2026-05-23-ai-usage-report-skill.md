# AI Usage Report Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create a repository-local Codex skill that converts harness-specific usage artifacts into an AI-harness-neutral markdown report, with optional Codex-derived observations when local Codex session data is available.

**Architecture:** Add a repo-local skill under `.codex/skills/ai-usage-report/`. The skill orchestrates two paths: a report-normalization path for existing artifacts such as `~/.claude/usage-data/report.html`, and a Codex-summary path powered by a small Python helper that reads local Codex history/session data and emits a compact markdown fragment. The final report is always written to `.dev/` using the repository’s existing artifact convention.

**Tech Stack:** Markdown (`SKILL.md`), Python 3 standard library (`argparse`, `json`, `sqlite3`, `datetime`, `pathlib`), shell validation commands, git

---

## File Structure

- Create: `.codex/skills/ai-usage-report/SKILL.md` — repo-local Codex skill instructions and workflow
- Create: `.codex/skills/ai-usage-report/scripts/summarize_codex_usage.py` — deterministic Codex local-data summarizer used by the skill
- Create: `.codex/skills/ai-usage-report/tests/fixtures/codex-history-sample.jsonl` — minimal sample user-history fixture for script validation
- Create: `.codex/skills/ai-usage-report/tests/fixtures/codex-state-schema-notes.md` — lightweight fixture notes documenting expected SQLite inputs for manual validation
- Modify: `CODEX.md` — add a short section documenting the repo-local skill and its intended use

---

### Task 1: Create the Repo-Local Skill Skeleton

**Files:**
- Create: `.codex/skills/ai-usage-report/SKILL.md`
- Create: `.codex/skills/ai-usage-report/scripts/summarize_codex_usage.py`
- Create: `.codex/skills/ai-usage-report/tests/fixtures/codex-history-sample.jsonl`
- Create: `.codex/skills/ai-usage-report/tests/fixtures/codex-state-schema-notes.md`

- [ ] **Step 1: Verify the repo-local `.codex` skill path does not already exist**

  Run:
  ```bash
  find .codex/skills -maxdepth 2 -type f 2>/dev/null | grep "ai-usage-report" || echo "NOT FOUND"
  ```

  Expected: `NOT FOUND`

- [ ] **Step 2: Create the directory structure**

  Run:
  ```bash
  mkdir -p .codex/skills/ai-usage-report/scripts .codex/skills/ai-usage-report/tests/fixtures
  ```

  Expected: command exits `0` with no output

- [ ] **Step 3: Verify the directories were created**

  Run:
  ```bash
  find .codex/skills/ai-usage-report -maxdepth 3 -type d | sort
  ```

  Expected:
  ```text
  .codex/skills/ai-usage-report
  .codex/skills/ai-usage-report/scripts
  .codex/skills/ai-usage-report/tests
  .codex/skills/ai-usage-report/tests/fixtures
  ```

---

### Task 2: Write the Skill Instructions

**Files:**
- Create: `.codex/skills/ai-usage-report/SKILL.md`

- [ ] **Step 1: Write the skill file with complete frontmatter and workflow**

  Create `.codex/skills/ai-usage-report/SKILL.md` with this exact content:

  ```markdown
  ---
  name: ai-usage-report
  description: Convert harness-specific usage/session artifacts into an AI-harness-neutral markdown report, optionally augmenting the output with Codex-derived session observations from local Codex history/state data. Use when asked to review Claude Code Insights HTML, create a neutral cross-harness usage report, or include Codex-side usage observations in the same report.
  ---

  # AI Usage Report

  Create a neutral markdown report from one or more AI harness usage artifacts.

  ## When to Use

  Use this skill when the user asks to:

  - review a Claude Code Insights HTML report
  - convert a harness-specific usage report into neutral markdown
  - include Codex-derived observations in a report
  - write the final report into this repository’s `.dev/` artifact area

  ## Output Convention

  Write the final artifact to:

  - `.dev/YYYY-MM-DD-ai-harness-neutral-usage-report.md`

  If that filename already exists for the current day, append a short suffix that reflects the scope, for example:

  - `.dev/YYYY-MM-DD-ai-harness-neutral-usage-report-claude-only.md`
  - `.dev/YYYY-MM-DD-ai-harness-neutral-usage-report-cross-harness.md`

  ## Supported Inputs

  ### 1. Existing harness reports

  Examples:

  - `~/.claude/usage-data/report.html`
  - any similar local HTML or markdown usage summary supplied by the user

  For existing reports:

  1. Read the source artifact directly.
  2. Extract the core findings, metrics, strengths, friction points, and recommendations.
  3. Rewrite them in harness-neutral language.
  4. Keep product-specific terminology only when needed to identify a source artifact or tool capability.

  ### 2. Codex local session/history data

  When the user asks to include Codex-side observations, inspect local Codex artifacts if available:

  - `~/.codex/history.jsonl`
  - `~/.codex/state_5.sqlite`

  Use the helper script:

  ```bash
  python3 .codex/skills/ai-usage-report/scripts/summarize_codex_usage.py \
    --history ~/.codex/history.jsonl \
    --state ~/.codex/state_5.sqlite
  ```

  The script emits a markdown fragment that can be incorporated into the final report.

  ## Workflow

  ### Phase 1: Classify the request

  Determine which of these applies:

  - normalize an existing harness report only
  - normalize an existing harness report and add Codex observations
  - create a Codex-only usage summary

  State the chosen scope briefly in the response before doing substantial work.

  ### Phase 2: Read source artifacts

  For report files:

  - read the source artifact directly
  - extract:
    - reporting window
    - activity counts
    - dominant work patterns
    - strengths
    - friction/failure modes
    - recommendations
    - caveats or missing sections

  For Codex data:

  - run the helper script
  - review the emitted markdown fragment before using it
  - if the fragment is sparse or obviously misleading, say so and keep the Codex section minimal

  ### Phase 3: Write the neutral report

  The report should usually use this structure:

  1. `# AI Harness Neutral Usage Report`
  2. `## Source`
  3. `## Executive Summary`
  4. `## Activity Snapshot`
  5. `## Observed Working Style`
  6. `## What Is Working Well`
  7. `## Friction and Failure Modes`
  8. `## Neutral Recommendations`
  9. `## Codex Observations` (only when Codex data is included)
  10. `## Caveats`
  11. `## Bottom Line`

  Keep the final wording:

  - harness-neutral
  - direct
  - evidence-based
  - explicit about missing data or inference

  ## Guardrails

  - Do not describe the result as cross-harness unless Codex observations were actually included.
  - Do not imply Codex has a built-in Insights HTML artifact unless one was explicitly provided.
  - If the Codex data is limited to local history/session stores, state that clearly.
  - Preserve useful exact counts from the source artifact when available.
  - Do not silently drop notable caveats from the source artifact.

  ## Validation

  Before reporting success:

  1. Confirm the target markdown file exists in `.dev/`.
  2. Re-open the file and scan for:
     - placeholder text
     - harness-specific wording that should have been generalized
     - claims about Codex unsupported by the local data actually read
  3. If Codex observations were included, confirm the helper script ran successfully or explain why it could not.
  ```

- [ ] **Step 2: Verify the skill file exists and is non-empty**

  Run:
  ```bash
  wc -l .codex/skills/ai-usage-report/SKILL.md
  ```

  Expected: at least `100` lines

- [ ] **Step 3: Verify the skill metadata reads cleanly**

  Run:
  ```bash
  sed -n '1,20p' .codex/skills/ai-usage-report/SKILL.md
  ```

  Expected: frontmatter with `name: ai-usage-report` and a description that mentions both neutral report conversion and Codex observations

---

### Task 3: Implement the Codex Usage Summarizer Script

**Files:**
- Create: `.codex/skills/ai-usage-report/scripts/summarize_codex_usage.py`

- [ ] **Step 1: Write the script**

  Create `.codex/skills/ai-usage-report/scripts/summarize_codex_usage.py` with this exact content:

  ```python
  #!/usr/bin/env python3
  import argparse
  import json
  import sqlite3
  from collections import Counter
  from datetime import datetime, timezone
  from pathlib import Path


  def load_history(history_path: Path) -> tuple[int, int, str | None, str | None]:
      session_ids: set[str] = set()
      message_count = 0
      first_ts = None
      last_ts = None

      if not history_path.exists():
          return 0, 0, None, None

      with history_path.open("r", encoding="utf-8") as handle:
          for line in handle:
              line = line.strip()
              if not line:
                  continue
              record = json.loads(line)
              message_count += 1
              session_id = record.get("session_id")
              if session_id:
                  session_ids.add(session_id)
              ts = record.get("ts")
              if isinstance(ts, int):
                  if first_ts is None or ts < first_ts:
                      first_ts = ts
                  if last_ts is None or ts > last_ts:
                      last_ts = ts

      return len(session_ids), message_count, format_ts(first_ts), format_ts(last_ts)


  def load_thread_summary(state_path: Path) -> tuple[int, Counter, Counter]:
      if not state_path.exists():
          return 0, Counter(), Counter()

      connection = sqlite3.connect(state_path)
      try:
          rows = connection.execute(
              """
              SELECT source, model_provider, COALESCE(cwd, '')
              FROM threads
              WHERE archived = 0 OR archived IS NULL
              """
          ).fetchall()
      finally:
          connection.close()

      source_counts: Counter[str] = Counter()
      provider_counts: Counter[str] = Counter()
      cwd_counts: Counter[str] = Counter()

      for source, provider, cwd in rows:
          source_counts[source or "unknown"] += 1
          provider_counts[provider or "unknown"] += 1
          cwd_counts[cwd or "(none)"] += 1

      return len(rows), source_counts, provider_counts, cwd_counts


  def format_ts(ts: int | None) -> str | None:
      if ts is None:
          return None
      return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")


  def top_items(counter: Counter, limit: int = 3) -> list[str]:
      return [f"{name} ({count})" for name, count in counter.most_common(limit)]


  def render_markdown(
      history_sessions: int,
      history_messages: int,
      first_seen: str | None,
      last_seen: str | None,
      thread_count: int,
      source_counts: Counter,
      provider_counts: Counter,
      cwd_counts: Counter,
  ) -> str:
      lines: list[str] = []
      lines.append("## Codex Observations")
      lines.append("")
      lines.append("These observations are derived from local Codex history/state data rather than a built-in Codex Insights report.")
      lines.append("")
      lines.append("### Available Local Data")
      lines.append("")
      lines.append(f"- History sessions seen: `{history_sessions}`")
      lines.append(f"- History messages seen: `{history_messages}`")
      lines.append(f"- Active thread rows seen: `{thread_count}`")
      if first_seen:
          lines.append(f"- First history timestamp seen: `{first_seen}`")
      if last_seen:
          lines.append(f"- Last history timestamp seen: `{last_seen}`")
      lines.append("")
      lines.append("### Pattern Hints")
      lines.append("")
      if source_counts:
          lines.append(f"- Top thread sources: {', '.join(top_items(source_counts))}")
      if provider_counts:
          lines.append(f"- Top model providers: {', '.join(top_items(provider_counts))}")
      if cwd_counts:
          lines.append(f"- Top working directories: {', '.join(top_items(cwd_counts))}")
      if not source_counts and not provider_counts and not cwd_counts:
          lines.append("- Local state data was too sparse to identify stable usage patterns.")
      lines.append("")
      lines.append("### Interpretation Limits")
      lines.append("")
      lines.append("- This section is inferential and based only on locally readable Codex history/state artifacts.")
      lines.append("- It does not include a built-in Codex sentiment, friction, or recommendation engine.")
      return "\n".join(lines)


  def main() -> int:
      parser = argparse.ArgumentParser(description="Summarize local Codex usage artifacts as markdown.")
      parser.add_argument("--history", type=Path, required=True, help="Path to Codex history.jsonl")
      parser.add_argument("--state", type=Path, required=True, help="Path to Codex state_5.sqlite")
      args = parser.parse_args()

      history_sessions, history_messages, first_seen, last_seen = load_history(args.history)
      thread_count, source_counts, provider_counts, cwd_counts = load_thread_summary(args.state)

      print(
          render_markdown(
              history_sessions,
              history_messages,
              first_seen,
              last_seen,
              thread_count,
              source_counts,
              provider_counts,
              cwd_counts,
          )
      )
      return 0


  if __name__ == "__main__":
      raise SystemExit(main())
  ```

- [ ] **Step 2: Verify the script parses**

  Run:
  ```bash
  python3 -m py_compile .codex/skills/ai-usage-report/scripts/summarize_codex_usage.py
  ```

  Expected: no output

- [ ] **Step 3: Verify the help text is available**

  Run:
  ```bash
  python3 .codex/skills/ai-usage-report/scripts/summarize_codex_usage.py --help
  ```

  Expected: usage output mentioning `--history` and `--state`

---

### Task 4: Add Minimal Validation Fixtures

**Files:**
- Create: `.codex/skills/ai-usage-report/tests/fixtures/codex-history-sample.jsonl`
- Create: `.codex/skills/ai-usage-report/tests/fixtures/codex-state-schema-notes.md`

- [ ] **Step 1: Create the sample history fixture**

  Create `.codex/skills/ai-usage-report/tests/fixtures/codex-history-sample.jsonl` with this exact content:

  ```jsonl
  {"session_id":"session-001","ts":1778836097,"text":"review this usage report"}
  {"session_id":"session-001","ts":1778836401,"text":"include codex observations too"}
  {"session_id":"session-002","ts":1778840000,"text":"create a plan file for me to review first"}
  ```

- [ ] **Step 2: Create the state fixture notes**

  Create `.codex/skills/ai-usage-report/tests/fixtures/codex-state-schema-notes.md` with this exact content:

  ```markdown
  # Codex State Fixture Notes

  This skill does not commit a SQLite fixture because the local Codex `threads`
  schema may evolve. Manual validation should be run against the operator's real
  `~/.codex/state_5.sqlite` file after confirming the `threads` table contains at
  least these columns:

  - `source`
  - `model_provider`
  - `cwd`
  - `archived`

  If the schema changes in a future Codex release, update
  `scripts/summarize_codex_usage.py` and these notes together.
  ```

- [ ] **Step 3: Run fixture-based script validation using the real local state file**

  Run:
  ```bash
  python3 .codex/skills/ai-usage-report/scripts/summarize_codex_usage.py \
    --history .codex/skills/ai-usage-report/tests/fixtures/codex-history-sample.jsonl \
    --state /Users/russelllaing/.codex/state_5.sqlite
  ```

  Expected: markdown output beginning with `## Codex Observations`

- [ ] **Step 4: Verify the sample counts are reflected**

  Run:
  ```bash
  python3 .codex/skills/ai-usage-report/scripts/summarize_codex_usage.py \
    --history .codex/skills/ai-usage-report/tests/fixtures/codex-history-sample.jsonl \
    --state /Users/russelllaing/.codex/state_5.sqlite | grep "History sessions seen\\|History messages seen"
  ```

  Expected:
  ```text
  - History sessions seen: `2`
  - History messages seen: `3`
  ```

---

### Task 5: Document the Repo-Local Skill in CODEX.md

**Files:**
- Modify: `CODEX.md`

- [ ] **Step 1: Confirm the insertion anchor**

  Run:
  ```bash
  grep -n "Codex Registration and Plugin Loading" CODEX.md
  ```

  Expected: one matching line near the top of the file

- [ ] **Step 2: Add a short repo-local skill section**

  Use the Edit tool with this exact change:

  Old string:
  ```markdown
  `al-dev-shared` is registered as a Codex plugin and loaded into the active session environment. Codex consumes:
  ```

  New string:
  ```markdown
  `al-dev-shared` is registered as a Codex plugin and loaded into the active session environment. Codex consumes:
  ```

  Add this block immediately after the bullet list in that section:

  ```markdown
  ### Repo-Local Codex Skills

  This repository may also contain repo-local Codex skills under `.codex/skills/`.
  These are not part of the shared plugin surface and should be used only for
  repository-specific workflows that should not be projected into other harnesses.

  Current repo-local skill:

  - `.codex/skills/ai-usage-report/` — converts harness-specific usage artifacts
    into neutral markdown reports and can optionally add Codex-derived local
    usage observations.
  ```

- [ ] **Step 3: Verify the new section exists**

  Run:
  ```bash
  grep -n "Repo-Local Codex Skills" CODEX.md
  ```

  Expected: one matching line

---

### Task 6: End-to-End Manual Validation

**Files:**
- Test: `.codex/skills/ai-usage-report/SKILL.md`
- Test: `.codex/skills/ai-usage-report/scripts/summarize_codex_usage.py`
- Test: `.dev/YYYY-MM-DD-ai-harness-neutral-usage-report*.md`

- [ ] **Step 1: Run the Codex summarizer against real local inputs**

  Run:
  ```bash
  python3 .codex/skills/ai-usage-report/scripts/summarize_codex_usage.py \
    --history /Users/russelllaing/.codex/history.jsonl \
    --state /Users/russelllaing/.codex/state_5.sqlite | sed -n '1,40p'
  ```

  Expected: output starts with `## Codex Observations`

- [ ] **Step 2: Execute the skill manually on the known Claude report**

  Prompt to use in Codex:
  ```text
  Use the ai-usage-report skill. Convert /Users/russelllaing/.claude/usage-data/report.html into a harness-neutral markdown report in .dev/ and include Codex observations if local Codex history/state data is available.
  ```

  Expected: a markdown file is written under `.dev/` and explicitly distinguishes source-report findings from Codex-derived observations

- [ ] **Step 3: Verify the generated report persisted**

  Run:
  ```bash
  ls .dev/*ai-harness-neutral-usage-report*.md
  ```

  Expected: at least one matching file

- [ ] **Step 4: Review the generated report for required sections**

  Run:
  ```bash
  rg -n "^## (Source|Executive Summary|Neutral Recommendations|Codex Observations|Bottom Line)" .dev/*ai-harness-neutral-usage-report*.md
  ```

  Expected: all required sections present for the chosen scope

- [ ] **Step 5: Commit the repo-local skill**

  Run:
  ```bash
  git add .codex/skills/ai-usage-report CODEX.md
  git commit -m "feat(codex): add repo-local ai usage report skill"
  ```

  Run:
  ```bash
  git log --oneline -1
  ```

  Expected: latest commit message contains `feat(codex): add repo-local ai usage report skill`

---

## Self-Review

### Spec coverage

- Repo-local skill at base level rather than plugin surface → Task 2, Task 5 ✓
- Claude report normalization → Task 2, Task 6 ✓
- Codex inclusion when comparable local data exists → Task 3, Task 4, Task 6 ✓
- Output to `.dev/` using repository artifact conventions → Task 2, Task 6 ✓
- Reviewable implementation plan before coding → this document ✓

### Placeholder scan

No `TODO`, `TBD`, or deferred implementation placeholders are present. All file paths, commands, and code blocks are concrete.

### Type consistency

- Skill path is consistently `.codex/skills/ai-usage-report/`
- Helper script path is consistently `.codex/skills/ai-usage-report/scripts/summarize_codex_usage.py`
- Codex source files are consistently `~/.codex/history.jsonl` and `~/.codex/state_5.sqlite`
- Final report naming consistently uses `ai-harness-neutral-usage-report`

### Scope check

The plan stays intentionally narrow:

- one repo-local skill
- one helper script
- minimal fixture coverage
- one short `CODEX.md` documentation update

It does not attempt to build a generalized analytics framework, plugin projection, or multi-harness testing matrix.
