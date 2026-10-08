# Независимое ревью всех выполненных работ — AWR-20261007

Дата: 2026-10-07T08:49:10.342144+00:00. Канонический Review Log: `../DRAFT_NOTES/REVIEW/2026-10-07_COMPLETED_WORK_REVIEW_LOG.json`; checks: `../DRAFT_NOTES/REVIEW/2026-10-07_COMPLETED_WORK_REVIEW_CHECKS.json`; подтверждение записи: `../EXPERIMENTS/completed_work_review/all_completed_review_38d75beb67fb4b23909e09f3898bfe70/REVIEW_SAVE_RECEIPT.json`.

Объект — вся уже выполненная работа проекта, а не только последний UI или ответ. Проверены planning/version requirements, R0 contracts и experimental R1 intake→SQLite→reads→lexical search→commands→producer→UI, текущее состояние и сохранённая evidence/history.246 актуальных scoped файлов прочитаны с проверкой SHA; дополнительно root README и5 accepted routing/architecture inputs.264 accepted v1.11 файла подтверждены побайтово; полный legacy runtime заново не принимался.

Исходная цель — локальный Bank для материалов, идей и анализа, удобное сохранение/поиск/reuse через ChatGPT при включённом PC. Два потока версий, Source≠Entity, staged MVP/TARGET, exact bytes/CAS/replay/receipts и пользовательское требование вести документы остаются применимыми. Публичные данные/отсутствие секретов не означают публичность всех идей. Другие AI и always-on cloud не планировались. Задача не переопределена; будущие authoring/deployment/full release gates не объявлены дефектами уже ограниченной карточки.

Итог: **пять подтверждённых проблем; P-1/P-2/P-3/P-5 открыты, P-4 исправлена в документации при guarded записи.** Полный зелёный native результат/готовность реального Bank не подтверждены.

## 1. Реальные проблемы

### P-1 — Длинное JSON-число выходит из контролируемого отказа

**Статус:** open_confirmed; severity `high`. Ledger ID `AWR-20261007-P01`. Основной результат.

**Цель/требование:** LOCAL_WRITE_CONTRACT: ограниченный malformed input получает явный отказ; VERIFIED_TRANSPORT отделён от Bank acceptance.

**Условия → механизм:** JSON содержит целое число длиннее лимита преобразования Python, оставаясь внутри разрешённого размера файла. json.loads вызывает ValueError при превышении integer conversion limit. strict_json ловит UnicodeError/JSONDecodeError/RecursionError, но этот ValueError пропускает.

**Воспроизводимый пример:** strict_json(b'{"n":' + b'1'*5000 + b'}', 16384, 64): 5006 bytes → uncaught ValueError. Настоящий READY на Windows: 5199 bytes с manifest_byte_length из 5000 цифр → тот же выход из read_package; staging пуст.

**Последствие:** Standalone reader аварийно завершается вместо структурированного REJECTED; controller может свести это к общей I/O-ошибке. Повреждение/принятие этих данных не наблюдалось.

**Proposal:** Нормализовать отказ преобразования числа, сохранив собственные коды Rejected, duplicate/nonfinite/Unicode проверки и interpreter digit guard. Не отключать глобальный лимит Python. Проверить actual reader и controller на границах.

**Evidence:** `EXPERIMENTS/completed_work_review/all_completed_review_38d75beb67fb4b23909e09f3898bfe70/REGRESSION_NATIVE.json#PARSER_LONG_INTEGER`, `EXPERIMENTS/completed_work_review/all_completed_review_38d75beb67fb4b23909e09f3898bfe70/REGRESSION_NATIVE.json#NATIVE_READY_LONG_INTEGER`, `EXPERIMENTS/completed_work_review/all_completed_review_38d75beb67fb4b23909e09f3898bfe70/REGRESSION_LOCAL.json#PARSER_LONG_INTEGER`

### P-2 — Приватность каталогов не дополнена проверкой ACL отдельных входных/SQLite файлов

