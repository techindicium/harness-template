---
name: verify
description: Use after act to check the evidence the proposed transition requires. Reports each requirement as present, absent, in conflict or not computable and returns PASS or FAIL. Refuses T9 (RESOLVED) without a documented transfer basis, written approval from the policy owner and the set of covered accounts, and refuses T5 (STALLED) while the maximum days without touch is unknown.
---

# Verify

Lifecycle stage: Check the transition evidence.

## Purpose
Check, against the actual sources, that every piece of evidence the transition requires exists. A draft, a claim or a tick is not evidence. The result is PASS or FAIL. There is no partial pass.

## Entry conditions
- A Route record with a candidate transition exists in this run.
- Act drafts exist for it, or the transition needs none.

## Required context
- The transition row in `lifecycle.md` (required evidence, approving role, "if the evidence is missing").
- The Route, Act and Context evidence blocks of this run.
- Each source a pointer cites, opened again at that file and field to confirm what it says.
- `traces/transition-log.md`, for recorded attempts and the current state.

## Prohibited context
- Counting as evidence: a draft, a promise, a tick on the readiness checklist ("somebody believed the item was done", `data/README.md`), "Verbal confirmation from engineering" (DECISION-0028), or anything "claimed, not recorded".
- Evidence that belongs to another item.
- Computing elapsed days with an unknown date, or using a maximum that no one defined.
- Choosing between conflicting sources.
- Writing to the track repository.

## Procedure
1. Read the required evidence of the transition from `lifecycle.md`.
2. For each requirement, find the pointer (file and field), open it and compare. Classify it: present, absent, in conflict, or not computable.
3. Check state: the item must be in the transition's origin state. If not, FAIL.
4. Check active flags that block the transition. FACTS_IN_DISPUTE on a fact the transition depends on is a FAIL.
5. Apply the explicit rules below.
6. Apply the "If the evidence is missing" column of the transition. For T1 it says the item opens with ORIGIN_OR_DATE_UNKNOWN, so absent origin fields give PASS with that flag and nothing is filled in. For every other transition, absent evidence means FAIL. Return PASS only if every requirement is present (or T1's allowed gap) and no blocking flag is active. Otherwise FAIL, with each missing item listed and the transition refused.
7. Append the Verify report to `traces/worked-case.md`, under "Stage evidence".

### Explicit rule for T9 (IN_ANALYSIS to RESOLVED)
T9 requires all of: (a) a documented transfer basis, (b) written approval from the policy owner of POLICY-03, (c) a recorded set of covered accounts, each with source and date. In addition the item must be in IN_ANALYSIS and FACTS_IN_DISPUTE must not be active on the wording of POLICY-03 or on the accounts.

If any of (a), (b) or (c) is absent, in conflict or not computable, Verify refuses T9. It does not offer a lighter version, does not accept a "yes" without evidence, and does not mark RESOLVED. For BLOCKER-01 the author's reading of the sources is that none of the three exists (the set of accounts is "unknown", F4 and F6 are open, and the state is OPEN_UNOWNED, not IN_ANALYSIS). Verify must re-check the sources and not rely on this sentence.

### Explicit rule for T5 (to STALLED)
T5 requires the counter of recorded attempts at the limit, or the maximum days without touch exceeded, with recorded dates. The maximum is "unknown". Verify reports "not computable" and refuses T5, even though the tracker shows 60 days since the last touch (G9 to the run date). The three follow-ups are "claimed, not recorded" and do not count.

## Evidence produced
Verify report: transition checked; table of requirements (requirement, status, pointer, note); state check; blocking flags; verdict PASS or FAIL; for FAIL, the refused transition and what is missing.

## Proposed transition
On PASS: no state change yet. Recommend `approve`. On FAIL: recommend `recover`, and state that the transition is refused and the state is unchanged.

## Stop or escalation conditions
- Any required evidence is absent, in conflict or not computable: FAIL.
- A pointer does not open or does not say what the draft says it says: FAIL for that requirement.
- The item is not in the origin state: FAIL.
- A request to treat a draft or a tick as evidence: refuse.

## Human judgment boundary
Verify checks that evidence exists. It does not judge whether a document is a sufficient transfer basis, because Policies.docx does not define the form, the content or who may give it (open question for the policy owner). Even on PASS, sufficiency is decided by the approving role. This skill never states that an approval occurred.
