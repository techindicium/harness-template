---
name: handoff
description: Use after a Verify PASS and a recorded Approve to append one transition line to traces/transition-log.md and to draft the communication. The only skill that writes the log, append-only. Refuses to write a transition without both, and sends nothing on anyone's behalf.
---

# Handoff

Lifecycle stage: Write the transition and communicate. This skill cannot act until the transition has a Verify PASS and an Approve record for the same item and run.

## Purpose
Turn an approved transition into one appended line in the transition log and a draft notice for the affected role. Handoff records what was decided. It decides nothing.

## Entry conditions
- A Verify report with verdict PASS for this transition in this run.
- An Approve record for the same transition with outcome "approved", real or `simulated: true`. A "pending", "denied" or "not valid" outcome does not qualify.
- If either is missing, refuse. Every transition in `lifecycle.md` names an approver, so none is exempt.

## Required context
- The Verify report and the Approve record of this run.
- `traces/transition-log.md` (read the last line for the item). It is created by the first write.
- The record fields in `lifecycle.md` ("How a transition is recorded").

## Prohibited context
- Editing, deleting, reordering or overwriting any earlier line of the log.
- Filling a field from a guess. Any date, person or pointer no record gives is "unknown".
- Writing a line for a transition Verify refused or Approve did not approve.
- Sending a message or posting anything, or writing a notice in the name of Ana Fialho, Tomas Silva or any other person.
- Writing to the track repository.

## Procedure
1. Confirm Verify PASS and the Approve outcome for the same item and transition. Stop if either is absent.
2. Read the last line for the item in the log. Its `to` must equal this transition's `from`. If the log has no line for the item, the `from` must match the state proposed by Intake.
3. Build one line with the fields: item, from, to, recorded_at, recorded_by, approved_by, evidence, reason, versions.
   - `recorded_at`: the run date and time if the session gives it, otherwise "unknown". A fact date that no source gives is "unknown".
   - `recorded_by`: "handoff skill".
   - `approved_by`: role and person from the Approve record. If it is a demonstration, write `simulated: true` in this field.
   - `evidence`: the pointers from the Verify report, or "verbal, not recorded".
   - `versions`: both versions and sources when a conflict is open, otherwise empty.
4. If any required field would need an invented value, refuse and say which one.
5. Append the line to the end of `traces/transition-log.md`. If the file does not exist, create it with a header row of the field names first. Do not touch earlier lines.
6. To correct an earlier line, append a new line with the corrected values and a reason that starts "Correction of line N" and cites the original. The original stays as written. A correction line repeats the original's `from` and `to`, is not checked against step 2, and does not change the state.
7. Draft the communication for the affected role: item, from, to, approver (and `simulated: true` if so), evidence pointers. Mark it "DRAFT, not sent". Name no recipient that no source gives.
8. Append the Handoff evidence block to `traces/worked-case.md`, under "Stage evidence": the line written, its position in the log, and the draft notice.

## Evidence produced
One new line in `traces/transition-log.md`. Handoff evidence block with that line, its position and the draft communication (not sent).

## Proposed transition
The transition written is the one the human approved. This skill does not choose a new one. Next stage: `observe`. A terminal state written here ends the item. Reopening is a new linked item.

## Stop or escalation conditions
- No Verify PASS, or no Approve "approved" record: refuse.
- The log's last `to` for the item does not match this transition's `from`: stop and show both.
- A required field has no source: refuse, do not estimate.
- A request to edit, delete or reorder a line: refuse. Offer a correction line.
- A request to send the notice: refuse. A human sends it.
- The log cannot be written: stop and say so.

## Human judgment boundary
A human holding the named role approves before this skill acts, and a human sends any communication. This skill never states that an approval occurred beyond what the Approve record contains, and it always carries `simulated: true` forward. A simulated line is a demonstration and not a real decision of Ana Fialho or Tomas Silva.
