# Route: REQUEST-007

Produced by following `skills/route/SKILL.md` on 2026-09-29, against `../portwell-analytics` at
commit `a8aecb4`. Operator: Yuri Alves (group 5). Decisions marked `simulated: true` were made by
a group member playing the named role.

## Entry conditions

| Condition | Result | Source |
| :- | :- | :- |
| Context is `clear` | Met, with recorded deviations | `evidence/context-REQUEST-007.md` |
| All required fields present in extract and staging | **Not met for v3**; met for v2 apart from the close date | `evidence/context-REQUEST-007.md` |

The second condition holds only because of the simulated decision at Context to compute v2.

## Step 1 and 2: definition and mart

```yaml
metric_name: self_service_rate
current_definition_version: 3        # effective 2026-07-01; v2 is status: superseded
authorised_version: 2                # simulated decision at Context
mart: project/models/marts/self_service.sql
mart_logic: "sum(CASE WHEN p.is_self_served THEN 1 ELSE 0 END) / count(*)"
staging_logic: "CAST(sent AS BOOLEAN) AS is_self_served"   # stg_suggestions.sql
mart_implements_version: 2           # by rule name; field-level check belongs to Verify
mart_definition_aligned: false        # against v3; the v2 rule by name
```

**Stop, version.** `mart_implements_version` is not `current_definition_version`. Message to
Declan Byrne and the Analytics lead:

> The mart `self_service.sql` implements `self_service_rate` v2 (field:
> `is_self_served = CAST(sent AS BOOLEAN)`). The current definition is v3. Should I update the
> mart before building, or proceed with v2 and document that the output does not match the
> current definition? Note: the requester has not specified a version.

Resolved by the decision already recorded at Context (v2, labelled). No new decision was taken.

## Step 3: duplicates

REQUEST-011 is still open. The Intake decision deferred the duplicate question rather than
resolving it, so step 3's re-escalation condition is met. It is covered by the same Intake
decision, and no new decision was taken. The question stays UNKNOWN.

## Step 4: policies

| Policy | Applicable | Finding | Source |
| :- | :- | :- | :- |
| POLICY-05 | Yes | The v3 change was never announced, and there is no consumer log (`evidence/consumer-log.md` does not exist) | `docs/policies.md`; ISSUE-30 |
| POLICY-06 | No, as the skill defines it | The build uses `run.py`, not `rebuild.py`. `run.py` does run `CREATE OR REPLACE TABLE` on every model; whether that counts as a destructive transformation is UNKNOWN, because the policy does not define the term | `docs/policies.md`; `project/run.py` |
| POLICY-13 | Yes | The approval package and any delivery must name `self_service_rate` v2 | `docs/policies.md` |

```yaml
policy_05_applicable: true
policy_05_block: true
policy_06_applicable: false
policy_13_applicable: true
```

**Stop, POLICY-05.** Message to Sofia Marques:

> The definition of `self_service_rate` changed to v3 on 2026-07-01. POLICY-05 requires announcing
> definition changes one period ahead. I cannot find a consumer list. Who should be notified, and
> has the notification been sent?

```yaml
decision: August stays on v2, the version the July packs used, so this delivery changes no
  definition for its consumers. The v3 announcement POLICY-05 requires is still owed and cannot be
  made without a consumer list (ISSUE-30)
decided_by: Yuri Alves, playing Sofia Marques
simulated: true
decided_at: 2026-09-29
```

## Resulting state

```yaml
path_chosen: standard_build
justification: v2 authorised at Context; POLICY-05 decision above; duplicate deferred at Intake
duplicate_flag: suspected (deferred, not resolved)
```

Next skill: Act.
