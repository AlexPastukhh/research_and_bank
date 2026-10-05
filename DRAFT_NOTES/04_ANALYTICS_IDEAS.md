# Analytics ideas backlog

This file intentionally contains more ideas than an MVP should implement. Each technique must be validated against domain assumptions, sample size, source bias, and user value before adoption.

## Baseline products worth keeping

The existing v1.11 result boundary is strong and reusable:

- `CurrentStateSnapshot`;
- `ChangeSet`;
- `TrendSeries`;
- `InterpretationRecord`;
- `ResearchHealthSnapshot`.

The proposals below can feed those products or become additional projections/capabilities.

## Distribution-first analysis

Do not default to averages. For price, payout, ratings, engagement, lifetime, etc. consider:

- min/max;
- P10/P25/median/P75/P90;
- histogram/distribution shape;
- sample count and coverage;
- confidence/uncertainty where meaningful.

## Frequency, value and competition

Useful market-style dimensions:

- observation/demand frequency;
- value/pay/revenue proxies;
- competition proxies;
- personal fit;
- persistence/lifetime;
- source diversity.

Do not collapse these into one master score too early. Pareto-frontier views can expose non-dominated choices without arbitrary weights.

## Velocity and persistence

Measure:

- new items per day/week;
- rate of change in observations/mentions;
- number of periods in which a phenomenon persists;
- recurrence after disappearance;
- acceleration/deceleration.

## Lifecycle / survival analysis

For entities that enter/leave observable populations:

- first seen / last seen;
- median lifetime;
- survival curves;
- hazard of disappearance/closure;
- lifetime by segment/value/source.

Examples: job-post lifetime, time in app top charts, trending-story half-life, game popularity persistence.

## Cohort analysis

Group items by first-seen/release/registration period or other cohort and compare subsequent behavior.

Examples:

- games released in Q1;
- apps first appearing in a category this month;
- opportunities first seen this week;
- news topics emerging during an event.

## Change-point detection

Detect structural breaks rather than only percent changes. Useful question: “When did the regime change?” Then ChatGPT can investigate plausible external causes around the detected period.

## Concept/data drift

Track whether the statistical character of incoming data changes enough that an old baseline/model/comparison is no longer representative.

## Anomaly detection

Detect unexpected spikes/drops/outliers in time series or multivariate behavior, but separate anomaly detection from causal explanation.

## Distribution shift

Two periods can have the same mean and very different distributions. Consider quantile changes plus distribution-distance metrics such as KS/Wasserstein/PSI where assumptions fit.

## Seasonality decomposition

Distinguish trend, recurring seasonal pattern and residual noise. Potential grains: hour/day/week/month/season/event cycle.

## Coverage-adjusted and source-normalized trends

Raw counts are dangerous when source coverage changes. Preserve:

- raw count;
- source count/coverage;
- source-normalized rates;
- comparable-route subset;
- coverage-adjusted estimates where methodologically justified.

Existing v1.11 comparability rules are a foundation; vNext can go beyond allow/deny comparison into explicit normalization.

## Source divergence

Show when sources disagree instead of hiding disagreement inside one aggregate.

Example:

```text
Steam signal: rising
Reddit signal: flat
YouTube signal: rising strongly
```

Source divergence is both an analytical result and a research-health signal.

## Evidence strength / confidence

Confidence should be explainable from factors such as:

- observation count;
- source diversity;
- source quality/independence;
- recency;
- method comparability;
- consistency/counterevidence;
- identity-resolution confidence.

Avoid pseudo-precise confidence numbers unless the method supports them.

## Novelty analysis

For each new run distinguish:

- already known and unchanged;
- known but changed;
- reappeared/reopened;
- genuinely new entity;
- new relation/event/property;
- new cluster/pattern.

The user should not repeatedly receive the same result set when only a small fraction is novel.

## Semantic clustering and demand/topic structures

Use embeddings/features + clustering + human/AI labels to discover recurring needs/topics/mechanics rather than treating every post/article/result as unrelated.

Examples:

- many differently worded freelance posts → one demand cluster;
- many news articles → one underlying story/event cluster;
- many game descriptions → mechanics/theme clusters.

Cluster identity should also be versioned because clusters evolve.

## Emerging / declining phenomena

Identify clusters/entities/metrics that are moving from rare to persistent or vice versa. Combine frequency, velocity, persistence, source diversity and history rather than a single threshold.

## Graph analysis

On the relation layer consider:

- co-occurrence;
- centrality;
- community detection;
- emerging relationships;
- bridges between clusters/domains;
- relationship changes over time.

Examples: skill ↔ task networks, company ↔ product ↔ person networks, game ↔ mechanic graphs.

## Personal relevance and skill-gap projections

Keep personalization separate from raw facts. Possible projections:

- personal fit;
- missing requirements;
- learning effort;
- opportunity expansion if skill X is acquired;
- items similar to user-curated positives and dissimilar to negatives.

## Counterfactual analysis

Ask “what changes if assumption/profile/action X changes?”. Examples:

- if user learns Blender, how many additional opportunities become plausible?
- if price ceiling increases, what additional app/game/product set appears?
- if a source is excluded, does the trend conclusion survive?

## Sensitivity / robustness analysis

Vary thresholds, source subsets, weights or method parameters to see whether conclusions are stable. This is particularly valuable for rankings and personal-fit recommendations.

## Capture-recapture population estimation (experimental)

Overlap between partially independent sources can sometimes estimate unseen population size. This is methodologically fragile because source independence and equal-capture assumptions often fail; treat as an optional research method with explicit assumptions, not a default metric.

## Time-aware similarity

Similarity itself can be historical:

- “items that were similar at launch”;
- “items whose trajectories evolved similarly”;
- “find games with a similar first-90-day growth curve”.

This may require sequence/trajectory representations rather than static embeddings.

## Explainable similarity

Return dimensions and reasons, not only `0.84 similarity`.

Example:

```text
mechanics      0.93
core loop      0.91
theme          0.77
visual style   0.38
audience       0.82
```

Then provide the concrete shared features that produced the score.

## Forecasting with uncertainty (future/optional)

After sufficient longitudinal history exists, evaluate forecasting separately from descriptive trend analysis. Prefer forecast distributions or prediction/credible intervals over a single point estimate, and retain out-of-sample forecast evaluation. Do not imply forecasting is reliable merely because a trend exists.

## Censoring and missingness semantics for lifecycle analysis

If lifecycle/survival analysis is implemented, explicitly preserve the accepted `not_seen != disappeared` principle. Relevant cases include:

- right censoring: an item is still active at the end of the observation period;
- source/route failure or partial coverage: absence is not an exit;
- interval censoring: exit happened between two observations;
- left truncation/delayed entry when observation began after the real lifecycle began.

A naive `last_seen - first_seen` should not automatically be treated as true lifetime. Coverage and observation-process state must participate in the analysis.

## Alert calibration / multiple comparisons (conditional)

If a future Watch/anomaly implementation performs many statistical hypothesis tests, evaluate false-discovery control and/or practical alert controls such as minimum effect size, persistence across periods, alert budgets and calibration on historical data. Do **not** mandate classical FDR when the chosen detector is not a hypothesis-testing procedure.

## Sparse-segment / hierarchical estimation (future/optional)

When overall data volume is large but a requested segment has few observations, consider minimum effective-sample rules, partial pooling/hierarchical models or shrinkage so tiny segments do not produce unstable pseudo-precise trends. The correct method is domain/data dependent.
