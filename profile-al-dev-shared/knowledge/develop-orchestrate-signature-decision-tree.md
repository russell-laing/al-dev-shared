# Signature Verification Decision Tree

Referenced by `skills/develop-orchestrate/SKILL.md` Phase 1.2 (Signature
Verification, Autonomous Mode). Applied when a required external procedure
(named in the approved solution plan's Procedures/Triggers section, or
equivalent implementation step) cannot be verified by any evidence tier.

**Decision tree if any required external procedure is NOT VERIFIED:**

1. Stop developer spawn immediately — do not proceed to Phase 3
2. Generate report block with exact procedure name and reason for non-verification:

   ```text
   SIGNATURE_VERIFICATION_FAILED

   Unverified required signature: [ProcedureName]
   Evidence source attempted: [AL LSP / AL MCP / text search]
   Reason: [not found / ambiguous match / no provider available]

   Impact: This procedure is required for the implementation plan.
   Cannot proceed without verification.

   Resolution required:
   - Verify the procedure exists and signature is correct
   - Consult BC documentation or base app source
   - Confirm exact parameter names and types (including var modifiers)
   - Rerun /develop-orchestrate with --autonomous after verification
   ```

3. Escalate to user with this report
4. Do NOT spawn developers until signature is verified

Only carry a NOT VERIFIED item forward as a documented risk when the
procedure is explicitly optional or no assigned developer task depends on
calling it. If an optional item is carried forward, include this block in the
developer spawn prompt:

```text
Optional unverified signatures — do NOT guess these:
- [ProcedureName]: [reason not verified; not required for assigned task]
STOP and report back if the implementation would need to call this procedure.
```
