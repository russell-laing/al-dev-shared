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
Scripts must export structured output (JSON/CSV) that parses cleanly. Always include an exit code that indicates success/failure.

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
