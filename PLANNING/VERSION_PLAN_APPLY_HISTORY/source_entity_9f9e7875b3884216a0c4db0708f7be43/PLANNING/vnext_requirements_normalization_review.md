# Нормализация требований vNext — предложения до изменения registry

Дата: 2026-10-05. Версия отчёта: 1.1. Обновление 2026-10-05: OPP-017 утверждён как TARGET_REQUIRED вне MVP.

**Результат:** просмотрены все 115 записей `REQUIREMENTS_MAP.json`, все 159 bullet-пунктов `08_IDEA_BACKLOG_AND_OPEN_DECISIONS.md`, human master и связанные сценарии/ревью. После решения по OPP-017: 55 KEEP, 55 CLARIFY, 4 SPLIT и 1 CHANGE_STATUS. Удаление исходных записей не предлагается. Большинство предложений остаётся непринятым. Единственная применённая правка этой редакции — OPP-017: FUTURE_OPPORTUNITY → TARGET_REQUIRED, вне MVP; карта, master, backlog-ссылка и scenario note обновлены в сопровождающем ZIP.

Главная правка — сделать inventory однозначным: записать ранее принятые решения, устранить различия master/JSON, классифицировать все идеи backlog и добавить traceability. Не требуется пересматривать продукт с нуля или расширять MVP всеми идеями.

## Решение этой редакции: OPP-017

Пользователь утвердил поиск по положительным и отрицательным примерам как **TARGET_REQUIRED, вне MVP**. Принимаются: указание учитываемых/нежелательных dimensions, выбор мягкого снижения ранга или жёсткого исключения и объяснение фактических match/exclusion reasons. Улучшение качества проверяется на сравнении с поиском без отрицательных примеров, с human relevance judgments.

Первоначальная рекомендация отчёта оставить OPP-017 в FUTURE отменена этим решением. Ниже сохранён baseline snapshot исходных 115 entries: поэтому OPP-017 остаётся в разделе исходных FUTURE записей и исходная count table показывает 24 TARGET / 20 FUTURE. **Текущая map после правки: 25 TARGET / 19 FUTURE, всего 115 entries.** ID OPP-017 сохранён. Другая нормализация пока не применена.

## 1. Граница проверки и исходные данные

Исходный архив: `freelance_research_system_with_universal_bank_vnext_master_requirements_reviewed(1).zip`.

Полностью прочитаны: `REQUIREMENTS_MAP.json`, `11_MASTER_REQUIREMENTS_AND_EXTENSION_AXES.md`, `08_IDEA_BACKLOG_AND_OPEN_DECISIONS.md`, `09_GOLDEN_SCENARIOS.md`, `10_REVIEW_CORRECTIONS.md`, `12_REASONING_AND_SCOPE_RULES.md`, `REVIEW/2026-10-05_MASTER_REQUIREMENTS_REVIEW.md`. Дополнительно проверены релевантные места в `02_UNIVERSAL_BANK_MODEL.md`, `04_ANALYTICS_IDEAS.md`, `05_SOURCES_TOOLS_INTEGRATIONS.md`. Учитываются явно переданные решения из разговора. Реализация vNext не проверялась, legacy tests не запускались: это проверка intent и документации.

Внутри архива 115 записей и 22 оси. Все записи ещё относятся к vNext exploration; accepted v1.11 implementation contracts не заменяются этим отчётом.


| Текущий статус | Количество |
| --- | --- |
| CORE_INTENT | 12 |
| MVP_REQUIRED | 11 |
| TARGET_REQUIRED | 24 |
| CONDITIONAL_REQUIRED | 10 |
| FUTURE_OPPORTUNITY | 20 |
| OPEN_DECISION | 18 |
| ANTI_GOAL | 16 |
| EXPERIMENT | 4 |


SHA-256 исходного `REQUIREMENTS_MAP.json`: `04e600c0b3bf1c83940249bfeaa175d45865352229e07cd59062ce284cf6e60e`.


## 2. Согласованные решения и предложения разделены

| Решение | Основание в переданном разговоре | Что зафиксировать |
| --- | --- | --- |
| Один authoritative inventory | Пользователь согласился с ролью master + map и попросил проверить текущие requirements | JSON — structured registry; master — согласованное human представление и rationale; 08 — historical inbox с triage links. Ни один из двух authoritative видов не должен обещать больше другого. |
| Mechanics similarity вне обязательного MVP | Пользователь выбрал Golden Scenario, затем согласился с нормализацией | TARGET + GSU02; game-domain store/research/reuse проверяется в MVP без полноценного mechanics engine. |
| Source отдельно от Entity | Пользователь делегировал решение; в разговоре принято отдельное canonical type | Source может ссылаться на Entity; SourceRoute принадлежит Source. Множественные acquisition endpoints не означают множественные предметы мира. |
| Начальное хранение в GitHub | Пользователь прямо выбрал GitHub | Provisional backend choice. Private repo, конкретная directory layout и adapter design — предлагаемые детали, а не приписанная пользователю точная спецификация. |

В архиве также уже есть draft-adopted configuration authority и news identity boundary. Их предлагается оформить как CURRENT_DECISION, сохранив origin `archive_adopted_draft`. Они не превращаются в accepted v1.11 contracts.

`NEW-001…NEW-028` ниже — временные идентификаторы предложений этого отчёта. При внесении в registry назначить штатные DEC/OPP/OPEN/TGT/COND/ANTI ID и сохранить mapping. Эти обозначения не создают второй официальный inventory.

## 3. Что требует нормализации сейчас

| Область | Реальное расхождение/пробел | Предлагаемая правка | Степень решения |
| --- | --- | --- | --- |
| MVP-011 / master 5.5 | Master требует mechanics similarity; JSON говорит слабее об object flow | Убрать similarity из MVP acceptance; сохранить TARGET capability и GSU02 | Уже согласовано |
| Source / Entity | Master 3.1 включает source в Entity examples и отдельно требует Source | Удалить ambiguous example; добавить отдельный type и optional subject Entity reference | Уже согласовано |
| OPEN-011 | Одним пунктом открыты backend и topology | Backend закрыть CURRENT_DECISION GitHub; execution/cache/media/sync topology оставить открытой | GitHub согласован; topology не решена |
| MVP provenance links | Master 5.1 требует basic links; JSON MVP не явен, TGT-001 требует Relation | MVP-001 явно включает минимальные references; full typed Relation registry остаётся TARGET | Предложение границы |
| AI/evidence origin | Полный evidence machinery TARGET, но MVP Annotation уже бывает AI/user | Минимальные author/origin/derivation поля MVP; full admissibility/dependency graph TARGET | Уточнение существующего invariant |
| Claim statuses | JSON `PARTIAL`, master `PARTIALLY_SUPPORTED` | Предлагается одно имя `PARTIALLY_SUPPORTED`, explicit old alias/migration | Предложение enum choice |
| Negative examples | В исходном snapshot master 6.1 включал их в TARGET, OPP-017 — FUTURE | Пользователь утвердил TARGET_REQUIRED вне MVP: dimensions, soft preference/hard exclusion, explanations и evaluation | Согласовано и применено 2026-10-05 |
| Clustering | Master 8.2 обещает semantic/topic/mechanics clusters и emerging/declining phenomena; JSON TGT-020 их явно не включает | В split TGT-020.E сохранить TARGET intent с model/method/version/data sufficiency qualifiers | Сохранение master intent; можно явно пересмотреть later |
| Full-text и arbitrary file | «Save anything» может прочитаться как extraction/OCR всех форматов | Зафиксировать supported save formats отдельно от searchable extracted text | Предложение acceptance wording |
| RunSpec / reproducibility | Immutable config легко спутать с deterministic replay live web/AI | Frozen effective config + retained output; unknown internals видимы; exact replay policy OPEN | Уточнение guarantee |
| UI surfaces | TGT-022 может превратиться в обязательные десятки страниц | Нужна inspectability state, navigation/layout остаются open | Уточнение UX intent |
| Reference stack | Список продуктов можно принять за обязательные integrations/features | Reference patterns с источником и ограничением; adoption только отдельно | Правило нормализации |

`kind` и `status` отвечают на разные вопросы. Архитектурное требование может быть CORE_INTENT или MVP_REQUIRED; наличие architecture kind само по себе не основание его понижать. CURRENT_DECISION нужен для уже выбранного решения, а не для переименования всех constraints. EXPERIMENT/OPPORTUNITY не являются implementation obligations.

## 4. Рекомендуемая граница MVP

Первый полезный vNext сохраняет supported files/URLs/notes/domain objects без research; имеет stable IDs, basic provenance/annotations, mixed collections, browse и exact/full-text поиск по доступному сохранённому тексту. Source и Entity различаются. История не требует каждый раз читать чат.

Tracked research хранит Lens, SourcePolicy, frozen effective RunSpec, ResearchRun и фактически выданный ResultSet/Occurrences. Простая конфигурация допустима без full Recipe/Route registries. ChatGPT должен иметь конкретный callable путь save/retrieve/writeback через приложение; native web/Deep Research не создаёт такой путь автоматически.

Proof: два последовательных freelance observation cycles с общей identity/history и доступным basic comparison; game объект сохраняется, используется как research seed и найденный результат возвращается в Bank; image/file сохраняется без активного research. Полная generalization Trend/Health/Interpretation, graph search, semantic/multimodal similarity, scheduling и formal bitemporal не являются скрытыми MVP gates. Если сохраняем старые freelance продукты, это их доступное переиспользование, а не требование уже реализовать universal analytics engine.

Перед schema/API MVP нужно закрыть минимальный вариант OPEN-004 (bytes/reference/note/entity), OPEN-012 (реальный callable handoff), runtime/media остаток OPEN-011, basic timestamp/retention решения OPEN-006/007 и фактическую активность COND-003. Backend GitHub уже выбран; library folders не следует трактовать как решение о workspace scope. Offline/sync/navigation/plugin framework могут оставаться открытыми до соответствующего использования.

### Предлагаемые acceptance checks для MVP

Это intent-level checks для будущего implementation contract, а не исполненные tests.

1. Сохранённый supported file или note без Lens/Run получает ID и затем находится через Bank get/search.
2. Game Entity и вложенный Asset различаются; Source может ссылаться на эту Entity, но не обязано ею быть.
3. Изменение Lens/SourcePolicy после run не изменяет старый RunSpec; unresolved ownership conflict вызывает явную ошибку компиляции.
4. Один и тот же сохранённый item участвует в двух runs; в обоих сохраняются собственные membership/order/reasons.
5. Второй freelance cycle добавляет observations, не стирает первый; отсутствующий item имеет `not_seen` или unknown coverage, а не автоматически closed.
6. AI annotation ссылается на автора/derivation; сохранение не превращает её в независимый source fact.
7. Read-only get/query не запускает external refresh автоматически вне явно разрешённой policy.
8. Unsupported extraction/similarity route или inaccessible external source отображается как unsupported/partial/unavailable, а не как успешно исполненная capability.

## 5. Полный pass по 115 текущим записям

KEEP — оставить смысл и статус, добавить metadata. CLARIFY — сохранить status, уточнить scope/guarantee/границу. SPLIT — сохранить intent и исходный ID с child/supersession links, разнести независимые outcomes или частично закрытое решение. CHANGE_STATUS — согласованная смена статуса с сохранением history (OPP-017). Каждая строка показывает **исходный statement из JSON** и отдельное предложение.

В колонке trace `Vxx` означает `AX-Vxx`; `§` — предложенная связь с разделом `11_MASTER_REQUIREMENTS_AND_EXTENSION_AXES.md`. Это новые review mappings, не восстановленная историческая атрибуция пользователю. `—` в references означает отсутствие подходящего подтверждённого reference pattern, а не недостающий requirement.


### Core intent — CORE_INTENT (12)


