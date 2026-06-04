# al-dev-shared

Shared AL/BC development skills, knowledge, and markdown guidelines
for all harness profiles (Claude Code, Copilot CLI, and future
harnesses).

## Installation

### Option A — Install from GitHub (consumers)

In Claude Code, add the marketplace directly from the GitHub repo and
install the plugin:

```text
/plugin marketplace add russell-laing/al-dev-shared
/plugin install al-dev-shared@al-dev-shared
```

The plugin is copied to a versioned cache under
`~/.claude/plugins/cache/` — consumers get an installed snapshot, not
a live view of this repo. The plugin tracks the latest commit on
`master`: updates apply automatically at startup, or on demand with
`/plugin marketplace update al-dev-shared`.

### Option B — Local clone (development)

Clone to a fixed path — `bc-code-intel-config.json` in each
harness profile references this location directly.

```bash
git clone https://github.com/russell-laing/al-dev-shared.git \
  ~/al-dev-shared
```

A directory-source marketplace reads this repo's working tree live,
so skill and knowledge edits take effect without reinstalling. A
machine cannot register two marketplaces with the same name, so use
either Option A or Option B, not both.

Then register as a marketplace in your harness settings:

**Claude Code (`~/.claude/settings.json`):**

```json
"al-dev-shared": {
  "source": { "source": "directory",
              "path": "/Users/russelllaing/al-dev-shared" }
}
```

**Copilot CLI (`~/.copilot/settings.json`):**

```json
"al-dev-shared": {
  "source": { "source": "directory",
              "path": "/Users/russelllaing/al-dev-shared" }
}
```

## Contents

- `skills/` — 19 shared AL dev skills
- `knowledge/` — AL workflow knowledge docs
- `bc-code-intel-knowledge/` — BC Code Intelligence knowledge base
- `markdown/` — Markdown and Mermaid style guides
