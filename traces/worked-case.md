# Worked lifecycle case

## Case

| Field | Value |
| :- | :- |
| Work item | BLOCKER-01, "POLICY-03 sign-off for LATAM accounts" (data/product-tracker.xlsx, row 9) |
| Intended outcome | Move BLOCKER-01 through the nine skills as far as the evidence allows. The business outcome the lifecycle represents is RESOLVED, which needs a documented transfer basis, written approval from the policy owner and the set of covered accounts. |
| Starting state | No line in `traces/transition-log.md`. Intake proposes OPEN_UNOWNED (tracker D9 `open`, E9 empty). |
| Final state | **Simulated state: OPEN_UNOWNED** (one demonstration transition, `simulated: true`, plus one correction line). No real transition has been recorded. RESOLVED is not reachable today. |

## How this run was executed

- Date of the run: 2026-10-21. The approval record (A6) and the log were corrected on 2026-10-22. The author is Thomaz, the only participant of Grupo 3, and the run was done with Claude Code. Sources were read from `C:\Users\thomaz.picelli_indic\portwell-product-1`, read-only. That repository shows no changes after the run.
- Each skill was executed by hand by Claude, following the procedure in its `SKILL.md`, in a Claude Code session. The skills were not run by an engine and no tool enforced a stop. The stops below are the skills' own rules applied by the executor.
- Two runs. **Run A** takes the item through T1, the only transition the item can attempt from its starting state. **Run B** takes a request to mark the item RESOLVED. That request was supplied by the author running the trace as a test input, and it is not a decision of any role.
- Source text was extracted with read-only scripts over the `.docx`, `.xlsx` and `.md` files, and over the slide text of the one `.pptx` file (`data/discovery/sales-deck-2025.pptx`, 4 parts, no hit). Text inside images or embedded objects was not searched.
- Done by hand rather than by a skill: the extraction scripts and the searches; the edits to the skills listed under "Execution findings"; writing the evidence blocks and the log line (the `handoff` and the other skills are procedures, not programs).

## Trace

| # | Skill invoked | Context read | Evidence produced | Proposed state | Result | Human intervention |
| -: | :- | :- | :- | :- | :- | :- |
| A1 | intake | Tracker rows 9 and 12 | Intake block, T1 line drafted | OPEN_UNOWNED (T1) | Done. Owner, who opened, origin: "unknown". REQUEST-T01 linked, not merged. | None |
| A2 | context | 13 sources, listed in the Context block | Source table, F1 to F5, flags, blocked transitions | None (state unchanged) | Done. Conflicts recorded, none chosen. | None |
| A3 | route | Intake and Context blocks | Route record | T1, level `draft` | Done | None |
| A4 | act | Route record | T1 record line draft, "DRAFT, not sent" | None | Done. Blanks left for a human. | None |
| A5 | verify | Tracker row 9, Context block | Verify report for T1 | None | PASS with ORIGIN_OR_DATE_UNKNOWN | None |
| A6 | approve | Verify report, session message | Approve record | None | Approved, **simulated: true**. Exact words recorded on 2026-10-22. | Thomaz, the only participant of Grupo 3, in the tracker maintainer role for the demonstration |
| A7 | handoff | Verify report, Approve record, empty log | Header and line 1 of `traces/transition-log.md`, draft notice. Line 2 (correction, 2026-10-22). | OPEN_UNOWNED (simulated state) | Written. Line 2 corrects the approver's words, no new transition. | None |
| A8 | observe | Log line 1, tracker G9 | Observe report | None | No recorded response, 0 recorded attempts, maximum "not computable" | None |
| B1 | route | Context block, `lifecycle.md` | Route record for the request "mark RESOLVED" | None | **REFUSED**: no transition from OPEN_UNOWNED to RESOLVED | None |
| B2 | verify | Whole text of the track repository, Context block | Verify report for T9, called by hand | None | **FAIL**: T9 refused | None |
| B3 | recover | Verify B2, tracker H9, Ana Fialho interview | Failure record | None | T5 **not computable**, no state change | None |
| B4 | recover | Failure record B3, Ana Fialho interview | Finding | None | ESCALATION_REQUIRED_NO_TARGET **cannot be raised today** | Thomaz chose to keep the rule as written (option B) |

## Stage evidence

### A1. intake

Context read: `data/product-tracker.xlsx`, rows 9 and 12 only.