**Статус:** open_confirmed; severity `high`. Ledger ID `AWR-20261007-P02`. Основной результат.

**Цель/требование:** LOCAL_WRITE_CONTRACT/private current-user+SYSTEM roots: не доверять существующим файлам с небезопасными правами. Отсутствие секретов не отменяет целостность локального Bank; идеи не объявлены публичными.

**Условия → механизм:** Внутри проверенного приватного каталога один существующий payload, DB или cache имеет явный Everyone FullControl ACE. Native verify_private_acl на самом файле отвергает UNTRUSTED_DACL, но названные пути эту проверку файла не вызывают. Проверка parent/package ACL не доказывает file ACL; bypass traverse у другого токена может позволять доступ к известному пути, если файл его разрешает.

**Воспроизводимый пример:** Только в собственных временных Windows fixtures добавлен Everyone ACE. Root/package остались private. Store принимает DB; cache rebuild → BUILT; защищённый reader принимает payload → VERIFIED_TRANSPORT/OK. Для каждого файла прямой native ACL guard правильно отвергает тот же DACL.

**Последствие:** Небезопасный существующий файл продолжает использоваться доверенным компонентом. При соответствующих правах другого локального пользователя возможны чтение/изменение известного файла; фактический доступ другим токеном/утечка в этом ревью не проверялись.

**Контрдоказательство/границы:** Producer Fileguard и read exports проверяют file ACL; приватность обычных synthetic roots и блокирование write/rename сейчас подтверждены. Это не опровергает пропуск на других путях.

**Proposal:** Ввести SQLite-совместимые проверки owner/DACL/reparse/hardlink/identity для существующих DB/cache и нужных sidecars; проверить READY/manifest/payload/nested entries. Сохранить normal SQLite writes/recovery; не переносить эксклюзивный no-write handle режим без адаптации и не чинить права неизвестных файлов автоматически.

**Evidence:** `EXPERIMENTS/completed_work_review/all_completed_review_38d75beb67fb4b23909e09f3898bfe70/REGRESSION_NATIVE.json#NATIVE_DATABASE_AND_CACHE_FILE_ACL`, `EXPERIMENTS/completed_work_review/all_completed_review_38d75beb67fb4b23909e09f3898bfe70/REGRESSION_NATIVE.json#NATIVE_INTAKE_PAYLOAD_FILE_ACL`, `EXPERIMENTS/completed_work_review/all_completed_review_38d75beb67fb4b23909e09f3898bfe70/SUPPLEMENTAL_NATIVE_CHECKS.json`

### P-3 — Ссылки многократно перечитывают старые оригиналы, без общего бюджета historical work

**Статус:** open_confirmed; severity `medium`. Ledger ID `AWR-20261007-P03`. Основной результат.

**Цель/требование:** DB8/LOCAL_WRITE bounded work; интерфейс ожидает завершения serial worker и должен оставаться предсказуемым при росте Bank.

**Условия → механизм:** Маленький валидный пакет повторяет ссылки на три разных старых commit, тогда как cache удерживает только два. Каждый cache miss вызывает проверку всего commit со streaming hash всех его оригиналов. Цикл трёх commit вытесняет запись на каждом обращении; incoming byte/operation caps не задают общий бюджет старых прочитанных bytes/времени.

**Воспроизводимый пример:** 64 notes ×3 refs; 3 старых оригинала по1MiB. Incoming payload62966 bytes; 192 commit verifications/384 BLOB reads; 201450240 retained bytes (~192.12MiB), amplification3199.3; Windows import3.133s; ACCEPTED. Такой же счёт независимо получен локально.

**Последствие:** Лишнее I/O/CPU растёт с размерами уже принятого Bank; close ждёт эту работу. При64MiB на старый оригинал этот же счёт означал бы около12GiB чтения (расчёт, не измеренный latency). Неверного результата/коррупции в пробе нет.

