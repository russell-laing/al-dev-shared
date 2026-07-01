# Implementation Skill Phase Structure

## Sequential, not coupled phase operations

**Design principle:** Each phase of the implementation skill (Locate → Resume →
Checkpoint → Execute → Verify → Sync) reads output from the prior phase but writes
independently. Phases are sequential (execute after prior completion) but not tightly
coupled (output format of Phase N does not dictate input parsing of Phase N+1).

**Rationale for sequentiality:** Implementation order matters. We must locate the plan
before deciding resume/restart; must evaluate resume state before reading the plan;
must verify execution success before closing the ledger. Parallel execution would
violate causal ordering.

**Rationale against coupling:** Each phase should be independently testable and
understandable. If Phase 3 (Checkpoint Write) required parsing Phase 2 (Resume Decision)
output directly, changing Phase 2 would force Phase 3 changes. By deferring to `.dev/`
checkpoint files with stable schema, phases remain independently testable and more
maintainable.

**Structure:** Each phase reads from stable checkpoint files created by prior phases,
not from the prior phase's in-memory state. This supports resume (checkpoint files persist
across sessions) and testing (phases can be unit-tested with fixture checkpoints).

**See also:** `knowledge/phase-proof-contract.md` (phase boundary verification)
