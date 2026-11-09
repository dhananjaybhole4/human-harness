# addon: ML / data science

Extra probes and checks when the project trains, evaluates or uses a model.

## Probes (weave into areas B–F)
- **Data:** source, how it's collected, size, time span, who labels and how reliable the labels are,
  class balance, missing values, known quirks. "Show me 5 raw rows."
- **Unit of prediction:** one row = what? Groups (customer, machine, part) that must not cross splits?
- **Time:** does order matter? Is anything used as input that wouldn't be known at prediction time?
- **Split strategy:** random / time-based / grouped. Why that one?
- **Baseline:** majority class, a simple rule, linear model, or the current manual process. What
  score does it get? What margin over it is worth the complexity?
- **Metric ↔ cost:** cost of a false positive vs a false negative. Which metric reflects that?
  What threshold is "useful"? Is calibration needed?
- **Use:** batch or real-time, latency and memory limits, where it runs, who acts on predictions.
- **Explainability:** does someone need to understand why a prediction was made?
- **Change:** data drift, retraining cadence, how a degradation would be noticed.
- **Reproducibility:** seeds, data versioning, environment pinning.
- **Simplicity:** "If a heuristic gets 90% of the value, do we still want a model?"

## Checks to propose
| Check | Proves |
|---|---|
| beats baseline by ≥ agreed margin on the validation set | complexity is earning its keep |
| holdout metric ≥ threshold (holdout, owner-run) | generalises to unseen data |
| no split overlap (IDs/groups/time windows) | no leakage via shared entities |
| no target-derived or future features (feature audit list) | no leakage via features |
| shuffled-label sanity: score ≈ chance | the pipeline isn't leaking the label |
| same seed → same metric (± tolerance) | reproducible |
| training/inference runtime and memory within budget | usable in production |
| prediction on malformed/missing input → clear error or defined fallback | robust inputs |

## Red flags (investigate before reporting)
Metric far above baseline on the first try · validation ≫ holdout · one feature dominating ·
performance that drops on recent data · results that change a lot between seeds.
