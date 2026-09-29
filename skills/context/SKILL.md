---
name: context
description: Validates that the operational extract covers the correct reporting period and contains every field required by the current metric definition before any build begins.
---

# Context

## Purpose
Validate the extract against two independent criteria — period coverage and field completeness — and block the item before any build starts if either criterion fails.

## Entry conditions
- `evidence/intake-<REQUEST-NNN>.md` exists with `status: open` (not blocked).
- The requested metric is defined in `project/metrics/metric-definitions.yaml`.

## Required context
- `data/ops-extract/extract-manifest.yaml` — authoritative source for `taken_at`, `taken_by`, coverage dates, and `row_counts`
- `data/ops-extract/suggestion.csv` — column headers only; to verify field presence
- `data/ops-extract/ticket.csv` — column headers only
- `project/metrics/metric-definitions.yaml` — to read which fields the current version requires
- `project/models/staging/stg_suggestions.sql` — to verify whether required fields are loaded into staging
- `project/models/staging/stg_tickets.sql` — same
- `evidence/intake-<REQUEST-NNN>.md` — to read the requested metric, version (if specified), and reporting period

## Prohibited context
- Do not read mart SQL at this stage — mart validation belongs to Verify.
- Do not infer extract period from row counts or filenames; only `extract-manifest.yaml` is authoritative.
- Do not proceed past step 3 if the period does not match. Do not proceed past step 5 if a required field is absent.

## Procedure
1. Read `data/ops-extract/extract-manifest.yaml`. Record: `taken_at`, `taken_by`, declared coverage range, `row_counts`.
2. Read the intake note to obtain the reporting period requested.
3. Compare the coverage declared in the manifest with the reporting period. If `taken_at` is absent from the manifest, or if the declared coverage does not include the requested period, stop — see "Stop or escalation conditions." Note: `project/run.py` docstring confirms "Nothing here compares that date to the period being reported on," so this check is entirely manual.
4. Read `project/metrics/metric-definitions.yaml`. Identify the current version of the requested metric. List every input field the definition requires. For `self_service_rate` v3 (effective 2026-07-01), the required fields are: `sent`, `human_edit_material` (to exclude material edits), and a within-48h reopening flag derived from ticket status.
5. Read the column headers of `data/ops-extract/suggestion.csv` and `data/ops-extract/ticket.csv`. For each required field, record `present_in_extract: true/false`. Then read `project/models/staging/stg_suggestions.sql` and `stg_tickets.sql` and record `loaded_in_staging: true/false`. As of the last read, `stg_suggestions.sql` selects: `suggestion_id, ticket_id, created_at, confidence, route, CAST(sent AS BOOLEAN) AS was_sent, CAST(sent AS BOOLEAN) AS is_self_served` — the field `human_edit_material` is absent from the staging model and from `suggestion.csv`.
6. Record all findings in `evidence/context-<REQUEST-NNN>.md`.

## Evidence produced
- `evidence/context-<REQUEST-NNN>.md` in the harness, containing:
  - `extract_taken_at`, `extract_taken_by`, `extract_coverage` (from manifest)
  - `reporting_period_requested` (from intake note)
  - `period_match: true / false / UNKNOWN`
  - For each field required by the current definition: `field_name`, `present_in_extract (true/false)`, `loaded_in_staging (true/false)`
  - `fields_check_result: pass / blocked` (with list of absent fields if blocked)
  - `context_status: clear / blocked`

## Proposed transition
- Period matches and all required fields present in extract and staging → propose **Route**.
- Period does not match → propose **Blocked** (reason: extract from wrong period; cite manifest `taken_at` and requested period).
- One or more required fields absent from extract → propose **Blocked** (reason: field `<name>` required by `<metric>` v<N> is not present in the extract; the metric cannot be computed at the current definition version with the current extract).

## Stop or escalation conditions
- Extract period does not match the reporting period → stop and ask Declan Byrne: "The manifest shows `taken_at: <date>` covering `<coverage>`. The request is for `<reporting_period>`. Should I request a new extract, or has the coverage been updated in the shared folder?"
- A required field for the current metric definition is absent from the extract CSV — for example, `human_edit_material` required by `self_service_rate` v3 is not in `data/ops-extract/suggestion.csv` (columns: `suggestion_id, ticket_id, created_at, article_ids, confidence, route, route_reason, sent`) → stop and ask Declan Byrne and Sofia Marques: "The current definition of `<metric>` v<N> requires the field `<field>`, which is not present in the extract. The metric cannot be computed as defined. Options: (a) use v<N-1> with explicit requester agreement; (b) update the extract query to include `<field>` and re-extract. Which should I do?"
- `extract-manifest.yaml` is absent or has no `taken_at` field → stop and ask Declan Byrne: "The extract manifest is missing or has no `taken_at`. I cannot verify the extract period without it."

## Human judgment boundary
Only a person can decide whether to fall back to a superseded definition version or to block and wait for a new extract. The skill surfaces which fields are missing and from which version they are required; the human chooses the path forward. This skill must not silently proceed with an older definition when the current one is not satisfiable — that is exactly the failure mode that produced INCIDENT-03.
