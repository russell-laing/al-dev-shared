---
name: al-dev-review
description: >-
  Analyse the most recent Claude Code session for friction
  patterns in the profile-claude-al-dev plugin. Reads the
  latest session transcript for the current project, extracts
  signals, spawns an analyst agent, and writes a structured
  findings report to .dev/ with file-specific improvement
  recommendations. Manually triggered — run at the end of a
  session you want to review.
---

# Skill: /al-dev-review

Analyse the most recent session and produce improvement
recommendations for the plugin.

---

## Step 1 — Locate Session JSONL & Detect Repo Context

Derive the project hash from the current working directory and
find the most recently modified session file. Detect if running
in the claude-configs plugin repo itself:

```bash
PROJECT_HASH=$(pwd | tr '/' '-')
JSONL=$(ls -t ~/.claude/projects/$PROJECT_HASH/*.jsonl \
  2>/dev/null | head -1)
if [ -z "$JSONL" ]; then
  echo "No session files found."
  echo "Expected: ~/.claude/projects/$PROJECT_HASH/"
  exit 1
fi
echo "Analysing: $JSONL"

# Detect if running in claude-configs repo itself
IS_PLUGIN_REPO=false
if [ -f "./CLAUDE.md" ] && [ -d "./profile-claude-al-dev" ]; then
  IS_PLUGIN_REPO=true
  echo "Detected: Running in claude-configs plugin repository"
fi
```

---

## Step 2 — Extract Session Signals

Save the extraction script to a temp file, then run it:

```bash
cat > /tmp/al-dev-extract.py << 'EOF'
import json, sys, re

REJECTION_WORDS = [
    'wrong', 'redo', 'not what i', 'incorrect',
    'try again', "that's not", 'that is not',
    'not what i asked', 'start over', 'that was not',
    "didn't", "doesn't", 'no not'
]
SHORT_REPLY = re.compile(r'^.{1,15}$', re.DOTALL)

jsonl_file = sys.argv[1]

signals = {
    'file': jsonl_file,
    'skills_invoked': {},
    'tool_errors': [],
    'human_messages': [],
    'rejection_signals': [],
    'clarification_turns': {}
}

current_skill = None
pending_tool_uses = {}

with open(jsonl_file) as f:
    for i, line in enumerate(f):
        try:
            obj = json.loads(line)
        except Exception:
            continue

        t = obj.get('type', '')

        if t == 'assistant':
            skill = obj.get('attributionSkill')
            if skill:
                current_skill = skill
                signals['skills_invoked'][skill] = \
                    signals['skills_invoked'].get(skill, 0) + 1
            msg = obj.get('message', {})
            content = msg.get('content', [])
            if isinstance(content, list):
                for block in content:
                    if not isinstance(block, dict):
                        continue
                    if block.get('type') == 'tool_use':
                        name = block.get('name', '')
                        tool_id = block.get('id', '')
                        pending_tool_uses[tool_id] = name
                        if name == 'Skill':
                            sn = block.get('input', {}).get('skill', '')
                            if sn:
                                signals['skills_invoked'][sn] = \
                                    signals['skills_invoked'].get(sn, 0) + 1

        elif t == 'user':
            if obj.get('toolUseResult'):
                msg = obj.get('message', {})
                content = msg.get('content', [])
                if isinstance(content, list):
                    for block in content:
                        if not isinstance(block, dict):
                            continue
                        if (block.get('type') == 'tool_result'
                                and block.get('is_error')):
                            tid = block.get('tool_use_id', '')
                            tname = pending_tool_uses.get(tid, 'unknown')
                            signals['tool_errors'].append({
                                'line': i,
                                'skill': current_skill,
                                'tool_name': tname,
                                'content': str(
                                    block.get('content', ''))[:300]
                            })
            elif not obj.get('isMeta'):
                msg = obj.get('message', {})
                content = msg.get('content', '')
                text = ''
                if isinstance(content, str):
                    text = content.strip()
                elif isinstance(content, list):
                    for block in content:
                        if (isinstance(block, dict)
                                and block.get('type') == 'text'):
                            text = block.get('text', '').strip()
                            break

                if not text or text.startswith('<') or len(text) < 2:
                    continue

                entry = {
                    'line': i,
                    'text': text[:300],
                    'skill': current_skill
                }
                signals['human_messages'].append(entry)

                text_lower = text.lower()
                for word in REJECTION_WORDS:
                    if word in text_lower:
                        signals['rejection_signals'].append(entry)
                        break

                if current_skill and SHORT_REPLY.match(text.strip()):
                    k = current_skill
                    if k not in signals['clarification_turns']:
                        signals['clarification_turns'][k] = []
                    signals['clarification_turns'][k].append(entry)

print(json.dumps(signals, indent=2))
EOF

python3 /tmp/al-dev-extract.py "$JSONL" > /tmp/signals.json
echo "Extraction complete. Skills detected:"
python3 << 'EOF'
import json
with open('/tmp/signals.json') as f:
    d = json.load(f)
    for k, v in sorted(d['skills_invoked'].items()):
        print(f'  {k}: {v} turns')
EOF
```

---

## Step 3 — Spawn Analyst Agent

```text
Agent tool:
  agent: al-dev-session-analyst
  description: "Session analysis: [basename of JSONL file]"

Prompt:
  "Analyse the session transcript signals below and produce
  a findings report.

  SIGNALS_JSON:
  [paste full JSON output from $SIGNALS]

  REPO_CONTEXT:
  This analysis is running in the claude-configs plugin repository itself.
  Recommendations should target the PROJECT-LEVEL CLAUDE.md and
  project-specific files, NOT plugin profile-level CLAUDE.md files.
  The plugin profiles (profile-claude-al-dev, profile-claude-vault)
  are third-party and read-only in this repo.

  PLUGIN_SOURCE: ~/claude-configs/profile-claude-al-dev

  OUTPUT_FILE: .dev/[date +%Y-%m-%d]-al-dev-review-findings.md

  Follow the al-dev-session-analyst agent instructions exactly."
```

---

## Step 4 — Present Summary

Once the agent writes the findings file, present to the user:

```
Session review complete → .dev/[date]-al-dev-review-findings.md

Issues found: N high, N medium, N low
Top priority: [highest severity finding title]

[If zero issues:]
No significant friction detected in this session.
```
