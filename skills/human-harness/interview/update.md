# update: mid-project re-interview

Keeps the harness true as the project teaches us things. Short and targeted: 3–10 questions.
Same push rules as `init.md` §3 (load that section only if you need the technique table).
Ask via AskUserQuestion by default (option 1 = your recommendation), as in `init.md` §3.
**Scope:** works on the current scope. On a branch, read and change only the branch files
(`harness/branches/<slug>/`); a change the trunk needs goes into the branch SPEC "Changes to trunk"
(applied at merge). On trunk, changes go to the trunk files.

## Triggers (when to suggest it during normal work)
Milestone done · a check fails repeatedly · new unknown found · code doing something SPEC doesn't
say · owner changed their mind · you made a judgment call that needs ratifying · holdout score
dropped · ≥5 work sessions since the last update.

## 1. Prep (silent)
- Read `STATUS.md`, the tail of `DECISIONS.md`, and open items + readiness in `INTERVIEW.md`.
- Run `harness/verify`. Read the last lines of `harness/.holdout_history` if present.
- `git log --oneline` since the last update (date in INTERVIEW.md).
- Work out: what changed, what we learned, which assumptions broke, drift between SPEC and code,
  open items that are now due, and decisions you made alone.

## 2. Report (≤8 lines to the owner)
Progress against milestones, verify result, holdout status/age, what you learned, what is now unclear.

## 3. Targeted interview
**Owner brings new scope** ("I want to add X"): run a mini-init on X only. Cover areas A, C, D, E, F
and G from `init.md` (why, examples, done-criteria, boundaries, risks, approach) with the same
pushing, plus: how X affects what already exists and works, and what X must not break. Output: X as
a new milestone in SPEC, new checks, holdout cases if X must generalise. If X is unrelated to the
project's goal, recommend a separate project with its own `init`.

Otherwise ask about, in priority order:
1. Learnings that contradict SPEC or BOUNDARIES ("We found X; SPEC assumes Y. Which way?")
2. Judgment calls you made: ratify or reverse
3. Open items and unknowns whose trigger has arrived
4. The next milestone: its done-criteria, sharpened with push techniques
5. Any new risk: a mini-premortem on the next milestone
Coaching: 1–2 role-reversal questions (see `coach.md`). Example: "Before I propose it, how would you
check this milestone is really done?"

## 4. Apply
- SPEC / BOUNDARIES / checks: propose each change as `before → after — reason`. On a yes, write it.
  Remind the owner to re-run `harness/verify --lock` (and `--seal` if new holdout cases were staged).
- Freely update STATUS (overwrite), DECISIONS (append), ARCHITECTURE, INTERVIEW (log + readiness).
- If the same kind of problem keeps coming back, offer a postmortem.

## 5. Close
One line: what changed in the harness. Coaching grades as in `coach.md` (short debrief only if ≥2
coached questions).
