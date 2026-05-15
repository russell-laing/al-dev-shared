# al-dev-commit OOXML Guardrails Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prevent corrupted OOXML files from being committed through `/al-dev-commit` and require explicit human confirmation for risky mixed `.al` + `.docx` commit sets.

**Architecture:** Apply targeted, additive changes in two existing files only: the commit agent instructions (`analysis` + `execute`) and the commit orchestrator skill gate. The agent gets robust NUL-safe staged-file scanning, a canonical extension policy, and a hard ZIP-integrity block. The orchestrator adds an explicit acknowledgement checkpoint before execution dispatch when mixed `.al` and `.docx` files are staged.

**Tech Stack:** Markdown skill/agent docs, Bash (`git -C`, NUL-safe loops), Python stdlib `zipfile`, `rg`, `wc`.

---

## File Map

| File | Responsibility |
| --- | --- |
| `profile-al-dev-shared/agents/al-dev-commit-agent.md` | Add robust OOXML staged-file detection, `.gitattributes` warning logic, mixed `.al` + `.docx` warning output in analysis, and hard ZIP validation in execute |
| `profile-al-dev-shared/skills/al-dev-commit/SKILL.md` | Add explicit mixed `.al` + `.docx` acknowledgement gate between message approval and execute dispatch |

---

### Task 1: Add canonical staged-file detection primitives in analysis phase

**Files:**
- Modify: `profile-al-dev-shared/agents/al-dev-commit-agent.md` (analysis phase, before grouping/warnings output)

- [ ] **Step 1: Write failing verification check for unsafe loops**

```bash
rg -n "for f in \\$\\(git .*diff --cached --name-only.*\\)" \
  /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-commit-agent.md
```

Expected: at least one match showing unsafe `for f in $(...)` pattern still exists.

- [ ] **Step 2: Write failing verification check for missing NUL-safe staged scan guidance**

```bash
rg -n "name-only -z|read -r -d ''|OOXML_EXTENSIONS" \
  /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-commit-agent.md
```

Expected: no results for all three markers.

- [ ] **Step 3: Insert canonical staged-file scanning block in analysis phase**

Insert this block in analysis instructions after staged file listing and before grouping logic:

```markdown
### Step 4.5 — Build staged-file sets (NUL-safe)

Use one canonical extension set for OOXML policy checks:

```bash
OOXML_EXTENSIONS_REGEX='\\.(docx|xlsx|pptx|odt)$'
```

Build staged-file sets without word-splitting:

```bash
STAGED_AL=()
STAGED_DOCX=()
STAGED_OOXML=()

while IFS= read -r -d '' f; do
  case "$f" in
    *.al) STAGED_AL+=("$f") ;;
  esac
  case "$f" in
    *.docx) STAGED_DOCX+=("$f") ;;
  esac
  case "$f" in
    *.docx|*.xlsx|*.pptx|*.odt) STAGED_OOXML+=("$f") ;;
  esac
done < <(git -C "$REPO" diff --cached --name-only -z --diff-filter=ACMRDT)
```
```

- [ ] **Step 4: Run verification check to confirm insertion**

```bash
rg -n "Step 4.5 — Build staged-file sets|OOXML_EXTENSIONS_REGEX|read -r -d ''|name-only -z" \
  /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-commit-agent.md
```

Expected: all markers present at least once.

- [ ] **Step 5: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add profile-al-dev-shared/agents/al-dev-commit-agent.md
git -C /Users/russelllaing/al-dev-shared commit -m "$(cat <<'EOF'
🔧 refactor(al-dev-commit): add NUL-safe staged file set construction for analysis
EOF
)"
```

---

### Task 2: Add analysis warnings for `.gitattributes` gaps and mixed `.al` + `.docx`

**Files:**
- Modify: `profile-al-dev-shared/agents/al-dev-commit-agent.md` (analysis phase warnings section)

- [ ] **Step 1: Write failing check for missing `.gitattributes` warning markers**

```bash
rg -n "gitattributes|\\*\\.docx\\s+binary|\\*\\.xlsx\\s+binary|\\*\\.pptx\\s+binary|\\*\\.odt\\s+binary" \
  /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-commit-agent.md
```

Expected: no comprehensive policy warning block found.

- [ ] **Step 2: Add `.gitattributes` warning-only logic in analysis**

Add this analysis-phase guidance:

```markdown
### Step 6.7 — `.gitattributes` OOXML advisory (warn only)

If `STAGED_OOXML` is non-empty, inspect `.gitattributes`:

