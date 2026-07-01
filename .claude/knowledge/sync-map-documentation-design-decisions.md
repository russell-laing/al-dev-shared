# Sync Map Documentation — Design Decisions

## Phase 2 async-dispatch handling

**Decision:** The sync workflow dispatches audit agents asynchronously (Phase 2), allowing
audit completion to happen in the background while the user continues work. This design
trades reduced interaction latency (audit runs headlessly) against deferral of result
presentation to Phase 2 collect.

**Rationale:** Audit agents run for 5-10 minutes; blocking the user in Phase 1 would
exceed interactive feedback windows. Async dispatch allows fast Phase 1 completion and
separate Phase 2 collection without coupling the audit logic to the user's session state.

**Tradeoffs:**

- **Benefit:** User can work while audit runs; collect phase can run in separate session
- **Cost:** Requires deterministic audit-completion state machine and robust checkpoint handling
- **Alternative considered:** Synchronous dispatch with long-poll; rejected due to session
  timeout risk and poor UX (users waiting 10+ minutes for "collecting results")

**See also:** `knowledge/health-filter-contract.md` (filter state propagation),
`knowledge/dispatch-fallback-contract.md` (failure handling)
