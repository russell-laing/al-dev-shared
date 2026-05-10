# al-dev-shared

Shared AL/BC development skills, knowledge, and markdown guidelines
for all harness profiles (Claude Code, Copilot CLI, and future
harnesses).

## Installation

Clone to a fixed path — `bc-code-intel-config.json` in each
harness profile references this location directly.

```bash
git clone https://github.com/russell-laing/al-dev-shared.git \
  ~/al-dev-shared
```

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
