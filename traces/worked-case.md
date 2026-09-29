# Worked lifecycle case

Every claim cites its source. Missing facts are UNKNOWN. Contradictions are registered, not resolved.

---

## Case metadata

| Field | Value |
| :- | :- |
| Track | DDLC — Portwell Analytics |
| Principal case | INCIDENT-03: the self-service number moved and nobody could say why (retrospective) |
| Second case | REQUEST-007: self-service per account for the August 2026 packs (executed) |
| Principal trace type | Counterfactual — what would the proposed lifecycle have done when the July 2026 figures were produced |
| Second trace type | Executed on 2026-09-29 by following each skill; evidence in `evidence/*-REQUEST-007.md` |
| Sources | `docs/incidents/INCIDENT-03.md`, `docs/pr-notes/0088-self-service-v3.md`, `data/requests/REQUEST-007.docx`, `data/requests/REQUEST-011.docx`, `data/ops-extract/extract-manifest.yaml`, `data/ops-extract/suggestion.csv`, `project/metrics/metric-definitions.yaml`, `project/models/staging/stg_suggestions.sql`, `project/tests/*.sql`, `docs/policies.md`, `data/tracker.csv`, `docs/interviews/2026-08-12 Declan Byrne...` |

---

## Trace 1 — Retrospective: INCIDENT-03 (counterfactual, not executed)

The evidence files named in this table (`evidence/*-REFRESH-2026-07.md`) were not produced. They describe what the skills would have written in July 2026. Trace 2 is the executed one.

### Setup

The June 2026 reporting period has closed. The monthly refresh of `self_service_rate` is due for the July service review packs. This is the production cycle that generated the figures that triggered INCIDENT-03.

In the current process (no lifecycle): build ran → figures delivered → customer pack published → Sunder Retail Supply (ACCOUNT-1008) questioned why the self-service figure changed between June and July packs → two-day investigation → root-cause attribution (INCIDENT-03 attributed the change to the v2→v3 transition). C6 in `notes/findings.md` registers this against two other sources that do not agree with it: change note 0088 says the mart still applies the v2 rule, and the July pack shows the figure moving from 0 to 0.3478. The July extract's own columns are UNKNOWN, so whether v3 was computable that month is not established either way; the real cause stays open. Source: `docs/incidents/INCIDENT-03.md`.

This trace shows what the proposed lifecycle would have done at each stage.

### Trace table

