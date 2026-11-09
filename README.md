# human-harness

A [Claude Code](https://docs.claude.com/en/docs/claude-code) skill for people who direct AI coding agents but don't review the code themselves.

It interviews you until "what I want" is written down as numbers and examples, turns that into checks the agent has to pass, and keeps a set of test cases encrypted where the agent can't read them. You judge the work by running those checks. You never have to read a diff.

## Why

When an agent says "done", you usually can't tell whether:

- it built what you meant, or something close to it
- it made a failing test pass by editing the test
- it remembers the decision you made together last week
- it works on inputs it has never seen, or only on the examples you gave it

Spec-driven tools ([Spec Kit](https://github.com/github/spec-kit), Kiro, BMAD) help the agent plan before it codes. human-harness deals with what happens afterwards. Your spec, rules and checks are owner-approved and fingerprinted, the agent is stopped before it can change them, and the final judgement comes from cases it never saw.

## What it looks like

`harness/verify` is the one command you need to understand. This is real output from a small project with two acceptance checks:

```
HARNESS VERIFY — demo @ trunk (main) — 2026-11-09 16:23
 PASS     totals add up (0.0s)  cases=1
 FAIL     handles empty input (0.0s)
          | TypeError: 'NoneType' object is not iterable
 WARN     fingerprint: never locked (owner: `harness/verify --lock` after approving checks)
 PASS     hardcode: no test literals found in source
 PASS     docs within size limits
RESULT: FAIL (1 fail, 1 warn) · logs: harness/.logs/
```

The last three lines are built-in checks. They warn when the checks have changed since you approved them, when values copied from test files show up in the source code (a sign that a test was special-cased), and when the spec or status docs grow past what you can read in a minute.

When the agent needs a decision only you can make, it doesn't guess. It writes the question in `harness/STATUS.md` and carries on with the work the question doesn't block:

```
Q3. Drop rows with missing timestamps? (4% of rows)
    a) drop them — simpler, loses 4% of data
    b) fill from the previous row — keeps data, may hide sensor faults   ← recommended: gaps are single readings
    Blocks: training run. Not blocking: data validation, report layout.
```

## Install

Requires Python 3.11+, git, and openssl (openssl is only needed for the hidden test cases). Tested on Linux (WSL2).

```bash
git clone https://github.com/dhananjaybhole4/human-harness.git
cd human-harness && ./install.sh
```

The installer copies the skill to `~/.claude/skills/human-harness` and adds three hooks to `~/.claude/settings.json`, after backing that file up. It is safe to re-run, but a re-run replaces the installed skill, so any local edits you made to it are lost.

Restart Claude Code, open a project, and type `/human-harness`.

## How it works

1. **`/human-harness init`: the interview.** It covers purpose, context, inputs and outputs, success criteria, boundaries, risks and approach. It doesn't accept adjectives: "fast" becomes "under 200 ms for 10k rows", and "handles bad input" becomes three example rows with their expected results. On an existing repo it reads the code first, then asks about the choices it finds. No code is written during init.
2. **You approve the harness.** These files are written to `harness/` in your repo:

   | File | Contains | Changes |
   |---|---|---|
   | `SPEC.md` | goal, examples, a "done when" table where every row names its check | only with your approval |
   | `BOUNDARIES.md` | never / ask first / free (max 15 rules) | only with your approval |
   | `checks.toml` + `checks/` | acceptance checks: shell commands, exit 0 = pass | only with your approval, then you run `verify --lock` |
   | `STATUS.md` | done, next, questions for you, what is *not* verified | overwritten every session |
   | `DECISIONS.md` | `date — decision — why`, one line each | appended |
   | `INTERVIEW.md` | every question and answer, so nothing is asked twice | appended |

3. **You seal the hidden cases.** You put test cases in `harness/_holdout_staging/` and run `harness/verify --seal` in your own terminal. They're encrypted with a password you choose (AES-256, openssl) into `~/harness-holdouts/`, outside the repo.
4. **`/human-harness run`: the agent builds.** It works through STATUS one step at a time and runs `verify` after each step. It stops when a milestone passes, when everything left is waiting on your answers, or when the same check has failed three times in a row. At that point it reports and suggests a postmortem.
5. **You run `harness/verify --holdout`.** It prints the scores only. If the agent passes the practice checks but fails here, it fitted the examples instead of solving the problem.

Every Claude Code session in a harnessed project starts with the rules and the current status already loaded. If code changed after STATUS was last updated, the agent is blocked from ending the session until it updates STATUS.

## Commands

| Command | Where | What it does |
|---|---|---|
| `/human-harness init` | Claude Code | Interview → harness. On a branch: a short interview, since main is already known. |
| `/human-harness run` | Claude Code | Build until done or blocked. Use `/loop /human-harness run` to run it unattended. |
| `/human-harness update [add X]` | Claude Code | Re-interview when plans change, or add new scope |
| `/human-harness check` | Claude Code | Health audit of the harness: GREEN / AMBER / RED |
| `/human-harness merge` | Claude Code | Finish a branch: compare it with main, then keep it or drop it (the lesson is kept either way) |
| `/human-harness postmortem` | Claude Code | Turn a mistake into a new rule or check |
| `/human-harness learn <topic>` | Claude Code | Step-by-step teaching with graded questions. It teaches judgment, not syntax. |
| `harness/verify [--only NAME]` | terminal | Run the checks |
| `harness/verify --compare [ref]` | terminal | Run the checks on this branch and on `ref` (default main), side by side |
| `harness/verify --lock` / `--seal` / `--holdout` | **your terminal only** | Approve the checks / encrypt the hidden cases / score the hidden cases |

The owner-only flags refuse to run unless the command is run interactively in a terminal (stdin and stdout attached to a TTY), and the guard hook blocks the agent from typing them at all.

For ML projects there's an add-on (`addons/ml.md`). It requires a baseline that must be beaten by an agreed margin and checks for data leakage (overlap between splits, features from the future). It also runs a shuffled-label sanity test: if the model still scores well on shuffled labels, the pipeline is leaking.

## What it protects against, and what it doesn't

This is a set of guard rails, not a sandbox.

**Covered:**
- **Edits to approved files.** Editing `SPEC.md`, `BOUNDARIES.md`, `checks.toml` or `checks/` triggers an approval prompt. Edits that get past the prompt, for example through a script, are flagged by the fingerprint the next time `verify` runs.
- **Reading the hidden cases.** Any tool call that mentions the vault path is denied, and the cases are encrypted. Even if the agent found the file, it would need your password to read it.
- **Gaming the tests.** Test values copied into source code are flagged by the hardcode scan.
- **Forgetting.** Decisions and Q&A live in the repo, not in chat history.

**Not covered:**
- **A determined agent can get past a text-matching guard.** For example, it could build the vault path inside a script instead of typing it. The encryption is what actually protects the hidden cases, so don't store your password anywhere the agent can read it.
- **The holdout command is yours to check.** `--holdout` runs the evaluation command from `checks.toml`. If that script prints the cases, they leak. Approve it the way you'd approve any check.
- **Checks only prove what they test.** A weak check passes weak code. The interview pushes for measurable criteria, but deciding which checks matter is still your job.

## Things to know before installing

- **The guard hook is global.** It runs on every tool call in every project, not just harnessed ones. Outside a harness it does two things: it blocks commands that mention the vault or owner-only flags, and it asks before the agent edits `~/.claude/settings.json` or `~/.claude/CLAUDE.md`. The other two hooks do nothing in projects without a `harness/` folder.
- **Each harnessed repo depends on the installed skill.** `harness/verify` calls `~/.claude/skills/human-harness/scripts/verify.py`, so anyone who clones the repo needs the skill installed too.
- **Claude Code only.** It relies on Claude Code skills and hooks.
- **The interview takes time.** That's deliberate, because time spent answering questions upfront is time not spent redoing work later. For a throwaway script, it isn't worth it.

## Uninstall

Delete `~/.claude/skills/human-harness`, and remove the three `human-harness` hook entries from `~/.claude/settings.json`. The installer saved a backup next to it as `settings.json.bak.<timestamp>`. Each project's `harness/` folder is plain files: keep it or delete it.

## Contributing

The most useful contributions are domain add-ons in `skills/human-harness/addons/` (web apps, data pipelines, embedded and so on): what to ask in the interview, which checks to propose, and the red flags for that domain. `addons/ml.md` shows the format.

Bug reports are most useful when they include the `harness/verify` output and what you expected instead.

## License

[MIT](LICENSE)
