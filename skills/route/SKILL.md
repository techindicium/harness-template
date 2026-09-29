---
name: route
description: Determines the build path by checking whether the mart implements the current definition, whether a definition change is in progress, whether duplicates exist, and what can be resolved autonomously vs. what requires a human decision.
---

# Route

## Purpose
Choose the build path and level of autonomy: decide whether to proceed directly to Act, escalate because a human decision is required, or reject because the request cannot be fulfilled.

## Entry conditions
- `evidence/context-<REQUEST-NNN>.md` exists with `context_status: clear`.
- All required fields are confirmed present in the extract and in staging.

## Required context
- `evidence/intake-<REQUEST-NNN>.md`
- `evidence/context-<REQUEST-NNN>.md`
- `project/metrics/metric-definitions.yaml` — to confirm the current definition version and check for recently superseded versions
- `project/models/marts/self_service.sql` (and other relevant mart files) — to determine which definition version each mart currently implements
- `project/models/staging/stg_suggestions.sql` — to confirm field mapping for `is_self_served`
- `data/requests/inbox.csv` — to check for open duplicate requests
- `docs/policies.md` — to check POLICY-05 (announce definition changes one period ahead), POLICY-06 (named approver for destructive transforms), POLICY-13 (figures in packs must cite metric name and version)

## Prohibited context
- Do not run `project/run.py` at this stage; that belongs to Act.
- Do not declare a routing decision without checking mart vs. definition alignment.
- Do not treat passing shape tests as evidence that the mart implements the current definition — the 6 shape tests in `project/tests/` verify form only, not correctness (confirmed: `project/tests/*.sql`, Declan Byrne interview).

## Procedure
1. Read `project/metrics/metric-definitions.yaml`. Confirm the current version of the requested metric. Confirm it is not `status: superseded`.
2. Read the relevant mart SQL. Compare the logic implemented with the current definition. Record `mart_implements_version` and `current_definition_version`. For `self_service_rate`: the mart `project/models/marts/self_service.sql` uses `is_self_served = CAST(sent AS BOOLEAN)` — this is v2 logic. The current definition as of 2026-07-01 is v3 (per `project/metrics/metric-definitions.yaml`). If `mart_implements_version ≠ current_definition_version`, stop — see "Stop or escalation conditions."
3. Check `data/requests/inbox.csv` for open items that may overlap with the current request. If a suspected duplicate has not been resolved since Intake, re-escalate.
4. Check `docs/policies.md` for applicable policies:
   - POLICY-05: if the definition version changed recently, identify known consumers from the Observe consumer log. If no consumer log exists or the list is empty, record `policy_05_block: true`.
   - POLICY-06: if the build requires `rebuild.py` or dropping a mart, record that a named approver is required at Approve.
   - POLICY-13: record that the evidence package at Approve must include the metric name and version used; this is not enforced by the pipeline.
5. Determine the routing path and record justification in `evidence/route-<REQUEST-NNN>.md`.

## Evidence produced
- `evidence/route-<REQUEST-NNN>.md` in the harness, containing:
  - `metric_name`, `current_definition_version` (from `metric-definitions.yaml`)
  - `mart_implements_version` (from mart SQL)
  - `mart_definition_aligned: true/false`
  - `path_chosen: standard_build / escalated / rejected`
  - `duplicate_flag: none / suspected / confirmed`
  - `policy_05_applicable: true/false`, `policy_05_block: true/false`
  - `policy_06_applicable: true/false`
  - `policy_13_applicable: true/false`
  - `justification` with source citations

## Proposed transition
- Mart aligns with current definition, no duplicate, no policy block → propose **Act**.
- Mart does not implement current definition → propose **Escalated** (human decides: fix mart first or proceed with the implemented version and document it explicitly).
- Confirmed duplicate request → propose **Rejected**.
- POLICY-05 applicable and no consumer list → propose **Escalated** (consumers must be identified before publishing a number based on a changed definition).

## Stop or escalation conditions
- `mart_implements_version ≠ current_definition_version` → stop and ask Declan Byrne and Analytics lead: "The mart `<mart>.sql` implements `<metric>` v<old> (field: `is_self_served = CAST(sent AS BOOLEAN)`). The current definition is v<new>. Should I update the mart before building, or proceed with v<old> and document that the output does not match the current definition? Note: the requester has not specified a version."
- Two open requests share the same deadline and overlapping summary and no resolution was recorded at Intake → stop and ask Declan Byrne: "REQUEST-007 and REQUEST-011 have the same deadline (2026-09-04) and may describe the same number. Please confirm with both requesters before I proceed."
- POLICY-05 applies (definition changed) and no consumer list is available → stop and ask Sofia Marques: "The definition of `<metric>` changed to v<N> on `<date>`. POLICY-05 requires announcing definition changes one period ahead. I cannot find a consumer list. Who should be notified, and has the notification been sent?"

## Human judgment boundary
The decision to proceed with a superseded mart implementation vs. waiting for a mart fix is a scope and risk trade-off that only the Analytics lead can make. The skill presents the misalignment and its implications (a published number labelled current but computed from a superseded definition); it does not choose.
