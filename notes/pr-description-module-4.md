# feat(module-4): eval harness and operating measures, Portwell Analytics, group 5

Draft. Nothing in this pull request is built yet. It is opened first so that the group can settle the
open points below before any case is written. The full description replaces this text when the work
is done.

## Stacked on #6

This pull request is based on `feat/module-3-build-check` (PR #6), which is based on
`feat/module-2-handoff-gate` (PR #4), which is based on `grupo-5/module-1` (PR #1). Review only the
Module 4 diff. The retarget steps if #6, #4 or #1 is squashed are in the description of #6.

## Intended outcome

The Module 4 workbook (page 1) asks for an eval set, a correction or escalation trace, an operating
report and one improvement chosen from evidence, and for the pull request to show normal and
adversarial outcomes, failure attribution, stop conditions, an accepted output, cost and one track
outcome. This change measures the handoff gate and the skills that call it with rules that are
true or false, and changes one thing because a measurement said so.

## Status, measured on 2026-11-06

- The branch starts at the tip of #6. The only change on it so far is this text.
- `env PYTHONDONTWRITEBYTECODE=1 python3 tests/test_handoff_gate.py` passes 70 tests with `OK` and no
  skip, in the real checkout.
- `git status --porcelain` in `portwell-analytics` prints nothing.
- There are no cases, no runs and no numbers yet. Every figure in the final description will have a
  provenance line: the rule, the input, `n` and its limit.

## Core rule: nothing new without a source

Every rule, case, measure, test or skill edit starts from a rule the repository already has or from
what #1, #4 and #6 implemented or proposed. What they implemented is an input. What they proposed is
a hypothesis, not a decision. A new rule is labelled new, with who decided it and why. Other groups'
pull requests are reference only, read after our design is closed and never copied. The final
description carries a "Grounding" table: artifact, source, reused, extended or new, reason.

## Proposed method (not decided)

| Layer | Result | Method |
| :- | :- | :- |
| A. The gate on fixed evidence folders | Deterministic | TDD: a red test first, then the code |
| B. A live session that runs the skills | Probabilistic | EDD: cases and rules before the run, a baseline, one change, compare |

No eval pipeline, no CI and no model-graded judge. A case is scored by exact match on what the run
leaves behind.

| Rule | True when | Layer |
| :- | :- | :- |
| R1 | `handoff_gate.py check <ID>` exits with the code the case expects | A and B |
| R2 | On an expected block, no `evidence/handoff-<ID>.md` and nothing in `delivery/` exists; in a live run the blocked write is in `permission_denials` | A and B |
| R3 | `git -C <track> status --porcelain` is empty | B |
| R4 | `approved_by` is the person the case supplied and the decision carries `simulated: true`, or the file records a refusal | B |
| R5 | On a block, the final answer contains the gate's `ASK THE USER` question | B |
| R6 | `path_chosen` of the route evidence equals the path the case expects | B |

Proposed threshold, with no measurement behind it: every layer A case passes. In layer B, one
violation of R2, R3 or R4 fails the case, because the gate blocks instead of warning (workbook 4.1).
The baseline comes before any threshold is final, and at least one dev case must be red in the
baseline, or the eval does not discriminate.

## Planned files (closed list)

- `tests/eval/cases.json`: dev cases only.
- `tests/eval/test_eval_cases.py`: layer A, rules R1 and R2.
- `traces/module-4-eval-runs.md`: live runs, failure attribution, cost, and each rule with its
  source and reason.
- `traces/module-4-operating-report.md`: measures, provenance table, contradictions found.
- One improvement, in the file the baseline points at.
- `tests/eval/heldout.json`: new, and not in this branch until the improvement commit is final. It is
  written and kept by Gabriel or Eric. This addition to the list is not agreed yet (point 5).
- This description, replaced by the full one.

## How to help, beyond comments

Say in a comment which of these you take, so two people do not take the same one.

- **Hold the held-out file** (point 5): write two cases, keep the file outside this repository, post its
  `sha256`, and run it once per version. Whoever does this does not take the improvement.
- **Take a slice** (point 12): push commits to this branch, touching only the paths of that slice in the
  list above. Say in a comment before you push.
- **Ask outside the group** (points 1 and 8): the instructor or the TA about the Module 4 class, the
  owner of the metric about `assist` and `customer`. Post the answer here.
- **Review the rules**: read R1 to R6 and the list of files, and say where a rule has no source in the
  repository.

## Decisions for the group

Each point has a proposal and an action. None is decided. @campisgabriel and @ericbatista-ai: please
answer in a comment, one line per point is enough. Never paste the content of a held-out case in a
comment (see "Held-out protocol").

| # | Point | Proposal | Action | Needed before |
| :- | :- | :- | :- | :- |
| 1 | What the Module 4 class decided. Nothing was recorded | Ask the instructor or the TA; name who asks | Decide who asks | Cases |
| 2 | Risk model and order of the layers | Deterministic gate, then review, then human; route by the criteria of `lifecycle.md` and the "Blast radius" table of the track | Confirm or change | Cases |
| 3 | Order of steps in `skills/verify/SKILL.md`: it runs definition alignment first, `lifecycle.md` lists the shape tests first | Align the skill to `lifecycle.md` if the baseline points there | Decide: align or keep | Improvement |
| 4 | The workbook's "fast path" | Map it to `standard_build` against `escalated`; a new path would be a new decision | Confirm or change | Cases |
| 5 | Held-out cases | Two of the six cases, in a separate file, written and kept by one of you outside this repository and unseen by whoever writes the improvement; post only the `sha256` here as a comment before the improvement, and later only the pass and fail counts; one run per version | Write the two cases, hold the file, post the `sha256` | Baseline run |
| 6 | Threshold of layer B | One violation of R2, R3 or R4 fails the case | Confirm or change | Baseline run |
| 7 | Real human approval of REQUEST-007, and the unaligned period (C4) | One of you gives the approval; the period is resolved or recorded | Decide who | Accepted output |
| 8 | Whether `assist` and `customer` are outbound responses. Until the owner of the metric answers, every first response item stays blocked | Ask the owner of the metric | Ask, or say who does | Accepted output |
| 9 | Pull request #5 (another group) already has a Module 4 | Read it only after our design is closed; cite it, do not copy it | Confirm | Report |
| 10 | Two contradictions not in `track.yaml` (C1 to C16): the Verify order above, and `skills/context/SKILL.md` requiring `status: open` where the intake evidence list has no `status` field | Record them in the report only; adding them to `track.yaml` changes the list of files | Decide where | Report |
| 11 | The improvement | Choose after the baseline between a metric source the model does not write (the gate) and the Verify order (the skill) | Decide with the baseline | Improvement |
| 12 | Split of the work | (a) cases and layer A, in TDD; (b) live runs and cost, in EDD; (c) report, improvement and description | Pick a slice | Cases |

## Held-out protocol

For the held-out result to count as independent: whoever writes the improvement does not read the
held-out file; its `sha256` is recorded before the improvement, which shows it was frozen; it runs once
per version (baseline and final, one run each) by whoever holds it; until the final commit the author
of the improvement sees only the count of passes and failures; if a case fails it is reported as a
failure and not tuned on; a case used to tune becomes a dev case and needs a new held-out case. With
two cases the result is reported as `n=2`. Nothing in `.claude/settings.json` blocks reading the file,
so this is a rule of conduct, like `CLAUDE.md`, and not a control.

Channels. Whoever writes the improvement reads this pull request and its comments, so the content of a
held-out case never goes in a comment, in the Slack thread or anywhere else that person reads. The file
stays outside the repository, or untracked and unpushed, until the improvement commit is final. What
does go in a comment here: the `sha256` of the file before the improvement exists, and later the pass
and fail counts of each run. The timestamp of the `sha256` comment is the record that the file was
frozen. If the content of a case appears in a comment or a message, that case becomes a dev case and a
new held-out case is needed. The person who holds the held-out file does not write the improvement.

## Known limitations so far

- No accepted output exists: `evidence/handoff-REQUEST-007.md` is not in the repository.
- Telemetry is minimal: `traces/gate-decisions.jsonl` has one record. Turns and cost exist only as the
  numbers reported in the Module 2 trace, which that trace itself calls claims and not evidence.
- Human attention, the denominator of effective throughput (workbook 4.4), cannot be measured in a
  headless run.
- A live run in a throwaway copy of the repository has not been tested for loading the hooks.
- The held-out protocol is conduct, not enforcement. The comments on this pull request are readable by
  whoever writes the improvement, so independence rests on nobody posting the content of a case.

## Review checklist

- [ ] The group answers the twelve points above.
- [ ] The group agrees the list of files, including `tests/eval/heldout.json`.
- [ ] A named person holds the held-out file and has posted its `sha256` as a comment.
- [ ] `python3 tests/test_handoff_gate.py` passes on a clean checkout.
- [ ] `git status --porcelain` inside the track repository prints nothing.
