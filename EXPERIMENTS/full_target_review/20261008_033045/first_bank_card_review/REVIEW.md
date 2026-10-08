# Ревью карточки первого Bank — FBCR-20261008-01

Проверен следующий шаг целиком: текущие контракты, известные first-use стыки и ограниченная карточка реализации. Результат — подготовленный дизайн, не готовое приложение.

## Реальные проблемы

P-1. В активном примере передачи задачи оставался Remote Desktop Commander. При копировании новый чат нарушал бы текущий workflow. Пример заменён на выбранный Туннель и snapshot-first; исходный текст сохранён. Исправление подготовлено и входит в guarded native apply; успешность записи подтверждается отдельной квитанцией.

## Неопределённости и ограничения

U-1. UNKNOWN нельзя помещать в каноническую квитанцию. Диагностика получает отдельный versioned private формат в существующей append-only таблице; app read-result schema требует явного расширения. Принятый Bank receipt остаётся единственным доказательством принятия.

U-2. Прежние P-2 и U-3 ещё не исправлены в runtime: обычный текст сейчас binary, внешняя запись не обновляет открытый список автоматически, failed-attempt не сохраняется. Все они включены в обязательную карточку первого Bank.

U-3. Четыре прежних symlink-fixture Windows проверки блокированы Win1314. Другие PASS их не заменяют.

## Что выдержало проверку

Exact originals/replay/pinned IDs, note/URL semantics, положительный text/plain content-search control и frozen v1 reopen подтверждены. Новые headless пробы проверяют также несовместимость UNKNOWN receipt, неизменяемую diagnostics table, закрытый read-result placeholder и компактный commit signal. PASS этих проб не означает реализации новых возможностей.

Первый вариант сохраняет file/URL/note, ищет поддерживаемый UTF8 текст, выдаёт точные оригиналы, честно показывает состояния и восстанавливает их после открытия. Используются семь имеющихся roots, SQLite, existing publisher/importer/read/search/UI worker. Существующие v1 intents не переоформляются под новые defaults. UTF8 mode и producer/profile фиксируются на подготовке, byte originals не изменяются. Индексирование >4MiB не обещано; ограничения видны.

## User Assistance

UA-1 нужен после реализации: открыть приложение и проверить конкретный визуальный save/find/original/reopen/external-update сценарий. Сейчас это не блокирует карточку. GUI автоматически не открывался.

## Deferred

D-1: большие профили и staging maintenance — вернуться при превышении действующих лимитов. D-2: indexed diagnostics/migration — при частом достижении bounded scan. D-3: оставшиеся object/version editors и stable restore/lifecycle — после первого Bank. Их отсутствие не позволяет объявить полный R1/R3.

## Proposals

Q-1..Q-4 в DESIGN_PROFILE.json выбирают совместимый текстовый профиль, read-only observer с generation guards, независимую диагностику и простой setup/launch/manual verified backup. Высокая уместность самостоятельного решения: цель, scope пользователя и сложность кардинально не меняются. Новых блокирующих решений пользователя нет.

Следующая карточка: PLANNING/WORK_ITEMS/R1_FIRST_USABLE_BANK.json. FUB1–FUB10 задают точные изменения, meaningful local/native tests и отдельный будущий пользовательский visual gate. Research/counterevidence/time/packs/Watch и полные object editors сохраняются в первоначальных этапах.

Review Log: REVIEW_LOG.json. Native apply/readback receipts должны быть подтверждены отдельно; сохранение дизайна не закрывает runtime дефекты.

Подтверждённые проверки: local10PASS и native10PASS,0fail/errors/skips, источники неизменны; PID19324 exit0. Повторная проверка225guarded files/264baseline не выявила drift. Квитанция фактической записи: PLANNING/WORK_ITEMS/R1_FIRST_USABLE_BANK_CARD_REVIEW_RECEIPT.json.
