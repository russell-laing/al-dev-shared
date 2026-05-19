# Script Engineer Conventions

Referenced by: `al-dev-script-engineer` agent

## Script Conventions (follow strictly)

### Async-First Design
Write async code patterns when possible; use proper concurrency primitives. For Python, use `asyncio`. For Node.js, use `async/await` or Promises. For Bash, use background processes sparingly and document cleanup.

### Protocol-Based Integration
Scripts must export structured output (JSON/CSV) that parses cleanly. Always include an exit code that indicates success/failure.

### Strict Typing
Define input/output schemas; validate at boundaries. For Python, use type hints. For TypeScript, use explicit types. Document expected schema in comments.

## Toolkit Reference

The `al-analysis-toolkit` is optional:

```bash
TOOLKIT_PATH=$(find ~ -name "al-analysis-toolkit" -maxdepth 5 -type d 2>/dev/null | head -1)
if [ -z "$TOOLKIT_PATH" ]; then
  echo "al-analysis-toolkit not found; continuing without it"
else
  source "$TOOLKIT_PATH/init.sh"
fi
```

If toolkit is not found, script should continue with reduced capability or provide clear error messages.

## Language Selection

Always match the language to the project's existing stack. Detection order:
1. Check `package.json` (Node.js project)
2. Check `go.mod` (Go project)
3. Check `requirements.txt` or `setup.py` (Python project)
4. If none found, default to Python 3

Document the detection logic in the script.

## Code Examples

### Python Error Handling Pattern
```python
import json
import sys

def main():
    try:
        result = process_data()
        print(json.dumps(result, indent=2))
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
```

### Output Format
Scripts should return:
- `0` on success
- Non-zero on failure
- Structured output to stdout (JSON preferred)
- Errors to stderr
