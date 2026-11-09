#!/usr/bin/env python3
"""Harness verifier (branch-aware).
Agent:  harness/verify [--only NAME ...] [--compare [REF]]
Owner only, own terminal:  --lock | --seal | --holdout
On a branch: runs trunk checks + this branch's checks; --seal/--holdout use this branch's suite as well."""
import argparse
import datetime
import getpass
import hashlib
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from hctx import Ctx, find_root, git, load_toml  # noqa: E402

VAULT = Path.home() / "harness-holdouts"
SKIP_DIRS = {".git", "__pycache__", ".venv", "venv", "node_modules", ".pytest_cache", ".mypy_cache", ".ipynb_checkpoints"}
TEXT_EXT = {".py", ".ipynb", ".js", ".ts", ".sql", ".sh", ".r", ".R", ".json", ".yaml", ".yml", ".toml", ".csv", ".txt", ".md"}
CIPHER = ["-aes-256-cbc", "-pbkdf2", "-iter", "200000"]
METRIC_RE = re.compile(r"^METRIC\s+(.+)$", re.M)


# ---------- helpers ----------
def owner_only(flag):
    if not (sys.stdin.isatty() and sys.stdout.isatty()):
        sys.exit(f"{flag} is owner-only: run it yourself in your own terminal.")


def tail(text, n):
    return "\n".join(text.strip().splitlines()[-n:])


def as_list(x):
    return [] if x is None else ([x] if isinstance(x, dict) else list(x))


def files_under(root, dirs, exts):
    for d in dirs:
        base = root / d
        if base.exists():
            for p in base.rglob("*"):
                if p.is_file() and p.suffix in exts and not (SKIP_DIRS & set(p.parts)):
                    yield p


def effective(ctx):
    """Trunk config merged with the current branch's config (checks/holdouts appended, settings overridden)."""
    t, b = ctx.cfg, ctx.bcfg()
    checks = [dict(c, scope="trunk") for c in t.get("check", [])] + [dict(c, scope=ctx.slug) for c in b.get("check", [])]
    holdouts = [dict({"suite": "main"}, **x, scope="trunk") for x in as_list(t.get("holdout"))]
    holdouts += [dict({"suite": ctx.slug}, **x, scope=ctx.slug) for x in as_list(b.get("holdout"))]
    docs = dict(t.get("docs", {}))
    if ctx.branch_ready:
        rel = ctx.bdir.relative_to(ctx.root)
        docs.update({f"{rel}/SPEC.md": 50, f"{rel}/STATUS.md": 30})
    docs.update(b.get("docs", {}))
    return {"checks": checks, "holdouts": holdouts, "docs": docs,
            "budget": {**t.get("budget", {}), **b.get("budget", {})},
            "hardcode": {**t.get("hardcode", {}), **b.get("hardcode", {})}}


def protected(root):
    h = root / "harness"
    files = [h / n for n in ("checks.toml", "SPEC.md", "BOUNDARIES.md")]
    if (h / "branches").is_dir():
        for bd in (h / "branches").iterdir():
            files += [bd / "SPEC.md", bd / "checks.toml"]
    if (h / "checks").is_dir():
        files += [p for p in (h / "checks").rglob("*") if p.is_file() and not (SKIP_DIRS & set(p.parts))]
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(files) if p.is_file()}


def openssl(args, pw):
    r = subprocess.run(["openssl", "enc", *args, *CIPHER, "-pass", "env:HV_PW"],
                       env={**os.environ, "HV_PW": pw}, capture_output=True)
    if r.returncode:
        raise RuntimeError("openssl failed (wrong password?)")


def decrypt(enc, pw, workdir):
    """Decrypt a vault file into workdir/holdout."""
    tarp = Path(workdir) / "in.tar"
    openssl(["-d", "-in", str(enc), "-out", str(tarp)], pw)
    with tarfile.open(tarp) as t:
        t.extractall(workdir, filter="data")
    tarp.unlink()


def vault_file(ctx, suite):
    name = ctx.cfg.get("project", {}).get("name")
    if not name or not re.fullmatch(r"[\w.-]+", name):
        sys.exit("checks.toml [project] name missing or invalid.")
    return VAULT / name / f"{suite}.tar.enc"