**Отличие от прежней проблемы:** DB-CARD-20261006-P-3 относился к recursive helper/materialization всей истории и устранён в исходном scope. Новый механизм — повторное hashing из-за cache churn; прежнее исправление не переоткрывается автоматически.

**Proposal:** Проверять каждый нужный commit однократно за request с компактным verified metadata и ограниченной памятью; отдельно ограничить retained bytes/elapsed work и cancellation до commit. Не ослаблять integrity/ref checks; определить правдивые rollback/UNKNOWN outcomes.

**Evidence:** `EXPERIMENTS/completed_work_review/all_completed_review_38d75beb67fb4b23909e09f3898bfe70/REGRESSION_NATIVE.json#REFERENCE_VERIFICATION_WORK`, `EXPERIMENTS/completed_work_review/all_completed_review_38d75beb67fb4b23909e09f3898bfe70/REGRESSION_LOCAL.json#REFERENCE_VERIFICATION_WORK`

### P-4 — Четыре старые importer findings и текущий заголовок ISSUES не синхронизированы с native completion

**Статус:** resolved_documentation_readback; severity `medium_local`. Ledger ID `AWR-20261007-P04`. Локальная проблема документации/проверки.

**Цель/требование:** Пользователь: вести документы; завершение/проблему/решение фиксировать для надёжного продолжения.

**Условия → механизм:** Следующий агент читает current classification/ISSUES header вместо реконструкции всей истории. Ledger содержал resolved_in_work_item_runtime_pending и scope native verification pending, хотя component ISSUES, native42 report и receipt уже фиксируют resolved_native_synthetic/completed.

**Воспроизводимый пример:** Fresh source comparison: все4 ledger записи runtime pending; те же4 component issues resolved_native_synthetic; native historical42 PASS, источник тот же.

**Последствие:** Локальная документальная ошибка: повторение уже закрытой части работы/неверный текущий статус. Полная R1/production acceptance из component completion не следует.

**Исправление:** При записи этого ревью синхронизированы4 current classifications, scoped component acceptance и ISSUES header; appended history/evidence. Исходные report/receipt/история сохранены. Новые P-2/P-3/P-5 остаются отдельными открытыми записями.

**Evidence:** `DRAFT_NOTES/REVIEW/FINDINGS.json`, `EXPERIMENTS/sqlite_importer/ISSUES.json`, `PLANNING/WORK_ITEMS/R1_SQLITE_IMPORTER_RECEIPT.json`, `EXPERIMENTS/completed_work_review/all_completed_review_38d75beb67fb4b23909e09f3898bfe70/RETAINED_EVIDENCE_CHECKS.json`, `EXPERIMENTS/completed_work_review/all_completed_review_38d75beb67fb4b23909e09f3898bfe70/REVIEW_SAVE_RECEIPT.json`

### P-5 — Windows importer test42 декодирует localized CMD output неверной кодировкой

**Статус:** open_confirmed; severity `medium`. Ledger ID `AWR-20261007-P05`. Локальная проблема документации/проверки.

**Цель/требование:** Native evidence должно реально доходить до reparse guard assertion; исходный42-case acceptance должен воспроизводиться без false-green.

**Условия → механизм:** Python -X utf8 и локализованный CMD mklink /J возвращают OEM bytes. capture_output=True,text=True пытается decode как UTF-8; reader thread получает UnicodeDecodeError(0xa4), stdout остаётся None. Eager diagnostic made.stdout+made.stderr вызывает TypeError даже при returncode0.

**Воспроизводимый пример:** Общий native suite и изолированный unchanged-source test42 повторили ERROR. Фактический mklink returncode0/stdout None/stderr empty. Direct bytes-capture supplementary probe создаёт junction и Store правильно отвергает UNTRUSTED_DB_FILE.

**Последствие:** Дефект теста/QA: guard assertion не выполняется, полный текущий native suite не green. Дефект приложения в rejection junction этим не доказан.

**Proposal:** Capture bytes и явно/безопасно формировать bounded diagnostic; не менять глобальную codepage/OS privileges. Повторить настоящий test42 и проверить не-UTF8 output fixture.

