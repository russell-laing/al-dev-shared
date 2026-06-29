# AL Developer Shared Standards

This document is the canonical shared standards reference for AL developer
agents. It covers only the rules that are correct across both orchestrated
implementation and `/fix` dispatch paths.

## Required Pre-Flight

- Complete `knowledge/al-symbol-pre-flight.md` before writing AL code.
- Label every symbol-evidence item as `AL LSP`, `AL MCP`, `text search`, or
  `unverified`.
- Stop and report if any required item remains `unverified`.

## Required Standards

- Follow `knowledge/al-developer-patterns.md` for AL code patterns,
  naming, error handling, and performance rules.

## Compilation Safeguard

- Apply `knowledge/compile-output-safeguard.md` before treating compile
  output as success evidence.

## Agent Route Rules

- TDD agent: use `TDD_CYCLE_GATE` after each RED, GREEN, and REFACTOR phase.
- Traditional agent: use `BUILD_VERIFY_GATE` after implementation.
- `/fix` dispatches to the traditional agent without inheriting
  orchestrate-only ownership-report wording from the spawn prompt.
