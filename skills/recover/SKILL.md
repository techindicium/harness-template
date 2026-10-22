---
name: recover
description: Use when verify failed, approve was denied or pending, a retry limit or deadline is reached, a conflict blocks a fact, or an owner or escalation target is missing. Counts recorded attempts, proposes STALLED or ESCALATED when the records allow, answers "not computable" without a maximum, and stops with ESCALATION_REQUIRED_NO_TARGET when no target exists. Never closes an item and never chooses a destination.
---

# Recover

Lifecycle stage: Retries, stall and escalation.

## Purpose
Handle work that is blocked, failed or ambiguous without hiding it and without making it look resolved. Recover records the failure, counts attempts, and proposes the next permitted step or stops.

## Entry conditions
- A Verify FAIL, an Approve outcome of denied, pending or not valid, or an Observe suggestion.
- Or one of: retry limit reached, maximum days exceeded, an unresolved conflict over a needed fact, a missing item owner, a missing escalation target.

## Required context
- The failing record (Verify, Approve or Observe) and the Route record of this run.
- The failure and recovery table and the transitions table in `lifecycle.md`.
- `traces/transition-log.md` for recorded attempts.

## Prohibited context
- Closing the item or setting any terminal state (RESOLVED, DECLINED, CANCELLED, MERGED).
- Choosing or suggesting an escalation target. This includes the "person waiting" that Ana Fialho mentions, and anyone from `data/people/headcount.xlsx`.
- Counting "claimed, not recorded" attempts toward the limit.
- Estimating a maximum, a deadline or any missing date.
- Resolving a conflict between sources.

## Procedure
1. Record the cause: which skill failed and why, with the pointer.
2. Count attempts separately: recorded (log lines with date, recipient and content) and claimed. For BLOCKER-01 this is "3 claimed, 0 recorded" (tracker H9, Ana Fialho interview).
3. Compare to the retry limit: 3 recorded attempts. This is a author hypothesis, not validated, and the only number in the sources is Ana Fialho's "three".
4. Below the limit: recommend the next permitted step toward a further recorded attempt, through `route` and `act`: T4 from AWAITING_RESPONSE, T13 from STALLED, T3 from OPEN_OWNED, and T2 first when the item has no owner. Propose nothing else.
5. At the limit with recorded dates: propose T5 (STALLED) for the item owner to confirm. If there is no item owner, the product decision role confirms.
6. For the deadline part of T5: the maximum days without touch is "unknown". Answer "not computable" and propose nothing, even though the tracker shows 60 days since the last touch (G9 to the run date).
7. From STALLED, if escalation is needed (T6): check for an escalation target role recorded by a human. If none, raise ESCALATION_REQUIRED_NO_TARGET and stop. Ask the product decision role to name one. Offer no name.
8. For a conflict that blocks a fact, point to FACTS_IN_DISPUTE and the fact authority. Do not decide.
9. Append the failure record to `traces/worked-case.md`, under "Stage evidence".

## Evidence produced
Failure record: cause with pointer; attempts recorded and claimed; retry limit and its status; days and maximum ("not computable" when unknown); flags raised; proposed transition or "none, and why".

## Proposed transition
At most one of: T4 or T13 (another recorded attempt), T5 (STALLED), T6 (ESCALATED, only with a named target), or none. Each is a recommendation. The state is unchanged here. Next stage: `route`, or stop for a human.

## Stop or escalation conditions
- Maximum days without touch unknown: "not computable", no T5 on the deadline.
- No escalation target: raise ESCALATION_REQUIRED_NO_TARGET and stop.
- No item owner and no product decision role available to confirm: stop.
- A request to close, cancel, merge or mark resolved: refuse. Those transitions belong to the named roles (T9 to T12) and need their own evidence.
- A request to name a destination: refuse.

## Human judgment boundary
The item owner confirms T5. The product decision role approves T6 and designates the escalation target (Ana Fialho is a declared assumption, not a fact). The fact authority records the value of a disputed fact. This skill never closes an item and never states that anyone approved a step.
