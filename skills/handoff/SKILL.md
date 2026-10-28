---
name: handoff
description: Delivers the approved figures as a file artifact (never as a message), records every consumer, and logs the provenance so that future questions about origin can be answered from the log rather than from memory.
---

# Handoff

## Purpose
Deliver the approved build output to the requester as a file that includes its own provenance, and register every consumer in the consumer log so that definition changes and restatements can reach them.

## Entry conditions
- `evidence/approve-<REQUEST-NNN>.md` exists with `approved_by` and `approved_at` filled by the named approver. `status` is a label and is not an entry condition.
- No block or escalation is recorded in any prior evidence file.
- `approved_by` holds a person's name. Blank, `UNKNOWN`, a role and a placeholder do not count.
- The handoff gate check exits 0 for the item: `python3 scripts/hooks/handoff_gate.py check <REQUEST-NNN>`, run from the repository root. It reads the same evidence as the conditions above, plus the period and the build, and prints what to do when it exits 1. Any other non-zero exit means the check did not run: treat the item as not clear.

## Required context
- `evidence/approve-<REQUEST-NNN>.md` — to read `approved_by`, `approved_at`, `definition_version_in_effect`, `policy_13_citation`
- `evidence/build-<REQUEST-NNN>.md` — to read `extract_taken_at`, `extract_taken_by`, `output_row_counts`
- `evidence/intake-<REQUEST-NNN>.md` — to read `requester`, `from_team`, `needed_by`
- `project/metrics/metric-definitions.yaml` — to confirm metric name and version for the pack header

## Prohibited context
- Do not deliver figures as a message, a paste, or a Slack text. The delivered artifact must be a file.
- Do not deliver without `approved_by` holding a person's name. If it does not, stop.
- Do not omit the provenance header from the delivery file (metric name, version, extract date, approver name, approval date).

## Procedure
1. Run the handoff gate check for the item (the command in the entry conditions), from the repository root. If it exits with any code other than 0, stop: do not assemble the delivery, and follow the NEXT and ASK THE USER sections it prints. If it printed none, the check itself failed: tell the user. The same check blocks the writes of the delivery artifacts when the session loaded the project hooks; this step does not depend on that. Then read `evidence/approve-<REQUEST-NNN>.md` and confirm `approved_by` holds a person's name (not blank, `UNKNOWN`, a role or a placeholder). Otherwise stop.
2. Assemble the delivery file `delivery/figures-<REQUEST-NNN>.csv` in the harness. This file must include, as a header comment or companion section:
   - `metric_name` and `definition_version` (from `policy_13_citation` in the approve evidence)
   - `extract_taken_at` and `extract_taken_by`
   - `approved_by` and `approved_at`
   - `request_id`
3. Copy the relevant mart output rows into the delivery file. Do not recompute; use the output captured in `evidence/build-<REQUEST-NNN>.md`.
4. Deliver `delivery/figures-<REQUEST-NNN>.csv` to the requester via a file transfer (shared folder or equivalent). Do not send figures as a message body.
5. Record the delivery: update `evidence/handoff-<REQUEST-NNN>.md` with `delivered_to`, `delivered_at`, `delivery_method: file`, `delivery_path`.
6. Update the consumer log (`evidence/consumer-log.md` in the harness, or the equivalent persistent log) with a new row: `consumer_name`, `team`, `request_id`, `metric_name`, `definition_version`, `delivered_at`. If this is the first entry for this consumer, add them; if the consumer already appears, add a new row for this delivery. Note: ISSUE-30 in `data/tracker.csv` ("Não temos uma lista de consumidores") is addressed by this step — the consumer log maintained here becomes that list.

## Evidence produced
- `delivery/figures-<REQUEST-NNN>.csv` in the harness, with provenance header.
- `evidence/handoff-<REQUEST-NNN>.md` in the harness, containing: `request_id`, `delivered_to`, `delivered_at`, `delivery_method`, `delivery_path`.
- Updated `evidence/consumer-log.md` with a new consumer entry.

## Proposed transition
- File delivered and consumer log updated → propose **Observe**.
- Delivery failed (file not received, wrong recipient) → return to **Handoff** (re-deliver).
- Approver was not recorded and delivery was blocked → propose **Approve** (the approval step must be completed before Handoff can proceed).

## Stop or escalation conditions
- The handoff gate check exits with a code other than 0, or a write of a delivery artifact is blocked by the gate → stop and do not deliver. Do not retry through another path and do not edit the evidence to satisfy the gate. Put the questions the gate prints to the user.
- `approved_by` field in `evidence/approve-<REQUEST-NNN>.md` is blank or does not hold a person's name → stop and do not deliver. Notify Declan Byrne: "The approval for REQUEST-NNN has not been recorded. I will not deliver figures without a named approver on file."
- The delivery method requested by the requester is a chat message or Slack paste → refuse and explain: "Delivery by message leaves no traceable artifact. Per the lifecycle, figures are delivered as a file. Please provide a file share path."

## Human judgment boundary
Only a person can confirm that the recipient is the correct one for the given request. The skill does not infer the delivery target from the team name; it reads `requester` from the intake evidence. If the requester has changed (e.g., Lucia Ferreira is on leave and a colleague is covering), a person must update the intake note before Handoff proceeds.
