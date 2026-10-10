# Решения и открытые развилки

Источник новых уточнений — пользовательский разговор 2026-10-10, сохранённый в [плане DOC-REBASE](../PLANNING/DOCUMENTATION_REBASE_PLAN_2026-10-10.md). Historical requirements имеют document lineage, но неизвестную исходную attribution; не приписывать им новые commits.

| Установлено | Применение |
| --- | --- |
| Все прикладные типы настраиваемые | Новый замысел; старый закрытый runtime действует до отдельного перехода |
| Сущность — объект Bank; исследуемый объект — роль | Исправляет терминологию, не объединяет identity источника и его предмета |
| ChatGPT/Туннель — основной путь | Операции и данные устойчивы между чатами; ручной путь возможен позднее |
| История сохраняется, версии не перегружают обычную работу | Сквозное сохранение, не обязательное создание второй версии |
| Сейчас без UI/представлений/экспорта | Временный scope; прежняя визуальная приёмка deferred, не закрыта |
| Локальный доступ при включённом ПК достаточен | Облако/другие AI providers не обязательные prerequisites |

Материальные Proposals (origin=assistant, status=selected candidate, **не committed**):

- PR-ENGINE-001: NEXT-01 перед production-интеграцией. HIGH review / MEDIUM autonomy: малый эксперимент обратим, выбор постоянного двигателя зависит от evidence. RECOMMENDED_WITH PR-COMPAT-001.
- PR-COMPAT-001: сначала совместимость старого профиля и один generic slice, затем расширение. HIGH / MEDIUM: защищает данные, точная migration policy неизвестна. Полную автоматическую миграцию не выполнять сейчас.

F-U-DOC-001 (UPSTREAM, HIGH, partially blocking): core + адаптер или полный runtime gendocen. Блокирует production dependency composition, не временную пробу. Закрытие: проверенные результаты и выбор по требованиям persistence/freshness. Связанный PR-ENGINE-001.

F-U-DOC-002 (UPSTREAM, HIGH, partially blocking): чтение старого профиля через совместимый adapter или явная миграция в новый формат. Варианты различаются переписыванием/откатом и стоимостью поддержки. Блокирует реальную миграцию, не документы. Закрытие: compatibility probe, backup/restore evidence и отдельный migration Proposal. Связанный PR-COMPAT-001.

F-U-DOC-003 (UPSTREAM, HIGH, partially blocking): какие конкретные будущие promises были committed, а какие остаются catalog candidates. Исходные классы/ID сохранены; новое распределение не понижает обязательный outcome. Закрытие перед выпуском/снятием scope: исходные решения или пользовательский выбор. Не блокирует обновление текста по явным уточнениям.

Recommended composition: PR-ENGINE-001 + PR-COMPAT-001, TRANSACTION OPEN; conflicts/unsatisfied REQUIRES отсутствуют. Принятие документационной редакции не принимает эти product Proposals атомарно. Выбор движка/миграции требует внимания перед downstream реализацией; прежний выбранный user вариант B редакторов не отменён.
