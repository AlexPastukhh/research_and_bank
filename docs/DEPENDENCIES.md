# Зависимости и актуальность

**Need, candidate/inferred:** использовать структурированные данные и производные поля без обязательного Markdown-вывода. **PR-ENGINE-001, assistant, selected candidate:** проверить gendocen малым экспериментом; постоянное принятие двигателя ещё pending. См. [следующую карточку](../PLANNING/WORK_ITEMS/NEXT_GENERIC_DATA_PROBE.json).

Зависимость поля — например, budget = hours × rate. Простая ссылка vacancy → source означает связанность объектов; она не создаёт вычисление. Изменение hours должно потребовать новый budget; изменение несвязанного комментария не обязано. Сохранённый AI-вывод может потребовать смыслового пересмотра, а не механического автопереписывания.

| Проверено в snapshot gendocen | Ограничение |
| --- | --- |
| BuildStore get/version допускает адаптер; временная SQLite-проба работала | Не интегрирован с настоящим Bank/Windows |
| ctx.read фиксирует nested JSONPointer; ctx.get зависит от всего объекта | Точность зависит от реально прочитанных входов |
| DerivedObject.to_builtin возвращает JSON-совместимые данные | Markdown-рендер не обязателен и исключён сейчас |
| Циклы/недостающий вход и устаревшая операция проверяются | Нет доказательства готового постоянного Bank cache |
| BuildOperation cache действует внутри операции | Постоянные dependencies/evidence требуют отдельного решения |
| persistent/semantic runtime хранит файловые records | Не готовая SQLite drop-in замена |
| FieldPlan есть в примерах | Не стабильный отдельный kernel API и не редактор формул |

Изученный snapshot: `6c7aac0f48b3d475722f64083c3e1ddffc176368`, runtime `0.1.0.dev25`. 63 targeted проверки PASS, 2 skipped из-за jsonschema; это не полный suite и не Windows acceptance. Исходный проект: https://github.com/AlexPastukhh/gendocen. Результаты перенесены как evidence исследования; библиотека здесь не установлена.

Минимальный эксперимент: временное определение типа, JSON-объекты с Markdown-строкой, правило, JSON результата и читаемая после перезапуска provenance. Проверить used/unrelated field, nested/transitive dependency, missing, cycle, stale publish и старый профиль без миграции реальных данных. Выход должен различать fresh/stale/error/review_required и входные состояния; названия статусов пока candidate.

Существенная развилка: core + Bank adapter либо полный файловый runtime. Вторая даёт существующие records, но добавляет согласование двух хранилищ. Первая требует собственного persistence. Delta количественно unknown; выбор может отменить downstream работу, поэтому HIGH review / MEDIUM autonomy, до production-интеграции требуется evidence пробы. Новый язык формул, scheduler, UI и экспорт не нужны для этой проверки.
