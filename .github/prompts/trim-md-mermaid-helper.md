# Prompt: Trim md-mermaid-helper.md Context Cost

## Context

`profile-al-dev-shared/markdown/md-mermaid-helper.md` is a Copilot CLI instruction file that
currently loads automatically on **every markdown and Mermaid file** due to its frontmatter:

```yaml
applyTo: "**/*.{md,mmd}"
```

This means it contributes to the System/Tools token budget in every session where markdown files
are open — even sessions that have nothing to do with diagrams. The file is 3,133 bytes (~800 tokens).

## Goal

Reduce the context cost of this file without losing its value for Mermaid diagram work.

## Analysis Tasks

1. **Assess actual usage**: Search the codebase for how often Mermaid diagrams (` ```mermaid ` blocks
   or `.mmd` files) actually appear. If they're rare, a broad `applyTo` is wasteful.

2. **Review the rules**: Read the file in full. Identify which rules are:
   - Always needed when writing any markdown (worth keeping in broad auto-load)
   - Only needed when writing Mermaid diagrams specifically (load on-demand)
   - Redundant or inferable from context

3. **Evaluate options** (propose 2-3 with trade-offs):
   - **Narrow the applyTo pattern** — change to `applyTo: "**/*.mmd"` so it only loads for
     dedicated Mermaid files, not all markdown. Agents writing diagrams in `.md` files would
     need to load it explicitly.
   - **Split the file** — keep a tiny "always-load" subset (2-3 universal rules) and move
     the rest to an on-demand knowledge doc that agents load when writing diagrams.
   - **Remove auto-loading entirely** — make it a pure knowledge doc that agents load
     explicitly via `read` when they need diagram guidance.

4. **Check AGENTS.md** for any instructions telling agents to read or rely on this file being
   auto-loaded. If agents depend on it, note which ones need updating.

## Expected Output

- A recommendation with reasoning
- The proposed change implemented
- Any agent instructions updated to explicitly load the file if auto-loading is removed
- A brief summary of tokens saved

## File Location

`/Users/russelllaing/al-dev-shared/profile-al-dev-shared/markdown/md-mermaid-helper.md`
