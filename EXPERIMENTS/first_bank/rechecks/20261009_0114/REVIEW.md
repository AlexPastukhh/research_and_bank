# Первый Bank: результат выполнения и готовность следующего шага

Review ID: BFR-20261009-02. После review пользователь выбрал B и остальные Proposals; applied followup подтверждён3local/4native, exact native report и real-config reopen сохранены в AGREED_CORRECTIONS_RECEIPT.json / REAL_CONFIG_FOLLOWUP_CHECK.json. Проверенная версия: Git `727061ced0a5f288d19b6979f27779c9d98792ae`; HOST и remote main совпали. Дата: 2026-10-09. Targets: реализация R1-FIRST-USABLE-BANK-001 и готовность R1-OBJECT-AUTHORING-001. Это review реализации и следующего плана, не замена предыдущего review. Исходные FUBER-20261009-01 / OAR-20261008-01 IDs сохраняются как source references; локальные F/PR ниже принадлежат этому Review ID.

## Краткий результат / Для пользователя

Основной путь первого Bank подтверждён независимыми16local/17Windows проверками исходного review. Найденный NORMAL F-P-001 исправлен: после подтверждённого восстановления индекса снимается только сообщение о недоступном поиске, Bank/newer-head/disconnect уведомления сохраняются. Followup3local/4Windows PASS,0skips; это focused проверки на изменённом исходнике, не новый full-suite180/181 прогон. Пользовательская визуальная приёмка FUB10 остаётся pending.

Пользователь выбрал B и принял остальные recommended Proposals. Композиция PR-001/002/003/004B/005 COMMITTED атомарно; PR-004A rejected. HIGH: F-U-001 resolved явным выбором B, повторный A/B вопрос не нужен; F-P-002 resolved в плане (manual GUI gate), F-R-001 mitigated current-source/profile compatibility criteria. Actual editor native proof ещё впереди. Все11OBJ criteria сохранены; официальная R1_OBJECT_AUTHORING.json обновлена. Принятие плана не является завершением редакторов или полной приёмкой R1. CRITICAL нет.

Карта: «Что выдержало проверку» — первоначальные independent probes и отдельно новый focused followup; «Приоритетные находки и предложения» — canonical IDs и их актуальные dispositions; «Принятый план следующего шага» — B/current-source compatibility/manual GUI и early G1/G2 порядок; «Ограничения и помощь пользователя» — остающаяся визуальная/native граница. Следующее исполнение: early G1/G2, все11OBJ gates и подключение редакторов к существующему приложению в принятом B scope. Текущий официальный указатель первого Bank остаётся на FUB10; подготовку общего editor runtime можно выполнять независимо.

## Что восстановлено независимо

- N-1, explicit: usable локальный Bank для сохранения файла/URL/заметки, нахождения и получения материала после повторного открытия. Основание: пользовательское решение UFB-20261008-01 и текущий контекст работы.
- N-2, explicit after user selection B: развивать этот Bank до создания Entity, mixed Collection, targeted Annotation и редактирования версий Asset/Entity/Annotation/Collection. Пользователь выбрал подключение к существующему Bank и принял всю рекомендованную композицию; это теперь определённая граница следующего результата.
- FR-1: точные originals, immutable history/IDs/pins и честная каноническая квитанция; подготовка, диагностика и отсутствие receipt не заменяют доказательство принятия.
- FR-2: сохранность текущего Bank/неизвестной БД и frozen старых подготовок; никакой скрытой миграции, reset или изменения accepted264/canonical schema/DDL.
- FR-3: snapshot-first, изменения на HOST с проверкой актуальности, native proof; главное desktop GUI не автоматизируется. Пользовательская проверка интерфейса остаётся необходимой, не заменяется headless результатом.
- FR-4: все 11 OBJ gates сохраняются; SOURCE/Research/Watch, network и full release не становятся текущим scope.

Конкретные SQLite/7-root config, single worker, poll2s, diagnostic wrapper и authoring/2 — уже реализованные способы, а не новые Fundamental Requirements. Предложенные object-authoring limits — versioned technical profile, не постоянные пользовательские максимумы. Deadline, календарный бюджет и обещанный срок следующего этапа не установлены.

