# Research and Bank

Рабочий репозиторий исследовательской системы и проекта Universal Research / Intelligence Bank.

## С чего начать

1. [Текущее состояние и решения](PLANNING/SESSION_STATE.md) — продолжение работы без восстановления истории из чата.
2. [Master requirements и оси расширения](DRAFT_NOTES/11_MASTER_REQUIREMENTS_AND_EXTENSION_AXES.md) — цель Universal Bank и план фаз A–F (§16).
3. [Машиночитаемые требования](DRAFT_NOTES/REQUIREMENTS_MAP.json) — 115 стабильных ID.
4. [Независимое ревью плана и требований](PLANNING/vnext_plan_requirements_critical_review.md) — проблемы, неопределённости и follow-up items.
5. [Предложение нормализации требований](PLANNING/vnext_requirements_normalization_review.md) — разбор всех 115 требований и 159 backlog-пунктов; изменения ещё не применены полностью.
6. [Хранение и подключение к ChatGPT](PLANNING/STORAGE_OPTIONS_2026-10-05.md) — варианты, опубликованные квоты и границы проверки.

## Что уже существует

[`freelance_research_system_feature_architecture_red_tests/`](freelance_research_system_feature_architecture_red_tests/README.md) содержит перенесённую систему v1.11.0, её контракты, инструменты, тесты, шаблоны, историю принятия фаз и исходный план развития. Этот каталог сохранён без изменения содержимого файлов.

[`DRAFT_NOTES/`](DRAFT_NOTES/00_README.md) содержит черновик Universal Bank, требования, Golden Scenarios, backlog и накопленную историю ревью. Universal Bank ещё не является реализованным приложением.

[`PLANNING/`](PLANNING/SESSION_STATE.md) содержит результаты нашей работы и уточнения, появившиеся после сохранённого архива. Они явно различают принятые решения, предложения и открытые вопросы.

Архитектурные тесты в `ARCHITECTURE_TESTS/` специально описывают будущее поведение через падающие тесты. Их нельзя выдавать за завершённую реализацию. Пилот `ENGINE_PILOT/` также не заменяет принятую v1.11.

## Проверка принятой системы

Из корня репозитория:

```powershell
python -m venv .venv
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt
Set-Location .\freelance_research_system_feature_architecture_red_tests
& ..\.venv\Scripts\python.exe TOOLS/validate_system.py
& ..\.venv\Scripts\python.exe TOOLS/run_tests.py
# Полная регрессия при изменении системы:
& ..\.venv\Scripts\python.exe TOOLS/run_tests.py --full
```

Исходный [development plan](freelance_research_system_feature_architecture_red_tests/REFERENCE/DEVELOPMENT_PLAN_vNext.md) относится к развитию принятой исследовательской системы. План Universal Bank A–F находится в master requirements; это разные планы.

## Хранение

Этот GitHub-репозиторий выбран для системы, проектных документов и результатов планирования. Выбор хранилища пользовательских данных Bank, особенно приватных изображений и PDF, остаётся открытым до проверки полного пути сохранения, поиска, визуального анализа в ChatGPT и записи результата обратно.

Происхождение и контроль переноса: [IMPORT_MANIFEST.json](PLANNING/IMPORT_MANIFEST.json).

## Результат проверки переноса

Все исходные файлы сохранены побайтово. На Windows выявлено расхождение классификации узла tests/TESTS в генераторе карты системы: валидатор и один тест parity падают; остальные восемь групп короткого набора проходят. Детали и следующий шаг: [IMPORT_VALIDATION.md](PLANNING/IMPORT_VALIDATION.md).
