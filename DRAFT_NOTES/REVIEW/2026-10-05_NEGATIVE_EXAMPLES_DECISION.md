# Decision update — positive and negative examples

Date: 2026-10-05. Scope: vNext product intent; accepted v1.11 contracts are unchanged.

The user approved promotion of `OPP-017` from `FUTURE_OPPORTUNITY` to `TARGET_REQUIRED`, explicitly outside MVP. Its ID is retained despite the historical OPP prefix so references and status history remain stable.

The capability supports positive and negative seed examples, with explicit similarity dimensions to include or avoid. A user can choose a soft negative preference that lowers rank or a hard exclusion. Match/exclusion explanations must reflect the actual supported behavior. Any improvement in search quality must be evaluated with relevant human judgments against a positive-only baseline; this decision is not a claim that quality has already improved.

Updated: `REQUIREMENTS_MAP.json`, master §6.1, the specific 08 backlog bullet, the GSU02 target extension and `INDEX.json`. The standalone normalization report is revised to mark this issue resolved. All other normalization proposals remain proposals; this update does not apply the full normalization pass.

The registry contains 115 entries: 25 TARGET_REQUIRED and 19 FUTURE_OPPORTUNITY; the other categories retain their prior counts. No new requirement ID is allocated. Previous statement/status/area are retained in OPP-017 change_history. The original review findings are historical records and are not rewritten or closed by this targeted update.

Validation: master and JSON agree on target status, outside-MVP scope, selected dimensions, soft preference/hard exclusion, explanation and evaluation. ZIP contents outside the named draft changes are checked byte-for-byte against the input archive. This is a document update, not implementation acceptance or a runtime search test.
