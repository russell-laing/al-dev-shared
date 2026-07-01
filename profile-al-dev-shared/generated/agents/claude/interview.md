---
description: "Interview the user to extract complete BC/AL implementation details through structured questioning. Spawned by the interview skill. Produces `.dev/$(date +%Y-%m-%d)-interview-requirements.md`."
tools: ["Read", "Write", "AskUserQuestion"]
---


# Interview Orchestrator

Coordinates the interview workflow:

1. Invoke question-gatherer to conduct interview and collect answers
2. Invoke spec-writer to synthesize answers into specification

See question-gatherer and spec-writer agents for implementation details.

## Inputs

- The user's implementation request/context that motivated the interview

## Outputs

- `.dev/$(date +%Y-%m-%d)-interview-requirements.md` — the synthesized
  specification produced via spec-writer
