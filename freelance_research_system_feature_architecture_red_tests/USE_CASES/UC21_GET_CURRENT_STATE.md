# UC21 — Get Current State

## Procedure

1. Resolve the requested result scope and `fresh_only` preference.
2. Invoke the CurrentStateSnapshot projection capability if available.
3. Return the typed snapshot exactly as projected, including coverage and exclusions.
4. If inputs are insufficient/stale, return an explicit refresh recommendation; do not launch research.
5. If projection capability is unavailable, return `projection_unavailable`; do not fabricate a snapshot.
