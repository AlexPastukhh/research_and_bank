# Screen map

## 01 Current State
Questions answered:
- What is the latest valid state across all research?
- What is current for one direction?
- Which stale results were excluded?

Primary product: `CurrentStateSnapshot`.

## 02 Direction Detail
Questions answered:
- What do we currently know about Programming / Pixel Art / Testing / etc.?
- Latest metrics, economics, changes, risks and coverage?

Primary products: scoped `CurrentStateSnapshot` + latest `ChangeSet` + selected `TrendSeries`.

## 03 Daily Changes
Questions answered:
- What appeared today?
- What changed?
- What explicitly closed or reopened?
- What is merely not seen?

Primary product: `ChangeSet`.

## 04 Trends
Questions answered:
- Is a metric rising, falling or stable?
- What changes over 7d/30d/90d/week/month/custom windows?
- How much of the trend is supported by comparable coverage?

Primary product: `TrendSeries`.

## 05 Interpretations
Questions answered:
- What do the current results mean overall?
- What changed in a selected period?
- What are the caveats and confidence?

Primary product: `InterpretationRecord`.

## 06 Coverage & Quality
Questions answered:
- Can we trust this view?
- What is stale, partial, incompatible or missing?
- Which areas need refresh?

Primary product: `ResearchHealthSnapshot`.
