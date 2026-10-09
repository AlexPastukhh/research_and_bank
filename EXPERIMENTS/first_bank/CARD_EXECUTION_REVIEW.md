# Независимая перепроверка карточки первого Bank

Review ID: FUBER-20261009-01. Target: R1_FIRST_USABLE_BANK.json 1.0, текущий код после R1_DRAFT_AUTHORING. Проверка реконструирована из пользовательского запроса о первом Bank, исходных контрактов и реального поведения компонентов; предыдущий design review использован для сравнения после реконструкции.

## Краткий результат / Для пользователя

Карточка независимо перепроверена и реализована без изменения пользовательской цели. В native execution подтвердились и исправлены Problems запуска/настройки, затем уточнены READY fixture и статус восстановленного соединения. Локальный затронутый прогон180 PASS; Windows coverage union180 PASS из исходных177 PASS, исправленных3 PASS и notice followup1 PASS. Это несколько сохранённых прогонов, не один выдуманный чистый rerun. Реальный Bank создан/переоткрыт, verified SQLite snapshot получен; пользовательский GUI ещё не принят.

HIGH: F-P-001 → PR-002 (проектный Python вместо системного без зависимости), F-P-002 → PR-003 (разрешённый write-sharing lease только для setup); оба resolved, Decision Autonomy HIGH. Они блокировали первый запуск, данные не повреждались. CRITICAL нет. Пользовательский выбор по техническим исправлениям не требуется; UA-1 partially blocks только actual visual/adoption acceptance по явно заданному workflow.

Карта отчёта: «Что независимо восстановлено» — Need/FR и reused seams; записи F-O/F-P рядом с PR — механизм, проверка и качественный cost delta каждого изменения; «Ограничения и дальнейшая проверка» — пользовательский GUI и прежние capability blockers; «Candidate Composition и Review Log» — состав коррекций и незавершённая граница приёмки. Следующий шаг пользователя: открыть готовый launch_bank.cmd и проверить конкретный file/URL/note путь из карточки; читать весь отчёт для этого не нужно.

## Что независимо восстановлено

N-1 (explicit): первый доступный на включённом ПК Bank для файла/URL/заметки, поиска/оригинала/повторного открытия. FR-1: точные данные и честное принятие/неопределённость. FR-2: старые frozen IDs/docs/draft/replay не изменяются. FR-3: сохранность и непротиворечивые ограниченные результаты; без скрытого reset неизвестной БД. FR-4: snapshot-first и Tunnel, отсутствие GUI автоматизации основного desktop. Пользовательская инструкция разрешает реализацию текущего bounded этапа; полный R1/редакторы/исследование не включаются.

По коду: .txt authoring всегда выдаёт octet-stream; search поддерживает content только text/plain до 4 МиБ. UI вручную refresh/rebuild, не наблюдает внешний commit. Controller возвращает diagnostic только в памяти; _receipt — чистая функция, attempt_receipts уже append-only в текущем DDL. Setup отсутствует, backend требует существующие отдельные roots. Read receipt подтверждает canonical принятие и проверяет retained bytes; новый диагностический слой должен оставаться независимым. Эти четыре стыка проверяются действием, а не числом features.

## F-O-001 — единая карта проверок и вход в приложение

Type: Improvement Opportunity. Target: work card / documentation, CURRENT. Priority NORMAL; disposition resolved: entry/map applied and verified. Существующая приемлемая карточка содержит FUB1–FUB10; outline DESIGN_PROFILE переиспользует FUB1–FUB6 с другими значениями. Это исторический outline, не отдельные обязательные проверки, но легко ошибиться при закрытии. Новый entry README и карта точных acceptance IDs сокращают поиск команды запуска.

PR-001, origin review, selected candidate: сохранять исходный design review неизменным, отчёт реализации привязать к десяти canonical acceptance IDs; добавить README entry и one-command launcher. Не меняет outcome или обязательный scope. Плюс: однозначное продолжение и запуск. Минус: небольшой дополнительный документ. Decision Autonomy HIGH; пользовательский выбор не нужен, правка обратима. Relations: RECOMMENDED_WITH существующие выбранные технические Q-1..Q-4; не отменяет их. Cost/Timing Delta: число действий запуска становится одной командой после одноразовой явной настройки; доставка — локальная документационная правка, точные часы/срок unknown. Lifecycle: одна canonical карточка вместо двух конкурирующих карт.

## F-P-001 — первый запуск выбирал системный Python без зависимости

Type Problem. Semantic target: SRU setup/launcher implementation, CURRENT. Priority HIGH; disposition resolved (native execution and actual setup evidence в receipt). Need N-1 → fresh Windows process через `python` → импорт runtime/authoring → ModuleNotFoundError jsonschema, exit1 → ожидается проверенное проектное окружение и понятный отказ до создания config. Default WindowsApps Python выбирал системный Python3.14.7, тогда как зависимости предыдущих native прогонов находятся в `.venv`. Bank/config ещё не создавались; дефект блокировал именно новый запуск, не повреждал данные и не переоценивает прошлое scoped acceptance.

PR-002, origin review, selected candidate: закрепить существующий проектный `.venv\Scripts\python.exe` в launcher/docs, проверить его jsonschema/Tk/SQLite и дать typed dependency refusal до записи. Плюс: повторяемый рабочий запуск; ограничение: окружение должно быть доступно, глобальный Python не становится автоматически подходящим. Decision Autonomy HIGH: причина объективно установлена, выбор обратим и не меняет user scope. RECOMMENDED_WITH PR-001. Cost/Timing Delta относительно неработавшего default: исчезает ручной поиск интерпретатора при каждом запуске; дополнительная доставка — малый launcher/doc patch и native повтор, без установки software; точный календарный delta unknown. Следующий шаг: native headless regression + actual setup/check.

