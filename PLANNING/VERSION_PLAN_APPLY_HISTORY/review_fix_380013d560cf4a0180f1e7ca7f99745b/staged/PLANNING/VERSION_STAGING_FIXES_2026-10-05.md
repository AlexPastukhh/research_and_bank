# Применённые правки version staging — 2026-10-05

Основание: пользователь поручил применить правки из `VERSION_STAGING_REVIEW_2026-10-05_BRANCH.md`.
Область: план распределения требований и его структурная проверка. Это не приёмка приложения или будущих релизов.

| Finding | Применённая правка | Состояние |
| --- | --- | --- |
| VSR-001 | Положительные scopes и отдельные результаты сторон для всех MVP slices, identity R1/R6 и Watch R8; у одноэтапных поставок вместо шаблона используются сохранённые per-side обязанности | Исправлено в плане |
| VSR-002 | Валидатор проверяет точки MVP/stable, версии и покрытие, per-side scopes, зависимости/очередность и decision checkpoints; фиксированные 115/11 удалены из проверки покрытия; ошибки работают и с Python -O | Исправлено в коде |
| VSR-003 | R1 acceptance проверяет interrupted write, сохранность принятых данных после reopen, повтор и конфликт версий, восстановление индекса | Критерии добавлены; runtime ещё предстоит реализовать |
| VSR-004 | Watch R8 содержит policy/cadence/alerts/budget, pause/resume/lifecycle и историю; manual execution отделён от scheduler/background delivery | Исправлено в плане |
| VSR-005 | OPEN-018 получает checkpoints R0/R6/R7; базовый exact/full-text scope определяется в R0 и проверяется в R1 | Исправлено в плане |
| VSR-006 | R2 проверяет соблюдение применимых CORE/ANTI в поставляемом scope; непоставленный TARGET не расширяет MVP | Формулировка исправлена |

Продуктовые номера версий, 115 requirement IDs, классификации, исходные statements и milestone assignment сохранены. Schema overlay повышена с 1.0 до 1.1 из-за добавления optional decision_checkpoints. Это отдельная версия формата плана, а не системы или приложения.

Добавлен `PLANNING/TOOLS/test_release_plan.py`: текущий план/генерация, 19 негативных вариантов и рост inventory без фиксированного лимита 115. Негативные случаи включают неверные milestone/versions checkpoint, duplicate MVP IDs, неизвестные/циклические ссылки, пустые scopes, неправильную сторону ответственности, поздний MVP, snapshot/count drift и неверные decision checkpoints. Mutations применяются только к копиям данных в памяти.

Команды проверки:

```text
python PLANNING/TOOLS/release_plan.py --requirements DRAFT_NOTES/REQUIREMENTS_MAP.json
python PLANNING/TOOLS/test_release_plan.py
python -O PLANNING/TOOLS/test_release_plan.py
```

Все три команды прошли на подготовленной копии. После применения на ПК их результат фиксируется в `VERSION_PLAN_FIX_RECEIPT.json`; статус `verified` означает совпадение файлов и прохождение документных проверок, а не реализацию product capabilities.

Перед применением проверяются нормализованные контрольные суммы исходных документов и SESSION_STATE, а прежние версии изменяемых файлов сохраняются в `VERSION_PLAN_APPLY_HISTORY`. Существующие изменения других веток не перезаписываются при несовпадении исходных сумм. Commit/push не входят в это изменение.

Исходное ревью сохранено как исторический документ; этот файл фиксирует disposition его замечаний. PLAN-SOURCE-ENTITY/CLAIM-ENUM/CLUSTERING/INVENTORY/LOCAL-WRITE/WINDOWS-PARITY остаются подготовительными работами R0. Формат production-данных, внутренняя БД и конкретные механизмы восстановления ещё не выбраны этим изменением.
