# Worked lifecycle case

Every claim cites its source. Missing facts are UNKNOWN. Contradictions are registered, not resolved.

---

## Case metadata

| Field | Value |
| :- | :- |
| Track | DDLC — Portwell Analytics |
| Principal case | INCIDENT-03: the self-service number moved and nobody could say why (retrospective) |
| Held-out case | REQUEST-007: self-service per account for the August 2026 packs (prospective) |
| Principal trace type | Counterfactual — what would the proposed lifecycle have done when the July 2026 figures were produced |
| Held-out trace type | Prospective — active item traced through the proposed lifecycle |
| Sources | `docs/incidents/INCIDENT-03.md`, `docs/pr-notes/0088-self-service-v3.md`, `data/requests/REQUEST-007.docx`, `data/requests/REQUEST-011.docx`, `data/ops-extract/extract-manifest.yaml`, `data/ops-extract/suggestion.csv`, `project/metrics/metric-definitions.yaml`, `project/models/staging/stg_suggestions.sql`, `project/tests/*.sql`, `docs/policies.md`, `data/tracker.csv`, `docs/interviews/2026-08-12 Declan Byrne...` |

---

## Trace 1 — Principal: INCIDENT-03

### Setup

The June 2026 reporting period has closed. The monthly refresh of `self_service_rate` is due for the July service review packs. This is the production cycle that generated the figures that triggered INCIDENT-03.

In the current process (no lifecycle): build ran → figures delivered → customer pack published → Sunder Retail Supply (ACCOUNT-1008) questioned why the self-service figure changed between June and July packs → two-day investigation → incorrect root-cause attribution (INCIDENT-03 attributed change to v2→v3 transition; C6 in `notes/findings.md` documents that this is structurally impossible because `human_edit_material` — required by v3 — is absent from `data/ops-extract/suggestion.csv`). Source: `docs/incidents/INCIDENT-03.md`.

This trace shows what the proposed lifecycle would have done at each stage.

### Trace table