| ID | Текущее содержание | Действие | Предложение и причина | Kind / оси / human ref / pattern |
| --- | --- | --- | --- | --- |
| INT-001 | Product is a universal personal research/intelligence bank around ChatGPT, not a vacancy/freelance-specific product. | KEEP | Универсальность — продуктовая цель; freelance остаётся одним domain pack. | user_outcome; V01, V02, V18; §1.1; ref: — |
| INT-002 | User can save arbitrary useful material independently of an active research project. | CLARIFY | «Arbitrary» означает поддерживаемые форматы; не обещать любой формат/размер в MVP. | user_outcome; V02, V22; §2.1; ref: FAB.capture |
| INT-003 | Saved items can later act as search seeds, research inputs/results, evidence/reference, comparison items, collection members, or watch subjects. | KEEP | Роли контекстные: один объект может быть seed, evidence или result в разных операциях. | user_outcome; V03, V05, V10; §2.1; ref: FAB.example_search |
| INT-004 | Repeated research enriches one longitudinal bank/history rather than producing isolated reports only. | KEEP | Повторные исследования пополняют историю; сохранение отчётов остаётся допустимым дополнением. | user_outcome; V09, V22; §2.1; ref: — |
| INT-005 | System supports scope/coverage-aware current state, changes, trends, lifecycle/history, and research health. | CLARIFY | Это конечный пользовательский outcome; не переносить все Trend/lifecycle/Health функции в MVP. | user_outcome; V09, V11, V18; §1.2; ref: — |
| INT-006 | ChatGPT is the primary interactive reasoning/orchestration layer; the application owns durable state/history/UI/deterministic contracts. | KEEP | Разделение ответственности важно независимо от выбранного протокола и backend. | architecture_constraint; V07, V18, V19; §4.2–4.3; ref: PAL.data_logic_actions |
| INT-007 | Sources/tools/providers are reusable but replaceable; research semantics should depend on capabilities/contracts rather than vendor brands. | KEEP | Capabilities задают смысл; бренд и конкретная реализация относятся к executor. | architecture_constraint; V03, V07, V19; §2.8; ref: — |
| INT-008 | New domains should normally be added through Domain Packs rather than universal-core schema rewrites. | KEEP | Domain Packs — принятый архитектурный ориентир; kind объясняет, почему это не UI feature. | architecture_constraint; V01, V19; §2.7; ref: — |
| INT-009 | Preserve provenance, history, comparability, counterevidence and command/query boundaries. | CLARIFY | Групповой invariant сохранить; не выдавать одну отметку «done» за все provenance/history/comparability/query-boundary. | architecture_constraint; V08, V09, V22; §2.2–2.6; ref: — |
| INT-010 | Discovery is not measurement; search-result frequency is not demand/prevalence without valid method/sampling. | KEEP | Нормативное ограничение интерпретации, а не требование строить статистический движок. | research_method; V08, V11; §7.1; ref: — |
| INT-011 | Raw evidence, canonical identity, annotation, derived representation, analytical projection and search ranking remain distinct epistemic layers. | KEEP | Разделить identity, evidence, annotation и projection; сложность хранения не следует из количества понятий. | data_contract; V02, V04, V08; §2.3; ref: ZOT.item_attachment |
| INT-012 | “Complete/current state” is always relative to declared scope, method and coverage; never imply total-world exhaustiveness by default. | KEEP | Scope/method/coverage должны сопровождать выводы уже при простом research. | research_method; V08, V09, V11; §2.5; ref: — |


### MVP — MVP_REQUIRED (11)


| ID | Текущее содержание | Действие | Предложение и причина | Kind / оси / human ref / pattern |
| --- | --- | --- | --- | --- |
| MVP-001 | Persist Asset, Entity, Observation, Annotation and Collection with stable IDs and basic provenance. | CLARIFY | Добавить минимальные ID-ссылки для source/run/asset/use provenance; общий Relation registry остаётся TARGET. Сохранение файла не обязано создавать Entity. | data_contract; V02, V09, V12, V22; §5.1; ref: PAL.objects_links, ZOT.item_attachment |
| MVP-002 | Save supported file/URL/note/object without requiring research. | CLARIFY | Явно перечислить поддерживаемые file/URL/note/object типы и что сохраняется: bytes, URL reference или snapshot. | product_capability; V02, V18, V22; §5.1; ref: FAB.capture, ZOT.snapshot |
| MVP-003 | Browse item detail, collections, basic history and exact/full-text local-bank search. | CLARIFY | Full-text по сохранённому/извлечённому тексту; не делать OCR каждого изображения и parsing любого файла скрытой обязанностью MVP. | product_capability; V04, V09, V18; §5.1; ref: FAB.bank_search |
| MVP-004 | Persist Source and SourcePolicy. | CLARIFY | Source — отдельный canonical object; Entity link необязателен. SourcePolicy фиксирует scope допуска источников. | data_contract; V06, V08; §3.2; ref: — |
| MVP-005 | Persist ResearchLens with semantic intent/filters/seeds/time/ranking intent. | CLARIFY | Lens хранит намерение; метод и cadence не дублировать. Unsupported similarity profile может сохраниться как намерение, но исполнение не должно притворяться поддержанным. | data_contract; V03, V05, V08, V13; §3.2; ref: — |
| MVP-006 | Compile immutable RunSpec before a tracked run; no silent last-value-wins config precedence. | CLARIFY | RunSpec нужен для tracked research. Не требовать полноценные Recipe/Route registries: можно заморозить простую explicit effective configuration и записать недоступные provider parameters как unknown. | architecture_constraint; V07, V08, V09; §3.2; ref: — |
| MVP-007 | Persist ResearchRun linked to RunSpec and provenance. | CLARIFY | Зафиксировать status/partial/failure и связь с frozen spec; точная внешняя воспроизводимость не гарантируется одним RunSpec. | data_contract; V07, V09, V22; §5.2; ref: — |
| MVP-008 | Persist ResultSet/ResultOccurrence so historical run membership/order/reasons can survive later model/index changes. | CLARIFY | Хранить фактически выданные membership/order/reasons; неизвестные scores не выдумывать. Не требуется создавать новый Observation для уже сохранённого result. | data_contract; V04, V09, V20; §3.2; ref: — |
| MVP-009 | Expose stable application operations so ChatGPT can save/retrieve bank items and record/retrieve research state/results. | CLARIFY | Нужны save/get/search/collections/run/results и validation; конкретное имя tools, MCP и platform-specific side panel ещё не выбраны. | product_capability; V07, V18, V19; §5.3; ref: — |
| MVP-010 | Use ChatGPT native web/Deep Research and optional ChatGPT-accessible connectors by default; direct provider APIs are not MVP assumptions. | CLARIFY | MVP поддерживает интерактивный ChatGPT-mediated handoff без обязательных direct APIs. Web/Deep Research используются по фактической доступности, это не обещание приложению скрытого API ChatGPT. | architecture_constraint; V03, V07, V21; §5.4; ref: — |
| MVP-011 | Prove at least freelance longitudinal flow, game/mechanics-oriented object flow, and arbitrary image/file saving at design/implementation acceptance level. | CLARIFY | Применить согласованную границу: freelance повторные observations/history; game хранится, research/reuse работает; image/file сохраняется без research. Mechanics similarity только TARGET + GSU02. | governance; V01, V02, V09, V20; §5.5; ref: — |


### Target — TARGET_REQUIRED (24)


| ID | Текущее содержание | Действие | Предложение и причина | Kind / оси / human ref / pattern |
| --- | --- | --- | --- | --- |
| TGT-001 | Support typed Relation layer sufficient for graph/research/provenance use cases. | CLARIFY | Полный typed Relation layer позже; минимальные provenance/use references входят в MVP-001. Graph DB не является требованием. | data_contract; V01, V06, V12; §3.1; ref: PAL.objects_links |
| TGT-002 | Support Event objects with domain-relevant time semantics. | KEEP | Event отличается от публикации/обнаружения; сложная news ontology не нужна во всех domains. | data_contract; V01, V09; §3.1; ref: PAL.objects_links |
| TGT-003 | Support MetricObservation with method/unit/scope/provenance. | KEEP | Unit/method/scope/provenance обязательны для измерения; domain-specific величины вне universal schema. | data_contract; V09, V11; §3.1; ref: — |
| TGT-004 | Support versioned Representations such as embeddings, OCR, captions, perceptual hashes and domain feature vectors. | CLARIFY | Примеры OCR/embeddings/hashes — семейства representations, а не обязанность вычислять всё для каждого item. Версии + derivation обязательны, exact AI replay отдельно NEW-017. | data_contract; V02, V04, V05, V20; §3.1; ref: FAB.media_search |
| TGT-005 | Support reusable SourceRoute history/configuration distinct from Source identity. | KEEP | SourceRoute принадлежит Source; route changes должны сохранять историю, не менять source identity. | data_contract; V06, V09; §3.2; ref: — |
| TGT-006 | Support reusable ResearchRecipe owning methods/tools/steps but not semantic intent or cadence. | CLARIFY | Добавить recipe versions и explicit references; Lens/Watch authority не наследовать молча. | data_contract; V07, V08, V10; §3.2; ref: — |
| TGT-007 | Support Watch over entity, collection, lens/query, similarity neighborhood, metric/relation or source health. | CLARIFY | Разделить сохранение Watch policy и unattended execution; последнее активирует COND-001. Добавить pause/resume/history, остальные операционные детали conditional. | product_capability; V06, V09, V10; §6.6; ref: FEED.monitoring |
| TGT-008 | Support vendor-neutral Capability and CapabilityExecutor abstractions. | KEEP | Нужен небольшой contract capability/executor, не обязательный marketplace или plugin platform. | architecture_constraint; V07, V19; §3.4; ref: PAL.data_logic_actions |
| TGT-009 | Support cross-run/cross-source entity resolution, confidence, merge/split/correction history and reprojection. | CLARIFY | Результат — исправимая identity history; probabilistic matching применяется по нужде, не обязательно на первом domain. Entity merges не сливают Sources автоматически. | data_contract; V09, V12, V20; §6.2; ref: — |
| TGT-010 | Support structured, full-text, semantic, example, multimodal, domain-structural, temporal, change, graph/evidence-lineage and hybrid search over time. | SPLIT | Разделить search families с отдельной проверкой результата; exact/full-text MVP уже покрыты MVP-003. Не считать весь набор одним done. | product_capability; V04, V05, V09; §6.1; ref: FAB.bank_search, FAB.media_search, FAB.example_search |
| TGT-011 | Support multiple explainable similarity profiles/dimensions rather than one opaque universal score. | CLARIFY | Explainable profiles — TARGET; user-defined profile editor сохранять отдельной opportunity NEW-009. Один score допустим в известном profile с объяснением компонентов. | product_capability; V05, V13, V20; §6.1; ref: FAB.example_search |
| TGT-012 | Support first/last seen, reappearance/reopen, as-of history, comparable repeated runs and explicit coverage. | CLARIFY | first/last seen относятся к наблюдаемому scope; as-of system history не обещает formal valid/system-time queries до COND-007. | data_contract; V09, V12; §6.3; ref: — |
| TGT-013 | Retain/generalize CurrentStateSnapshot, ChangeSet, TrendSeries, InterpretationRecord and ResearchHealthSnapshot. | SPLIT | Пять result products проверяются отдельно; MVP basic history/diff не означает полной generalization всех пяти. | data_contract; V08, V09, V11, V18; §6.4; ref: — |
| TGT-014 | Support claim→evidence verification and important-claim statuses SUPPORTED/PARTIAL/CONTRADICTED/INSUFFICIENT/MISSCOPED/SOURCE_DOES_NOT_SUPPORT. | CLARIFY | Согласовать PARTIAL (JSON) и PARTIALLY_SUPPORTED (master); предложено PARTIALLY_SUPPORTED с явной миграцией alias. Claim/EvidenceLink — отдельная typed reasoning layer. | data_contract; V08, V20; §7.2; ref: ALPHA.cited_answers |
| TGT-015 | Support counter-search as a reusable serious-research stage; lack of found counterevidence is not proof. | CLARIFY | TARGET поддерживает counter-search stage; обязательность выполнения зависит от recipe/rigor, для high-stakes действует COND-005. | research_method; V03, V08; §7.3; ref: — |
| TGT-016 | Support separable independent verification context/role for high-value claims. | CLARIFY | Разделяемые verification roles/context — TARGET capability; не требовать второго агента/провайдера/платного исполнения в каждом run. | research_method; V08, V20; §7.4; ref: — |
| TGT-017 | Distinguish evidence admissibility/dependency for raw source, user note, AI annotation, derived metric and summaries. | CLARIFY | Full eligibility/dependency machinery — TARGET; MVP уже обязан сохранять author/origin/derivation, чтобы summary не становилось независимым подтверждением. | data_contract; V08, V22; §7.5; ref: ZOT.item_attachment |
| TGT-018 | Support source genealogy/dependency relations where false triangulation matters. | CLARIFY | Сохранять known genealogy relations в релевантных domains; неизвестная genealogy должна быть unknown, не доказанной независимостью. | data_contract; V06, V08; §7.6; ref: — |
| TGT-019 | Treat retrieval runs/providers as measurable process where practical; evaluate marginal evidence rather than assume independence. | CLARIFY | Доступные origin/coverage/time записывать; измерение marginal value требует сопоставимого benchmark. Не требовать недоступные internals ChatGPT retrieval. | research_method; V03, V08, V20, V21; §7.7; ref: — |
| TGT-020 | Provide basic distributions/quantiles, novelty/change decomposition, velocity/persistence, lifecycle/cohort/source-divergence/coverage-aware analysis as data permits. | SPLIT | Разделить descriptive, novelty, temporal/cohort, source/coverage и clustering. Data sufficiency и COND-009 ограничивают lifecycle выводы. | product_capability; V09, V11; §8.1–8.2; ref: — |
| TGT-021 | Personal fit/taste/skill relevance is a projection over bank observations/profile, not raw entity truth. | KEEP | Personal fit — user/profile-specific projection, не свойство entity; skill-gap остаётся OPP-008. | architecture_constraint; V11, V13; §8.4; ref: — |
| TGT-022 | Provide persistent UI surfaces for Bank/Discover/Collections/Research/Current/Changes/Trends/Watch/Sources/History/Evidence/Health as product matures. | CLARIFY | Это набор inspectable surfaces, не обязанность сделать 13 отдельных страниц и menu items. Navigation OPEN-001. | product_capability; V18; §10.2; ref: FAB.bank_search, FEED.monitoring |
| TGT-023 | Stable UI selections/IDs can be passed into ChatGPT for compare/explain/find-similar/research/save/watch actions. | CLARIFY | Стабильный selection context — TARGET; отдельная ChatGPT side panel зависит от platform, не универсальное требование. | product_capability; V18, V19; §10.3; ref: PAL.data_logic_actions |
| TGT-024 | Domain Packs can declare domain types/properties/metrics/identity/extraction/source/similarity/analysis/UI hints/tests. | CLARIFY | Pack может объявлять семантику/tests/UI hints; packaging/install/version compatibility ещё OPEN-022, не обязательный store. | architecture_constraint; V01, V19, V20; §6.7; ref: PAL.objects_links |


