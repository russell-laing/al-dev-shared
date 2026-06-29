# False-Positive Classes

| ID | Description | First seen | Last seen | Status |
| --- | --- | --- | --- | --- |
| friction-surface-mismatch | Friction-ingest findings mapped to structurally different target files | 2026-06-18 | 2026-06-18 | Candidate |
| subjective-clarity-name-fit | Clarity and name-fit lens findings with no objective criterion | 2026-06-19 | 2026-06-19 | Candidate |

## Status Progression

`Candidate` means the class has been observed in one sweep. `Monitor` means the
class recurred across two independent sweeps and should be named in benchmark
precision notes. `Suppress` means a maintainer approved active suppression and
the discovery or verification prompt has been updated to include the class as a
known false-positive pattern.

Promoting a class to `Suppress` has no runtime effect by itself. The prompt
context must change, and the next two sweeps must retain zero findings from
that class before the suppression is considered effective.
