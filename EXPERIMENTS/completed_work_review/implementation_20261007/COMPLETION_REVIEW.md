# Исправления AWR — AWR-FIX-20261007-01

Четыре дефекта исправлены и проверены на ПК в экспериментальной цепочке intake → SQLite → чтение → поиск → commands → producer → UI. Полная R0/R1/production приёмка остаётся открытой.

| Проблема | Изменение | Подтверждение |
|---|---|---|
| P-1: ValueError для длинного JSON-числа | Контролируемый INVALID_JSON; сохранены duplicate/nonfinite/depth/Unicode codes; доверенная конфигурация отделена | Parser + actual READY/manifest/document + configuration cases PASS |
| P-2: файл мог иметь широкие права при приватной папке | Индивидуальные ACL/owner/link checks; SQLite-compatible identity lease; sidecars проверяются до recovery | Actual unsafe intake/DB/cache/journal/hardlink cases, обычная запись и hot-journal recovery PASS |
| P-3: повторное чтение истории без общего бюджета | Компактные verified summaries один раз на commit/request; отдельный configurable profile, streaming/cancel и достоверные исходы | 192→3 full checks; старое чтение 201450240→3147627 байт; corruption/rollback/exact retry/UNKNOWN PASS |
| P-5: CMD decoding ломал test42 | Bytes capture и bounded replacement diagnostic | Настоящий native test42 дошёл до junction guard и PASS; non-UTF8 fixture PASS |

247 локальных проверок прошли; пять Windows-only случаев пропущены локально. На ПК прошли290 из294: все19 новых adversarial tests, все10 mapped UI workflows,11 owned captures. Исходники local/native совпадают. Файл64MiB прошёл save/replay/original; пакет268310420 байт прошёл save/replay. Это текущий проверенный профиль, не постоянный пользовательский максимум и не обещание любой задержки.

**Неопределённость U-1.** Четыре исходных reader symlink fixtures получили Win1314 до guard assertions. Они остаются BLOCKED; исторический PASS и другие guard tests их не заменяют. Scoped fixes приняты отдельно; full native-reader/MVP/release критерии не сокращены.

**User Assistance UA-1.** Для закрытия полного native gate в будущем нужен разрешённый Windows контекст, способный создать эти fixtures. Это касается только четырёх original assertions; настройки OS/DeveloperMode/права автоматически не менялись.

**Deferred D-1.** Большие размеры, durable jobs/resume и полный UX: вернуться после первого рабочего slice/реальных объёмов или отклонения необходимой операции. Сейчас выбран отдельный configurable work profile; без возврата большие операции могут требовать retry/смены профиля. **D-2.** Real deployment/privacy/backup/restore/hardware и human keyboard/a11y проверяются на соответствующих release gates; synthetic evidence их не доказывает. Сценарий алгоритмы+теория+эволюция остаётся в плане SCE/GSU15 и требует будущих research/history/Watch runtime milestones.

**Questions / Proposals.** Q-1 выбран после пяти actual Windows lifecycle probes, Q-2 после local/native64MiB/~256MiB boundary measurements. Высокая уместность самостоятельного решения для обоих; нужда пользователя/scope/card scale не меняются, ответ пользователя не блокирует. Current work defaults:512MiB retained reads,64MiB metadata,4MiB compact summaries,128 distinct commits,30s cooperative checkpoints. Старые canonical intake policy bytes не менялись; hard wall-time guarantee не заявлен.

Canonical Review Log: REVIEW_LOG.json. Original component reports/receipts сохранены, свежие результаты находятся в REGRESSION_LOCAL.json и native/REGRESSION_NATIVE.json. Код перенесён с guards/backups/readback; финальный receipt находится в PLANNING/WORK_ITEMS/R1_COMPLETED_WORK_REVIEW_FIXES_RECEIPT.json. Следующий шаг — независимое ревью подготовленной R1_DRAFT_AUTHORING.json с учётом нового fixes receipt; authoring ещё не реализован.
