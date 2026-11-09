# run: work through STATUS until done or blocked

Autonomous build loop. The owner wants maximum progress with minimum interruptions, and never wants
a guess on a decision that belongs to them.

## Before the first step
- **Scope:** on trunk use `harness/` files. On a branch: trunk SPEC + BOUNDARIES + the branch SPEC,
  and write STATUS/DECISIONS/ARCHITECTURE notes only in `harness/branches/<slug>/`. A branch without a
  branch harness → stop and suggest `/human-harness init` (branch interview) first.
  If `verify` warns the trunk has newer harness changes, ask the owner to merge trunk in before continuing.
- Read `SPEC.md`, `BOUNDARIES.md`, `STATUS.md`. Read ARCHITECTURE/DECISIONS only as needed.
- If STATUS has answered questions (owner replied, e.g. "Q3 b"): log each one in DECISIONS.md
  (`date — decision — why — owner`), remove it from **Needs owner**, unblock the work.
- Run `harness/verify` once for a baseline.

## The loop
1. Pick the next **unblocked** step from STATUS (explore tasks first if planned; respect time-boxes).
2. Do it. Iterate with `harness/verify --only "<check>"` or the narrowest unit test.
3. Run full `harness/verify`.
4. Overwrite STATUS (done / in progress / next / needs owner / not verified / last verify line).
   Log decisions: judgment calls within delegated scope → DECISIONS.md tagged `agent, ratify`.
5. Repeat.

## Decisions during the loop
| Kind | Action |
|---|---|
| Free (inside BOUNDARIES "free", within budget) | Do it |
| Delegated judgment call | Decide, log as `agent, ratify` |
| Ask-first, or any change to SPEC/BOUNDARIES/checks | **Don't attempt it.** Add a question to **Needs owner**, then continue with work it doesn't block |

Question format in STATUS (numbered, never reused):
```
Q3. <decision in one line> (<key fact, e.g. 4% of rows>)
    a) <option> — <tradeoff>
    b) <option> — <tradeoff>   ← recommended: <one-line why>
    Blocks: <what>. Not blocking: <what continues>.
```

## Stop when (then tell the owner in ≤5 lines)
- **Milestone done** (its checks pass): "Run `harness/verify --holdout` in your terminal, then
  `/human-harness update`." On a branch whose goal is met: suggest `/human-harness merge`.
- **Experiment time-box reached** (branch SPEC): stop even if unfinished, run `harness/verify --compare`,
  report vs keep criteria, suggest `/human-harness merge` (keep / drop / continue).
- **Everything left is blocked** by Needs-owner questions: list them.
- **Same check failed 3 attempts in a row:** stop thrashing, report what you tried, suggest `/human-harness postmortem`.
- **Something contradicts SPEC**, or an unknown appears that changes the plan: suggest `/human-harness update`.
- **Budget exceeded** (code size), or a guard hook blocked you: report it, don't work around it.

On stop: if a PushNotification tool is available, send one line ("human-harness: <project> needs you:
<reason>"). If running under `/loop`, end the loop instead of scheduling another wakeup.

## Never
Guess an ask-first decision · edit approved files without approval · weaken checks · report a
milestone done without a full verify PASS · touch the holdout.
