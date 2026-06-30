# Commit Compile Gate

Called from `commit-preflight` Phase 0.3 when staged changes include AL files.

Run this compile gate when staged changes include any `.al`, `app.json`, or `.al.json`
files. Skip the compile gate when **all** staged files match documentation or
config-only patterns: `.md`, `.txt`, `.rst`, `CHANGELOG*`, `LICENSE*`,
`.markdownlint.json`, `package.json`, `.gitignore`, `.editorconfig`, or other non-AL
`.json` configuration files (i.e., when `$AL_STAGED` is empty after the filter below).

```bash
AL_STAGED=$(git diff --cached --name-only --diff-filter=ACMRDT \
  | grep -E '(^|/)(app\.json|[^/]+\.al|[^/]+\.al\.json)$')
```

If `$AL_STAGED` is non-empty, run the compile gate before proceeding.

**Do not stash, reset, or otherwise modify the working tree to run a baseline
compile.** Compile only the current staged state. See the working-tree-safety
prohibition in `knowledge/compile-lint-procedure.md`.

1. Apply `knowledge/compile-lint-procedure.md`. Run `al-compile` with `--output`
   only — never piped to `tee`, `grep`, `head`, or `tail` (piping captures the
   entire multi-MB log into session context and forces a compact).
   (Piping prohibitions and output safeguards are summarised in
   `knowledge/compile-output-safeguard.md` for standalone reference.)
2. Produce a fresh `.dev/compile-errors.log` if the current log is absent or stale
3. Read the log and report:
   - `Errors:` count
   - `Warnings:` count
   - up to 3 representative diagnostics
   - `Detailed log:` `.dev/compile-errors.log`
4. If `Errors > 0`, determine whether any error originates in a staged file.
   Grep the error log for each staged path (or diff against
   `.dev/compile-baseline.log` if one was captured before this session's first
   edit):
   - **An error originates in a staged file** → stop the commit workflow and
     tell the user the staged changes are not ready to commit.
   - **All errors are pre-existing (none in the staged files)** → this is a
     known backlog. Ask the user: "The project has N pre-existing compile
     errors, none in the staged files. This is a known backlog. Proceed with
     commit despite pre-existing errors? (yes / no)". On `yes`, hold
     `pre_existing_errors_acknowledged: true` to record in the persisted
     `LINT_CONTEXT` block (Phase 2 Completion) and continue. On `no`, stop.
5. Only continue when the compile result shows zero errors **or** the user has
   acknowledged a pre-existing-error backlog per step 4

If `$AL_STAGED` is empty, no AL files are staged — skip the compile gate and
continue to 0.4.

## Cost Awareness (Future Enhancement)

Currently, steps 1–2 above invoke a full-project `al-compile` regardless of how many AL files changed.
When a single-file diff touches ≤20 lines, a full-project compile may be overkill.

**Future:** If al-compile supports scoped or incremental modes (e.g., `al-compile --only-staged-files`),
update step 1 to conditionally use scoped compilation for diffs ≤20 lines and defer to full-project
compile for larger changes or multi-file diffs.

For now: If you need faster feedback on a single-file AL fix, run `al-compile --file <path>` manually
before committing to verify the error count locally.
