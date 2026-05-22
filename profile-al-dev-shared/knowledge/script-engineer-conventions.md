# Script Engineer Conventions

Referenced by: `al-dev-script-engineer` agent

## Script Conventions (follow strictly)

### Async-First Design
Write async code patterns when possible; use proper concurrency primitives. For Python, use `asyncio`. For Node.js, use `async/await` or Promises. For Bash, use background processes sparingly and document cleanup.

**Python asyncio example:**
```python
import asyncio
import aiohttp

async def fetch_data(url: str) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            return await resp.json()

async def fetch_multiple(urls: list) -> list:
    # Fetch all URLs in parallel, not sequentially
    tasks = [fetch_data(url) for url in urls]
    return await asyncio.gather(*tasks)

if __name__ == "__main__":
    urls = ["https://api.example.com/1", "https://api.example.com/2"]
    result = asyncio.run(fetch_multiple(urls))
    print(json.dumps(result))
```

**Why:** Sequential requests are slow — fetching 10 URLs one-by-one takes 10× the time of parallel. Use `asyncio.gather()` for true concurrency.

### Protocol-Based Integration

Scripts often need to communicate results to parent processes (Claude Code harness, CI/CD, Slack, etc.). Use **structured protocol output** instead of free-form logging. Scripts must export structured output (JSON/CSV) that parses cleanly. Always include an exit code that indicates success/failure.

**Protocol patterns:**

**Pattern 1: Exit Code + Stdout JSON**

```bash
#!/bin/bash
# Script performs some task and outputs structured result

result_json=$(cat <<EOF
{
  "status": "success",
  "task": "deploy-app",
  "version": "1.0.5",
  "duration_seconds": 42,
  "artifacts": [
    "dist/app-1.0.5.tar.gz",
    "dist/app-1.0.5.sha256"
  ]
}
EOF
)

echo "$result_json"
exit 0  # 0 = success; non-zero = failure
```

Parent process parses JSON from stdout, checks exit code:

```bash
output=$(./deploy.sh)
if [ $? -eq 0 ]; then
    version=$(echo "$output" | jq -r '.version')
    echo "Deployment succeeded: $version"
else
    echo "Deployment failed"
    exit 1
fi
```

**Pattern 2: Structured Log Lines (Newline-Delimited JSON)**

```bash
#!/bin/bash
# Script emits progress as it runs; each line is parseable JSON

log_event() {
    local phase=$1
    local status=$2
    local message=$3
    echo "{\"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\", \"phase\": \"$phase\", \"status\": \"$status\", \"message\": \"$message\"}"
}

log_event "setup" "in_progress" "Installing dependencies..."
pip install -r requirements.txt
log_event "setup" "completed" "Dependencies installed"

log_event "test" "in_progress" "Running tests..."
pytest tests/
log_event "test" "completed" "Tests passed (24/24)"
```

Parent process (Claude Code monitor) reads each line, parses JSON, updates UI:

```
✓ Setup completed: Dependencies installed
✓ Test completed: Tests passed (24/24)
```

**Pattern 3: File-Based Result Checkpoint**

```bash
#!/bin/bash
# Long-running script writes progress to .dev/progress.json periodically

progress_file=".dev/progress.json"

update_progress() {
    local phase=$1
    local percent=$2
    cat > "$progress_file" <<EOF
{
  "phase": "$phase",
  "percent_complete": $percent,
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "status": "in_progress"
}
EOF
}

update_progress "compilation" 25
./compile-all.sh
update_progress "linking" 50
./link-all.sh
update_progress "packaging" 75
./package-app.sh
update_progress "completed" 100

cat > "$progress_file" <<EOF
{
  "phase": "completed",
  "percent_complete": 100,
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "status": "success",
  "output": "app-1.0.5.tar.gz"
}
EOF
```

Claude Code harness polls `.dev/progress.json` and shows progress bar; on completion, reads the `output` field.

**When to use each pattern:**

- **Exit Code + JSON:** Simple scripts, one-shot operations, CI/CD integration
- **Log Lines (NDJSON):** Long-running scripts, multiple discrete steps, monitoring/UI feedback
- **File Checkpoint:** Very long operations (>10 minutes), risk of process interruption, need to resume

All three patterns follow the rule: **Make your output machine-parseable, not human-readable.** Humans read JSON fine; machines struggle with prose.

### Strict Typing
Define input/output schemas; validate at boundaries. For Python, use type hints. For TypeScript, use explicit types. Document expected schema in comments.

**Python typed dataclass example:**
```python
from dataclasses import dataclass
from typing import Optional, List
import json

@dataclass
class Order:
    id: str
    customer_name: str
    amount: float
    items: List[str]
    created_at: Optional[str] = None

def process_order(order_dict: dict) -> Order:
    # Validate and convert input to typed object
    try:
        order = Order(
            id=order_dict["id"],
            customer_name=order_dict["customer_name"],
            amount=float(order_dict["amount"]),
            items=order_dict.get("items", []),
        )
        return order
    except KeyError as e:
        raise ValueError(f"Missing required field: {e}")

# Output is guaranteed to match the schema
output = Order(id="123", customer_name="John", amount=99.99, items=["A", "B"])
print(json.dumps(output.__dict__))
```

**Why:** Type hints catch mistakes at validation time, not at some downstream use. Define your schema upfront, validate at entry points, and the rest of your code can trust the data.

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
