# Критическое ревью плана и requirements Universal Bank vNext

Дата: 2026-10-05. Review ID: `2026-10-05_PLAN_REQUIREMENTS_CRITICAL_REVIEW`.

**Вывод:** направление соответствует доступному пользовательскому замыслу. Текущие документы не готовы служить однозначным implementation plan и sole authoritative inventory: принятие нескольких решений не отражено в registry/master, scope двух видов расходится, а фазовый план не фиксирует границу готовности MVP. Это реальные planning/document gaps; потеря данных или runtime bug Universal Bank этим ревью не установлены.

## Объект, scope и восстановленная задача

Основной план — master §16, Phases A–F. Requirements — текущие 115 entries JSON + fuller human master. Дополнительно проверяются vision/model/research/source/UI notes, 159 backlog bullets, Golden Scenarios, normalization report v1.1 и targeted OPP-017 update.

Legacy `freelance_research_system_feature_architecture_red_tests/REFERENCE/DEVELOPMENT_PLAN_vNext.md` (Phases 0–7) проверяется отдельно как прежняя дорожная карта use-case/query развития v1.11. Совпадение имени vNext не делает её планом нового Universal Bank. Ни legacy plan, ни accepted v1.11 не требуется переписать лишь из-за расширения цели.

Исходная цель: сохранять полезные files/URLs/notes/domain objects без research; искать/организовывать/reuse как seeds/evidence/references; повторно исследовать и накапливать longitudinal knowledge с provenance, scope/coverage и historical results. ChatGPT — reasoning/orchestration; приложение — durable state/validated operations/UI. Domains добавляются через packs, providers заменяемы. Mechanics similarity — TARGET/Golden Scenario, не MVP blocker; Source отдельно от Entity; initial storage GitHub; master+map единый authoritative inventory, 08 historical inbox. Позднее OPP-017 явно promoted в TARGET вне MVP.

Критерий успеха проверки: отличить current inconsistency от intentionally open design, доказать findings конкретными примерами, проверить scope последних edits, сохранить history и useful future triggers. Это ревью не реализует остальные normalization proposals.

## Независимая reconstruction перед оценкой плана

Из outcomes и dependencies независимо получается такой минимальный порядок:

1. Привести authoritative intent к принятым решениям; определить supported save/read/search форматы, basic links/time/identity, source boundary, minimal RunSpec и actual callable ChatGPT↔app writeback.
2. Durable Bank/IDs/Asset-vs-Entity/annotations/collections/basic browse и text search; external acquisition остаётся через доступные interactive tools.
3. Frozen RunSpec/Run/ResultOccurrence и повторное исследование с basic comparable history. Versioned Recipe/Route registries не обязательны для заморозки простой explicit configuration.
4. **MVP checkpoint:** independent image/file save, game store→research seed→save result и reduced two-run freelance observation/history comparison; source/run provenance и no-silent-refresh checks.
5. TARGET: rich representations/search/similarity (включая OPP-017), typed relations, general Current/Changes/Trend/Interpretation/Health, claim verification и richer domain packs. Each capability имеет свой acceptance.
6. Scheduling/direct integrations/scale/security extensions активируются соответствующим actual trigger; placement «позже» не отменяет trigger, если он появляется раньше.

Это recommended crosswalk, не незаметно принятый новый execution plan. Сравнение с A–F показывает: общая dependency direction разумна; отсутствует явный переход от minimal B к принятому MVP до расширения C/D.

## 1. Реальные проблемы

Ниже шесть существенных findings. Первые четыре продолжают существующие MRQ records, а не стирают прошлое review. Known pending normalization остаётся текущим gap authoritative документов, но не означает, что ограниченное изменение OPP-017 было выполнено неправильно.


### MRQ-001 — Authoritative registry lacks per-entry traceability

**Классификация:** confirmed problem; major_for_authoritative_inventory. **Влияние:** на основной результат планирования/inventory.

**Цель:** Единый durable inventory, позволяющий рассуждать по stable ID/AX-V без реконструкции чата.