```bash
GITATTR="$REPO/.gitattributes"
MISSING_BINARY_PATTERNS=()

if [ "${#STAGED_OOXML[@]}" -gt 0 ]; then
  if [ ! -f "$GITATTR" ]; then
    MISSING_BINARY_PATTERNS+=("*.docx binary" "*.xlsx binary" "*.pptx binary" "*.odt binary")
  else
    grep -Eq '^\\*\\.docx[[:space:]]+binary$' "$GITATTR" || MISSING_BINARY_PATTERNS+=("*.docx binary")
    grep -Eq '^\\*\\.xlsx[[:space:]]+binary$' "$GITATTR" || MISSING_BINARY_PATTERNS+=("*.xlsx binary")
    grep -Eq '^\\*\\.pptx[[:space:]]+binary$' "$GITATTR" || MISSING_BINARY_PATTERNS+=("*.pptx binary")
    grep -Eq '^\\*\\.odt[[:space:]]+binary$' "$GITATTR" || MISSING_BINARY_PATTERNS+=("*.odt binary")
  fi
fi
```

If `MISSING_BINARY_PATTERNS` is non-empty, add one `WARNINGS` item that lists each missing line and states this is advisory only.
```

- [ ] **Step 3: Add mixed `.al` + `.docx` analysis flag output**

Add this analysis-phase guidance:

```markdown
### Step 6.8 — Mixed `.al` + `.docx` risk flag

If both `STAGED_AL` and `STAGED_DOCX` are non-empty, add a `WARNINGS` entry:

```text
MIXED_AL_DOCX: This staged set contains both .al and .docx files.
AL files: <comma-separated list>
DOCX files: <comma-separated list>
Verify each .docx was saved from Microsoft Word and run OOXML ZIP validation before execute.
```
```

- [ ] **Step 4: Verify warnings are now documented**

```bash
rg -n "Step 6.7|Step 6.8|MIXED_AL_DOCX|MISSING_BINARY_PATTERNS|advisory only" \
  /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-commit-agent.md
```

Expected: all markers present.

- [ ] **Step 5: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add profile-al-dev-shared/agents/al-dev-commit-agent.md
git -C /Users/russelllaing/al-dev-shared commit -m "$(cat <<'EOF'
⚠️ feat(al-dev-commit): warn on OOXML gitattributes gaps and mixed al-docx staging
EOF
)"
```

---

### Task 3: Add execute-phase hard block for OOXML ZIP integrity

**Files:**
- Modify: `profile-al-dev-shared/agents/al-dev-commit-agent.md` (execute phase, before `git commit`)

- [ ] **Step 1: Write failing check for missing hard-block markers**

```bash
rg -n "COMMIT BLOCKED: One or more staged OOXML files failed ZIP integrity validation|testzip\\(\\)|CORRUPT_OOXML" \
  /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-commit-agent.md
```

Expected: no hard-block section with these markers yet.

- [ ] **Step 2: Insert execute pre-commit OOXML validation block**

Insert this block at execute phase pre-flight, before commit execution:

```markdown
### Step 1.5 — OOXML ZIP integrity gate (hard block)

Before any `git commit`, validate all staged OOXML files:

```bash
CORRUPT_OOXML=()

while IFS= read -r -d '' f; do
  case "$f" in
    *.docx|*.xlsx|*.pptx|*.odt)
      ABS="$REPO/$f"
      RESULT=$(python3 - "$ABS" <<'PY'
import sys, zipfile
path = sys.argv[1]
try:
    with zipfile.ZipFile(path) as z:
        bad = z.testzip()
        if bad is not None:
            print(f"BAD_ENTRY:{bad}")
            raise SystemExit(1)
    print("OK")
except Exception as e:
    print(f"ERROR:{e}")
    raise SystemExit(1)
PY
      2>&1) || CORRUPT_OOXML+=("$f :: $RESULT")
      ;;
  esac
done < <(git -C "$REPO" diff --cached --name-only -z --diff-filter=ACMRDT)

if [ "${#CORRUPT_OOXML[@]}" -gt 0 ]; then
  echo "COMMIT BLOCKED: One or more staged OOXML files failed ZIP integrity validation."
  printf '%s\n' "${CORRUPT_OOXML[@]}"
  exit 1
fi
```
```

- [ ] **Step 3: Verify hard-block section exists**

```bash
rg -n "Step 1.5 — OOXML ZIP integrity gate|COMMIT BLOCKED: One or more staged OOXML files failed ZIP integrity validation|BAD_ENTRY:|diff --cached --name-only -z" \
  /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-commit-agent.md
```

Expected: all markers present exactly once.

