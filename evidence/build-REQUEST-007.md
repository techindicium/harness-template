# Build: REQUEST-007

Produced by following `skills/act/SKILL.md` on 2026-09-29, against `../portwell-analytics` at
commit `a8aecb4`. Operator: Yuri Alves (group 5).

## Entry conditions

| Condition | Result | Source |
| :- | :- | :- |
| Route chose `standard_build` | Met | `evidence/route-REQUEST-007.md` |
| The mart matches the definition, or a mismatch was approved | Met: v2 approved at Context (simulated) | `evidence/context-REQUEST-007.md` |
| The extract period matches the reporting period | **Not met as written.** Coverage ends 2026-08-27; the partial period was accepted at Context (simulated) | `evidence/context-REQUEST-007.md` |

The Act skill has no clause for a human-accepted partial period. The operator went ahead under the
Context decision and records the deviation here. The gap is recorded in `notes/findings.md`.

## Pre-build state

```yaml
extract_taken_at: 2026-08-28T09:14:00Z
extract_taken_by: Declan Byrne
extract_version: committed CSVs at portwell-analytics commit a8aecb4
definition_version_in_effect: 3 (current); 2 authorised for this run
mart_logic_used: "CAST(sent AS BOOLEAN) AS is_self_served (stg_suggestions.sql), summed over count(*) of tickets per account-month (marts/self_service.sql)"
policy_06_applicable: false
```

## Run

```yaml
command: .venv/bin/python project/run.py     # the environment was created by ./scripts/setup.sh (uv)
run_timestamp: 2026-09-29T15:04:50Z
python: 3.13.7
duckdb: 1.5.6
exit_code: 0
```

```text
  loaded extract from data/ops-extract
Building warehouse.duckdb
  built project/models/staging/stg_accounts.sql
  built project/models/staging/stg_extract_metadata.sql
  built project/models/staging/stg_interactions.sql
  built project/models/staging/stg_suggestions.sql
  built project/models/staging/stg_tickets.sql
  built project/models/staging/stg_tier_commitments.sql
  built project/models/marts/first_response.sql
  built project/models/marts/self_service.sql
  built project/models/marts/sla_attainment.sql
Tests
  pass accepted_values_tier.sql
  pass first_response_positive.sql
  pass no_null_self-service_for_pilot.sql
  pass not_null_self-service_account.sql
  pass referential_ticket_account.sql
  pass self_service_rate_in_range.sql

OK: 0 failing test(s)
```

## Output

```yaml
row_counts: {marts.self_service: 30, marts.first_response: 938, marts.first_response_p50: 30, marts.sla_attainment: 30}
august_rows: {marts.self_service: 10, marts.first_response_p50: 10, marts.sla_attainment: 10}
staging.extract_metadata.extracted_at: 2026-09-29T12:04:50Z   # build time in local time (-03:00) with a Z suffix, not the extract date (C10)
```

`marts.self_service`, August 2026 (tickets opened 2026-08-01 to 2026-08-27):

| account_id | tier | pilot | closed_tickets | suggestions_shown | self_served_tickets | self_service_rate |
| :- | :- | :- | -: | -: | -: | -: |
| ACCOUNT-1001 | enterprise | yes | 97 | 75 | 42 | 0.433 |
| ACCOUNT-1002 | business | yes | 26 | 20 | 11 | 0.4231 |
| ACCOUNT-1003 | enterprise | yes | 78 | 50 | 28 | 0.359 |
| ACCOUNT-1004 | business | yes | 35 | 22 | 9 | 0.2571 |
| ACCOUNT-1005 | standard | no | 8 | 0 | 0 | 0.0 |
| ACCOUNT-1006 | business | yes | 28 | 15 | 8 | 0.2857 |
| ACCOUNT-1007 | standard | no | 6 | 0 | 0 | 0.0 |
| ACCOUNT-1008 | enterprise | yes | 116 | 92 | 53 | 0.4569 |
| ACCOUNT-1009 | business | no | 20 | 0 | 0 | 0.0 |
| ACCOUNT-1010 | standard | no | 4 | 0 | 0 | 0.0 |

These are build output, not figures fit to deliver. The non-pilot accounts read 0.0 where the
backlog says they should read "not applicable" (ISSUE-32).

## Effect on the track repository

`run.py` rewrote `warehouse.duckdb` in the track root, and `scripts/setup.sh` created `.venv/`.
Both are in its `.gitignore`. `git -C ../portwell-analytics status --porcelain` printed nothing
after the run.

## Resulting state

Exit code 0 and output rows present. Next skill: Verify.