| # | Skill | Context read | Evidence produced | Proposed state | Result | Human decision |
| -: | :- | :- | :- | :- | :- | :- |
| 1 | **Intake** | `data/requests/inbox.csv` (no open monthly refresh item for July); `project/metrics/metric-definitions.yaml` (`self_service_rate` v3 declared current since 2026-07-01, owner: Sofia Marques) | `evidence/intake-REFRESH-2026-07.md`: trigger = month close, metric = `self_service_rate`, `version_specified: false` | Context | → Context | None required at this stage |
| 2 | **Context** — period check | `data/ops-extract/extract-manifest.yaml`: `taken_at` (July 2026, exact date UNKNOWN — manifest in repo is dated 2026-08-28 for the August extract; July extract details reconstructed from Declan Byrne interview); declared coverage for July period | `evidence/context-REFRESH-2026-07.md` partial: `period_match: true` (assumed — manifest covers July reporting period) | — | Period check passes | None |
| 3 | **Context** — field check | `project/metrics/metric-definitions.yaml` v3 (effective 2026-07-01): requires `sent`, `human_edit_material` (to exclude material edits), and within-48h-reopening indicator from ticket status; `data/ops-extract/suggestion.csv` column list: `suggestion_id, ticket_id, created_at, article_ids, confidence, route, route_reason, sent` | `evidence/context-REFRESH-2026-07.md` completed: `human_edit_material: absent from extract`, `fields_check_result: blocked`, `context_status: blocked` | **Blocked** | **⛔ CATCH POINT 1 — Lifecycle stops. Build not started.** Field `human_edit_material` required by `self_service_rate` v3 is absent from `data/ops-extract/suggestion.csv`. Item moves to Blocked. | **Required — stop and ask Declan Byrne + Sofia Marques:** "The current definition of `self_service_rate` v3 requires `human_edit_material`, which is not in the extract. The metric cannot be computed as defined. Options: (a) proceed with v2 with explicit requester agreement; (b) request a new extract that includes `human_edit_material`. Which should I do?" |
| 4 | [Human decision recorded] | — | Analytics lead records decision in `evidence/context-REFRESH-2026-07.md`: `decision: proceed with self_service_rate v2 for the July cycle; reason: human_edit_material absent from extract, v3 not computable; authorised_by: [Analytics lead name UNKNOWN]; requester_informed: true` | Route | → Route (v2 path authorised) | Analytics lead chooses v2, records decision, informs Reporting |
| 5 | **Route** | `project/models/marts/self_service.sql`: `is_self_served = CAST(sent AS BOOLEAN)` (v2 logic, source: `stg_suggestions.sql`); `project/metrics/metric-definitions.yaml`: v2 status = superseded, v3 = current (but v2 authorised for this run per step 4); `docs/policies.md` POLICY-13 (figures in packs must cite metric name and version — not currently enforced by pipeline) | `evidence/route-REFRESH-2026-07.md`: `mart_implements_version: v2`, `current_definition_version: v3`, `mart_definition_aligned: true (v2, authorised by human decision at Context)`, `policy_13_applicable: true`, `path_chosen: standard_build` | Act | → Act | None additional |
| 6 | **Act** | `project/run.py`; `data/ops-extract/extract-manifest.yaml` (`taken_at`, `taken_by`); `project/metrics/metric-definitions.yaml` v2 fields | `evidence/build-REFRESH-2026-07.md`: `definition_version_in_effect: v2 (authorised — v3 not computable with current extract)`, `mart_logic_used: CAST(sent AS BOOLEAN) AS is_self_served`, `exit_code: 0`, `output_row_counts: [non-zero]` | Verify | → Verify | None |
| 7 | **Verify** — shape tests | `project/tests/*.sql` (6 tests): accepted_values_tier, first_response_positive, no_null_self-service_for_pilot, not_null_self-service_account, referential_ticket_account, self_service_rate_in_range | `evidence/verify-REFRESH-2026-07.md` partial: `shape_tests_verdict: pass` | — | All 6 shape tests pass — same result as in the actual July cycle. Note: these tests do not verify which definition version was used. Source: `notes/findings.md` section "O que os 6 testes verificam." | None |
| 8 | **Verify** — definition alignment | `project/models/staging/stg_suggestions.sql`: `CAST(sent AS BOOLEAN) AS is_self_served`; `project/metrics/metric-definitions.yaml` v2: `is_self_served = sent (boolean)` — aligned; human decision at step 4 authorises v2 for this cycle | `evidence/verify-REFRESH-2026-07.md` completed: `definition_alignment_verdict: aligned (v2, authorised)`, `period_alignment_verdict: match`, `verify_status: clear` | Approve | → Approve | None — v2 alignment confirmed against the authorised decision |
| 9 | **Approve** | All 5 evidence files (`evidence/intake-`, `context-`, `route-`, `build-`, `verify-REFRESH-2026-07.md`); `docs/policies.md` POLICY-13 | `evidence/approve-REFRESH-2026-07.md`: package assembled with `policy_13_citation: self_service_rate v2`, `definition_version_in_effect: v2 (authorised — v3 requires extract update)`, `definition_alignment_verdict: aligned (v2)`, `status: awaiting_approval` | awaiting sign-off | **⛔ CATCH POINT 2 — Hard stop. Skill does not advance until a named person records `approved_by` and `approved_at`.** | **Required — Analytics lead (or named approver per POLICY-06) reviews the package and signs. The package explicitly states that v2 was used and why.** |
| 10 | [Named approver signs] | — | `evidence/approve-REFRESH-2026-07.md` updated: `approved_by: [name UNKNOWN]`, `approved_at: [datetime UNKNOWN]`, `status: approved` | Handoff | → Handoff | Analytics lead signs the approval record |
| 11 | **Handoff** | `evidence/approve-REFRESH-2026-07.md`; `evidence/build-REFRESH-2026-07.md` | `delivery/figures-REFRESH-2026-07.csv` with provenance header: `metric: self_service_rate`, `version: v2`, `period: July 2026`, `extract_date: [taken_at UNKNOWN]`, `approved_by: [name]`; `evidence/consumer-log.md` created with first three entries: Sunder Retail Supply (ACCOUNT-1008, service review pack), help portal (per INCIDENT-03: "portal still serves the metric"), board slide from REQUEST-005 (per INCIDENT-03) | Observe | **⛔ CATCH POINT 3 — Delivery file carries explicit version label `v2`.** Figures delivered as CSV file, never as a message. Consumer log created. | None |
| 12 | **Observe** | `evidence/handoff-REFRESH-2026-07.md`; `evidence/consumer-log.md`; `project/metrics/metric-definitions.yaml` (monitoring for new versions) | `evidence/observe-REFRESH-2026-07.md`: `definition_version_delivered: v2`, `monitoring_period: July 2026 pack cycle`, `consumer_error_reports: []`, `definition_changes_detected: []`, `observe_status: active` | active | Observe active — monitoring for consumer reports and definition changes | None at this point |