### Conditional — CONDITIONAL_REQUIRED (10)


| ID | Текущее содержание | Действие | Предложение и причина | Kind / оси / human ref / pattern |
| --- | --- | --- | --- | --- |
| COND-001 | Add scheduler/background jobs/retries/idempotency/budget/alerts/automatable executors. Trigger: User expects unattended or scheduled watches/research. | CLARIFY | Trigger сохраняется. Split операционных contracts позже; Watch policy можно хранить без scheduler. Нужны partial/failure states и explicit autonomy scope. | architecture_constraint; V07, V10, V21; §12.1; ref: FEED.monitoring |
| COND-002 | Add bulk ingestion/queues/object or columnar storage/incremental projections/index lifecycle/retention policies. Trigger: Data volume exceeds practical interactive/small-store operation. | CLARIFY | Не обязать сразу queues+Parquet+DB: требуются достаточные throughput/retention/rebuild свойства, технология выбирается по измеренному ограничению. | architecture_constraint; V14, V15, V21, V22; §12.2; ref: — |
| COND-003 | Add secret management, ACL/auth boundaries, encryption, retention/deletion/export and provider exposure controls. Trigger: Authenticated/private/sensitive sources or data are stored/queried. | CLARIFY | Trigger оценить перед реальными private data/credentials; не откладывать минимальные access/secret boundaries, нужные выбранному prototype. Полный enterprise набор не следует из private repo автоматически. | architecture_constraint; V16, V22; §12.3; ref: — |
| COND-004 | Add workspace ownership, roles/ACLs, shared/personal boundaries, audit/conflict semantics. Trigger: Multi-user/shared collaboration enters scope. | KEEP | Активируется shared/multi-user scope; в single-user prototype не строить roles/tenants заранее. | architecture_constraint; V16, V17, V22; §12.4; ref: — |
| COND-005 | Apply stricter primary-source/counter-search/independent-verification/source-genealogy/uncertainty gates. Trigger: Claims become high-stakes or materially drive decisions. | KEEP | Усиленные gates включаются по риску claims, не по domain label всего приложения. | research_method; V08, V20; §12.5; ref: — |
| COND-006 | Maintain evaluation sets/relevance judgments/regression runs. Trigger: Similarity/ranking is product-critical or models/rankers/providers change regularly. | CLARIFY | Evaluation обязателен когда ranking product-critical или часто меняется. Historical output нужно хранить уже в MVP независимо от regression sets. | governance; V04, V05, V20; §7.8; ref: — |
| COND-007 | Implement formal valid-time/system-time semantics. Trigger: Need to distinguish what was true then from what the system knew then across backfills/corrections. | KEEP | Чёткий trigger для formal bitemporal; не путать timestamps MVP с полной temporal query algebra. | data_contract; V09; §12.7; ref: — |
| COND-008 | Add direct provider/API/backend integration. Trigger: Automation, bulk volume, cost/latency, exact reproducibility, missing connector capability, reliability, governance, or direct streaming makes ChatGPT-mediated execution insufficient. | CLARIFY | Trigger оправдывает нужную integration, а не каждый provider. Record конкретную unmet capability/cost/reliability причину. | implementation_choice; V03, V07, V21; §9.3; ref: — |
| COND-009 | Handle right/left/interval censoring and source-missingness explicitly. Trigger: Lifecycle/survival analysis is implemented. | CLARIFY | Активировать при duration/persistence/survival выводах с неполным наблюдением, а не только при выборе формального survival model. | research_method; V09, V11; §8.2; ref: — |
| COND-010 | Use alert calibration/multiple-comparison controls when statistically applicable. Trigger: Large numbers of statistical alerts/tests create meaningful false-positive risk. | KEEP | Calibration нужна статистическим mass alerts; обычное уведомление о новом item не требует multiple-testing framework. | research_method; V10, V11, V20; §12.1; ref: — |


### Opportunities — FUTURE_OPPORTUNITY (20)


| ID | Текущее содержание | Действие | Предложение и причина | Kind / оси / human ref / pattern |
| --- | --- | --- | --- | --- |
| OPP-001 | Change-point detection | KEEP | Change points — optional; promotion после истории и проверки ценности, не для готовности MVP. | product_capability; V09, V11; §8.3; ref: — |
| OPP-002 | Anomaly detection | KEEP | Сначала определить аномалию и action пользователя; не обещать generic anomaly detector. | product_capability; V11, V20; §8.3; ref: — |
| OPP-003 | Concept/data drift detection | KEEP | Drift применим к версии representation/данным; не путать его с изменением реального мира. | product_capability; V04, V11, V20; §8.3; ref: — |
| OPP-004 | Seasonality decomposition | KEEP | Нужны длина и регулярность истории; статус не повышать по одному набору данных. | product_capability; V09, V11; §8.3; ref: — |
| OPP-005 | Distribution-shift metrics | KEEP | Distribution shift отделить от coverage/source shift; optional метод. | product_capability; V11, V20; §8.3; ref: — |
| OPP-006 | Graph/community/centrality analysis | KEEP | Typed Relations не обязывают строить centrality/community analytics. | product_capability; V04, V11, V12; §8.3; ref: — |
| OPP-007 | Trajectory similarity | KEEP | Не объединять со static mechanics similarity; time-aware trajectories — отдельная opportunity. | product_capability; V05, V09, V11; §8.3; ref: — |
| OPP-008 | Personal skill-gap analysis | KEEP | Skill-gap отличается от personal-fit projection; target relevance не требует skill-gap analysis. | product_capability; V11, V13; §8.3; ref: — |
| OPP-009 | Counterfactual projections | KEEP | Counterfactuals только при явных assumptions; не делать causal claims по bank correlation. | product_capability; V11, V13; §8.3; ref: — |
| OPP-010 | Sensitivity/robustness analysis | KEEP | Полная sensitivity analysis optional; обычное раскрытие ограничения поддерживается INT-012. | research_method; V08, V11; §8.3; ref: — |
| OPP-011 | Pareto-frontier decision views | KEEP | Полезно при явных нескольких критериях; не вводить заранее универсальный optimal score. | product_capability; V11, V13, V18; §8.3; ref: — |
| OPP-012 | Forecasting with uncertainty | CLARIFY | Добавить out-of-sample evaluation и uncertainty; без достаточной истории прогноз не обещать. | product_capability; V09, V11, V20; §8.3; ref: — |
| OPP-013 | Sparse-segment/hierarchical estimation | CLARIFY | Advanced hierarchical estimation optional; basic minimum effective-sample/insufficient-data rule — часть честной аналитики TGT-020/INT-012. | research_method; V11, V20; §8.3; ref: — |
| OPP-014 | Capture-recapture under explicit assumptions | KEEP | Capture-recapture сохранять opportunity под EXP-003, не численный market-size default. | research_method; V08, V11; §8.3; ref: — |
| OPP-015 | Collection-level prototype/diversity retrieval | KEEP | Collection можно использовать как seed без обязательного centroid/prototype algorithm; advanced diversity retrieval optional. | product_capability; V04, V05; §6.1; ref: — |
| OPP-016 | Find original/source/appearance of saved media over time | KEEP | Find-original не следует автоматически из image save или similarity; сохраним отдельной opportunity. | product_capability; V03, V09, V10; §11.3; ref: — |
| OPP-017 | Positive+negative example retrieval | CHANGE_STATUS | Утверждено пользователем: TARGET_REQUIRED, вне MVP; выбираемые dimensions, soft preference или hard exclusion, explanation и human quality comparison. Исходное FUTURE сохранено в change_history; ID остаётся прежним. | product_capability; V05, V13, V20; §6.1; ref: — |
| OPP-018 | Provider routing/caching/budget optimization | KEEP | Оптимизация routing/caching optional; budgets при unattended execution уже COND-001. | implementation_choice; V07, V10, V21; §9.3; ref: — |
| OPP-019 | Personal knowledge/workspace tool integration or partial substitution | KEEP | Интеграция/partial substitution требует export/ownership fit; reference не становится dependency. | product_capability; V19, V22; §9.4; ref: — |
| OPP-020 | Domain-specific data provider integration | KEEP | Domain providers выбираются по need/license/value; capabilities/domain pack не требуют всех интеграций. | product_capability; V01, V03, V19; §9.2; ref: — |


### Open decisions — OPEN_DECISION (18)


| ID | Текущее содержание | Действие | Предложение и причина | Kind / оси / human ref / pattern |
| --- | --- | --- | --- | --- |
| OPEN-001 | Product name and primary navigation | CLARIFY | Сохранить open name/navigation, решения независимы; блокирует polishing, не data contracts. | governance; V18; §14 Product; ref: — |
| OPEN-002 | Workspace/Project/Lens user-facing relationship | KEEP | Проверить UX на Bank→Lens→Run сценарии до именования Workspace/Project. | governance; V18, V22; §14 Product; ref: — |
| OPEN-003 | Global bank vs workspace scopes | KEEP | Scope affects IDs/permissions; не решить скрыто через Git directory tree. | data_contract; V16, V17, V22; §14 Data model; ref: — |
| OPEN-004 | Exact BankItem/Asset/Document/Note boundaries | CLARIFY | Закрыть минимальные границы file/URL/note/entity перед schema MVP; не требуется финальная UX taxonomy всех форматов. | data_contract; V02, V22; §14 Data model; ref: — |
| OPEN-005 | Relation type registry/extensibility | KEEP | MVP fixed references возможны до general relation registry. | data_contract; V01, V12, V19; §14 Data model; ref: — |
| OPEN-006 | Bitemporal implementation stage | CLARIFY | Связать COND-007; решить timestamps MVP сейчас, formal bitemporal stage только при trigger. Не дублировать как новый required object. | implementation_choice; V09; §14 Data model; ref: — |
| OPEN-007 | Raw capture retention policy | CLARIFY | Retention/raw captures влияет на размер Git и воспроизводимость; нужен prototype policy до большой загрузки. | governance; V09, V16, V22; §14 Data model; ref: — |
| OPEN-008 | Source genealogy granularity | KEEP | Granularity зависит от news/high-value claims; не блокировать simple source provenance. | data_contract; V06, V08; §14 Data model; ref: — |
| OPEN-009 | Domain schema evolution strategy | KEEP | Нужны pack/schema versions и migration meaning до второго изменённого schema, не обязательно сложная platform сейчас. | architecture_constraint; V01, V19; §14 Data model; ref: — |
| OPEN-010 | Combined vs separate relational/lexical/vector/graph search stores | CLARIFY | Deferred engine topology; в Git prototype indexes — rebuildable derived state. DB choice не требуется для normalization. | implementation_choice; V04, V14, V15; §14 Search; ref: — |
| OPEN-011 | Initial storage stack and local/cloud topology | SPLIT | Начальный persistence закрыт решением GitHub. Остаток execution/cache/media/sync topology остаётся open; future replacements выбирать по trigger. Не объявлять весь local/cloud вопрос решённым. | implementation_choice; V15, V22; §14 Storage; ref: — |
| OPEN-012 | ChatGPT↔application protocol and MCP boundary | CLARIFY | Приоритетный blocker MVP-009: выбрать реальный callable handoff/API, authorization и command/query semantics. Наличие ChatGPT web не решает writeback в Git. | implementation_choice; V07, V19; §14 Execution; ref: — |
| OPEN-013 | Async orchestration framework | CLARIFY | Отложить framework до COND-001; interactive ResearchRun status не требует workflow engine. | implementation_choice; V07, V10, V15; §14 Execution; ref: — |
| OPEN-014 | Notification channels | CLARIFY | Выбрать channel при scheduled Watch/alerts; bank browse MVP им не блокируется. | implementation_choice; V10, V18, V19; §14 Execution; ref: — |
| OPEN-015 | Local-first/cloud-first expectations | KEEP | GitHub remote persistence не решает offline-first, local execution или конечную topology. | governance; V15, V16, V22; §14 Product; ref: — |
| OPEN-016 | Collaboration timing | CLARIFY | Вернуть при намерении shared workspaces; single-user — рабочий scope, не permanent rejection collaboration. | governance; V17; §14 Product; ref: — |
| OPEN-017 | Credential and per-source compliance policy | CLARIFY | Разделить secret handling и source policy decisions; только actual data/access triggers активируют подробный дизайн. | governance; V06, V16, V22; §14 Security; ref: — |
| OPEN-018 | Exact search/similarity evaluation metrics and thresholds | CLARIFY | Метрики выбирать по search mode и human judgments; механическая similarity требует собственного eval, не universal benchmark threshold. | governance; V04, V05, V20; §14 Search; ref: — |