**Evidence:** `EXPERIMENTS/completed_work_review/all_completed_review_38d75beb67fb4b23909e09f3898bfe70/REGRESSION_NATIVE.json`, `EXPERIMENTS/completed_work_review/all_completed_review_38d75beb67fb4b23909e09f3898bfe70/TARGETED_NATIVE_RECHECK.json`, `EXPERIMENTS/completed_work_review/all_completed_review_38d75beb67fb4b23909e09f3898bfe70/TARGETED_NATIVE_CONSOLE.txt`, `EXPERIMENTS/completed_work_review/all_completed_review_38d75beb67fb4b23909e09f3898bfe70/SUPPLEMENTAL_NATIVE_CHECKS.json`

## 2. Спорные/неопределённые места

### U-1 — текущие права на создание symlink

test_reader08/09/10/29 получили WinError1314 при создании fixture до guard assertion. Свежая capability probe: file/directory symlink create=false; hardlink/junction guards=true.

Не доказан ни новый guard defect, ни PASS этих4 случаев. Исторический reader32 PASS сохранён, но текущую capability он не заменяет.

P-2 не включает утверждение о произошедшей утечке: отдельный user token не проверялся. P-3 подтверждает redundant work, а не универсальный latency SLA. Оба ограничения сохранены в соответствующих canonical findings.

## 3. Что выдержало проверку

- 115 unique requirements,159 backlog,45 proposals(41pending) parity; milestone DAG acyclic,18 existing cards17completed/1prepared; all actual required inputs exist and one current pointer.
- R0/R1 staged versions, Source≠Entity, R2 tracked_research boundary, OPP-017 TARGET outside blockingMVP and pending normalization retain original meanings.
- Local233 regressions+8 storage mechanism checks PASS; Windows current secure share-mode/ACL private fixture/hardlink/junction guards PASS and storage8 PASS.
- Typed pinned reads/history/original byte integrity, exact replay/CAS/receipts, search/manual oracle, producer publish≠accepted/UNKNOWN recovery and native mapped UI flows retained/currently rerun in scoped suites.
- 7 historical component reports total255 groups match current own-source hashes; old FAIL/runtime Tk warning/captures retained. Independent current counterprobes found uncovered issues despite those previous PASS reports.
- 264 accepted baseline files unchanged; no real Bank/user import/install/OS codepage/privilege change, no commit/push; fresh native suite source246 unchanged.

| Повторная проверка | Фактический результат |
|---|---|
| Local existing regression |233/233 PASS; skips0|
| Local storage mechanism |8/8 PASS отдельно|
| Windows original aggregate |268/274 PASS;4 fixtureERROR,1 testERROR,1 audit harnessFAIL|
| Windows targeted follow-up |Actual UI09 PASS; actual test42 ERROR reproduced|
| Windows current unique accounting |269PASS,4 capabilityblocked,1 testdefect; полный suite не green|
| Windows storage/capability |8/8 storage PASS; actual privateACL/share-mode/hardlink/junction PASS; symlink create Win1314|
| Corrected document invariants |PASS local/native;115requirements/159backlog/45proposals,41pending;18cards17completed/1prepared; no DAGcycles/missingactualinputs|

Повтор existing suites сам по себе не обеспечивает независимость. Независимо составлены numeric boundary/individual file ACL/reference-work counterprobes, document invariant checker и direct storage/junction checks; результаты сравнивались с заявленными contracts. Historical255 component groups/source hashes проверены отдельно, их aggregate не использован вместо свежего выполнения. После docs write появляется новая fixes prepared карточка; table18 отражает состояние именно до review save.

Ошибки нового review harness не выданы за дефекты приложения: initial document checker ошибочно требовал uppercase PASS/receipt field; исправленный standalone checker PASS. UI09 initial audit capture relocation менял test module path; настоящий source-preserving UI09 повторно PASS. Initial reports сохранены. P-5, напротив, повторяется в настоящем неизменённом исходном тесте и остаётся открытым.

