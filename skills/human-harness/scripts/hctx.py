"""Shared harness context (used by verify, scaffold and hooks): project root, trunk, current branch, scope paths.
Rule: trunk harness files are shared; a branch writes only in harness/branches/<slug>/."""
import re
import subprocess
import tomllib
from pathlib import Path

TRUNK_DOCS = {"STATUS.md", "DECISIONS.md", "ARCHITECTURE.md", "INTERVIEW.md"}


def git(root, *args):
    try:
        r = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return r.stdout.rstrip() if r.returncode == 0 else None  # rstrip only: porcelain lines start with a space


def slug(branch):
    return re.sub(r"[^\w.-]+", "-", branch).strip("-") or "branch"


def detect_trunk(root):
    ref = git(root, "symbolic-ref", "--short", "refs/remotes/origin/HEAD")
    if ref:
        return ref.split("/", 1)[-1]
    for b in ("main", "master"):
        if git(root, "rev-parse", "--verify", "--quiet", f"refs/heads/{b}") is not None:
            return b
    cur = git(root, "rev-parse", "--abbrev-ref", "HEAD")
    return cur if cur and cur != "HEAD" else "main"


def load_toml(path):
    try:
        with open(path, "rb") as f:
            return tomllib.load(f)
    except (OSError, tomllib.TOMLDecodeError):
        return {}


def find_root(start):
    start = Path(start).resolve()
    for d in [start, *start.parents]:
        if (d / "harness" / "checks.toml").is_file() or (d / "harness" / "STATUS.md").is_file():
            return d
    return None


class Ctx:
    def __init__(self, root):
        self.root = Path(root)
        self.h = self.root / "harness"
        self.cfg = load_toml(self.h / "checks.toml")
        self.is_git = git(self.root, "rev-parse", "--is-inside-work-tree") == "true"
        self.trunk = self.cfg.get("project", {}).get("trunk") or (detect_trunk(self.root) if self.is_git else "main")
        b = git(self.root, "rev-parse", "--abbrev-ref", "HEAD") if self.is_git else None
        self.branch = b if b and b != "HEAD" else None
        self.on_trunk = self.branch in (None, self.trunk)
        self.slug = None if self.on_trunk else slug(self.branch)
        self.bdir = None if self.on_trunk else self.h / "branches" / self.slug
        self.branch_ready = bool(self.bdir and (self.bdir / "STATUS.md").is_file())
        self.scope_dir = self.bdir if self.bdir else self.h
        self.status = self.scope_dir / "STATUS.md"
        self.suite = "main" if self.on_trunk else self.slug
        self.label = f"trunk ({self.trunk})" if self.on_trunk else f"branch {self.branch} (base {self.trunk})"

    def bcfg(self):
        return load_toml(self.bdir / "checks.toml") if self.branch_ready else {}

    def trunk_has_new_harness(self):
        """True if the trunk changed harness/ since this branch split off (branch should merge trunk in)."""
        if self.on_trunk or not self.is_git:
            return False
        r = subprocess.run(["git", "-C", str(self.root), "diff", "--quiet", f"HEAD...{self.trunk}", "--", "harness/"],
                           capture_output=True)
        return r.returncode == 1