**Недостаток:** После targeted update только OPP-017 имеет kind/axes/human_ref/change_history. У 114/115 entries этих links/history нет; CURRENT_DECISION отсутствует в taxonomy.

**Условия:** Новый агент/изменение requirement status/вопрос о влиянии изменения оси.

**Механизм:** Registry объявлен authoritative, но связь с human rationale, осью и основанием отсутствует; внешний proposal report содержит mappings, которые в registry ещё не применены.

**Воспроизводимый пример:** Запрос «какие requirements меняются по AX-V04?» не может получить явный registry crosswalk. При редактировании TGT-010 прежний status/reason легко исчезает.

**Последствие:** Авторитетное понимание снова приходится выводить из чата/внешних отчётов; разные агенты могут дать разные scope решения.

**Доказательства:** REQUIREMENTS_MAP.json: per-entry metadata count 1/115; Master status/authority and classification vocabulary; Normalization report §§5,10,12.

**Правка:** Применить metadata и решение об authority к registry/master; старые origins помечать unknown/archive-sourced, не приписывать пользователю. Не закрывать MRQ-001 по факту одного report.


### MRQ-002 — Backlog triage is not yet incorporated into authoritative inventory

**Классификация:** confirmed problem; major_for_inventory_completeness. **Влияние:** на основной результат планирования/inventory.

**Цель:** Master+map — единственный current inventory; 08 остаётся historical inbox.

**Недостаток:** 159/159 triage выполнен в standalone report, но live map остаётся 115 entries с изменением только OPP-017. Offline, import, nested collections, local representations и pack packaging не получили явные current dispositions в authoritative map.

**Условия:** Планирование по master/map без доступа к отдельному normalization report или 08.

**Механизм:** Исторические идеи сохранены, но часть классификаций существует только в NEW-* proposals отчёта; authority в JSON/master уже объявлена текущей.

**Воспроизводимый пример:** Offline expectations найдены в 08 и NEW-014 отчёта, но отсутствуют в 18 OPEN_DECISION live map. Агент, читающий только registry, не узнает о сохранённом вопросе.

**Последствие:** Обещание полноты authoritative inventory не выполняется; optional ideas могут потеряться или позднее быть заново приняты как требования.

**Доказательства:** 08: nested collections/import/offline/pack packaging bullets; REQUIREMENTS_MAP.json: current 115 entries; Normalization report: NEW-005/007/014/015/016/017; 159 unique B rows.

**Правка:** Перенести согласованные dispositions в registry либо включить explicit classified subclauses. Сохранить 08 и origin ссылки; это pending normalization, не провал узкого OPP-017 update.


### MRQ-003 — Human/machine scope and guarantee parity remains inconsistent

**Классификация:** confirmed problem; major_for_mvp_scope. **Влияние:** на основной результат планирования/inventory.

**Цель:** Одинаковый MVP/target смысл независимо от чтения master или JSON; mechanics similarity не блокирует MVP.

**Недостаток:** Master §5.5 всё ещё требует games «domain structure and mechanics similarity», тогда как согласован TARGET/Golden Scenario. В §5.1 explicit provenance/use links отсутствуют в JSON MVP; PARTIALLY_SUPPORTED vs PARTIAL и target clustering также не согласованы.

**Условия:** Составление backlog/acceptance/schema на основании только одного authoritative вида.

**Механизм:** Два вида содержат разные обязательства; запись MVP-011 остаётся game/mechanics-oriented object flow, а human text задаёт более сильный gate. Target Relation не отделён явно от минимальных MVP references.

**Воспроизводимый пример:** Реализация сохраняет/исследует game, но не считает mechanics similarity. JSON MVP-011 можно признать выполненным, human §5.5 — нет. Другой consumer принимает только PARTIAL и не понимает master PARTIALLY_SUPPORTED.

**Последствие:** Разные implementers получают разный объём MVP и несовместимые guarantees. Clustering intent master 8.2 теряется при JSON-only planning.

**Доказательства:** Master §§5.1,5.5,7.2,8.2; Map MVP-001/011, TGT-001/014/020; Provided conversation: mechanics=Golden Scenario/TARGET, not MVP blocker.