### Where INCIDENT-03 would have been intercepted

INCIDENT-03 was triggered by Sunder Retail Supply noticing their self-service figure changed between June and July packs. The team took two days to respond and attributed the cause to the v2→v3 definition transition — an attribution that C6 in `notes/findings.md` documents as structurally impossible: the mart has never implemented v3 (`stg_suggestions.sql` uses `CAST(sent AS BOOLEAN)`, v2 logic), and the field v3 requires (`human_edit_material`) does not exist in the extract (`suggestion.csv` columns: `suggestion_id, ticket_id, created_at, article_ids, confidence, route, route_reason, sent`).

The proposed lifecycle intercepts this at three independent points:

**Catch point 1 — Context, step 3:** The field check finds `human_edit_material` absent. The build does not start. A human decision is required before any July number is produced. The choice between "proceed with v2" and "wait for a new extract" is made explicitly, recorded in evidence, and associated with a named authoriser. The undocumented fallback to a superseded definition — the root condition for all subsequent ambiguity — is eliminated.

**Catch point 2 — Approve, step 9:** The approval package states `definition_version_in_effect: v2` and `policy_13_citation: self_service_rate v2`. The named approver sees this before signing. Even if the decision at Context had been made without full documentation, the Approve stage forces the approver to confirm which version they are releasing.

**Catch point 3 — Handoff, step 11:** The delivery file carries `version: v2` in the provenance header (per POLICY-13, `docs/policies.md`). When Sunder Retail Supply receives the July figures, the version is visible. When they compare with June figures (also v2), the versions match. This immediately eliminates the definition-change hypothesis — without any investigation — and directs the inquiry to the actual cause (data behaviour change, extract quality, or portal logic change). The two-day investigation would have been minutes.

**What the lifecycle does not resolve:** The actual cause of the figure change between June and July packs remains UNKNOWN. The proposed lifecycle would have shortened the investigation from two days to minutes (by eliminating the definition-change hypothesis via version provenance), but it does not determine why the number moved. Investigating the real cause requires looking at account-level behaviour in the underlying operational data — outside the scope of this lifecycle.

---

## Failure, refusal, or ambiguity — INCIDENT-03 trace

**What happened at step 3:** The Context skill read `project/metrics/metric-definitions.yaml` and determined that `self_service_rate` v3 (current since 2026-07-01) requires the field `human_edit_material`. It then read the column headers of `data/ops-extract/suggestion.csv` and found the field absent. Per `skills/context/SKILL.md` step 5, the skill stopped and refused to advance to Route.

**Why the lifecycle did not advance:** The lifecycle rule is explicit: if a field required by the current definition is absent from the extract, the item moves to Blocked and a human decision is required before any build begins. The reason this rule exists is to prevent the silent fallback to a superseded definition — precisely what occurred in the actual July 2026 cycle and what the two-day investigation failed to identify.

**Recovery path taken in this trace:** The Analytics lead decided to proceed with v2 for the July cycle and recorded the reason. This is a valid lifecycle path — the lifecycle does not prohibit using v2; it prohibits doing so without explicit human authorisation and documentation. The decision propagated forward: every subsequent stage recorded `v2` in its evidence, and the delivery file carried the version label.

