# Forbidden Pattern Scan

Shared forbidden-pattern list and scan procedure referenced by
`implement-health-plan` Phase 1 (verification checklist) and Phase 2
(per-task commit scan).

## Patterns

A change passes the forbidden-pattern scan when none of the following appear in
the changed file content:

| Pattern | Meaning |
|---------|---------|
| `[date]` | Unrendered date placeholder |
| Bare `YYYY-MM-DD` as a literal value | Not a path-format specifier or example |
| `TODO` or `TBD` | Incomplete work |
| `Co-Authored-By` | AI attribution forbidden per `commit-conventions.md` (file content AND git trailers) |
| `claude:` or `copilot:` prefixed tokens | Harness debug tokens left in |

## Scan command

Run the following from the repo root (replace `<task-commit>` and `<changed-files>` with actual values):

```bash
git show <task-commit> -- <changed-files> | grep -E '\[date\]|TODO|TBD|claude:|copilot:'
grep -rEn '[0-9]{4}-[0-9]{2}-[0-9]{2}' <changed-files>   # bare YYYY-MM-DD placeholders
grep -rn  'Co-Authored-By'             <changed-files>   # AI attribution (forbidden per commit-conventions.md)
```

An empty result means the scan passed.
