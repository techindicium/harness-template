---
name: observe
description: Monitors post-handoff outcomes by maintaining the consumer log, watching for consumer-reported errors, and triggering Recover if a definition change affects a published number.
---

# Observe

## Purpose
Track where each delivered number was used, maintain the consumer log started at Handoff, receive error reports from consumers, and initiate Recover if a published number is affected by a subsequent definition change.

## Entry conditions
- `evidence/handoff-<REQUEST-NNN>.md` exists with `delivery_method: file` and `delivered_at` filled.
- At least one entry for this delivery exists in `evidence/consumer-log.md`.

## Required context
- `evidence/handoff-<REQUEST-NNN>.md` — to read what was delivered, to whom, and when
- `evidence/consumer-log.md` — the persistent consumer log; to check who received which version
- `evidence/approve-<REQUEST-NNN>.md` — to read `definition_version_in_effect` for the delivered number
- `project/metrics/metric-definitions.yaml` — to detect if a new version has been published since delivery
- `docs/policies.md` — POLICY-05 (announce definition changes one period ahead to affected consumers)

## Prohibited context
- Do not close an item as Observed until at least one monitoring period has passed after delivery.
- Do not remove consumer entries from `evidence/consumer-log.md`; log is append-only.
- Do not infer that a consumer has not used the figure because they have not reported an error. Absence of complaint is not evidence of correctness.

## Procedure
1. After delivery, monitor `evidence/consumer-log.md` for the consumers who received figures from this request. For each consumer, record the context in which the figure is expected to appear (e.g., "Lucia Ferreira — Reporting — monthly client pack for August 2026").
2. At each subsequent period close, check `project/metrics/metric-definitions.yaml` for new or changed definition versions that post-date the `delivered_at` timestamp. If a new version of the delivered metric has become effective since delivery, record it in `evidence/observe-<REQUEST-NNN>.md` and trigger Recover.
3. Receive consumer error reports. If a consumer reports that a figure appears incorrect (as Sunder Retail Supply did in INCIDENT-03, where the self-service figure changed between June and July packs): record the report in `evidence/observe-<REQUEST-NNN>.md` with `reporter`, `report_date`, `description`, and the specific figure cited. Propose Correction required.
4. If a consumer cites a figure in a downstream artefact (another pack, a deck, an external report), update `evidence/consumer-log.md` with the downstream use: `downstream_consumer`, `context`, `date`. This extends the reach of the number and must be captured so that any future restatement can reach every downstream user.
5. Record `observe_status: active` while monitoring continues. Record `observe_status: closed` only when no open consumer errors exist and no pending definition changes affect this number.

## Evidence produced
- `evidence/observe-<REQUEST-NNN>.md` in the harness, containing:
  - `delivery_date` and `definition_version_delivered`
  - `monitoring_period` (the interval being observed)
  - `consumer_error_reports` (list: reporter, date, description, figure cited)
  - `definition_changes_detected` (list: new version, effective date, impact on delivered number)
  - `observe_status: active / closed`
- Updated `evidence/consumer-log.md` if downstream uses are discovered.

## Proposed transition
- Monitoring period closed, no errors, no definition changes → propose **Observe** remains active until next period; mark `observe_status: closed` when no further changes are expected.
- Consumer reports an error → propose **Correction required** (the delivered number may be wrong).
- A definition change post-dates the delivered number and affects the metric → propose **Recover** (the published number is based on a definition no longer in effect; consumers must be notified).

## Stop or escalation conditions
- A consumer reports an error and the error cites a number that the build log does not recognise (the figure cannot be traced to a delivery from this lifecycle) → stop and escalate to Declan Byrne: "A consumer reports an error on a figure I cannot trace to a known delivery. The figure may have been delivered outside the lifecycle (e.g., as a message). I cannot restate it without a traceable source."
- A new definition version is effective but no consumer list exists for the metric → stop and ask Sofia Marques: "A new version of `<metric>` is now in effect. POLICY-05 requires notifying consumers one period ahead. The consumer log for this metric is empty. Who should be notified?"
- Three or more consumers are listed as having received a figure that Verify had flagged as definition-misaligned → stop and ask Analytics lead: "Three or more consumers received figures computed under a superseded definition (v<old>) while the current definition is v<new>. A restatement may be required. Please review and decide whether to initiate Recover."

## Human judgment boundary
The skill can detect that a new definition version is effective and that consumers received figures under an older version. It cannot decide whether the numerical difference between versions is material enough to require a restatement. That is a judgment only the Analytics lead can make, informed by the magnitude of the change and the contractual context of the consumers (e.g., SLA-bearing accounts like Sunder Retail Supply).
