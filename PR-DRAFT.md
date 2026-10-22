# Module 1: BLOCKER-01 lifecycle and skills (Grupo 3, PDLC)

Draft for review. The pull request has not been opened.

## Intended outcome

Design a lifecycle for one real Portwell item, BLOCKER-01 ("POLICY-03 sign-off for LATAM accounts", `data/product-tracker.xlsx` row 9), write one skill per stage, and run the item through them as far as the evidence allows. The result that matters is where the cycle stops.

Constraints: the track repository (`portwell-product-1`) is read-only and nothing from it is copied here; no estimated dates; no conflict between sources is resolved; nothing from Modules 2, 3 or 4 is built.

Non-goals: resolving BLOCKER-01, revising DECISION-0028, deciding who owns the blocker, choosing between the two wordings of POLICY-03.

## What this PR adds

| File | Content |
| :- | :- |
| `track.yaml` | Group name (Grupo 3), track, process and work item |
| `lifecycle.md` | Current process, findings, states, flags, transitions T1 to T14, failure and recovery, terminal states |
| `skills/*/SKILL.md` | Nine skills: intake, context, route, act, verify, approve, handoff, observe, recover |
| `traces/worked-case.md` | The run of BLOCKER-01 and the evidence of each skill |
| `traces/transition-log.md` | Append-only log: one demonstration transition (`simulated: true`) and one correction line |

`README.md` and `.claude-plugin/plugin.json` are unchanged. The local `context/` folder is not part of this PR.

## Design of the lifecycle

- **Two levels.** States and flags describe the item. Stages describe the procedure each transition attempt goes through: Intake, Context, Route, Act, Verify, Approve, Handoff and Observe, with Recover as a detour when something fails.
- **Main states** (mutually exclusive): OPEN_UNOWNED, OPEN_OWNED, AWAITING_RESPONSE, IN_ANALYSIS, STALLED, ESCALATED. **Terminal states:** RESOLVED, DECLINED, CANCELLED, MERGED. Terminal states have no exit. Reopening is a new linked item.
- **Flags** (can coexist with any state): LINKED_DUPLICATE, FACTS_IN_DISPUTE, WAIT_CONTESTED, BYPASSED_BY_DECISION, ORIGIN_OR_DATE_UNKNOWN, ESCALATION_REQUIRED_NO_TARGET.
- **Transitions T1 to T14.** Each has required evidence, an approving role and a stated outcome when the evidence is missing. T9 (to RESOLVED) needs a documented transfer basis, written approval from the policy owner and the set of covered accounts.
- **Retry limit and escalation.** Retry limit: 3 recorded attempts, a author hypothesis. Escalation fires when the limit is reached or the maximum days without touch is exceeded. The maximum is "unknown".
- **Human judgment.** Nine boundaries are listed in `lifecycle.md`. The machine never resolves a disagreement, chooses between sources, estimates a date, designates an owner or an escalation target, or marks a terminal state.
- **Recording.** One line per transition in `traces/transition-log.md`, written only by `handoff`, append-only, a correction is a new line.

## Execution trace (summary)

Full record: `traces/worked-case.md`. The skills were executed by hand by Claude in a Claude Code session, following each `SKILL.md`.

| Run | What happened |
| :- | :- |
| A, T1 | Intake, Context, Route, Act and Verify ran. Verify returned PASS with ORIGIN_OR_DATE_UNKNOWN. Approve recorded a **simulated** decision by the author (Thomaz) in the tracker maintainer role (`simulated: true`, "demonstration, not a real decision of Ana Fialho"). Handoff wrote line 1 of the log, and line 2 later corrected it once the approver's exact words were recorded. Observe found no recorded response and 0 recorded attempts. |
| B, request "mark RESOLVED" | **Route refused**: no transition from OPEN_UNOWNED to RESOLVED. **Verify on T9 returned FAIL**: no transfer basis, no written approval, no set of covered accounts, wrong state, FACTS_IN_DISPUTE active. |
| B, STALLED | **Recover answered "not computable"** for T5: the maximum days without touch is unknown, although the tracker shows 60 days since the last touch. |
| B, escalation | ESCALATION_REQUIRED_NO_TARGET **cannot be raised today**: 0 of 3 recorded attempts, deadline not computable, item not STALLED. Recorded as a finding. |

**Final state: simulated state OPEN_UNOWNED.** No real transition was recorded. RESOLVED is not reachable today.

### What failed on purpose

