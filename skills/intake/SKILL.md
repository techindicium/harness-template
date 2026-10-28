---
name: intake
description: Accepts and bounds a new work item by registering the request or monthly refresh trigger with enough information to scope the work.
---

# Intake

## Purpose
Accept and register a work item — an incoming request or a monthly refresh trigger — with enough detail to determine which metric is being asked for and whether it is already in progress.

## Entry conditions
- A request has arrived from Reporting, Product, or Portal Engineering; OR the month has closed and a refresh cycle is due.
- No existing open item for this request has already been registered (checked against `data/requests/inbox.csv`).

## Required context
- `data/requests/inbox.csv` — to check for existing open items and to determine the next REQUEST-NNN
- `project/metrics/metric-definitions.yaml` — to confirm the requested metric exists and which version is current
- `docs/identifiers.md` — to assign the correct REQUEST-NNN format
- `data/requests/REQUEST-NNN.docx` — if the requester provided a written brief

## Prohibited context
- Nothing from outside the `portwell-analytics` track repository may be treated as a definition source.
- Do not read, infer, or use the extract CSVs at this stage — the extract is not yet in scope.

## Procedure
1. Read `data/requests/inbox.csv`. Search for open items with the same requester name and a summary that overlaps with the new request. If a likely duplicate exists (e.g., REQUEST-007 "self-service" and REQUEST-011 "automation rate" from `data/tracker.csv`, note: "REQUEST-007 e REQUEST-011 podem ser o mesmo número"), record the suspected duplicate and stop at "Stop or escalation conditions."
2. Determine the next REQUEST-NNN: take the highest REQUEST-NNN in `inbox.csv` and add one, following the format described in `docs/identifiers.md`.
3. Record in the harness intake note (`evidence/intake-<REQUEST-NNN>.md`): request_id, from_team, requester, received (today's date), needed_by (as stated by the requester or UNKNOWN), and a verbatim copy of the summary.
4. Look up the requested metric in `project/metrics/metric-definitions.yaml`. If the metric is not listed, record `metric_defined: false`.
5. Check whether the requester specified a definition version. If not, record `version_specified: false` — this gap must be resolved at Context before a build can begin.
6. Record the deadline exactly as stated. If no deadline was given, record `needed_by: UNKNOWN`. Do not estimate.

## Evidence produced
- `evidence/intake-<REQUEST-NNN>.md` in the harness, containing: request_id, from_team, requester, received, needed_by, summary (verbatim), metric_name, metric_defined (true/false), version_specified (true/false/version string), duplicate_flag (none/suspected/confirmed).

## Proposed transition
- Metric defined and no duplicate → propose **Context**.
- Metric not found in `metric-definitions.yaml` → propose **Blocked** (cannot route without a definition; record `block_reason: metric undefined`).
- Suspected or confirmed duplicate → propose **Escalated** (human must confirm whether items are the same before Context proceeds).

## Stop or escalation conditions
- Two open items share the same deadline and overlapping summary (e.g., REQUEST-007 and REQUEST-011 per `data/tracker.csv`) → stop and escalate to Declan Byrne: "REQUEST-NNN and REQUEST-NNN appear to describe the same number. Please confirm with both requesters whether they are the same item before I proceed."
- The requester's team is not one of the four known consuming teams (Reporting, Product, Portal Engineering, customer-facing account) → stop and ask Declan Byrne: "Who is authorising this request and which team does it come from?"

## Human judgment boundary
Only a person can confirm whether two requests from different requesters using different names (e.g., "self-service rate" vs. "automation rate") refer to the same metric. The skill surfaces the ambiguity and presents the evidence; the human resolves it.
