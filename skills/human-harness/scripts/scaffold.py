#!/usr/bin/env python3
"""Create harness files from templates. Creates missing files only; never overwrites.
  scaffold.py <project-name>   trunk harness in ./harness
  scaffold.py --branch         branch harness in ./harness/branches/<branch>/ (needs an existing trunk harness)"""
import datetime
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from hctx import Ctx, detect_trunk, find_root, git  # noqa: E402

TEMPLATES = Path(__file__).resolve().parent.parent / "templates"
GITIGNORE = ["harness/_holdout_staging/", "harness/.logs/"]


def fill(src_dir, dest_dir, subs):
    created = []
    for t in sorted(p for p in src_dir.iterdir() if p.is_file()):
        dest = dest_dir / t.name
        if not dest.exists():
            text = t.read_text()
            for k, v in subs.items():
                text = text.replace("{{" + k + "}}", v)
            dest.write_text(text)
            created.append(str(dest.relative_to(Path.cwd())))
    return created


def trunk(name):
    root = Path.cwd()
    h = root / "harness"
    is_git = git(root, "rev-parse", "--is-inside-work-tree") == "true"
    tr = detect_trunk(root) if is_git else "main"
    cur = git(root, "rev-parse", "--abbrev-ref", "HEAD") if is_git else None
    (h / "checks").mkdir(parents=True, exist_ok=True)
    (h / "_holdout_staging").mkdir(exist_ok=True)
    created = fill(TEMPLATES, h, {"NAME": name, "DATE": datetime.date.today().isoformat(), "TRUNK": tr})
    wrapper = h / "verify"
    if not wrapper.exists():
        wrapper.write_text('#!/usr/bin/env bash\nexec python3 "$HOME/.claude/skills/human-harness/scripts/verify.py" "$@"\n')
        os.chmod(wrapper, 0o755)
        created.append("harness/verify")
    gi = root / ".gitignore"
    lines = gi.read_text().splitlines() if gi.exists() else []
    missing = [l for l in GITIGNORE if l not in lines]
    if missing:
        with gi.open("a") as f:
            f.write(("\n" if lines and lines[-1] else "") + "\n".join(missing) + "\n")
    print(f"Trunk harness ready (trunk = {tr}). Created: {', '.join(created) or 'nothing (all existed)'}")
    if cur and cur not in ("HEAD", tr):
        print(f"WARNING: you are on '{cur}', not trunk '{tr}'. The trunk harness reaches {tr} only when this branch is merged.")


def branch():
    root = find_root(Path.cwd())
    if not root or not (root / "harness" / "checks.toml").is_file():
        sys.exit("No trunk harness found. Run the trunk scaffold (and the init interview) on the trunk first.")
    ctx = Ctx(root)
    if ctx.on_trunk:
        sys.exit(f"You are on the trunk ({ctx.trunk}); a branch harness is only for other branches.")
    ctx.bdir.mkdir(parents=True, exist_ok=True)
    (ctx.h / "checks" / ctx.slug).mkdir(parents=True, exist_ok=True)
    os.chdir(root)
    created = fill(TEMPLATES / "branch", ctx.bdir, {"BRANCH": ctx.branch, "SLUG": ctx.slug, "TRUNK": ctx.trunk,
                                                    "DATE": datetime.date.today().isoformat()})
    print(f"Branch harness ready for {ctx.branch} in {ctx.bdir.relative_to(root)}. "
          f"Created: {', '.join(created) or 'nothing (all existed)'}")


def main():
    if sys.argv[1:] == ["--branch"]:
        return branch()
    if len(sys.argv) != 2 or not re.fullmatch(r"[\w.-]+", sys.argv[1]):
        sys.exit(__doc__)
    trunk(sys.argv[1])


if __name__ == "__main__":
    main()
