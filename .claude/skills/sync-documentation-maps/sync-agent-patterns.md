# Sync-Documentation-Maps Agent Patterns

Shared boilerplate for the four `sync-documentation-maps-*` audit/update agents.
Referenced from each agent body so the path-setup, JSON-construction, and
verification logic stay in one place.

---

## Result-Directory Path Setup

Create the output subdirectory if it does not exist before writing any file:

```bash
mkdir -p <result_dir>/audit      # for audit agents writing to audit/
mkdir -p <result_dir>/updates    # for update agents writing to updates/
```

Use the `<result_dir>` value provided in the agent inputs. Do not hard-code
paths. After creating the directory, proceed to write the output file.

---

## JSON Result Construction

Both audit agents write a JSON object to their respective `audit/` subdirectory.
Use the following structure as the skeleton; substitute surface-specific field
names (`agent` vs `skill`) and `type` values as appropriate to the surface:

**Audit agents — JSON schema:**

```json
{
  "surface": "<agents|skills>",
  "run_id": "<run_id>",
  "total_files": 12,
  "map_entries": 11,
  "discrepancies": [
    {
      "type": "<discrepancy-type>",
      "<agent|skill>": "<name>",
      "detail": "<human-readable detail>"
    }
  ],
  "summary": "1 discrepancy found: 1 missing_from_map."
}
```

- Populate `total_files` from the active surface count discovered in Step 1.
- Populate `map_entries` from the Layer 2 section count extracted from the map.
- Populate `discrepancies` from all issues found during the compare step.
- Write a plain-English `summary` field (e.g. `"3 discrepancies found: 2 missing_from_map, 1 stale_in_map."`).
- If no discrepancies were found, set `discrepancies` to `[]` and `summary` to `"No discrepancies found."`.

---

## Artifact Verification ("Read X; stop if absent")

Before reading any audit artifact, verify it exists and stop if it does not.

### Update agents — read audit JSON

```text
Read <result_dir>/audit/<surface>-audit.json.

If the file does not exist, stop immediately and report:
  ERROR: <surface>-audit.json not found at <result_dir>/audit/<surface>-audit.json
  — cannot proceed.
```

Substitute `<surface>` with `agent` or `skill` to match the surface being processed.

### Audit agents — verify written output

After writing the JSON report, verify the file exists before returning its path:

```bash
ls -la <result_dir>/audit/<surface>-audit.json
```

If the file is not found, stop and report the failure — do not return a path
for a file that does not exist on disk.

### Update agents — verify written map

After writing the updated map, verify it with both commands:

```bash
ls -la <result_dir>/updates/<map-file>
wc -l <result_dir>/updates/<map-file>
```

If `wc -l` reports fewer than the surface minimum (≥50 lines for agents,
≥100 lines for skills), stop and report:
`ERROR: written file has <N> lines (expected ≥<minimum>) — content may be truncated.`

If the file does not begin with `# AL Dev`, stop and report:
`ERROR: written file does not begin with "# AL Dev" — content format incorrect.`
