# Исправления полного ревью — 2026-10-06

R0-PLAN-REVIEW-FIXES-001 по запросу пользователя.

- P-1: workflow теперь читает единственный CURRENT_WORK_ITEM из SESSION_STATE; Source/Entity — завершённый исторический пример. Новая незавершённая карточка R0_GATE_READINESS.json указывает точные ограничения pending answers.
- P-2: ранние/поздние deadlines OPEN-005 R1/R4, OPEN-006 R5 (bitemporal по активному COND-007 раньше при необходимости), OPEN-009 R0/R7 и OPEN-010 R0/R6 структурированы. Генератор roadmap перезапущен. Добавлена earliest-declared-deadline проверка и две отрицательные регрессии исходных ошибок.
- P-3: reassessment registry version/tooling из предыдущего review сохранён; formal compatibility D-3 не объявлен выполненным.

Добавлен R0_GATE_READINESS.md с design state и remaining gates. User вопросы: первые data class, дополнительные AI/provider exposure, доступ когда ПК выключен. Ответы pending; это не выдуманное согласие и не blanket scope change. Влияние на privacy/deployment существенно: требуется решение пользователя; соответствующий use/acceptance blocking, synthetic contract work non-blocking.

R5 clustering input/method quality остаётся отдельной future decision до R5; новый scope не принимается. R1 search/ops/ownership/retention contracts ещё подготовить и принять отдельно.

Проверки и успешность записи: WORK_ITEMS/R0_PLAN_REVIEW_FIXES_RECEIPT.json. Результат — корректировка плана, не production implementation, не R0/R1 release acceptance.
