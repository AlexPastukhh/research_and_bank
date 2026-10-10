# Текущее состояние

Сверено 2026-10-10 с Windows HEAD `eaac02ee3ae266b158db28c1abeaa76c5b465868` и рабочими документами. HEAD не идентифицирует незакоммиченные изменения; их hashes учитываются при применении.

| Область | Фактическая граница |
| --- | --- |
| Принятая исследовательская система | v1.11 в отдельной исходной папке; не переписана новым замыслом |
| Локальный Bank | SQLite, immutable originals/revisions/receipts, secure intake, typed reads, exact/lexical search и command adapter реализованы |
| Профиль записи | Asset, Entity, Annotation, Collection; Note — Annotation(kind=note), возможны targets=[] |
| Редакторы | Entity/Collection/targeted Annotation и revisions подключены; ограниченные native проверки выполнены |
| Source / research | Source — R0 contract / будущее сохранение; Source/Lens/Run/Result не универсальный работающий workflow в текущем Bank |
| Новая модель | Registry произвольных типов, правила/derived fields и gendocen не интегрированы |
| Приёмка | FUB/OBJ технические gates и отдельные receipts; пользовательская визуальная/adoption приёмка не подтверждена |

[First Bank receipt](../PLANNING/WORK_ITEMS/R1_FIRST_USABLE_BANK_RECEIPT.json), [authoring receipt](../PLANNING/WORK_ITEMS/R1_OBJECT_AUTHORING_RECEIPT.json), [completion review](../EXPERIMENTS/object_authoring/implementation/COMPLETION_REVIEW.md). Статус карточек implemented_native_verified_awaiting_user_visual_acceptance не означает полную готовность продукта.

Отложено: FUB10 и GUI-части OBJ10/OBJ11. Причина — явная пауза работы над UI/представлениями. Revisit trigger: пользователь явно возвращает это направление. Они блокируют только визуальную/adoption приёмку соответствующих runtime outcomes; документацию и временную data-пробу не блокируют. Старые gates не удаляются и не становятся PASS.

Реальные пользовательские config/данные находятся в `%LOCALAPPDATA%\ResearchAndBank`, вне Git. Исходные материалы и native evidence не импортировать/переписывать для эксперимента. Использовать `.venv\Scripts\python.exe`: системный Python может быть недоступен или без нужных зависимостей.

[Единственная точка продолжения](../PLANNING/SESSION_STATE.md). Исторические «следующие шаги» receipts и подробные R0–R8 не являются текущей очередью. Документационное обновление не доказывает исправление любого runtime-дефекта и не закрывает полный MVP.
