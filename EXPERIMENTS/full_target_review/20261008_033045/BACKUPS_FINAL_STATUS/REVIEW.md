# Проверка выполненной работы и оставшегося целевого плана

Review: **FTR-20261008-01**. Проверен весь текущий `research_and_bank`: планирование, контракты, восемь реализованных runtime компонентов, исправления, creation UI, последняя object карточка и оставшийся R0–R8. Не только последний файл. Исторический процесс восстановлен по доступным источникам и receipts, без додумывания невидимых действий.

**Итог:** общая архитектура и распределение требований согласованы. Свежая локальная регрессия прошла. Найдены две подтверждённые проблемы: устаревшие current статусы ledger и разрыв text-file save→content search перед первым использованием. Полный R1 и первый usable Bank пока не приняты. Итог Windows подтверждён:321PASS/4capability blockers; независимые10doc checks прошли на обеих платформах;8исправленных counterprobes прошли на обеих платформах, Windows exit0.

## Цель и критерии

Первый полезный локальный Bank должен сохранять file/URL/note через приложение, находить поддерживаемое содержимое и возвращать точные оригиналы/версии в работу с ChatGPT. История, pinned refs, CAS, exact retry/receipt и видимые ограничения сохраняются. Размеры и полный UX можно расширять позже через versioned профили и отдельные компоненты. Пользователь выбрал **Bank раньше**, до полного набора object/version editors; это новая последовательность, не ретроактивная ошибка прошлых карточек и не отмена полного R1.

Универсальность означает общие storage/research контракты и расширяемые схемы. Она не означает автоматическую поддержку любой новой structured схемы, PDF/OCR или достоверную проверку развития любой технологии. Алгоритмы/теория сохраняются как материалы/заметки/связи; проверка альтернатив и обновлений требует соответствующих исследовательских этапов и доказательств.

## 1. Реальные проблемы

**P-1 — устаревшие current поля Findings.** RVP-001 всё ещё ставит под вопрос backend/transport, RVP-002 — MVP checkpoint, FPR-U04 — объявленные поля/контроли поиска. Решения SQLite/local app и R2full/R3stable уже зафиксированы, scoped search реализован. Следующий исполнитель может повторить решённые вопросы или неверно выбрать работу. Подготовлен patch с сохранением истории; фактическое применение на ПК подтверждается отдельным DOCUMENTATION_APPLY_RECEIPT.json. Original классификации и открытая полная runtime приёмка сохраняются.

**P-2 — обычный UTF8 file сохраняется как `application/octet-stream`.** В owned сценарии `algorithm.txt` с уникальным термином `quicksorttargetomega` сохраняется полностью и находится по имени, но content search даёт0hits/unsupported_media1. Те же bytes через объявленный `text/plain` дают точный pinned hit. Причина — media boundary file-authoring, не индекс и не потеря данных. Это мешает первому save→find использованию алгоритмов/теории. Нужен bounded поддерживаемый text save путь и явный unsupported UX. Ранее binary creation-only scope принят корректно; общий OCR scope сюда не добавляется.

## 2. Неопределённости и обязательные остатки

**U-1.** Четыре оригинальных Windows symlink fixtures раньше остановились Win1314 до проверяемых утверждений. Это BLOCKED, не PASS и не доказанный reader bug. Нужен ограниченный запуск с доступной capability перед полной native security приёмкой.

**U-2 — разрешено.** Уже созданный Windows отчёт прочитан, без повторного запуска:325cases,321PASS,4BLOCKED_FIXTURE_WIN1314,0skip; исходники не изменены. PID7784 завершился exit0 за712.05s. Ошибка409 была реальной, но последующие вызовы выбранного туннеля сработали; внутреннюю причину/смену версии из этого не выводим. Runner exit0 не превращает четыре blocked кейса в PASS.

**U-3 — first-use ещё не принят.** Внешний app save принят и виден fresh query, но открытый UI ждёт list/refresh. Диагностика INCOMPLETE без READY видна сразу, но не сохраняется как attempt receipt после reopen. Реальный Bank setup/roots/access и сквозное первое использование ещё не приняты. Это ранее известные R1 обязанности, а не ложные completed утверждения scoped UI. После нового Bank-earlier решения они относятся к ближайшей работе и не откладываются до advanced UX.

**U-4.** Generic metadata допускает новые reviewed types, но закрытые R1 schemas и отсутствие R2 research runtime не доказывают полной domain/migration совместимости. Новые structured fields требуют schema/profile/read/search/UI проверок.

**U-5 — разрешено.** Результат исправленного native8case запуска прочитан:8PASS/0errors/exit0, исходники приложения не менялись. Перезапускать suite ради тайм-аутов не потребовалось.

## 3. Что выдержало проверку