Desired Scenario первого этапа: на включённом Windows ПК пользователь открывает проверенный Bank, создаёт файл/ссылку/заметку, явно проходит подготовку/публикацию/сохранение, находит сохранённый материал, получает его точный original либо locator, после закрытия возвращается к тем же данным и квитанции. Открытое окно получает информацию о внешней записи, не меняя выбранную revision. Повторяющиеся затраты пользователя включают несколько явных действий записи, выбор поля поиска и ручное сохранение backup отдельно от рабочего диска. Эти действия не выдаются за автоматическую однокнопочную поставку всего продукта.

## Что выдержало проверку

Сначала были прочитаны исходный delivery decision, current cards, Bank contracts и код; затем созданы новые probes с независимыми byte/hash/SQL/ID ожиданиями. Старые отчёты использованы после этого для сравнения.

1. Fresh Tunnel: 185 файлов snapshot/source/contracts совпали по SHA-256; HOST clean, HEAD=remote main. Это контроль версии проверки, не заранее созданный нормативный baseline.
2. Собственный сквозной probe: три новые подготовки, фактические publish/save, SQL counts commits/revisions/receipts=[3,3,3], точные IDs в content/body search; UTF8/BOM/CRLF/emoji original совпадает побайтово после удаления external source. URL возвращён как locator без утверждения fetch.
3. Новый Backend переоткрывает те же receipts; exact replay возвращает REPLAY. Verified SQLite copy включает три commits. На реальном Bank отдельно выполнен только read-only reopen/observer: config и SHA БД не изменились, пользовательские материалы не импортировались.
4. Выполнен настоящий `Window.poll` с headless объектами вместо Tk widgets; наблюдение сохраняет pinned selected ref и показанный detail. Это проверка callback, не визуальная проверка его расположения/удобства.
5. Старый native coverage пересчитан из самих case records: исходный180 =177PASS+1FAIL+2ERROR; отдельный исправленный3PASS и notice followup1PASS дают180 уникальных latest PASS. Это несколько прогонов. Full clean180 на окончательном коде не заявляется. Их failures и source snapshots не удаляются.

Evidence исходного review рядом: PROBES_LOCAL.json, PROBES_NATIVE.json, HOST_SNAPSHOT_VERIFICATION.json, NATIVE_COVERAGE_RECOUNT.json, independent_probes.py. Этот старый counterexample сохраняется как исторический reproducer до исправления; актуальный regression — test_22 и AGREED_CORRECTIONS_RECEIPT.json с3local/4native PASS. Новые Windows17 включают самостоятельный read-only real-config check. Native probe source и report первоначально исполнялись в HOST Temp; JSON экспортирован сюда с тем же run_id и содержательными данными.

## Приоритетные находки и предложения

### F-R-001 — следующая интеграция может потерять возможности нового Bank

Type Risk; target Scenario/SRU composition следующей карточки, UPSTREAM относительно будущей реализации; priority HIGH; disposition mitigated: current-card compatibility criteria applied, actual editor runtime proof pending. До обновления `required_inputs` и acceptance map следующей карточки опирались на прежние creation/local_ui seams, не называют first_bank app/runtime/Flow и frozen authoring/2. Исходный план допускал отдельный composer/window. Это ещё не проявившаяся регрессия: нового editor runtime нет.

Механизм: реализовать новую Window от старого desktop/creation пути и считать legacy creation regression достаточной → редакторы работают в synthetic окружении, но current entrypoint может не получить их, автообновление/видимое index rebuild/attempts/backup либо UTF8 поведение остаются вне их доказанной композиции. Полезная альтернатива — переиспользовать нынешнюю интеграцию или предъявить проверяемое эквивалентное поведение; нельзя выводить loss только из отсутствия конкретного import.

PR-003, origin review, status committed: добавить current first_bank/config/receipt/attempt/result sources в входы карточки; явную compatibility matrix authoring/1, authoring/2 и object-authoring/1; критерии сохранения launch, UTF8 auto/explicit modes, pinned external visibility, search rebuild, diagnostics и backup. Для Asset replacement явно определить frozen input mode/media validation: replacement не получает text/plain автоматически от прежнего original. Canonical contracts и accepted264 неизменны. Autonomy HIGH: это сохранение уже достигнутого поведения, без расширения Need. RECOMMENDED_WITH PR-002 и PR-005; REQUIRES перед PR-004B.