### Anti-goals — ANTI_GOAL (16)


| ID | Текущее содержание | Действие | Предложение и причина | Kind / оси / human ref / pattern |
| --- | --- | --- | --- | --- |
| ANTI-001 | Job/vacancy as universal root object | KEEP | Связать INT-001/INT-008; сохраняет universal core без запрета freelance pack. | architecture_constraint; V01; §13; ref: — |
| ANTI-002 | ResearchProject owns all durable knowledge | KEEP | Связать INT-002/INT-004; исследование ссылается на knowledge, не владеет всем Bank. | architecture_constraint; V09, V22; §13; ref: — |
| ANTI-003 | Build general web search/crawler merely to avoid existing ChatGPT/providers | CLARIFY | Запрет на дублирование инфраструктуры без причины; specialized acquisition по COND-008 допустим. | architecture_constraint; V03, V07, V21; §13; ref: — |
| ANTI-004 | Hard-code provider brands into universal research semantics | KEEP | Provider brand может быть в executor metadata, не в universal semantics. | architecture_constraint; V03, V07, V19; §13; ref: — |
| ANTI-005 | Assume multiple retrieval providers equal independent evidence | KEEP | Несколько retrieval каналов не заменяют dependency/source independence analysis. | research_method; V06, V08; §13; ref: — |
| ANTI-006 | Treat vector index/embedding/ranking as canonical truth | KEEP | Canonical objects/evidence восстанавливаются независимо от index/model. | data_contract; V04, V08; §13; ref: — |
| ANTI-007 | Create one giant GenericObject schema | CLARIFY | Общий metadata envelope допустим; один неограниченный schema со всеми domain fields — anti-goal. | architecture_constraint; V01, V02; §13; ref: — |
| ANTI-008 | Use one opaque similarity score for every purpose | CLARIFY | Запрещён один opaque score для всех purposes; объяснимый aggregate в конкретном profile допустим. | research_method; V05, V13; §13; ref: — |
| ANTI-009 | Silently overwrite history after identity/model/method changes | KEEP | Corrections append history; superseded данные можно пометить, не стирать незаметно. | data_contract; V09, V12, V22; §13; ref: — |
| ANTI-010 | Treat not_seen as disappeared/closed | KEEP | Связать INT-012/COND-009: not_seen характеризует наблюдение, не доказанное закрытие. | research_method; V09, V11; §13; ref: — |
| ANTI-011 | Claim complete market/world state without scope and coverage | KEEP | Связать INT-012; coverage boundary не optional decoration UI. | research_method; V08, V09; §13; ref: — |
| ANTI-012 | Treat discovery counts as demand/frequency measurement by default | KEEP | Связать INT-010; valid sampling/method может разрешить frequency estimation. | research_method; V08, V11; §13; ref: — |
| ANTI-013 | Hide source disagreement inside a single aggregate | KEEP | Aggregate должен позволять увидеть source divergence и underlying evidence. | research_method; V06, V08, V11; §13; ref: — |
| ANTI-014 | Silently refresh/mutate on a read-only query without authorization | KEEP | Разделять query/refresh и выполнять ранее разрешённую policy; не требовать повторного подтверждения каждого authorised command. | architecture_constraint; V07, V10, V19; §13; ref: — |
| ANTI-015 | Implement every analytics idea or provider integration before user value | KEEP | Сохранённые opportunities не входят в обязательный implementation scope автоматически. | governance; V03, V11, V21; §13; ref: — |
| ANTI-016 | Use chat transcript memory as durable product state | KEEP | Chat retrieves durable Bank; transcript может служить origin/context, не primary state store. | architecture_constraint; V19, V22; §13; ref: — |


### Experiments — EXPERIMENT (4)


| ID | Текущее содержание | Действие | Предложение и причина | Kind / оси / human ref / pattern |
| --- | --- | --- | --- | --- |
| EXP-001 | Compare ChatGPT-native retrieval vs Exa/Tavily/Parallel/other channels on real tasks using marginal useful evidence, primary-source discovery, counterevidence, overlap, cost and latency. | CLARIFY | Сравнение каналов по доступным comparable tasks; не интегрировать все providers ради эксперимента. | research_method; V03, V08, V20, V21; §9.2; ref: — |
| EXP-002 | Benchmark personal knowledge/AI workspace/research platforms and domain providers before building major commodity subsystems. | CLARIFY | Reference matrix — первый этап, не benchmark proof. Практически сравнить capture/retrieval/export/provenance до major commodity build. | governance; V02, V15, V19, V21, V22; §9.4; ref: FAB.bank_search, PAL.objects_links, ZOT.snapshot, FEED.monitoring, ALPHA.repeatable_grid |
| EXP-003 | Promote advanced analytical methods only after validating assumptions, sample/coverage quality and concrete user value on real longitudinal data. | KEEP | Эксперимент gating optional analytics, не обязательное внедрение каждого перечисленного метода. | research_method; V08, V11, V20; §8.3; ref: — |
| EXP-004 | Evaluate domain-specific representation/similarity profiles with human relevance judgments before treating similarity scores as useful product signals. | CLARIFY | Human mechanics relevance перед score promises; relation GSU02/GSU13 и conditional regression COND-006. | research_method; V05, V20; §7.8; ref: — |


## 6. Как разделить крупные записи

Child ID ниже — предложенные временные labels; исходный ID сохраняет audit/history. Parent станет grouping entry с `children`, а completion оценивается по child acceptance, не процентом одной широкой фразы. Если формат registry не допускает grouping entries, parent помечается SUPERSEDED с перечислением successor IDs. Это `lifecycle`, не новая шкала приоритета.


| Child label | Статус | Outcome / вопрос | Граница / зависимости |
| --- | --- | --- | --- |
| TGT-010.A | TARGET_REQUIRED | Semantic и example-based search | MVP-003 baseline + TGT-004; конкретная representation и relevance eval по mode. |
| TGT-010.B | TARGET_REQUIRED | Multimodal и domain-structural search | TGT-004/011/024; mechanics engine NEW-021 — domain capability, не MVP. |
| TGT-010.C | TARGET_REQUIRED | Temporal и change search | TGT-012/013; known-then history vs formal bitemporal COND-007. |
| TGT-010.D | TARGET_REQUIRED | Relation/graph и evidence-lineage search | TGT-001/014/017; minimal provenance links MVP не требуют graph query engine. |
| TGT-010.E | TARGET_REQUIRED | Hybrid combinations supported modes | Не строить каждый вариант cross-product всех modalities; implementation-specific composition contract. |
| TGT-013.CURRENT | TARGET_REQUIRED | CurrentStateSnapshot | Scope + latest admissible observations + coverage; basic MVP history не equals full product. |
| TGT-013.CHANGES | TARGET_REQUIRED | ChangeSet | Declared comparable run/time boundaries и explicit difference classes. |
| TGT-013.TREND | TARGET_REQUIRED | TrendSeries | Method/unit/source comparability, insufficient-data state. |
| TGT-013.INTERPRETATION | TARGET_REQUIRED | InterpretationRecord | Evidence/derivation + author/model/method context. |
| TGT-013.HEALTH | TARGET_REQUIRED | ResearchHealthSnapshot | Coverage/staleness/partial/failure отдельно от предметных изменений. |
| TGT-020.A | TARGET_REQUIRED | Descriptive / grouped distributions и quantiles | TGT-003; eligible sample definition, insufficient-data rules. |
| TGT-020.B | TARGET_REQUIRED | Novelty/change decomposition | New/known/changed/reappeared/not_seen по explicit definitions и scope. |
| TGT-020.C | TARGET_REQUIRED | Velocity/persistence/lifecycle/cohorts | TGT-012; duration/survival inference активирует COND-009. |
| TGT-020.D | TARGET_REQUIRED | Source divergence / coverage-aware analytics | INT-010/012; explicit normalization model, разрывы comparability видимы. |
| TGT-020.E | TARGET_REQUIRED | Semantic/topic/mechanics grouping и emerging/declining clusters | Master 8.2 intent; TGT-004/024 + EXP-003 validation. Advanced change-point/anomaly/drift methods остаются opportunities. |
| OPEN-011.backend | CURRENT_DECISION | Initial persistence: GitHub | NEW-004; provisional, domain semantics independent of Git. |
| OPEN-011.runtime | OPEN_DECISION | Prototype execution/cache/media/sync topology | Приложение выполняется где-то, Git — repository; raw bytes, derived indexes и local/cloud execution требуют отдельного design. |


Существующие exact/full-text search сохраняются в MVP-003 и не дублируются как новые TARGET обязанности. Перечень five result products не требует пяти раздельных UI страниц.

## 7. Новые registry proposals и принятые решения для фиксации

28 строк ниже не означают 28 обязательных новых features. Они включают запись решений, opportunities, вопросы, условный alert contract, явную TARGET mechanics capability, общую target search explanation и сохранение существующего anti-goal. Некоторые пункты можно встроить в существующие записи через explicit subclauses вместо отдельного ID; coverage при этом должно остаться проверяемым.