| Field | Value (tracker cell) |
| :- | :- |
| Item | BLOCKER-01 (A9) |
| What | POLICY-03 sign-off for LATAM accounts (B9) |
| Type | blocker (C9) |
| Status | open (D9) |
| Owner | empty (E9), unknown |
| Opened | 2026-07-11 (F9) |
| Last touched | 2026-08-22 (G9) |
| Notes | "Asked three times" (H9) |

- Bounded outcome: POLICY-03 sign-off for LATAM accounts (B9). Constraints: track repository read-only, no estimated dates, no resolved conflicts.
- Out of scope: revising DECISION-0028, LAUNCH-01, REQUEST-R01, the two pilot incidents.
- Linked duplicate: row 12, REQUEST-T01 (B12 "LATAM transfer basis", E12 Tomas Silva, F12 2026-08-11, G12 empty), note "Same as BLOCKER-01" (H12). Link recorded. Which row is primary is not decided.
- Unknown fields: who opened BLOCKER-01, why on that date, item owner. Proposed flag: ORIGIN_OR_DATE_UNKNOWN.
- Drafted T1 line (not written to the log): item BLOCKER-01, from (start), to OPEN_UNOWNED, approved_by empty.
- Proposed transition: T1, for the tracker maintainer to approve. Next stage: context.

### A2. context

Run date 2026-10-21. Age is computed only from a date written inside the document.

| Source | Field | Internal date | Age (days) |
| :- | :- | :- | -: |
| data/product-tracker.xlsx | rows 9, 12 | Sheet undated (A2: "Updated when someone remembers"). Row 9 last touched 2026-08-22 (G9). Row 12 last touched: empty (G12). | Sheet: unknown. Row 9 touch: 60. Row 12 touch: unknown. |
| data/launch/launch-readiness-checklist.xlsx | A3, row 8 | Last updated 2026-08-26 | 56 |
| docs/Policies.docx | POLICY-03, 08, 10, 11 | Last reviewed 2026-06-02 | 141 |
| docs/How we work today.docx | "When something is blocked" | Written 2025-11-04, "Last revised: never" | 351 |
| data/discovery/stakeholder-requests/2026-08-11-tomas-silva.docx | whole | 2026-08-11 | 71 |
| data/discovery/stakeholder-requests/2026-08-13-ana-fialho.docx | whole | 2026-08-13 | 69 |
| data/decisions/DECISION-0028-pilot-scope-change.docx | Constraints | 2026-08-07 | 75 |
| data/discovery/OPPORTUNITY-04-expand-the-portal-pilot.docx | "What we would need" | Written and last revised 2026-06-18 | 125 |
| data/discovery/portal-expansion-design.docx | whole | 2026-07-09 | 104 |
| docs/interviews/2026-08-12 Ana Fialho, how decisions happen.docx | whole | 2026-08-12 | 70 |
| docs/incidents/Pilot incidents, product view.docx | whole | 2026-08-04 | 78 |
| data/people/headcount.xlsx | Headcount, Notes | Sheet undated | unknown |
| data/README.md | "Reading these" | Undated | unknown |

Not read in this run: EXPERIMENT-02 files (not in the Context list), `SEED-MANIFEST.md`, anything outside the repository. `traces/transition-log.md` did not exist yet.

Conflicts, side by side, none chosen:

| # | Fact | Version A | Version B |
| -: | :- | :- | :- |
| F1 | Owner of the blocker | Owner empty (tracker E9) | Tomas Silva owns REQUEST-T01 (E12), checklist item 3 (C8) and POLICY-03 (Policies.docx) |
| F2 | Who waits for whom | Ana Fialho interview: "That has been open since July", "I ask him again" | Tomas Silva request: "Until I do I cannot sign off on those accounts." |
| F3 | Opening date | 2026-07-11 (tracker F9, checklist E8) | 2026-08-11 (REQUEST-T01, tracker F12) |
| F4 | Wording of POLICY-03 | "Customer data leaving the EU region requires a documented transfer basis." (Policies.docx) | "POLICY-03 requires a documented transfer basis where customer data is processed outside the region it originates in." (Tomas Silva request) |
| F5 | State of DECISION-0028 | `done` (tracker D6) | Constraint "remains open with Tomas Silva" and review pending (DECISION-0028) |

Covered accounts: unknown. The only counts in the sources read are 12 accounts (OPPORTUNITY-04, DECISION-0028) and 28 after DECISION-0028. No source lists accounts by region. The 16 added accounts are "selected by account manager request" and not listed.

