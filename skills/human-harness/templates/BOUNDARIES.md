# BOUNDARIES — {{NAME}}
_Approved by owner: {{DATE}}. Changes need owner approval. Max 15 rules._

## Never
- Hardcode values or special-case sample/test inputs.
- Weaken, skip or delete a check or test to make it pass.
- Touch the holdout vault or `harness/_holdout_staging/` contents.
- On a branch: change trunk harness files (they change only at merge). Branch work goes in `harness/branches/<branch>/`.

## Ask first
- Choosing between approaches with real tradeoffs; changing data formats or interfaces.
- Adding a dependency or service; anything irreversible or outward-facing.

## Free
- Refactors inside the code-size budget; adding unit tests; updating STATUS/DECISIONS/ARCHITECTURE.
