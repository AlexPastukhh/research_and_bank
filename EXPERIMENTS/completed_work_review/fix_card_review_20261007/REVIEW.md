# Ревью карточки исправлений — FCR-20261007-01

Объект: `PLANNING/WORK_ITEMS/R1_COMPLETED_WORK_REVIEW_FIXES.json` целиком и её зависимости. Цель — ограниченный шаг исправления AWR-P01/P02/P03/P05 перед authoring, с приоритетом первого рабочего варианта. Код приложения в этом шаге не исправлялся.

## Реальные проблемы карточки

**P-1. Не разделены недопустимый JSON пакета и ошибка доверенной конфигурации.** Policy создаётся до try read_package; общий ValueError может также перехватить Rejected. Если назвать все такие исходы package REJECTED или потерять duplicate/nonfinite codes, результат нарушит контракт. Пример: 5000 цифр → ValueError; duplicate → Rejected(DUPLICATE_JSON_KEY). Влияние: Локальный пробел спецификации при обработке ошибок. FIX2 уточнён: INVALID_JSON, отдельная config boundary, Rejected сохраняется. Статус: `resolved_in_card`.

**P-2. Жизненный цикл SQLite guard недостаточно задан.** SQLite может читать journal при connect; проверка после connect запаздывает. Удержание обычного reader handle с запретом записи/удаления может блокировать writer или удаление journal при commit. Пример: Безопасный DB + небезопасный существующий journal; либо нормальный commit под неподходящим lease. Влияние: Основной save/recovery результат при неверном выборе guard. FIX3 задаёт before-connect checks и обязательный реальный native lifecycle prototype; конкретный share mode пока не объявлен проверенным. Статус: `resolved_in_card_with_explicit_gate`.

**P-3. Не определены исходы при исчерпании бюджета истории.** _verify_commit нормализует Problem в INTEGRITY_ERROR. Общий REJECTED при exact retry принятой транзакции или после COMMIT скрывает реально сохранённое состояние. Пример: Лимит до COMMIT нового импорта vs лимит проверки уже принятого exact retry vs неопределённость после COMMIT. Влияние: Основной результат/save trust и UX retry. FIX4 задаёт отдельные REJECTED/IO_ERROR/UNKNOWN границы, streaming checks, компактную once-per-request стратегию; числа отдельно gate. Статус: `resolved_in_card_with_explicit_gate`.

**P-4. Неполный scope зависимостей и свежих доказательств.** Card требует actual UI/reads, но отсутствуют их inputs и bounded allowed paths; перепись старых NATIVE_RESULTS создаст неверное впечатление прежней same-source приёмки. Пример: Новый work-limit exception доходит до reads/controller/UI и требует совместимой трансляции. Влияние: Локальная полнота карточки и достоверность интеграционной приёмки. Добавлены необходимые read/UI/dependency inputs, ограниченные пути и отдельная директория свежих evidence; старые отчёты неизменяемы. Статус: `resolved_in_card`.

## Неопределённости

U-1: конкретный Win32 lifecycle/share strategy и численные work-policy defaults ещё не подтверждены. Они стали явными technical gates перед FIX3/FIX4, а не скрытыми исходными требованиями. U-2: четыре исходных symlink случая остаются BLOCKED по AWR-U01. Это не признанные новые дефекты guards и не PASS.

## Что выдержало проверку

Все 256 фактических native hashes совпадают с актуальной локальной копией. Три устаревших значения вспомогательного metadata исправлены; внешнего drift нет. Принятые 264 файла неизменны, текущий указатель один, AGENTS не обнаружены.

Независимо повторены шесть parser probes и сценарий 64×3 refs. Текущий код всё ещё пропускает ValueError для 5000 цифр; остальные duplicate/nonfinite/depth/Unicode codes подтвердились. Reference scenario сохранился с 192 проверками commits и 201450240 байт исторического чтения при 62966 байтах нового payload. Эти цифры не доказывают универсальный порог задержки.

## User Assistance / Process Improvement

Новых действий пользователя для текущего шага не требуется. Для полного будущего свежего symlink acceptance сохраняется AWR-UA01: нужен разрешённый Windows контекст, способный создать fixtures. Это блокирует четыре конкретных проверки; остальные fixes доступны. Глобальные права/DeveloperMode автоматически не меняются.

## Deferred / Follow-up Items

D-1: большие размеры, durable jobs/resume и полный UX — после первого slice и измерений реальных объёмов; без возврата большие операции ограничены рабочим профилем. D-2: GSU15 алгоритмы+теория+эволюция требует runtime research/evidence/history/Watch проверок на соответствующих milestones; static coverage не заменяет мониторинг.

## Вопросы и Proposals

Q-1: выбрать SQLite-совместимый file guard после owned Windows prototype: нормальная запись, удаление journal, настоящее recovery после завершения owned writer, unsafe existing sidecars и identity race. Q-2: измерить нормальный текущий профиль и зафиксировать отдельные versioned aggregate-work defaults перед FIX4. Для обоих высокая уместность самостоятельного решения: нужду пользователя/scope/card scale не меняют; пользовательский ответ не блокирует. Блокируют принятие только соответствующей технической стратегии.

## Review Log и итог

Canonical Review Log находится рядом в REVIEW_LOG.json, включает проблемы, ограничения, Proposals и триггеры возврата. Исходная карточка сохранена как CARD_BEFORE_REVIEW.json. FIX1 card review завершён; FIX2–FIX7 pending, runtime AWR-P01/P02/P03/P05 остаются open. Следующий шаг — local heavy implementation, затем guarded native transfer и same-source affected UI/runtime evidence. Full R0/R1/production не приняты.
