# postmortem: turn a mistake into a permanent fix

Use when something went wrong: rework, a wrong assumption, holdout failing while visible checks pass,
a broken rule, the owner unhappy with a "done" result. Blameless and short.

## Steps
1. **What happened:** ≤3 lines of facts (expected vs actual, cost in time).
2. **Root cause, in harness terms.** Ask "why" until you reach one of:
   - missing or vague SPEC info (the interview didn't ask, or accepted a vague answer)
   - missing check (nothing would have caught it)
   - missing boundary or ask-first rule
   - an unknown was never classified
   - the agent ignored a rule (→ needs enforcement, not just text)
   - the skill itself has a gap (an interview question it should always ask)
3. **Smallest durable fix**, at the right level:
   | Applies to | Put it in |
   |---|---|
   | this project | a check, a boundary, or a SPEC line |
   | every project | one line in `~/.claude/CLAUDE.md` |
   | every interview | a new probe in `interview/init.md` or an addon (new addon for a new domain) |
   | must not depend on memory | a check or a guard rule (hook) |
4. Show the fix (`before → after — reason`). Apply on approval. Re-lock if checks changed (owner).
5. Log: DECISIONS.md `date — postmortem: <cause> → <fix>`, and one line in
   `~/.claude/harness-growth/LESSONS.md` (create if missing): `date | project | lesson`.
6. **Coach:** "What could you have said or asked at the start that would have prevented this?"
   Grade it per `coach.md` (skill: usually problem framing or eval design).
