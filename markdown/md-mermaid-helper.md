---
applyTo: "**/*.mmd"
---

# Mermaid Diagram Rules

1. No HTML tags in node labels. Plain text or quoted labels only.
2. Do not mix diagram types per block.
3. Correct relationship syntax:
   flowchart `A --> B`, ERD `A ||--o{ B : label`.
4. Node IDs: letters, numbers, underscores only.
5. Consistent quote usage in labels.
6. No class assignments in ERD diagrams except for table/entity coloring.
7. No database cylinder notation in flowcharts. Use `[Database]`.
8. Structure order: class definitions → node declarations →
   connections → class assignments.
9. Group related nodes and connections with `%%` comments.
10. Keep diagrams focused and avoid excessive complexity.
11. No parentheses in edge labels — use dashes or underscores instead.
12. Sequence diagrams do not support `classDef` or `class` assignments.

## Rules for All Diagrams

- Each `classDef` must include `font-weight:bold`.
- Assign only one class per node, one per line.
- Use consistent 4-space indentation inside code blocks.
- Keep node/entity labels under 30 characters.
- Subdued fill colors for most nodes; emphasis colors for critical
  elements only.

## Color Palette

| Name | fill | stroke | color | Usage |
| --- | --- | --- | --- | --- |
| input | #e3f2fd | #1976d2 | #323130 | General input nodes |
| process | #f3e5f5 | #8e24aa | #323130 | General process nodes |
| output | #e8f5e8 | #388e3c | #323130 | General output nodes |
| decision | #fff8e1 | #fbc02d | #323130 | Decision nodes |
| data | #ffebee | #c62828 | #323130 | Data nodes |
| error | #fce4ec | #ad1457 | #323130 | Error states |
| emphasisBlue | #1976d2 | none | #fff | Critical elements |
| emphasisOrange | #f57f17 | none | #fff | Critical elements |
| emphasisGreen | #388e3c | none | #fff | Critical success |
| emphasisRed | #c62828 | none | #fff | Critical errors |

## Flowchart Rules

- Use `flowchart TD/TB/LR` etc.
- Valid shapes: `[Label]` `(Label)` `{Label}` `((Label))` `>Label]`
- One connection per line.
- Decision nodes: use `<br/>` for line breaks,
  keep each line ≤15 characters.
- Stroke color must contrast with fill color.

## Sequence Diagram Rules

- Use `sequenceDiagram` syntax only.
- Use `participant` for each actor.
- Use `->>` for requests, `-->>` for responses.
- Use `+`/`-` for activation boxes.
- Use `alt`/`else` for branching.
- No `classDef` or `class` assignments.

## ERD Rules

- Use `erDiagram` syntax only.
- Valid relationships:
  `||--||` `||--o{` `||--|{` `}o--||` `}|--||` `}o--o{`
- Each entity uses a distinct muted color (max 6; reuse if more).
- `classDef` and `class` allowed for table/entity coloring only.
- Text must be dark (`#323130`) for accessibility.

## Error Prevention Checklist

- [ ] No HTML tags in any label
- [ ] Only one diagram type per block
- [ ] Node IDs are alphanumeric/underscores only
- [ ] No class assignments in sequence or ERD (except entity coloring)
- [ ] No database cylinder notation in flowcharts
- [ ] One class per node, one class per line
- [ ] No semicolons on `classDef` or `class` lines
- [ ] No parentheses in edge labels
- [ ] Class assignments at end of diagram
