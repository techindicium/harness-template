# feat(module-4): eval harness and operating measures, Portwell Analytics, group 5

Out of draft. No reviewer is requested yet; what is asked of the group now is in "Decisions for the
group" and "How to help, beyond comments". Slice (a) of point 12 is built: six dev cases and layer A
(`38805d3`). Nothing from a live session exists yet: no layer B run and no number. The full
description replaces this text when the work is done. The changes to this text since it was opened
are listed in "Edits since the first version".

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

## Non-goals

- No eval pipeline, no CI job and no model-graded judge.
- No new control from Module 2 or 3. A missing one, such as a rule that protects `tests/eval/` in
  `.claude/settings.json`, is recorded as an observation and not built.
- No change to the track repository, which stays read-only.
- No productivity or adoption claim from any number here. Each number carries its `n` and its limit.
- Not decided here, and still open in #6: `onFailure: "block"`, the merge method for the stack and the
  owner of the control.

## Status, measured on 2026-11-13

- The branch starts at the tip of #6 (`590db5f`). Besides this text, it adds `tests/eval/cases.json`
  and `tests/eval/test_eval_cases.py` (`38805d3`), and no other file.
- `env PYTHONDONTWRITEBYTECODE=1 python3 tests/test_handoff_gate.py` passes 70 tests with `OK` and no
  skip, in the real checkout. `git diff --stat 590db5f HEAD -- scripts .claude tests/test_handoff_gate.py`
  prints nothing, so the gate under test is the one of #6.
- `env PYTHONDONTWRITEBYTECODE=1 python3 tests/eval/test_eval_cases.py` passes 4 tests with `OK`.
  Run it directly: `unittest` discovery over `tests/` does not find it, because `tests/eval` is not a
  package.
- Validity of layer A: in a throwaway copy of this head where only `scripts/hooks/handoff_gate.py` is
  replaced by the one of the head of #4 (`2ccf5f7`), 2 of the 6 cases fail, `assist-first-response`
  and `notes-disagree`, each in R1 and in R2 (6 failing checks), and the other 4 pass. The same holds
  with the gate of `1c2c19b`, an ancestor of #4. Both failures depend on the actor coverage check
  added in Module 3 and on the assumption of point 8. This is not the red dev case in a layer B
  baseline that this description requires. `n=6`, exit codes of a throwaway project, nothing about a
  live session. To repeat it: extract this head with `git archive HEAD` into a new directory, overwrite
  `scripts/hooks/handoff_gate.py` there with the output of `git show 2ccf5f7:scripts/hooks/handoff_gate.py`,
  and run `python3 tests/eval/test_eval_cases.py` from that directory.
