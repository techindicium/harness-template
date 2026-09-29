# Verify: REQUEST-007

Produced by following `skills/verify/SKILL.md` on 2026-09-29, against `../portwell-analytics` at
commit `a8aecb4`, reading `warehouse.duckdb` with `read_only=True`. Operator: Yuri Alves (group 5).

## Entry conditions

| Condition | Result | Source |
| :- | :- | :- |
| The build evidence exists with `exit_code: 0` | Met | `evidence/build-REQUEST-007.md` |
| The output has rows | Met: 10 August rows per mart | `evidence/build-REQUEST-007.md` |

## Step 2: definition, field by field

### `self_service_rate` against v3 (current)

| Element | v3 says | Mart does | Aligned |
| :- | :- | :- | :- |
| Numerator | proposal sent **and** `human_edit_material` false | proposal sent | No |
| Exclusion | tickets reopened within 48 hours | nothing | No |

### `self_service_rate` against v2 (authorised at Context)

| Element | v2 says | Mart does | Aligned | Measured effect |
| :- | :- | :- | :- | :- |
| Numerator | tickets where `proposal_sent` is true | `sum(is_self_served)`, from `suggestion.sent` | Yes | 296 `sent` true, 296 `proposal_sent` interactions |
| Denominator | tickets closed in the period | `count(*)` of every ticket opened in the month, open ones included | **No** | 10 open tickets, all in August. ACCOUNT-1001 0.433 against 0.4421 closed only; ACCOUNT-1003 0.359 against 0.3636; ACCOUNT-1008 0.4569 against 0.4609 |
| Period of a ticket | closed in the period | month the ticket was opened | **No** | Not computable: the extract has no close date |
| Grain | account-day | account-month | **No** | Declared grain differs; the rate itself is a monthly ratio |

### `first_response_minutes_p50` against v1 (step 2 of the skill names it)

| Element | v1 says | Mart does | Aligned | Measured effect |
| :- | :- | :- | :- | :- |
| First response | first outbound interaction | first interaction with `actor IN ('agent', 'portal')` | **No** | The extract has `agent`, `assist` and `customer`. 151 August tickets answered only by `assist` drop out |
| Minimum denominator | 20 | 20 | Yes | |

August p50, as published in `../portwell-knowledge/data/figures/warehouse-export-2026-08-29.csv`
and as built today: ACCOUNT-1001 41 against 100, ACCOUNT-1003 65 against 104, ACCOUNT-1008 38
against 101. `marts.sla_attainment` inherits the gap: ACCOUNT-1008 0.3966 published against 0.0952
today. See C7 in `notes/findings.md`.

## Step 3: period

`period_match: false` in `evidence/context-REQUEST-007.md`. The extract covers tickets opened to
2026-08-27, and the request is for all of August. The skill says: "If not, stop — the build was
run against an incorrect extract period." The partial period was accepted at Context, but the
Verify skill has no clause for an accepted partial period, so the check fails as written.

## Step 4: shape tests

| Test | Result | What it does not see |
| :- | :- | :- |
| `accepted_values_tier.sql` | pass | Whether commitments match the contracts |
| `first_response_positive.sql` | pass | That 296 tickets are missing from the table it checks |
| `no_null_self-service_for_pilot.sql` | pass | Which definition version produced the rate |
| `not_null_self-service_account.sql` | pass | Whether the mart implements the current definition |
| `referential_ticket_account.sql` | pass | Whether the extract covers the period |
| `self_service_rate_in_range.sql` | pass | Whether the number is right |

The same 6 tests also pass against empty `staging` and `marts` tables (measured in memory, C9).

## Additional check, not in the skill: does the build reproduce the last delivery?

Against the July figures Reporting received (`warehouse-export-2026-08-06.csv`):
`self_service_rate` reproduces for 3 of 3 accounts; `first_response_p50`, `attainment` and
`tickets` reproduce for 0 of 3. Proposed as a Verify step in `notes/findings.md`.

## Step 5 and 6: verdicts

```yaml
shape_tests_verdict: pass
definition_alignment_verdict: misaligned
  # self_service_rate: v3 not implemented; v2 differs on denominator, period and grain
  # first_response_minutes_p50: v1 differs on first outbound interaction
period_alignment_verdict: mismatch
verify_status: blocked
block_reason: definition misaligned (self_service_rate v2, first_response_minutes_p50 v1) and extract period short of August
```

## Proposed transition

The skill proposes **Correction required**. The correction means changing
`marts/self_service.sql` and `marts/first_response.sql` in the track repository, which triggers
the skill's stop condition, so the item goes to **Escalated**. Message to Declan Byrne and the
Analytics lead:

> Shape tests passed. This does not confirm that `self_service_rate` v2 was computed correctly.
> The mart counts open tickets in the denominator and the extract has no close date;
> `first_response.sql` drops the `assist` actor. Correcting the misalignment requires modifying the
> track repository. This skill cannot make that change. A human must update the mart and re-run.

## Human decision

Not simulated. Whether to publish with a disclaimer or to block belongs to the Analytics lead,
whose name is UNKNOWN. The trace stops here on purpose: this is the red state.

## Resulting state

`Escalated`, waiting for a mart correction by the Analytics team. Nothing was delivered.
