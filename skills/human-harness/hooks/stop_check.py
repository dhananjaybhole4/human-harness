#!/usr/bin/env python3
"""Stop: in projects with harness/, block finishing if code changed after the current scope's STATUS.md
(trunk: harness/STATUS.md, branch: harness/branches/<branch>/STATUS.md) was last updated.
Uses git (uncommitted changes + commit times), so switching branches doesn't count as a change."""
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from hctx import Ctx, git  # noqa: E402

CODE_EXT = {".py", ".ipynb", ".js", ".ts", ".tsx", ".sql", ".sh", ".r", ".R", ".java", ".go", ".rs", ".c", ".cpp", ".h"}
SKIP = {".git", "harness", "node_modules", ".venv", "venv", "__pycache__", ".pytest_cache", ".mypy_cache",
        ".ipynb_checkpoints", "graphify-out", "dist", "build", "data", ".claude"}
PATHSPEC = [f":(glob)**/*{e}" for e in CODE_EXT] + [":(exclude)harness"]


def changed_git(ctx, status):
    smt = status.stat().st_mtime if status.is_file() else 0
    for line in (git(ctx.root, "status", "--porcelain", "--untracked-files=all") or "").splitlines():
        path = line[3:].split(" -> ")[-1].strip('"')
        f = ctx.root / path
        if not path.startswith("harness/") and f.suffix in CODE_EXT and f.is_file() and f.stat().st_mtime > smt + 1:
            return path
    if not status.is_file():  # branch without harness: any code commit on this branch counts
        n = git(ctx.root, "rev-list", "--count", f"{ctx.trunk}..HEAD", "--", *PATHSPEC)
        return f"{n} commit(s) on this branch" if n and n != "0" else None
    code_ct = git(ctx.root, "log", "-1", "--format=%ct", "--", *PATHSPEC)
    st_ct = git(ctx.root, "log", "-1", "--format=%ct", "--", str(status.relative_to(ctx.root)))
    if code_ct and int(code_ct) > max(int(st_ct or 0), smt + 1):
        return "a commit after the last STATUS update"
    return None


def changed_walk(root, status):
    since = status.stat().st_mtime + 1
    seen = 0
    for dirpath, dirs, files in os.walk(root):
        dirs[:] = [x for x in dirs if x not in SKIP and not x.startswith(".")]
        for f in files:
            seen += 1
            p = os.path.join(dirpath, f)
            if Path(f).suffix in CODE_EXT and os.path.getmtime(p) > since:
                return os.path.relpath(p, root)
        if seen > 20000:
            return None
    return None


try:
    d = json.load(sys.stdin)
except Exception:
    sys.exit(0)
if d.get("stop_hook_active"):
    sys.exit(0)
root = Path(d.get("cwd") or ".")
if not (root / "harness" / "STATUS.md").is_file():
    sys.exit(0)
ctx = Ctx(root)
status = ctx.status
what = changed_git(ctx, status) if ctx.is_git else changed_walk(root, status)
if not what:
    sys.exit(0)
if not ctx.on_trunk and not ctx.branch_ready:
    reason = (f"human-harness: code changed on branch '{ctx.branch}' ({what}) but it has no branch harness. Run "
              "`python3 ~/.claude/skills/human-harness/scripts/scaffold.py --branch`, fill its STATUS.md (what this branch "
              "is for, done, next, not verified), and tell the owner to run `/human-harness init` for the branch interview.")
else:
    rel = status.relative_to(root)
    reason = (f"human-harness: code changed ({what}) after {rel} was last updated. Before finishing: overwrite {rel} "
              "(done / in progress / next / needs owner / not verified / last verify result), append decisions to the "
              "same scope's DECISIONS.md, update ARCHITECTURE notes if structure changed, and tell the owner in one line "
              "if an update-interview or postmortem trigger fired.")
print(json.dumps({"decision": "block", "reason": reason}))
