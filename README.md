# human-harness

Make Claude Code prove it built what you asked for.

human-harness is a [Claude Code](https://docs.claude.com/en/docs/claude-code) skill. It interviews you until your idea is written down as numbers and examples, turns that into checks the agent has to pass, and keeps a second set of test cases encrypted where the agent can't read them. You judge the result by running one command, without reading the code.

<img alt="harness/verify fails on an empty invoice, one line is fixed, verify passes" src="assets/demo.gif" width="720">

A real recording of a three-check project: one check fails, one line is fixed, and every check passes.

I built it because I direct AI agents but don't review the code they write. "Done" from an agent meant nothing to me until it came with evidence I could check myself.

## Install

```bash
git clone https://github.com/dhananjaybhole4/human-harness.git
cd human-harness && ./install.sh
```

You need Python 3.11+ and git, plus openssl if you want hidden test cases. The installer copies the skill to `~/.claude/skills/human-harness` and adds three hooks to `~/.claude/settings.json`, saving a backup of that file first. So far it has only been tested on Linux (WSL2).

## A first project

Open Claude Code in your project and run:

```
/human-harness init
```

It starts asking questions and keeps going until none of your answers are vague. "Fast" turns into "under 200 ms for 10k rows". "Handle bad input" turns into three example rows, each with the output you expect. If the repo already has code, it reads that first and asks which of the decisions it finds were on purpose. It writes no code during this step.

When the interview is done, it shows you the harness it wrote in `harness/`: a one-page `SPEC.md` with a "done when" table, a `BOUNDARIES.md` of things it must never do or must ask about, and `checks.toml`, which lists the acceptance checks as shell commands. Nothing changes until you approve it. Then you lock it:

```
harness/verify --lock
```

Locking fingerprints the checks. If they change later without your approval, `verify` will flag it.

Next, put a few test cases the agent should never see into `harness/_holdout_staging/` and seal them with a password:

```
harness/verify --seal
```

Now let it build:

```
/human-harness run
```

The agent works through `harness/STATUS.md` one step at a time and runs `verify` after each step. If it hits a decision that belongs to you, it doesn't guess. It writes the question into STATUS and carries on with whatever the question doesn't block:

```
Q3. Drop rows with missing timestamps? (4% of rows)
    a) drop them — simpler, loses 4% of data
    b) fill from the previous row — keeps data, may hide sensor faults   ← recommended: gaps are single readings
    Blocks: training run. Not blocking: data validation, report layout.
```

It stops when a milestone passes, when every remaining step is waiting on you, or when the same check has failed three times in a row. When it says a milestone is done, run the hidden cases yourself:

```
harness/verify --holdout
```

You only see scores. If it passes its own checks but fails these, it learned your examples instead of solving the problem.

## Commands

```
/human-harness init              interview, then write the harness
/human-harness run               build until done or blocked (/loop it to run unattended)
/human-harness update [add X]    re-interview when plans change or scope grows
/human-harness check             audit the harness itself
/human-harness merge             finish a branch: compare with main, keep or drop
/human-harness postmortem        turn a mistake into a new rule or check
/human-harness learn <topic>     step-by-step teaching with graded questions

harness/verify [--only NAME]     run the checks
harness/verify --compare [ref]   this branch vs main, side by side
harness/verify --lock|--seal|--holdout   owner only, in your own terminal
```

Each git branch gets its own small spec and checks on top of main's. For ML projects there's an add-on with a baseline to beat, data-leakage checks and a shuffled-label sanity test.

## Limits

The agent is kept out of the hidden cases in two ways. The guard hook refuses any command that mentions the vault, and the cases are encrypted. The guard only matches text, so an agent that really wanted to could get past it. The encryption is the part that actually protects the cases, so keep your password somewhere the agent can't read. Likewise, `--holdout` runs whatever evaluation command you approved. If that script prints the cases, they leak.

The guard hook runs in every Claude Code project, not only harnessed ones. Outside a harness it does nothing except refuse vault commands and ask before the agent edits your Claude settings or global `CLAUDE.md`.

Each project's `harness/verify` calls the installed skill. Anyone who clones a harnessed repo needs the skill installed too.

The interview takes a while. It's worth it for anything you'll spend more than a day on. For a throwaway script, it isn't.

## Uninstall

Delete `~/.claude/skills/human-harness` and remove its three hook entries from `~/.claude/settings.json`. The installer left a backup next to that file. Your projects' `harness/` folders are plain text: keep them or delete them.

## Contributing

Domain add-ons are the most useful contribution. An add-on covers what to ask, which checks to propose, and what looks suspicious in that domain. [`addons/ml.md`](skills/human-harness/addons/ml.md) is the template. For bugs, include your `harness/verify` output.

## License

MIT