# ---------- built-in checks ----------
def check_lock(root):
    lp = root / "harness" / ".lock"
    if not lp.exists():
        return "WARN", "fingerprint: never locked (owner: `harness/verify --lock` after approving checks)", None
    lock, cur = json.loads(lp.read_text()), protected(root)
    changed = sorted(f for f in set(lock["files"]) | set(cur) if lock["files"].get(f) != cur.get(f))
    if changed:
        return "TAMPERED", (f"protected files changed since owner lock {lock['locked_at'][:10]}: "
                            + ", ".join(changed[:6]) + " (if owner approved: owner re-runs --lock)"), None
    return "PASS", f"fingerprint: protected files unchanged since lock {lock['locked_at'][:10]}", None


def check_budget(root, budget):
    limit = budget.get("max_code_lines", 0)
    if not limit:
        return None
    n = sum(1 for p in files_under(root, budget.get("src_dirs", ["src"]), set(budget.get("extensions", [".py"])))
            for l in p.read_text(errors="ignore").splitlines() if l.strip() and not l.strip().startswith(("#", "//")))
    return ("PASS" if n <= limit else "FAIL"), f"code size {n}/{limit} lines (budget)", None


def check_hardcode(root, hc):
    if not hc:
        return None
    min_len, ignore = hc.get("min_len", 6), set(hc.get("ignore", []))
    str_re = re.compile(r"""(["'])((?:(?!\1)[^\n\\]){%d,200})\1""" % min_len)
    num_re = re.compile(r"(?<![\w.])\d+\.\d{3,}(?![\w.])")
    ident = re.compile(r"^[A-Za-z_][\w.]*$")
    lits = {}
    for p in files_under(root, hc.get("test_dirs", []), TEXT_EXT):
        text = p.read_text(errors="ignore")
        for s in [m.group(2) for m in str_re.finditer(text) if not ident.match(m.group(2))] + num_re.findall(text):
            if s not in ignore:
                lits.setdefault(s, p)
        if len(lits) > 3000:
            break
    hits = [f'"{s[:40]}" from {o.relative_to(root)} found in {p.relative_to(root)}'
            for p in files_under(root, hc.get("src_dirs", ["src"]), TEXT_EXT)
            for text in [p.read_text(errors="ignore")] for s, o in lits.items() if s in text]
    if hits:
        return "WARN", f"hardcode: {len(hits)} test literal(s) in source (judge each; add false alarms to ignore)", "\n".join(hits[:10])
    return "PASS", "hardcode: no test literals found in source", None


def check_docs(root, docs):
    over = [f"{rel} {n}/{lim}" for rel, lim in docs.items() if (root / rel).is_file()
            for n in [len((root / rel).read_text(errors="ignore").splitlines())] if n > lim]
    return ("WARN", "docs over limit: " + ", ".join(over), None) if over else ("PASS", "docs within size limits", None)


def run_checks(cwd, checks, only, logs):
    logs.mkdir(parents=True, exist_ok=True)
    rows = []
    for c in checks:
        if only and c["name"] not in only:
            continue
        t0, to = time.time(), c.get("timeout", 900)
        try:
            r = subprocess.run(c["cmd"], shell=True, cwd=cwd, capture_output=True, text=True, timeout=to)
            ok, out = r.returncode == 0, (r.stdout or "") + (r.stderr or "")
        except subprocess.TimeoutExpired:
            ok, out = False, f"TIMEOUT after {to}s"
        (logs / (re.sub(r"[^\w.-]+", "_", c["name"]) + ".log")).write_text(out)
        metric = " · ".join(METRIC_RE.findall(out)[-3:])
        rows.append({"name": c["name"], "scope": c.get("scope", "trunk"), "ok": ok, "secs": time.time() - t0,
                     "metric": metric, "tail": None if ok else tail(out, 12)})
    return rows


