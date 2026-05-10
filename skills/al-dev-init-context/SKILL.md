---
name: al-dev-init-context
description: Initialize project context document for faster workflows.
---

# Command: /init-context

Initialize project for AL development profile and create project context document.

## Purpose

**Three-part setup:**

1. **Link profile instructions** — Ensures the AL development CLAUDE.md is
   loaded in this project
2. **Create project CLAUDE.md** — Project-specific instructions not covered
   by the profile
3. **Create project context** — Documents project structure for faster agent
   workflows

Creates `.dev/project-context.md` by exploring the project once and
documenting:
- Project structure
- Key objects and their purposes
- Architectural patterns
- Base app integration points
- Common code locations

This document is then used by ALL agents to avoid redundant exploration,
reducing workflow runtime by 40-60%.

## Implementation

### Step 0: Link Profile Instructions

The AL development profile CLAUDE.md must be available to Claude Code via
`.claude/rules/`. Check if it's already linked:

```bash
# Check if profile instructions are already linked
if [ -f .claude/rules/al-development-profile.md ]; then
    echo "Profile instructions already linked."
else
    echo "Profile instructions NOT linked - needs setup."
fi
```

**If not linked:**

1. Create the rules directory:

```bash
mkdir -p .claude/rules
```

2. Create a symlink to the profile CLAUDE.md:

```bash
ln -s ~/claude-configs/profile-claude-al-dev/CLAUDE.md .claude/rules/al-development-profile.md
```

3. Verify the link works:

```bash
# Should show the symlink target
ls -la .claude/rules/al-development-profile.md
# Should show content (first line)
head -1 .claude/rules/al-development-profile.md
```

4. Check if `.claude/rules/` is gitignored (it should be — these are local
   machine paths):

```bash
# If .gitignore doesn't cover it, inform the user
grep -q '.claude/rules/' .gitignore 2>/dev/null || echo "Consider adding .claude/rules/ to .gitignore (symlink is machine-specific)"
```

**Tell the user:** "Profile instructions linked. Restart Claude Code session
for instructions to take effect."

**If already linked:** Skip to Step 0b.

### Step 0b: Create Project CLAUDE.md

Check whether the project has a real `CLAUDE.md` at its root:

```bash
if [ -f CLAUDE.md ]; then
    # Check it is not a symlink
    if [ -L CLAUDE.md ]; then
        echo "CLAUDE.md is a symlink — needs replacing with a real file."
    else
        echo "Project CLAUDE.md already exists."
    fi
else
    echo "No CLAUDE.md found — needs creating."
fi
```

**If missing or is a symlink**, create a real file containing only
project-specific information. Read `app.json` to extract the project name,
publisher, ID range, and brief description, then write `CLAUDE.md`.

**Rules for project CLAUDE.md — strictly enforced:**

- Must be a real file, never a symlink to the profile CLAUDE.md
- Contains ONLY information specific to this project
- Does NOT duplicate anything already in the profile CLAUDE.md
- Does NOT include AL compile commands, build steps, deploy steps,
  or tool usage (`al-compile`, `bc-publish`, `bc-test`, `.bcconfig.json`)
  — those live in the profile

**What belongs here:**

- App name, publisher, version, and object ID range (from `app.json`)
- Project purpose — what business problem this app solves
- Object name prefix used in this project (e.g. `"ABC"`)
- Project-specific conventions that differ from profile defaults
- Key contacts or repo links if relevant

**Minimal template to populate:**

```markdown
# [App Name]

[One-sentence description of what this app does.]

## Project Details

- **Publisher:** [Publisher]
- **Version:** [Version]
- **Object ID range:** [Start]–[End]
- **Name prefix:** [Prefix]

## Project-Specific Conventions

[Any conventions unique to this project not covered by the profile.]
```

**If already exists and is a real file:** Skip to Step 1.

### Step 1: Check if Context Exists

```bash
if [ -f .dev/project-context.md ]; then
    Read existing context
    Ask user: [Update] [Regenerate] [Cancel]
else
    Proceed to creation
fi
```

### Step 2: Explore Project Structure

**Use Task tool with subagent_type=Explore (thoroughness: medium):**

```text
Explore the AL project and document:

1. Directory structure (where are tables, pages, codeunits, etc.)
2. All custom objects (tables, table extensions, pages, page extensions,
   codeunits, reports, enums)
   - Object IDs
   - Object names
   - Brief purpose (from code or name)

3. Architectural patterns:
   - How are validations implemented? (OnValidate, events, dedicated codeunits?)
   - How are extensions structured? (field naming, placement)
   - Error handling patterns (Error() vs Message() usage)

4. Base app integration:
   - Which base tables are extended? (find table extensions, note base table)
   - Which events are subscribed to? (find EventSubscriber attributes)
   - Which base app procedures are called? (look for Database:: references)

5. Common code locations:
   - Where is validation logic?
   - Where are posting extensions?
   - Where is UI customization?

6. Dependencies:
   - Internal (which codeunits depend on others)
   - External (any dependencies.json references)

Write findings to .dev/project-context.md using the template from
.dev-templates/project-context.md
```

### Step 3: Validate Context

Read the generated context and check:
- All sections have content (not just templates)
- At least 3 objects documented
- Structure makes sense

### Step 4: Confirm

```text
Project context initialized → .dev/project-context.md

Documented:
- [N] tables/extensions
- [N] pages/extensions
- [N] codeunits
- [N] base app integration points
- [N] architectural patterns

This context will speed up all future workflows by 40-60%.
Agents will read this first before exploring.

Update this context when you add significant new patterns or objects:
/init-context (will offer to update, not regenerate)
```

## Update Mode

If context exists and user chooses Update:

1. Read existing context
2. Scan project for new objects (compare IDs)
3. Append new findings to appropriate sections
4. Don't rewrite existing content
5. Add timestamp to "Recent Changes Log"

## When to Run

**Run once per project** (first time using AL profile)
**Update when:**
- Adding new architectural patterns
- Major refactoring
- Significant new features added
- Project structure changes

## Integration

This command is automatically suggested if:
- User runs `/al-dev-dev-cycle` or `/al-dev-plan`
- `.dev/project-context.md` doesn't exist
- Agents detect they're doing excessive exploration

```text
"No project context found. Would you like me to create one?
This one-time setup (2-3 min) will speed up all future workflows by 40-60%."

[Yes, Create Context] [Skip for Now]
```

## Technical Notes

- Uses Explore agent (medium thoroughness)
- First-time cost: 2-4 minutes
- Ongoing benefit: Saves 5-15 minutes per workflow
- ROI: Breaks even after 1-2 workflows

---

**This is infrastructure work that pays dividends immediately.**