## 4. User Assistance / Process Improvement

**UA-1 → U-1:** перед полным повторным native acceptance минимально полезно выполнить только4 symlink теста в Windows context, имеющем право создавать такие ссылки. Это устранит fixture Win1314 и позволит дойти до guards. Сейчас не требуется; review/исправления и остальные тесты не блокируются. Глобальные privileges/DeveloperMode не менялись. Простого самостоятельного эквивалентного доказательства без такого права нет.

Туннель восстановлен после user reconnect; эта зависимость закрыта. Calls ограничены25s, длинный native процесс запускался один раз; чтение его результата продолжено после reconnect. Не нужны повторные ответы о данных/AI/PC-on.

## 5. Deferred / Follow-up Items

**D-1: File/URL/note authoring, Entity/Collection editor, automatic handoff и durable failed-attempt status.** Отдельные будущие карточки; prepared-input UI не выдавался за полный new-intent journey. Связь: Полное удобное сохранение/reuse R1. Вернуться: После fixes review и перед полным R1 acceptance. Если не вернуться после триггера: Ручная подготовка/неполный recovery путь не закрывают полный MVP workflow.

**D-2: Реальные root/deploy/privacy/backup/restore/hardware/scale checks, особенно непубличные идеи.** Все пробы synthetic; пользователь исключил секреты, но не объявил все идеи публичными. PC-on architecture соответствует ответу. Связь: Надёжное реальное хранение Bank. Вернуться: Перед first real Bank/import/install, непубличными материалами, повышением limits или release. Если не вернуться после триггера: В реальном использовании могут остаться недоказанные access/recovery/durability/volume свойства.

**D-3: Интегрированное R0 UC/type/schema compatibility и formal full release acceptance.** 264 принятых baseline файла сохранены, новые contracts имеют scoped tests; всю legacy acceptance не переисполняли и release не объявлен принятой. Связь: Совместимость исследовательской системы и приложения. Вернуться: Перед milestone acceptance/изменением canonical consumers/contracts. Если не вернуться после триггера: Раздельно работающие компоненты могут не доказывать полную совместимость потребителей и переходов.

**D-4: Ручная keyboard/mouse usability, accessibility и installed UI packaging.** Mapped Tk/generated events/owned captures проверены; это не human usability acceptance. Связь: Удобное настольное приложение. Вернуться: При installed/user-facing usability review. Если не вернуться после триггера: Автоматические journeys не выявят все неудобства ввода, фокуса и accessibility.

## 6. Вопросы и Proposals

**Q-1 — Исправлять обнаруженные дефекты перед draft authoring?** Authoring расширяет использование уже найденных parser/file-trust/work-budget путей. **Proposal:** Подготовлена ограниченная fixes карточка; текущий pointer указывает на неё. Authoring остаётся prepared и следует после подтверждённых fixes. Это рабочий Proposal, не новое исходное требование пользователя. Категория: **высокая уместность самостоятельного решения**; user answer non-blocking. Новые authoring implementation/acceptance и реальное использование отложены до fixes; ответы пользователя не нужны.

**Q-2 — Как повторить4 symlink cases без подмены evidence?** U-1 оставляет часть native security regression непроверенной. **Proposal:** Сохранять blocked status и вернуться к UA-1 при следующем полном acceptance. Сейчас никаких глобальных OS изменений. Категория: **высокая уместность самостоятельного решения**; user answer non-blocking. Только4 fresh cases. Если понадобится изменение OS configuration/privileges, это отдельное решение пользователя.

## Ограничения и AX01–AX26

