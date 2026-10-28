---
name: verify
description: Verifies the build output against the current metric definition and extract period, distinguishing shape-test evidence from correctness evidence, and blocks on any definition or period mismatch.
---

# Verify

## Purpose
Confirm that the output produced by Act satisfies three independent criteria — shape tests pass, the mart implements the current definition, and the extract covers the correct period — and produce a verification record that distinguishes each criterion explicitly.

## Entry conditions
- `evidence/build-<REQUEST-NNN>.md` exists with `exit_code: 0`.
- Build output row counts are non-zero.

## Required context
- `evidence/build-<REQUEST-NNN>.md` — to read the mart logic used and the definition version in effect
- `evidence/context-<REQUEST-NNN>.md` — to confirm the extract period and field results
- `project/tests/*.sql` — to confirm which shape tests ran and passed
- `project/metrics/metric-definitions.yaml` — to confirm the current definition version and its required fields
- The staging and mart SQL for the requested metric (not only `self_service`): e.g. `stg_suggestions.sql` + `marts/self_service.sql`, or `marts/first_response.sql`, or whichever models the Route evidence named

## Prohibited context
- Do not treat passing shape tests as confirmation that the number is correct. The 6 shape tests in `project/tests/` verify form only: non-null account_id, tier in accepted values, rate in [0,1], first_response >= 0, referential integrity, pilot accounts non-null. None checks whether the implemented definition matches the current one (confirmed: Declan Byrne interview; findings.md section "O que os 6 testes verificam").
- Do not proceed to Approve if `mart_definition_aligned: false`.
- Do not proceed to Approve if the extract period does not match the reporting period.

## Procedure
1. Read `evidence/build-<REQUEST-NNN>.md`. Record `definition_version_in_effect` and `mart_logic_used`.
2. Read the current definition of the requested metric from `project/metrics/metric-definitions.yaml`. Compare field by field against the mart/staging SQL named in the build evidence. Examples (not an exhaustive allow-list):
   - `self_service_rate` v3: definition requires excluding suggestions where `human_edit_material = true` and excluding tickets reopened within 48 hours. The current mart uses `CAST(sent AS BOOLEAN) AS is_self_served` — no `human_edit_material` filter, no reopening filter. Record `mart_definition_aligned: false`, `divergence: mart implements v2 logic; current definition is v3`.
   - `first_response_minutes_p50` v1: read `first_response.sql` and compare with the v1 definition (`minimum_denominator: 20`, p50 of first_response_minutes). Record alignment result.
   - `suggestion_acceptance_rate` v1: if no mart exists, record `mart_definition_aligned: false`, `divergence: no mart implements this metric` and propose Escalated / Correction required — do not invent alignment.
3. Read `evidence/context-<REQUEST-NNN>.md`. Confirm `period_match: true`. If not, stop — the build was run against an incorrect extract period.
4. Review the shape test results from the build log in `evidence/build-<REQUEST-NNN>.md`. Record each test name and pass/fail. For each test, record what it does and does not verify (use the table in `notes/findings.md` section "O que os 6 testes verificam").
5. Record three explicit verdicts in `evidence/verify-<REQUEST-NNN>.md`:
   - `shape_tests_verdict: pass/fail`
   - `definition_alignment_verdict: aligned/misaligned` (with specific divergence)
   - `period_alignment_verdict: match/mismatch`
6. Record the overall `verify_status: clear` only if all three verdicts are pass/aligned/match. Otherwise record `verify_status: blocked` with the specific criterion that failed.

## Evidence produced
- `evidence/verify-<REQUEST-NNN>.md` in the harness, containing:
  - `shape_tests_verdict` and list of tests with pass/fail
  - `definition_alignment_verdict` with field-by-field comparison
  - `period_alignment_verdict`
  - `verify_status: clear / blocked`
  - `block_reason` (if blocked): specific criterion and source

## Proposed transition
- All three verdicts pass → propose **Approve**.
- `definition_alignment_verdict: misaligned` → propose **Correction required** (the mart does not implement the current definition; the number produced is based on a superseded definition).
- `period_alignment_verdict: mismatch` → propose **Correction required** (extract covers the wrong period; rebuild required with the correct extract).
- Definition mismatch and no clear path to fix → propose **Escalated** (fix requires a human decision about mart update scope).

## Stop or escalation conditions
- The build passed all 6 shape tests but the mart definition check reveals misalignment → do not proceed to Approve. Record: "Shape tests passed. This does not confirm that `<metric>` v<current> was computed correctly. The mart implements v<old> logic. Proposing Correction required." Notify Declan Byrne and Analytics lead.
- The misalignment requires updating track-repository models (e.g. `stg_suggestions.sql`, `marts/self_service.sql`, or another mart named by Route) → stop and escalate: "Correcting the misalignment requires modifying the track repository. This skill cannot make that change. A human must update the mart and re-run."

## Human judgment boundary
The skill can detect that the mart implements a superseded definition and that the shape tests do not catch this. It cannot decide whether to publish the misaligned number with a disclaimer or to block the handoff. That decision belongs to the Analytics lead. The lifecycle proposed in `lifecycle.md` (Part 2, stage Verify) requires that only the misalignment evidence — not the number itself — moves forward until a human resolves this.
