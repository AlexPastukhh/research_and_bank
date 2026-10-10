# Заметка не сохранялась: причина и обычный путь сохранения

> Обновление NS-20261010-02: повторный пользовательский отказ reopen NS-F-P-001. [Дополнение про SQLite и текущий статус](SQLITE_OWNER_FOLLOWUP_20261010.md). Результаты ниже сохранены как история первой коррекции; полного реального GUI success они не доказывают.

Record: NS-20261010-01. Base Git: ed562049ee6557257d3756bee3f96d0edd53c389. Status: implemented and HOST verified; manual visual acceptance pending.

## Краткий результат / Для пользователя

Отказ подтверждён: пустой INTENT.pending в authoring и пустой search-cache.sqlite3 имеют владельца Administrators; guard требует текущего пользователя Windows. Название и выбор автора user не являются причиной показанного отказа. Автор заметки и владелец файла Windows — разные поля.

HIGH NS-F-P-001 → NS-PR-001/002 выполнены: новые приватные файлы получают явного владельца, два конкретных пустых остатка сохранены вне активных рабочих папок, поиск восстановлен. HIGH NS-F-P-002 → NS-PR-003 выполнен: обычная форма имеет одну кнопку «Сохранить», технические этапы выполняются внутри и доступны отдельно в дополнительных инструментах. Decision Autonomy HIGH для этих исправлений: сохранена модель данных и проверки, существующие данные и права не переписываются.

В разделах «Почему не сохранилось» — конкретный механизм; «Как теперь сохранять» — пользовательский путь; «Findings и принятые исправления» — границы решений; «Что проверено» — сохранение/повтор/CAS/ACL и реальный поиск; «Ограничения и следующий шаг» — оставшаяся ручная проверка. Следующее действие: скопировать текст из ещё открытой формы, перезапустить launcher и проверить обычное сохранение. Файл не нужно читать целиком для этого действия.

## Задача и критерии успеха

N-NS-001 established: пользователь сохраняет заметку и затем может открыть её в банке. N-NS-002 established: обычный интерфейс объясняет пользовательские действия понятными словами.

FR-NS-001: не показывать сохранение как успешное до canonical ACCEPTED/REPLAY. FR-NS-002: сохранять точные данные, существующий Bank и историю; при конфликте не перезаписывать чужую правку. FR-NS-003: не отключать проверку владельца/ACL и не изменять права существующих файлов для обхода ошибки. Это применимые ограничения прежнего механизма, а не новая модель версий.

Scope: текущие формы, сохранение заметки/объекта, первичное создание приватных служебных файлов и два подтверждённых пустых остатка. Не full R1/research/restore audit. Никакая настоящая заметка пользователя в рамках проверки не импортировалась.

## Почему не сохранилось

Требование → новая заметка должна попасть в Bank. Preconditions → configured authoring/source private roots, заполненный ввод, один worker. Trigger → author_prepare проверяет fields, выделяет transaction, создаёт INTENT.pending и сразу проверяет security descriptor, до записи JSON. Observed → файл 0 bytes с owner O:BA; guard выдаёт UNTRUSTED_OWNER, результат INCOMPLETE. Expected → запись проверенной копии и подтверждённое сохранение.

Нативный scan обнаружил ровно эти блокирующие файлы среди 12 проверенных путей. Других нарушений owner/ACL в этой выборке не было. Пустой INTENT.pending не содержит текста и не позволяет восстановить заметку с диска. Наличие INCOMPLETE с выделенным transaction в этом пути означает, что отказ не является EMPTY_INPUT из начальной проверки title/body/author.

