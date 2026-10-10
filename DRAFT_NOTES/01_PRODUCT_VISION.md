# Product vision draft

> **Статус с 2026-10-10: историческая справка.** Прежние ценности и evidence сохранены; новое развитие отделено от runtime. Актуальный документ: [PRODUCT.md](../docs/PRODUCT.md). Нижний текст сохраняет прежний контекст, не задаёт текущую очередь или закрытый enum типов.

## Working formulation

A **personal research and intelligence bank** that lets the user save arbitrary useful things, search and discover related things, repeatedly research chosen areas, preserve source-level evidence and historical state, and analyze how the observed world changes over time.

ChatGPT, the application UI, the durable bank, the research engine, monitoring, analytics, and external tools should feel like one product even though they have separate responsibilities.

## Product is not centered on vacancies

Freelance opportunities and vacancies remain valuable domain objects, but they are only one application of the system. Other intended domains include:

- games and game mechanics;
- mobile/desktop/web applications;
- news, stories, events, companies, people and topics;
- products and prices;
- technologies, libraries and adoption signals;
- media and images;
- arbitrary user-curated reference material;
- future domain-specific object types.

The reusable core must therefore avoid treating `service unit`, `job`, `salary`, `payout`, `Steam`, `news`, etc. as universal concepts.

## Core product verbs

### Save
Save an object, file, image, URL, note, source, tool configuration, search result, research result, or collection without requiring an active research project.

### Organize
Tag, annotate, relate, collect, pin, archive, and classify saved material. Organization can be user-authored, rule-derived, or AI-assisted but must keep provenance.

### Search
Search the bank using structured filters, text, semantic meaning, similarity, images, domain attributes, relations, time, historical state, changes, and hybrid combinations.

### Discover
Use saved items, collections, queries, or research lenses as seeds to find new things inside the bank and in external sources.

### Research
Run reproducible research with explicit scope, sources, methods, tool versions, captured evidence, normalization, measurement, claims, and typed result products.

### Watch
Continuously or periodically re-observe an entity, collection, query, similarity neighborhood, relationship, metric, or research lens.

### Analyze
Produce current state, changes, trends, distributions, clusters, novelty, lifecycle, anomalies, confidence, source divergence, personal relevance, and other derived views while preserving raw evidence.

### Explain
Allow ChatGPT to answer questions such as “why do we think this?”, “what changed?”, “what is similar and in what sense?”, and “what evidence supports this?” using traceable result/evidence links.

## Key lifecycle

```text
save / discover / ingest
        ↓
universal bank
        ↓
represent / normalize / resolve identity
        ↓
search / compare / research / watch
        ↓
new observations and derived analysis
        ↓
current state + history + changes + trends
        ↓
user decisions / further discovery
        ↓
bank grows and becomes a better search/research substrate
```

## Critical product principle: Bank → Web → Bank

A saved thing should be usable as a query seed:

```text
saved item or collection
        ↓
internal bank search
        ↓
external discovery when requested/needed
        ↓
new candidates
        ↓
compare / inspect / research
        ↓
selected candidates saved back to bank
```

This feedback loop is central to the desired product.

## Research is a role, not ownership of all stored data

A game, image, company, article, source, or other item may exist in the bank before any research exists. The same canonical item can later participate in many research runs in different roles:

- seed;
- candidate;
- result;
- evidence;
- counterexample;
- comparison item;
- reference;
- monitored subject.

Research should reference bank objects, not duplicate or exclusively own them.

## Domain packs

The universal core supplies protocols and storage. Domain packs supply domain meaning.

A domain pack may declare:

- entity types;
- event types;
- domain properties/facets;
- metric definitions;
- identity rules;
- extraction schemas;
- source adapters/routes;
- normalization rules;
- comparison/similarity profiles;
- analysis recipes;
- default research lenses;
- UI presentation hints.

Examples: `freelance`, `games`, `apps`, `news`.

## Personalization is a projection, not raw truth

“Useful to me”, “fits my skills”, “interesting”, “similar to what I like”, or “worth watching” should normally be derived from global/shared observations plus a user profile or user lens. Raw entities should not be mutated to contain one user’s personal relevance as if it were universal fact.