| Proposal ID | Предлагаемый статус / kind | Формулировка | Origin / основания | Scope / условия / оси |
| --- | --- | --- | --- | --- |
| NEW-001 | CURRENT_DECISION; governance | Master + REQUIREMENTS_MAP — единый authoritative vNext intent inventory; 08 — historical inbox. | Согласовано в переданном разговоре. | У master и JSON одна семантика; JSON структурная registry, master human rationale; accepted v1.11 отдельно. Оси: V19, V20, V22 |
| NEW-002 | CURRENT_DECISION; governance | Mechanics similarity — TARGET capability + Golden Scenario GSU02, не MVP blocker. | Согласовано в переданном разговоре. | Изменить MVP-011 и master 5.5; game object/research reuse остаётся MVP proof. Оси: V01, V05, V20 |
| NEW-003 | CURRENT_DECISION; architecture_constraint | Source и Entity — разные canonical types; Source может ссылаться на Entity, SourceRoute принадлежит Source. | Делегировано пользователем и принято в переданном разговоре. | Entity = предмет мира; Source = acquisition endpoint/corpus. Не создавать Entity для каждого Source без semantic need. Оси: V06, V12 |
| NEW-004 | CURRENT_DECISION; implementation_choice | Начальный persistent backend — GitHub; domain model не зависит от Git. | GitHub выбран пользователем; private repo и backend abstraction — предложенные детали реализации. | Provisional. Revisit: media/scale/query performance/automation/privacy. Git history не заменяет ResearchRun history. Оси: V15, V22 |
| NEW-005 | FUTURE_OPPORTUNITY; product_capability | Nested collections и saved views. | B009. | Развести два UX features при promotion; базовые collections MVP не делают nesting обязательным. Оси: V18, V22 |
| NEW-006 | FUTURE_OPPORTUNITY; product_capability | Favorites, pins, archive states. | B011. | Archive не равен deletion; не добавлять новый object type только ради флага. Оси: V18, V22 |
| NEW-007 | FUTURE_OPPORTUNITY; product_capability | Import bookmarks, local folders, exports. | B016. | Supported imports только после необходимости; general save не означает bulk import UI. Оси: V19, V22 |
| NEW-008 | FUTURE_OPPORTUNITY; product_capability | Import dedupe и explicit conflict handling. | B017. | Автоматический merge без provenance/confidence не предполагается; импорт и identity resolution не одно и то же. Оси: V12, V19, V22 |
| NEW-009 | FUTURE_OPPORTUNITY; product_capability | User-defined similarity profiles/editor. | B028. | Несколько системных profiles в TGT-011 не обещают editor. Оси: V05, V13, V18 |
| NEW-010 | FUTURE_OPPORTUNITY; product_capability | Branch/clone Lens. | B059. | Копировать намерение и явные version refs; не клонировать исторические runs как новые факты. Оси: V08, V18 |
| NEW-011 | FUTURE_OPPORTUNITY; product_capability | Compare lenses и их result scopes. | B060. | Развести сравнение config и results; comparability показывать явно. Оси: V08, V11, V18 |
| NEW-012 | FUTURE_OPPORTUNITY; product_capability | Suggestions исследования по saved collection. | B062. | Suggestion не запускает дорогое external work автоматически; autonomy определяется policy. Оси: V10, V18 |
| NEW-013 | CONDITIONAL_REQUIRED; product_capability | Novelty suppression/dedupe alerts. | B050. | Trigger: recurring Watch alerts. Уведомления не повторяют уже acknowledged findings, suppressed история доступна; details выбрать при alert design. Оси: V10, V20 |
| NEW-014 | OPEN_DECISION; governance | Offline mode expectations. | B138. | Отдельно decide read cached Bank, search, write queue и external research; GitHub не решает offline UX. Оси: V15, V18 |
| NEW-015 | OPEN_DECISION; implementation_choice | Local recomputation of representations и provider exposure choice. | B119. | Связать TGT-004/COND-003/OPEN-015; возможность зависит от model/runtime, не обещать полную локальность. Оси: V04, V15, V16 |
| NEW-016 | OPEN_DECISION; architecture_constraint | Domain Pack/plugin packaging, compatibility, install/version boundary. | B143. | При внедрении pack loader выбрать contract; не обязательно plugin marketplace. Оси: V01, V19 |
| NEW-017 | OPEN_DECISION; data_contract | AI representation/annotation reproducibility policy. | B147. | Сохранить input/model/prompt/config/version/output где доступно. Развести output retention, rerun и bit-identical replay; последнее не гарантировать. Оси: V04, V08, V20 |
| NEW-018 | OPEN_DECISION; data_contract | Provenance granularity/retention/storage cost. | B129. | В MVP обязательны минимальные links; полнота capture, routes/executor internals и raw payload retention требуют policy. Оси: V06, V08, V21, V22 |
| NEW-019 | FUTURE_OPPORTUNITY; product_capability | Perceptual near-duplicate detection для media. | B021. | pHash из TGT-004 — пример representation, не обязательная automatic duplicate detector feature. Оси: V04, V05 |
| NEW-020 | FUTURE_OPPORTUNITY; product_capability | Platform-specific ChatGPT side panel. | B103. | TGT-023 остаётся platform-independent selection handoff; конкретная side panel требует доступного host contract. Оси: V18, V19 |
| NEW-021 | TARGET_REQUIRED; product_capability | Game mechanics/core-loop similarity по версионированным признакам и объяснимым dimensions. | B022/B023 и согласованное решение mechanics TARGET. | Явная child capability TGT-010/TGT-011/TGT-024; GSU02. Полноценный engine после MVP и human relevance experiment. Оси: V01, V04, V05, V20 |
| NEW-022 | CURRENT_DECISION; architecture_constraint | Configuration ownership: Lens/SourcePolicy/Route/Recipe/Watch, compiled RunSpec. | B001/B002; archive 10_REVIEW_CORRECTIONS, draft-level adopted decision. | Уже draft-adopted в архиве, не новое user approval. Scope vNext draft, accepted v1.11 не меняется. Оси: V07, V08, V10 |
| NEW-023 | CURRENT_DECISION; data_contract | Publication/Article ≠ derived Story/Narrative ≠ real-world Event. | B005; archive 10_REVIEW_CORRECTIONS. | Domain-scoped news decision; не внедрять все три объекта в каждый domain или MVP. Draft-adopted, не отдельно подтверждено пользователем. Оси: V01, V08, V09 |
| NEW-024 | FUTURE_OPPORTUNITY; product_capability | Natural-language → structured/hybrid query builder. | B031. | Разговорный поиск в MVP возможен через ChatGPT tools; собственный parser/builder приложения — отдельная optional feature. Оси: V04, V05, V18 |
| NEW-025 | OPEN_DECISION; governance | Autonomy/approval policy для дорогих и scheduled external commands. | B110/B120/B136. | Повторная confirmation не нужна при ранее разрешённой scope/budget policy; unattended authorization определить при COND-001. Оси: V10, V16, V21 |
| NEW-026 | FUTURE_OPPORTUNITY; product_capability | AI-assisted tagging/organisation. | B010. | Manual Annotation входит MVP; automatic tags suggestions optional, происхождение AI tags сохранять. Оси: V18 |
| NEW-027 | TARGET_REQUIRED; product_capability | Объяснение search matches: fields, representations, relations и происхождение результата. | B039; TGT-010/011 частично. | У similarity уже есть объяснения; расширить на все поддержанные search modes. В MVP достаточно фактических available match reasons, без отдельного explainability engine. Оси: V04, V18 |
| NEW-028 | ANTI_GOAL; research_method | Не приравнивать изменение страницы/источника к изменению реальной Entity. | B151 и master 2.3. | INT-011/012 близки, но не фиксируют конкретный temporal trap. Добавить явную guardrail либо атомарную часть INT-009, без нового runtime subsystem. Оси: V08, V09 |


Распределение этих proposed entries: 6 CURRENT_DECISION, 12 FUTURE_OPPORTUNITY, 6 OPEN_DECISION, 1 CONDITIONAL_REQUIRED, 2 TARGET_REQUIRED, 1 ANTI_GOAL. Все labels временные. Split children не прибавлять к этому числу как полностью новые независимые идеи: они разлагают старые commitments.

## 8. Полная triage-map backlog: 159/159

Каждый `Bxxx` соответствует одному исходному bullet в 08, в исходном порядке. Идентификаторы для review и номера строк привязаны к этому snapshot; для постоянной origin ссылки при применении использовать source path + section + exact excerpt/content hash, не только номер строки.

LINK — смысл уже покрыт; CLARIFY — нужное покрытие есть, но scope надо уточнить; PARTIAL — исходная идея содержит покрытую и отсутствующую часть; ADD_* — предлагается явная новая запись/решение. Ни LINK, ни ADD автоматически не делает idea MVP_REQUIRED.

Все строки получили назначение или explicit scope proposal. Это **полнота triage**, не утверждение, что live authoritative map уже обновлена. Конфликт OPP-017 закрыт targeted update: TARGET_REQUIRED вне MVP в обоих представлениях. Остальные policy details сохраняют proposed disposition.


### Tentative design decisions adopted after independent review


| Bullet / строка | Исходная идея | Действие | Destination IDs | Почему / точность покрытия |
| --- | --- | --- | --- | --- |
| B001 / 10 | separate configuration authority: `Lens = what`, `SourcePolicy = allowed/preferred sources`, `SourceRoute = source-specific access`, `Recipe = execution method`, `Watch = cadence/alerts`; | LINK | MVP-005, MVP-004, TGT-005, TGT-006, TGT-007, NEW-022 | Draft decision уже в archive; добавить classification CURRENT_DECISION, не менять ownership. |
| B002 / 11 | compile every execution into an immutable `RunSpec`; no silent “last object wins” precedence; | LINK | MVP-006, NEW-022 | Уточнить tracked research vs каждый save/query. |
| B003 / 12 | preserve exact historical search/research membership through a `ResultSet`/`ResultOccurrence`-style lineage contract; | LINK | MVP-008 | Исторический output сохраняется, не реконструируется current ranker. |
| B004 / 13 | arbitrary saved material is not automatically independent evidence; retain epistemic class/derivation/independence semantics; | LINK | INT-011, TGT-017 | MVP origin/author сохранён; full eligibility позже. |
| B005 / 14 | for news, distinguish Publication/Article, derived Story/Narrative grouping, and real-world Event; | ADD_DECISION | TGT-002, NEW-023 | News boundary принят в draft; general Entity primitive не решает grouping semantics. |
| B006 / 15 | central similarity/search modes should eventually have versioned retrieval evaluation sets and relevance judgments. | LINK | COND-006, OPEN-018 | Conditional, не MVP gate. |


### Bank / organization ideas


| Bullet / строка | Исходная идея | Действие | Destination IDs | Почему / точность покрытия |
| --- | --- | --- | --- | --- |
| B007 / 19 | save arbitrary object/file/link/note with one action; | CLARIFY | MVP-002 | Save capability covered; «one action» — UX ориентир, не буквальный запрет metadata prompt. |
| B008 / 20 | mixed collections; | LINK | MVP-001, MVP-003 | Collection допускает разные supported types. |
| B009 / 21 | nested collections or saved views; | ADD_OPPORTUNITY | NEW-005 | Не покрыто basic collections. |
| B010 / 22 | manual + AI-assisted tags; | PARTIAL | MVP-001, NEW-026 | Manual tags — Annotation; AI-assisted organisation optional. |
| B011 / 23 | favorites/pins/archive states; | ADD_OPPORTUNITY | NEW-006 | Новые организационные состояния. |
| B012 / 24 | item roles independent of item type; | LINK | INT-003, MVP-008 | Роль относится к использованию, а не type item. |
| B013 / 25 | backlinks: “where has this item been used?”; | CLARIFY | TGT-010, MVP-001 | MVP хранит use references; общий backlink/lineage query позже. |
| B014 / 26 | research lineage from item to every run/claim/result that referenced it; | CLARIFY | MVP-007, MVP-008, TGT-014, TGT-010 | Runs/results MVP, claims и полный lineage search TARGET. |
| B015 / 27 | user annotations distinct from machine-extracted facts; | LINK | INT-011, MVP-001, TGT-017 | Author/epistemic origin не терять. |
| B016 / 28 | import browser bookmarks/local folders/exports later; | ADD_OPPORTUNITY | NEW-007 | General save не означает import pipeline. |
| B017 / 29 | optional dedupe on import with explicit conflict handling. | ADD_OPPORTUNITY | NEW-008, TGT-009 | Dedupe workflow отдельно от canonical identity. |


### Similarity ideas


| Bullet / строка | Исходная идея | Действие | Destination IDs | Почему / точность покрытия |
| --- | --- | --- | --- | --- |
| B018 / 33 | visual similarity; | LINK | TGT-010, TGT-011 | TARGET visual profile; не MVP. |
| B019 / 34 | semantic image similarity; | LINK | TGT-004, TGT-010, TGT-011 | Semantics и visual attributes не один profile. |
| B020 / 35 | style similarity; | CLARIFY | TGT-011, TGT-024 | Domain/media style profile, не обязательность всех styles/model families. |
| B021 / 36 | perceptual duplicate detection; | ADD_OPPORTUNITY | NEW-019 | Hash representation ≠ automatic duplicate workflow. |
| B022 / 37 | game mechanics similarity; | ADD_TARGET | NEW-002, NEW-021, EXP-004 | Согласовано: TARGET + GSU02. |
| B023 / 38 | core-loop similarity; | CLARIFY | NEW-021, TGT-024 | Core-loop dimension в game domain profile. |
| B024 / 39 | trajectory similarity over time; | LINK | OPP-007 | Trajectory не static similarity. |
| B025 / 40 | “similar to all these positive examples”; | CLARIFY | INT-003, MVP-005, TGT-011 | Multi-seed query/profile возможен; конкретное aggregation rule уточнить в profile. |
| B026 / 41 | positive examples + negative examples (“like these, but not those”); | CHANGE_STATUS | OPP-017 | Утверждено TARGET_REQUIRED вне MVP; dimensions, soft preference/hard exclusion, explanations и quality evaluation. |
| B027 / 42 | explainable dimension-level similarity; | LINK | TGT-011 | Explain dimensions по actual used features. |
| B028 / 43 | user-defined similarity profiles; | ADD_OPPORTUNITY | NEW-009 | Multiple profiles не означает user editor. |
| B029 / 44 | collection-level prototype/centroid plus diverse-result retrieval. | LINK | OPP-015 | Prototype/diversity optional; collection-as-seed отдельно уже core. |