Старая реализация новых Handle передавала NULL security attributes; Cache.initialize использовал os.open. Windows выбирает security descriptor/owner по умолчанию, поэтому новое содержимое может не соответствовать последующему строгому owner guard. Microsoft описывает [CreateFile](https://learn.microsoft.com/en-us/windows/win32/fileio/file-security-and-access-rights) и [owner нового объекта](https://learn.microsoft.com/en-us/windows/win32/secauthz/owner-of-a-new-object). Повышенный запуск — правдоподобное объяснение Administrators; процесс, создавший эти конкретные остатки, не установлен. Нынешний Tunnel-процесс не elevated; до исправления новый тестовый файл в нём проходил owner check.

## Как теперь сохранять

1. «Новый материал» → выбрать «Заметка», «Файл» или «Ссылка».
2. Для заметки ввести название и текст. Автор — «Человек», «ИИ» или «Не указан»; имя автора необязательно. Формат — «Обычный текст»/Markdown.
3. Нажать «Сохранить». Форма остаётся при ошибке и закрывается после подтверждения банком.
4. Найти материал в списке и нажать «Открыть». Поиск обновляется после сохранения.

«Новая сущность», «Новая коллекция», «Заметка к материалу» и «Редактировать» также используют «Сохранить»/«Сохранить изменения». Неизменённая форма без другого файла по-прежнему даёт «Изменений нет» до worker/preparation.

Подготовка, публикация и canonical save остались внутренними этапами. Их кнопки, журналы, полные IDs, receipt, ручной rebuild и диагностика показываются через «Дополнительные инструменты». Это UI composition, не изменение протоколов хранения. История по-прежнему отдельная команда.

При неудаче после создания проверенной копии повтор с теми же полями продолжает тот же transaction; исходный файл не перечитывается для новой подготовки. Это относится и к запечатанной копии при прерывании подготовки. Если пользователь изменил поля, это новый ввод и отдельная попытка. UNKNOWN не маскируется успехом; STALE_BASE не обходится. Отмена проверяется между этапами; завершённый canonical save не отменяется.

## Findings и принятые исправления

### NS-F-P-001 — реальное сохранение/поиск блокировались owner check

Type Problem; target implementation/execution; CURRENT для исправления, UPSTREAM относительно обычного пользовательского Scenario; impact HIGH; disposition resolved for observed residues/new creation, manual user path still pending. Evidence: HOST_OBSERVATION, снимок пользователя, REAL_WORKSPACE_RECOVERY.

NS-PR-001 (origin review, committed, User Review Priority HIGH, Decision Autonomy HIGH): для CREATE_NEW передавать явный user+SYSTEM private descriptor, owner текущего пользователя. Cache.initialize использует тот же native Handle. Existing-file open и owner/ACL validation не изменены. Trade-off: небольшое изменение общего adapter вместо требований к запуску каждого окна/процесса. Elevated run не воспроизводился, но descriptor реально наблюдался нативным тестом.

NS-PR-002 (origin review, committed, HIGH/HIGH): переместить только два предварительно проверенных пустых остатка в новую recovery-папку. Проверены exact inventory, owner, file identity/links/final path, нулевой размер, отсутствие source для несостоявшейся заметки и неизменность Bank/config. Shared workspace lease удерживался. Metadata/bytes сохранены; ACL/owner существующих файлов не менялись. REQUIRES NS-PR-001; BUNDLE NS-PG-001 HARD_BUNDLE для устойчивого снятия блокировки. Цена — одна явная восстановительная операция; автоматической очистки других файлов нет.

### NS-F-P-002 — обычное сохранение требовало понимания технических этапов

Type Problem; target Desired Scenario/UI composition; UPSTREAM; User Review Priority HIGH; disposition resolved technically. Current trigger: создать заметку → «Подготовить запись» → «Опубликовать» → «Сохранить в Bank», выбирать raw enums. Это не отражало ожидаемое обычное действие пользователя «сохранить заметку».

NS-PR-003 (origin review, committed, HIGH/HIGH): одна обычная Save operation на прежнем единственном worker, прежние stages/guards, честный final status, удержание формы/transaction при ошибке, технические controls скрыты по умолчанию. Новые сущности/версии/core algorithms не вводились. Costs: после ввода один вызов пользователя вместо трёх отдельных команд; число внутренних проверок сохранено. Delivery delta — ограниченная UI orchestration, без часов/сроков оценки; lifecycle — существующий протокол и exact retry переиспользованы. Технические ручные этапы сохранены как recovery option. RECOMMENDED_WITH NS-PR-001/002.

Alternative: оставить три команды и только переименовать их. Не выбран, поскольку нагрузка понимания stages остаётся, а исходный пользовательский outcome тот же. Это не отдельное требование будущей версии.

NS-PG-001 HARD_BUNDLE: NS-PR-001+002; внешняя зависимость — конкретные остатки всё ещё пусты и неизменны перед перемещением. Проверка пройдена. Remediation composition: NS-PR-001+002+003 implemented; больше blocking выбора пользователя нет. Сохранение записи в документации не означает принятия новых Desired Scenarios или полного релиза.

## Что проверено

Snapshot: syntax восьми первоначально изменённых runtime файлов и шесть независимых stage oracles на реальном методе save_material: order/transaction, stop-on-prepare/publish failure, UNKNOWN recovery без fields, cancellation, exception outcome. Остальные изменённые файлы разобраны Python AST в native runs.

Windows 3.14.7: полный focused прогон 12 PASS, 0 skips. Включены точное чтение тела/автора после save, REPLAY с одним SQL commit, structured save/STALE_BASE, обязательный body и необязательный identity, настоящие withdrawn Tk callbacks и human choices, explicit native descriptor и неизменность существующего файла, сохранение transaction после UNKNOWN, создание/проверка cache, прежние no-op/порядок/IDs и broad-ACL/handle-lease counterexamples.

После этого уточнены два form recovery predicates для sealed interruption и название «Заметка к материалу». Повтор одного affected Tk test PASS на конечных hash всех 10 code/test файлов. Он проверяет реальный handle_extension_result для sealed failure и следующий exact continue_save без fields. Это focused повтор после изменения callbacks, не заявление о полном повторе всех 12 на этих последних hashes. Первый ошибочный тестовый прогон сохранён: неправильный o.im импорт в новой фикстуре, 10 PASS/1 ERROR; исправленная фикстура прошла.

Реальное окружение: config/Bank bytes не менялись; два пустых файла preserved с прежними identity/metadata; backend.config и workspace.usage проходят; actual cache rebuild BUILT и read-only observe cache_ready true. Native verification никогда не писала тестовую заметку в пользовательский Bank. Search snapshot sequence 0 отражает настоящий Bank на момент проверки.

## Ограничения и следующий шаг

Evidence Gap NS-EG-001: неизвестно, какой именно процесс создал старые admin-owned файлы. Это не доказательство elevated запуска пользователем. NS-EG-002: не выполнена человеческая визуальная приёмка новой формы/общего окна; withdrawn Tk проверяет callbacks/layout, не удобство в работе. NS-EG-003: фактический elevated launch не повторяли; не заявляем полную приёмку всех контекстов Windows.

UA-NS-001 non-blocking для кода, partially blocking для ручной visual acceptance: если в открытой форме есть текст, скопировать его; закрыть приложение и открыть прежний EXPERIMENTS/first_bank/launch_bank.cmd обычным запуском. Ввести небольшую заметку с title/body, нажать «Сохранить», открыть её в списке, перезапустить и открыть снова. Код уже на диске; работающий старый Python-процесс не подхватывает его автоматически. Отдельного пользовательского решения о новой модели данных не требуется.

Прежние FUB10/OBJ10/OBJ11 manual gates не закрываются этими тестами. Исторический UIF-F-P-003 теперь resolved for the actual search blocker: оба старых reports остаются неизменными, новое recovery evidence дополняет их. Full research/provider/Watch/restore и full R1 не приняты.

## Review Log

Canonical record: REVIEW_LOG.json. NS-F-P-001/002 resolved technically; NS-PR-001/002/003 committed implementation choices; NS-PG-001 satisfied. Evidence gaps NS-EG-001..003 сохранены. UA-NS-001 pending manual confirmation; нет unresolved blocking value forks, выдуманного бюджета или deadline. Git publication записывается отдельным подтверждением после commit/push, чтобы не заявлять её заранее.