- Регрессионные suites — повторные проверки исходных тестов, а не сами по себе независимое доказательство. Независимость обеспечена fresh source/hash checks, иной document checker, storage mechanism probe, adversarial numeric/ACL/work probes и прямым native junction guard.
- Initial audit document checker ожидал uppercase PASS и receipt field, которых исторические карточки не требуют. Его PROBE_ERROR — ошибка нового checker. Standalone corrected DOCUMENT_RECHECK_LOCAL/NATIVE PASS; исходные reports не переписаны.
- Initial audit UI capture relocation меняла test_ui.__file__, нарушая путь subprocess import в UI09. Изолированный реальный unchanged-source UI09 PASS. Первоначальный FAIL сохранён как harness issue, не application finding.
- 4 symlink fixture errors Win1314 остаются blocked U-1; test42 encoding ERROR P-5 остаётся открытым, supplementary junction PASS его не заменяет.
- Actual cross-user token effective access не выполнялся; P-2 подтверждает отсутствие required fileACL validation/приём неверногоDACL, а не произошедшую утечку.
- No real Bank/init/import/install/provider/network/physical power loss/full legacy regression/full R0/R1 release. Неизвестный процесс старой работы не восстановлен как факт: проверялись доступные файлы, receipts, raw evidence/history и новое выполнение.
- Объёмные fixtures и native повторный suite заняли701.542s; connector calls ограничены25s. Timeout/409 Туннеля разрешены чтением уже запущенного процесса, suite не перезапускался вслепую. User reconnect решён.
- Оригинальные7 component native reports/receipts и ранние fail/warning/captures сохранены. Native P-3 latency — одна synthetic проба, не universal hardware benchmark.

Все26 audit axes рассмотрены в пределах сделанной работы. Это scoped assessment, не формальное принятие whole reusable system/release. Полная матрица сохранена в checks; ниже краткий результат.

| Axis | Оценка scope | Основание/граница |
|---|---|---|
|AX01 Purpose & decision fitness|findings|Цель соответствует локальному Bank;P-1/P-2/P-3 ограничивают readiness.|
|AX02 Authority, pointers & state consistency|findings_resolved_in_docs|Один CURRENT_WORK_ITEM; P-4 выявлен и синхронизирован при записи.|
|AX03 Schema, enums & version integrity|scoped_checked|115 IDs/version pairs/schema/enums/DDL/static creation-query checks; P-1 numeric rejection gap.|
|AX04 Identity, deduplication & idempotency|scoped_checked|Actual same-ID exact replay/CAS/receipt tests; независимые user intents не реализованы D-1.|
|AX05 Temporal correctness & daily history|scoped_checked|Pinned revision/as-of/history/reopen regressions; полный daily research timeline вне R1.|
|AX06 Method/scope/source-route comparability|planned_not_runtime_accepted|Source≠Entity/R2 tracked research boundary сохранены; method/source comparability full gate D-3.|
|AX07 Sources, provenance & evidence traceability|scoped_checked|Asset binding/exact bytes/hashes/provenance contracts и receipts; authoring provenance D-1.|
|AX08 Sampling & measurement validity|out_of_implemented_slice|Sampling/research evaluation ещё будущая system work; новых результативных claims нет.|
|AX09 Economics & effort validity|out_of_implemented_slice|Research economics не реализованы; measured work amplification отдельно P-3, без universal cost claim.|
|AX10 Dependency/change propagation|scoped_checked|Dependency graph acyclic, inputs существуют;115/159/45 inventory parity.|
|AX11 Bootstrap, reuse & handoff|partial|Native pipeline через UI подтверждён; automatic handoff/new intent D-1.|
|AX12 Configurability & extensibility|scoped_checked|Version staging/frozen baseline/limits reviewed; реальные roots/config D-2.|
|AX13 Crash, retry, concurrency & recovery|scoped_checked|CAS/replay/BUSY/UNKNOWN/atomic rollback/process death/hot journal/cancel tests; hardware D-2.|
|AX14 Security, path confinement & data safety|findings_and_blocked|Actual ACL acceptance gapP-2;4 symlink setup blockedU-1; current hardlink/junction/share-mode guards PASS.|
|AX15 Migrations & backward compatibility|preservation_only|264 baseline hashes equal; broader migrations/consumer compatibility D-3.|
|AX16 Portability & capability awareness|findings_and_blocked|Local233 +native274 attempted; P-5 codepage test defect; U-1 current capability differs from historical run.|
|AX17 Performance & long-term scalability|finding|Reference cache churn/192 verifications P-3 confirmed; large production scale D-2.|
|AX18 Diagnostics, observability & repairability|findings|P-1 loses controlled diagnostic; scoped controller outcomes/logs; durable failed attempts D-1.|
|AX19 Test quality & refactor resilience|finding|P-5 reproduced; audit-only checker/UI harness mistakes independently corrected, original evidence preserved.|
|AX20 Release, manifest, docs & workbook integrity|scoped_checked_with_doc_fix|Cards/receipts/history/source match; P-4 corrected; full release not accepted.|
|AX21 Use-case routing correctness & determinism|routing_lineage_checked|UC19 selected via existing3.2.0 registry; routing fixtures/full legacy conformance not rerun.|
|AX22 Use-case boundaries, orthogonality & coverage|scoped_checked|Transport≠domain≠Bank acceptance, command/query/publication boundaries preserved; future queries/research separated.|
|AX23 Workflow composition, transitions & closure|partial|Prepared→publish→save→receipt/replay scoped journeys; new-intent/automatic lifecycle D-1.|
|AX24 DRY, canonical ownership & derived-view integrity|scoped_checked_with_doc_fix|No second authority introduced; P-4 stale classifications corrected with additive history.|
|AX25 End-to-end action & evidence traceability|scoped_checked|7 source-matching component reports/receipts, current fresh results,9 owned capture hashes, guarded review save.|
|AX26 Architecture simplicity & complexity budget|scoped_review|Existing local SQLite+file pipeline fits PC-on scope; no service/cloud/OCR/R2 scope expansion. P-3 bounded fix proposed, not full architecture budget acceptance.|

