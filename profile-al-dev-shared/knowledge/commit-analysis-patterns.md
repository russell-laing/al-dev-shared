# Commit Analysis Patterns

Diff-parsing patterns and manifest extraction rules for al-dev-commit-analyzer.

## AL File Detection

A file is an AL file when its path ends in `.al` (case-insensitive).
All other extensions are non-AL files.

## AL Manifest Extraction

Extract one manifest block per AL file from `git diff` output.

### Extraction Rules

From diff lines (`-` = removed, `+` = added):

- **`fields_removed`** — `-` lines matching `field(\d+;` inside a `fields` block — extract the quoted name
- **`fields_added`** — `+` lines matching the same pattern
- **`procs_modified`** — Procedure name appears on both a `-` line and a `+` line
- **`procs_added`** — Procedure name on `+` lines with no matching `-` pair
- **`procs_removed`** — Procedure name on `-` lines with no matching `+` pair

### Manifest Block Format

```json
{
  "file": "path/to/Codeunit.al",
  "object_type": "Codeunit",
  "object_id": 50100,
  "object_name": "My Codeunit",
  "fields_added": [],
  "fields_removed": [],
  "procs_added": [],
  "procs_removed": [],
  "procs_modified": []
}
```

## Non-AL File Handling

For non-AL files (`.json`, `.md`, `.yaml`, `.xml`, `.txt`, etc.):
emit a simple one-liner — no full manifest block.

```json
{ "file": "app.json", "change": "modified" }
```
