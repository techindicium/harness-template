---
name: approve
description: Use after a Verify PASS to prepare the decision request for the approving role and to record the decision a human gives. Never asserts that an approval happened unless a named person with the right role said so in this run. Any decision given only for demonstration is recorded with simulated true.
---

# Approve

Lifecycle stage: Record the role's decision.

## Purpose
Put the decision in front of the role that owns it, with the evidence, and record exactly what that human says. Approve prepares and records. It never decides and never speaks for a role.

## Entry conditions
- A Verify report with verdict PASS exists for this transition in this run.
- If the verdict is FAIL or missing, refuse and send the item to `recover`.

## Required context
- The Verify report and the Route record of this run.
- The "Who approves" column of the transition in `lifecycle.md`.
- The human's reply, given in this session.

## Prohibited context
- Silence, a tick, a draft, an earlier statement or "nobody objected in the meeting" as approval (the last is how docs/How we work today.docx describes agreement today).
- An approval from a person who does not hold the role the transition names. Ana Fialho as product decision role is a declared assumption, so the person must confirm the role.
- Speaking or recording on behalf of Ana Fialho or Tomas Silva.
- Using a decision to fill a gap in evidence. A simulated or real decision never replaces evidence Verify required.

## Procedure
1. Confirm the Verify verdict is PASS for this transition.
2. Name the approving role from `lifecycle.md` and, if known, the person, marking assumed roles as assumed.
3. Write the decision request: what is proposed, the evidence pointers, what happens on approve, deny and defer. Address it to the role.
4. Stop and wait. Do not fill any decision field.
5. When a human replies, record: person, role they state, date and time, their exact words, form (written in this session, document, or verbal, not recorded) and the pointer to any document.
6. Check the role matches. If not, record the reply as "not valid for this transition" and do not proceed.
7. If the reply is given only for demonstration, or by a participant on behalf of a role, set `simulated: true` and write "demonstration, not a real decision of <role holder>". The record then carries `simulated: true` into the transition log line.
8. If there is no reply, record the outcome as "pending". Do not assume a default.
9. Append the Approve record to `traces/worked-case.md`, under "Stage evidence".

## Evidence produced
Approve record: transition; role required; person; stated role; date; form; exact words; evidence pointer; `simulated` (true or false); outcome (approved, denied, pending or not valid).

## Proposed transition
If the outcome is approved (real, or simulated inside a demonstration): recommend `handoff` to write the transition line. If denied, pending or not valid: recommend `recover`. The state does not change in this skill.

## Stop or escalation conditions
- Verify did not return PASS: refuse.
- No person, role or date attached to the decision: record "pending" and stop.
- The person's role does not match the transition: refuse the approval.
- A request to approve on someone's behalf: refuse, or record only as `simulated: true` if it is for demonstration.
- A terminal transition (T9, T10, T11, T12) asked for without the required written approval from its named role: refuse.

## Human judgment boundary
The role named in the transition decides: tracker maintainer, product decision role, item owner, policy owner or escalation target role. Whether evidence is sufficient and whether a disagreement is resolved are theirs. This skill never claims that a human approval occurred unless the Approve record contains a named person, role, date and words from this run, and it labels every demonstration answer `simulated: true`.
