#!/usr/bin/env bash
# Installs the human-harness skill into ~/.claude/skills and registers its 3 hooks in ~/.claude/settings.json.
# Safe to re-run: the skill is refreshed, hooks are added only once, settings.json is backed up first.
set -euo pipefail

SRC="$(cd "$(dirname "$0")" && pwd)/skills/human-harness"
DEST="$HOME/.claude/skills/human-harness"
SETTINGS="$HOME/.claude/settings.json"

command -v python3 >/dev/null || { echo "python3 (3.11+) is required"; exit 1; }
python3 -c 'import sys; sys.exit(sys.version_info < (3, 11))' || { echo "python3 3.11+ is required (tomllib)"; exit 1; }
command -v git >/dev/null || { echo "git is required"; exit 1; }
command -v openssl >/dev/null || echo "warning: openssl not found; holdout sealing (verify --seal) will not work"

mkdir -p "$(dirname "$DEST")"
rm -rf "$DEST"
cp -R "$SRC" "$DEST"
echo "skill installed -> $DEST"

[ -f "$SETTINGS" ] && cp "$SETTINGS" "$SETTINGS.bak.$(date +%s)"
python3 - "$SETTINGS" <<'EOF'
import json, sys
from pathlib import Path

path = Path(sys.argv[1])
cfg = json.loads(path.read_text()) if path.is_file() and path.read_text().strip() else {}
hooks = cfg.setdefault("hooks", {})
base = 'python3 "$HOME/.claude/skills/human-harness/hooks/{}"'
wanted = {
    "SessionStart": ("startup|resume|clear|compact", "session_start.py"),
    "PreToolUse": ("*", "guard.py"),
    "Stop": (None, "stop_check.py"),
}
for event, (matcher, script) in wanted.items():
    cmd = base.format(script)
    entries = hooks.setdefault(event, [])
    if any(h.get("command") == cmd for e in entries for h in e.get("hooks", [])):
        continue
    entry = {"hooks": [{"type": "command", "command": cmd}]}
    if matcher:
        entry["matcher"] = matcher
    entries.append(entry)
path.parent.mkdir(parents=True, exist_ok=True)
path.write_text(json.dumps(cfg, indent=2) + "\n")
print(f"hooks registered -> {path}")
EOF

echo "done. Restart Claude Code, open a project, and type: /human-harness"