# ---------- modes ----------
def verify(ctx, only):
    eff = effective(ctx)
    rows = []
    if not eff["checks"]:
        rows.append(("WARN", "no acceptance checks defined", None))
    for r in run_checks(ctx.root, eff["checks"], only, ctx.h / ".logs"):
        tag = "" if r["scope"] == "trunk" else "[branch] "
        rows.append(("PASS" if r["ok"] else "FAIL",
                     f"{tag}{r['name']} ({r['secs']:.1f}s)" + (f"  {r['metric']}" if r["metric"] else ""), r["tail"]))
    if not only:
        rows.append(check_lock(ctx.root))
        rows += [x for x in (check_budget(ctx.root, eff["budget"]), check_hardcode(ctx.root, eff["hardcode"]),
                             check_docs(ctx.root, eff["docs"])) if x]
    if not ctx.on_trunk and not ctx.branch_ready:
        rows.append(("WARN", f"branch {ctx.branch} has no branch harness (owner: `/human-harness init` for a branch interview)", None))
    if ctx.trunk_has_new_harness():
        rows.append(("WARN", f"{ctx.trunk} has newer harness changes: merge {ctx.trunk} into this branch", None))
    print(f"HARNESS VERIFY — {ctx.cfg.get('project', {}).get('name', ctx.root.name)} @ {ctx.label} — {datetime.datetime.now():%Y-%m-%d %H:%M}")
    for state, msg, detail in rows:
        print(f" {state:<8} {msg}")
        if detail:
            print("\n".join("          | " + l for l in detail.splitlines()))
    fails = sum(s in ("FAIL", "TAMPERED") for s, _, _ in rows)
    warns = sum(s == "WARN" for s, _, _ in rows)
    print(f"RESULT: {'FAIL' if fails else 'PASS'} ({fails} fail, {warns} warn) · logs: harness/.logs/")
    for hist in {ctx.h / ".holdout_history", ctx.scope_dir / ".holdout_history"}:
        if hist.is_file() and hist.read_text().strip():
            print("Last holdout: " + hist.read_text().strip().splitlines()[-1])
    return 1 if fails else 0


def compare(ctx, ref):
    """Run the checks at another ref (default: trunk) in a temporary worktree and show results side by side."""
    ref = ref or ctx.trunk
    if not ctx.is_git or git(ctx.root, "rev-parse", "--verify", "--quiet", ref) is None:
        sys.exit(f"Cannot compare: '{ref}' is not a git ref here.")
    tmp = Path(tempfile.mkdtemp(prefix="harness-compare-"))
    wt = tmp / "wt"
    try:
        if git(ctx.root, "worktree", "add", "--detach", str(wt), ref) is None:
            sys.exit("git worktree add failed.")
        ignored = git(ctx.root, "ls-files", "--others", "--ignored", "--exclude-standard", "--directory") or ""
        for entry in {l.rstrip("/") for l in ignored.splitlines() if l.rstrip("/").count("/") == 0}:
            if not (wt / entry).exists():  # share untracked data/venv so checks can run
                (wt / entry).symlink_to(ctx.root / entry)
        base_checks = [dict(c, scope="trunk") for c in load_toml(wt / "harness" / "checks.toml").get("check", [])]
        base = {r["name"]: r for r in run_checks(wt, base_checks, None, tmp / "logs")}
        cur = {r["name"]: r for r in run_checks(ctx.root, effective(ctx)["checks"], None, ctx.h / ".logs")}
    finally:
        git(ctx.root, "worktree", "remove", "--force", str(wt))
        shutil.rmtree(tmp, ignore_errors=True)
    cell = lambda r: "—" if not r else (("PASS" if r["ok"] else "FAIL") + (f" {r['metric']}" if r["metric"] else ""))
    here = ctx.branch or "working tree"
    print(f"COMPARE — {ref}  vs  {here}")
    w = max([len(n) for n in {**base, **cur}] + [5])
    print(f" {'check':<{w}}  {ref[:30]:<40}  {here[:30]}")
    for n in sorted({**base, **cur}):
        print(f" {n:<{w}}  {cell(base.get(n)):<40}  {cell(cur.get(n))}")
    return 0


def lock(ctx):
    owner_only("--lock")
    fp = protected(ctx.root)
    (ctx.h / ".lock").write_text(json.dumps(
        {"locked_at": datetime.datetime.now().isoformat(timespec="seconds"), "files": fp}, indent=1))
    print("Locked fingerprints of:\n  " + "\n  ".join(fp))
    return 0