### Search ideas


| Bullet / строка | Исходная идея | Действие | Destination IDs | Почему / точность покрытия |
| --- | --- | --- | --- | --- |
| B030 / 48 | bank only / my sources / my sources + web / selected sources modes; | CLARIFY | MVP-004, TGT-005 | SourcePolicy scope и effective scope каждого run должны совпадать. |
| B031 / 49 | natural-language → structured/hybrid query; | PARTIAL | NEW-024, MVP-009, TGT-010 | ChatGPT mapping intent covered; собственный query parser optional. |
| B032 / 50 | saved query/lens; | LINK | MVP-005 | Saved Lens — MVP; UI builder может позже. |
| B033 / 51 | historical “as known then” search; | CLARIFY | TGT-012, COND-007 | Known-then system history vs formal dual-time queries разделить. |
| B034 / 52 | “first appeared between dates”; | LINK | TGT-010, TGT-012 | Scope-aware first_seen. |
| B035 / 53 | “changed in the last N days”; | LINK | TGT-010, TGT-012, TGT-013 | Changes относятся к сравнимой history. |
| B036 / 54 | “new relationships around this item”; | LINK | TGT-001, TGT-010, TGT-012 | Relation change queries TARGET. |
| B037 / 55 | graph-neighborhood search; | LINK | TGT-001, TGT-010 | Graph query не требует graph DB. |
| B038 / 56 | cross-modal text→image and image→text/item search; | LINK | TGT-004, TGT-010 | Cross-modal family TARGET; exact model выбор открыт. |
| B039 / 57 | search result explanation: matched fields/representations/relations. | PARTIAL | NEW-027, MVP-008, TGT-011 | Existing result reasons/similarity explanations есть; общий search explanation needs explicit target clause. |


### Watch ideas


| Bullet / строка | Исходная идея | Действие | Destination IDs | Почему / точность покрытия |
| --- | --- | --- | --- | --- |
| B040 / 61 | watch entity; | LINK | TGT-007 | Policy TARGET; execution COND-001. |
| B041 / 62 | watch collection; | LINK | TGT-007 | Membership/scope semantics учитывать. |
| B042 / 63 | watch query; | LINK | TGT-007, MVP-005 | Watch references saved Lens/query. |
| B043 / 64 | watch similarity neighborhood; | LINK | TGT-007, TGT-011 | Depends on similarity support + profile version. |
| B044 / 65 | watch relation/event; | CLARIFY | TGT-007, TGT-001, TGT-002 | Event explicitly add к Watch supported targets. |
| B045 / 66 | watch metric threshold; | LINK | TGT-007, TGT-003 | Threshold meaningful only with units/method/time. |
| B046 / 67 | watch source health; | LINK | TGT-007, TGT-005, TGT-013 | Health coverage не путать с empty result set. |
| B047 / 68 | watch for original/source of saved media; | LINK | OPP-016, TGT-007 | Original-finding optional, scheduler conditional. |
| B048 / 69 | cadence per watch; | CLARIFY | TGT-007, COND-001 | Cadence stores policy; не гарантирует autonomous executor. |
| B049 / 70 | budgets/cost caps; | CLARIFY | COND-001, OPP-018 | Hard budget constraints при automation; routing optimisation optional. |
| B050 / 71 | alerts with novelty suppression to avoid repeated noise; | ADD_CONDITIONAL | NEW-013 | Recurring alerts trigger; anti-noise behavior missing explicit map clause. |
| B051 / 72 | pause/resume/history of watch policy changes. | CLARIFY | TGT-007 | Добавить lifecycle/history к формулировке Watch. |


### Research ideas


| Bullet / строка | Исходная идея | Действие | Destination IDs | Почему / точность покрытия |
| --- | --- | --- | --- | --- |
| B052 / 76 | research lens independent of project; | LINK | INT-002, MVP-005, OPEN-002 | Lens semantic object independent of exclusive Project ownership. |
| B053 / 77 | reusable research recipe; | LINK | TGT-006 | Recipe method, не intent/cadence. |
| B054 / 78 | immutable compiled RunSpec for every execution; | CLARIFY | MVP-006 | Tracked run, не каждый bank save. |
| B055 / 79 | historical ResultSet/ResultOccurrence lineage; | LINK | MVP-008 | Even existing bank items need ResultOccurrence. |
| B056 / 80 | recipe versions; | CLARIFY | TGT-006, MVP-006 | Add versioned Recipe refs; current RunSpec may use simple config before recipe registry. |
| B057 / 81 | run against frozen source set for comparability; | CLARIFY | MVP-006, TGT-012 | Freeze effective source identities/routes/config; не обещать frozen live web content. |
| B058 / 82 | run against current source set for freshness; | CLARIFY | MVP-004, MVP-006, TGT-012 | Resolve current source set at compile time; subsequent changes не mutate old spec. |
| B059 / 83 | branch/clone a lens; | ADD_OPPORTUNITY | NEW-010 | Workflow ранее отсутствовал. |
| B060 / 84 | compare two lenses; | ADD_OPPORTUNITY | NEW-011 | Config vs results comparison distinguish. |
| B061 / 85 | combine several saved objects into a research question; | CLARIFY | INT-003, MVP-005, TGT-011 | Сохранить seed IDs + intent; не обязательный advanced collection prototype. |
| B062 / 86 | automatically suggest research when a saved collection has enough material, but never start expensive work silently. | ADD_OPPORTUNITY | NEW-012, NEW-025, ANTI-014 | Suggestion и external command разные actions. |


### Analytics ideas


| Bullet / строка | Исходная идея | Действие | Destination IDs | Почему / точность покрытия |
| --- | --- | --- | --- | --- |
| B063 / 90 | distributions/quantiles; | LINK | TGT-020.A | Child proposed descriptive analytics. |
| B064 / 91 | demand/frequency/value/competition matrices; | CLARIFY | TGT-003, TGT-020.A, INT-010, TGT-024 | Freelance pack-specific matrices; demand frequency требует valid method. |
| B065 / 92 | velocity, persistence, lifecycle/survival; | CLARIFY | TGT-020.C, COND-009 | Lifecycle history + missingness guards before durations. |
| B066 / 93 | cohorts; | LINK | TGT-020.C | Comparable cohorts, не arbitrary groups. |
| B067 / 94 | change points; | LINK | OPP-001 | Optional change points. |
| B068 / 95 | concept drift; | LINK | OPP-003 | Optional drift. |
| B069 / 96 | anomalies; | LINK | OPP-002 | Optional anomalies. |
| B070 / 97 | distribution shifts; | LINK | OPP-005 | Optional distribution shifts. |
| B071 / 98 | seasonality; | LINK | OPP-004 | Optional seasonality. |
| B072 / 99 | source divergence; | LINK | TGT-020.D, ANTI-013 | Do not hide disagreement. |
| B073 / 100 | coverage-normalized metrics; | CLARIFY | TGT-020.D, INT-012 | Normalization assumption явное; не «divide by coverage» без method. |
| B074 / 101 | novelty/new-vs-known decomposition; | LINK | TGT-020.B | Different novelty dimensions need definitions. |
| B075 / 102 | semantic clustering; | PARTIAL | TGT-020.E, EXP-003 | Есть в master 8.2, JSON omission; сохранить TARGET с validation, не implicit MVP. |
| B076 / 103 | emerging/declining clusters; | PARTIAL | TGT-020.E, OPP-001 | Basic cluster dynamics target; algorithmic change points remain opportunity. |
| B077 / 104 | graph analysis; | LINK | OPP-006 | Graph analysis optional, query support TARGET. |
| B078 / 105 | personal-fit projections; | LINK | TGT-021 | Projection over user profile, not entity truth. |
| B079 / 106 | skill-gap analysis; | LINK | OPP-008 | Future skill-gap. |
| B080 / 107 | counterfactual scenarios; | LINK | OPP-009 | Future counterfactuals. |
| B081 / 108 | sensitivity/robustness analysis; | LINK | OPP-010 | Future robust/sensitivity analysis. |
| B082 / 109 | Pareto frontiers; | LINK | OPP-011 | Future Pareto views. |
| B083 / 110 | experimental capture-recapture estimates; | LINK | OPP-014, EXP-003 | Validate assumptions before adoption. |
| B084 / 111 | trajectory similarity; | LINK | OPP-007 | Future trajectory similarity. |
| B085 / 112 | forecasting with uncertainty and out-of-sample evaluation (optional, after enough history); | CLARIFY | OPP-012 | Uncertainty + out-of-sample tests. |
| B086 / 113 | explicit censoring/missingness semantics for lifecycle/survival; | CLARIFY | COND-009 | Trigger duration inference with incomplete observation. |
| B087 / 114 | conditional alert/multiple-comparison calibration for mass statistical watches; | LINK | COND-010 | Applies statistical mass alerts only. |
| B088 / 115 | sparse-segment/hierarchical estimation or minimum effective-sample rules. | CLARIFY | OPP-013, TGT-020.A, INT-012 | Advanced estimation optional; insufficient-data state must remain honest. |


### UI ideas


| Bullet / строка | Исходная идея | Действие | Destination IDs | Почему / точность покрытия |
| --- | --- | --- | --- | --- |
| B089 / 119 | Bank home; | LINK | MVP-003, TGT-022 | Basic Bank MVP, mature surface target. |
| B090 / 120 | object/entity detail with timeline; | CLARIFY | MVP-003, TGT-012, TGT-022 | Basic history vs full timeline surface. |
| B091 / 121 | collection detail; | LINK | MVP-003, TGT-022 | Basic collection browse included. |
| B092 / 122 | Discover/search builder; | CLARIFY | TGT-010, TGT-022, NEW-024 | Simple search MVP; rich builder target/optional parser. |
| B093 / 123 | Research lens/recipe editor; | CLARIFY | MVP-005, TGT-006, TGT-022 | Persist Lens MVP; full rich editor target. |
| B094 / 124 | Run history; | LINK | MVP-007, MVP-009, TGT-022 | Run history MVP operations. |
| B095 / 125 | Current State; | CLARIFY | TGT-013.CURRENT, TGT-022 | Full universal CurrentState TARGET; basic freelance history/diff MVP proof. |
| B096 / 126 | Changes; | CLARIFY | TGT-013.CHANGES, TGT-022 | Typed ChangeSet generalization TARGET. |
| B097 / 127 | Trends; | LINK | TGT-013.TREND, TGT-022 | Comparable data required. |
| B098 / 128 | Watch center; | LINK | TGT-007, TGT-022, COND-001 | Watch center target; background runtime conditional. |
| B099 / 129 | Sources; | LINK | MVP-004, TGT-022 | Source registry MVP; full UI target. |
| B100 / 130 | Tools/connectors; | LINK | TGT-008, TGT-022 | Capability/executor registry, не direct integration list commitments. |
| B101 / 131 | evidence/provenance drilldown; | CLARIFY | MVP-001, TGT-014, TGT-022 | MVP source/run provenance, full claim drilldown TARGET. |
| B102 / 132 | research health; | LINK | TGT-013.HEALTH, TGT-022 | Health distinguishes failure/partial/coverage. |
| B103 / 133 | ChatGPT side panel that can operate on selected UI objects/current view; | PARTIAL | TGT-023, NEW-020 | Selection context target; literal host side panel optional. |
| B104 / 134 | “use selection as seed” action everywhere. | CLARIFY | INT-003, TGT-023 | Action на supported selectable items; «everywhere» не буквальное навязывание UI каждой странице. |


### ChatGPT ideas


