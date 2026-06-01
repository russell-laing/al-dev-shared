# Compile Output — Critical Safeguard

When running `al-compile --output .dev/compile-errors.log`:

**DO:**

- Run the command without pipes: `al-compile --output .dev/compile-errors.log`
- Always include a `description` parameter on the Bash tool call (e.g., "Compile AL project and write results to log file")
- Use the Read tool to inspect the log file afterward if needed
- Use file-based grep if you need to filter results: `grep -E "pattern" .dev/compile-errors.log`

**DO NOT:**

- Pipe output to terminal viewers: `al-compile ... 2>&1 | head/tail/grep` ❌
- Omit the `description` parameter on Bash calls
- Run `al-compile` without the `--output` flag (unless explicitly verifying stderr capture)

**Why:** Piping compile output causes the entire log (4.7MB+) to be captured in session context, triggering context compacts and session restarts. The `--output` flag already writes silently — pipes serve no functional purpose and only cause harm.