def seal(ctx):
    owner_only("--seal")
    stage = ctx.h / "_holdout_staging"
    if not stage.is_dir() or not any(stage.iterdir()):
        sys.exit(f"Put holdout files in {stage} first.")
    enc = vault_file(ctx, ctx.suite)
    enc.parent.mkdir(parents=True, exist_ok=True)
    os.chmod(VAULT, 0o700)
    os.chmod(enc.parent, 0o700)
    print(f"Sealing into suite '{ctx.suite}' ({ctx.label}).")
    pw = getpass.getpass("Holdout password: ")
    with tempfile.TemporaryDirectory() as td:
        work = Path(td) / "holdout"
        if enc.exists():
            ans = input("This suite already exists: [a]dd to it, [r]eplace it, [c]ancel? ").strip().lower()
            if ans == "a":
                try:
                    decrypt(enc, pw, td)
                except RuntimeError as e:
                    sys.exit(str(e))
            elif ans != "r":
                sys.exit("Cancelled.")
        elif getpass.getpass("Repeat password: ") != pw:
            sys.exit("Passwords differ.")
        work.mkdir(exist_ok=True)
        for p in stage.iterdir():
            (shutil.copytree(p, work / p.name, dirs_exist_ok=True) if p.is_dir() else shutil.copy2(p, work / p.name))
        tarp = Path(td) / "out.tar"
        with tarfile.open(tarp, "w") as t:
            t.add(work, arcname="holdout")
        openssl(["-salt", "-in", str(tarp), "-out", str(enc)], pw)
    shutil.rmtree(stage)
    stage.mkdir()
    if not any(h["suite"] == ctx.suite for h in effective(ctx)["holdouts"]):
        print(f"Note: no [[holdout]] entry with suite = \"{ctx.suite}\" yet; ask Claude to add one (you approve).")
    print(f"Sealed into {enc}. Staging emptied. Keep a backup of the vault and never share the password.")
    return 0


def holdout(ctx):
    owner_only("--holdout")
    entries = effective(ctx)["holdouts"]
    if not entries:
        sys.exit("No [[holdout]] entries in checks.toml.")
    state, msg, _ = check_lock(ctx.root)
    if state != "PASS":
        sys.exit(f"Refusing: {msg}")
    pw = getpass.getpass("Holdout password: ")
    all_ok = True
    for h in entries:
        enc = vault_file(ctx, h["suite"])
        if not enc.exists():
            print(f"HOLDOUT [{h['suite']}]: not sealed yet — skipped")
            continue
        with tempfile.TemporaryDirectory() as td:
            try:
                decrypt(enc, pw, td)
            except RuntimeError:
                pw2 = getpass.getpass(f"Password for suite '{h['suite']}': ")
                try:
                    decrypt(enc, pw2, td)
                except RuntimeError as e:
                    print(f"HOLDOUT [{h['suite']}]: {e}")
                    all_ok = False
                    continue
            cmd = h["cmd"].replace("{holdout_dir}", shlex.quote(str(Path(td) / "holdout")))
            r = subprocess.run(cmd, shell=True, cwd=ctx.root, capture_output=True, text=True, timeout=h.get("timeout", 1800))
            out = (r.stdout or "") + (r.stderr or "")
        ok = bool(r.returncode == 0 and (not h.get("pass_regex") or re.search(h["pass_regex"], out)))
        all_ok &= ok
        summary = tail(out, h.get("show_lines", 5))
        print(f"HOLDOUT [{h['suite']}]: {'PASS' if ok else 'FAIL'}\n{summary}")
        last = summary.splitlines()[-1][:200] if summary else ""
        with (ctx.scope_dir / ".holdout_history").open("a") as f:
            f.write(f"{datetime.datetime.now():%Y-%m-%d %H:%M} | {ctx.branch or ctx.trunk} | suite {h['suite']} | "
                    f"{'PASS' if ok else 'FAIL'} | {last}\n")
    return 0 if all_ok else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--lock", action="store_true")
    g.add_argument("--seal", action="store_true")
    g.add_argument("--holdout", action="store_true")
    g.add_argument("--compare", nargs="?", const="", metavar="REF")
    ap.add_argument("--only", nargs="+", metavar="NAME")
    a = ap.parse_args()
    root = find_root(Path.cwd())
    if not root or not (root / "harness" / "checks.toml").is_file():
        sys.exit("No harness/checks.toml found. Run from inside a project with a harness.")
    ctx = Ctx(root)
    if a.lock:
        return lock(ctx)
    if a.seal:
        return seal(ctx)
    if a.holdout:
        return holdout(ctx)
    if a.compare is not None:
        return compare(ctx, a.compare)
    return verify(ctx, a.only)


if __name__ == "__main__":
    sys.exit(main())
