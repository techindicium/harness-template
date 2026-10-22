# Lifecycle worksheet

Conventions in this document:

- Unknown dates appear as "unknown". No date was estimated.
- Today's date is 2026-10-21 (session date). Elapsed days are computed only when both dates are recorded in the source.
- Every fact about the case cites file and field, relative to the `portwell-product-1` repository (read-only). Citations were checked directly against the sources on 2026-10-21.
- The author is Thomaz, the only participant of Grupo 3. "Author decision" means a decision taken by the author, working with Claude Code.
- A stage is a step of the procedure that every transition attempt goes through. A state is where the item is. A flag is a condition that can coexist with any state.

## Selected work item

| Field | Value |
| :- | :- |
| Track | PDLC (Product Development Lifecycle) |
| Process | A product decision is made (README.md, track table) |
| Work item | BLOCKER-01, "POLICY-03 sign-off for LATAM accounts", type `blocker`, status `open`, opened 2026-07-11, last touched 2026-08-22 (data/product-tracker.xlsx, row 9, columns B, C, D, F, G) |
| Intended outcome | Move BLOCKER-01 through the lifecycle as far as the evidence allows. The business outcome the lifecycle represents is RESOLVED: documented transfer basis, written approval from the policy owner and the set of covered accounts, all with source and date. Today that outcome is not reachable (see "Terminal states"). |
| Current owner | Unknown. Owner field is empty (data/product-tracker.xlsx, E9). Tomas Silva is the owner of REQUEST-T01 (tracker, E12), of checklist item 3 (data/launch/launch-readiness-checklist.xlsx, C8) and of POLICY-03 (docs/Policies.docx). No source says who owns the blocker as a pending task. Conflict recorded in "Findings", F1. |

## Current process

Timeline of BLOCKER-01 as the sources record it. "Unknown" means no source in the repository says.

| Step | Actor | System or artifact | Input | Output | Decision | Evidence | Problem or unknown |
| -: | :- | :- | :- | :- | :- | :- | :- |
| 1 | Ana Fialho | data/discovery/OPPORTUNITY-04-expand-the-portal-pilot.docx (2026-06-18) | Request to expand the pilot | The brief lists "A data protection position for the LATAM accounts" under "What we would need" | None recorded | Brief text | No owner and no deadline for this item. Brief "Last revised: 2026-06-18", never revised (Ana Fialho herself says it is out of date: docs/interviews/2026-08-12 Ana Fialho). |
| 2 | Ana Fialho, Kofi Adjei | data/discovery/portal-expansion-design.docx (2026-07-09, draft) | OPPORTUNITY-04 | Expansion design | None recorded | Document | The text does not mention LATAM, region or where the search runs. "Circulated 9 July, no comments received". |
| 3 | Unknown | data/product-tracker.xlsx (row 9) and checklist (item 3) | Unknown | BLOCKER-01 open, Owner empty | Unknown | "Opened 2026-07-11" (tracker F9). "Open since 2026-07-11" (checklist E8) | Who opened it and why on that date: unknown. The interval from 2026-06-18 to 2026-07-11 has no record. |
| 4 | Ana Fialho | Unknown | Missing sign-off | Three follow-ups to Tomas Silva | None recorded | "Asked three times" (tracker H9). "Three, so far" (docs/interviews/2026-08-12 Ana Fialho) | Dates, channel, recipient, content and replies: unknown. They count as "3 claimed, 0 recorded". |
| 5 | Ana Fialho | data/decisions/DECISION-0028-pilot-scope-change.docx (2026-08-07) | OPPORTUNITY-04 and "Verbal confirmation from engineering" | Pilot extended from 12 to 28 accounts, as a "scope change" | Approver: Ana Fialho | The record. Constraints: "POLICY-03 data protection position for LATAM accounts remains open with Tomas Silva" | Tracker D6 marks it `done` with the constraint open. Review "alongside the launch readiness assessment", which is `In Progress` (tracker D14). |
| 6 | Tomas Silva, Legal and Data Protection | data/discovery/stakeholder-requests/2026-08-11-tomas-silva.docx and REQUEST-T01 (tracker, row 12) | Proposed expansion | Written request: "I have not seen where the search runs or what data reaches it. Until I do I cannot sign off on those accounts." | Does not approve the LATAM accounts of the expansion. EU and NA accounts "are not affected" | Written request | The question has no recorded recipient. REQUEST-T01 carries the note "Same as BLOCKER-01" (H12) and Opened 2026-08-11 (F12), one month after 2026-07-11. Last touched of REQUEST-T01: empty (G12). |
| 7 | Ana Fialho, interviewed by Mei Tan | docs/interviews/2026-08-12 Ana Fialho, how decisions happen.docx | Question about the blocked-sign-off process | "I ask him again." "There is no next step. I do not have anyone to escalate to, because the person I would escalate to is the person waiting." | None | Interview | The last sentence is ambiguous and this document does not interpret it. The interviewer's note says "Ask Tomas directly". Whether that was done: unknown. |
| 8 | Ana Fialho | data/discovery/stakeholder-requests/2026-08-13-ana-fialho.docx and REQUEST-A01 | Need for a decision on the expansion | Request for a decision "before the end of August" | None | Written request. Tracker H13: "Now overdue" | The date of the "Now overdue" note is unknown. |
| 9 | Unknown | data/product-tracker.xlsx G9 | Unknown | Last touch on 2026-08-22 | Unknown | Cell G9 | What changed on 2026-08-22: unknown. The note still reads "Asked three times". |
| 10 | Ana Fialho (owner of the spreadsheet) | data/launch/launch-readiness-checklist.xlsx (2026-08-26) | Item 3 | "Data protection position for LATAM accounts", owner Tomas Silva, Done `No` | None | "Open since 2026-07-11" (E8). "Ready to launch when every row reads Yes." (A17) | Items 5 and 9 are also `No`. What a tick means: "somebody believed the item was done" (data/README.md). |
| 11 | No one on record | None | None | None | None | No record from 2026-08-26 to 2026-10-21 | Days since opening depend on a disputed date (F3): 102 days if 2026-07-11 holds, 71 days if 2026-08-11 holds, neither chosen. 60 days since the last touch (2026-08-22, tracker G9), computed from the tracker date. Activity outside the repository: unknown. |