Cost/Timing Delta: operation — текущие действия первого Bank не увеличиваются, уменьшается риск необходимости другого окна/ручной конфигурации; realization — нужны targeted compatibility checks и integration seam, количественная delta unknown; lifecycle — reuse снижает вероятность конкурирующих launcher/worker/config реализаций. Evidence verified по актуальным источникам; отсутствие будущей регрессии пока unconfirmed. Вопрос non-blocking для review, partially blocking для выбора integration/asset replacement design; закрывается обновлённой compatibility map и actual probes.

### F-P-002 — GUI gates следующей карточки противоречат текущему workflow

Type Problem текущего плана исполнения; target Work Requirement/OBJ10–11, UPSTREAM; priority HIGH; disposition resolved at current plan level. Historical OBJ10 требует generated mapped GUI events/owned screenshots, OBJ11 — screenshot visual QA; действующая пользовательская инструкция запрещает GUI основного desktop ради проверки и поручает пользователю открыть окно. Следование карточке буквально нарушает FR-3 либо не позволяет честно закрыть эти gates.

Нормативная хронология: карточка1.0 создана до позднейшего snapshot-first/Tunnel указания. Это не доказательство ошибки её первоначального составления; текущий execution plan необходимо адаптировать к новому ограничению.

PR-002, origin review, status committed: сохранить native headless/controller/callback/integrity/race tests; визуальную часть OBJ10/11 и NATIVE-OBJ-G3 заменить конкретным пользовательским маршрутом по всем новым формам, edit/history/conflict/reopen, фиксируя manual gate pending до evidence. Screenshot нужен только для конкретной проверки/проблемы. Сам gate не исключается. Autonomy HIGH: прямое следствие явного workflow; пользовательский выбор способа автоматизации не требуется. RECOMMENDED_WITH PR-003; REQUIRES для обеих PR-004A/B.

Cost/Timing Delta: operation — один реальный пользовательский проверочный маршрут; точное active time unknown. Realization — автоматизацию desktop заменяет headless proof + внешнее ожидание пользователя, elapsed нельзя вывести из суммы test effort. Lifecycle — сохраняется проверяемая карта GUI без зависимостей на управление рабочим столом. Partially blocking только visual/adoption closure; headless проектирование/исполнение не блокируется.

### F-U-001 — synthetic редактор и подключённые редакторы дают разные результаты

Type Decision Uncertainty; target Desired Scenario/version boundary и configuration SRU, UPSTREAM; priority HIGH; disposition resolved by explicit user B choice. Историческая развилка: real Bank уже настроен с profile research-bank-config/1 и семью roles; следующая карточка требует восьмого существующего object_authoring root и исключает Real Bank/import/install. Текущий `validate_roots` отвергает восемь roles с INVALID_ROOT_CONFIGURATION, `load` требует roots_for(base) строго из семи. Нельзя просто добавить ключ в config.json.

Вариант A: завершить bounded synthetic editor runtime/ручную проверку, оставить current Bank/launcher/config как есть; real adoption отдельной следующей карточкой. Вариант B: выполнить тот же synthetic proof, затем подключить редакторы к уже используемому приложению с явной безопасной настройкой object root и пользовательской приёмкой. Оба жизнеспособны, но разные promised outcomes. Исходный план A не является ошибочным из-за более позднего usable Bank; До выбора пользователя B не был разрешённой границей; теперь scope B принят, actual adoption остаётся зависимым от native/preservation proof.

PR-004A, origin previous-plan/review, status rejected после выбора B; историческая альтернатива: сохранить synthetic границу, добавить конкретный последующий adoption item до заявления доступности редакторов в рабочем Bank. Плюс: текущую конфигурацию не требуется менять сейчас. Минус: редакторы ещё не доступны в основном launch; позднее потребуются отдельная настройка и регрессия. Autonomy USER_REQUIRED для выбора итогового scope: цена и ценность промежуточного результата зависят от пользователя.

PR-004B, origin review, status committed, выбран пользователем для желаемого развития приложения: после общих OBJ/native gates явно описать управляемое подключение к существующему Bank. Scope принят пользователем; actual config/root adoption выполняется после предусмотренного native/preservation proof. Определить владельца eighth-root setup и versioned overlay/новую конфигурацию, old7 reopen, согласованность roots и rollback; no reset/implicit read-side creation/перезапись frozen journals. Использовать существующий entrypoint либо явно согласованный новый launch. Плюс: новые возможности входят в usable приложение; минус: дополнительная конфигурационная/adoption работа и её verification. Autonomy USER_REQUIRED для real adoption scope. REQUIRES PR-002, PR-003; ALTERNATIVE_TO и CONFLICTS_WITH PR-004A внутри одной delivery transaction; оба BUNDLE PG-001, ALTERNATIVE_GROUP.

