# Diagnostic Rules Reference

Classification rules for AL/BC diagnostic violations.

| Rule Category | Severity | Fix Strategy | Notes |
| --- | --- | --- | --- |
| Semantic Errors | High | Direct fix | Missing declaration, type mismatch |
| Performance Anti-patterns | Medium | Manual review | Index missing, inefficient loops |
| Style Violations | Low | Auto-format | Naming, indentation |
| Deprecated APIs | Medium | Manual migration | API version check required |

**Cross-agent usage:** Referenced by diagnostics-resolver, diagnostics-classifier, and lint-analyzer agents.