### Process as described versus what the records show

| What docs/How we work today.docx says (2025-11-04, "Last revised: never") | What the records show |
| :- | :- |
| "Legal agrees where there is a data protection angle." | DECISION-0028 has only Ana Fialho as approver, with the Legal position open. |
| "In practice agreement means nobody objected in the meeting." | Tomas Silva objected in writing on 2026-08-11, after the decision of 2026-08-07. |
| "The launch readiness checklist, before anything ships." | There is a `done` decision that widens the pilot with the checklist incomplete (item 3 `No`). Whether the 16 accounts are already active: unknown. |
| "Decision records, when somebody is likely to be annoyed later." | BLOCKER-01 has no decision record and no record of follow-ups. |
| "When something is blocked: Ask again. There is no defined next step and no escalation path." | Confirmed by the Ana Fialho interview. It is the current process and it is where the item stopped. |

### Findings (unresolved)

Recorded side by side. This document does not choose between sources.

| # | Conflicting fact | Version A | Version B | Effect on the model |
| -: | :- | :- | :- | :- |
| F1 | Owner of the blocker (contradiction 3.1) | Owner empty (tracker E9) | Tomas Silva is the owner of REQUEST-T01 (E12), of checklist item 3 (C8) and of POLICY-03 (Policies.docx) | FACTS_IN_DISPUTE flag on the "item owner" field. The model separates "item owner" from "policy owner" and does not copy Tomas Silva's name into the empty field. |
| F2 | Who is waiting for whom (contradiction 3.2) | Ana Fialho: the sign-off from Tomas Silva is open and she follows up (Ana Fialho interview: "That has been open since July", "I ask him again") | Tomas Silva: waiting to see where the search runs and what data reaches it (2026-08-11-tomas-silva.docx) | WAIT_CONTESTED flag. State AWAITING_RESPONSE keeps both claims, each with its source. |
| F3 | Start of the blocker (contradiction 3.3) | 2026-07-11 (tracker F9, checklist E8) | 2026-08-11 (REQUEST-T01, tracker F12, note "Same as BLOCKER-01") | FACTS_IN_DISPUTE flag on the "opening date" field. The sources do not say whether it is an error, two events or something else. |
| F4 | Text of POLICY-03 (contradiction 3.4) | "Customer data leaving the EU region requires a documented transfer basis." Owner: Tomas Silva (Policies.docx, maintained by Ana Fialho, reviewed 2026-06-02) | "POLICY-03 requires a documented transfer basis where customer data is processed outside the region it originates in." (request from Tomas Silva, 2026-08-11) | FACTS_IN_DISPUTE flag on the applicability criterion. Blocks T9. Trigger, region reference and unit ("leaving" versus "processed") differ. |
| F5 | State of DECISION-0028 (contradiction 3.5) | Tracker D6: `done` | The record itself: POLICY-03 constraint open and review pending | BYPASSED_BY_DECISION flag. The model exposes the link and does not alter the decision. Whether POLICY-08 ("beyond 25 accounts requires a documented launch-readiness decision") applies to a "scope change": the sources do not say. |
| F6 | Covered accounts | OPPORTUNITY-04 and DECISION-0028: 12 accounts in the pilot | EXPERIMENT-02: six accounts (data/experiments/EXPERIMENT-02-design-and-result.docx, Method: "Six accounts, six weeks"; data/experiments/EXPERIMENT-02-results.xlsx, rows 5 to 10 list six accounts) | Not necessarily a conflict. The set of covered LATAM accounts is "unknown": no source lists accounts by region and the 16 accounts added "selected by account manager request" are not listed. |