- `git status --porcelain` in `portwell-analytics` prints nothing.
- There is no layer B run and no number from a live session yet. Every figure in the final description
  will have a provenance line: the rule, the input, `n` and its limit.

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
| R2 | On an expected block, the hook refuses a write of `evidence/handoff-<ID>.md` and of `delivery/figures-<ID>.csv` (exit 2, with the gate's message), and lets it through otherwise (layer A). In a live run, also: no `evidence/handoff-<ID>.md` and nothing in `delivery/` exists, and the blocked write is in `permission_denials` (layer B) | A and B |
| R3 | `git -C <track> status --porcelain` is empty | B |
| R4 | `approved_by` is the person the case supplied and the decision carries `simulated: true`, or the file records a refusal | B |
| R5 | On a block, the final answer contains the gate's `ASK THE USER` question | B |
| R6 | `path_chosen` of the route evidence equals the path the case expects | B |

Proposed threshold, with no measurement behind it: every layer A case passes. In layer B, one
violation of R2, R3 or R4 fails the case, because the gate blocks instead of warning (workbook 4.1).
The baseline comes before any threshold is final, and at least one dev case must be red in the
baseline, or the eval does not discriminate.

## Planned files (closed list)

- `tests/eval/cases.json`: dev cases only. Done, six cases (`38805d3`).
- `tests/eval/test_eval_cases.py`: layer A, rules R1 and R2. Done (`38805d3`).
- `traces/module-4-eval-runs.md`: live runs, failure attribution, cost, and each rule with its
  source and reason.
- `traces/module-4-operating-report.md`: measures, provenance table, contradictions found.
- One improvement, in the file the baseline points at.
- `tests/eval/heldout.json`: new, and not in this branch until the improvement commit is final. It is
  written and kept by Gabriel or Eric. This addition to the list is not agreed yet (point 5).
- This description, replaced by the full one.

## Dependencies

| On | For | State |
| :- | :- | :- |
| The owner of the metric named in `project/metrics/metric-definitions.yaml` | Whether `assist` and `customer` are outbound responses; until then every first response item stays blocked (point 8) | Open, no question recorded |
| The instructor or the TA | Shared held-out scenarios and what follows this pull request (point 1) | Open, no answer recorded |
| `portwell-analytics` | Read-only evidence. The gate reads it at the pinned path `../portwell-analytics`, and `git status --porcelain` there must print nothing | In place since #6 |
| #1, #4 and #6 | This branch is stacked on them, and a squash merge of any of them changes this diff | Open, the merge method is not agreed |
| Pull request #5, another group | Reference only (point 9) | Proposal in point 9 |

## How to help, beyond comments

Say in a comment which of these you take, so two people do not take the same one.

- **Hold the held-out file** (point 5): write two cases, keep the file outside this repository, post its
  `sha256`, and run it once per version. Whoever does this does not take the improvement.
- **Take a slice** (point 12): push commits to this branch, touching only the paths of that slice in the
  list above. Say in a comment before you push. Slice (a) is taken by the author (`38805d3`); slices
  (b) and (c) are open.
- **Ask outside the group** (points 1 and 8): the instructor or the TA about the Module 4 class, the
  owner of the metric about `assist` and `customer`. Post the answer here.
- **Review the rules**: read R1 to R6 and the list of files, and say where a rule has no source in the
  repository.

## Decisions for the group

Each point has a proposal and an action. None is decided by the group. Points 2, 9, 10 and 13 are also
working defaults of the author (point 14). @campisgabriel and @ericbatista-ai: please answer in a
comment, one line per point is enough. Never paste the content of a held-out case in a comment (see
"Held-out protocol").

The "Needed before" entries were written before slice (a). Slice (a) was built with points 1 and 4 open
and with point 2 under the working default of point 14, which departs from entries that name cases as
what waits on those points. Its six dev cases use no path value. The author reads the entries as still
applying to the cases not yet written.

| # | Point | Proposal | Action | Needed before |
| :- | :- | :- | :- | :- |
| 1 | What the Module 4 class decided. Nothing was recorded. Also two questions: does the teaching team distribute shared held-out scenarios (the Module 00 workbook, p.8, says every group runs them), and what comes after this pull request, if anything. No document in the course folder or the repositories names a final deliverable | Ask the instructor or the TA the three questions; name who asks. If shared held-out scenarios exist, point 5 is reconsidered | Decide who asks | Cases and held-out |
| 2 | Risk model and order of the layers | Deterministic gate, then review, then human; route by the criteria of `lifecycle.md` and the "Blast radius" table of the track (as a working default it is narrowed to the order of the layers, see point 14) | Confirm or change | Cases |
| 3 | Order of steps in `skills/verify/SKILL.md`: it runs definition alignment first, `lifecycle.md` lists the shape tests first | Align the skill to `lifecycle.md` if the baseline points there | Decide: align or keep | Improvement |
| 4 | The workbook's "fast path" | Map it to `standard_build` against `escalated`; a new path would be a new decision. Finding of 2026-11-13: the sources do not support this mapping as a fact. The workbook (4.3) uses "fast path" in its prose, and its routing table gives the first work profile, "Small, local, reversible, well-patterned", the path "Short specification, focused tests, automated validation". The Route row of the stage table in `lifecycle.md` says "happy path / escalação / bloqueio", and its contract table lists the next states of Route as "Act; Escalated; Rejected". `skills/route/SKILL.md` records `path_chosen: standard_build / escalated / rejected`. `lifecycle.md` treats Blocked and Rejected as different states, and its section 3b lets Blocked be reached from Context and Route; the skill has no blocked value. A `standard_build` item still goes through a named human approval at Approve, which the first row of the workbook table does not list. The cases do not use a path until this is settled | Confirm or change | Cases |
| 5 | Held-out cases | Two held-out cases, in a separate file, written and kept by one of you outside this repository and unseen by whoever writes the improvement; post only the `sha256` here as a comment before the improvement, and later only the pass and fail counts; one run per version. The first version of this point said "two of the six cases". `tests/eval/cases.json` now holds six dev cases, so whether the pair is two of a total of six or two beyond these six is for the group to say | Write the two cases, hold the file, post the `sha256` | Baseline run |
| 6 | Threshold of layer B | One violation of R2, R3 or R4 fails the case | Confirm or change. Also settle whether it is needed before the baseline run (the "Needed before" column) or final only after it ("The baseline comes before any threshold is final", in "Proposed method (not decided)") | Baseline run |
| 7 | Real human approval of REQUEST-007, and the unaligned period (C4) | One of you gives the approval; the period is resolved or recorded | Decide who | Accepted output |
| 8 | Whether `assist` and `customer` are outbound responses. Until the owner of the metric answers, every first response item stays blocked | Ask the owner of the metric | Ask, or say who does | Accepted output |
| 9 | Pull request #5 (another group) already has a Module 4 | Read it only after our design is closed; cite it, do not copy it | Confirm | Report |
| 10 | Three contradictions not in `track.yaml` (C1 to C16): the Verify order above, `skills/context/SKILL.md` requiring `status: open` where the intake evidence list has no `status` field, and the path vocabulary of point 4 | Record them in the report only, each source stated and none chosen; adding them to `track.yaml` changes the list of files | Decide where | Report |
| 11 | The improvement | Choose after the baseline between a metric source the model does not write (the gate) and the Verify order (the skill) | Decide with the baseline | Improvement |
| 12 | Split of the work | (a) cases and layer A, in TDD; (b) live runs and cost, in EDD; (c) report, improvement and description | Slice (a) is taken by the author (`38805d3`). Pick (b) or (c) | Cases |
| 13 | Operating measures, which the Module 4 contract says are decided in class | Report a measure only with the rule that produces it and the file or run it reads; where neither exists it is UNKNOWN. The workbook (4.5) names seven operating measures besides its delivery baseline: correction ratio, iterations to green, convergence rate, escalation rate, cost per accepted feature, architectural violation rate and escaped defect rate. Today none has a value. Iterations to green is UNKNOWN: `traces/gate-decisions.jsonl` has one blocked decision (n=1) and no run reached green. Escalation rate, convergence rate and architectural violation rate need layer B runs. Correction ratio has no record of human edits. Escaped defect rate needs defects reaching production, and nothing is deployed. Cost per accepted feature is undefined while no change has landed. Turns and cost per session are not workbook measures. They exist only as claims in the Module 2 trace and are given as context, labelled as claims. The delivery baseline (deployment frequency, lead time for change, change failure rate, mean time to restore) is reported as not measured, because nothing is deployed; that reason is this description's and not the workbook's. Convergence rate, read as "no human intervention", is reported with the limit that in layer B every accepted run carries an approval supplied by the case and marked `simulated: true` (R4) | Confirm or change | Report |
| 14 | Working defaults of the author for the points that rest on a source. Points 2, 9, 10 and 13 each have a proposal above, and nobody has answered | Until the group answers, the author works with point 9 as proposed; point 2 narrowed to the order of the layers (workbook 4.1), with the routing half not adopted, since the workbook (4.3) names its own routing inputs and mapping them to our path values is point 4; point 10 with the third contradiction; and point 13 as written above. A default is not a decision of the group: anyone can reopen it with a comment at any time, and work done under it is reported as done under it. Points 1, 3, 4, 5, 6, 7, 8 and 11 have no default, and point 12 is split as its row says | Confirm, change or leave; leaving one is not a decision | Cases and report |

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
- Layer A scores exit codes and the `BLOCKED` message, not which check blocked. Each case names in
  `covered_by` the test of `tests/test_handoff_gate.py` that already pins it, so the six cases add a
  table and a validity run, not coverage of the gate. The pointer test checks that the named test
  exists, not that it pins the scenario.
- R2 in layer A mirrors R1: the CLI and the hook both call `check_item`, so R2 fails only if the hook
  adapter diverges from `check`. It scores a write through the `Write` tool, not `Edit` or a shell
  command, and not the absence of the file.
- The case where one note names `self_service_rate` for an item that is really a first response item
  is not a layer A case: its inputs are those of the honest self-service case, which an existing test
  pins at exit 0. It is a candidate for layer B.

## Edits since the first version

- 2026-11-13: slice (a) is built. The draft notice, the status block, the list of files, the slice
  entries in point 12 and in "How to help", the intro of "Decisions for the group", the limitations
  about layer A and the checklist changed accordingly. The R2 row says what layer A scores and what
  only layer B can. Point 4 carries a finding about its sources. Point 5 no longer says "two of the
  six cases", which became ambiguous once `cases.json` held six dev cases. Point 6 records an open
  question. Point 10 lists a third contradiction. Point 13 uses the names of the workbook: the first
  version said "DORA", "turns and cost" and "cost per accepted change", and the workbook uses none of
  the three. Point 14 is new.
- 2026-11-13: the comment of the same day on this pull request has the reasons and the criticisms
  (https://github.com/techindicium/harness-template/pull/7#issuecomment-6856626035). Its criticism 10,
  the stale description, is resolved by this text. Two of its wordings call the path of the first row of
  the workbook table "the fast path": that the workbook "describes the fast path as" the short
  specification, and that "the fast path does not mention" a human approval. The workbook uses "fast
  path" only in its prose, so both say more than the workbook does: see point 4 for the wording that
  holds.

## Review checklist

- [ ] The group answers the fourteen points above.
- [ ] The group agrees the list of files, including `tests/eval/heldout.json`.
- [ ] A named person holds the held-out file and has posted its `sha256` as a comment.
- [ ] `python3 tests/test_handoff_gate.py` passes on a clean checkout.
- [ ] `python3 tests/eval/test_eval_cases.py` passes on a clean checkout.
- [ ] `git status --porcelain` inside the track repository prints nothing.
- [ ] The final description has a "Who did what" section that lists each participant with their commits.
- [ ] The final description has a "Decision record" and a "Next improvement" section.
