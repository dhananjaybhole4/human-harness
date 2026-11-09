# init: the deep interview

Goal: after this interview, a fresh agent with only the harness could deliver what the owner wants
without asking anything important. You are done only when that is true or every remaining gap is a
recorded "don't know" with a plan.

## 0. Prep (before the first question)
- **Scope first** (SKILL.md "Scope"): on a branch with a trunk harness already present → stop here
  and use `interview/branch.md` instead.
- Existing repo with several branches: list them (`git branch -a`). In area B ask, in one go, what each
  is for and whether it's alive. Record in INTERVIEW. Live ones get a branch interview later, only when
  work happens on them.
- Check `~/.claude/harness-growth/LOG.md` (if present): note the owner's weakest skills to coach.
- If `harness/INTERVIEW.md` exists: this is a resume. Read it, recap in 3 lines, continue from the
  weakest area. Never re-ask what is logged.
- **Existing repo:** understand it cheaply before asking anything.
  - `graphify-out/` present → query it. Otherwise: tree (depth 2, skip junk dirs), README, configs,
    entry points, tests, `git log --oneline -n 30`, grep for constants, thresholds, paths, magic numbers,
    filters, model/algorithm choices, eval code.
  - Draft `ARCHITECTURE.md` (agent-facing).
  - Build an **observed decisions** list, ranked by impact:
    `what — file:line — your guess why — risk if wrong`. It feeds area B; don't dump it on the owner.
- Run the scaffold script if `harness/` doesn't exist.

## 1. Open (one message)
Tell the owner, in ≤6 lines: how this works (broad questions first, then you will push on
answers), that it may take 30–60 min, "pause" saves progress, "don't know" is a fine answer,
coaching is on ("skip coaching" turns it off), and nothing gets built today.
Then ask the first broad question: **"Tell me about this project: what is it, and why does it
matter to you or the company?"**

## 2. Areas to cover (a map, not a script)
Start broad (A), then go wherever the gaps are. Come back to weak areas. Track readiness in
`INTERVIEW.md`.

| Area | Must learn | Ready when |
|---|---|---|
| **A. Purpose** | Real goal, why now, who uses the result, what decision or action changes, cost of not doing it, deadline | One-sentence goal + the real why + named consumer |
| **B. Context** | What exists, previous attempts and why they failed, data sources, where it runs, who maintains it later. Existing repo: walk the observed decisions | Every high-impact observed decision is labelled intentional / legacy / unknown |
| **C. Inputs & outputs** | Real samples: ≥2 typical, ≥1 edge, ≥1 invalid. Formats, volume, frequency, how output is consumed | Concrete samples exist, or "don't know" + plan to get them |
| **D. Success** | Done-criteria as numbers, metric + threshold + baseline, what would make the owner reject a working solution, non-functional needs (speed, cost, memory, explainability, maintainability, code size) | Every criterion is testable by a check or a named manual step |
| **E. Boundaries** | What must not be touched, data/privacy rules, allowed dependencies/services, cost limits, where code may run, irreversible actions, explicit out-of-scope | Never / ask-first / free lists are filled |
| **F. Risks & unknowns** | Premortem, critical assumptions, unknowns | Every unknown is: explore task (time-boxed) / ask-when trigger / owner finds out |
| **G. Approach** | Only after A–F: options, owner preferences, constraints. Unknown → explore phase first | Approach chosen, or explore plan agreed |
| **H. Working agreement** | Milestones, when to stop and ask, how the owner wants updates, autonomy level | Milestones with their own done-criteria |

Pull in `addons/<x>.md` as soon as the domain is clear (e.g. ML → `addons/ml.md`).

## 3. Question craft
- **Open first, then narrow.** "Tell me about…" → "What exactly happens when…" → "Give me the number."
- **One question per message, asked with AskUserQuestion by default.** Option 1 = your
  recommendation (label ends "(Recommended)"); 1–3 more real alternatives; the owner's own words go
  in the automatic "Other" field. Make each question stand alone (the owner may see only the
  dialog). Quick facts (formats, versions, yes/no) may be batched, up to 4 per call.
  Plain text instead whenever options would hurt the answer, e.g. you can't yet guess plausible
  answers (early "Tell me about…" openers), a coached 🎯 question (options would give the answer
  away), or you need the owner's own words (stories, examples, reasons).
- **After every answer:** extract facts, check for contradictions with earlier answers, find the
  weakest point in what was just said, and push on it before moving on.

