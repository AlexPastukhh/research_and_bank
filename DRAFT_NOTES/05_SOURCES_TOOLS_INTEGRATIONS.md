# Sources, tools and integration ideas

> **Статус с 2026-10-10: историческая справка.** Прежние ценности и evidence сохранены; новое развитие отделено от runtime. Актуальный документ: [AI_WORKFLOW.md](../docs/AI_WORKFLOW.md). Нижний текст сохраняет прежний контекст, не задаёт текущую очередь или закрытый enum типов.

## Sources are durable reusable objects

A source is not just a URL used once. It should be saveable, reviewable, groupable and reusable across research.

Possible source metadata:

- name/type/location;
- domain/topic usefulness;
- source role (`discovery`, `evidence`, `both`, `archive` or future roles);
- trust/quality notes;
- provenance/ownership;
- access restrictions;
- general and task-specific priority;
- last checked / health;
- allowed access methods;
- cost/rate limits;
- source groups/collections.

Examples:

- a subreddit;
- Steam/App Store/Google Play;
- a specific website;
- RSS feed;
- GitHub repository;
- YouTube channel;
- API;
- local folder;
- database;
- document archive;
- news dataset.

The accepted v1.11 `SourceInbox → SourceRegistry → SourceReviews → SourceUsePlan` model is a strong starting point.

In vNext, Source and Entity are separate canonical types. A Source may optionally reference a subject/provider Entity; saving a Source does not require creating an Entity. For example, a local archive folder may have no Entity link, while Reuters website and Reuters RSS Sources may reference the same Reuters organization Entity. Entity merge/split does not automatically merge/split these Sources. This confirms the identity boundary without choosing persisted field names/cardinality or migrating v1.11 records.

## `SourceRoute`

A source and a concrete way of querying it should be distinct. `SourceRoute` belongs to `Source`, not to an optional linked Entity. Changing route configuration does not change Source identity; reusable route history remains TARGET work.

Example:

```text
Source: Reddit
Route:
  subreddits = [gamedev, indiegames]
  query = "inventory system"
  sort = new
  lookback = 30d
```

or:

```text
Source: Steam
Route:
  category = Strategy
  released_after = 2024
  reviews > 100
```

Route history matters for comparability and reproducibility.

## Tool / Connector Registry

Tools are “how”, sources are “where”. A reusable registry can track:

- capability names;
- input/output contracts;
- supported source types;
- tool/version;
- reliability/health;
- cost and rate limits;
- credential reference (not raw secrets in general metadata);
- deterministic vs semantic behavior;
- side effects;
- provenance fields to attach to outputs.

Potential capabilities:

```text
crawl_site
search_web
fetch_api
extract_entities
extract_structured_data
find_similar_images
find_similar_entities
resolve_identity
compute_embedding
cluster_items
detect_change_point
detect_drift
query_news
query_app_market
```

## Ready-made systems/components to evaluate

This is an evaluation backlog, not an adoption decision. Capabilities/licensing/pricing should be rechecked at implementation time.

### Retrieval / search providers

Treat these as candidate executors for search capabilities, not required architecture dependencies:

- **ChatGPT native web search / Deep Research** — current default interactive research channel.
- **Exa** — AI-oriented semantic/web retrieval candidate, useful for testing alternate discovery and marginal useful-source contribution.
- **Tavily** — search/extract/crawl/research-oriented agent web infrastructure candidate.
- **Parallel Search** — another AI-oriented retrieval/extraction candidate for provider-diversity experiments.
- **Brave Search API** — candidate independent search-index channel when an additional classic web index is useful.
- **SerpAPI-style SERP access** — useful when the requirement is specifically to observe/query classic search-engine result pages rather than semantic retrieval.
- **Perplexity** — useful as a manual/consumer research benchmark or separate retrieval/research channel; consumer subscription and programmatic API should be treated as separate purchasing/integration decisions.

Do not adopt multiple search providers merely for variety; compare marginal independent/useful evidence and cost.

### Acquisition / crawling

- **Apify** — hosted actors, browser/scraping jobs, reusable input/output jobs, scheduling; useful as connector/execution infrastructure.
- **Firecrawl** — web extraction and page change tracking; useful for web capture, but page change must not be confused with entity change.
- **Airbyte** — structured API/database connectors and replication for sources that fit connector-style ingestion.
- custom browser/API adapters where domain semantics or compliance require them.

### Browser interaction / difficult sites

- **ChatGPT Computer Use / browser-capable execution** and provider tools such as **TinyFish** are candidates when the task requires navigating an interactive site, clicking, filtering, or reading state that cannot be handled as ordinary search/extraction.
- Browser interaction should remain a capability (`browser_interact`) rather than a dependency on one provider.

### Personal knowledge/source connectors

- **Readwise/Reader** and similar services are useful reference/integration candidates for searching user-saved reading/highlights. They may act as an external personal Source rather than replacing the Universal Bank.

### News

- **GDELT** — large global news/event source; promising as a News domain adapter and historical/near-real-time signal source.

### Web entities / enrichment

- **Diffbot** — structured web extraction/knowledge-graph-style entities; evaluate for entity enrichment and provenance.

### App/game intelligence

- specialized providers such as **Sensor Tower** and **Similarweb App Intelligence** can provide data that would be expensive to reproduce. Use adapters where licensing/value makes sense rather than pretending to own their acquisition stack.

### Entity resolution

- **Splink** — probabilistic record linkage candidate for deduplication/linking when no stable common ID exists.

### Storage / analytical execution

Possible staged stack:

```text
PostgreSQL for canonical transactional metadata/state
Parquet/object storage for immutable raw captures/history
DuckDB for local/embedded analytical workloads
TimescaleDB if time-series scale/query patterns justify it
ClickHouse later for very large analytical/event volumes
```

