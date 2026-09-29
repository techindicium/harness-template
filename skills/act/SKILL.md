---
name: act
description: Executes the build by running run.py, recording which definition version each mart implements, and capturing the build log as the primary evidence artifact.
---

# Act

## Purpose
Run the build, record what was computed and with which definition version, and produce a build log that is traceable to the extract and to the metric definition used.

## Entry conditions
- `evidence/route-<REQUEST-NNN>.md` exists with `path_chosen: standard_build`.
- The mart has been confirmed to align with the current definition (or the Analytics lead has explicitly approved proceeding with a documented version mismatch).
- The extract period has been confirmed to match the reporting period (from Context).

## Required context
- `project/run.py` — the only authorised build entry point; do not invoke individual SQL files directly
- `data/ops-extract/*.csv` — read by the pipeline; must not be modified
- `data/ops-extract/extract-manifest.yaml` — to embed `taken_at` and `taken_by` in the build log
- `project/metrics/metric-definitions.yaml` — to record the version in effect at build time
- `project/models/marts/*.sql` — to record which logic was applied (read only, not modified)
- `evidence/route-<REQUEST-NNN>.md` — to confirm the approved path and any policy flags

## Prohibited context
- Do not modify the track repository (`portwell-analytics`) or any of its files.
- Do not invoke `rebuild.py` unless POLICY-06 compliance (named approver) has already been recorded.
- Do not produce figures as a message or paste them into a chat. The build log is the only output artifact.
- Do not re-run the build to try to match an expected number. Record what the build produces.

## Procedure
1. Confirm the approved path from `evidence/route-<REQUEST-NNN>.md`. If `policy_06_applicable: true`, confirm that a named approver has been recorded before continuing; if not, stop — see "Stop or escalation conditions."
2. Record the pre-build state: extract `taken_at` and `taken_by` from `data/ops-extract/extract-manifest.yaml`; the current definition version from `project/metrics/metric-definitions.yaml`; the logic in the relevant mart SQL (e.g., for `self_service_rate`: `is_self_served = CAST(sent AS BOOLEAN)` from `stg_suggestions.sql`, as used by `marts/self_service.sql`).
3. Run `python project/run.py` in the track repository environment (WSL, within the uv venv created by `scripts/setup.sh`). Do not pass additional arguments unless the approved path specified them.
4. Capture the full stdout and stderr of the run.
5. Record the exit code. If non-zero, stop — see "Failure path" below.
6. Record the row counts produced for the relevant mart output, and the definition version implemented (from step 2 — not re-derived from the output, because the mart does not emit a version field per POLICY-13 non-compliance: `docs/policies.md`).
7. Write `evidence/build-<REQUEST-NNN>.md` with all of the above.

## Evidence produced
- `evidence/build-<REQUEST-NNN>.md` in the harness, containing:
  - `run_timestamp` (when run.py was invoked)
  - `extract_taken_at` and `extract_taken_by` (from manifest)
  - `definition_version_in_effect` (from `metric-definitions.yaml`)
  - `mart_logic_used` (verbatim field expression from the staging or mart SQL, e.g., `CAST(sent AS BOOLEAN) AS is_self_served`)
  - `exit_code`
  - `stdout_log` (full text)
  - `output_row_counts` (from the mart table relevant to the request)

## Proposed transition
- Exit code 0 and output row counts non-zero → propose **Verify**.
- Exit code non-zero → propose **Correction required** (build failed; see failure path).

## Stop or escalation conditions
- POLICY-06 flag is set in the route evidence but no named approver has been recorded → stop and ask Analytics lead: "The build for `<metric>` requires a destructive operation. POLICY-06 requires a named approver. Who approves this build?"
- The build requires a mart update (mart does not implement current definition and Analytics lead approved a documented mismatch) → record the approved mismatch explicitly in `evidence/build-<REQUEST-NNN>.md` before running.

## Human judgment boundary
Only a person can authorise a destructive mart rebuild (POLICY-06). The skill checks for this condition and stops; it does not estimate whether the risk is low enough to proceed without the named approver.
