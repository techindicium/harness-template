---
name: recover
description: Handles three paths — rebuild (corrected figure), restatement (published figure was wrong), and retirement (figure is withdrawn) — including notifying every consumer recorded in the Observe consumer log.
---

# Recover

## Purpose
Correct the state of published figures through one of three paths — rebuild, restatement, or retirement — and ensure that every consumer who received the original figure receives the correction or withdrawal notice.

## Entry conditions
- An Observe entry or an Analytics lead decision has identified one of three conditions:
  1. **Rebuild**: the build failed or produced incorrect output; a corrected build is required.
  2. **Restatement**: a figure was delivered to consumers but is now known to be wrong (wrong definition version, wrong extract period, or model error); a corrected figure replaces it.
  3. **Retirement**: the metric or figure is being withdrawn; no replacement is issued; consumers must be informed.
- `evidence/consumer-log.md` contains at least one consumer entry for the affected delivery.
- The Analytics lead has explicitly chosen one of the three paths.

## Required context
- `evidence/observe-<REQUEST-NNN>.md` — to read the error report or definition-change trigger
- `evidence/consumer-log.md` — to identify every consumer who received the original figure and any downstream uses
- `evidence/handoff-<REQUEST-NNN>.md` — to read what was delivered and to whom
- `evidence/approve-<REQUEST-NNN>.md` — to read what was approved and which version
- `project/metrics/metric-definitions.yaml` — for the current definition (if rebuilding or restating)
- `docs/policies.md` — POLICY-05 (notification), POLICY-06 (named approver for destructive operations)

## Prohibited context
- Do not perform a restatement without a named approver on the corrected build (same requirement as Approve).
- Do not retire a figure without notifying every consumer listed in `evidence/consumer-log.md`, including downstream uses.
- Do not delete or overwrite `evidence/handoff-<REQUEST-NNN>.md` or any prior evidence; the original delivery record must be preserved.
- Do not modify the track repository.

## Procedure

### Path 1 — Rebuild (corrected build, no consumers yet affected)
1. Record the reason for rebuild in `evidence/recover-<REQUEST-NNN>.md`: `path: rebuild`, `reason`, source of the error.
2. Return the item to **Act** with a note: "Rebuild required. Prior build log preserved at `evidence/build-<REQUEST-NNN>.md`." The prior evidence is not deleted.
3. If the rebuild requires a different extract (period mismatch), return to **Context** instead.

### Path 2 — Restatement (figure was delivered; it is wrong; a correction replaces it)
1. Record in `evidence/recover-<REQUEST-NNN>.md`: `path: restatement`, `original_delivery_date`, `original_definition_version`, `error_description`, `impact_scope` (which consumers, which periods, which figures).
2. Re-run the lifecycle from the appropriate stage: if the extract is correct, return to Act; if the extract must be replaced, return to Context.
3. When the corrected build is approved (Approve stage, with a named approver), assemble a restatement delivery package:
   - `delivery/restatement-<REQUEST-NNN>.csv` containing the corrected figures
   - A cover note specifying: what the original figure was, what the corrected figure is, why it changed, which definition version was used for each
4. Notify every consumer listed in `evidence/consumer-log.md` for the affected delivery, including any downstream consumers recorded during Observe. Notification must be a written record (file or tracked message), not a verbal statement.
5. Record each notification in `evidence/recover-<REQUEST-NNN>.md`: `notified_consumer`, `notification_date`, `notification_method`.
6. If the figure has already been included in a customer-facing pack (as in INCIDENT-03, where Sunder Retail Supply received the figure in their pack), record this in the recover evidence and escalate to the Analytics lead to determine whether a direct customer communication is required.

### Path 3 — Retirement (figure is withdrawn; no replacement)
1. Record in `evidence/recover-<REQUEST-NNN>.md`: `path: retirement`, `retirement_reason`, `effective_date`.
2. Notify every consumer listed in `evidence/consumer-log.md` that the figure is retired: what it was, why it is being withdrawn, what (if anything) replaces it.
3. Record each notification as in Path 2, step 5.
4. Mark the consumer log entries for this metric as `status: retired` (do not delete).
5. Mark `evidence/observe-<REQUEST-NNN>.md` as `observe_status: retired`.

## Evidence produced
- `evidence/recover-<REQUEST-NNN>.md` in the harness, containing:
  - `path: rebuild / restatement / retirement`
  - `reason` and `error_description`
  - `original_delivery_date`, `original_definition_version`
  - `impact_scope` (consumers, periods, figures affected)
  - `corrected_definition_version` (if restatement)
  - `notifications`: list of `{consumer, notification_date, notification_method}`
  - `downstream_consumers_notified: true/false`
  - `customer_facing_escalation_required: true/false`
- `delivery/restatement-<REQUEST-NNN>.csv` (Path 2 only)
- Updated `evidence/consumer-log.md` entries

## Proposed transition
- Rebuild: return to **Act** (or **Context** if extract must change).
- Restatement: proceed through Act → Verify → Approve → Handoff (with restatement delivery), then close.
- Retirement: after all consumers notified → **terminal state** (item closed).

## Stop or escalation conditions
- A consumer who received the figure cannot be contacted or their downstream use cannot be traced → stop and notify Analytics lead: "Consumer `<name>` received figures from REQUEST-NNN but I cannot confirm they have received the restatement. Manual follow-up required."
- The figure appeared in a customer-facing pack (as with Sunder Retail Supply, INCIDENT-03) → stop and notify Analytics lead: "The affected figure reached at least one external customer. A direct customer communication may be required. This decision is outside the scope of this skill."
- The corrected build also fails Verify (e.g., because the mart still does not implement the current definition) → stop: "The corrected build has the same definition misalignment as the original. I cannot produce a restatement without a mart update. Escalating to Analytics lead."
- No consumer log exists for the affected delivery → stop and ask Declan Byrne: "I cannot identify who received the figure from REQUEST-NNN. The consumer log has no entry for this delivery. Who should receive the restatement or retirement notice?"

## Human judgment boundary
Three decisions in Recover belong exclusively to a named person: (1) whether a restatement is material enough to require customer notification (vs. internal correction only); (2) whether the retired metric has a replacement that consumers should be directed to; (3) whether the corrected build requires a new named approver or the original approver can re-approve. The skill presents the evidence and stops at each of these; it does not decide.
