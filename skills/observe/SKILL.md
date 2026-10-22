---
name: observe
description: Use only after handoff has written a transition line for the item. Inspects what followed (a recorded response, the counter of recorded attempts, days since the last touch when both dates are recorded) and proposes the next round. Cannot act on an item with no transition written.
---

# Observe

Lifecycle stage: Inspect the outcome. It cannot act until the item has a recorded transition.

## Purpose
After a transition is written, look at what the records show happened next and report it. Observe reports. It does not change state.

## Entry conditions
- `traces/transition-log.md` has at least one line for the item written by `handoff` in this run or an earlier one.
- The item is not in a terminal state. For a terminal state there is nothing to observe.
- If no line exists for the item, stop and say "no recorded transition, observe cannot act". Do not read the tracker as a substitute.

## Required context
- The log lines for the item.
- Any response document or message a human points to, with its source and date.
- The retry limit and maximum days in the failure table of `lifecycle.md`.

## Prohibited context
- Counting "claimed, not recorded" attempts.
- Computing days when either date is "unknown", or comparing to a maximum that is "unknown".
- Choosing between the tracker's last touch and the log's last line. Report each separately.
- Treating a reply as the requested information. The policy owner confirms that (T7).

## Procedure
1. Read the last line for the item and its `to` state.
2. Look for a recorded response after it. If none is pointed to, write "no recorded response".
3. Count recorded attempts (log lines for T3, T4, T13 with date, recipient and content).
4. Compute days since the last recorded touch only when both dates are recorded. Otherwise write "not computable".
5. Report the observations. Suggest T5 or T13 if the records support them. Do not execute any.
6. Append the Observe report to `traces/worked-case.md`, under "Stage evidence".

## Evidence produced
Observe report: last recorded transition; response found or "no recorded response"; recorded attempts count; days since last touch or "not computable"; suggested next transition, if any.

## Proposed transition
None. Observe may suggest T5 or T13, which `route` and `recover` handle. Next stage: `route` for a new round, or `recover`.

## Stop or escalation conditions
- No transition line for the item: stop.
- Item terminal: stop.
- Dates unknown: report "not computable" and stop at that measure.

## Human judgment boundary
Whether a response answers the question belongs to the policy owner. Whether a stall is confirmed belongs to the item owner. This skill never states that either decided.
