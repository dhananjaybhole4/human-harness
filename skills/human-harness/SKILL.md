---
name: human-harness
description: Build and maintain a project harness (spec, boundaries, acceptance checks, encrypted holdout, status, decisions, architecture map) by deeply interviewing the owner, squeezing out everything in their head, and coaching them on core engineering skills along the way. Modes - init (new or existing project), run (autonomous build loop that stops for owner decisions), update (mid-project re-interview, including adding new scope), merge (finish a branch), check (health audit), postmortem (turn a mistake into a rule or check), learn (Socratic teaching of any topic, 5 tiered questions per step, honest grading). Use for "/human-harness", "/human-harness init|update|check|postmortem", "set up a harness", "update the harness", "something went wrong, fix the harness", "/human-harness learn <topic>", "teach me X step by step".
argument-hint: [init|run|update|merge|check|postmortem|learn] [notes or topic]
---

# human-harness

The owner does not review code. They judge work only through the harness. So the harness must
(1) capture exactly what they want, (2) wall off what they don't, (3) prove results by behaviour.
Your job: get all of that out of the owner's head by interviewing hard, keep it true as the project
moves, and make the owner a better engineer while doing it.

## Routing
| Arg | Load (only these) |
|---|---|
| `init` | First detect scope (below). Trunk: `interview/init.md`. Branch: `interview/branch.md`. Plus `coach.md` (+ `addons/<x>.md` once relevant) |
| `update` | `interview/update.md`, `coach.md` |
| `run` | `modes/run.md` (autonomous build loop; stops at owner decisions and milestones) |
| `merge` | `modes/merge.md`, `coach.md` (finish a branch: fold into base, or drop and keep the lesson) |
| `check` | `modes/check.md` |
| `postmortem` | `modes/postmortem.md`, `coach.md` |
| `learn <topic>` | `modes/learn.md` only (teach the owner; topic = the rest of the args; works with or without `harness/`) |
| none | No `harness/` → `init`. On a branch without a branch harness → `init` (branch). Else show 3-line status (scope, verify result, next) and ask which mode; default `update`. |

## Scope (branches)
Detect with git: trunk = `[project] trunk` in checks.toml (else origin HEAD / main / master).
| Situation | Scope | `init` does |
|---|---|---|
| No `harness/`, on trunk (or no git) | trunk | full interview (`init.md`) |
| No `harness/`, on another branch | — | ask: switch to trunk first (recommended if tree is clean), or build the trunk harness here (reaches trunk at merge) |
| `harness/` exists, on trunk | trunk | resume interview if INTERVIEW has open areas, else suggest `update` |
| `harness/` exists, on branch, no `harness/branches/<slug>/` | branch | branch interview (`branch.md`): trunk is known context |
| branch folder exists | branch | resume branch interview or suggest `update` |
**On a branch:** trunk harness files are read-only (guard asks). Write STATUS/DECISIONS/INTERVIEW/
ARCHITECTURE notes in `harness/branches/<slug>/`; branch checks in `harness/checks/<slug>/` declared in
the branch `checks.toml`. `verify` runs trunk checks + branch checks. Trunk files change only in `merge`.
`update`, `run`, `check` all work on the current scope.

Load `templates/` only when writing files. Available addons: `ml.md`. If no addon fits, derive
domain probes from first principles, and propose a new addon at the end (postmortem step 3).

## Project layout
| Path | Who reads | Who changes |
|---|---|---|
| `harness/SPEC.md` | owner + agent | agent proposes, **owner approves** |
| `harness/BOUNDARIES.md` | owner + agent | agent proposes, **owner approves** |
| `harness/checks.toml`, `harness/checks/` | agent; owner sees plain-language list | agent proposes, **owner approves**, owner locks |
| `harness/STATUS.md` | owner skims | agent, overwritten every session |
| `harness/DECISIONS.md` | owner skims | agent, append one line each |
| `harness/ARCHITECTURE.md` | agent | agent, kept current |
| `harness/INTERVIEW.md` | agent | agent; all Q&A so nothing is ever re-asked |
| `harness/verify` | agent runs it | protected |
| `harness/branches/<slug>/` | agent + owner (SPEC) | branch scope: SPEC + checks.toml approval-gated, rest free |
| `harness/checks/<slug>/` | agent | branch check files (approval-gated like all checks) |
| `~/harness-holdouts/<name>/<suite>.tar.enc` | **nobody but the owner** | owner via `verify --seal` (suite `main` on trunk, `<slug>` on a branch) |

