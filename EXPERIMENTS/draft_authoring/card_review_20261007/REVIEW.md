# Ревью карточки создания материалов Bank — DAR-20261007-01

Проверена вся R1_DRAFT_AUTHORING.json: создание файла, ссылки и standalone заметки поверх текущих контрактов. Исправлены два пробела спецификации. Реализация новой формы ещё не выполнена; AUTH2–AUTH8 остаются pending.

**Реальные проблемы карточки, исправлены на уровне спецификации**

| ID | При каких условиях возникала проблема | Последствие | Исправление |
|---|---|---|---|
| P-2 | Прерывание до SEAL или до полного READY.pending | Reread изменённого оригинала меняет bytes под теми же IDs; publisher resume не достраивает partial; журнал среди payload отклоняется | Journal отдельно; INTENT→payload/DRAFT.pending→SEAL→DRAFT.json; конкретные INCOMPLETE/resumable состояния, без скрытых repair/new IDs |
| P-3 | После сохранения A пользователь выбирает новое B | Base Model сохраняет прежний ACCEPTED/receipt, новая форма может ошибочно показать его для B | Изоляция tx/context/generation, сброс панелей и verified restore, app-selected tx |

Это выявленные недостатки карточки/условия интеграции, а не утверждение о дефектах ещё не написанного authoring runtime. История обнаружения и исправления добавлена в canonical Findings.

**Что выдержало проверку.** Выполнены10 local probes: отдельные schema-valid Asset(bytes), Asset(locator), Annotation(note) проходят publisher→save→REPLAY с теми же ID/commit/bytes; проверены strict inventory, partial vs complete pending resume, changed-transaction conflict, standalone/author-origin profiles и сохранение контекста base model. Все279 source files на ПК совпали с проверенной копией; свежие AWR native290PASS/4blocked относятся к текущей цепочке, не к будущей форме. Все26 канонических осей рассмотрены в bounded card audit с явными runtime/scope ограничениями.

**Неопределённости.** U-1: новое journal/lock/SelectedOriginal/Tk расширение не реализовано; NATIVE-AUTH-G1/G2 должны доказать протокол на NTFS до его принятия, AUTH2–AUTH8 — после реализации. AWR-20261007-U01 остаётся существующим canonical blocker:4 original reader symlink assertions не выполнены из-за Win1314; full reader/release gate открыт.

**Вопросы и Proposals.** Q-3: список inputs дополнен после AWR fixes; это обновление контекста, не ошибка исходной карточки: SESSION_STATE уже указывал свежие evidence, а карточка подготовлена до исправлений. Q1/Q2 решены как рабочие технические Proposals с высокой уместностью самостоятельного решения: layout/state/limits и отдельный read-only input adapter/private prepared boundary плюс wrapper UI. Они не меняют принципиальную нужду, scope creation slice или сложность кардинально; пользовательский ответ не блокирует. Native proof — обязательный технический gate, не запрос новых прав. DESIGN_PROFILE.json фиксирует все выбранные варианты. Первый note standalone; existing-object editor/Entity/Collection остаются отдельными шагами.

**Deferred / Follow-up.** D-1: explicit maintenance/partial-publication repair перед quota exhaustion или нужным repair; без него сохраняются INCOMPLETE и controlled quota refusal. D-2: larger files/jobs/full UX/human/a11y перед реальным превышением текущего профиля или deployment, иначе повышение одной цифры не расширит всю цепочку. D-3: pinned-target/editor/research/evolution milestones; generic теория/алгоритм сохраняются сейчас, автоматическая актуализация/Watch ещё не реализованы. Новых User Assistance запросов сейчас нет; существующий AWR capability вопрос остаётся у своего canonical ID.

**Ограничения.** Local probes используют явные portable synthetic adapters; новая Windows source boundary/UI/journal ими не доказана. Native source/old evidence проверены, новый runtime не запускался. API документация служит основанием прототипа, не доказательством hardware durability: [CreateFileW](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-createfilew), [FlushFileBuffers](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-flushfilebuffers).

Review Log: REVIEW_LOG.json. Original card: CARD_BEFORE_REVIEW.json. Следующая команда — bounded implementation по DESIGN_PROFILE и native gates; сохранив immutable accepted components, канонические schemas и264 baseline. Не повторять завершённое ревью и не принимать R1/MVP автоматически.