### Search / vectors

Candidates to evaluate:

- OpenSearch for lexical + vector + hybrid search and aggregations;
- Qdrant for vector search and multiple named vector representations;
- Weaviate for multimodal/multi-target vector search.

Do not let a vector DB become canonical truth. It is an index/derived representation store.

### Analytics libraries

- `ruptures` for change-point detection;
- `River` for streaming/concept-drift techniques;
- standard scientific Python/statistics stack for distributions, survival/cohort analysis, clustering, etc.

### Personal knowledge / universal-bank references and partial substitutes

The build-vs-buy survey must include products closer to the **save anything → organize → retrieve/search → AI-assisted workspace** layer, not only data infrastructure and enterprise market-intelligence systems. These are comparison/reference candidates, not adoption decisions.

- **Fabric** — current product materials describe capture of links, files, images/screenshots, notes and other media into one searchable workspace; semantic/visual retrieval, AI assistance, and MCP access make it a particularly relevant reference for the Universal Bank + AI interaction layer. Evaluate export/data ownership, APIs, local/cloud boundaries, automation depth and whether its model can support our historical research/temporal contracts before considering reuse.
- **Zotero** — a mature durable research/source bank with typed items, arbitrary file attachments, notes, web snapshots, browser capture and RSS feeds. It is a strong reference/possible component for source/reference management, but it does not by itself replace our domain entity resolution, temporal monitoring, multi-aspect similarity or repeated research analytics.
- **Other personal knowledge/reference/media-library products** — survey as a product class (for example local-first knowledge bases, bookmark/read-later systems, visual asset libraries and research managers) before building commodity capture/organization UI from scratch. Do not assume feature parity without an explicit comparison matrix.

Recommended comparison axes:

```text
arbitrary capture/media support
canonical IDs and exportability
full-text/semantic/visual search
collections/relations/backlinks
source/provenance fidelity
version/history model
API/MCP/automation surface
local/private/cloud storage boundaries
external discovery and connector support
temporal observation/watch support
research-run/result lineage
domain-pack extensibility
cost/licensing/vendor lock-in
```

The likely outcome may be **integration or reference reuse**, not necessarily full replacement. The specific evaluation should be redone near implementation because product capabilities and pricing change.

Official references checked during the review-correction pass (2026-10-05):

- Fabric research workspace: https://fabric.so/use-cases/research
- Fabric quick capture / visual search: https://fabric.so/features/quick-capture
- Fabric MCP integration: https://fabric.so/features/mcp
- Zotero quick start / item, file, snapshot and feed model: https://www.zotero.org/support/quick_start_guide

These links are evidence for the current comparison notes, not a compatibility guarantee. Recheck them when making an implementation/adoption decision.

### Full-platform/reference alternatives

Evaluate platforms as benchmarks or partial replacements rather than assuming we must build everything:

- Palantir Foundry — ontology-centric analytical/operational platform; closest conceptual reference for entity/property/relation/action modeling, but likely heavy/enterprise for this product.
- Databricks — strong data/lakehouse/ML platform; can replace a large amount of data infrastructure but not the product-specific research methodology and interaction model.
- AlphaSense / Feedly AI — relevant if the product were narrowed to market/company/news intelligence; less suitable as a universal personal bank with arbitrary saved objects.

## MCP / AI integration

Expose product capabilities through a stable tool/resource protocol so ChatGPT is an orchestrator, not the database.

Conceptual resources:

```text
bank://entities/...
bank://collections/...
research://runs/...
source://...
```

Conceptual tools:

```text
bank.save
bank.search
bank.find_similar
bank.link
source.register
source.search
research.run
research.compare
watch.create
watch.pause
```

MCP is a candidate interoperability layer; the core application API should remain independently usable by UI/background jobs/tests.

## Provenance must cross tool boundaries

Each acquired/derived result should retain enough lineage to answer “where did this come from?”:

```text
source_id
source_route_id
tool_id
tool_version
run_id
captured_at
raw_capture_id
normalization/extraction version
analysis method/version
```

Ready-made tools reduce implementation effort but do not remove the need for our provenance, entity identity, temporal semantics and research-health contracts.

## Current execution strategy: ChatGPT-first, integrations only when justified

The current vNext direction is **not** to directly integrate every useful provider into the application.

Interactive research can initially be executed by ChatGPT using native web/Deep Research and available connectors/tools. The application should concentrate on durable Bank/history/research state/provenance/UI.

Model the need as:

```text
Capability
  ↓ executed by
CapabilityExecutor
```

Example:

```text
Capability: semantic_web_search
Executors:
  - ChatGPT + Exa connector
  - direct Exa API (future/conditional)
  - another provider
```

or:

```text
Capability: crawl_site
Executors:
  - ChatGPT + Firecrawl connector
  - direct Firecrawl API
  - Apify Actor
```

A direct application integration becomes justified only when a concrete trigger exists, such as:

- unattended/scheduled execution;
- bulk/high-volume ingestion;
- materially better cost/latency;
- exact provider-parameter reproducibility;
- a capability unavailable through ChatGPT-accessible tooling;
- reliability/data-governance requirements;
- direct streaming into persistent projections without an interactive chat step.

Until then, avoid duplicating commodity provider clients inside the application.

## Retrieval-provider experiments

Candidate retrieval channels can include native ChatGPT search/Deep Research and external providers such as Exa, Tavily, Parallel or future alternatives. Their value should be measured empirically rather than inferred from brand/provider diversity.

A useful experiment compares providers on real research questions using metrics such as:

- marginal useful sources;
- primary-source discovery;
- independent evidence contribution;
- counterevidence contribution;
- overlap/duplicates;
- cost/latency;
- failure/access rate.

This experiment can determine whether any provider deserves a direct backend integration later.