Scaffold (project root; creates missing files only, never overwrites):
trunk `python3 ~/.claude/skills/human-harness/scripts/scaffold.py <name>` · branch `… scaffold.py --branch`.

## Non-negotiables
1. **Approval gate.** Never change SPEC, BOUNDARIES, checks.toml or `harness/checks/` without first
   showing the owner the change and the reason, and getting a yes. Write each approved file in one
   Write. STATUS, DECISIONS, ARCHITECTURE, INTERVIEW you maintain freely.
2. **Owner docs stay short.** SPEC ≤ ~60 lines, BOUNDARIES ≤ 15 rules, STATUS ≤ 30 lines. Plain
   language. Numbers and examples, never adjectives. Cut words, never information.
3. **Every done-criterion has a check.** Either an executable check in checks.toml, or explicitly
   `manual: owner verifies by …`. No orphan criteria.
4. **Acceptance checks vs unit tests.** Acceptance checks (`harness/checks/`) are owner-approved and
   fingerprinted. Unit tests are yours to add freely. Never weaken, skip or delete either to pass.
5. **Holdout is invisible to you.** Never read, list, decrypt or reason about holdout contents.
   `verify --holdout | --seal | --lock` are owner-only (own terminal).
6. **Honesty.** Never call the harness or the work "good". Report readiness, verify results, and
   what is not verified.
7. **No building during init.** Init produces the harness; build starts in a fresh session.

## verify
- `harness/verify` — runs every check plus built-ins (fingerprint, code-size budget, hardcode scan,
  doc sizes). Prints a PASS/FAIL table. `--only "<name>"` runs one check while iterating. On a branch it
  runs trunk + branch checks (branch ones tagged `[branch]`).
- `harness/verify --compare [ref]` — runs the checks at `ref` (default trunk) in a temp worktree and
  shows them side by side with the current tree, including `METRIC name=value` lines.
- Owner only, in their own terminal: `--lock` (fingerprint approved checks), `--seal` (encrypt
  `harness/_holdout_staging/` into the current scope's suite), `--holdout` (run all suites in scope,
  print scores only).
- Full logs: `harness/.logs/<check>.log` (grep them; don't rerun to see more).
- The guard blocks any shell command that *mentions* the owner-only flags or the vault, even in text.
  Use Read/Write tools for files that contain those words.

## Enforcement already installed (global hooks)
- Session start: rules + BOUNDARIES + the current scope's STATUS (trunk or branch) injected; flags a
  branch without a branch harness and trunk harness changes not yet merged into the branch.
- Guard: holdout vault and owner-only flags denied; edits to approved files (trunk and branch) and to
  trunk docs while on a branch trigger an owner prompt; `_holdout_staging/` is write-only for you.
- Stop: if code changed (git-based) after the current scope's STATUS.md, update the harness before finishing.
If a block looks wrong, tell the owner. Never work around it.

## Owner's command cheat-sheet (show this at the end of init)
| Owner types | Where | Does |
|---|---|---|
| `/human-harness init` | Claude chat | Interview → harness (on a new branch: short branch interview; main is already known) |
| `/human-harness merge` | Claude chat | Branch finished: compare with main, keep (fold in) or drop (keep the lesson) |
| `harness/verify --compare` | Own terminal (Claude runs it too) | Branch vs main, side by side |
| `/human-harness run` | Claude chat | Build until done or a question for the owner (`/loop /human-harness run` = unattended) |
| `/human-harness update [I want to add X]` | Claude chat | Short re-interview / add new scope |
| `/human-harness check` | Claude chat | Report card: GREEN / AMBER / RED |
| `/human-harness postmortem` | Claude chat | Mistake → permanent fix |
| `/human-harness learn <topic>` | Claude chat | Learn any topic step by step, 5 hard questions per step |
| `harness/verify` | Own terminal (Claude runs it too) | Practice test: PASS / FAIL |
| `harness/verify --seal` | Own terminal only | Lock hidden exam cases in the safe |
| `harness/verify --lock` | Own terminal only | Sign the rulebook (after approving changes) |
| `harness/verify --holdout` | Own terminal only | Real exam on hidden cases: score only |
Explain in plain words (exam analogy: practice questions vs hidden exam). Owner is not a coder.

## While doing normal project work (skill not invoked)
Suggest `/human-harness update` in one line when: a milestone finishes, a check keeps failing, a new
unknown appears, the code starts doing something SPEC doesn't say, the owner changes their mind, or
you made a judgment call the owner should ratify. Suggest `/human-harness postmortem` when something
went wrong or work had to be redone.
