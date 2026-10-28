---
name: approve
description: Assembles the decision package for human review and waits for a named approver to sign off. This skill prepares the package only — it never records the approval itself.
---

# Approve

## Purpose
Assemble the complete decision package that a named approver needs to sign off on the build, and stop until that sign-off is received and recorded by the approver. This skill does not record the approval.

## Entry conditions
- `evidence/verify-<REQUEST-NNN>.md` exists with `verify_status: clear`.
- All three verdicts in the verify evidence are pass/aligned/match.

## Required context
- `evidence/intake-<REQUEST-NNN>.md`
- `evidence/context-<REQUEST-NNN>.md`
- `evidence/route-<REQUEST-NNN>.md`
- `evidence/build-<REQUEST-NNN>.md`
- `evidence/verify-<REQUEST-NNN>.md`
- `docs/policies.md` — POLICY-06 (named approver), POLICY-13 (version citation)
- `project/metrics/metric-definitions.yaml` — to confirm the metric name and version for citation in the package

## Prohibited context
- This skill must never write `approved_by: <name>` or `approved_at: <datetime>` on behalf of a person.
- Do not advance to Handoff without a recorded human approval in `evidence/approve-<REQUEST-NNN>.md`.
- Do not deliver figures to the requester before Handoff; the build output stays within the harness until then.
- Do not infer the approver's name. A role (`Analytics lead`), the `owner:` of a metric in `metric-definitions.yaml`, `authorised_by` in a Context decision, the `approved_by` of an earlier approval, or any name found in another record is not an approver. No source names the Analytics lead, so that name is UNKNOWN until a person records it.
- `UNKNOWN`, `none`, a role name and a placeholder are not names. The skill never writes any of them in `approved_by`.

## Procedure
1. Read all five evidence files (intake, context, route, build, verify). Check that each exists and that no status field records a block or escalation. If any piece is missing or shows a block, stop — the package is incomplete.
2. Assemble `evidence/approve-<REQUEST-NNN>.md` with the decision package (see "Evidence produced"). This is the only document the approver needs to read before signing off.
3. Record in the package: metric name, version in effect, definition_alignment_verdict (from Verify), shape_tests_verdict, extract_taken_at, extract_taken_by, period_alignment_verdict, and — per POLICY-13 — the explicit statement of which definition version was used to produce the output.
4. If POLICY-06 applies (destructive transform was used), record which operation and confirm the approver is named.
5. Mark the package `status: awaiting_approval` and stop. Do not proceed to Handoff.
6. The package remains at `status: awaiting_approval` until a named person explicitly records `approved_by: <name>` and `approved_at: <datetime>` in the file. Those two fields are the approval: `status` is a label that Handoff does not read. This edit is made by the approver or by the skill operator on the approver's instruction — never autonomously by the skill. A name from another record (for example, the original approver re-approving a restatement) is eligible only after a named person writes `designated_approver`, `designated_by` and `designated_at` in the package. `designated_by` follows the same rule as `approved_by`. The skill never writes or copies a name into these fields, and `approved_by` and `approved_at` are still written by the approver.

## Evidence produced
- `evidence/approve-<REQUEST-NNN>.md` in the harness, containing:
  - `request_id`, `metric_name`, `definition_version_in_effect`
  - `extract_taken_at`, `extract_taken_by`
  - `shape_tests_verdict` (from Verify)
  - `definition_alignment_verdict` (from Verify) — explicitly states whether the mart implements the current or a superseded definition
  - `period_alignment_verdict` (from Verify)
  - `policy_06_compliant: true/false` (named approver recorded if applicable)
  - `policy_13_citation`: verbatim metric name and version for inclusion in the pack
  - `status: awaiting_approval`
  - `designated_approver: `, `designated_by: `, `designated_at: ` (blank; filled only by a named person who designates, see step 6)
  - `approved_by: ` (blank — to be filled by the named person)
  - `approved_at: ` (blank — to be filled by the named person)

## Proposed transition
- Package complete, `approved_by` field filled by the named approver → propose **Handoff**.
- Package incomplete (any evidence file missing or blocked) → propose **Correction required**.
- Approver refuses or raises a concern → propose **Escalated**.

## Stop or escalation conditions
- Any of the five evidence files is missing or shows a block → stop and notify Declan Byrne: "The approval package for REQUEST-NNN is incomplete. Missing or blocked: `<file>`. I cannot prepare the package until all prior stages have a clear status."
- The `definition_alignment_verdict` is misaligned (even if Verify passed this through with a note) → stop and refuse to assemble the package: "Verify recorded a definition misalignment. The approval package cannot be assembled until the mart is updated or the Analytics lead explicitly approves proceeding with a documented version mismatch."
- Approver is not reachable or is not named (blank, `UNKNOWN`, a role or a placeholder) and no designation is recorded → stop and ask Declan Byrne: "POLICY-06 requires a named approver. I cannot advance to Handoff without one, and I will not infer the name from a role, a metric owner or an earlier decision. Who is the named approver for REQUEST-NNN?"

## Human judgment boundary
The entire purpose of this skill is to create a hard stop that cannot be bypassed by the skill itself. Approval is a named human act. The skill assembles the evidence; the human reads it and decides. The lesson from INCIDENT-03 is that the absence of this stop allowed a number produced under a superseded definition to reach a customer pack without anyone reviewing what definition was used. Who the approver is also belongs to a person: the skill asks for the name and never supplies one.
