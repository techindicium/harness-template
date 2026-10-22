---
name: route
description: Use after context to pick which permitted transition an item should attempt next and how much the skills may do alone. Refuses requests for transitions that do not exist from the item's current state, for example marking RESOLVED from OPEN_UNOWNED.
---

# Route

Lifecycle stage: Choose the candidate transition.

## Purpose
Read the item's current state, list the transitions allowed from it, check what each one still lacks using the Context evidence, and pick one candidate with an autonomy level. Route chooses the path. It never approves or performs a transition.

## Entry conditions
- Intake and Context evidence blocks exist for the item in this run.
- The item is not terminal.

## Required context
- Current state: the last line for the item in `traces/transition-log.md` if the file exists. Otherwise the state proposed by Intake, marked as "not yet written to the log". If that last line carries `simulated: true`, report the state as "simulated state" and never present it as the item's real state.
- The Intake and Context evidence blocks of this run.
- The transitions table, flags and failure table in `lifecycle.md`.
- The counter of recorded attempts (recorded only, never "claimed, not recorded").

## Prohibited context
- Re-reading product sources to find new facts. If a fact is missing, send the item back to `context`.
- Inferring an owner, a date or a recipient.
- Choosing between conflicting sources.

## Procedure
1. State the current state and active flags.
2. List the transitions that leave this state (from `lifecycle.md`). From OPEN_UNOWNED these are T2, T5, T11 and T12. If the item has no line in the log yet, the only candidate is T1 ((start) to OPEN_UNOWNED), proposed by Intake.
3. If the request names a target state with no transition from the current state, refuse. List the shortest permitted path, for example OPEN_UNOWNED to RESOLVED needs T2, T3, T7 and T9, each with its own evidence and approval.
4. For each listed transition, mark what Context shows as present, absent, in conflict or "not computable". This is a preliminary read. `verify` does the check.
5. Pick the candidate. If more than one is plausible, stop and ask the human which to attempt.
6. Set the autonomy level:
   - `draft`: the skills may prepare material, and nothing changes state without a recorded human approval. This is the highest level in Module 1.
   - `stop`: nothing can be prepared because the evidence or the role is missing. Hand to the human with what is missing.
7. Name the human decision point and the role that must decide.
8. Choose the next stage: `act` for `draft`, `recover` for a limit, deadline, conflict or missing role, `approve` only when everything is ready and just a decision is missing.
9. Append the Route record to `traces/worked-case.md`, under "Stage evidence".

## Evidence produced
Route record: current state and flags; transitions listed with presence of evidence; candidate (T#) or refusal with the permitted path; autonomy level; human decision point and role; next stage.

## Proposed transition
The candidate T#, recommended only. Next stage: `act`, `recover` or `approve`. For BLOCKER-01 in OPEN_UNOWNED: T2 needs an assignment record that does not exist (level `stop`, ask the product decision role). T5 is "not computable" while the maximum days without touch is unknown, so route to `recover`. T12 needs a human decision.

## Stop or escalation conditions
- No permitted transition applies: refuse and list the path.
- The choice depends on deciding between conflicting sources: stop, ask the fact authority.
- Two or more candidates: stop and ask which to attempt.
- Context is missing for the item: send back to `context`.

## Human judgment boundary
The human confirms the route when there is more than one candidate. Designating an owner or an escalation target belongs to the product decision role (Ana Fialho is a declared assumption, not a fact). Route never states that a transition was approved.
