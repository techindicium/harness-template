# Intake: REQUEST-007

Produced by following `skills/intake/SKILL.md` on 2026-09-29, against `../portwell-analytics` at
commit `a8aecb4`. Operator: Yuri Alves (group 5).

Decisions marked `simulated: true` were made by a group member playing the named role. They are
not decisions by the Portwell people named, and they are recorded so the trace can continue.

## Entry conditions

| Condition | Result | Source |
| :- | :- | :- |
| A request has arrived | Met. REQUEST-007 is in the inbox | `data/requests/inbox.csv` |
| No open item for this request is already registered | **Not met as written.** REQUEST-007 is already registered, with status `open` | `data/requests/inbox.csv` |

The skill is written for a new arrival. REQUEST-007 was registered on 2026-08-11 and has no intake
note. The operator ran the procedure on the registered item to produce one, and no new identifier
was assigned. This gap in the skill is recorded in `notes/findings.md`.

## Recorded fields

```yaml
request_id: REQUEST-007
from_team: Reporting
requester: Lucia Ferreira
received: 2026-08-11
needed_by: 2026-09-04          # stated in REQUEST-007.docx: "five business days after month end"
                                # CONTRADICTION (C16): five business days after 2026-08-31 is
                                # 2026-09-07, not 2026-09-04. The error is in the source document.
                                # Recorded, not corrected: the stated date is what was requested.
summary: "Self-service per account for the August packs"   # verbatim, inbox.csv
brief: "The same self-service number we had in July, per account, for the August packs."  # REQUEST-007.docx
reporting_period: August 2026  # from the summary; the skill has no field for it (see findings)
metric_name: self_service_rate
metric_defined: true           # metric-definitions.yaml, current version 3, effective 2026-07-01
version_specified: false       # REQUEST-007.docx: "Nothing here says which version of the definition to use"
duplicate_flag: suspected      # REQUEST-011
status_in_inbox: open
tracker_owner: Declan Byrne    # data/tracker.csv
tracker_last_touched: 2026-08-28
```

At run time, `needed_by` is 25 days in the past. Whether figures were delivered outside the
lifecycle is UNKNOWN: the inbox still says `open`.

## Duplicate check

| Item | Requester | Summary | needed_by | Owner |
| :- | :- | :- | :- | :- |
| REQUEST-007 | Lucia Ferreira | Self-service per account for the August packs | 2026-09-04 | Declan Byrne |
| REQUEST-011 | Henrik Sole | Automation rate per account for the August packs | 2026-09-04 | none |

Procedure step 1 looks for the *same requester*, so it does not flag REQUEST-011. The stop
condition, the same deadline plus an overlapping summary, does. `data/tracker.csv` says "Possibly
the same as REQUEST-007. Not checked." `../portwell-knowledge/docs/backlog.md` (ISSUE-52) raises
the same question from the consumer side.

## Proposed transition

**Escalated.** Message to Declan Byrne, as the skill words it:

> REQUEST-007 and REQUEST-011 appear to describe the same number. Please confirm with both
> requesters whether they are the same item before I proceed.

## Human decision

```yaml
decision: proceed with REQUEST-007 alone; REQUEST-011 stays open and unanswered
not_decided: whether REQUEST-007 and REQUEST-011 are the same number (still UNKNOWN)
reason: REQUEST-007 has an owner in the tracker; REQUEST-011 has none
decided_by: Yuri Alves, playing Declan Byrne
simulated: true
decided_at: 2026-09-29
```

## Resulting state

`open`. Next skill: Context.
