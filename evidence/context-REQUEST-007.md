# Context: REQUEST-007

Produced by following `skills/context/SKILL.md` on 2026-09-29, against `../portwell-analytics` at
commit `a8aecb4`. Operator: Yuri Alves (group 5). Decisions marked `simulated: true` were made by
a group member playing the named role.

## Entry conditions

| Condition | Result | Source |
| :- | :- | :- |
| The intake note exists and is open | Met | `evidence/intake-REQUEST-007.md` |
| The metric is defined | Met: `self_service_rate`, v3 current | `project/metrics/metric-definitions.yaml` |

## Step 1 to 3: period

```yaml
extract_taken_at: 2026-08-28T09:14:00Z
extract_taken_by: Declan Byrne
extract_method: manual export
extract_coverage: "Covers tickets opened before 2026-08-28."   # no lower bound
row_counts_manifest: {account: 10, tier_commitment: 3, ticket: 1234, interaction: 2468, suggestion: 533}
row_counts_csv: {account: 10, tier_commitment: 3, ticket: 1234, interaction: 2468, suggestion: 533}  # counted, match
ticket_opened_at_range: [2026-06-01T07:21:00Z, 2026-08-27T18:57:00Z]   # measured in ticket.csv
reporting_period_requested: August 2026 (2026-08-01 to 2026-08-31)
period_match: false   # the extract stops at 2026-08-27; August has four more days
```

`project/run.py` states: "Nothing here compares that date to the period being reported on." This
check was done by hand, as the skill says.

**Stop, period.** Message to Declan Byrne:

> The manifest shows `taken_at: 2026-08-28T09:14:00Z` covering tickets opened before 2026-08-28.
> The request is for August 2026. Should I request a new extract, or has the coverage been updated
> in the shared folder?

```yaml
decision: no new extract can be taken from here; build from the 2026-08-28 extract and label every
  figure as covering tickets opened 2026-08-01 to 2026-08-27
reason: the operational database is not reachable. `python project/run.py --live` exits 1 with
  "portwell-portal/data/portwell_ops.db is not reachable from here"
decided_by: Yuri Alves, playing Declan Byrne
simulated: true
decided_at: 2026-09-29
```

## Step 4 and 5: fields required by the current definition

`self_service_rate` v3: numerator "tickets where proposal_sent is true and human_edit_material is
false", denominator "tickets closed in the period", excludes "tickets reopened within 48 hours".

| Field | Present in extract | Loaded in staging | Note |
| :- | :- | :- | :- |
| `proposal_sent` | Yes, under another name: `suggestion.sent` (296 true), and interaction `kind = proposal_sent` (296) | Yes: `was_sent`, `is_self_served` | Same 296 tickets either way |
| `human_edit_material` | **No** | **No** | `suggestion.csv`: suggestion_id, ticket_id, created_at, article_ids, confidence, route, route_reason, sent |
| Ticket closed in the period | **Partly**: `ticket.status` exists; no close date | `status` only | `ticket.csv`: ticket_id, account_id, area, opened_at, subject, body, status |
| Reopened within 48 hours | **No** | **No** | No reopen field; interaction kinds are only `message` and `proposal_sent` |

```yaml
fields_check_result: blocked
absent_fields: [human_edit_material, ticket close date, reopen indicator]
```

**Stop, fields.** Message to Declan Byrne and Sofia Marques:

> The current definition of `self_service_rate` v3 requires `human_edit_material`, which is not
> present in the extract. The metric cannot be computed as defined. Options: (a) use v2 with
> explicit requester agreement; (b) update the extract query to include `human_edit_material` and
> re-extract. Which should I do?

```yaml
decision: compute v2, the rule the July packs used; label every figure self_service_rate v2
reason: REQUEST-007.docx asks for "The same self-service number we had in July", and the July
  mart applied the v2 rule (docs/pr-notes/0088-self-service-v3.md)
requester_agreement: Yuri Alves, playing Lucia Ferreira
decided_by: Yuri Alves, playing Sofia Marques (definition owner)
simulated: true
decided_at: 2026-09-29
open_consequence: v2 also needs "tickets closed in the period", and the extract has no close date.
  The period can only be approximated by the month the ticket was opened
```

## Resulting state

```yaml
context_status: clear, with recorded deviations
deviations:
  - extract covers August only to 2026-08-27 (simulated decision)
  - v2 instead of the current v3 (simulated decision)
  - closed in the period, approximated by the opening month
```

Next skill: Route.
