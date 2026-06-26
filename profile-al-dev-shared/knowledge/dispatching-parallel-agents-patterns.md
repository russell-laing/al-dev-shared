# Parallel Agent Dispatching Patterns

Guidance for skills that dispatch agents to solve independent problems at scale (3+ agents, unbounded concurrency risk).

## When to Use Parallel Dispatch

- 3+ independent verification or analysis tasks (e.g., rubber-duck 10+ findings)
- Each task can run without shared state or blocking on others' results
- Caller can collect results and synthesize without individual errors blocking the batch

**Unbounded concurrency risk:** Dispatching N agents for N findings without batching can overload a single session if N > 50–100. Implement bounded waves or batching below.

## Pattern 1: Bounded Waves

Group agents into waves of K (typically 3–5) and dispatch each wave, awaiting results before the next.

**Use when:**

- Finding count is moderate (10–30)
- Results from one wave may inform the next
- Session load must be predictable

**Example:** `discover-plugin-health` Phase 3 dispatches lens agents in bounded waves of ≤5, awaiting completion before moving to Phase 4.

```python
wave_size = 5
agents_to_dispatch = list_of_agents
for i in range(0, len(agents_to_dispatch), wave_size):
    wave = agents_to_dispatch[i:i+wave_size]
    # Dispatch all in wave
    # Await all results before next wave
```

## Pattern 2: Batching by Subject

Group findings that reference the same subject file and dispatch one agent per unique subject (vs. one agent per finding).

**Use when:**

- Many findings (20+) reference a small set of files (e.g., 5–10 unique skill files)
- Verification is file-centric (read once, verify all claims in that file)
- Reduces agent spawn count by 2–3×

**Example:** `plan-plugin-findings` Phase 3 batches findings by subject_path, dispatching one `verify-health-finding` agent per path.

```
Subject: skill-a.md → Agent 1 verifies [Finding 1, Finding 3, Finding 7]
Subject: skill-b.md → Agent 2 verifies [Finding 2]
Subject: skill-c.md → Agent 3 verifies [Finding 4, Finding 5, Finding 6]
```

## Pattern 3: One-per-Task (Unbounded Risk)

Dispatch one agent per task with no grouping. Simple but risky at scale.

**Use only when:**

- Task count < 10 and session load is acceptable
- Grouping would break agent focus (each task is semantically independent)

**Avoid at scale:** At 50+ tasks, unbounded dispatch risks session timeouts.

## Fallback: Inline Sequential Dispatch

When parallel dispatch is unavailable (e.g., harness limitation), fall back to sequential agent dispatch within a loop:

```
for finding in findings:
  agent = dispatch(verify, finding)
  record = agent.await_result()
  records.append(record)
```

Slower (N serial agents vs. N/K parallel waves) but maintains correct semantics and error handling.

## Decision Table

| Task Count | Recommendation | Pattern | Rationale |
|-------|----|---------|-----------|
| < 5 | One-per-task | None (inline) | No batching needed |
| 5–10 | One-per-task | None (bounded implicitly) | Session load acceptable |
| 10–20 | Batching by subject | Batch + bounded waves | Reduce spawn count, predictable load |
| 20–50 | Bounded waves | Waves of 5–10 | Predictable load, easy recovery |
| 50+ | Bounded waves + batching | Waves of batched subjects | Must control session load |

---

## Contract for Callers

Each dispatching skill must document:

1. **Agent dispatch count:** Expected number of agents spawned
2. **Batching strategy:** One-per-finding, by-subject, or other
3. **Wave size:** If using bounded waves, K value and rationale
4. **Fallback plan:** Sequential dispatch if parallel unavailable
5. **Error handling:** What if one agent fails? Is the batch atomic?
