---
name: intake
description: Use when a PDLC work item (for example BLOCKER-01) enters the lifecycle or is re-registered. Accepts the item by its existing identifier, bounds its scope and drafts the T1 record line. Does not assign owners, fill unknown fields or write the transition log.
---

# Intake

Lifecycle stage: Register the blocker. Author design: main states plus flags, not confirmed with the instructor (see `lifecycle.md`).

## Purpose
Accept one existing tracker item by its identifier, record what the tracker says about it (including what is empty), state the bounded outcome and what is out of scope, and draft the T1 record. Intake describes the item. It does not decide anything about it.

## Entry conditions
- The input names an identifier that exists in `data/product-tracker.xlsx` of the repository in `track.yaml` `context_repository`, or a new request is described in words.
- The item is not in a terminal state (RESOLVED, DECLINED, CANCELLED, MERGED). If it is, stop (see below).
- No instruction to renumber, rename or merge the identifier.

## Required context
- The tracker row of the item, read by identifier, with cell references (for BLOCKER-01: `data/product-tracker.xlsx` row 9).
- Other tracker rows only to find a row that claims to be the same item (for BLOCKER-01: REQUEST-T01, row 12, note "Same as BLOCKER-01").
- `lifecycle.md` (states, flags, T1) and `track.yaml`.

## Prohibited context
- Any source beyond the tracker row and the links it names. Gathering sources is the `context` skill's job.
- Course-team material in the track repository (`SEED-MANIFEST.md`, `heldout` folders) and anything outside the repository (email, chat).
- Copying product data into this repository. Quote only the short excerpt a citation needs.
- Writing to the track repository. It is read-only.

## Procedure
1. Read the tracker row by identifier. Copy each field with its cell reference. An empty cell is recorded as "empty (unknown)". Do not copy a value from another row into an empty cell.
2. Check that the identifier is unchanged and the item is not terminal.
3. State the bounded outcome in one sentence, taken from the item's own title (BLOCKER-01: "POLICY-03 sign-off for LATAM accounts"), and the constraints: read-only track repository, no estimated dates, no resolved conflicts.
4. List what is out of scope. For BLOCKER-01: revising DECISION-0028, LAUNCH-01, REQUEST-R01, the two pilot incidents.
5. Check for another row that claims to be the same item. Record the link and the claim's source. Do not decide which row is primary.
6. For every required field with no source (who opened the item, why on that date, owner), propose the flag ORIGIN_OR_DATE_UNKNOWN and write "unknown".
7. Draft the T1 record line (fields in `lifecycle.md`, "How a transition is recorded"): item, from "(start)", to OPEN_UNOWNED, evidence pointers, reason. Leave `approved_by` empty.
8. Append the Intake evidence block to `traces/worked-case.md`, under "Stage evidence", and show it to the human. Do not write `traces/transition-log.md`.

## Evidence produced
Intake evidence block with: item identifier; tracker fields with cell references; bounded outcome; out-of-scope list; linked-duplicate note with source; unknown fields; proposed flags; the drafted T1 line (not yet written to the log).

## Proposed transition
T1: (start) to OPEN_UNOWNED, for the tracker maintainer to approve. The skill only recommends it. Next stage: `context`.

## Stop or escalation conditions
- The identifier is not found, or appears on more than one row: stop and report both rows.
- The item is already terminal: refuse. Reopening is a new linked item, decided by a human.
- A request to renumber, rename or merge the identifier: refuse.
- A request to fill in an owner, an opening date or the reason from another field: refuse and keep "unknown".
- The tracker cannot be read: stop and say what is missing.

## Human judgment boundary
The tracker maintainer approves T1 (Ana Fialho per "Kept by Ana Fialho", `data/product-tracker.xlsx` A2, a reading by the author). Whether BLOCKER-01 and REQUEST-T01 are the same item is decided by the tracker maintainer and the policy owner (T12), never by this skill. This skill never states that an approval happened.