Elapsed days: since opening, 102 if 2026-07-11 holds and 71 if 2026-08-11 holds (F3, neither chosen). Since the last touch of row 9: 60. Since the last touch of REQUEST-T01: not computable.

Superseded or unsourced inputs: POLICY-10 is cited in the checklist (row 11) and was superseded by POLICY-11 on 2026-07-01 (Policies.docx). The checklist (row 9) cites `assist-expansion-design.docx`, which is not in the repository file list. Both concern other checklist items.

Proposed flags: LINKED_DUPLICATE (H12), FACTS_IN_DISPUTE (F1, F3, F4), WAIT_CONTESTED (F2), BYPASSED_BY_DECISION (F5), ORIGIN_OR_DATE_UNKNOWN.

Transitions blocked: T9 (F4 and unknown accounts), T5 (maximum days unknown), T6 (no target role), T12 (needs a human decision).

Unknown, and who could record it: who opened BLOCKER-01 and why on that date; item owner (product decision role); dates, channel, recipient and content of the three follow-ups (Ana Fialho); what changed on 2026-08-22; transfer basis and covered accounts (policy owner); escalation target; maximum days without touch (author with Ana Fialho).

Proposed transition: none. Next stage: route.

### A3. route

- Current state: no line in the log. Intake proposes OPEN_UNOWNED, not yet written.
- Candidate: T1 ((start) to OPEN_UNOWNED), the only one for an item with no log line.
- Preliminary check from Context: description present (B9). Who opened: absent. Origin of the requirement: no source records the link between BLOCKER-01 and OPPORTUNITY-04, so absent as a recorded link. OPPORTUNITY-04 does list "A data protection position for the LATAM accounts", so it is a candidate pointer, not a recorded origin.
- Autonomy level: `draft`.
- Human decision point: the tracker maintainer approves T1.
- Next stage: act.

### A4. act

Drafts, all "DRAFT, not sent". T1 needs no request, only the record line.

| Field | Draft value |
| :- | :- |
| item | BLOCKER-01 |
| from, to | (start), OPEN_UNOWNED |
| recorded_at | [set by handoff] |
| recorded_by | handoff skill |
| approved_by | [human to fill: tracker maintainer] |
| evidence | data/product-tracker.xlsx D9, E9 (empty), F9 |
| reason | Item registered. Owner, who opened it and origin of the requirement are unknown. |
| versions | F1 owner: E9 empty versus Tomas Silva as owner of E12, C8 and POLICY-03. F3 opening date: 2026-07-11 versus 2026-08-11. |

Nothing was sent or changed.

### A5. verify (T1)

| Requirement | Status | Pointer | Note |
| :- | :- | :- | :- |
| Description | present | tracker B9 | |
| Who opened it | absent | tracker has no such field | |
| Origin of the requirement | absent (no recorded link) | OPPORTUNITY-04, "What we would need" mentions the need | Link to BLOCKER-01 is not recorded |

- State check: origin is (start). Met.
- Blocking flags: FACTS_IN_DISPUTE concerns owner, opening date and the POLICY-03 wording. T1 does not depend on any of them. Not blocking.
- Rule for T1 ("If the evidence is missing"): the item opens with ORIGIN_OR_DATE_UNKNOWN and nothing is filled in.
- Verdict: **PASS with ORIGIN_OR_DATE_UNKNOWN**. Recommend approve.

### A6. approve (T1)

Decision request, addressed to the **tracker maintainer**. The tracker header says "Kept by Ana Fialho" (data/product-tracker.xlsx A2), which is the author's reading of the role, not a confirmed fact.

Approve record:

| Field | Value |
| :- | :- |
| Transition | T1, (start) to OPEN_UNOWNED |
| Role required | Tracker maintainer |
| Person | Thomaz, the only participant of Grupo 3 |
| Role stated | Tracker maintainer, for the demonstration only |
| Date | The role was assigned on 2026-10-21 (time unknown). The approval sentence was given on 2026-10-22 (time unknown). |
| Form | Written in this session (chat, in Portuguese). Not a document. |
| Exact words | "Como Tracker maintainer, em demonstração, aprovo a transição T1 para o BLOCKER-01." |
| Translation of the words | "As Tracker maintainer, in demonstration, I approve transition T1 for BLOCKER-01." |
| Evidence pointer | None beyond this session |
| simulated | **true** |
| Outcome | approved, as a demonstration |