| # | Skill | Context read | Evidence produced | Proposed state | Result | Human decision |
| -: | :- | :- | :- | :- | :- | :- |
| 1 | **Intake** | `data/requests/inbox.csv` (no open monthly refresh item for July); `project/metrics/metric-definitions.yaml` (`self_service_rate` v3 declared current since 2026-07-01, owner: Sofia Marques) | `evidence/intake-REFRESH-2026-07.md`: trigger = month close, metric = `self_service_rate`, `version_specified: false` | Context | → Context | None required at this stage |
| 2 | **Context** — period check | `data/ops-extract/extract-manifest.yaml` is the August manifest (`taken_at: 2026-08-28T09:14:00Z`); the July manifest is not preserved. `../portwell-knowledge/data/figures/` holds two July exports: 2026-08-01, "July figures, first cut", and 2026-08-06, "A late batch of tickets landed after the first cut. Use this one." | `evidence/context-REFRESH-2026-07.md` partial: `period_match: UNKNOWN` (not assumed). The only preserved evidence says the first July cut was incomplete | — | Period check cannot be evaluated from preserved evidence. The trace continues to the field check, which does not depend on it | None |
| 3 | **Context** — field check | `project/metrics/metric-definitions.yaml` v3 (effective 2026-07-01): requires `sent`, `human_edit_material` (to exclude material edits), and within-48h-reopening indicator from ticket status; `data/ops-extract/suggestion.csv` column list: `suggestion_id, ticket_id, created_at, article_ids, confidence, route, route_reason, sent` | `evidence/context-REFRESH-2026-07.md` completed: `human_edit_material: absent from extract`, `fields_check_result: blocked`, `context_status: blocked` | **Blocked** | **⛔ CATCH POINT 1 — Lifecycle stops. Build not started.** Field `human_edit_material` required by `self_service_rate` v3 is absent from `data/ops-extract/suggestion.csv`. Item moves to Blocked. | **Required — stop and ask Declan Byrne + Sofia Marques:** "The current definition of `self_service_rate` v3 requires `human_edit_material`, which is not in the extract. The metric cannot be computed as defined. Options: (a) proceed with v2 with explicit requester agreement; (b) request a new extract that includes `human_edit_material`. Which should I do?" |
| 4 | [Human decision recorded] | — | Analytics lead records decision in `evidence/context-REFRESH-2026-07.md`: `decision: proceed with self_service_rate v2 for the July cycle; reason: human_edit_material absent from extract, v3 not computable; authorised_by: [Analytics lead name UNKNOWN]; requester_informed: true` | Route | → Route (v2 path authorised) | Analytics lead chooses v2, records decision, informs Reporting |
| 5 | **Route** | `project/models/marts/self_service.sql`: `is_self_served = CAST(sent AS BOOLEAN)` (v2 logic, source: `stg_suggestions.sql`); `project/metrics/metric-definitions.yaml`: v2 status = superseded, v3 = current (but v2 authorised for this run per step 4); `docs/policies.md` POLICY-13 (figures in packs must cite metric name and version — not currently enforced by pipeline) | `evidence/route-REFRESH-2026-07.md`: `mart_implements_version: v2`, `current_definition_version: v3`, `mart_definition_aligned: true (v2, authorised by human decision at Context)`, `policy_13_applicable: true`, `path_chosen: standard_build` | Act | → Act | None additional |
| 6 | **Act** | `project/run.py`; `data/ops-extract/extract-manifest.yaml` (`taken_at`, `taken_by`); `project/metrics/metric-definitions.yaml` v2 fields | `evidence/build-REFRESH-2026-07.md`: `definition_version_in_effect: v2 (authorised — v3 not computable with current extract)`, `mart_logic_used: CAST(sent AS BOOLEAN) AS is_self_served`, `exit_code: 0`, `output_row_counts: UNKNOWN` (the July build output is not preserved; the figures delivered are in `../portwell-knowledge/data/figures/warehouse-export-2026-08-06.csv`) | Verify | → Verify | None |
| 7 | **Verify** — shape tests | `project/tests/*.sql` (6 tests): accepted_values_tier, first_response_positive, no_null_self-service_for_pilot, not_null_self-service_account, referential_ticket_account, self_service_rate_in_range | `evidence/verify-REFRESH-2026-07.md` partial: `shape_tests_verdict: pass` | — | All 6 shape tests pass — same result as in the actual July cycle. Note: these tests do not verify which definition version was used. Source: `notes/findings.md` section "O que os 6 testes verificam." | None |
| 8 | **Verify** — definition alignment | `stg_suggestions.sql` and `marts/self_service.sql` against `metric-definitions.yaml` v2, field by field | `evidence/verify-REFRESH-2026-07.md`: numerator aligned; denominator counts every ticket opened in the month rather than tickets closed in the period, and the extract has no close date; declared grain account-day against account-month (C8). No July ticket is open in the preserved extract, so the July figure is not changed by the denominator gap. `period_alignment_verdict: UNKNOWN` (step 2), `verify_status: blocked` | Escalated | **Verify does not clear as written.** Steps 9 to 12 assume, counterfactually, that the Analytics lead accepted the documented deviations and the period uncertainty in writing | **Required — the Analytics lead accepts or rejects the documented deviations.** |
| 9 | **Approve** | All 5 evidence files (`evidence/intake-`, `context-`, `route-`, `build-`, `verify-REFRESH-2026-07.md`); `docs/policies.md` POLICY-13 | `evidence/approve-REFRESH-2026-07.md`: package assembled with `policy_13_citation: self_service_rate v2`, `definition_version_in_effect: v2 (authorised — v3 requires extract update)`, `definition_alignment_verdict: aligned (v2)`, `status: awaiting_approval` | awaiting sign-off | **⛔ CATCH POINT 2 — Hard stop. Skill does not advance until a named person records `approved_by` and `approved_at`.** | **Required — Analytics lead (or named approver per POLICY-06) reviews the package and signs. The package explicitly states that v2 was used and why.** |
| 10 | [Named approver signs] | — | `evidence/approve-REFRESH-2026-07.md` updated: `approved_by: [name UNKNOWN]`, `approved_at: [datetime UNKNOWN]`, `status: approved` | Handoff | → Handoff | Analytics lead signs the approval record |
| 11 | **Handoff** | `evidence/approve-REFRESH-2026-07.md`; `evidence/build-REFRESH-2026-07.md` | `delivery/figures-REFRESH-2026-07.csv` with provenance header: `metric: self_service_rate`, `version: v2`, `period: July 2026`, `extract_date: [taken_at UNKNOWN]`, `approved_by: [name]`; `evidence/consumer-log.md` created with first three entries: Sunder Retail Supply (ACCOUNT-1008, service review pack), help portal (per INCIDENT-03: "portal still serves the metric"), board slide from REQUEST-005 (per INCIDENT-03) | Observe | **⛔ CATCH POINT 3 — Delivery file carries explicit version label `v2`.** Figures delivered as CSV file, never as a message. Consumer log created. | None |
| 12 | **Observe** | `evidence/handoff-REFRESH-2026-07.md`; `evidence/consumer-log.md`; `project/metrics/metric-definitions.yaml` (monitoring for new versions) | `evidence/observe-REFRESH-2026-07.md`: `definition_version_delivered: v2`, `monitoring_period: July 2026 pack cycle`, `consumer_error_reports: []`, `definition_changes_detected: []`, `observe_status: active` | active | Observe active — monitoring for consumer reports and definition changes | None at this point |