Conflicts 3.6 (start of the readiness work) and 3.7 (support review capacity) belong to other items (LAUNCH-01, REQUEST-R01) and stay outside this model, as links only.

## Proposed lifecycle

### How to read the model

There are two levels, and the distinction matters:

1. **States and flags describe the item.** BLOCKER-01 is always in exactly one main state and can carry several flags.
2. **Stages describe the procedure.** Each attempt to change the item's state (a transition, T1 to T14) goes through Intake, Context, Route, Act, Verify, Approve, Handoff and Observe, with Recover as a detour when something fails. One skill per stage.

Stages are not states. The item returns to the start of the procedure on each new transition attempt.

Author design decision, **not confirmed with the instructor**: mutually exclusive main states plus flags, instead of exclusive states only. Reason: the trace shows BLOCKER-01 unowned, duplicated, stalled, bypassed by a decision and with conflicting facts all at the same time (context/trace-blocker-01.md, section 4). If the instructor requires exclusive states only, each flag would become a composite state.

### Stages

The "Item state" column is the extra column that maps each stage to a state.

| Common stage | Track-specific state | Entry conditions | Evidence produced | Next states | Owner | Stop or escalation condition | Item state (stage-to-state mapping) |
| :- | :- | :- | :- | :- | :- | :- | :- |
| Intake (`skills/intake`) | Register the blocker | The item has an existing identifier in the tracker (never renumbered) or a new request arrives. The item is not terminal. | T1 record line: description, who opened it, origin of the requirement. Fields without a source stay "unknown" and raise the ORIGIN_OR_DATE_UNKNOWN flag. | Context. Proposed state: OPEN_UNOWNED (T1) | Skill prepares. Tracker maintainer approves T1. | Stops if there is no identifier, if the item is already terminal, or if someone asks to renumber. | Produces OPEN_UNOWNED. Reads any non-terminal state. |
| Context (`skills/context`) | Gather sources and conflicts | Item registered. | List of sources with file, field, internal date (or "unknown") and age. Conflicts side by side. Proposed flags. | Route | Skill. No approval. | Stops any transition that depends on a fact that is stale, superseded, without an identifiable source or in conflict. The conflict is recorded and the fact is not chosen. | Does not change the state. Proposes flags. |
| Route (`skills/route`) | Choose the candidate transition | Context gathered. | Route record: candidate transition (T#), autonomy level, human decision point, what is missing. | Act, Approve (when only a decision is missing), Recover | Skill proposes. A human confirms the route when there is more than one candidate. | Stops if no permitted transition applies, or if the choice depends on deciding between conflicting sources. | Reads the state. Does not change it. |
| Act (`skills/act`) | Prepare the transition material | Route chosen. | Drafts: request to the recipient (with the question from Tomas Silva about where the search runs and what data reaches it), owner assignment proposal, draft of the record line. Nothing is sent. | Verify | Skill drafts. A human sends. | Stops if the draft would require writing a fact nobody recorded, or if the step would require sending a message (no integration in Module 1). | Does not change the state. |
| Verify (`skills/verify`) | Check the transition evidence | Act material ready. | Result per evidence requirement of the transition: present, absent or in conflict, with a pointer to file and field. Elapsed days only with two recorded dates. | Approve (all present), Recover (any absent or in conflict) | Skill. No approval. | Stops if any required evidence is missing. In T9, if the transfer basis, the written approval or the set of covered accounts is missing, or if FACTS_IN_DISPUTE is active on the wording of POLICY-03 or on the accounts. | Does not change the state. |
| Approve (`skills/approve`) | Record the role's decision | Verify with no pending item. | Decision record: role, person, date, form and pointer to the evidence. A simulated answer carries `simulated: true`. | Handoff (approved), Recover (denied or no decision) | The role the transition indicates ("Who approves" column of the transitions). | Stops without a person, role or date. Refuses a "yes" without evidence and an approval from a role that is not the indicated one. Never approves on its own. | Does not change the state. |
| Handoff (`skills/handoff`) | Write the transition and communicate | Verify PASS and an Approve record (real, or marked `simulated: true`) for the same transition in this run. Every transition in the table names an approver, so none is exempt. | Line appended to the transition log (see "How a transition is recorded") and a communication prepared for the affected role. | Observe. New state: the one of the transition | Skill writes. A human sends the communication. | Stops without a recorded approval. Refuses to edit an earlier line: a correction is a new line. | Produces the new state. |
| Observe (`skills/observe`) | Inspect the outcome | Transition written. The item is not terminal. | Report: was a response recorded? attempt counter. Days without touch, only with recorded dates. | Route (new round), Recover | Skill. | Stops if the item has not yet gone through Handoff, or if it is already terminal (nothing to observe). | Reads the state. Proposes T5 or T13 but does not execute them. |
| Recover (`skills/recover`) | Retries, stall and escalation | Verify failed, Approve was denied, retry limit reached, deadline exceeded, conflict over a needed fact, or an owner or target is missing. | Failure record: cause, counter of recorded attempts, flags, proposed transition (T5, T6, T13 or none). | STALLED, ESCALATED, AWAITING_RESPONSE or the current state | Item owner confirms T5. Product decision role approves T6. | Stops when escalation is required and no escalation target role exists. Raises ESCALATION_REQUIRED_NO_TARGET and asks for a human decision. | Proposes STALLED or ESCALATED. Never marks a terminal state. |

### States

**Main states** (mutually exclusive):

| State | Definition | Origin of the definition |
| :- | :- | :- |
| OPEN_UNOWNED | The item exists and no owner assignment has been recorded. | Observed: tracker D9 `open`, E9 empty |
| OPEN_OWNED | An owner assignment has been recorded for the item. | Anticipated, no source shows it |
| AWAITING_RESPONSE | A recorded request (date, recipient, content) is waiting for an answer. Keeps who claims to be waiting for whom, each claim with its source. | Observed claims (F2). Formal entry requires T3, which BLOCKER-01 does not meet. |
| IN_ANALYSIS | The policy owner has received the requested information and is evaluating it. | Anticipated |
| STALLED | The item is still open with no recorded action beyond the agreed limit. | Observed as a description (Ana Fialho: "There is no next step"; 60 days without touch). Formal entry requires T5, which is not computable today (see "Failure and recovery"). |
| ESCALATED | Forwarded, with a record, to a role above the current chain. | Anticipated |

**Flags** (can coexist with any main state):

| Flag | Definition | Evidence |
| :- | :- | :- |
| LINKED_DUPLICATE | Another item claims to be the same one. The link is recorded and no primary is chosen. | REQUEST-T01, tracker H12 |
| FACTS_IN_DISPUTE | Two sources give different values for a fact the item depends on. Both are kept side by side. | F1, F3, F4 |
| WAIT_CONTESTED | Two parties each claim to be waiting for the other. | F2 |
| BYPASSED_BY_DECISION | A decision was made while this item was open. | DECISION-0028, tracker D6 |
| ORIGIN_OR_DATE_UNKNOWN | A required field has no recorded value and stays "unknown". | Steps 3, 4 and 9 of the current process |
| ESCALATION_REQUIRED_NO_TARGET | The escalation condition was reached and no target role exists. | Anticipated. Ana Fialho interview: nobody to escalate to. |

**Situation of BLOCKER-01 today, according to this model** (author reading, not from any source): main state OPEN_UNOWNED, because T2 was never recorded. Flags: LINKED_DUPLICATE, FACTS_IN_DISPUTE (item owner, opening date, wording of POLICY-03), WAIT_CONTESTED, BYPASSED_BY_DECISION, ORIGIN_OR_DATE_UNKNOWN. AWAITING_RESPONSE and STALLED describe what the sources report, but T3 and T5 cannot be recorded for lack of evidence.

### Transitions

For each transition: required evidence, approving role and what happens if the evidence is missing. Rows T13 and T14 were added in this document and are not in the proposal in context/proposta-estados.md. T5 was widened (see "Design decisions and limitations").

| # | From, to | Required evidence | Who approves (role) | If the evidence is missing |
| -: | :- | :- | :- | :- |
| T1 | (start), OPEN_UNOWNED | Description, who opened it, origin of the requirement | Tracker maintainer | Opens with ORIGIN_OR_DATE_UNKNOWN. Nothing is filled in by estimate. |
| T2 | OPEN_UNOWNED, OPEN_OWNED | Record of who assigned, when and who was assigned | Product decision role | Stays unowned. The name of a related owner is not copied from another field. |
| T3 | OPEN_OWNED, AWAITING_RESPONSE | Recorded request, with date, recipient and content | Item owner | Without recipient or without date, the request stays "claimed, not recorded" and does not count toward the limit. |
| T4 | AWAITING_RESPONSE, AWAITING_RESPONSE | New recorded attempt, which increments the counter | Item owner | The attempt does not count. |
| T5 | OPEN_UNOWNED, OPEN_OWNED or AWAITING_RESPONSE, to STALLED | Counter at the limit with no recorded response, or maximum days without touch exceeded, with recorded dates | Item owner confirms. With no owner, the product decision role confirms. The machine only proposes. | Without recorded dates, or without a defined maximum, the machine reports "not computable" and nothing changes. |
| T6 | STALLED, ESCALATED | Record of the forwarding: target role, date, content | Product decision role | Without a defined target, the item stays STALLED with ESCALATION_REQUIRED_NO_TARGET. |
| T7 | AWAITING_RESPONSE, IN_ANALYSIS | Response document or message, with source and date | Policy owner (who asked for the information) confirms it is what was asked | Stays awaiting. |
| T8 | ESCALATED, AWAITING_RESPONSE or IN_ANALYSIS | Recorded response from the target role | Escalation target role | Stays ESCALATED. |
| T9 | IN_ANALYSIS, RESOLVED | (a) Documented transfer basis, (b) written approval from the policy owner (POLICY-03), (c) recorded set of covered accounts, all with source and date | Policy owner (POLICY-03) | No transition. A "yes" without evidence does not count (data/README.md: a tick means "somebody believed the item was done"). With FACTS_IN_DISPUTE active on the wording of POLICY-03 or on the accounts, T9 does not happen. |
| T10 | IN_ANALYSIS, DECLINED | Written refusal with a reason | Policy owner | No transition. |
| T11 | Any non-terminal, CANCELLED | Written reason that the item no longer applies | Product decision role | No transition. |
| T12 | Any non-terminal, MERGED | Record that the items concern the same fact, citing both sources | Tracker maintainer and policy owner | Keeps only the LINKED_DUPLICATE flag. |
| T13 | STALLED, AWAITING_RESPONSE | New recorded attempt (date, recipient, content) | Item owner | The attempt does not count and the item stays STALLED. |
| T14 | IN_ANALYSIS, AWAITING_RESPONSE | Record that the information received is insufficient and what is missing, with date | Policy owner | Stays IN_ANALYSIS. |

### Roles and the source of each

| Role | Who, according to the sources | Note |
| :- | :- | :- |
| Tracker maintainer | Ana Fialho ("Kept by Ana Fialho", data/product-tracker.xlsx A2) | The source says "Kept by". Reading that as the tracker maintainer role is the author's plain reading of the header. |
| Product decision role | "The product lead decides" (docs/How we work today.docx). Ana Fialho is VP Product (data/people/headcount.xlsx, row 4). | Declared assumption, not a fact: that Ana Fialho is the "product lead". To be confirmed. |
| Policy owner (POLICY-03) | Tomas Silva (docs/Policies.docx). "Legal and Data Protection" (2026-08-11-tomas-silva.docx). | Tomas Silva is not listed in data/people/headcount.xlsx, a spreadsheet that declares itself "the record for anything contractual". Reporting line: unknown. |
| Item owner (BLOCKER-01) | Unknown (F1) | The model keeps this role separate from the policy owner. The separation is a author inference and does not resolve F1. |
| Escalation target role | Does not exist (Ana Fialho interview) | Unknown today. |
| Fact authority | Not a named person. The human with authority over a disputed fact. | For F4 the policy owner (Policies.docx lists Tomas Silva as the owner of POLICY-03). |

## Human judgment boundaries

Points where the machine stops and asks for a human decision. The machine never decides any of them.

| Decision | Why it is not mechanical | Decision owner | Evidence prepared by a skill |
| :- | :- | :- | :- |
| Declare a disagreement resolved | Ana Fialho: something that smoothed it over "would look like agreement" (Ana Fialho interview). Rui Bastos: "considering it is not the same as fixing it" (docs/interviews/2026-08-19 Rui Bastos, what the pilot showed.docx, last answer). | Fact authority | Conflict side by side, with both sources (Context) |
| Choose between two sources that contradict each other | The product repository's CLAUDE.md forbids picking the more plausible version. | Fact authority (for F4, the policy owner) | Updated Findings table (Context) |
| Estimate an unknown date | An unknown date is information. | No one. The date stays "unknown" until someone records it. | Field marked "unknown", with the question of who could record it (Context) |
| Assign the item owner or the escalation target | No source defines who can be owner and the target does not exist today. | Product decision role (assumption to be confirmed) | Assignment proposal and list of what is missing (Act) |
| Mark RESOLVED, DECLINED, CANCELLED or MERGED | Terminal states have no exit. RESOLVED requires T9. | RESOLVED and DECLINED: policy owner. CANCELLED: product decision role. MERGED: tracker maintainer and policy owner. | Verify result with each requirement marked present, absent or in conflict |
| Decide that BLOCKER-01 and REQUEST-T01 are the same item | Today this comes only from the tracker note (H12). One is `blocker` and the other is `request`. | Tracker maintainer and policy owner (T12) | The two tracker rows and the difference in dates (Context) |
| Decide whether DECISION-0028 should be revisited or whether POLICY-08 applies | "Whether either incident should block expansion. Nobody has been asked to decide." (docs/incidents/Pilot incidents, product view). | Unknown. The decision belongs to Ana Fialho as approver of DECISION-0028, but who should decide whether it applies is not in the sources. | Link exposed by the BYPASSED_BY_DECISION flag (Context) |
| Send any request or communication | Module 1 has no integration. A follow-up only counts if it has a date, a recipient and content. | Item owner, or the role that sends it | Draft of the request (Act) |
| Confirm that an attempt counts toward the limit | The three current follow-ups are "claimed, not recorded". | Item owner | Separate counter: "3 claimed, 0 recorded" (Recover) |

The machine can: detect and list conflicts, signal conditions, count recorded attempts and compute elapsed days when both dates are recorded.

## Failure and recovery

| Failure or blocked state | Detection signal | Recovery path | Retry limit | Escalation owner |
| :- | :- | :- | :- | :- |
| OPEN_UNOWNED | Item open with no recorded assignment (tracker E9 empty) | T2: assignment recorded and approved by the product decision role | Not applicable (no attempt to count) | Product decision role |
| AWAITING_RESPONSE with no response | Counter of recorded attempts at the limit, with no recorded response | T5 (proposed by the machine, confirmed by the item owner), then T6 | 3 recorded attempts. Value proposed by the author and not validated: the only number in the sources is the "three" from Ana Fialho (tracker H9, Ana Fialho interview), which shows three follow-ups and does not show that three is the right limit. | Unknown. The escalation target does not exist. |
| Maximum days without touch exceeded | Days since the last touch above the maximum, with both dates recorded | T5 | Maximum days without touch: **unknown**. To be defined by the author with Ana Fialho. Until then the machine answers "not computable". The 60 days without touch are an observed fact and do not trigger T5. | Unknown |
| STALLED | T5 confirmed | New recorded action (T13) or escalation (T6). Does not close on its own. The warning stays active. | Same counter | Product decision role |
| ESCALATED with no response | T6 recorded, no reply | Recorded response from the escalation target role (T8). The target's deadline is flagged. | Target's deadline: unknown | The escalation target role itself |
| FACTS_IN_DISPUTE | Two sources conflict on a fact the item depends on | The fact authority records the chosen value and the reason, or records "remains in conflict". Meanwhile T9 does not happen. | Not applicable | Fact authority |
| Missing evidence in Verify | Transition requirement absent | Recover records what is missing and stops the transition. Nothing is filled in by estimate. | Each new attempt only counts if recorded with date, recipient and content | Item owner |
| Escalation required with no target | Condition of T6 reached and no target role recorded | ESCALATION_REQUIRED_NO_TARGET flag. The machine stops and asks for a human decision. | Not applicable | Product decision role (assumption to be confirmed). Ana Fialho says the natural target "is the person waiting". Ambiguous sentence, not interpreted. |
| Stale, superseded or unidentifiable input | Context finds no source or finds a superseded one (example: POLICY-10, superseded by POLICY-11 on 2026-07-01, cited in checklist item 6) | Context records it and the transition that depends on it does not proceed | Not applicable | Fact authority |

**Escalation condition:** fires when the limit of recorded attempts is reached, or when the maximum days without touch is exceeded (with both dates recorded). Today the second part is "not computable" and the target does not exist.

## How a transition is recorded

The smallest thing that records a transition is one line appended at the end and never edited. Fields:

| Field | Content |
| :- | :- |
| item | Existing identifier, not renumbered |
| from, to | Origin state and destination state |
| recorded_at | Date and time of the record. If the date of the fact is different and unknown: "unknown" |
| recorded_by | Person and role. When the record is made by a skill: the name of the skill |
| approved_by | Role and person, when the transition requires it. A simulated answer carries `simulated: true` |
| evidence | Pointer to file and field, or "verbal, not recorded" marked as such |
| reason | One sentence |
| versions | Both versions and sources, when there is a conflict |

A correction is a new line. Reason: INCIDENT-01, "Nobody wrote down who changed it or when" (docs/incidents/INCIDENT-01 superseded refund window.docx, section "What was done afterwards").

Author decision: the log is a new file, `traces/transition-log.md`, append-only. It is never edited, and a correction is a new line. The `handoff` skill writes to it.

## Terminal states

Terminal states have no outgoing transition. Reopening is a new item linked to the previous one, to preserve the record. This rule is the author's, not from the sources (Policies.docx only says that a decision that reverses another references it "sometimes").

| State | Business outcome represented | Required final evidence |
| :- | :- | :- |
| RESOLVED | The policy owner approved the covered accounts in writing, with a documented transfer basis | Documented transfer basis, written approval from the policy owner, set of covered accounts, all with source and date. Today the set of accounts is "unknown", so RESOLVED is not reachable. |
| DECLINED | The policy owner refused in writing | Written refusal with reason, source and date |
| CANCELLED | The item no longer applies | Written reason by a human in the product decision role |
| MERGED | The item was absorbed into another by human decision. The identifier is not renumbered, only linked. | Record that the items concern the same fact, citing both sources, with the approvals of T12 |

EXPIRED is not a terminal state. No source says that blockers expire, and closing by elapsed time would make an unresolved blocker look closed.

## Design decisions and limitations

- Main states plus flags is a author decision and was **not confirmed with the instructor**.
- Changes relative to context/proposta-estados.md: extra column mapping stage to state; T5 widened to leave OPEN_UNOWNED and OPEN_OWNED (the proposal described this exit in its text but its transition table did not cover it); T13 and T14 added (the proposal said STALLED exits by a "new recorded action" and that IN_ANALYSIS may need more information, with no corresponding transition); roles tied to sources; citations checked against the sources.
- Attribution correction relative to the earlier trace: the sentence "Tomas has not signed off" is from Mei Tan in the interview. Ana Fialho answers "No. That has been open since July." The content of F2 does not change.
- The maximum days without touch is "unknown". Because of that, the machine cannot propose STALLED (T5) for BLOCKER-01, even with 60 days since the last touch (tracker G9 to the session date 2026-10-21). This is an accepted limitation, not a defect to fix.
- The product decision role is Ana Fialho as a declared assumption, not a fact.
- The transition log, `traces/transition-log.md`, is a author decision. It is append-only, and a correction is a new line.
- Author decision: each skill appends its evidence block to `traces/worked-case.md`, under a "Stage evidence" section. Only the `handoff` skill writes to `traces/transition-log.md`.
- Author decision: the autonomy levels `draft` (skills may prepare material, nothing changes state without a recorded human approval) and `stop` (nothing can be prepared, hand to a human) are the author's definition. They do not come from the sources.
- The source list in the `context` skill covers BLOCKER-01 only. Another item would need its own list.
- The `verify` skill checks that required evidence exists, not that it is sufficient. What counts as a "documented transfer basis" is an open question for Tomas Silva (Policies.docx does not define it).
- The evidence checklists drafted by the `act` skill are the author's interpretation of what the policy owner must provide. "Who produces it" stays "unknown".
- The retry limit of 3 recorded attempts is a author hypothesis, not validated.
- Author decision: a transition written with `simulated: true` is a demonstration line. When the last line of the log for an item is simulated, the state read from it is reported as "simulated state" and is not the real state of the item.
- Author decision: the header row of `traces/transition-log.md`, written by the first `handoff` run, is the only exception to "append-only". After it, no line is ever edited, deleted or reordered.
- Missing controls, noted only as observations (Modules 2 and 3, not built here): mandatory owner per blocker; a record of each follow-up with date, recipient and response; a deadline and an escalation path; a link between blocker and decision (DECISION-0028 `done` with an open constraint); verification of policies ("Nothing checks any of them", Policies.docx); detection of duplicates and of divergence between spreadsheets; flagging of stale evidence; an age warning for documents without a review date.
- An executable stop: today every stop depends on a person following the skill (Modules 2 and 3, not built).
- Possible future change, not adopted: raise ESCALATION_REQUIRED_NO_TARGET also when a human requests escalation and no target exists. The design as written does not represent that case (see traces/worked-case.md, B4).
- Each transition is prompt-level (a written procedure). Nothing prevents a person from editing the tracker directly.

## Open questions

- Retry limit of three attempts and maximum days without touch: validate with Ana Fialho. The maximum is **unknown**.
- Who receives an escalation? Ana Fialho says the natural target "is the person waiting". Tomas Silva is not in headcount.xlsx.
- Which wording of POLICY-03 holds (F4)? Question for Tomas Silva.
- What counts as a "documented transfer basis" and as an "approval": form, content and who may give it. Policies.docx does not define them. Is the approval per account, per region or per another unit? Question for Tomas Silva.
- Does POLICY-08 apply to a "scope change"? Should DECISION-0028 be `done` with the constraint open? Question for Ana Fialho.
- Is there an exception flow to POLICY-03 ("accepted with risk")? No source describes it and it was not included. If it exists, it changes the list of terminal states.
- Are main states plus flags accepted, or does Module 1 require exclusive states? Question for the track assistants.
- The role names ("policy owner", "product decision role", "tracker maintainer") need to be confirmed. How we work today.docx speaks of "product lead", "Support" and "Legal".
- Is there a list of accounts by region outside the repository? Without it, "covered accounts" stays "unknown".
- Activity outside the repository (email, chat, meeting) may explain the 60 days with no record and the three follow-ups. None was consulted.
- Who opened BLOCKER-01, why on 2026-07-11 and what changed on 2026-08-22: unknown.