History of this record. On 2026-10-21 the role was assigned in a chat message ("quem faz o papel de Tracker maintainer em T1 é Thomaz, integrante do Grupo 3 ... Não preencha dono nem data."). The run recorded the approval from that message, which contained no approval sentence, and said so. On 2026-10-22 Thomaz gave the sentence above. The record now uses it as the exact words. The log was corrected by a new line (line 2), because line 1 cannot be edited.

**demonstration, not a real decision of Ana Fialho** (the tracker maintainer per the author's reading of the tracker header). It is also not a decision of Tomas Silva.

Limits of this record. The approval is simulated: the person playing the role is the author, not the tracker maintainer. The dates above are dates of the record, not dates of the item. Owner and the item's own dates were not filled in. Log line 1 still says "the group's reading" in its approved_by cell (an earlier wording that cannot be edited). The reader is the author, who is the only participant. Line 2 uses "the author's reading".

### A7. handoff (T1)

- Checks: Verify PASS for T1 (A5). Approve outcome "approved", `simulated: true` (A6). The log had no line for the item, so `from` matches the state proposed by Intake.
- Wrote `traces/transition-log.md` on 2026-10-21: header row (the only exception to append-only) and **line 1**:
  - item BLOCKER-01, from (start), to OPEN_UNOWNED
  - recorded_at 2026-10-21, time unknown; recorded_by handoff skill
  - approved_by tracker maintainer, Thomaz (Grupo 3), simulated: true, with the sentence "demonstration, not a real decision of Ana Fialho"
  - evidence tracker D9, E9 (empty), F9; reason item registered with unknown owner, who opened and origin; versions F1 and F3.
- Draft notice, **DRAFT, not sent**, no recipient named: "BLOCKER-01 moved from (start) to OPEN_UNOWNED in the demonstration log. Approved by: tracker maintainer role, played by Thomaz (Grupo 3), simulated: true, a demonstration and not a real decision of Ana Fialho. Evidence: tracker D9, E9 (empty), F9. Flag: ORIGIN_OR_DATE_UNKNOWN. Open conflicts: F1 owner, F3 opening date."
- Nothing was sent. No earlier line was touched.
- **Correction, 2026-10-22.** Line 1 recorded the approval without the exact words of the approver. Handoff appended **line 2**, which starts "Correction of line 1", repeats `from` and `to`, carries the exact words "Como Tracker maintainer, em demonstração, aprovo a transição T1 para o BLOCKER-01.", keeps `simulated: true` and "demonstration, not a real decision of Ana Fialho", and states that it is not a second transition. Line 1 was not edited. The state stays OPEN_UNOWNED.

### A8. observe

- Observed on 2026-10-21, when the log had one line. Line 2 (a correction, 2026-10-22) changes no state and no count below.
- Entry check: the log has one line for the item (line 1, written by handoff). The item is not terminal. Observe may act.
- Last recorded transition: OPEN_UNOWNED, simulated. The state read from it is the **simulated state**, not the real state of the item.
- Recorded response after it: no recorded response.
- Recorded attempts (T3, T4, T13 lines): 0.
- Days since the last touch, reported separately. Tracker G9: 2026-08-22, 60 days. Log: the only line is simulated and is not counted as a touch of the item. Compared with a maximum: "not computable", because the maximum is "unknown".
- Suggested transition: none. T5 is not computable. T13 does not apply.
- Next stage: route for a new round. The next permitted step is T2, which needs the product decision role to designate an owner.

### B1. route, request "mark RESOLVED"

- Current state: no log line. Intake proposes OPEN_UNOWNED.
- Request: mark BLOCKER-01 RESOLVED. Supplied by the author running the trace as a test input.
- Result: **refused**. `lifecycle.md` has no transition from OPEN_UNOWNED to RESOLVED. T9 leaves only from IN_ANALYSIS.
- Shortest permitted path: T2 (OPEN_UNOWNED to OPEN_OWNED), T3 (to AWAITING_RESPONSE), T7 (to IN_ANALYSIS), T9 (to RESOLVED), each with its own evidence and approval.
- Next stage: none from this request.

### B2. verify (T9), called by hand

Route refused the request, so Verify was called directly on T9 to show what it does. This is outside the normal order.

Search: the text of every `.docx`, `.xlsx` and `.md` file in the track repository, and the slide text of `sales-deck-2025.pptx` (4 parts, no hit), for "transfer basis", "LATAM", "region", "country", "approv" and "sign-off". "Approver" appears only in DECISION-0028 and DECISION-0031 (other decisions). "Sign-off" appears only in the tracker title, in the Tomas Silva request and in the Ana Fialho interview, none of them an approval. "Transfer basis" appears only in `docs/Policies.docx` (POLICY-03, a requirement), `2026-08-11-tomas-silva.docx` (a requirement and the request) and `data/product-tracker.xlsx` B12 (a title). None is a documented transfer basis.

| Requirement | Status | Pointer | Note |
| :- | :- | :- | :- |
| (a) Documented transfer basis | absent | none | The hits above state the requirement and are not a basis |
| (b) Written approval from the policy owner | absent | none | Tomas Silva wrote on 2026-08-11 that he "cannot sign off on those accounts" until he sees where the search runs. That is the opposite of an approval. |
| (c) Recorded set of covered accounts | absent | none | No source lists accounts by region. Value: "unknown". |
| State is IN_ANALYSIS | not met | tracker D9, log line 1 (simulated) | State is OPEN_UNOWNED |
| No FACTS_IN_DISPUTE on the POLICY-03 wording or the accounts | not met | F4 | Active |

- Verdict: **FAIL**. T9 is refused. The state is unchanged. No lighter version was offered.
- Sufficiency was not judged. What counts as a documented transfer basis is not defined in any source and is an open question for the policy owner.
- A simulated approval could not change this result. Approve is not reachable after a FAIL.
- Recommended next stage: recover.

### B3. recover, from Verify B2 and the deadline question

- Cause: Verify FAIL on T9, missing (a), (b), (c), wrong state, FACTS_IN_DISPUTE active.
- Attempts: 3 claimed, 0 recorded (tracker H9, Ana Fialho interview). Retry limit: 3 recorded attempts, a author hypothesis not validated.
- Below the limit (0 of 3 recorded). Next permitted step toward a recorded attempt: T2 first, because the item has no owner. This needs the product decision role.
- T5 (STALLED), counter route: not met, 0 recorded.
- T5, deadline route: the maximum days without touch is "unknown". The tracker shows 60 days since the last touch (G9 to 2026-10-21), and that is an observed fact. The Verify rule for T5 applies: **"not computable". T5 is refused. The state is unchanged.**
- Flags raised: none new.
- Proposed transition: none. Recommended next step: a human in the product decision role considers T2.

### B4. recover, escalation

Question: raise ESCALATION_REQUIRED_NO_TARGET for BLOCKER-01 and stop.

- The flag is defined as "the escalation condition was reached and no target role exists".
- Escalation condition (limit reached or maximum days exceeded): recorded attempts are 0 of 3, and the deadline is "not computable".
- T6 leaves only from STALLED. The item is not STALLED, because T5 is refused (B3).
- No escalation target role exists. Ana Fialho: "I do not have anyone to escalate to, because the person I would escalate to is the person waiting." That sentence is ambiguous and is not interpreted.
- Result: **the flag cannot be raised for BLOCKER-01 today.** This is recorded as a finding and not forced. `recover` stops at step 7 without a flag. It names no target.
- Decision by Thomaz (Grupo 3): keep the rule as written (option B). Option A is recorded under "Missing controls" as a future change.

## Execution findings

Found by running the cycle. Items 1 to 4 are changes to skills made after the batches were approved, so they need review. Items 5 to 8 are about the design, the documents and the run. Item 8 also led to a clarifying edit in `handoff` step 6.

1. `route` did not handle an item with no log line. Fixed: step 2 now says the only candidate is T1.
2. `act` did not list T1. Fixed: T1 needs only the record line.
3. `verify` would have returned FAIL for T1, contradicting T1's own "If the evidence is missing" outcome. Fixed: step 6 applies the transition's own column, with T1 as the only allowed gap.
4. `recover` step 4 named T4 for an item in OPEN_UNOWNED, where T2 must come first. Fixed.
5. `lifecycle.md` computed "102 days since opening" from one of two disputed dates (F3). Fixed: it now shows 102 or 71 and chooses neither.
6. ESCALATION_REQUIRED_NO_TARGET cannot be raised for BLOCKER-01 today (B4).
7. The design does not represent "a human asks for escalation and no target exists". It only represents "the escalation condition was reached and no target exists".
8. The first Approve record had no approval sentence from the approver, and the log line was written anyway. The Approve skill asks for the exact words, but nothing blocked the handoff. It was fixed after the fact by a correction line (line 2), and `handoff` step 6 now says what a correction line looks like. A check that the exact words are present before writing the line is a missing control.

## Failure, refusal, or ambiguity

**What happened:** Route refused a request to mark RESOLVED (B1). Verify, called on T9, returned FAIL (B2). Recover reported T5 as "not computable" (B3) and could not raise ESCALATION_REQUIRED_NO_TARGET (B4).

**Why the lifecycle did not advance:** the item has no owner and is not IN_ANALYSIS; no document records a transfer basis, a written approval or the set of covered accounts; the POLICY-03 wording and the owner are in dispute (F1, F4); the maximum days without touch is unknown; no escalation target exists.

**Recovery or escalation:** none is possible by rule today. The next permitted step is T2, which needs the product decision role to designate an owner. No escalation target exists.

## Final state

- **Simulated state: OPEN_UNOWNED**, from log line 1 (`simulated: true`).
- Real state: no real transition line exists. Per the model, the item is OPEN_UNOWNED because T2 was never recorded.
- Flags: LINKED_DUPLICATE, FACTS_IN_DISPUTE, WAIT_CONTESTED, BYPASSED_BY_DECISION, ORIGIN_OR_DATE_UNKNOWN.
- Refused or not computable: T9 refused (B2), T5 "not computable" (B3), ESCALATION_REQUIRED_NO_TARGET not raisable (B4).
- The real business outcome, RESOLVED, was not reached and is not reachable today. The tracker was not changed and still shows D9 `open`, E9 empty.

## Limitations and next improvement

Limitations:

- The skills were executed by hand. Nothing enforces a stop, and nothing prevents a person from editing the tracker directly.
- Verify of T9 was called by hand after Route refused the request.
- The searches covered the text of `.docx`, `.xlsx`, `.md` and the slide text of one `.pptx`. Images, embedded objects and anything outside the repository (email, chat, meetings) were not searched. Activity outside the repository may explain the 60 days with no record and the three follow-ups.
- The `context` source list covers BLOCKER-01 only.
- Verify checks that evidence exists, not that it is sufficient. What counts as a "documented transfer basis" is an open question for Tomas Silva.
- The `act` checklists are the author's interpretation, with "who produces it" as "unknown".
- The only approval in the run is simulated, and the person playing the tracker maintainer is the author. The log holds one demonstration transition and one correction line. Both stay in the log, because the log is append-only. The first approval record lacked the approver's exact words, and a correction line was needed (finding 8).
- The work was done by one participant, so no other participant cross-reviewed it. This reduces independent verification of the design.
- Main states plus flags is a author decision and was not confirmed with the instructor.
- The product decision role and tracker maintainer are readings of the sources (Ana Fialho), not confirmed.
- The retry limit of 3 recorded attempts is a author hypothesis. The maximum days without touch is "unknown". Because of that the machine cannot propose STALLED, even with 60 days since the last touch. This is an accepted limitation, not a defect to fix.
- The autonomy levels `draft` and `stop`, the stage evidence section and the transition log file are author decisions, not from the sources.

Missing controls, noted only as observations for Modules 2 and 3 (not built):

- A mandatory owner per blocker, which would protect against an empty Owner (E9).
- A record of every follow-up with date, recipient and response, which would protect against "Asked three times" that no one can audit.
- A deadline and an escalation path, which would protect against waiting with no end.
- A link between a blocker and a decision, which would protect against DECISION-0028 being `done` with the POLICY-03 constraint open.
- Verification of policies. Policies.docx says "Nothing checks any of them."
- Detection of duplicates and of divergence between rows (BLOCKER-01 and REQUEST-T01 differ in date and owner).
- An executable stop. Today the stops depend on a person following the skill.
- A check that an Approve record carries the approver's exact words before `handoff` writes a line (finding 8).
- Option A, a future change to the design: raise ESCALATION_REQUIRED_NO_TARGET also when a human requests escalation and no target exists. It would reflect Ana Fialho's situation, and it would change what the flag means from "required" to "requested or required". It was not adopted.

Next improvement, small and concrete: ask Ana Fialho one question in writing, "what is the maximum number of days a blocker can go without a touch?", and record her written answer in `lifecycle.md`. This turns T5 from "not computable" into a computable check for BLOCKER-01 and lets the stall be proposed or refused on a real number.