- [ ] **Step 4: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add profile-al-dev-shared/agents/al-dev-commit-agent.md
git -C /Users/russelllaing/al-dev-shared commit -m "$(cat <<'EOF'
🔒 feat(al-dev-commit): block commits when staged OOXML fails zip integrity
EOF
)"
```

---

### Task 4: Add orchestrator acknowledgement gate for mixed `.al` + `.docx`

**Files:**
- Modify: `profile-al-dev-shared/skills/al-dev-commit/SKILL.md` (between Step 9 and Step 10)

- [ ] **Step 1: Write failing check for missing mixed-file ack gate**

```bash
rg -n "MIXED_AL_DOCX|explicit acknowledgement|yes / no|before Step 10" \
  /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-commit/SKILL.md
```

Expected: no explicit mixed `.al` + `.docx` acknowledge gate exists.

- [ ] **Step 2: Insert new gate section after commit-message confirmations**

Insert this section after current Step 9 and before current Step 10:

```markdown
## Step 9.5 — Mixed `.al` + `.docx` acknowledgement gate

Inspect analysis `WARNINGS` for a `MIXED_AL_DOCX` entry.

If present, show:

```text
⚠️  MIXED AL + DOCX STAGING DETECTED

This commit plan includes both `.al` source files and `.docx` layout files.
High-risk pattern: automated tool rewrites of Word layouts can produce malformed OOXML.

Confirm all `.docx` files were edited and saved in Microsoft Word (not scripted),
and that OOXML ZIP validation has passed.

Proceed to execution? (yes / no)
```

User response:
- `yes` → continue to Step 10
- `no` → stop; leave staged files unchanged

If no `MIXED_AL_DOCX` warning exists, continue directly to Step 10.
```

- [ ] **Step 3: Renumber downstream section headings**

Rename:
- `## Step 10 — Dispatch Execution Agent` → `## Step 10 — Dispatch Execution Agent` (unchanged number, keep section order with new 9.5 inserted)
- `## Step 11 — Summary` remains unchanged

Verify the new sequence in file order: Step 9 → Step 9.5 → Step 10 → Step 11.

- [ ] **Step 4: Verify gate insertion**

```bash
rg -n "^## Step 9 —|^## Step 9.5 —|^## Step 10 —|^## Step 11 —|MIXED_AL_DOCX|Proceed to execution\\? \\(yes / no\\)" \
  /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-commit/SKILL.md
```

Expected: all headings and gate prompt markers found in order.

- [ ] **Step 5: Commit**

```bash
git -C /Users/russelllaing/al-dev-shared add profile-al-dev-shared/skills/al-dev-commit/SKILL.md
git -C /Users/russelllaing/al-dev-shared commit -m "$(cat <<'EOF'
🛡️ feat(al-dev-commit): require explicit mixed al-docx acknowledgement before execute
EOF
)"
```

---

### Task 5: End-to-end verification and plan closeout commit

**Files:**
- Modify: `profile-al-dev-shared/agents/al-dev-commit-agent.md`
- Modify: `profile-al-dev-shared/skills/al-dev-commit/SKILL.md`

- [ ] **Step 1: Run structural verification checks**

```bash
rg -n "Step 4.5 — Build staged-file sets|Step 6.7 — \\.gitattributes OOXML advisory|Step 6.8 — Mixed \\.al \\+ \\.docx risk flag|Step 1.5 — OOXML ZIP integrity gate" \
  /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-commit-agent.md
rg -n "^## Step 9.5 — Mixed `\\.al` \\+ `\\.docx` acknowledgement gate|MIXED_AL_DOCX|Proceed to execution\\? \\(yes / no\\)" \
  /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-commit/SKILL.md
```

Expected: all new sections present.

- [ ] **Step 2: Run forbidden-pattern scan on changed files**

```bash
rg -n "\\[date\\]|YYYY-MM-DD|for f in \\$\\(git .*diff --cached --name-only.*\\)" \
  /Users/russelllaing/al-dev-shared/profile-al-dev-shared/agents/al-dev-commit-agent.md \
  /Users/russelllaing/al-dev-shared/profile-al-dev-shared/skills/al-dev-commit/SKILL.md
```

Expected: no matches.

- [ ] **Step 3: Verify only intended files changed**

```bash
git -C /Users/russelllaing/al-dev-shared --no-pager status --short
```

Expected: only the two targeted files are modified/staged for this change set.

- [ ] **Step 4: Commit final integrated change set**

```bash
git -C /Users/russelllaing/al-dev-shared add \
  profile-al-dev-shared/agents/al-dev-commit-agent.md \
  profile-al-dev-shared/skills/al-dev-commit/SKILL.md
git -C /Users/russelllaing/al-dev-shared commit -m "$(cat <<'EOF'
🐛 fix(al-dev-commit): enforce robust OOXML safety checks and mixed-file execution gate
EOF
)"
```
