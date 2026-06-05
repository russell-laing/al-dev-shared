# al-dev-shared

Shared AL/BC development skills, knowledge, and markdown guidelines
for all AI development harnesses:

- **Claude Code** — Desktop app, CLI, and IDE extensions
- **GitHub Copilot CLI** — Autonomous command-line agent
- **Codex** — Autonomous development system

## System Prerequisites

Before installing al-dev-shared, ensure you have:

- **Git** — for cloning the repository and version control
- **Python 3.9+** — for validation scripts and development tools
- **One of the supported harnesses:**
  - [Claude Code](https://claude.ai/code) (Desktop app, CLI, or IDE extension)
  - [GitHub Copilot CLI](https://github.com/features/copilot/cli)
  - [Codex](https://docs.anthropic.com/agents/codex)

**For local development (Option B):**

```bash
# Verify Python version
python3 --version

# Verify Git
git --version
```

### Optional: Development Tools

If you plan to contribute to the plugin or run development scripts, install:

- **markdownlint** — for markdown validation

  ```bash
  # Option 1: via npm
  npm install -g markdownlint-cli
  
  # Option 2: via npx (no install required)
  npx --yes markdownlint-cli <file>
  ```

- **ruff** — for Python linting (development only)

  ```bash
  pip3 install ruff
  ```

- **Node.js 18+** — for npm-based tools

  ```bash
  # Install via Homebrew (macOS)
  brew install node

  # Or download from https://nodejs.org/
  ```

- **pytest** — for running Python tests

  ```bash
  pip3 install pytest
  ```

- **jq** — for JSON parsing and manipulation

  ```bash
  # Install via Homebrew (macOS)
  brew install jq

  # Or compile from source: https://github.com/jqlang/jq
  ```

- **ripgrep (rg)** — faster alternative to grep

  ```bash
  # Install via Homebrew (macOS)
  brew install ripgrep

  # Falls back to standard grep if not available
  ```

- **al-compile** — for AL/BC syntax validation
  - Installed via AL Code Intelligence MCP or Business Central development environment

---

## Installation

### Option A: Install from GitHub Marketplace (Recommended)

Add the plugin marketplace from GitHub and install in your harness.

#### Claude Code

```bash
/plugin marketplace add russell-laing/al-dev-shared
/plugin install al-dev-shared@al-dev-shared
```

Updates apply automatically at startup. Check for updates manually:

```bash
/plugin marketplace update al-dev-shared
```

List installed plugins:

```bash
/plugin list
```

#### GitHub Copilot CLI

```bash
copilot plugin marketplace add russell-laing/al-dev-shared
copilot plugin install al-dev-shared@al-dev-shared
```

Check for updates:

```bash
copilot plugin update al-dev-shared
copilot plugin update --all
```

List installed plugins:

```bash
copilot plugin list
```

#### Codex

```bash
codex plugin marketplace add russell-laing/al-dev-shared
```

Verify installation by entering the Codex CLI and listing plugins:

```bash
codex
/plugins
```

---

### Option B: Local Clone (Development)

Clone the repository to a local path for live development access. Changes to skills, agents, and knowledge take effect immediately without reinstalling.

#### Clone the Repository

```bash
git clone https://github.com/russell-laing/al-dev-shared.git \
  ~/al-dev-shared
```

> **Note:** Use a consistent path (`~/al-dev-shared` recommended) — harness
> configurations reference this location directly.

#### Claude Code

Register as a local directory marketplace in `~/.claude/settings.json`:

```json
{
  "al-dev-shared": {
    "source": {
      "source": "directory",
      "path": "/Users/YOUR-USERNAME/al-dev-shared"
    }
  }
}
```

Then install:

```bash
/plugin install al-dev-shared@al-dev-shared
```

#### GitHub Copilot CLI

Register as a local directory marketplace in `~/.copilot/settings.json`:

```json
{
  "al-dev-shared": {
    "source": {
      "source": "directory",
      "path": "/Users/YOUR-USERNAME/al-dev-shared"
    }
  }
}
```

Then install:

```bash
copilot plugin install al-dev-shared@al-dev-shared
```

#### Codex

Edit or create `~/.codex/config.toml` and add the plugin source:

```toml
[[plugin_sources]]
name = "al-dev-shared"
path = "/Users/YOUR-USERNAME/al-dev-shared"
```

Then reload Codex or verify with:

```bash
codex
/plugins
```

---

### Option A vs. Option B

| Aspect | Option A (Marketplace) | Option B (Local Clone) |
|--------|------------------------|------------------------|
| **Setup** | One command per harness | Clone + config file edits |
| **Updates** | Automatic or manual command | Manual `git pull` |
| **Use Case** | Production / stable usage | Development / testing changes |
| **Live Edits** | No — installed snapshot cached | Yes — reads repo working tree |
| **Storage** | `~/.claude/plugins/cache/` | Your chosen path (`~/al-dev-shared`) |

> **Important:** Do not register both Option A and Option B on the same
> machine — harnesses cannot load the same plugin from two sources. Choose
> one option and use it consistently.

---

## Plugin Management

### Disable or Uninstall

**Claude Code:**

```bash
/plugin disable al-dev-shared@al-dev-shared
/plugin uninstall al-dev-shared@al-dev-shared
/plugin marketplace remove al-dev-shared
```

**Copilot CLI:**

```bash
copilot plugin disable al-dev-shared@al-dev-shared
copilot plugin uninstall al-dev-shared@al-dev-shared
copilot plugin marketplace remove al-dev-shared
```

**Codex:**

Edit `~/.codex/config.toml` and set:

```toml
[plugins."al-dev-shared@al-dev-shared"]
enabled = false
```

Or remove the entire `[[plugin_sources]]` block for that plugin.

---

## Contents

- `profile-al-dev-shared/skills/` — 19 shared AL development skills
- `profile-al-dev-shared/agents/` — Agent definitions (harness-neutral)
- `profile-al-dev-shared/knowledge/` — Workflow and development knowledge
- `bc-code-intel-knowledge/` — BC Code Intelligence specialist knowledge
- `profile-al-dev-shared/markdown/` — Markdown and Mermaid style guides
- `docs/` — Architectural documentation and development guides

---

## Documentation

- **Getting Started:** See `CLAUDE.md`, `AGENTS.md`, or `CODEX.md` for harness-specific setup
- **Skill Reference:** `docs/al-dev-skills-map.md`
- **Agent Reference:** `docs/al-dev-agent-map.md`
- **Development Guide:** `docs/development-commands.md`

---

## Troubleshooting

### Plugin Won't Load

**Claude Code:**

```bash
# Verify marketplace is registered
/plugin marketplace list

# Clear cache and reload
/reload-plugins
```

**Copilot CLI:**

```bash
# Verify marketplace is registered
copilot plugin marketplace list

# Test plugin path
copilot plugin list
```

**Codex:**

```bash
# Verify config syntax
cat ~/.codex/config.toml

# Check plugin sources
codex
/plugins
```

### Updates Not Appearing (Option B / Local Clone)

Pull the latest changes:

```bash
cd ~/al-dev-shared
git pull origin master
```

Then reload your harness (e.g., `/reload-plugins` in Claude Code, or restart
Copilot CLI / Codex).