**The contrast with what actually happened:** In the actual July 2026 cycle, no decision was recorded. The build used v2 logic (the only logic the mart has ever had), the figures were delivered without version metadata, and when Sunder Retail Supply asked why the number changed, nobody could answer from evidence — only from memory. Source: `docs/incidents/INCIDENT-03.md`; `docs/interviews/2026-08-12 Declan Byrne...`: "if someone asks in three months where a number came from, I have a message and a memory."

---

## Trace 2 — Held-out: REQUEST-007

### Setup

Lucia Ferreira (Reporting) submitted REQUEST-007 on 2026-08-11, requesting self-service figures by account for the August 2026 packs, deadline 2026-09-04. Source: `data/requests/REQUEST-007.docx`, `data/requests/inbox.csv`.

The request does not specify a definition version. Source: `data/requests/REQUEST-007.docx`.

A possible duplicate exists: REQUEST-011, submitted by Henrik Sole (Reporting) on 2026-08-18, requesting "automation rate by account" for the same deadline. Source: `data/tracker.csv` note: "REQUEST-007 e REQUEST-011 podem ser o mesmo número; ninguém perguntou se eles querem o mesmo número." The duplication has not been resolved in the current process.

### Trace table

| # | Skill | Context read | Evidence produced | Proposed state | Result | Human decision |
| -: | :- | :- | :- | :- | :- | :- |
| 1 | **Intake** | `data/requests/inbox.csv` (REQUEST-007 open; REQUEST-011 open — same deadline 2026-09-04, overlapping description per tracker note); `project/metrics/metric-definitions.yaml` (`self_service_rate` found, v3 current) | `evidence/intake-REQUEST-007.md`: `metric_defined: true`, `version_specified: false`, `needed_by: 2026-09-04`, `duplicate_flag: suspected` (REQUEST-011) | **Escalated** | **⛔ FIRST STOP — Suspected duplicate. Lifecycle escalates before Context.** Skill surfaces evidence of overlap to Declan Byrne. | **Required — Declan Byrne must confirm with both Lucia Ferreira and Henrik Sole whether REQUEST-007 and REQUEST-011 are the same number before any work proceeds.** |
| 2 | [Human decision: different requests] | `data/requests/REQUEST-007.docx`: "self-service rate per account"; `data/requests/REQUEST-011.docx`: "automation rate" — requesters confirm these are different metrics requested by different stakeholders | `evidence/intake-REQUEST-007.md` updated: `duplicate_flag: confirmed_different`, `confirmation_source: [Declan Byrne, Lucia Ferreira, Henrik Sole — all names; dates UNKNOWN]` | Context | → Context | Declan Byrne confirms with requesters; result recorded in intake evidence |
| 3 | **Context** — period check | `data/ops-extract/extract-manifest.yaml`: `taken_at: 2026-08-28T09:14:00Z`, `taken_by: Declan Byrne`, coverage declared as "Covers tickets opened before 2026-08-28" (source: manifest); REQUEST-007 deadline is 2026-09-04, requesting August 2026 figures | `evidence/context-REQUEST-007.md` partial: `extract_taken_at: 2026-08-28T09:14:00Z`, `reporting_period_requested: August 2026` | — | **Clarification needed:** August 2026 ends 2026-08-31. The manifest declares coverage only through 2026-08-28 — three days short. Skill stops and asks Declan Byrne: "The manifest declares coverage through 2026-08-28. August ends 2026-08-31. Does this extract cover the full August reporting period, or is a new extract required?" Note: `project/run.py` docstring confirms "Nothing here compares that date to the period being reported on" — this check is manual, not automated. | **Required — Declan Byrne clarifies whether the extract is complete for August or if a new extract must be taken.** |
| 4 | [Period confirmed or new extract taken] | Human confirms coverage is sufficient for the August figures as scoped (or a new extract is taken through 2026-08-31) | `evidence/context-REQUEST-007.md` updated: `period_match: true` (with confirmation note) | — | Period check resolved | Declan Byrne records confirmation |
| 5 | **Context** — field check | `project/metrics/metric-definitions.yaml` v3: requires `human_edit_material`; `data/ops-extract/suggestion.csv` columns: `suggestion_id, ticket_id, created_at, article_ids, confidence, route, route_reason, sent`; `project/models/staging/stg_suggestions.sql`: no `human_edit_material` column loaded | `evidence/context-REQUEST-007.md` completed: `human_edit_material: absent from extract`, `fields_check_result: blocked`, `context_status: blocked` | **Blocked** | **⛔ SECOND STOP — Same structural block as INCIDENT-03 trace.** `human_edit_material` required by v3, absent from extract. This is a systemic constraint: every request for `self_service_rate` at the current definition will block here until the extract is updated. | **Required — Declan Byrne + Sofia Marques decide: (a) v2 with explicit requester agreement, or (b) wait for new extract.** |
| 6 | [Decision: v2 with requester agreement] | Human decision recorded; Lucia Ferreira informed that August figures will use `self_service_rate` v2 and that v3 requires an extract field update | `evidence/context-REQUEST-007.md` updated: `decision: proceed with v2; reason: human_edit_material absent from extract; requester_informed: true (Lucia Ferreira); authorised_by: [Analytics lead, name UNKNOWN]` | Route | → Route | Analytics lead authorises v2; Lucia Ferreira agrees |
| 7 | **Route** | `project/models/marts/self_service.sql` (v2 logic confirmed); `project/metrics/metric-definitions.yaml` (v2 authorised for this run); `docs/policies.md` POLICY-13 | `evidence/route-REQUEST-007.md`: `mart_implements_version: v2`, `mart_definition_aligned: true (v2, authorised)`, `policy_13_applicable: true`, `path_chosen: standard_build` | Act | → Act | None additional |
| 8 | **Act** | `project/run.py`; `data/ops-extract/extract-manifest.yaml` | `evidence/build-REQUEST-007.md`: `definition_version_in_effect: v2 (authorised)`, `mart_logic_used: CAST(sent AS BOOLEAN) AS is_self_served`, `exit_code: 0` | Verify | → Verify | None |
| 9 | **Verify** | 6 shape tests (pass); `stg_suggestions.sql` vs. v2 definition (aligned); period alignment confirmed | `evidence/verify-REQUEST-007.md`: `shape_tests_verdict: pass`, `definition_alignment_verdict: aligned (v2)`, `period_alignment_verdict: match`, `verify_status: clear` | Approve | → Approve | None |
| 10 | **Approve** | All 5 evidence files; POLICY-13; POLICY-06 check (no destructive operation — not applicable) | `evidence/approve-REQUEST-007.md`: package assembled with `policy_13_citation: self_service_rate v2`, `definition_version_in_effect: v2 (authorised — v3 requires extract update)`, `status: awaiting_approval` | awaiting sign-off | **⛔ HARD STOP — Named approver required.** | **Required — Analytics lead reviews and records `approved_by`, `approved_at`.** |
| 11 | [Named approver signs] | — | `evidence/approve-REQUEST-007.md` updated: `approved_by: [name UNKNOWN]`, `approved_at: [datetime UNKNOWN]`, `status: approved` | Handoff | → Handoff | Analytics lead signs |
| 12 | **Handoff** | Approve and build evidence | `delivery/figures-REQUEST-007.csv` with provenance header: `metric: self_service_rate`, `version: v2`, `period: August 2026`, `extract_date: 2026-08-28T09:14:00Z`, `approved_by: [name]`; `evidence/consumer-log.md` updated with entry: Lucia Ferreira, Reporting, `self_service_rate v2`, August 2026 pack | Observe | → Observe | None |
| 13 | **Observe** | `evidence/handoff-REQUEST-007.md`; `evidence/consumer-log.md`; `project/metrics/metric-definitions.yaml` | `evidence/observe-REQUEST-007.md`: `definition_version_delivered: v2`, `monitoring_period: August 2026 pack cycle`, `observe_status: active` | active | Observe active | None |