### Push techniques (use constantly; don't accept the first answer)
| Technique | Example |
|---|---|
| Why ladder (3–5 levels, until real value) | "Why does that matter?" → "And if it didn't happen?" |
| Demand an example | "Show me a real input you'd get." |
| Counterexample | "If it returned X for this, would you accept it?" |
| Extremes | "Zero rows? 100× the data? Malformed file? Missing values?" |
| Quantify vague words | "fast / accurate / clean / robust / simple / soon" → "What number? Compared to what?" |
| Consequence | "If this is wrong, what breaks and who notices, and when?" |
| Contradiction | "Earlier you said X; now Y. Which wins?" |
| Simpler alternative | "Why not just <much simpler option>?" (catches over-engineering) |
| Ownership | "Is that your call or someone else's? Who signs off?" |
| Hidden stakeholder | "Who else will see, use or be affected by this?" |
| Assumption | "What are you assuming that, if false, changes everything?" |
| Premortem | "It's 15 days from now and this failed. What happened?" |
| Sweep (before leaving an area) | "What haven't I asked about this that I should have?" |

**Never accept as final:** "it should just work", "the standard way", "make it good", "the usual",
"whatever works". Push for a number, an example, or a rejection criterion.

**"You decide":** fine if truly delegated. Record `delegated to agent`, then still ask "What would
make you unhappy with my choice?" and record that as a criterion.

**"I don't know":** accept it at once, don't badger. Classify it:
- owner can find out → task (who, by when)
- exploration can answer it → explore task with a time-box
- doesn't matter yet → defer, with the trigger that makes it matter
Optionally offer your best default: "If unknown, I'd assume X. OK?"

### Existing repo: the "why did you do that" pass
For each high-impact observed decision: "In `file:line` you <do X>. Why?" Classify the answer:
- **intentional** → DECISIONS.md with the why
- **legacy/accidental** → ask keep or change
- **nobody knows** → investigate task
Prioritise: thresholds, data filters and drops, model/algorithm choice, eval method, hardcoded
values, anything that silently changes outputs.

## 4. Logging as you go
Update `INTERVIEW.md` every ~5 questions (terse): Q → A summary → facts, readiness table, open items.
This makes pause/resume and update interviews possible without re-asking.

## 5. Readiness gate
When you believe you're close, show the readiness table (area × ready / weak / unknown-with-plan,
one-line gap each). Any **weak** → keep interviewing. Don't move on to step 6 with a weak area.

## 6. Red-team the harness
List ways an agent could pass every check and still be wrong. For example: hardcoding or
special-casing samples, overfitting to visible tests, ignoring edge cases, silently dropping rows,
too slow at real data size, breaking on new data, bloated code. Turn each into a check, a boundary or
a holdout case. Then ask the owner: "What else could go wrong that these wouldn't catch?" (coach them).

## 7. Playback
Summarise in ≤15 lines, in the owner's words: goal, done-criteria, boundaries, unknowns, plan.
Ask: "What's wrong or missing?" Repeat until the owner says it's right.

## 8. Write the harness
1. `SPEC.md` and `BOUNDARIES.md` from the templates: show the owner, get approval, one Write each.
2. Acceptance checks: write them executable now, before any code exists. They are expected to fail
   (red) until the build is done. That is test-first. Show the owner a plain-language list
   (name — what it proves — threshold), not code. On approval, write `checks.toml` + `harness/checks/`.
   Set `[budget]` (code-size budget from the "how big should this be" discussion), `[hardcode]` and `[docs]`.
3. **Holdout** (always for ML/data/anything that must generalise; skip only for trivial scripts):
   - Best: owner copies real cases into `harness/_holdout_staging/` themselves (you never open it).
   - Else: you generate cases with Write into staging at the **very end** of this session, never read
     them back, and the owner must `/clear` before any build session.
   - The holdout eval command must live in `harness/checks/` (approved, fingerprinted) and print only
     a summary.
   - Tell the owner to run in **their own terminal**: `harness/verify --seal`.
4. Owner runs `harness/verify --lock` in their terminal after approving the checks.
5. `STATUS.md`: phase (explore or build), next step. Explore tasks first if unknowns need them.
   `DECISIONS.md`: all decisions so far. `ARCHITECTURE.md`: current map (or planned map for new projects).
6. Run `harness/verify` once and show the table (red is expected for a new build).

## 9. Close
Coaching debrief (see `coach.md`). Then tell the owner, in ≤6 lines: what to read (SPEC,
BOUNDARIES), the commands for their own terminal (`--seal`, `--lock`), and "`/clear`, then start the
build with `/human-harness run`". Then show the command cheat-sheet from SKILL.md.
