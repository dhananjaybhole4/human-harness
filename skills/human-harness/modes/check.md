# check: harness health audit

Read-only, except free docs (STATUS, INTERVIEW). Do not fix code or approved files unless asked.

## Steps
1. Run `harness/verify`. Keep the table.
2. Audit, reading only what's needed:
   - **Scope:** report which scope (trunk or branch). On a branch, audit the branch files plus trunk
     must-not-break. On trunk, list branches (`git branch`): which have a branch harness (only visible on
     that branch: `git ls-tree -d <b> harness/branches/`), which are stale or behind trunk's harness.
   - **Coverage:** each SPEC done-criterion ↔ a check in checks.toml or a `manual:` step. List orphans.
   - **Lock:** fingerprint state and lock age. TAMPERED → name the files and whether the owner approved them.
   - **Holdout:** sealed? Last run date and result (`harness/.holdout_history`). Flag as stale if it
     hasn't been run since the last milestone or for 14+ days.
   - **Drift:** ARCHITECTURE map vs actual tree (`ls`/grep). STATUS older than the last code change.
     Behaviour in code that SPEC doesn't mention.
   - **Bloat:** code size vs budget. Biggest files: any obvious duplication or simpler approach?
   - **Hardcoding:** verify warnings, plus a quick grep for absolute paths, magic numbers and sample values.
   - **Docs:** size limits. New stray .md files outside the fixed set.
   - **Unknowns/decisions:** unknowns whose trigger passed, decisions without a why.
3. Report on one screen:

```
HEALTH: GREEN | AMBER | RED
Verify: <n pass / n fail / warnings>     Holdout: <last result, age>    Lock: <ok/tampered/none>
| Area | State | Finding |
...
Top 3 actions: 1. … (owner/agent)  2. …  3. …
Not checked: …
```
RED = any FAIL on a check that should already pass at this phase, TAMPERED, or a holdout failure.
AMBER = gaps, staleness, warnings. Suggest `update` or `postmortem` if warranted.
