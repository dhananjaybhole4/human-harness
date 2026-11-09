# merge: finish a branch (keep it or drop it)

Run on the branch. Ends with the branch either folded into its base (usually trunk) or discarded,
with the lesson kept either way. Merging, pushing and deleting branches are owner decisions: ask.

## 1. Evidence (on the branch)
- Clean working tree. If the trunk has newer harness changes, merge trunk into the branch first.
- `harness/verify`: everything must PASS (base checks + branch checks).
- `harness/verify --compare`: base vs branch side by side.
- Owner runs `harness/verify --holdout` in their terminal (all suites: base + branch).
- Show a ≤8 line verdict against the branch SPEC "Done / keep when", including what is not verified.

## 2. Owner decides: keep / drop / continue
**Coach first** (🎯 eval design): "Before I give my view: keep or drop, and why?" Grade it, then give yours.

## 3a. Keep: fold the branch into the base harness (on the branch, before merging)
Show each change as `before → after — reason`. Apply after approval:
1. Branch SPEC → base SPEC: goal/examples/done-criteria become a new section. "Changes to trunk"
   items applied to SPEC/BOUNDARIES.
2. Branch `checks.toml` entries (`[[check]]`, `[[holdout]]`, overrides) → base `checks.toml`. Check
   files stay in `harness/checks/<slug>/` (paths unchanged). Holdout suite `<slug>` stays as its own suite.
3. Branch DECISIONS → base DECISIONS (prefixed `[<branch>]`). Branch INTERVIEW log → base INTERVIEW
   under `### branch <branch>`. ARCHITECTURE notes → merged into the base map.
4. Delete `harness/branches/<slug>/`. Update base STATUS (what this branch added, what's next).
5. Commit (owner asked). Merge into base: owner chooses local merge or PR. Resolve conflicts in
   harness files with the owner; never silently pick a side for SPEC/BOUNDARIES/checks.
6. On the base after merge: owner runs `harness/verify --lock`, then run `harness/verify`. Suggest
   `/human-harness update`.

If the base is another branch (nested), fold into that branch's `harness/branches/<base>/` instead.

## 3b. Drop: keep the lesson, lose the code
1. Base DECISIONS gets one line: `date — tried <branch>: <result vs keep criteria> — dropped because <why>`.
   Do it on the base branch (clean tree; switch, append, commit when the owner says so).
2. If it taught something general: offer a postmortem-style lesson (`~/.claude/harness-growth/LESSONS.md`).
3. Deleting the branch (local/remote) only when the owner says so. Its holdout suite stays in the vault;
   the owner may delete `<slug>.tar.enc` themselves.

## 3c. Continue
Update branch STATUS with the gap to the keep criteria and the new time-box (owner sets it).