| Bullet / строка | Исходная идея | Действие | Destination IDs | Почему / точность покрытия |
| --- | --- | --- | --- | --- |
| B105 / 138 | user can refer to bank items conversationally (“that colony game we analyzed”); | CLARIFY | MVP-009, TGT-010 | Resolve ambiguous references through Bank retrieval; не доказательство universal natural-language perfect recall. |
| B106 / 139 | ChatGPT retrieves rather than relying on chat memory; | LINK | INT-006, ANTI-016, MVP-009 | Retrieved durable context, not canonical transcript memory. |
| B107 / 140 | ChatGPT can propose a lens/recipe but application persists it; | LINK | MVP-005, MVP-009, TGT-006 | Agent proposes, app validates/persists. |
| B108 / 141 | selected UI items become chat context by stable IDs; | LINK | TGT-023 | Stable IDs in selection handoff. |
| B109 / 142 | every analytical claim can expose evidence/limitations; | CLARIFY | INT-012, TGT-014, TGT-017 | Traceability and limitations; full claim verification layer TARGET. |
| B110 / 143 | ChatGPT can ask for confirmation before costly/broad external runs; | PARTIAL | NEW-025, ANTI-014 | Policy needs explicit treatment, not unconditional confirmation for every operation. |
| B111 / 144 | deterministic tool actions remain application-enforced. | LINK | INT-006, MVP-009 | Command validation enforced by app. |


### Security/privacy/compliance questions


| Bullet / строка | Исходная идея | Действие | Destination IDs | Почему / точность покрытия |
| --- | --- | --- | --- | --- |
| B112 / 148 | local-first vs cloud storage boundaries; | CLARIFY | OPEN-015, NEW-004 | Initial GitHub closed; long-term local/cloud UX open. |
| B113 / 149 | encryption and secret/credential storage; | LINK | COND-003, OPEN-017 | Actual credentials/private data trigger. |
| B114 / 150 | per-source terms of service and robots/compliance; | LINK | OPEN-017, MVP-004 | Per-source policy, no blanket acquisition promise. |
| B115 / 151 | user-owned/private source access; | LINK | COND-003, OPEN-017 | Access boundaries before authenticated source use. |
| B116 / 152 | deletion/retention/export guarantees; | CLARIFY | COND-003, OPEN-007 | Detailed deletion/export guarantees not fixed; durable save does not mean eternal retention. |
| B117 / 153 | sensitive personal data in saved material; | LINK | COND-003 | Trigger assess on actual stored data, not label «personal bank» alone. |
| B118 / 154 | model-provider data exposure for embedding/analysis; | CLARIFY | COND-003, NEW-015 | Model exposure policy explicitly selected. |
| B119 / 155 | whether representations can be recomputed locally; | ADD_OPEN | NEW-015 | Local recompute not resolved by versioned Representation. |
| B120 / 156 | permission model for autonomous scheduled watches. | ADD_OPEN | NEW-025, COND-001, COND-003 | Define autonomy scope before unattended work. |


### Data model open decisions


| Bullet / строка | Исходная идея | Действие | Destination IDs | Почему / точность покрытия |
| --- | --- | --- | --- | --- |
| B121 / 160 | exact distinction/naming among BankItem, Asset, Entity, Note, Document, Observation; | LINK | OPEN-004, MVP-001 | Source boundary separately NEW-003. |
| B122 / 161 | global bank vs workspace/project scopes; | LINK | OPEN-003 | No silent inference from repo layout. |
| B123 / 162 | how domain schemas evolve; | LINK | OPEN-009, TGT-024 | Version and migrate pack/schema. |
| B124 / 163 | merge/split identity semantics; | CLARIFY | TGT-009 | Required semantics; exact algorithm/UI open within contract. |
| B125 / 164 | relation typing/extensibility; | LINK | OPEN-005, TGT-001 | Full registry later, fixed refs now. |
| B126 / 165 | representation storage/versioning; | CLARIFY | TGT-004, OPEN-010, NEW-017 | Version output/input refs; store topology still choice. |
| B127 / 166 | bitemporal support in MVP vs later; | LINK | OPEN-006, COND-007 | No formal bitemporal MVP requirement. |
| B128 / 167 | immutable raw capture retention policy; | LINK | OPEN-007 | Need capture retention rules, not all web copied forever. |
| B129 / 168 | provenance granularity and storage cost. | ADD_OPEN | NEW-018, MVP-001, OPEN-007 | Minimum required refs vs optional deep provenance metadata distinguish. |


### Product open decisions


| Bullet / строка | Исходная идея | Действие | Destination IDs | Почему / точность покрытия |
| --- | --- | --- | --- | --- |
| B130 / 172 | product name and primary navigation; | LINK | OPEN-001 | Name/navigation unresolved. |
| B131 / 173 | whether “Research Project” remains user-facing or becomes one kind of workspace/lens; | LINK | OPEN-002 | Project/Lens UX relation unresolved. |
| B132 / 174 | which first domains prove universality (recommended: freelance, games, apps, news); | CLARIFY | MVP-011, TGT-024, NEW-002 | MVP freelance/game/image-file; apps/news Golden Scenarios initially. |
| B133 / 175 | which data acquisition providers are affordable/allowed; | CLARIFY | EXP-001, COND-008, MVP-004, OPEN-017 | Specific provider evaluate only at need; price selection not product invariant. |
| B134 / 176 | build-vs-buy comparison for the personal knowledge / AI workspace / reference-manager layer before building commodity Bank/UI features; | LINK | EXP-002, OPP-019 | Matrix now; practical benchmark later. |
| B135 / 177 | what is local/private vs shared/syncable; | LINK | OPEN-003, OPEN-015, COND-004 | GitHub choice not collaboration/sync contract. |
| B136 / 178 | what can run automatically vs requires explicit approval; | ADD_OPEN | NEW-025, COND-001 | Automatic vs authorised policy explicit. |
| B137 / 179 | notification/alert channels; | LINK | OPEN-014 | Notification choice deferred to Watch execution. |
| B138 / 180 | offline mode expectations. | ADD_OPEN | NEW-014 | Offline read/write/search promises not covered elsewhere. |


### Architecture open decisions


| Bullet / строка | Исходная идея | Действие | Destination IDs | Почему / точность покрытия |
| --- | --- | --- | --- | --- |
| B139 / 184 | Postgres + object storage + vector/search stack vs simpler local-first stack; | CLARIFY | NEW-004, OPEN-011, OPEN-015 | Initial backend GitHub; execution/cache/media topology still open. |
| B140 / 185 | one search engine vs separate lexical/vector/graph indices; | LINK | OPEN-010 | Do not pick vector/search stack prematurely. |
| B141 / 186 | how much graph capability needs a graph DB vs relations in relational store; | CLARIFY | OPEN-010, TGT-001 | Graph functionality ≠ graph DB requirement. |
| B142 / 187 | async job/orchestration framework; | LINK | OPEN-013, COND-001 | Deferred until automation need. |
| B143 / 188 | plugin/domain-pack packaging contract; | ADD_OPEN | NEW-016, TGT-024 | Semantic packs ≠ installation contract. |
| B144 / 189 | MCP boundary vs internal API boundary; | LINK | OPEN-012 | MVP blocker callable application handoff. |
| B145 / 190 | testing strategy for probabilistic/LLM components; | CLARIFY | COND-006, EXP-004, EXP-003, NEW-017 | Deterministic contracts vs probabilistic judgments; no universal test suite promised. |
| B146 / 191 | versioned SearchEvaluationSet/RelevanceJudgment/SearchEvaluationRun for important retrieval modes; | LINK | COND-006, OPEN-018 | Versioned eval artifacts conditional. |
| B147 / 192 | reproducibility requirements for AI-generated representations/annotations. | ADD_OPEN | NEW-017, TGT-004, MVP-008 | Historical output retention distinguished from exact rerun. |


### Important anti-goals / traps


| Bullet / строка | Исходная идея | Действие | Destination IDs | Почему / точность покрытия |
| --- | --- | --- | --- | --- |
| B148 / 196 | do not make vacancy/job the universal root object; | LINK | ANTI-001 | Universal root guard. |
| B149 / 197 | do not make Research Project own all data; | LINK | ANTI-002 | Bank ownership guard. |
| B150 / 198 | do not equate “not seen” with disappearance; | LINK | ANTI-010 | Not_seen guard. |
| B151 / 199 | do not equate page change with real-world entity change; | ADD_ANTI_GOAL | NEW-028, INT-011, INT-012 | Explicit page-change vs entity-change clause missing in JSON. |
| B152 / 200 | do not treat embeddings/vector indexes as canonical truth; | LINK | ANTI-006 | Derived index not truth. |
| B153 / 201 | do not mix raw facts with AI interpretation; | LINK | INT-011, TGT-017 | Annotation/interpretation separate from raw evidence. |
| B154 / 202 | do not silently overwrite history; | LINK | ANTI-009 | Append traceable corrections. |
| B155 / 203 | do not use one opaque similarity score for every purpose; | LINK | ANTI-008 | Known explainable profile aggregate allowed. |
| B156 / 204 | do not create one giant GenericObject schema; | LINK | ANTI-007 | Common metadata envelope allowed, giant domain schema avoided. |
| B157 / 205 | do not hide source disagreement inside one aggregate; | LINK | ANTI-013 | Show divergence. |
| B158 / 206 | do not silently refresh when user asked only for a query; | LINK | ANTI-014 | Authorised policy does not require new confirmation every time. |
| B159 / 207 | do not implement every analytics idea before clear user value. | LINK | ANTI-015 | Opportunities not mandatory work. |


## 9. Reference matrix: наблюдаемый паттерн → наше применение

Это выбранные design references, не product dependencies и не доказательство feature quality. Официальные материалы проверены 2026-10-05; это claims/documentation самих продуктов, без hands-on benchmark и без проверки тарифов, APIs, MCP, export/локальности. Последние параметры нужны EXP-002 перед build-vs-buy решением.

По сравнению с предыдущим описанием Palantir требуется уточнение: актуальная документация объединяет **data, logic, action и security**, не только первые три.


