# История и источники документации

Актуальный вход: [docs/README.md](../../docs/README.md). Дата перехода: 2026-10-10. Старые подробные планы и closed-type описания — справка об исходном контексте, не competing active authority.

Сохраняются 115 requirement IDs и их origin/change_history, 159 backlog B IDs, normalization Proposals, SC-001…074/SRU-000…042/GSU, R0–R8 и решения v1.11. Новые SC-075/076 находятся в актуальном документе; старые номера не переиспользованы.

[Инвентарь](../../DRAFT_NOTES/REQUIREMENTS_MAP.json), [backlog](../../DRAFT_NOTES/BACKLOG_TRIAGE.json), [normalization](../../DRAFT_NOTES/NORMALIZATION_PROPOSALS.json), [исторический release map](../REQUIREMENTS_RELEASE_MAP.json), [review](../vnext_requirements_normalization_review.md), [исходный сценарный каталог](../../DRAFT_NOTES/research_bank_desired_scenarios.md).

Source statement snapshots не переписаны под новый замысел. Уточнения и текущее распределение живут в docs/OUTCOME_MAP.json; original attribution неизвестна там, где не восстановлена ранее. Accepted v1.11 и завершённые receipts не меняются. Старые подробные процедуры читаются вместе с новым authority banner.

Перед HOST apply исходные байты затрагиваемых файлов сохраняются локально и в отдельном change-history пакете с SHA-256. Bridge snapshot хранит их полные preimages, а apply сверяет каждый затрагиваемый путь. История apply дополняется receipt; GUI или продуктовые Proposals этим не принимаются.