**Правка:** Исправить mechanics scope по принятому решению; явно выделить minimal MVP references. Согласовать enum и clustering disposition, сохранив history/parity. Не объявлять enum mismatch runtime failure: vNext consumer отсутствует.


### MRQ-004 — Source/Entity decision is made but absent from current canonical definitions

**Классификация:** confirmed problem; important_before_data_contract_acceptance. **Влияние:** на основной результат планирования/inventory.

**Цель:** Source и Entity — отдельные canonical types; endpoint/corpus может ссылаться на предмет мира.

**Недостаток:** Переданный разговор решает boundary, но master §3.1 всё ещё включает source в Entity examples, §3.2 отдельно определяет Source без явной optional Entity связи.

**Условия:** Принятие schema для Reuters/Steam/subreddit и перенос examples в code.

**Механизм:** Entity identity и acquisition endpoint не разведены нормативным текстом; downstream designer может выбрать subtype или отдельные независимые дубли вопреки принятому решению.

**Воспроизводимый пример:** Reuters organization + website + RSS: subtype model заставляет endpoint совпадать с semantic identity, а отсутствие subject_entity link не выражает принадлежность двух Sources одной organization.

**Последствие:** Неверные identity/provenance boundaries либо повторное обсуждение уже делегированного решения.

**Доказательства:** Master §3.1 Entity examples and §3.2 Source; 05_SOURCES_TOOLS_INTEGRATIONS.md Source/Route examples; Provided Source != Entity decision.

**Правка:** Обновить definitions, references и examples. Исходное MRQ-004 было uncertain; теперь концептуальный вопрос решён, подтверждён текущий documentation drift. Это не доказанный runtime duplication bug.


### RVP-001 — Initial GitHub backend decision is still represented as open

**Классификация:** confirmed problem; local_planning_inconsistency. **Влияние:** локальное расхождение планирования.

**Цель:** Зафиксировать принятую initial persistence choice без предрешения runtime/local/cloud future.

**Недостаток:** OPEN-011 полностью остаётся «Initial storage stack and local/cloud topology»; master не содержит GitHub или current decision. Решение присутствует лишь в conversation/normalization proposal NEW-004.

**Условия:** Выбор storage stack по текущей карте.

**Механизм:** Смешаны уже выбранный backend и всё ещё открытая execution/media/cache/sync topology.

**Воспроизводимый пример:** Planner снова рассматривает Postgres vs local store как незакрытый стартовый выбор, хотя пользователь уже выбрал GitHub; либо объявляет весь local/cloud scope решённым при закрытии OPEN-011.

**Последствие:** Лишняя переоценка backend или ошибочное закрытие topology. Основной продуктовый замысел не меняется.

**Доказательства:** Map OPEN-011/015; Master §14 Storage; Conversation GitHub choice; normalization NEW-004.

**Правка:** Разделить closed initial backend и open runtime/media/sync remainder; private repo/details — отдельные implementation decisions, не приписывать exact policy пользователю.


### RVP-002 — Universal Bank phase plan lacks an explicit MVP acceptance checkpoint

**Классификация:** confirmed problem; major_planning_gap_before_implementation. **Влияние:** на основной результат планирования/inventory.

**Цель:** План позволяет понять первый полезный slice, зависимости и критерий готовности MVP без реализации всего TARGET.

**Недостаток:** Master §16 A–F — recommendation без MVP stop/acceptance mapping. Phase B содержит core state/API, Phase C — full Current/Changes/Trend/Health + verification, Phase D — games/mechanics similarity и multimodal search. Ни одна фаза не ссылается на stable requirement IDs или не фиксирует, какая часть MVP-011 закрыта.

**Условия:** Планирование первой implementation release и объявление фазы/MVP готовой.

**Механизм:** MVP proof распределён по advanced phases, где TARGET смешан с basic proof; отсутствие explicit checkpoint позволяет как остановиться слишком рано, так и считать весь C/D mandatory.