### Where INCIDENT-03 would have been intercepted

INCIDENT-03 was triggered by Sunder Retail Supply noticing their self-service figure changed between June and July packs. The team took two days to respond and attributed the cause to the v2→v3 definition transition — an attribution that C6 in `notes/findings.md` registers against two other sources: change note 0088 says the mart still applies the v2 rule (`stg_suggestions.sql` uses `CAST(sent AS BOOLEAN)`), and the July pack shows the self-service figure moving from 0 to 0.3478. The field v3 requires (`human_edit_material`) is not in the current extract; the July extract's columns are UNKNOWN.

The proposed lifecycle intercepts this at three independent points:

**Catch point 1 — Context, step 3:** The field check finds `human_edit_material` absent. The build does not start. A human decision is required before any July number is produced. The choice between "proceed with v2" and "wait for a new extract" is made explicitly, recorded in evidence, and associated with a named authoriser. The undocumented fallback to a superseded definition — the root condition for all subsequent ambiguity — is eliminated.

**Catch point 2 — Approve, step 9:** The approval package states `definition_version_in_effect: v2` and `policy_13_citation: self_service_rate v2`. The named approver sees this before signing. Even if the decision at Context had been made without full documentation, the Approve stage forces the approver to confirm which version they are releasing.

**Catch point 3 — Handoff, step 11:** The delivery file carries `version: v2` in the provenance header (per POLICY-13, `docs/policies.md`). When Sunder Retail Supply receives the July figures, the version is visible. When they compare with June figures (also v2), the versions match. This immediately eliminates the definition-change hypothesis — without any investigation — and directs the inquiry to the actual cause (data behaviour change, extract quality, or portal logic change). The two-day investigation would have been minutes.

**What the lifecycle does not resolve:** The actual cause of the figure change between June and July packs remains UNKNOWN. The proposed lifecycle would have shortened the investigation from two days to minutes (by eliminating the definition-change hypothesis via version provenance), but it does not determine why the number moved. Investigating the real cause requires looking at account-level behaviour in the underlying operational data — outside the scope of this lifecycle. Two preserved facts complicate the question itself: the July pack shows the June figure as 0 (C6), and `TICKET-004424`, the ticket the incident cites, was opened on 2026-08-20 about a six-point drop on the dashboard (C15).

---

## Failure, refusal, or ambiguity — INCIDENT-03 trace

