---
name: act
description: Use after route when the autonomy level is draft. Prepares the material for the chosen transition (a request, an assignment proposal, an evidence checklist, the draft record line). Sends nothing, names no recipient or owner on its own, and writes no fact nobody recorded.
---

# Act

Lifecycle stage: Prepare the transition material. In this domain the work is drafting, because Module 1 has no integration and the item is moved by people.

## Purpose
Turn the Route candidate into drafts a human can review, edit and send. Act produces text and blanks. It changes nothing in the tracker, sends nothing and does not move the item.

## Entry conditions
- A Route record exists in this run with a candidate transition and autonomy level `draft`.
- If the level is `stop`, refuse and return to the human with what Route said is missing.

## Required context
- The Route record, and the Context and Intake evidence blocks of this run.
- The transition row in `lifecycle.md` (required evidence, approving role).
- For BLOCKER-01, the question as written in `data/discovery/stakeholder-requests/2026-08-11-tomas-silva.docx`: "I have not seen where the search runs or what data reaches it."

## Prohibited context
- Sending or posting anything. There is no integration in Module 1.
- Filling a recipient, owner, date or channel that no source records. Those stay as blanks for a human.
- Copying an owner from a related field (the tracker lists Tomas Silva as owner of REQUEST-T01, which does not make Tomas Silva the item owner).
- Choosing a wording of POLICY-03 or answering where the search runs. Both are facts held by others (F4).
- Wording that suggests agreement, resolution or approval.

## Procedure
1. Read the candidate transition from the Route record.
2. Draft the material for that transition only:
   - T1: no request. Only the record line in step 3.
   - T2: a proposal asking the product decision role to designate an item owner. Fields: who designates, when, who is designated. All left blank.
   - T3, T4, T13: a request. Content: the pending question recorded in the 2026-08-11 request. Recipient, date and channel: blank, marked "[human to fill]".
   - T6: an escalation note, only if a target role is named by a human. If none is named, draft nothing and say why.
   - T7, T9, T10, T14: an evidence checklist of what the policy owner must provide, for example the three items required by T9. "Who produces it": unknown.
   - T11, T12: a short note of the reason or the two sources, for the named roles to complete.
3. Draft the transition record line (fields in `lifecycle.md`). Leave `approved_by` and `evidence` pointers that do not exist yet empty.
4. Mark every draft "DRAFT, not sent". List each blank and the person or role who could fill it.
5. Append the Act evidence block to `traces/worked-case.md`, under "Stage evidence".

## Evidence produced
Act evidence block: the drafts, each marked "DRAFT, not sent"; list of blanks with who could fill them; a statement that nothing was sent and nothing was changed.

## Proposed transition
None. The state is unchanged. Next stage: `verify`.

## Stop or escalation conditions
- The autonomy level is `stop`: refuse.
- The draft would need a fact nobody recorded (a recipient, a date, an owner, a transfer basis): leave a blank and say so. Do not infer.
- A request to send the draft: refuse and hand the draft to a human.
- A request to draft for a transition that is not the Route candidate: refuse and send back to `route`.

## Human judgment boundary
A human sends any request and decides recipient, channel and wording on policy matters. The product decision role designates owners and escalation targets (Ana Fialho is a declared assumption). A follow-up counts toward the retry limit only after a human records its date, recipient and content. This skill never states that anything was sent or approved.