**Воспроизводимый пример:** Команда завершает B и называет это MVP без двух freelance observation cycles и game reuse proof; другая команда перед MVP реализует C+D mechanics engine/Trend/verification. Обе опираются на A–F, но полезный first release разный.

**Последствие:** Неоднозначная acceptance boundary и scope growth/недоказанная универсальность. Это planning readiness gap, не нарушение уже принятого phase execution contract.

**Доказательства:** Master §16 Phases A–F; no ID crosswalk/MVP acceptance checkpoint; Master §5.5, Map MVP-011; Legacy plan has phase acceptance policy but its release goal is separate.

**Правка:** Добавить явный MVP checkpoint для B + reduced longitudinal/game/file proofs; отдельные TARGET/conditional phases. Legacy Phase0–7 сохранить как исторический plan, а не переименовывать его accepted state.


Не повышены до current defect: отсутствие graph DB/scheduler/formal bitemporal/full OCR/advanced forecasting; отсутствие exact hard-exclusion threshold до implementation; unresolved protocol stack до Phase A. Эти capability choices намеренно staged/open. Присутствие вопроса само по себе не означает невозможности продукта.

## 2. Спорные или неопределённые места


**URVP-001 — Какой минимальный executable ChatGPT↔application/Git writeback и effective RunSpec используются в MVP?**

Основание: OPEN-012 и runtime/media часть OPEN-011 не закрыты; RunSpec draft содержит Recipe/Route refs, сами registries TARGET. Ограничение: Нет принятого vNext executable schema/API prototype; наличие native web/Deep Research не доказывает automatic app writeback. Дальше: В Phase A/B выбрать минимальные supported fields/callable handoff; unsupported provider internals показывать unknown. Нельзя пока утверждать ни реализуемость выбранного deployment, ни его невозможность.

**URVP-002 — GitHub хранит project/system state, Bank metadata или также raw media bytes?**

Основание: Пользователь выбрал GitHub; точная media topology/limits/ownership policy не зафиксирована. Ограничение: Согласие на backend не задаёт точный file layout и long-term local/cloud expectation. Дальше: Вернуть перед asset storage contract; не решать whole topology из выбора repository.

**URVP-003 — Какая часть clustering — обязательная конечная capability?**

Основание: Master §8.2 задаёт target clustering; TGT-020 явно его не отражает. Report предлагает target child, но child не принят. Ограничение: Конкретные algorithms/emergence detection не выбраны; намерение допускает staging. Дальше: Сохранить current human intent при parity correction либо явно согласовать понижение. Само отсутствие clustering algorithm сейчас не дефект.

Отдельное ограничение воспроизводимости: immutable RunSpec сохраняет effective configuration, а stored ResultOccurrence — фактически выданный output. Это не обещание повторить live web/AI вывод bit-for-bit. Предыдущий normalization report различает эти guarantees; это различие выдержало проверку.

## 3. Что выдержало проверку


- Направление отвечает доступному user intent: personal Universal Bank, save независимо от research, reuse seeds, repeated longitudinal knowledge, ChatGPT/app разделение, replaceable providers.
- Сохранено полезное разделение CORE/MVP/TARGET/CONDITIONAL/OPPORTUNITY/EXPERIMENT/OPEN/ANTI и 22 expansion axes; статус не равен implementation completion.
- OPP-017 корректно promoted в TARGET_REQUIRED вне MVP; old statement/status/area сохранены в change_history, ID не переиспользован, related/axis IDs существуют; master/backlog/scenario согласованы.
- Independent counters: 115 unique registry IDs, 25 TARGET/19 FUTURE, 11 MVP. Другие categories unchanged. Report содержит 115 unique entry rows и 159 unique backlog rows, action counts 55/55/4/1.
- ZIP CRC и все INDEX hashes/sizes совпадают; все старые ZIP entries сохранены; все 264 legacy files byte-identical исходному attached archive. Это preservation evidence, не повторная runtime certification v1.11.
- Review history сохранена, findings не закрыты автоматически. Targeted OPP-017 update действительно не применяет остальную normalization; это scope discipline.
- Legacy development plan явно относится к evolution v1.9→v1.11 use cases/query products; его phase acceptance policy полезна и не становится ошибочной из-за последующего Universal Bank scope.
- Frozen configuration и historical ResultSet/Occurrence, query/command separation, discovery!=measurement, scope-relative completeness защищают реальные user outcomes.
- Reference patterns отдельно от dependencies; official descriptions corroborate Fabric bank/search, Palantir data/logic/actions/security, Zotero URL/snapshot distinction, Feedly AI Feeds, AlphaSense cited answers/Grid. No hands-on/API/price/export benchmark claimed.