- 115 IDs, формулировок и классификаций требований согласованы; все11MVP приходятся не позже R2. Зависимости и порядок9стадий ацикличны. Сохранены159backlog items и45proposals без общего автоматического принятия.
- Native preflight:353защищённых файлов и264accepted baseline без изменений;195authoritative current mirror файлов совпали по hash.917inventory entries — metadata, не доказательство проверки917реализаций.
- Свежая регрессия: **локально271PASS/5Windows-only skips, Windows321PASS/4Win1314 capability blockers**. Исходники не менялись; runner exit0 подтверждён. Нормальные64MiB/near256MiB fixtures проверены на обоих ОС, это не общая ёмкость/latency гарантия.
- **10 независимых document checks и8исправленных counterprobes PASS на обеих платформах.** Сохранены и начальные ошибки нашего проверяющего кода. Первый Windows запуск8probes имел0assertion failures/3teardown errors нашего SQLite helper. Явное close исправлено в V2; локально и native8PASS, native execution exit0, original cleanup failure history сохранена. Приложение не менялось.
- Проверены точные оригиналы, pinned content queries, все128018bytes note body, явное display-only ограничение предпросмотра, canonical receipt/replay после повреждения journal, frozen refs/profile и раздельный URL/AI provenance. P-2 и U-3 также подтверждены на Windows.
- Scoped completed карточки не объявляют полный release;11object editor runtime checks остаются pending. Исследование/Watch ещё не реализованы.

## 4. User Assistance / Process Improvement

**UA-1 → U-1:** перед полной native security приёмкой обеспечить один ограниченный запуск исходных четырёх fixture tests в Windows-контексте с разрешённым symlink creation. Не менять глобальные права автоматически. Остальное review этим не блокируется.

**UA-2 → U-5 — разрешено:** нужные main/V2 reports и exit proofs получены. Сейчас действие пользователя не нужно. При повторных409/тайм-аутах помогает переподключение той же app; внутреннюю причину/смену версии туннеля из симптомов не выводим.

## 5. Deferred / Follow-up Items

| ID | Сохранить | Триггер возврата | Почему позже / последствие пропуска |
|---|---|---|---|
| D-1 | Большие size/work profiles, staging quota и maintenance | Реальный материал сверх профиля/регулярный work отказ/рост диска | Сейчас быстрый first Bank; повышение одной цифры без всей цепочки может ломать UX. Accepted intents занимают quota, GC нет. |
| D-2 | Все object/version editors и11gates | Первый usable Bank принят или нужен edit journey | Пользователь выбрал порядок; полный R1 без этого не завершён. |
| D-3 | Алгоритмы/теория, альтернативы/исправления/новые технологии | R2/R4/R5/R7/R8 capabilities | Storage уже имеет путь; иначе future research/Watch заявления останутся недоказанными. |
| D-4 | Full release/migrations/backup/restore/human UX/COND | Формальная приёмка, новые types, stable R3, nonpublic scope | Scoped test UI не доказывает production; минимум setup/access/recovery первого Bank требуется сейчас по U-3. |

## 6. Вопросы и Proposals

**Q-1:** first Bank или full R1 сразу? Решение существенно меняет ближайший объём — требовалось решение пользователя. **Отвечено: Bank раньше.** Не блокирует.

**Q-2:** как закрыть P-2/U-3? Proposal — отдельная reviewed bounded first-use карта: text/plain, read-only automatic Bank change visibility, durable diagnostic attempts/reopen и usable setup, затем implementation. **Высокая уместность самостоятельного решения**, без нового продуктового вопроса; first-use acceptance ждёт проверки критериев.

**Q-3:** Windows symlink capability? Proposal — подходящий уже доступный контекст для original4tests; глобальную OS-конфигурацию обсуждать только при реальной необходимости. **Желательно согласование**, не блокирует review.

## Оставшийся путь

Сначала independently review first usable Bank карту, затем реализовать минимальные стыки локально и проверить Windows/default guards/UI, подтвердить документацию и first-use setup. После первого использования — сохранённая object authoring карта и остальные fullR1 gates. Затем R2fullMVP→R3stable→R4source/quality/counter-search→R5time→R6identity/hybridsearch→R7multimodal/packs→R8Watch. Unattended execution остаётся отдельным COND-001, не обещано самим manual Watch.

Полный canonical Review Log: `REVIEW_LOG.json`; goal evidence: `GOAL_COVERAGE.json`; concrete remainder: `REMAINDER_FIRST_BANK.json`; методические ошибки собственных checkers и их исправления: `QA_HISTORY.json`. Предыдущие ревью и исходные failed QA snapshots сохранены. Успешная запись здесь подтверждается отдельным `POST_SAVE_VERIFICATION.json`. Native sync считается подтверждённым только при наличии successful DOCUMENTATION_APPLY_RECEIPT.json; review не меняет компонентный код, real Bank, accepted baseline, provider/privilege/Watch настройки.