**What happened at step 3:** The Context skill read `project/metrics/metric-definitions.yaml` and determined that `self_service_rate` v3 (current since 2026-07-01) requires the field `human_edit_material`. It then read the column headers of `data/ops-extract/suggestion.csv` and found the field absent. Per `skills/context/SKILL.md` step 5, the skill stopped and refused to advance to Route.

**Why the lifecycle did not advance:** The lifecycle rule is explicit: if a field required by the current definition is absent from the extract, the item moves to Blocked and a human decision is required before any build begins. The reason this rule exists is to prevent the silent fallback to a superseded definition — precisely what occurred in the actual July 2026 cycle and what the two-day investigation failed to identify.

**Recovery path taken in this trace:** The Analytics lead decided to proceed with v2 for the July cycle and recorded the reason. This is a valid lifecycle path — the lifecycle does not prohibit using v2; it prohibits doing so without explicit human authorisation and documentation. The decision propagated forward: every subsequent stage recorded `v2` in its evidence, and the delivery file carried the version label.

**The contrast with what actually happened:** In the actual July 2026 cycle, no decision was recorded. The build used v2 logic (the only logic the mart has ever had), the figures were delivered without version metadata, and when Sunder Retail Supply asked why the number changed, nobody could answer from evidence — only from memory. Source: `docs/incidents/INCIDENT-03.md`; `docs/interviews/2026-08-12 Declan Byrne...`: "if someone asks in three months where a number came from, I have a message and a memory."

---

## Trace 2 — Executed: REQUEST-007

### Setup

Run on 2026-09-29 by Yuri Alves (group 5), following each `SKILL.md` in order against `../portwell-analytics` at commit `a8aecb4`. Every row cites the evidence file the skill wrote. Human decisions were simulated by a group member playing the named role and are marked `simulated: true` in the evidence; none of them is a decision by the Portwell people named. At run time the deadline (2026-09-04) had passed, and the inbox still says `open`.

### Trace table

| # | Skill invoked | Context read | Evidence produced | Proposed state | Result | Human intervention |
| -: | :- | :- | :- | :- | :- | :- |
| 1 | **Intake** | `data/requests/inbox.csv`; `REQUEST-007.docx`; `REQUEST-011.docx`; `data/tracker.csv`; `metric-definitions.yaml` | `evidence/intake-REQUEST-007.md`: `metric_defined: true`, `version_specified: false`, `duplicate_flag: suspected` | Escalated | **Stop.** Same deadline and overlapping summary as REQUEST-011. The entry condition "no open item already registered" fails as written, because REQUEST-007 is already in the inbox | Simulated, as Declan Byrne: proceed with REQUEST-007 alone; whether it duplicates REQUEST-011 stays UNKNOWN |
| 2 | **Context**, period | `extract-manifest.yaml`; `ticket.csv` | `evidence/context-REQUEST-007.md`: coverage "before 2026-08-28", last ticket 2026-08-27T18:57, `period_match: false` | Blocked | **Stop.** August is four days short | Simulated, as Declan Byrne: no new extract can be taken (`run.py --live` exits 1); label the figures 2026-08-01 to 2026-08-27 |
| 3 | **Context**, fields | `metric-definitions.yaml` v3; headers of `suggestion.csv`, `ticket.csv`, `interaction.csv`; `stg_suggestions.sql`; `stg_tickets.sql` | Same file: `human_edit_material`, close date and reopen indicator absent; `fields_check_result: blocked` | Blocked | **Stop.** v3 cannot be computed from this extract | Simulated, as Sofia Marques with Lucia Ferreira agreeing: compute v2, the rule the July packs used |
| 4 | **Route** | `marts/self_service.sql`; `stg_suggestions.sql`; `inbox.csv`; `docs/policies.md` | `evidence/route-REQUEST-007.md`: `mart_implements_version: 2`, `current_definition_version: 3`, `policy_05_block: true`, `path_chosen: standard_build` | Act | The version stop is covered by step 3 and the duplicate re-escalation by step 1. **Stop on POLICY-05** | Simulated, as Sofia Marques: August stays on v2, so no consumer sees a change; the v3 announcement is still owed |
| 5 | **Act** | `project/run.py`; manifest; marts | `evidence/build-REQUEST-007.md`: `exit_code: 0`, 10 August rows per mart, full stdout | Verify | Built. The entry condition "period confirmed" fails as written; the run proceeds under step 2's decision | None |
| 6 | **Verify** | Build and context evidence; `metric-definitions.yaml`; `marts/self_service.sql`; `marts/first_response.sql`; `project/tests/`; `../portwell-knowledge/data/figures/` | `evidence/verify-REQUEST-007.md`: `shape_tests_verdict: pass`, `definition_alignment_verdict: misaligned`, `period_alignment_verdict: mismatch`, `verify_status: blocked` | Escalated | **Red.** The 6 tests pass, but v2 differs from the mart on denominator and period, and `first_response.sql` drops the `assist` actor: ACCOUNT-1008's August p50 is 38 as published and 101 today | Not simulated. Publishing with a disclaimer or blocking is the Analytics lead's decision (name UNKNOWN) |
| 7 | **Approve** | `evidence/verify-REQUEST-007.md` | `evidence/approve-REQUEST-007.md`: `status: refused_entry_condition_not_met` | — | **Refusal.** No package assembled, no `approved_by` | None |