The stops are the evidence: the refused route, the Verify FAIL on T9, the "not computable" on T5 and the flag that could not be raised. Running the cycle also exposed eight findings (listed in the trace). Four were fixes to our own skills after the batches were approved (T1 handling in `route`, `act` and `verify`, and the T4 reference in `recover`) and need review. One corrected a "102 days since opening" that used one of two disputed dates.

## Decision record and trade-offs

| Decision | Trade-off | Status |
| :- | :- | :- |
| Main states plus flags, not exclusive states only | Represents five conditions at once, but adds a second concept. Based on one case. | Author decision, **not confirmed with the instructor** |
| Stages are the procedure, states describe the item | Nine skills for one item, some barely used (`observe`, `handoff`). Required by the README. | Decided |
| `draft` and `stop` autonomy levels | Simple, but not from the sources. | Author decision |
| Stage evidence appended to `traces/worked-case.md`, only `handoff` writes the log | One place to read, but skills write to a shared file. | Author decision |
| `traces/transition-log.md`, append-only, header as the only exception | Simple and auditable, but a demonstration line stays in the log forever. | Author decision |
| Keep ESCALATION_REQUIRED_NO_TARGET as written (option B) | Honest about the rule, but it does not represent "a human asks for escalation and no target exists". | Author decision. Option A kept as a future change. |
| Verify checks existence, not sufficiency | Avoids judging a policy the sources do not define. Leaves sufficiency to the approving role. | Decided |
| Ana Fialho as tracker maintainer and as product decision role | Needed to name approvers. Sourced for "Kept by" only. | Declared assumption |

## Known limitations

- The skills are prompt-level procedures, executed by hand. Nothing enforces a stop, and a person can still edit the tracker.
- The only approval in the run is simulated, and the person playing the tracker maintainer is the author. Verify of T9 was called by hand after Route refused the request.
- The work was done by one participant, so no other participant cross-reviewed it. This reduces independent verification of the design.
- The `context` source list covers BLOCKER-01 only. Searches covered `.docx`, `.xlsx`, `.md` and the slide text of one `.pptx`. Nothing outside the repository was consulted.
- What counts as a "documented transfer basis" is not defined in any source. Verify does not judge it.
- The retry limit of 3 is a hypothesis. The maximum days without touch is "unknown", so the machine cannot propose STALLED even with 60 days since the last touch. This is an accepted limitation.
- Role names and the mapping of Ana Fialho and Tomas Silva to roles are readings of the sources, not confirmed.
- Open facts, all recorded as "unknown": who opened BLOCKER-01 and why on 2026-07-11, the item owner, the date, channel and recipient of the three follow-ups, what changed on 2026-08-22, the set of covered accounts, the escalation target.
- Unresolved source conflicts, left as findings: F1 owner, F2 who waits for whom, F3 opening date, F4 wording of POLICY-03, F5 state of DECISION-0028.

Missing controls, as observations for later modules (not built): mandatory owner per blocker; a record of each follow-up; deadline and escalation path; link between blocker and decision; verification of policies; duplicate and divergence detection; an executable stop; option A for the escalation flag.

## Dependencies and integration

- Identifiers (BLOCKER-01, REQUEST-T01, DECISION-0028, POLICY-03 and others) are referenced, never renumbered.
- `portwell-product-1` was used as evidence and shows no changes.
- Nothing here depends on another group.

## Next improvement

Ask Ana Fialho one question in writing, "what is the maximum number of days a blocker can go without a touch?", and record her written answer in `lifecycle.md`. This makes T5 computable for BLOCKER-01.

## Questions for the instructor and assistants

- Are main states plus flags acceptable, or does Module 1 require exclusive states?
- Is `traces/transition-log.md`, a file outside the README list, acceptable?
- Does the PR come from a fork or from a branch in `harness-template`?

## Contributions

The work of Grupo 3 was done by one participant, Thomaz. There are no contributions from other participants to record.

| Participant | Contribution |
| :- | :- |
| Thomaz | Chose the work item BLOCKER-01. Ran the trace with Claude Code. Made the design decisions: main states plus flags, nine skills, a single append-only transition log file, and option B for the escalation flag. Reviewed each batch of skills before the next one was written. Played the simulated tracker maintainer role in T1, with `simulated: true`. |

The text and the skills were drafted with Claude Code under Thomaz's direction and review. They are not hand-written work.

Limitation: because there is a single participant, no other participant cross-reviewed the design, and this reduces independent verification.