Cost/Timing Delta A/B: operation — A требует отдельного synthetic запуска и позднейшего подключения; B стремится сохранить обычный запуск после одноразовой явной настройки. Realization — B добавляет current config/entrypoint adoption и регрессию сейчас; A переносит эти работы и ожидания в отдельную карточку. Количественная delta unknown, срока/ресурсов/slack нет. Lifecycle — B может исключить второй долгоживущий app/config путь; цена отката должна быть доказана до изменения real roots. Вопрос resolved: пользователь выбрал B и его dependencies. Actual config/entrypoint техническое доказательство остаётся OBJ7/G1 gate; дополнительных вопросов о той же границе нет.

### F-P-001 — сообщение о восстановлении индекса: исправлено

Type Problem; target SRU search status implementation (`first_bank/integration.py:Flow`, `app.py:Window.poll`), CURRENT; priority NORMAL; disposition resolved after local/native followup. Требование: честно показывать доступность поиска.

Reproduction до исправления: успешное наблюдение Bank → `Flow.apply('rebuild', ERROR)` устанавливает «Поиск пока недоступен» → повторная операция возвращает BUILT → observation того же token подтверждает cache_ready=true. Observed: index_ready=true, notice содержит прежнюю ошибку; Window.poll показывает notice вместо «поиск готов». Expected: сообщение о недоступности снимается при доказанном восстановлении, сохраняя unrelated newer-head/disconnected уведомления. Механизм: успешная rebuild ветка меняет index_ready, но не управляет собственным error notice. Следствие: вводящий в заблуждение статус; данные/индекс/receipt не повреждаются, search query может успешно находить материал. Counterexample воспроизведён local/native; visual location отдельно не проверена.

PR-001, origin review, status committed: хранить причину search error и снимать именно её на BUILT/подтверждённом cache_ready; targeted assertion ERROR→BUILT→same-token observer, без стирания чужих уведомлений. Autonomy HIGH: объективная обратимая коррекция status, scope не меняется. RECOMMENDED_WITH PR-003. Operation cost — нет новых пользовательских действий; realization — локальная правка presenter state и focused local/native proof, часы unknown; lifecycle — небольшое явное управление состоянием. После принятия композиции код исправлен; targeted ERROR→BUILT/same-token/ready observation assertions и actual external-process regression прошли local/native. См. AGREED_CORRECTIONS_RECEIPT.json. Прежняя FUBER/F-P-004 про восстановление соединения остаётся resolved: это другой trigger, не перенумерация и не откат прежнего исправления.

### F-O-001 — раньше проверить наиболее рискованные seams

Type Improvement Opportunity; target порядок реализации OBJ1/5/7/9, CURRENT plan, NORMAL; disposition accepted: early G1/G2 порядок записан в официальной карточке. Текущий план может дать требуемый результат, но позволяет построить формы до actual8-root LOCK/private retained-original64MiB/time-budget доказательства. Native sharing/guard ограничения уже выявлялись только на реальном Windows; они способны поменять composition и обесценить готовый UI.

PR-005, origin review, status committed: первым validation slice доказать G1/shared LOCK и G2/retained export/capture на current profiles/normal64MiB, после этого делать весь обязательный editor outcome. OBJ1–11 и G3/manual GUI не уменьшаются и не заменяются «MVP». Autonomy HIGH: порядок обратим, full scope тот же. RECOMMENDED_WITH PR-003 и PR-002. Operation cost — конечный пользовательский путь тот же. Realization — небольшой ранний prototype/probe, дополнительные часы unknown; может раньше обнаружить необходимость изменить root/locking/capture path. Lifecycle/option value — меньше переделки UI, probe не должен стать отдельной framework. Нет hard deadline, поэтому feasibility/slack не рассчитываются; нормальный64MiB в предложенном60s профиле ещё не доказан для object edit.

## Принятый план следующего шага

