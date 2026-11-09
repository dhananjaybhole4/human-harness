#!/usr/bin/env python3
"""SessionStart: in projects with harness/, inject harness rules, BOUNDARIES and the current scope's STATUS
(trunk or branch) into context."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from hctx import Ctx  # noqa: E402

try:
    d = json.load(sys.stdin)
except Exception:
    d = {}
root = Path(d.get("cwd") or ".")
if not (root / "harness" / "STATUS.md").is_file():
    sys.exit(0)
ctx = Ctx(root)


def head(p, n=40):
    return "\n".join(p.read_text(errors="ignore").splitlines()[:n]) if p.is_file() else ""


parts = ["HARNESS ACTIVE (human-harness). Read harness/SPEC.md before building. Obey BOUNDARIES below. Changes to "
         "SPEC/BOUNDARIES/checks need owner approval first. Prove work with `harness/verify`. Suggest `/human-harness "
         "update` at milestones, repeated check failures, new unknowns or drift from SPEC; `/human-harness postmortem` "
         "after rework. Never touch ~/harness-holdouts or read harness/_holdout_staging."]
if ctx.on_trunk:
    parts.append(f"Scope: trunk ({ctx.trunk}). Keep harness/STATUS (overwrite), DECISIONS (append), ARCHITECTURE current.")
elif ctx.branch_ready:
    rel = ctx.bdir.relative_to(root)
    parts.append(f"Scope: branch '{ctx.branch}' (base {ctx.trunk}). Trunk SPEC/BOUNDARIES/checks still apply. Write harness "
                 f"updates ONLY in {rel}/ (STATUS, DECISIONS, INTERVIEW, ARCHITECTURE notes); trunk harness files change "
                 f"only via `/human-harness merge`. Branch checks go in harness/checks/{ctx.slug}/.")
    parts.append(f"--- {rel}/SPEC.md (head) ---\n" + head(ctx.bdir / "SPEC.md", 25))
else:
    parts.append(f"Scope: branch '{ctx.branch}' with NO branch harness yet. Trunk harness applies. Before building here, "
                 f"suggest the owner run `/human-harness init` (short branch interview; trunk context is already known).")
if ctx.trunk_has_new_harness():
    parts.append(f"NOTE: {ctx.trunk} has newer harness changes than this branch. Suggest merging {ctx.trunk} into it.")
parts.append("--- harness/BOUNDARIES.md ---\n" + head(ctx.h / "BOUNDARIES.md"))
status = ctx.status if ctx.status.is_file() else ctx.h / "STATUS.md"
parts.append(f"--- {status.relative_to(root)} ---\n" + head(status))
for hist in (ctx.h / ".holdout_history", ctx.scope_dir / ".holdout_history"):
    if hist.is_file() and hist.read_text().strip():
        parts.append("Last holdout run: " + hist.read_text().strip().splitlines()[-1])
        break
print(json.dumps({"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": "\n\n".join(parts)}}))
