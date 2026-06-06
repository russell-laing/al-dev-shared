# Compile Output — Critical Safeguard

When running `al-compile --output .dev/compile-errors.log`:

**DO:**

- Run the command without pipes: `al-compile --output .dev/compile-errors.log`
- Always include a short execution description in the command invocation
  (for example, "Compile AL project and write results to log file")
- Read `.dev/compile-errors.log` directly afterward when verification is
  required
- Use file-based `rg` if you need to filter results:
  `rg -n "pattern" .dev/compile-errors.log`
- Read the current compile result before claiming success, cleanliness, or
  readiness for the next workflow step

**DO NOT:**

- Pipe output to terminal viewers: `al-compile ... 2>&1 | head/tail/grep` ❌
- Omit the execution description when the command interface supports it
- Run `al-compile` without the `--output` flag (unless explicitly verifying stderr capture)

**Why:** Piping compile output causes the entire log (often multiple
megabytes) to be captured in session context, triggering context compacts
and session restarts. The `--output` flag already writes silently —
pipes serve no functional purpose and only cause harm.
