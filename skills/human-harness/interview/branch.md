# init on a branch: the branch interview

Used when the project already has a trunk harness and you're on another branch without
`harness/branches/<branch>/`. The trunk is **known context**: never re-ask anything it answers.
Same depth, push techniques and coaching as `init.md` §3 (load that section), scoped to the branch.

## 0. Prep (silent)
- Read the trunk harness: SPEC, BOUNDARIES, DECISIONS, ARCHITECTURE, INTERVIEW (facts + open items).
  Treat all of it as answered.
- If trunk harness changed after this branch split off (`verify` warns), suggest merging trunk in first.
- **Base:** `git merge-base` with trunk. If the branch was cut from another branch that has its own
  `harness/branches/<that>/` folder, that folder is known context too, and the base is that branch.
- **Existing work on the branch:** `git log --oneline <base>..HEAD`, `git diff --stat <base>...HEAD`.
  List what it already changes and your guess why. This feeds the "why did you do that" pass.
- Scaffold: `python3 ~/.claude/skills/human-harness/scripts/scaffold.py --branch`.

## 1. Open (≤4 lines)
"Main's harness is already known: I'll only ask about this branch. 10–25 min. 'pause' and 'don't
know' are fine; coaching is on." First question: **"What is this branch for, and why now?"**

## 2. Areas (branch-scoped)
| Area | Must learn | Ready when |
|---|---|---|
| **A. Purpose + type** | Feature, experiment or fix. Why. Experiment: hypothesis and time-box | One-line goal + why; experiment has hypothesis + time-box |
| **C. New behaviour** | Real examples of the new or changed behaviour | Concrete samples or "don't know" + plan |
| **D. Done / keep** | Criteria **relative to base** where relevant ("accuracy ≥ base + 3%, latency ≤ base"). Experiment: the result that makes it worth keeping, and the result that kills it | Each criterion testable (check / holdout suite / manual) |
| **E. Boundaries delta** | Extra limits for this branch. **Must not break:** which base behaviours matter most | Delta listed; must-not-break named |
| **F. Risks** | What could this break on base? Premortem for the branch | Each risk → check or plan |
| **G. Approach** | Options and preference; unknown → explore first | Chosen or explore plan |
| **H. Merge plan** | What merges, what's thrown away, who decides, changes to trunk SPEC/BOUNDARIES the branch implies | Clear keep/discard rule |
| **Existing work** | For each existing change on the branch: "why?" | Labelled intentional / accidental / unknown |

Anything that would change the **trunk** SPEC or BOUNDARIES goes into the branch SPEC section
"Changes to trunk", applied only at merge.

## 3. Readiness → red-team → playback
Same as `init.md` §5–7, scoped to the branch.

## 4. Write (all inside the branch scope)
- `harness/branches/<slug>/SPEC.md` (show the owner, approve, one Write) and `checks.toml`.
- Check files in `harness/checks/<slug>/`. Print key numbers as `METRIC name=value` so
  `harness/verify --compare` can compare against base.
- Branch holdout if the new behaviour must generalise: the owner stages cases and seals them while on
  this branch (suite = branch slug). Add a `[[holdout]]` entry with `suite = "<slug>"`.
- Branch STATUS, DECISIONS, INTERVIEW, ARCHITECTURE notes. **Never** edit trunk harness files here.
- Owner runs `harness/verify --lock` (and `--seal` if staged) in their own terminal.
- Run `harness/verify` (base checks must still pass; new branch checks are expected red).
- Experiment: run `harness/verify --compare` once to record the base numbers in branch STATUS.

## 5. Close
Coaching debrief (`coach.md`). Then: "`/clear`, then `/human-harness run`. When done: `/human-harness merge`."
