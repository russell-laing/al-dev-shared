# Anti-Patterns

Watch for and prevent these failure modes in AL development workflows.
These are workflow anti-patterns, not a catalog of AL language or code-level anti-patterns.

| Anti-Pattern | Problem | Correct Approach |
| ------------- | --------- | ----------------- |
| **Coding it yourself** | You write AL code instead of routing implementation through the canonical developer agents | Always use `developer-tdd` or `developer-traditional` as routed by the workflow |
| **Rubber-stamping** | Accepting agent output without review | Critically evaluate every deliverable |
| **Skipping interviews** | Jumping to design without understanding requirements | Use `/interview` for complex features |
| **Single architect** | Only one design perspective considered | Spawn 2-3 solution architects with different approaches |
| **Sequential reviews** | Running reviewers one at a time | Spawn all relevant reviewers in parallel |
| **Ignoring gates** | Proceeding without user approval | Always pause at approval gates |
| **Gold-plating** | Adding features not in the requirements | Stay within scope; flag enhancements as future work |
| **Context starvation** | Spawning agents without sufficient context | Include all relevant `.dev/` artifacts and file paths |
| **Premature testing** | Writing tests before code review is resolved | Complete code review iteration first |
| **Monolith agents** | One agent doing everything | Decompose into specialist agents |
| **Trusting stale compile logs** | Reading `.dev/compile-errors.log` from a previous run and treating it as the current state — e.g., claiming "only pre-existing warnings" when the log predates recent edits | Run Step 0 (freshness check) from `knowledge/compile-lint-procedure.md` before reading any log; if any .al file is newer than the log, delete it and recompile |
| **Missing symbol pre-flight** | Writing AL code that references base-table fields, event publishers, or procedures without first verifying they exist — produces AL0118 and missing-var compile errors | Complete `knowledge/al-symbol-pre-flight.md` checklist before writing any AL code (`SYMBOL_PREFLIGHT_GATE`); report pre-flight summary before implementation begins |
| **Abstract option presentation** | Presenting design choices with only abstract descriptions ("approach A uses events, approach B uses tables") without concrete examples, forcing the user to ask for a second round of detail before deciding | Lead each option with a concrete artifact: a code snippet, a file-path list, or a before/after example. State one specific tradeoff per option, not abstract philosophy |

Not every anti-pattern applies to trivial work. Use proportional routing and scope judgment before treating every row as a mandatory gate.
