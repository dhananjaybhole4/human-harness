#!/usr/bin/env python3
"""PreToolUse guard for human-harness. Denies holdout access and owner-only commands; asks the owner before
changes to approved harness files, to Claude's own settings, and to trunk harness docs while on a branch."""
import json
import os
import re
import sys
from pathlib import Path

HOME = str(Path.home())
EDIT_TOOLS = {"Write", "Edit", "MultiEdit", "NotebookEdit"}
PROTECTED_TOP = {"SPEC.md", "BOUNDARIES.md", "checks.toml", "checks", "verify", ".lock", ".holdout_history"}
PROTECTED_BRANCH = {"SPEC.md", "checks.toml", ".holdout_history"}
TRUNK_DOCS = {"STATUS.md", "DECISIONS.md", "ARCHITECTURE.md", "INTERVIEW.md"}
BASH_PROT = re.compile(r"harness/(SPEC\.md|BOUNDARIES\.md|checks\.toml|checks/|\.lock)|harness/branches/[^/\s]+/(SPEC\.md|checks\.toml)"
                       r"|\.holdout_history|\.claude/(settings(\.local)?\.json|CLAUDE\.md)|skills/human-harness")
BASH_WRITE = re.compile(r">|\btee\b|\bsed\b[^|;&]*\s-i|\bperl\b[^|;&]*\s-i|\b(mv|rm|cp|truncate|chmod|ln|dd)\b"
                        r"|\bpython3?\b|\bgit\s+(checkout|restore|reset|rm|mv|apply|stash)\b")


def decide(decision, reason):
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": decision,
                                             "permissionDecisionReason": reason}}))
    sys.exit(0)


def harness_parts(p):
    """Return (project_root, parts after the last 'harness' dir) or (None, None)."""
    if "harness" not in p.parts:
        return None, None
    i = len(p.parts) - 1 - p.parts[::-1].index("harness")
    return Path(*p.parts[:i]), p.parts[i + 1:]


def edit_reason(path, cwd):
    if not path:
        return None
    p = Path(os.path.expanduser(path))
    p = (p if p.is_absolute() else Path(cwd) / p).resolve()
    s = str(p)
    if s.startswith(HOME + "/.claude/skills/human-harness/"):
        return "the human-harness skill itself"
    if p.name in ("settings.json", "settings.local.json") and p.parent.name == ".claude":
        return f"Claude settings ({s})"
    if s == HOME + "/.claude/CLAUDE.md":
        return "your global CLAUDE.md"
    root, rest = harness_parts(p)
    if not rest:
        return None
    rel = "harness/" + "/".join(rest)
    # existing approved files only: creating new files is fine (fingerprint catches new check files)
    if p.exists() and (rest[0] in PROTECTED_TOP or (rest[0] == "branches" and len(rest) >= 3 and rest[2] in PROTECTED_BRANCH)):
        return f"{rel} (owner-approved file)"
    if len(rest) == 1 and rest[0] in TRUNK_DOCS:
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
        from hctx import Ctx
        ctx = Ctx(root)
        if not ctx.on_trunk:
            return (f"trunk file {rel} while on branch '{ctx.branch}'. Branch work belongs in "
                    f"harness/branches/{ctx.slug}/; trunk docs change only when merging")
    return None


def main():
    try:
        d = json.load(sys.stdin)
    except Exception:
        return
    tool, ti = d.get("tool_name", ""), d.get("tool_input") or {}
    cwd = d.get("cwd") or os.getcwd()
    if tool in EDIT_TOOLS or tool == "Read":
        target = ti.get("file_path") or ti.get("notebook_path") or ""
    elif tool == "Bash":
        target = ti.get("command", "")
    else:
        target = json.dumps(ti)

    if "harness-holdouts" in target:
        decide("deny", "human-harness: the holdout vault is off-limits to the agent. Only the owner touches ~/harness-holdouts.")
    if tool == "Bash" and re.search(r"verify(\.py)?\b[^|;&]*--(holdout|seal|lock)\b", target):
        decide("deny", "human-harness: --holdout/--seal/--lock are owner-only. Ask the owner to run it in their own terminal.")
    if "_holdout_staging" in target and tool != "Write":
        decide("deny", "human-harness: harness/_holdout_staging is write-only for the agent. Never read holdout cases.")

    if tool in EDIT_TOOLS:
        why = edit_reason(target, cwd)
        if why:
            decide("ask", f"human-harness: Claude wants to change {why}. Approve only if Claude explained the change and "
                          f"you agree. If checks/SPEC/BOUNDARIES changed, run `harness/verify --lock` afterwards.")
    if tool == "Bash" and BASH_PROT.search(target) and BASH_WRITE.search(target):
        decide("ask", "human-harness: this shell command may modify an owner-approved harness file or Claude's settings. "
                      "Approve only if intended.")


if __name__ == "__main__":
    main()
