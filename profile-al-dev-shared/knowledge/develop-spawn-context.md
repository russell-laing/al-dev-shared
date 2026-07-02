# Develop Spawn Context

Shared auto-location behavior for developer-tdd and developer-traditional.

## Auto-Location Rule

Callers do not pass these paths explicitly. The agent auto-locates the latest matching files in `.dev/` by glob before implementation begins. When multiple files match, select the most recent by modification time (`ls -t <glob> | head -1`).