| Pattern ID | Система | Что подтверждают официальные материалы | Requirement links | Применение и предел | Официальный источник |
| --- | --- | --- | --- | --- | --- |
| FAB.capture / FAB.bank_search | Fabric | Unified поиск сохранённого материала, natural-language queries, поиск по тексту и быстрый retrieval capture. | INT-002; MVP-002/003; TGT-010/022 | Изучить saved item → retrieve → reuse UX. Из паттерна не следуют все supported formats MVP, обязательная AI organisation или cloud topology. | [Источник](https://fabric.so/features/search) |
| FAB.example_search / FAB.media_search | Fabric | Поиск по example, visual и cross-media content search заявлены в feature materials. | INT-003; TGT-004/010/011 | Изучить select item → find related. Mechanics relevance и независимость evidence эта feature page не подтверждает. | [Источник](https://fabric.so/zh/features/similar-search) |
| PAL.objects_links / PAL.data_logic_actions | Palantir Foundry Ontology | Objects/properties/links; data, logic, action и security объединены семантической моделью. | INT-006; MVP-001; TGT-001/008/024 | Semantic layer над backend и explicit actions. Это архитектурный ориентир, без enterprise масштаба и обязательных Foundry dependencies. | [Источник](https://www.palantir.com/docs/foundry/ontology/why-ontology) |
| ZOT.item_attachment / ZOT.snapshot | Zotero | Items, attachments, notes; URL link отличается от локально сохранённого web snapshot. | INT-011; MVP-001/002; TGT-017 | Capture identity/provenance, bytes vs link, note origin. Zotero не доказывает нашу Source/Entity модель и не гарантирует immutable evidence contract. | [Источник](https://www.zotero.org/support/quick_start_guide) |
| FEED.monitoring | Feedly | AI Feeds для search/tracking, topic prioritization, dedupe/muting. | TGT-007; COND-001; NEW-013 | Watch policy, continuous intake и подавление повторного шума. Универсальные entity/metric/similarity watches — наше расширение. | [Источник](https://docs.feedly.com/article/523-getting-started-with-feedly) |
| ALPHA.cited_answers / ALPHA.repeatable_grid | AlphaSense | Generative Search с citation к исходному snippet; Grid применяет prompts к множеству документов с source citations. | TGT-014; EXP-002; возможный UX для TGT-006 | Evidence drilldown и repeatable structured analysis. Citation не заменяет admissibility, counter-search или independent verification. | [Источник](https://www.alpha-sense.com/solutions/market-intelligence-platform/) |


Дополнительное объяснение URL vs snapshot: [Zotero Links vs Snapshots](https://www.zotero.org/support/kb/links_vs_snapshots). Fabric — основной bank UX reference; Palantir — semantic architecture reference. Это предложенные ориентиры, а не автоматически принятые CURRENT_DECISION о выборе готового продукта. Readwise Reader можно исследовать позже для capture/read/highlight flow; здесь новый benchmark по нему не проводился.

Reference pattern должен иметь `purpose`, `requirement_ids`, `source_url`, `checked_on`, `evidence_level=official_description`, `limitations`, `adoption_state=reference_only`. Не добавлять reference каждому requirement для красоты: longitudinal comparability, frozen RunSpec, historical ResultOccurrence и formal bitemporal требуют собственных contracts независимо от сходства с чужим продуктом.

## 10. Traceability и нормализованный schema

Рекомендуется один canonical structured registry + согласованный human view: JSON хранит stable ID/status/statement и rationale; master показывает ID и fuller объяснение того же смысла. Если master narrative меняется, parity check должен обнаружить scope/status drift. До введения generator допускается manual parity review; два независимо редактируемых списка обязательств без cross-links снова создадут ambiguity.

Для каждого entry нужны:

| Поле | Назначение / правило |
| --- | --- |
| `id`, `statement`, `status` | Stable identity и текущая intent classification; ID не переиспользовать после split. |
| `kind` | user_outcome / product_capability / data_contract / architecture_constraint / research_method / governance / implementation_choice. |
| `axes` | Проверенные AX-V ссылки. Mapping предложен для всех 115 строк. Ось не означает текущую реализацию. |
| `origin` | path/section/excerpt, conversation context при наличии; `basis` = explicit_user / delegated_decision / archive_adopted_draft / design_inference / review_proposal / unknown. |
| `origin_confidence` | Не выдавать author-интерпретацию из archive за точную user attribution. У старых 115 исходные per-entry user origins неизвестны; базовое source — текущая registry snapshot. |
| `human_ref` | Master path + section + stable ID anchor; номера разделов в отчёте — предложенный crosswalk. |
| `rationale` | Почему feature/constraint нужен, отдельно от origin. |
| `depends_on`, `related_to` | Hard prerequisite отдельно от тематической связи и applicable-capability dependencies. |
| `scenario_ids` | GSU scenarios + concrete acceptance; Golden Scenario не equals обязательный MVP test. |
| `reference_patterns` | Именованные проверенные паттерны + источник; пустой список допустим. |
| `trigger`, `trigger_state` | CONDITIONAL: condition и unknown/inactive/active с evidence/date; предполагаемые условия не автоматически active. |
| `decision` | CURRENT_DECISION: scope, stability, rationale, decided_on при известной дате, revisit_trigger. |
| `lifecycle`, `supersedes`, `children` | active/superseded/rejected, splitting and replacement. Отличать lifecycle от приоритета/обязательности. |
| `change_history` | Append-only from/to/scope change + reason/source/date; исходную неизвестную дату adoption не выдумывать. |
| `acceptance` | При promotion в implementation contract: observable result + verification; сейчас многие строки остаются intent. |
| `schema_version`, `registry_revision` | Отдельно version формата и ревизия содержимого. Нужны перед generator/CI/автоматическим consumer. |

Предлагаю CURRENT_DECISION добавить в taxonomy. REJECTED/SUPERSEDED учитывать через `lifecycle`, сохраняя последний meaningful status и history; иначе смешаются приоритет, принятость и архивность. Пока отчёт не требует нового lifecycle ни для одной исходной записи: при split способ сохранения parent выбирать при schema amendment.

Пример будущей записи (draft proposal, не содержимое текущего registry):

```json
{
  "id": "DEC-003",
  "status": "CURRENT_DECISION",
  "kind": "implementation_choice",
  "statement": "Initial persistent storage backend is GitHub; domain semantics are backend-independent.",
  "axes": ["AX-V15", "AX-V22"],
  "origin": {
    "basis": "explicit_user",
    "context": "User selected GitHub in the supplied conversation",
    "original_adoption_date": null
  },
  "decision": {
    "scope": "implementation",
    "stability": "provisional",
    "revisit_trigger": ["media volume", "query performance", "automation", "privacy"]
  },
  "reference_patterns": [],
  "lifecycle": "active"
}
```

DEC-003 здесь — пример schema; это не выделенный ID. При применении использовать mapping NEW-004 → реально свободный ID. Scope privacy не придумывает запрет: это ранее сохранённый trigger, который нужно оценить по actual prototype data.

### Кандидатные dependencies для наиболее существенных entries

Это предложенные prerequisites, не полный формальный dependency graph и не основание включать все TARGET в MVP. Когда dependency условная (например Watch по metric), она применяется только к соответствующему mode.


| ID | Предложенные dependencies | Комментарий |
| --- | --- | --- |
| MVP-003 | MVP-001, MVP-002 | Зависимости предложены этим review; не означают уже реализованный contract. |
| MVP-005 | MVP-001, MVP-004 | Зависимости предложены этим review; не означают уже реализованный contract. |
| MVP-006 | MVP-005, MVP-004 | Зависимости предложены этим review; не означают уже реализованный contract. |
| MVP-007 | MVP-006 | Зависимости предложены этим review; не означают уже реализованный contract. |
| MVP-008 | MVP-001, MVP-007 | Зависимости предложены этим review; не означают уже реализованный contract. |
| MVP-009 | MVP-001, MVP-003, MVP-007, MVP-008 | Зависимости предложены этим review; не означают уже реализованный contract. |
| MVP-011 | MVP-001, MVP-002, MVP-003, MVP-004, MVP-005, MVP-006, MVP-007, MVP-008, MVP-009 | Зависимости предложены этим review; не означают уже реализованный contract. |
| TGT-005 | MVP-004 | Зависимости предложены этим review; не означают уже реализованный contract. |
| TGT-006 | MVP-006 | Зависимости предложены этим review; не означают уже реализованный contract. |
| TGT-007 | MVP-005, MVP-006, MVP-007 | Зависимости предложены этим review; не означают уже реализованный contract. |
| TGT-009 | MVP-001 | Зависимости предложены этим review; не означают уже реализованный contract. |
| TGT-011 | TGT-004 | Зависимости предложены этим review; не означают уже реализованный contract. |
| TGT-012 | MVP-001, MVP-006, MVP-007 | Зависимости предложены этим review; не означают уже реализованный contract. |
| TGT-014 | MVP-001, TGT-017 | Зависимости предложены этим review; не означают уже реализованный contract. |
| TGT-018 | MVP-004, TGT-001 | Зависимости предложены этим review; не означают уже реализованный contract. |
| TGT-020 | TGT-003, TGT-012 | Зависимости предложены этим review; не означают уже реализованный contract. |
| TGT-023 | MVP-001, MVP-009 | Зависимости предложены этим review; не означают уже реализованный contract. |
| COND-001 | MVP-006, MVP-007, TGT-007, TGT-008 | Зависимости предложены этим review; не означают уже реализованный contract. |
| COND-006 | EXP-004, OPEN-018 | Перед implementation promotion проверить минимальную нужную capability subset; ссылки на EXP/OPEN — review readiness, не runtime dependency. |
| COND-009 | TGT-003, TGT-012 | Зависимости предложены этим review; не означают уже реализованный contract. |


### Golden Scenario crosswalk

| Scenario | Registry links | Gate / смысл |
| --- | --- | --- |
| GSU01 Freelance longitudinal | MVP-011, MVP-001/006/007/008; TGT-003/012/013/020/021 | MVP reduced repeated-observation proof; полный analytics flow TARGET. |
| GSU02 Mechanics discovery | NEW-002/021; TGT-004/010/011/024, EXP-004 | TARGET design/quality scenario; не MVP mechanics-engine gate. |
| GSU03 Apps | TGT-002/003/009/012/020, OPP-001 | Design/target; change-point step optional. |
| GSU04 News/events | TGT-002/014/018/020.E; NEW-023; COND-007 | Target/domain; scenario illustrates possible bitemporal need, не активирует formal implementation без use case. |
| GSU05 Image save→similarity | MVP-002; TGT-004/010/011 | Save-only slice MVP, similarity/research enrichment TARGET. |
| GSU06 Sources/tools/recipe/schedule | MVP-004; TGT-005/006/008; COND-001 | Reuse TARGET, scheduled execution conditional. |
| GSU07 Backfill | TGT-012, COND-007 | Formal dual-time conditional. |
| GSU08 Identity correction | TGT-009, ANTI-009 | Full merge/split/repair TARGET. |
| GSU09 Source scope | MVP-004/006; TGT-005 | MVP effective allowed scope; full route history TARGET. |
| GSU10 UI↔ChatGPT | MVP-009, TGT-022/023, NEW-020 | Basic callable handoff MVP; rich selection UI TARGET, literal side panel opportunity. |
| GSU11 Config authority | MVP-006; TGT-005/006/007; NEW-022 | MVP freeze simple config; full owners/registries later. |
| GSU12 Historical result output | MVP-008 | Retained membership/rank/reasons MVP; similarity example does not make similarity MVP. |
| GSU13 Search regression | COND-006, OPEN-018, EXP-004 | Conditional QA trigger. |
| GSU14 Evidence loops | INT-011; MVP-001; TGT-017 | MVP origin/derivation separation, full support graph TARGET. |

## 11. Что действительно требует scope choice

Большая часть правок — housekeeping и уточнение guarantees. Отдельно выделены решения, которые нельзя выдавать за уже принятые:

1. **Negative examples — решено 2026-10-05:** пользователь утвердил OPP-017 как TARGET_REQUIRED, вне MVP. Решение применено к map/master/backlog/scenario note. Первоначальное предложение оставить FUTURE отменено; факт смены статуса сохранён.
2. **Clustering:** сохранить human target intent через TGT-020.E, но не превращать advanced clustering/emergence algorithms в MVP. Если grouped distributions достаточно для конечного продукта, понизить этот child отдельно с rationale.
3. **Минимальные provenance links MVP:** предлагаю explicit ID references сейчас, общий typed Relation layer позже. Это устраняет расхождение, сохраняя возможность basic history и output lineage.
4. **Initial deployment details:** GitHub выбран; private/public repo policy, runtime, media bytes vs URI/cache, actual callable ChatGPT handoff и private-data trigger требуют concrete prototype design. Этот отчёт не выбирает всё за пользователя.
5. **Enum/schema mechanics:** PARTIALLY_SUPPORTED, CURRENT_DECISION, lifecycle vs status, parent/child IDs и generation/parity flow — schema предложения, а не опубликованный API contract.

Все остальные unanswered product questions сохраняются OPEN_DECISION с return trigger. Отчёт не предлагает спрашивать пользователя о каждом KEEP или routine phrasing fix.

## 12. Применение отчёта в следующей редакции

1. Сохранить snapshot 115 текущих entries и origin uncertainty; добавить metadata/schema version и append-only history.
2. Зафиксировать согласованные decisions, исправить mechanics и Source boundary одновременно в master/map/scenarios. OLD OPEN-011 history не стирать: закрыть только initial backend часть.
3. Выполнить 4 splits и новые explicit backlog dispositions. Исторический 08 сохранить с ссылками, запретить его трактовку как second authoritative requirements list.
4. Включить новые entries либо в existing subclauses, либо под свободными ID; сохранить NEW/B mapping и original excerpts. Отсутствие отдельного ID не должно скрывать status/guarantee части compound feature.
5. Master human view должен показывать ID и те же scope/status guarantees; update README/reasoning guide/INDEX/review ledger только для vNext notes, accepted v1.11 отдельно.
6. После edits проверить unique IDs, valid statuses/kinds/axes, destination/dependency/reference links, closed decision vs OPEN consistency, retained origin/history, human/JSON scope parity и 159/159 coverage. Только после этого закрывать MRQ-001/002/003/004 как addressed; этот отчёт сам по себе их не исправляет.
7. Выбрать конкретный MVP slice и закрыть нужные schema/API/runtime details; затем implementation contracts и соответствующие meaningful tests. Reference benchmark EXP-002 до крупных commodity подсистем, не вместо проверки actual requirements.

### Что проверено в самом отчёте

Автоматически проверены: точное множество 115 исходных IDs; 159 исходных bullets без пропусков и повторов; наличие review judgment у каждой записи; отсутствие dangling proposal/child destination links; принадлежность axes текущим 22 ID; валидность kind; исходные JSON statements и trigger text берутся из snapshot. Предлагаемые mappings, statuses и rationale — результат содержательного review, не доказанные runtime behaviors.

В сопровождающем обновлённом ZIP применено только решение OPP-017 и связанные documentation/index изменения. Остальные исходные archive entries, включая accepted v1.11, byte-identical. Полная нормализация и новый implementation contract ещё не применены.
