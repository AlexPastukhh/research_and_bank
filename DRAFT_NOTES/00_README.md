# vNext draft notes — Universal Personal Research / Intelligence Bank

> **Статус с 2026-10-10: историческая справка.** Прежние ценности и evidence сохранены; новое развитие отделено от runtime. Актуальный документ: [README.md](../docs/README.md). Нижний текст сохраняет прежний контекст, не задаёт текущую очередь или закрытый enum типов.

## Status

These files are **exploration notes only**. They are additive to the existing archive and do **not** modify or supersede accepted v1.11 contracts, methods, use cases, phase acceptance records, or the current red architecture suite.

The existing system root remains unchanged. These notes are stored as a sibling top-level `DRAFT_NOTES/` directory so the accepted baseline can still be evaluated independently.

## Why these notes exist

The product goal expanded beyond freelance-opportunity research. The desired system is now closer to a reusable personal research and intelligence environment in which a user can:

- save almost anything worth keeping: games, apps, images, files, articles, job posts, opportunities, companies, notes, links, datasets, research results, sources, and tool configurations;
- organize those things in one durable bank rather than isolated per-research reports;
- reuse saved things as search seeds, comparison examples, evidence, references, collection members, or long-term monitoring subjects;
- search by exact fields, text, meaning, similarity, image, domain-specific structure, relationships, time, change, or combinations of these;
- run repeated research over time, reconcile new observations with old ones, and see current state, changes, trends, novelty, lifecycle, anomalies, and research health;
- save reusable sources in which to search and reusable tools/connectors with which to acquire or analyze data;
- let ChatGPT orchestrate research and explain results while an application UI exposes persistent state, filters, collections, history, charts, evidence, watches, sources, and tools;
- plug in ready-made acquisition, search, storage, entity-resolution, analytics, and domain-intelligence tools rather than rebuilding commodity infrastructure.

## Baseline relationship

The accepted v1.11 system already contains reusable pieces worth preserving:

- canonical use-case routing;
- explicit command/query boundary;
- execution ownership (`research_agent`, `application`, `mixed`, `internal`, `development`);
- reusable source registry concepts;
- append-only temporal observations linked to stable entities;
- comparability/method/version discipline;
- claims and evidence;
- monitoring and daily differences;
- current-state / changes / trend / interpretation / research-health result contracts;
- checkpoint/recovery/migration/audit machinery.

The major question for vNext is not whether to discard that research core, but how to place it **on top of a more general durable bank** and move freelance-only concepts into a domain pack.

## Desired scenarios — цель системы и приложения

[Желаемые сценарии системы и приложения](research_bank_desired_scenarios.md) собирают найденные цели и пути в одном читаемом документе: ближайшее первое использование, целевой продукт, условные расширения, 74 карточки с устойчивыми IDs, ожидаемые результаты и SRU верхнего уровня. Начните с разделов 1–3; полные карточки находятся в разделе 4.

Статус — **candidate / TRANSACTION OPEN**. Документ основан на закреплённом снимке источников, сохраняет различие Needs/FR/решений/предложений и не заменяет intent map, принятые контракты v1.11 или текущий план версий.

## Suggested reading order

1. `01_PRODUCT_VISION.md`
2. `02_UNIVERSAL_BANK_MODEL.md`
3. `03_DISCOVERY_RESEARCH_WATCH.md`
4. `04_ANALYTICS_IDEAS.md`
5. `05_SOURCES_TOOLS_INTEGRATIONS.md`
6. `06_CHATGPT_UI_INTERACTION_SCENARIOS.md`
7. `07_BASELINE_GAP_MAP.md`
8. `08_IDEA_BACKLOG_AND_OPEN_DECISIONS.md`
9. `09_GOLDEN_SCENARIOS.md`
10. `10_REVIEW_CORRECTIONS.md`
11. `11_MASTER_REQUIREMENTS_AND_EXTENSION_AXES.md` — current authoritative map of vNext user intent, staged requirements, conditional triggers, anti-goals and expansion axes
12. `12_REASONING_AND_SCOPE_RULES.md` — rules for future ChatGPT/architecture reasoning against the intent map
13. `REQUIREMENTS_MAP.json` — machine-readable summary of requirement classes, current strategy and extension axes
14. `REVIEW/` — durable review/meta-review ledger and correction history
15. `REVIEW/README.md` — review classification/history policy

No item here should become a requirement merely because it is written down. Each proposal needs later architecture review, scope selection, and explicit acceptance.

## Product-intent map

`11_MASTER_REQUIREMENTS_AND_EXTENSION_AXES.md` is the current authoritative **intent map inside the draft layer**. It does not automatically turn every future idea into an implementation requirement and does not supersede accepted v1.11. It is used to distinguish core intent, MVP needs, target needs, conditional requirements, experiments, opportunities, open decisions and anti-goals.

Future design/review work should classify proposed changes against that map and the `AX-Vxx` extension axes before changing implementation contracts.

## Review findings are durable project knowledge

Review and meta-review results are stored under `DRAFT_NOTES/REVIEW/`. Confirmed problems, possible future problems, opportunities, uncertain questions, rejected/downgraded findings and confirmed strengths keep stable IDs and assessment history. A later meta-review reclassifies a finding instead of erasing the earlier assessment.

## Review-correction status

The first independent review and subsequent meta-review are preserved under `DRAFT_NOTES/REVIEW/`. Confirmed draft ambiguity around Lens/Recipe/Watch/SourceRoute ownership has been corrected in the notes through explicit concern ownership and immutable `RunSpec` compilation. Other review ideas remain explicitly marked future/conditional where appropriate rather than being retroactively promoted to accepted requirements.
