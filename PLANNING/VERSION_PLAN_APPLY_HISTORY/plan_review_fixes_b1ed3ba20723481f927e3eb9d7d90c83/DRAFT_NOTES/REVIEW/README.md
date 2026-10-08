# Review findings ledger — draft governance

## Purpose

Review and meta-review findings must not exist only in chat. They are durable project knowledge and should be stored with enough context to distinguish:

- a **confirmed problem** in the current proposal/result;
- a **possible future problem / conditional risk** whose mechanism is plausible but whose trigger or contract is not yet present;
- a **future opportunity / improvement idea** that is useful but was not a requirement of the reviewed work;
- an **open or uncertain question** that still needs evidence or a design decision;
- a **rejected, disproved, or downgraded finding** that was raised in an earlier review but did not survive independent re-checking;
- a **confirmed strength / passed check** when preserving positive review evidence is important to later decisions;
- a **resolved-at-draft-level finding** when the proposal text has been corrected but runtime implementation/acceptance has not yet occurred.

The ledger is additive. Meta-review must update a finding's classification/history rather than erase the fact that the earlier review raised it.

## Why this matters

Without a durable ledger, later work can accidentally:

- rediscover the same issue repeatedly;
- implement an idea that was only a speculative risk as if it were a required fix;
- forget a real problem after chat context is lost;
- lose the reasoning that caused a finding to be downgraded or rejected;
- confuse baseline defects with gaps created only by a later product expansion;
- lose useful future opportunities that were intentionally deferred.

## Finding lifecycle

Suggested lifecycle:

```text
raised
  -> confirmed
  -> planned
  -> implemented
  -> verified
  -> closed
```

Alternative branches:

```text
raised -> conditional / future-risk -> deferred
raised -> future-opportunity -> backlog
raised -> uncertain -> investigate
raised -> downgraded
raised -> rejected / disproved
```

A later meta-review should append a new assessment event. It should not rewrite the original review event.

## Required fields for substantial findings

At minimum retain:

- stable finding ID;
- date/review ID where first raised;
- reviewed object and scope;
- classification at that time;
- current classification;
- severity/impact;
- related user goal / requirement / baseline contract;
- finding statement;
- trigger conditions;
- causal mechanism;
- observable problematic situation;
- consequence;
- evidence references or explicit evidence limitation;
- whether the issue affects the main result or is local;
- disposition / next action;
- assessment history, including meta-review reclassifications.

For future opportunities and possible future problems, explicitly state that they were **not requirements of the earlier work** unless they actually were.

## Evidence policy

A finding is not `confirmed_problem` merely because it sounds plausible or because an Error Axis exists. Confirmation requires either:

- a reproducible scenario;
- direct contradiction of a current contract/requirement;
- independently verified evidence;
- or an explicit design inconsistency that makes the stated behavior ambiguous under reachable conditions.

If evidence is incomplete, store that limitation and use `possible_future_problem`, `uncertain`, or another non-confirmed classification.

## Files

- `FINDINGS.json` — machine-readable current ledger plus assessment history.
- `2026-10-05_ARCHIVE_REVIEW.md` — first independent review of the Universal Bank vNext draft archive.
- `2026-10-05_META_REVIEW.md` — independent review of that review, including reclassifications and newly found omissions.
- `2026-10-05_REVIEW_CORRECTIONS.md` — additive correction record showing which review findings were integrated into the vNext draft notes and which remain future/conditional.
- `2026-10-05_MASTER_REQUIREMENTS_REVIEW.md` — independent review of the authoritative vNext product-intent/master-requirements map, including confirmed registry/parity/completeness issues and deferred follow-up triggers.

These review records are themselves draft governance material. They do not modify accepted v1.11 contracts.

## Current critical plan/requirements review

- `2026-10-05_PLAN_REQUIREMENTS_CRITICAL_REVIEW.md` — full critical review, confirmed gaps vs uncertainties/deferred and limitations.
- `2026-10-05_PLAN_REQUIREMENTS_CRITICAL_REVIEW_LOG.md` — compact Review Log for later work.
- `2026-10-05_PLAN_REQUIREMENTS_CRITICAL_REVIEW_CHECKS.json` — independent artifact/count/parity evidence.

This review appends assessment history and preserves prior reviews; it does not apply the outstanding intent/plan fixes or close them.


## Full vNext plan review — 2026-10-06

- `../../PLANNING/FULL_PLAN_REVIEW_2026-10-06.md` — independent complete plan review: current problems, uncertainties, passed checks, user assistance, deferred items and proposals.
- `2026-10-06_FULL_PLAN_REVIEW_LOG.md` — compact durable Review Log; earlier reviews/history retained.
- `2026-10-06_FULL_PLAN_REVIEW_CHECKS.json` — fresh source hashes, independent graph/coverage/negative findings and seven native check outputs.
- `../../PLANNING/FULL_PLAN_REVIEW_2026-10-06_SAVE_RECEIPT.json` — guarded-write/readback/baseline evidence.
