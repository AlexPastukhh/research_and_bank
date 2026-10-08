# Idea backlog and open decisions

This document captures ideas so they are not lost. It is not a commitment to implement them all.


## Tentative design decisions adopted after independent review

These are still vNext draft decisions, not accepted v1.11 contracts:

- separate configuration authority: `Lens = what`, `SourcePolicy = allowed/preferred sources`, `SourceRoute = source-specific access`, `Recipe = execution method`, `Watch = cadence/alerts`;
- compile every execution into an immutable `RunSpec`; no silent “last object wins” precedence;
- preserve exact historical search/research membership through a `ResultSet`/`ResultOccurrence`-style lineage contract;
- arbitrary saved material is not automatically independent evidence; retain epistemic class/derivation/independence semantics;
- for news, distinguish Publication/Article, derived Story/Narrative grouping, and real-world Event;
- central similarity/search modes should eventually have versioned retrieval evaluation sets and relevance judgments.

## Bank / organization ideas

- save arbitrary object/file/link/note with one action;
- mixed collections;
- nested collections or saved views;
- manual + AI-assisted tags;
- favorites/pins/archive states;
- item roles independent of item type;
- backlinks: “where has this item been used?”;
- research lineage from item to every run/claim/result that referenced it;
- user annotations distinct from machine-extracted facts;
- import browser bookmarks/local folders/exports later;
- optional dedupe on import with explicit conflict handling.

## Similarity ideas

- visual similarity;
- semantic image similarity;
- style similarity;
- perceptual duplicate detection;
- game mechanics similarity;
- core-loop similarity;
- trajectory similarity over time;
- “similar to all these positive examples”;
- positive examples + negative examples (“like these, but not those”); — triaged as `OPP-017`, `TARGET_REQUIRED` on 2026-10-05, outside MVP. See the authoritative map/master for dimension selection, soft preference vs hard exclusion, explanations and quality evaluation.
- explainable dimension-level similarity;
- user-defined similarity profiles;
- collection-level prototype/centroid plus diverse-result retrieval.

## Search ideas

- bank only / my sources / my sources + web / selected sources modes;
- natural-language → structured/hybrid query;
- saved query/lens;
- historical “as known then” search;
- “first appeared between dates”;
- “changed in the last N days”;
- “new relationships around this item”;
- graph-neighborhood search;
- cross-modal text→image and image→text/item search;
- search result explanation: matched fields/representations/relations.

## Watch ideas

- watch entity;
- watch collection;
- watch query;
- watch similarity neighborhood;
- watch relation/event;
- watch metric threshold;
- watch source health;
- watch for original/source of saved media;
- cadence per watch;
- budgets/cost caps;
- alerts with novelty suppression to avoid repeated noise;
- pause/resume/history of watch policy changes.

## Research ideas

- research lens independent of project;
- reusable research recipe;
- immutable compiled RunSpec for every execution;
- historical ResultSet/ResultOccurrence lineage;
- recipe versions;
- run against frozen source set for comparability;
- run against current source set for freshness;
- branch/clone a lens;
- compare two lenses;
- combine several saved objects into a research question;
- automatically suggest research when a saved collection has enough material, but never start expensive work silently.

## Analytics ideas

- distributions/quantiles;
- demand/frequency/value/competition matrices;
- velocity, persistence, lifecycle/survival;
- cohorts;
- change points;
- concept drift;
- anomalies;
- distribution shifts;
- seasonality;
- source divergence;
- coverage-normalized metrics;
- novelty/new-vs-known decomposition;
- semantic clustering;
- emerging/declining clusters;
- graph analysis;
- personal-fit projections;
- skill-gap analysis;
- counterfactual scenarios;
- sensitivity/robustness analysis;
- Pareto frontiers;
- experimental capture-recapture estimates;
- trajectory similarity;
- forecasting with uncertainty and out-of-sample evaluation (optional, after enough history);
- explicit censoring/missingness semantics for lifecycle/survival;
- conditional alert/multiple-comparison calibration for mass statistical watches;
- sparse-segment/hierarchical estimation or minimum effective-sample rules.

## UI ideas

- Bank home;
- object/entity detail with timeline;
- collection detail;
- Discover/search builder;
- Research lens/recipe editor;
- Run history;
- Current State;
- Changes;
- Trends;
- Watch center;
- Sources;
- Tools/connectors;
- evidence/provenance drilldown;
- research health;
- ChatGPT side panel that can operate on selected UI objects/current view;
- “use selection as seed” action everywhere.

## ChatGPT ideas

- user can refer to bank items conversationally (“that colony game we analyzed”);
- ChatGPT retrieves rather than relying on chat memory;
- ChatGPT can propose a lens/recipe but application persists it;
- selected UI items become chat context by stable IDs;
- every analytical claim can expose evidence/limitations;
- ChatGPT can ask for confirmation before costly/broad external runs;
- deterministic tool actions remain application-enforced.

## Security/privacy/compliance questions

- local-first vs cloud storage boundaries;
- encryption and secret/credential storage;
- per-source terms of service and robots/compliance;
- user-owned/private source access;
- deletion/retention/export guarantees;
- sensitive personal data in saved material;
- model-provider data exposure for embedding/analysis;
- whether representations can be recomputed locally;
- permission model for autonomous scheduled watches.

## Data model open decisions

- exact distinction/naming among BankItem, Asset, Entity, Note, Document, Observation;
- global bank vs workspace/project scopes;
- how domain schemas evolve;
- merge/split identity semantics;
- relation typing/extensibility;
- representation storage/versioning;
- bitemporal support in MVP vs later;
- immutable raw capture retention policy;
- provenance granularity and storage cost.

## Product open decisions

- product name and primary navigation;
- whether “Research Project” remains user-facing or becomes one kind of workspace/lens;
- which first domains prove universality (recommended: freelance, games, apps, news);
- which data acquisition providers are affordable/allowed;
- build-vs-buy comparison for the personal knowledge / AI workspace / reference-manager layer before building commodity Bank/UI features;
- what is local/private vs shared/syncable;
- what can run automatically vs requires explicit approval;
- notification/alert channels;
- offline mode expectations.

## Architecture open decisions

- Postgres + object storage + vector/search stack vs simpler local-first stack;
- one search engine vs separate lexical/vector/graph indices;
- how much graph capability needs a graph DB vs relations in relational store;
- async job/orchestration framework;
- plugin/domain-pack packaging contract;
- MCP boundary vs internal API boundary;
- testing strategy for probabilistic/LLM components;
- versioned SearchEvaluationSet/RelevanceJudgment/SearchEvaluationRun for important retrieval modes;
- reproducibility requirements for AI-generated representations/annotations.

## Important anti-goals / traps

- do not make vacancy/job the universal root object;
- do not make Research Project own all data;
- do not equate “not seen” with disappearance;
- do not equate page change with real-world entity change;
- do not treat embeddings/vector indexes as canonical truth;
- do not mix raw facts with AI interpretation;
- do not silently overwrite history;
- do not use one opaque similarity score for every purpose;
- do not create one giant GenericObject schema;
- do not hide source disagreement inside one aggregate;
- do not silently refresh when user asked only for a query;
- do not implement every analytics idea before clear user value.


Triage preservation (2026-10-06): all current bullets are indexed in BACKLOG_TRIAGE.json, linked from REQUIREMENTS_MAP.json. NEW/split destinations remain proposals in NORMALIZATION_PROPOSALS.json; use current requirement scope and explicit proposal states rather than treating this inbox as a delivery promise. Original bullets and ordering are retained.
