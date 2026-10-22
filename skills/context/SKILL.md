---
name: context
description: Use after intake to assemble the sources a registered PDLC item depends on, with file, field, internal date and age, and to put conflicting facts side by side. Proposes flags. Never picks between conflicting sources and never estimates a date.
---

# Context

Lifecycle stage: Gather sources and conflicts.

## Purpose
Assemble, from a fixed list of read-only sources, the facts the item depends on. For each source say where it is, what it says, how old it is, and whether it conflicts with another. Report conflicts, do not resolve them.

## Entry conditions
- An Intake evidence block exists for the item in this run.
- The item is not terminal.

## Required context
Read-only, from the repository in `track.yaml` `context_repository`. For BLOCKER-01:
- `data/product-tracker.xlsx`, `data/launch/launch-readiness-checklist.xlsx`
- `docs/Policies.docx`, `docs/How we work today.docx`
- `data/discovery/stakeholder-requests/2026-08-11-tomas-silva.docx`, `.../2026-08-13-ana-fialho.docx`
- `data/decisions/DECISION-0028-pilot-scope-change.docx`
- `data/discovery/OPPORTUNITY-04-expand-the-portal-pilot.docx`, `data/discovery/portal-expansion-design.docx`
- `docs/interviews/2026-08-12 Ana Fialho, how decisions happen.docx`
- `docs/incidents/Pilot incidents, product view.docx`
- `data/people/headcount.xlsx`, `data/README.md`
- `lifecycle.md` (Findings F1 to F6, flags) and `traces/transition-log.md` if it exists.

## Prohibited context
- Dates from file-system or document properties. Only dates written inside a document count. Checked on 2026-10-21: `docs/Policies.docx`, `docs/How we work today.docx` and `data/decisions/DECISION-0028-pilot-scope-change.docx` all carry created and modified 2013-12-23 with author "python-docx", while their text says 2026-06-02, 2025-11-04 and 2026-08-07. If a document has no internal date, its date is "unknown".
- Course-team material (`SEED-MANIFEST.md`, `heldout`) and sources outside the repository (email, chat, meetings) unless a human grants access in this run.
- Writing to the track repository, and copying its content here beyond short citation excerpts.

## Procedure
1. For each source read, record: file, field or section, internal date (or "unknown"), and age in days against the run date only when the internal date exists. Never estimate an age.
2. Extract the facts the item depends on: owner, opening date, who is waiting for whom, wording of POLICY-03, state of DECISION-0028, set of covered accounts.
3. Compare the values across sources. Where two sources differ, write both versions side by side with their sources. Do not call one more plausible.
4. Check whether any cited source is superseded or has no identifiable source (example: POLICY-10, superseded by POLICY-11 on 2026-07-01, cited in checklist item 6). Record it.
5. Propose flags from `lifecycle.md`: FACTS_IN_DISPUTE, WAIT_CONTESTED, LINKED_DUPLICATE, BYPASSED_BY_DECISION, ORIGIN_OR_DATE_UNKNOWN. Each flag cites the finding it comes from.
6. Compute elapsed days only when both dates are recorded in sources. Otherwise write "not computable".
7. List which transitions each open conflict or unknown blocks (for example FACTS_IN_DISPUTE on the POLICY-03 wording blocks T9).
8. List what is missing and who could record it. Say "I do not know" instead of filling the gap.
9. Append the Context evidence block to `traces/worked-case.md`, under "Stage evidence".

## Evidence produced
Context evidence block: source table (file, field, internal date, age or "unknown"); conflicts side by side; superseded or unsourced inputs; proposed flags with their findings; transitions blocked; unknowns and who could record them.

## Proposed transition
None. The state is unchanged. Context proposes flags only. Next stage: `route`.

## Stop or escalation conditions
- A required input is stale, superseded or has no identifiable source: record it and mark the dependent transitions as blocked.
- Two sources contradict each other on a fact a transition depends on: record both and mark that transition as blocked until a fact authority records a value.
- A source needed is missing from the repository: say so and name it. Do not reconstruct it.
- A request to access outside sources: ask the human first.

## Human judgment boundary
Which of two conflicting sources holds, whether a stale source is acceptable, and whether a disagreement is resolved belong to the fact authority (for the POLICY-03 wording, the policy owner). This skill never decides them and never states that a conflict is resolved.