Официальные источники перепроверенных reference descriptions:

| Reference | Проверенный паттерн | Предел проверки |
| --- | --- | --- |
| [Fabric](https://fabric.so/features/search) | Bank/content search, visual/semantic retrieval, quick-capture retrieval | Official feature claims; не benchmark качества |
| [Palantir Ontology](https://www.palantir.com/docs/foundry/ontology/why-ontology) | Objects/properties/links; data/logic/action/security | Semantic architecture reference; не выбор vendor/backend |
| [Zotero](https://www.zotero.org/support/kb/links_vs_snapshots) | URL link vs locally retained page snapshot | Snapshot reference не доказывает immutable research contract |
| [Feedly](https://docs.feedly.com/article/523-getting-started-with-feedly) | AI Feeds, tracking/filtering/deduplication | Не доказательство universal metric/similarity Watch |
| [AlphaSense](https://www.alpha-sense.com/solutions/market-intelligence-platform/) | Source-snippet citations и repeatable document Grid | Citation сама не равна verification/independence |

## 4. Deferred / Follow-up Items


| ID / сохранить | Почему не current defect | Связь | Return trigger | Последствие после trigger |
| --- | --- | --- | --- | --- |
| DF-MRQ-001 — Минимальные access/secret/provider-exposure/data ownership boundaries при private GitHub/Bank data. | В проверяемом объекте нет running Bank или выбранного actual data classification; отсутствие enterprise ACL сейчас не доказанная утечка. | COND-003, OPEN-017, MVP-002, AX-V16, AX-V22 | Перед authenticated Git integration и первым сохранением private/sensitive material; конкретные controls зависят от actual access/data. | Credentials/data могут попасть в неверный scope или external model exposure без нужных controls. |
| DF-MRQ-003 — Версия requirements schema и automated links/parity validators. | Independent scan не обнаружил consumer REQUIREMENTS_MAP вне DRAFT_NOTES; current JSON валиден. Missing traceability — уже текущая MRQ-001, а consumer breakage пока не наблюдается. | REQUIREMENTS_MAP.json, AX-V19, AX-V20 | Первый generator/CI/API consumer/migration registry. | Смена структуры может ломать автоматические consumers или читать неверную intent classification. |
| DF-RVP-001 — Operational semantics и quality evaluation для отрицательных examples: dimension, threshold/predicate, missing features, soft vs hard. | OPP-017 — target intent, similarity engine ещё не реализован; exact metrics/thresholds OPEN-018, EXP-004. | OPP-017, TGT-011, EXP-004, COND-006, OPEN-018 | Перед implementation/acceptance отрицательных примеров; regression sets — когда ranking product-critical/regularly changes. | Hard exclusion может удалять релевантные результаты по theme/art или неизвестным features; объяснение не соответствует реальному ranking. |
| DF-RVP-002 — Git-backed write atomicity, idempotency, concurrency, recovery, asset placement and derived-index rebuild contract. | Backend выбран, StorageBackend implementation ещё нет; нельзя объявить потерю данных по одному storage preference. | MVP-001, MVP-006, MVP-007, MVP-008, OPEN-011, COND-002, AX-V15, AX-V22 | До первого writable prototype и особенно до concurrent/unattended writes или substantial media volume. | Частично сохранённые Run/Result refs, lost updates, growing Git/media footprint либо невозможность recover/rebuild. |
| DF-RVP-003 — Identity correction не должна менять старые ResultOccurrences; separate retained output and current alias/index resolution. | Full merge/split TGT-009 ещё не реализован. S13 «reindexes derived representations/results» допускает index rebuild, не доказывает canonical rewrite. | MVP-008, TGT-009, ANTI-009, GSU08, GSU12, S13, S17 | При реализации merge/split/reprojection и выдаче historical runs после correction. | Если перестроение затронет canonical membership/rank/reasons, старый run окажется переписан; historical lineage станет недостоверной. |


Ранее сохранённый DF-MRQ-002 (acceptance при promotion требований в implementation contracts) остаётся релевантным. Он не подменяет текущий RVP-002: checkpoint и scope надо уточнить уже в плане; exact feature-level tests должны появиться до реализации соответствующих capabilities.

## 5. Возникшие вопросы


1. Для MVP GitHub хранит только metadata/project state или также raw assets? Где выполняется приложение и расположен text index?
2. Достаточен ли MVP reduced two-run freelance comparison + game store/research/reuse + independent image/file save, при full Trend/Health/similarity later? Это рекомендуемый checkpoint, не ещё принятый execution contract.
3. Target clustering intent master сохраняем явно в registry или выбираем opportunity? От этого зависит TGT-020 decomposition, не MVP.
4. Перед implementation negative examples: какой observable predicate означает hard exclusion для выбранного domain/profile и как поступать с unknown/missing features?


Эти вопросы не блокируют сохранение ревью. Они привязаны к next contracts/prototype work; повторного подтверждения уже принятого OPP-017 или Source!=Entity не требуется.

## Проверка того, как выполнена предыдущая работа

Доступен actual process в текущем разговоре: normalization pass создал proposal report, а затем пользователь выбрал negative examples и разрешил targeted change. Независимый byte diff подтверждает ровно одно изменённое requirement — OPP-017; history/prior entry/target scope сохранены. Сопровождающие master/backlog/GSU02/index изменения ограничены этим решением. Поэтому не применять остальные normalization proposals в том update было соблюдением scope, а не неполным выполнением задачи.

В proposal report счетчики «55 KEEP/55 CLARIFY/4 SPLIT/1 CHANGE_STATUS» пересчитаны независимо и совпадают. Таблица 24 TARGET/20 FUTURE относится к исходному snapshot; рядом явно указаны текущие 25/19. Это не неверный подсчёт current map. `NEW-*` и child IDs помечены как proposals, поэтому их отсутствие в live map — pending adoption, не runtime dangling-reference failure.

Независимость проверки не организационная: основной агент повторно реконструировал минимальный план по user outcomes и напрямую проверил artifacts. Не использовалось предположение, что собственные прошлые выводы автоматически верны. Неведомый процесс внешней истории v1.11 не реконструирован как факт.

## Ограничения проверки


- Ревью выполнено одним основным агентом с отдельной reconstruction/checking задачей, без отдельного human reviewer или subagent. «Независимость» — подход и independent checks, не организационная независимость.
- Доступны supplied conversation и current workspace artifacts; hidden original conversations/user origins по каждой записи неизвестны.
- Нет работающей universal vNext реализации, production data/search relevance set или принятого app/API schema; runtime/quality/latency/cost/operational security не доказаны.
- Legacy runtime tests здесь не запускались; сохранность 264 файлов подтверждена byte comparison. Historical accepted statuses не переаттестованы.
- Проверка reference patterns основана на official descriptions, без hands-on или pricing/licensing/API/MCP/export verification.
- Прежние документы не объявляются ошибочными по новым требованиям: некоторые findings — нынешние intent/parity gaps после решений, а не ошибки исходной note-preservation работы. Последний узкий update оценён по своему scope.

## Компактный Review Log


**Объект / scope:** current `vnext_requirements_updated.zip` (reviewed input SHA-256 `2d5403b2717ba6ba5a7e506c97a0f20bb756a51b9b4d80bf529006699e5380ee`), Universal Bank master §16 A–F, 115 JSON requirements, human scope, 159 backlog bullets, scenarios, normalization report v1.1 и scoped OPP-017 update; legacy Phase0–7 отдельно как прежний plan. Runtime vNext не заявлен проверенным.

**Итог:** направление соответствует user intent; current authoritative documents и план требуют consolidation до implementation. Изменение OPP-017 корректно; остальные normalization proposals ещё не applied.

**Подтверждённые существенные проблемы:**

- MRQ-001: у 114/115 entries нет explicit kind/axes/human_ref/change_history; reasoning inventory недостаточно traceable (основной результат).
- MRQ-002: полная 159-item triage есть в report, но часть ideas/open questions не classified в authoritative map (основной результат).
- MRQ-003: MVP mechanics, minimal provenance links, claim enum и target clustering различаются в human/JSON (основной scope).
- MRQ-004: Source!=Entity решено в контексте, definitions ещё ambiguous; uncertainty reclassified как documentation drift (основной data-contract scope).
- RVP-001: initial GitHub всё ещё внутри полностью open OPEN-011; closed backend нужно отделить от open topology (локально).
- RVP-002: A–F не фиксирует MVP checkpoint/requirement acceptance, basic proof смешан с TARGET C/D (основной plan readiness).

**Неопределённости:** минимальный callable ChatGPT/app/Git handoff и effective RunSpec; metadata vs raw assets в Git; точная target clustering obligation. Эти вопросы не доказывают runtime failure.

**Что прошло:** 115 unique IDs, target/future=25/19, остальные counts сохранены; OPP-017 history/scope/reference parity; 115/159 report coverage; ZIP CRC и INDEX hashes; все 264 legacy files byte-identical; history intact; official reference descriptions подтверждены без hands-on claims.

**Deferred / возврат:**

- DF-MRQ-001: actual auth/private/sensitive use → access/secret/exposure policy; иначе возможны неверные права/экспозиция данных.
- DF-MRQ-003: первый schema consumer/generator/CI → format version и parity/links validation; иначе consumer breakage/drift.
- DF-RVP-001: implementation negative examples → dimension/exclusion/unknown-feature semantics и relevance comparison; иначе erroneous exclusions/объяснения.
- DF-RVP-002: первый writable prototype/concurrent writes/media growth → atomicity/idempotency/recovery/assets/index policy; иначе partial refs/lost updates/неуправляемый storage.
- DF-RVP-003: merge/split/reprojection → historical ResultOccurrence retention отдельно от rebuilt indexes; иначе переписанная история выдачи.
- Existing DF-MRQ-002: перед implementation promotion → feature-level acceptance; не заменяет текущий plan checkpoint fix.

**Ограничения:** supplied context only; single-agent independent approach, не separate reviewer; no vNext runtime/quality/cost/security acceptance, legacy tests не переаттестованы; official-product descriptions вместо API/export/pricing benchmark.

**Открытые вопросы:** Git metadata/raw media/runtime placement; reduced MVP proof checkpoint; target clustering scope; operational hard exclusion/missing-feature rule до implementation.

**Disposition:** сохранить current defects открытыми; не закрывать MRQ по этому review. В archive добавлены review/log/checks, ledger history events и updated INDEX; intent requirements/план не исправляются автоматически. Legacy contracts и прошлые reviews сохранены.



## Source/Entity documentation consolidation — 2026-10-05

R0-SOURCE-ENTITY-001 applied the already confirmed Source != Entity boundary, optional subject/provider Entity reference and SourceRoute ownership to master/model/source examples and MVP-004/TGT-005 statements. Source-only saving does not create an Entity; Entity merge/split does not automatically merge/split Sources/routes.
The earlier MRQ-004 finding and normalization proposal tables above remain historical. Their documentation-drift part is now resolved; the durable MRQ-004 ledger retains history and a separate actual persisted types/schema-compatibility follow-up before R0 acceptance. NEW-003 is not created as a new requirement ID; the confirmed boundary is consolidated into existing requirements. OPEN-004, other normalization proposals and R0/release acceptance remain open.
Evidence: PLANNING/WORK_ITEMS/R0_SOURCE_ENTITY_RECEIPT.json. Axes: AX-V06, AX-V12.
