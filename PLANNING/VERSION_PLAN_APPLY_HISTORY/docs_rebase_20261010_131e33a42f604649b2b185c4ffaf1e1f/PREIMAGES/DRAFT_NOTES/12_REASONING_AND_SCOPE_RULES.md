# Reasoning and scope rules for future architecture work

## Purpose

Use this note together with `11_MASTER_REQUIREMENTS_AND_EXTENSION_AXES.md` whenever evaluating a new feature, provider, domain, analytics method, or architecture change.

## 1. Start from intent, not from available technology

Do not ask first “Can Exa/Tavily/Firecrawl/VectorDB X do this?”. Ask:

1. What user outcome is required?
2. What durable state must exist afterward?
3. What capability is needed?
4. Who should own that capability/state?
5. Which executor can provide it most cheaply/reliably now?

Providers are replaceable executors; product semantics should not depend on their brand names.

## 2. Separate present requirement from future possibility

A feature belongs in the current implementation only if it is:

- required by `MVP_REQUIRED`; or
- a dependency of another currently accepted requirement; or
- a `CONDITIONAL_REQUIRED` whose trigger is already true; or
- explicitly promoted after evidence/review.

Otherwise preserve it as a future opportunity/experiment/open decision.

## 3. New requirements do not retroactively make old work wrong

When user intent expands, record:

- previous scope;
- new requirement;
- date/context of change;
- affected contracts/components;
- whether migration is required.

Do not relabel a previously correct result as defective merely because the target product later grew.

## 4. Prefer capability contracts over provider integrations

Example:

```text
Capability: semantic_web_search
Executors:
- ChatGPT + Exa connector
- direct Exa API
- future provider
```

Research logic requests the capability. Direct application integration is only one execution choice.

## 5. Keep canonical truth, evidence, derived representations, and projections distinct

Ask of every stored item:

- Is this a raw capture?
- A canonical entity identity?
- A source observation?
- A user/AI annotation?
- A derived representation/index?
- An analytical projection?
- A research result occurrence?

Do not allow a vector score, generated caption, AI summary, ranking, or dashboard projection to silently become raw truth.

## 6. For repeated research, freeze execution and output history

A completed run should retain enough immutable data to explain/reconstruct:

- what semantic intent was executed;
- what source boundary/routes applied;
- what methods/tools/versions applied;
- what coverage/result set occurred;
- which results appeared and why/rank when relevant;
- what observations/evidence were produced.

Current models/indexes may change later without rewriting that historical fact.

## 7. Distinguish exploration from measurement

Discovery answers “what might exist?”. Measurement/trend claims require a valid observation/sampling/comparability design. Do not convert search-result counts into market-demand estimates by default.

## 8. Treat “complete” as scope-relative

Never say “complete current state” without an explicit scope/method/coverage interpretation. The internet/market is not globally exhaustible by default.

## 9. Prefer Bank-first reuse, but do not trap research inside the Bank

Default order can be:

1. existing bank;
2. saved/preferred sources;
3. available external providers;
4. broad discovery when allowed.

But old bank content must not be allowed to self-confirm claims without provenance/independence checks.

## 10. Evaluate external providers empirically

Multiple providers are not automatically independent. Prefer experiments measuring:

- overlap;
- marginal useful sources;
- primary-source discovery;
- new independent evidence;
- counterevidence;
- cost/latency/quality.

## 11. Every significant proposed change should name extension axes

Use `AX-V01...AX-V22` from the master map. A change that spans many axes is probably not a small feature and should be reviewed as a broader scope change.

## 12. Review findings remain durable

When a review discovers a problem/risk/opportunity:

- add/update the durable review ledger;
- preserve original classification/history;
- connect the finding to the affected requirement/axis;
- reclassify rather than delete after meta-review.

## 13. Escalation test for architecture changes

Treat a proposal as a major architecture amendment if it changes any of:

- ownership of canonical data;
- dependency direction around Universal Bank;
- command/query boundary;
- historical immutability/provenance;
- definition of RunSpec/result occurrence;
- Domain Pack/core boundary;
- execution owner/capability model;
- current-state/comparability semantics;
- user privacy/data ownership boundary.

## 14. Minimum evidence before building commodity infrastructure

Before implementing a crawler/search-provider integration/vector store/etc. inside the app, show at least one concrete reason existing ChatGPT/tool execution is insufficient:

- automation;
- volume;
- cost;
- reproducibility/control;
- missing capability;
- reliability;
- data governance/security;
- latency/user experience.

If none applies, defer the integration.