### Comparison with INCIDENT-03 trace

REQUEST-007 hits the same structural block at Context (step 5 here, step 3 in INCIDENT-03): `human_edit_material` absent. This confirms the block is systemic: it applies to every `self_service_rate` request until the extract is updated. Without the lifecycle, the August cycle would produce figures with the same undocumented v2/v3 ambiguity that produced INCIDENT-03.

The REQUEST-007 trace surfaces two issues that the INCIDENT-03 trace did not:

1. **Suspected duplicate (steps 1–2):** The Intake skill flags REQUEST-007 / REQUEST-011 overlap before any work begins. In the current process, the tracker note ("ninguém perguntou se eles querem o mesmo número," `data/tracker.csv`) has no recorded resolution. The lifecycle requires this to be resolved at Intake — before Context, Route, Act, or any build resources are committed.

2. **Extract coverage gap (step 3):** The August extract's manifest declares coverage through 2026-08-28, three days short of month-end. This would not have been caught in the current process (no period check exists — confirmed by `project/run.py` docstring). The Context skill flags it; a human clarifies; the trace continues only after the period question is answered.

---

## Failure, refusal, or ambiguity — REQUEST-007 trace

**What happened at step 1 (duplicate flag):** The Intake skill read `data/requests/inbox.csv` and `data/tracker.csv` and found two open items with the same deadline and overlapping summaries. Per `skills/intake/SKILL.md`, the skill escalated rather than proceeding to Context. The reason: only the two requesters can confirm whether "self-service rate" and "automation rate" refer to the same underlying metric. The skill presented the evidence and stopped.

