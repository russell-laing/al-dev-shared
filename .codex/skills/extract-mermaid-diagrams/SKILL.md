---
name: extract-mermaid-diagrams
description: Use when Codex needs to extract Mermaid diagrams from Markdown files and render them as PNG, SVG, or PDF images for visual inspection by AI harnesses. Trigger on requests to analyze Mermaid diagrams visually, convert Mermaid fences to images, verify diagram readability, capture workflow diagrams from docs, or produce diagram artifacts with source-line metadata.
---

# Extract Mermaid Diagrams

## Overview

Extract Mermaid code fences from Markdown, render each diagram through Mermaid CLI, and produce an image set plus a JSON manifest and Markdown index for AI harness review.

## Quick Start

Run the bundled script from the repository root or any workspace with Markdown
files:

```bash
python3 .codex/skills/extract-mermaid-diagrams/scripts/extract_mermaid_diagrams.py docs/maintainer_tooling.md --out /private/tmp/mermaid-diagrams
```

Use `--format svg` for scalable review artifacts or repeat `--format` to
produce multiple render types:

```bash
python3 .codex/skills/extract-mermaid-diagrams/scripts/extract_mermaid_diagrams.py docs/maintainer_tooling.md --format png --format svg --out /private/tmp/mermaid-diagrams
```

## Workflow

1. Read the user's target path and resolve each Markdown file exactly.
2. Run `extract_mermaid_diagrams.py` with a temporary output directory unless
   the user requests a specific destination.
3. Inspect `manifest.json` for diagram IDs, source line ranges, render status,
   and output image paths.
4. Use `index.md` as the human-readable harness handoff. It embeds or links the
   rendered images and includes each diagram source block.
5. Analyze the rendered images, not just the Mermaid source, when the request is
   about visual clarity, layout, color, overlap, or readability.

## Output Contract

The script writes:

- `<diagram-id>.mmd` - extracted Mermaid source.
- `<diagram-id>.<format>` - rendered image artifact for each requested format.
- `manifest.json` - machine-readable source line and artifact metadata.
- `index.md` - review-friendly index for AI or human visual inspection.

Report the `index.md` and `manifest.json` paths when handing off results.

## Rendering Notes

- Prefer PNG for direct multimodal image analysis.
- Use SVG when the reviewer needs crisp zoomable artifacts or text inspection.
- Use `--no-render` only when extraction metadata is useful without images.
- If Mermaid CLI is missing, install or provide `mmdc` before claiming that
  diagrams cannot render.
- If `mmdc` fails because Chromium or Puppeteer cannot launch in the sandbox,
  rerun the same command outside the sandbox or with approved escalation before
  editing the diagrams. Treat browser-launch failure as environment evidence,
  not Mermaid syntax evidence.
- Keep generated image artifacts in `/private/tmp`, `.dev`, or another explicit
  scratch/output location unless the user asks to keep them in the repository.

## Script

Use:

```bash
python3 <skill-dir>/scripts/extract_mermaid_diagrams.py --help
```

The script supports multiple input files, repeated `--format` values, Mermaid
CLI theme/background/scale settings, and optional Mermaid, CSS, or Puppeteer
config files.
