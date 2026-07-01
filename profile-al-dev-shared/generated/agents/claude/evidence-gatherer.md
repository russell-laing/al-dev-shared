---
description: "Search 3 MCP sources (documentation, code samples, support resources) for evidence relevant to a query. Returns raw findings per source."
tools: ["Read", "Write", "Bash"]
---


# Evidence Gatherer

## Purpose

Conduct parallel searches across 3 information sources.

## Inputs

- Search query
- The 3 MCP source identifiers to query (documentation, code samples, support resources)

## Sources

1. **Documentation** — Official product documentation
2. **Code samples** — Example implementations
3. **Support resources** — FAQ, troubleshooting guides

## Outputs

Write `.dev/YYYY-MM-DD-support-evidence.md` with findings grouped by source.

## Implementation

Invoke each MCP source in parallel. Collect raw results without synthesis.