**What happened at step 5 (field block):** After the duplicate question was resolved and the period gap clarified, the Context skill blocked on the same missing field that blocks every v3 request. This is not a transient issue — it is a structural constraint on the track until the extract is updated. The skill recorded the block, presented the options (v2 or new extract), and stopped.

**Recovery paths in this trace:** Both blocks resolved by human decision — the duplicate confirmed as different items, the v2 path authorised for August. Both decisions were recorded in the evidence so that downstream stages (Route, Act, Verify, Approve) can trace why the version chosen differs from the current definition.

**What the lifecycle cannot resolve:** Whether REQUEST-007 and REQUEST-011 are actually different requests is UNKNOWN at the time of writing — the resolution is represented as "confirmed different" in this trace only to allow the trace to continue. If they are the same request, the correct outcome is Rejected for one of them with justification in `inbox.csv`. The lifecycle surfaces the question; the answer depends on the requesters.

---

## Limitations and next improvement

- The INCIDENT-03 trace is counterfactual. The July 2026 extract details (taken_at, taken_by) are UNKNOWN — the manifest in the repository is for the August 2026 extract. The July details are reconstructed from Declan Byrne's interview (`docs/interviews/2026-08-12 Declan Byrne...`).
- The actual cause of the figure change that triggered Sunder Retail Supply's question remains UNKNOWN. The lifecycle's version provenance would have eliminated the definition-change hypothesis in minutes, but the real cause is not determined by the lifecycle. Investigating it requires looking at account-level behaviour in the operational data — outside this scope.
- The consumer log does not exist in the current repository (ISSUE-30 in `data/tracker.csv`: "No list of who consumes which metric"). The first real execution of the lifecycle must retroactively populate it with the three consumers identified in INCIDENT-03: Sunder Retail Supply (service review pack), help portal ("portal still serves the metric," per INCIDENT-03), and the board slide from REQUEST-005.
- The REQUEST-007 trace assumes the duplicate question was resolved as "different requests." If confirmed as a duplicate, the correct outcome is Rejected — not traced here because the resolution is UNKNOWN.
- `self_service_rate` v3 cannot be computed in any lifecycle-compliant run with the current extract. Every request for v3 will block at Context until `suggestion.csv` includes `human_edit_material`. This is a constraint on the track, not a gap in the lifecycle design.
- The Analytics lead name is UNKNOWN throughout both traces. POLICY-06 and the Approve stage require a named approver. Until the role is assigned to a named person, the lifecycle has an open dependency.