## F-P-002 — публикацию config блокировал собственный Windows handle

Type Problem. Semantic target: SRU setup implementation, CURRENT. Priority HIGH; disposition resolved: native scoped checks pass. При новых семи roots и успешно проверенной БД `setup` держал base через read-only Directory, создавал/проверял pending config, затем MoveFileEx возвращал WinError32. Ожидалось атомарно опубликовать config после проверки. Механизм: Windows directory handle без write sharing блокирует публикацию дочернего имени. Данные и pending сохранены, ready config не опубликован, неизвестная БД не сброшена; first-use launch блокировался.

PR-003, origin review, selected candidate: использовать существующий `Directory(base,root=True,write=True)` только внутри явной setup mutation. Он предварительно проверяет NTFS/path/private ACL и держит identity без delete sharing; это не изменение ACL/привилегий. Плюс: корректная атомарная публикация и safe retry. Минус: требуется native проверка sharing semantics; portable PASS этого не доказывает. Decision Autonomy HIGH, объективная техническая коррекция. RECOMMENDED_WITH PR-002. Cost/Timing Delta: пользовательский запуск перестаёт блокироваться, добавляется только необходимая запись config; delivery — одна локальная строка плюс native setup/counterexample recheck, точная календарная delta unknown; сохраняются reversible config и partial paths.

## F-P-003 — тест отсутствия READY не задавал существующий пакет

Type Problem. Semantic target: verification fixture, CURRENT. Priority NORMAL; disposition resolved: native scoped checks pass. Исходный тест ожидал INCOMPLETE для отсутствующей transaction directory. Portable fixture возвращает INCOMPLETE, native secure reader честно возвращает IO_ERROR_2 при отсутствии каталога; отдельный случай INCOMPLETE требует существующего owned каталога без READY. Runtime outcome корректен, предположение теста неверно. PR-004, origin review, selected candidate: создать минимальный owned intake/tx и сохранить строгую проверку INCOMPLETE + durable точного status/code + отсутствия accepted receipt. Autonomy HIGH; требования/accepted reader не меняются, цена — одно подготовительное действие только в тесте. RECOMMENDED_WITH PR-003; нет blocking пользовательского вопроса.

## F-P-004 — уведомление disconnect оставалось после успешного восстановления

Type Problem. Semantic target: SRU external visibility / presenter state, CURRENT. Priority NORMAL; disposition resolved: local counterexample and native focused recheck. При token0 → BANK_BUSY → OK с тем же token0 прежний Flow сохранял текст «Bank недоступен», хотя проверка уже подтвердила соединение. Контрпример независимо воспроизведён на сохранённом исходнике: evidence/LOCAL_NOTICE_COUNTEREXAMPLE.json. Пины/данные не терялись; неверен видимый статус.

PR-005, origin review, selected candidate: отдельно помнить состояние disconnect и сбрасывать его при успешном observer того же контекста; добавить same-token recovery assertion к существующему тесту busy/generation/decrease/close. Autonomy HIGH: объективная обратимая коррекция отображения, без изменения scope/данных/worker/dependencies. Cost delta: никаких новых действий пользователя или IO; один флаг состояния, точный time delta unknown. RECOMMENDED_WITH существующий Q-2. Native focused recheck и final source/config audit PASS; GUI acceptance остаётся отдельной.

## Ограничения и дальнейшая проверка

EG-1: Linux не подтверждает Windows NTFS/ACL/handle guards, native процессы или пользовательский GUI. Native headless gates выполнены после защищённого применения. EG-2: неизвестный hardware/power-loss/restore lifecycle не закрывается snapshot backup. EG-3: пользовательская визуальная приёмка UA-1 blocks adoption acceptance only; после проверки кода и реальной конфигурации пользователь открывает готовое окно и проверяет сохранение, поиск, оригинал, reopen, внешнее обновление/status. Новых blocking value choices нет.

## Candidate Composition и Review Log

Включено PR-001, PR-002, PR-003, PR-004, PR-005 и исходные совместимые технические Q-1..Q-4; новых альтернатив, конфликтов, unsatisfied requires или Proposal Groups не установлено. Статус продуктовой композиции TRANSACTION OPEN до соответствующей приёмки; выполнение технической работы не принимает весь Desired Scenario / R1. Review log: target/version как выше; F-O-001 NORMAL/resolved/PR-001 selected candidate, autonomy HIGH; F-P-001 HIGH/resolved-after-native-recheck/PR-002 selected candidate, autonomy HIGH; F-P-002 HIGH/resolved/PR-003 selected candidate, autonomy HIGH; F-P-003 NORMAL/resolved/PR-004 selected candidate, autonomy HIGH; F-P-004 NORMAL/resolved/PR-005 selected candidate, autonomy HIGH; EG-1..3 preserved; UA-1 partially blocking только визуальная adoption acceptance. История исходного review сохраняется.


Evidence и точная карта FUB1–FUB10: ../../PLANNING/WORK_ITEMS/R1_FIRST_USABLE_BANK_RECEIPT.json. Все PR-001..005 остаются selected candidate / applied technical corrections; продуктовая TRANSACTION OPEN и Desired Scenarios candidate не повышены до commit. Файл записан в рабочую копию и синхронизируется с HOST с guards; факт publication фиксируется отдельно.