## Review Log — компактный checkpoint

Canonical JSON: `DRAFT_NOTES/REVIEW/2026-10-07_COMPLETED_WORK_REVIEW_LOG.json`. Review ID `AWR-20261007`, UC19 outcome `changes_required`; declared transition UC16 сохранён, подготовлена fixes карточка как working Proposal.

- Scope: вся выполненная planning/R0/experimentalR1/docs/evidence работа;246scoped source files+6additionalinputs;264baseline preserved. No full legacy/runtime/release acceptance.
- Problems: P-1 controlled numeric rejection; P-2 individual fileACL validation; P-3 historical work/cache churn; P-5 localized native test42. Все open. P-4 stale original importer statuses/header исправлены с history/readback; новые проблемы не закрыты этой записью.
- Checks: local233+8 PASS; Windows269uniquePASS/274,4blockedU-1,1testdefectP-5; native8storage PASS. Original268aggregate/UI harness/document checker mistakes retained with corrections, без false-green.
- Uncertainty/assistance: U-1/UA-1 — только будущие4 fresh symlink cases требуют capableWindows context; no OS policy change now. Cross-user actual leakage not tested; no leakage claim.
- Deferred: D-1authoring/handoff/editor beforeR1; D-2realdeploy/privacy/backup/hardware/scale before real use/release; D-3full compatibility beforemilestone/contractchange; D-4human usability/a11y before installedUIacceptance.
- Proposal Q-1: fixes first; `PLANNING/WORK_ITEMS/R1_COMPLETED_WORK_REVIEW_FIXES.json` prepared, currentpointer updated; высокая уместность самостоятельного решения, useranswernon-blocking. Q-2retainU-1untilfreshcapableacceptance; no global OS changes.
- Save: append-only new review/log/checks, original docs backed up, previous history retained. Factual save evidence is `EXPERIMENTS/completed_work_review/all_completed_review_38d75beb67fb4b23909e09f3898bfe70/REVIEW_SAVE_RECEIPT.json`; считать сохранённым только при успешной actual write/readback.
