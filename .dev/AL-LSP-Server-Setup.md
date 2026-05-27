# AL Language Server Protocol (LSP) Setup Guide

## Overview

This guide documents the installation, configuration, and use of the **al-lsp-for-agents** LSP server, which provides static code analysis and navigation features for AL (Business Central) development in Claude Code. The LSP server enables features like hover information, go-to-definition, find references, and call hierarchy without requiring a running Business Central instance.

**Project:** Kembla Remittance Advice  
**Repository:** [SShadowS/al-lsp-for-agents](https://github.com/SShadowS/al-lsp-for-agents)  
**Current Version:** 1.11.3

---

## What Is the AL LSP Server?

The AL LSP Server is a **Language Server Protocol** implementation that wraps Microsoft's proprietary AL Language Server (from the VS Code AL extension). It provides:

- **Go-to-Definition:** Jump to the source of a table, procedure, or field
- **Find References:** Locate all usages of a symbol
- **Hover Information:** View type information, field definitions, and documentation
- **Symbol Navigation:** Search for and navigate to AL objects
- **Call Hierarchy:** Explore the call graph of procedures (with Rust sidecar)
- **Code Lens:** Reference counts and unused procedure detection

All analysis is **static** — performed locally against your AL source files without a running BC server.

---

## Architecture

```
┌─────────────────┐
│  Claude Code    │
│   (AI Agent)    │
└────────┬────────┘
         │ (LSP over stdio)
         ▼
┌──────────────────────────────────────┐
│  al-lsp-wrapper (Go binary)          │
│  • Accepts LSP requests from Claude  │
│  • Proxies to MS AL Language Server  │
│  • Translates method names           │
└────────┬─────────────────────────────┘
         │ (child process over stdio)
         ▼
┌──────────────────────────────────────┐
│  Microsoft AL Language Server        │
│  (from VS Code extension)            │
│  • Parses .al files                  │
│  • Analyzes symbols & references     │
│  • Returns diagnostics               │
└──────────────────────────────────────┘
         │ (auto-discovered)
         ▼
┌──────────────────────────────────────┐
│  VS Code AL Extension (.NET DLLs)    │
│  ~/.vscode/extensions/               │
│    ms-dynamics-smb.al-17.0.2273547/  │
└──────────────────────────────────────┘
```

The wrapper also includes an optional Rust sidecar (`al-call-hierarchy`) for advanced features like call hierarchy and code lens.

---

## Prerequisites

### Required

- **macOS** (arm64) — The setup in this guide is specific to Apple Silicon Macs
- **Go 1.21+** — For building the wrapper from source (pre-built binary not yet available for macOS)
- **VS Code AL Extension** — Installed via VS Code
  - Minimum: `ms-dynamics-smb.al-17.0.0` or later
  - Location: `~/.vscode/extensions/ms-dynamics-smb.al-*/`
- **Claude Code** — Latest version with LSP tool support
- **AL Project** — A valid AL project with `app.json` and `.al` source files

### Optional

- **Git** — For cloning the al-lsp-for-agents repository (or download ZIP)

---

## Installation

### Step 1: Install the al-lsp-for-agents Plugin

In Claude Code, install the al-lsp-for-agents plugin from the marketplace:

```bash
/plugin marketplace add SShadowS/al-lsp-for-agents
```

Or navigate to the Plugins UI and search for `al-lsp-for-agents` by SShadowS.

### Step 2: Build the Darwin Binary (macOS)

The plugin is distributed with Linux and Windows binaries only. For macOS, build the wrapper from source:

#### 2.1 Install Go (if not already installed)

```bash
brew install go
```

Verify:
```bash
go version
# Output: go version go1.26.3 darwin/arm64 (or similar)
```

#### 2.2 Clone and Build

```bash
# Clone the repository
git clone https://github.com/SShadowS/al-lsp-for-agents /tmp/al-lsp-src

# Build for darwin/arm64
cd /tmp/al-lsp-src/al-language-server-go
GOOS=darwin GOARCH=arm64 go build -o al-lsp-wrapper-darwin .

# Verify the binary
file al-lsp-wrapper-darwin
# Output: al-lsp-wrapper-darwin: Mach-O 64-bit executable arm64
```

#### 2.3 Deploy the Binary

Replace the Linux binary in the Claude Code plugin cache:

```bash
# Copy the darwin binary into the plugin cache
cp /tmp/al-lsp-src/al-language-server-go/al-lsp-wrapper-darwin \
   ~/.claude/plugins/cache/al-lsp-for-agents/al-language-server-go-linux/1.11.3/bin/al-lsp-wrapper

# Ensure it's executable
chmod +x ~/.claude/plugins/cache/al-lsp-for-agents/al-language-server-go-linux/1.11.3/bin/al-lsp-wrapper

# Verify
file ~/.claude/plugins/cache/al-lsp-for-agents/al-language-server-go-linux/1.11.3/bin/al-lsp-wrapper
# Output: ... Mach-O 64-bit executable arm64
```

---

## Configuration

### Claude Code Settings

The `.lsp.json` configuration file is automatically created by the plugin at:

```
~/.claude/plugins/cache/al-lsp-for-agents/al-language-server-go-linux/1.11.3/.lsp.json
```

Default configuration:

```json
{
  "al": {
    "command": "${CLAUDE_PLUGIN_ROOT}/bin/al-lsp-wrapper",
    "args": ["--launcher", "claude-code"],
    "extensionToLanguage": {
      ".al": "al",
      ".dal": "al"
    },
    "transport": "stdio",
    "initializationOptions": {},
    "settings": {},
    "maxRestarts": 3
  }
}
```

**Key settings:**

- `command` — Path to the wrapper binary (auto-resolves `${CLAUDE_PLUGIN_ROOT}`)
- `args` — `--launcher claude-code` identifies this as a Claude Code client
- `transport` — `stdio` is the standard LSP transport
- `maxRestarts` — Automatically restart the server if it crashes (up to 3 times)

### Environment Variables

Set this environment variable in the shell that launches Claude Code to enable LSP tools:

```bash
export ENABLE_LSP_TOOL=1
```

This must be set **before** launching Claude Code for the first time in that shell session.

**Bash/Zsh (add to ~/.zshrc or ~/.bashrc):**

```bash
export ENABLE_LSP_TOOL=1
```

Then restart your shell or run:

```bash
source ~/.zshrc
```

---

## Activation & Startup

### First Time Setup

1. **Set the environment variable:**
   ```bash
   export ENABLE_LSP_TOOL=1
   ```

2. **Launch Claude Code:**
   ```bash
   claude-code
   ```

3. **Verify the plugin loaded:**
   - Run `/plugins` in Claude Code
   - Confirm `al-lsp-for-agents` is listed as **active**

4. **Test on an AL file:**
   - Open any `.al` file from your project
   - Hover over a table or field name — should show type information
   - No errors in Claude Code console

### Subsequent Sessions

As long as `ENABLE_LSP_TOOL=1` is exported in your shell, the LSP server will start automatically when you open an AL file.

---

## Usage

### Hover Information

Position your cursor over any AL symbol and hover to see:

- **Type information** — Table name, field type, size
- **Field definitions** — Available fields and their data types
- **Procedure signatures** — Parameter names, return types
- **Comments** — Documentation from the source code

### Go-to-Definition

**Command:** Cmd+Click (macOS) or Ctrl+Click (Linux/Windows) on a symbol

Navigate to the source definition of:
- Tables and table extensions
- Pages and page extensions
- Fields and variables
- Procedures and functions
- Codeunits and reports

### Find References

**Command:** Right-click symbol → "Find All References" (or use LSP tool directly)

Locate all usages of:
- Fields in triggers or procedures
- Procedures called from other codeunits
- Global variables and constants
- Tables referenced in field relations

### Symbol Search

Use Claude Code's symbol search to find AL objects by name.

### Call Hierarchy (with Rust Sidecar)

If the `al-call-hierarchy` Rust sidecar is compiled, inspect:
- **Incoming calls** — Which procedures call this one
- **Outgoing calls** — Which procedures this one calls
- **Code lens** — Reference counts in the editor margin

---

## Troubleshooting

### Issue: "exec format error" when starting Claude Code

**Cause:** The Linux binary is still in the wrapper path; the darwin build wasn't deployed.

**Solution:**

1. Verify the binary was replaced:
   ```bash
   file ~/.claude/plugins/cache/al-lsp-for-agents/al-language-server-go-linux/1.11.3/bin/al-lsp-wrapper
   # Should output: Mach-O 64-bit executable arm64
   ```

2. If it still shows `ELF` or `linux`, re-run the deployment step above.

3. Restart Claude Code.

### Issue: LSP tools not available in Claude Code UI

**Cause:** `ENABLE_LSP_TOOL=1` was not set before launching Claude Code.

**Solution:**

1. Ensure the env var is set:
   ```bash
   echo $ENABLE_LSP_TOOL
   # Should output: 1
   ```

2. If empty, set it and restart Claude Code:
   ```bash
   export ENABLE_LSP_TOOL=1
   claude-code
   ```

3. Check `/plugins` to confirm the plugin loaded.

### Issue: Hover shows no information or "symbol not found"

**Cause:** The AL Language Server hasn't indexed the project yet, or the symbol is in a dependency.

**Solution:**

1. Wait 5–10 seconds after opening the first AL file (indexing takes time).
2. Restart Claude Code.
3. Check that the project's `.alpackages/` directory is populated with dependencies.

### Issue: "Cannot find AL extension"

**Cause:** The wrapper can't locate the VS Code AL extension at `~/.vscode/extensions/`.

**Solution:**

1. Verify the extension is installed:
   ```bash
   ls ~/.vscode/extensions/ms-dynamics-smb.al-*/
   ```

2. If missing, install it in VS Code: Extensions → Search "AL" → Install "AL Language" by Microsoft Dynamics.

3. Manually specify the path (advanced):
   ```bash
   # Run the wrapper with explicit path
   /path/to/al-lsp-wrapper -al-extension-path /path/to/ms-dynamics-smb.al-17.0.2273547
   ```

### Issue: Wrapper crashes immediately

**Cause:** The darwin binary is corrupted or built for the wrong architecture.

**Solution:**

1. Check the binary:
   ```bash
   file ~/.claude/plugins/cache/al-lsp-for-agents/al-language-server-go-linux/1.11.3/bin/al-lsp-wrapper
   # Must be: Mach-O 64-bit executable arm64
   ```

2. If it shows x86-64, rebuild with `GOARCH=arm64`:
   ```bash
   cd /tmp/al-lsp-src/al-language-server-go
   GOOS=darwin GOARCH=arm64 go build -o al-lsp-wrapper-darwin .
   ```

3. Redeploy the binary.

### Issue: AL Language Server DLLs not found

**Cause:** The VS Code AL extension's platform-specific binaries are missing.

**Solution:**

1. Check for darwin binaries:
   ```bash
   ls ~/.vscode/extensions/ms-dynamics-smb.al-17.0.2273547/bin/darwin/
   # Should show ~350 .dll files
   ```

2. If empty, reinstall the AL extension in VS Code:
   - Uninstall: Extensions → Installed → AL Language → Uninstall
   - Reinstall: Extensions → Search "AL" → Install

### Viewing Logs

**Claude Code LSP Logs:**

```bash
ls -la ~/.claude/logs/
# Look for lsp_*.log files
```

**AL Language Server Logs:**

```bash
tail -f ~/.vscode/extensions/ms-dynamics-smb.al-*/bin/darwin/EditorServices.log
```

---

## Advanced Configuration

### Specify a Different AL Extension Path

If you have multiple AL extension versions installed or want to use a prerelease:

```bash
# Build wrapper with explicit path
/path/to/al-lsp-wrapper \
  -al-extension-path /path/to/custom/al-extension \
  --launcher claude-code
```

### Enable Debug Output

The wrapper accepts debug logging (if compiled with debug flags):

```bash
# Check available flags
~/.claude/plugins/cache/al-lsp-for-agents/al-language-server-go-linux/1.11.3/bin/al-lsp-wrapper --help
```

### Use Prerelease AL Extension

To use the prerelease version of the AL extension instead of release:

```bash
/path/to/al-lsp-wrapper \
  -al-extension-channel prerelease \
  --launcher claude-code
```

---

## Building the Rust Sidecar (Optional)

The `al-call-hierarchy` sidecar provides call hierarchy and code lens features. To build it:

```bash
# Requires Rust toolchain
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

cd /tmp/al-lsp-src/al-call-hierarchy
cargo build --release

# Copy to plugin cache
cp target/release/al-call-hierarchy \
   ~/.claude/plugins/cache/al-lsp-for-agents/al-language-server-go-linux/1.11.3/bin/
```

---

## Platform Support

| Platform | Status | Notes |
|----------|--------|-------|
| **macOS (arm64)** | ✅ Supported (this guide) | Build from source required |
| **macOS (x86-64)** | ✅ Supported | Requires `GOARCH=amd64` build |
| **Linux (x64)** | ✅ Supported | Pre-built binary available |
| **Windows** | ✅ Supported | Pre-built binary available |

---

## References

- **Official Repository:** https://github.com/SShadowS/al-lsp-for-agents
- **MS AL Language Extension:** https://marketplace.visualstudio.com/items?itemName=ms-dynamics-smb.al
- **LSP Specification:** https://microsoft.github.io/language-server-protocol/
- **AL Language Documentation:** https://learn.microsoft.com/en-us/dynamics365/business-central/dev-itpro/developer/devenv-dev-overview

---

## Version History

| Date | Version | Changes |
|------|---------|---------|
| 2026-05-27 | 1.11.3 | Initial documentation; macOS build guide |

---

## Support & Contribution

For issues or feature requests with the LSP server itself, visit the [al-lsp-for-agents GitHub repository](https://github.com/SShadowS/al-lsp-for-agents/issues).

For issues specific to this project's setup, refer to the troubleshooting section above or check the project's development notes in `.dev/`.