**Final state: Escalated**, waiting for the Analytics team to correct `marts/self_service.sql` and `marts/first_response.sql`. Nothing was delivered. Handoff, Observe and Recover did not run.

### Comparison with the INCIDENT-03 trace

- Both traces block at Context on `human_edit_material`. Every request for v3 will block there until the extract carries it.
- The executed trace blocks where the counterfactual one first passed: at Verify. Checking v2 field by field, and running the skill's own first-response check, turns "aligned (v2)" into "misaligned".
- Running the skills exposed three places where they contradict the item or each other: an Intake entry condition that excludes items already registered, an Intake procedure that only matches the same requester, and Act and Verify refusing a partial period that Context let a human accept. They are recorded in `notes/findings.md`.

---

## Failure, refusal, or ambiguity — REQUEST-007 trace

**What happened:** Verify compared the mart with the authorised definition and with the figures Reporting had received, and the numbers did not hold, although the 6 shape tests passed. Approve then refused to assemble a package.

**Why the lifecycle did not advance:** `verify_status: blocked`. The correction needs a change to the track repository, which no skill may make.

**Recovery or escalation:** Escalated to Declan Byrne and the Analytics lead with the verify evidence. Once the marts are corrected, the item re-enters at Act with the same Context and Route decisions (`skills/recover/SKILL.md`, path 1).

---

## Limitations and next improvement

- The INCIDENT-03 trace is counterfactual. The July 2026 extract details (taken_at, taken_by) are UNKNOWN — the manifest in the repository is for the August 2026 extract. The July details are reconstructed from Declan Byrne's interview (`docs/interviews/2026-08-12 Declan Byrne...`).
- The actual cause of the figure change that triggered Sunder Retail Supply's question remains UNKNOWN. The lifecycle's version provenance would have eliminated the definition-change hypothesis in minutes, but the real cause is not determined by the lifecycle. Investigating it requires looking at account-level behaviour in the operational data — outside this scope.
- The consumer log does not exist in the current repository (ISSUE-30 in `data/tracker.csv`: "No list of who consumes which metric"). The first real execution of the lifecycle must retroactively populate it with the three consumers identified in INCIDENT-03: Sunder Retail Supply (service review pack), help portal ("portal still serves the metric," per INCIDENT-03), and the board slide from REQUEST-005.
- The REQUEST-007 trace deferred the duplicate question rather than resolving it, by a simulated decision. If REQUEST-007 and REQUEST-011 are the same number, one of them should end Rejected.
- Every human decision in the executed trace was simulated by a group member playing the named role. None was taken by the Portwell people named.
- The executed trace stops at Verify, so Handoff, Observe and Recover have not yet run against a real item.
- `self_service_rate` v3 cannot be computed in any lifecycle-compliant run with the current extract. Every request for v3 will block at Context until `suggestion.csv` includes `human_edit_material`. This is a constraint on the track, not a gap in the lifecycle design.
- The Analytics lead name is UNKNOWN throughout both traces. POLICY-06 and the Approve stage require a named approver. Until the role is assigned to a named person, the lifecycle has an open dependency.
