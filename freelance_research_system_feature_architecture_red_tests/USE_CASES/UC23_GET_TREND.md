# UC23 — Get Trend

## Procedure

1. Resolve metric, scope, grain and time range.
2. Request TrendSeries from existing comparable metric history.
3. Return raw points/coverage together with separately derived trend statistics.
4. Surface incompatible or missing windows instead of bridging them silently.
5. If additional measurement is needed, recommend refresh; do not perform UC08 implicitly.