Официальная R1_OBJECT_AUTHORING.json1.1 подготовлена с committed B outcome и PR-002/003/005 уточнениями. Все OBJ1–OBJ11 остаются обязательными runtime checks; текущее выполнение редакторов не заявляется. Historical card/candidate сохранены в PLANNING/WORK_ITEMS/HISTORY/20261009_object_authoring_refinement и предыдущем Git commit. Candidate entry помечен superseded, current authority — официальная карточка. Historical DESIGN_PROFILE остаётся исходным; committed overlay явно заменяет его старые GUI/synthetic-only границы, сохраняя immutable/CAS/pinned/limit rules. Canonical schema/DDL не меняются.

Top-level realization composition:

| SRU | Contribution / input → output | Dependencies / success |
|---|---|---|
| SRU-OBJ-01 | Проверенные current roots/profiles/LOCK → bounded shared workspace/context | Fresh-source proof и G1; old1/new2 creation сохраняются |
| SRU-OBJ-02 | Pinned base/refs и явные поля/original → frozen recoverable full revision | После01; G2/private capture, точные bytes и immutable IDs |
| SRU-OBJ-03 | Подготовка → publication/CAS/actual receipt/recovery | После02; conflict/UNKNOWN/retry не меняют base/IDs |
| SRU-OBJ-04 | Готовые операции → usable structured forms/edit/history в выбранном app context | После02/03; сохраняются first-bank capabilities, pins и worker |
| SRU-OBJ-05 | Same-source native и пользовательский маршрут → scoped acceptance/adoption record | После01–04; выбран A/B, manual gates подтверждены; full release не заявляется |

SRU-OBJ-01/G1 и частичная02/G2 — ранняя validation, не новый вложенный Scenario. Все существенные переходы Desired Scenario покрыты; дальнейшая рекурсивная реализация здесь не проектируется.

Accepted Composition: PR-001+PR-002+PR-003+PR-005+PR-004B, COMMITTED по USER_OBJECT_AUTHORING_DELIVERY_B_2026-10-09.json. PG-001 closed с выбранным B; PR-004A rejected, исходная альтернатива/история сохраняются. Unsatisfied REQUIRES в составе нет. Runtime PR-001 исправлен и verified; PR-002/003/005 применены в плане; фактическая реализация/adoption редакторов PR-004B и full release ещё не завершены. Официальный current pointer первого Bank не перемещён без FUB10 evidence.

## Ограничения и помощь пользователя

- EG-1: реальный интерфейс/удобство/расположение статусов, все пользовательские переходы и dual-window visual journey не проверены. Headless poll не заменяет GUI. UA-001: открыть готовый launcher и пройти существующий FUB10 маршрут, сообщить итог/конкретную проблему; partially blocking только visual/adoption acceptance и official переход указателя. Независимое уточнение следующего плана уже выполнено.
- EG-2: object-authoring runtime отсутствует. Существующие contract probes не доказывают G1/G2/G3 будущего composer. Нельзя обещать8-root migration/64MiB performance заранее. Частично блокирует actual object acceptance, не review результата.
- EG-3: прежние четыре WinError1314 reader fixtures остаются capability BLOCKED; их не обходили и не объявляли закрытыми. Full accepted-system suite, hardware/power-loss/full restore/lifecycle/research не перепроверялись: они не следуют из нового17-check отчёта.
- EG-4: сроки/ресурсы/бюджет следующей разработки unknown. Proposed finite elapsed profile — лимит одной операции, не срок поставки всего Scenario. Данных для critical path/slack нет.

UA-002 resolved: пользователь выбрал B и остальные recommended Proposals. Снова спрашивать A/B или разрешение на тот же согласованный scope не требуется. Actual implementation/config/native и user visual gates сохраняются как проверки результата.

## Review Log и сохранённое состояние

Canonical records находятся в REVIEW_LOG.json. Current dispositions: F-P-001/002 resolved; F-U-001 resolved; F-R-001 mitigated с actual-runtime revisit trigger (OBJ compatibility failure); F-O-001 accepted. Все included PR committed; PR-004A rejected. Исторические act-now/proposed статусы сохранены в history/REVIEW_LOG_BEFORE_COMMIT.json и history/REVIEW_BEFORE_COMMIT.md, не удалены.

Официальный current work item остаётся first Bank/FUB10 до пользовательского visual evidence. После него применяется сохранённая официальная R1_OBJECT_AUTHORING.json1.1. Common editor implementation/early G1/G2 можно выполнять независимо; B scope уже разрешён, actual adoption закрывается после native/config preservation и human visual proof. Решение записано, повторного scope-approval вопроса нет.
