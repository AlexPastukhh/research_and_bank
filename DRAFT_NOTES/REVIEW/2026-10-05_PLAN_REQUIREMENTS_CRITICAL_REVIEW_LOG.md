# Review Log — 2026-10-05_PLAN_REQUIREMENTS_CRITICAL_REVIEW

**Объект / scope:** current `vnext_requirements_updated.zip` (reviewed input SHA-256 `2d5403b2717ba6ba5a7e506c97a0f20bb756a51b9b4d80bf529006699e5380ee`), Universal Bank master §16 A–F, 115 JSON requirements, human scope, 159 backlog bullets, scenarios, normalization report v1.1 и scoped OPP-017 update; legacy Phase0–7 отдельно как прежний plan. Runtime vNext не заявлен проверенным.

**Итог:** направление соответствует user intent; current authoritative documents и план требуют consolidation до implementation. Изменение OPP-017 корректно; остальные normalization proposals ещё не applied.

**Подтверждённые существенные проблемы:**

- MRQ-001: у 114/115 entries нет explicit kind/axes/human_ref/change_history; reasoning inventory недостаточно traceable (основной результат).
- MRQ-002: полная 159-item triage есть в report, но часть ideas/open questions не classified в authoritative map (основной результат).
- MRQ-003: MVP mechanics, minimal provenance links, claim enum и target clustering различаются в human/JSON (основной scope).
- MRQ-004: Source!=Entity решено в контексте, definitions ещё ambiguous; uncertainty reclassified как documentation drift (основной data-contract scope).
- RVP-001: initial GitHub всё ещё внутри полностью open OPEN-011; closed backend нужно отделить от open topology (локально).
- RVP-002: A–F не фиксирует MVP checkpoint/requirement acceptance, basic proof смешан с TARGET C/D (основной plan readiness).

**Неопределённости:** минимальный callable ChatGPT/app/Git handoff и effective RunSpec; metadata vs raw assets в Git; точная target clustering obligation. Эти вопросы не доказывают runtime failure.

**Что прошло:** 115 unique IDs, target/future=25/19, остальные counts сохранены; OPP-017 history/scope/reference parity; 115/159 report coverage; ZIP CRC и INDEX hashes; все 264 legacy files byte-identical; history intact; official reference descriptions подтверждены без hands-on claims.

**Deferred / возврат:**

- DF-MRQ-001: actual auth/private/sensitive use → access/secret/exposure policy; иначе возможны неверные права/экспозиция данных.
- DF-MRQ-003: первый schema consumer/generator/CI → format version и parity/links validation; иначе consumer breakage/drift.
- DF-RVP-001: implementation negative examples → dimension/exclusion/unknown-feature semantics и relevance comparison; иначе erroneous exclusions/объяснения.
- DF-RVP-002: первый writable prototype/concurrent writes/media growth → atomicity/idempotency/recovery/assets/index policy; иначе partial refs/lost updates/неуправляемый storage.
- DF-RVP-003: merge/split/reprojection → historical ResultOccurrence retention отдельно от rebuilt indexes; иначе переписанная история выдачи.
- Existing DF-MRQ-002: перед implementation promotion → feature-level acceptance; не заменяет текущий plan checkpoint fix.

**Ограничения:** supplied context only; single-agent independent approach, не separate reviewer; no vNext runtime/quality/cost/security acceptance, legacy tests не переаттестованы; official-product descriptions вместо API/export/pricing benchmark.

**Открытые вопросы:** Git metadata/raw media/runtime placement; reduced MVP proof checkpoint; target clustering scope; operational hard exclusion/missing-feature rule до implementation.

**Disposition:** сохранить current defects открытыми; не закрывать MRQ по этому review. В archive добавлены review/log/checks, ledger history events и updated INDEX; intent requirements/план не исправляются автоматически. Legacy contracts и прошлые reviews сохранены.
