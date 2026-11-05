# feat(module-3): independent build check in the handoff gate, Portwell Analytics, group 5

Draft. The group has not yet confirmed the framing in "Decision owned", and has not named the owner
in "Control record".

## Stacked on #4

This pull request is based on `feat/module-2-handoff-gate` (PR #4), which is based on
`grupo-5/module-1` (PR #1). The gate it changes exists only on the branch of #4. Review only the
Module 3 diff: `scripts/hooks/handoff_gate.py`, `tests/test_handoff_gate.py`, one sentence in
`skills/handoff/SKILL.md` and this text.

The base is not retargeted by itself when #4 or #1 is merged. If either is squashed, its work
reappears in this diff. If that happens:

```text
gh api --method PATCH repos/techindicium/harness-template/pulls/<this PR> --field base=main
git rebase --onto main feat/module-2-handoff-gate feat/module-3-build-check
git push --force-with-lease
```

The retarget uses the REST API because `gh pr edit` fails on this repository with a Projects
(classic) error. The force push should be agreed first.

## Intended outcome

The Module 2 gate decides from evidence files that the model writes: `build-<ID>.md` says
`exit_code: 0` and `verify-<ID>.md` says `clear`. It catches evidence that contradicts itself, not a
consistent falsehood (Module 2, "Known limitations"). This change gives the gate two facts it computes
itself, from the data and the SQL of the track repository, instead of from a field of the evidence.
The path of the track and the metric of the item still come from files the model can edit (see
"Known limitations"). The module contract of the Module 3
workbook asks for a rule that exists only as prose to become an executable control, with a regression
case and a recovery message.

## Decision owned

The same one decision as Module 2: **may a Handoff artifact exist for this item?** It gets two more
conditions, in the same gate. The control does not decide whether an interaction by the actor
`assist` is an outbound response. That stays with the owner of the metric named in
`project/metrics/metric-definitions.yaml`.

The scope is decided on purpose. The check of marts applies to every item. The check of actors
applies to an item unless its intake or route note names a metric that does not read the interaction
extract, which today is only `self_service_rate`. A self-service item such as REQUEST-007 is not held
by a defect in first response. No note that names a metric, an unknown metric and two notes that
disagree leave the check of actors on. One note that names `self_service_rate` is enough to skip it.

## Control record

1. **The rule and its current source.** A figure is handed off only when the build behind it is
   complete: every mart the track defines exists and has rows and, for a metric that reads
   interactions, every actor in the
   interaction extract is counted by the first response measure or is declared as not a response.
   Today the rule is prose. The definition says
   "the first outbound interaction" and does not list actors
   (`project/metrics/metric-definitions.yaml`). The interview of 2026-08-12 in the track repository
   says the tests check non-zero row counts, which none of the six does (`track.yaml`, C9).
2. **The failure.** `project/models/marts/first_response.sql` counts `actor IN ('agent', 'portal')`.
   The extract has `agent` 938, `assist` 296 and `customer` 1234 interactions. 296 of 1234 tickets
   drop out of first response and SLA attainment, and the six tests pass (C7). The six tests also pass
   against empty tables (C9). Measured with a read-only query on the built warehouse.
3. **The invariant.** No Handoff artifact exists for an item unless the gate, reading the track
   repository itself, finds every mart it defines present and non-empty and, for an item whose
   metric reads interactions, every extract actor accounted for.
4. **The form.** A guard inside the existing gate, on the same execution path, so the check runs
   where the artifact is written, in the `check` command the handoff skill runs first, and in the
   `Stop` audit. Not a test in the track, because the track is read-only. Not a new hook, because the
   gate already stands on the artifact.
5. **The message and the recovery.** The block says what was refused, why, what was found, what not
   to do, what to do next and the question to put to the user. See "Failure and recovery".
6. **Portability.** See "Not tied to one harness". The model does not matter: the check is plain
   code. The harness matters only to the adapter, which is unchanged. The track repository matters:
   the file paths, the query, `NON_RESPONSE_ACTORS` and `ACTOR_FREE_METRICS` are Portwell's, and sit
   as constants at the top of the script.

Owner of the control: to be named by the group.

## What it checks

| Check | Reads | Not clear when |
| :- | :- | :- |
| `coverage` | `data/ops-extract/interaction.csv` and `project/models/marts/first_response.sql`, in the track | An actor in the extract, compared as written (case and spaces count, as in the warehouse), is not in the `actor IN (...)` list of the mart and not in `NON_RESPONSE_ACTORS`. A mart filter that names an actor the extract lacks is noted in the message and does not block. Skipped when the intake or route note names a metric in `ACTOR_FREE_METRICS` and no other |
| `marts` | The SQL under `project/models/marts` (the tables it creates) and `warehouse.duckdb`, through `.venv/bin/python` of the track, read-only, 30 seconds at most | A table the SQL creates is missing from the warehouse, or any table of its `marts` schema has zero rows |
| `cannot_evaluate` | Everything above, and `track.yaml` | `track.yaml` is missing or has no `context_repository`; the path is not the pinned track (`TRACK_REPOSITORY`) or not a directory; the extract or the mart is unreadable, has no actor column, no rows, or not exactly one plain `WHERE ... actor IN (...)` filter (a second filter, a `NOT`, an `OR` or a `CASE` in the way, or none); no SQL creates a mart; the warehouse or the interpreter is missing, exits with an error, times out or answers with something that is not `<mart> <rows>` |

`NON_RESPONSE_ACTORS` holds `customer`. That is an assumption of the group, written in a comment at
the constant: the owner of the metric has not recorded it. With today's extract the only actor that
fails is `assist`.

`ACTOR_FREE_METRICS` holds `self_service_rate`, whose mart reads tickets and suggestions only
(`project/models/marts/self_service.sql`, measured with `grep` on its `FROM` and `JOIN` lines and on
the staging models behind them).

The track is pinned in the script: `TRACK_REPOSITORY` holds `../portwell-analytics`, relative to
the project root. `context_repository` in `track.yaml`, which is next to the `evidence/` directory
the gate already uses, has to name the same directory once resolved (`../portwell-analytics/` and
an absolute path to it both do); any other directory is `cannot_evaluate`, so the two cannot drift
apart unnoticed. `track.yaml` is a data file the model edits as part of the lifecycle; the script is
code that goes through review, like `NON_RESPONSE_ACTORS`. The signature of `check_item` does not change, so the hook, the
audit and the `check` command all get the checks.

## What else changes

`format_block` computed one reason for every question. The first run on the real item showed the
question about the actor citing the verify status. Each question now cites the first failure of its
own check, and a reason with no field is not prefixed by a dash. Two tests pin this.

`skills/handoff/SKILL.md`, step 1, gets one sentence that says what the check reads in the track and
that a track it cannot read counts as not clear. The skill is what tells a model what `check` does.

## Where it is enforced

Nothing changes in `.claude/settings.json`. The two existing entries (`PreToolUse` on
`Write|Edit|Bash`, and `Stop`) call the same script, and the new checks run inside the decision they
already make. The limits of Module 2 hold: the gate applies to sessions started at the repository
root.

## Not tied to one harness

The three layers of `scripts/hooks/handoff_gate.py` are unchanged. The core and the CLI
(`check <ID>`, `audit`) know no harness. The only thing the gate needs from the track is its
interpreter: the system `python3` has no `duckdb` (measured: `ModuleNotFoundError`), so the gate asks
the warehouse through `<track>/.venv/bin/python -I`, with a read-only connection. A pre-commit or a
CI job can call `check` and gets the same checks. The messages name no product or model.

## Failure and recovery

Captured from the gate run on a throwaway project with clear evidence, an intake note that names
`first_response_minutes_p50`, and the real track (see "Evidence"). REQUEST-007 itself asks for
self-service and does not print this block. Only the lines of the actor check are shown:

```text
WHY:
  A figure is only as complete as the actors the mart counts. An actor in the extract that the mart
  neither counts nor declares as not a response drops its tickets from the figure, and no shape test
  fails.
FOUND:
  data/ops-extract/interaction.csv: actor is assist (296 interactions), expected counted by
  first_response.sql (agent, portal; portal is not in the extract) or declared as not a response
NEXT:
  Do not edit the mart (the track repository is read-only) and do not add the actor to
  NON_RESPONSE_ACTORS yourself. Ask the user to put the question to the owner of the metric. Do not
  deliver meanwhile.
ASK THE USER:
  "For REQUEST-007: actor is assist (296 interactions). Is an interaction by that actor an outbound
  response, and who owns the decision?"
```

The recovery has two exits, and both belong to people. If the owner says `assist` is a response, the
fix is in the mart of the track, which this repository cannot change. If the owner says it is not,
the actor is added to `NON_RESPONSE_ACTORS` in a reviewed change to the script. Until then the gate
keeps refusing.

## Evidence

- **Reproducible.** `env PYTHONDONTWRITEBYTECODE=1 python3 tests/test_handoff_gate.py` passes 70
  tests: the 46 of Module 2 with their assertions unchanged, and 24 new ones. Only the test helper
  `project()` changed for the old tests: it now builds a clean track by default, beside the project
  under the pinned name, as the real layout has it. REQUEST-007 asks
  for self-service, so the real item is not held by the actor check. From the repository root with
  `../portwell-analytics` built, the two commands print the same message and both exit 1, because
  the evidence of REQUEST-007 is blocked:

  ```text
  git show 1c2c19b:scripts/hooks/handoff_gate.py | python3 -I - check REQUEST-007
  python3 -I scripts/hooks/handoff_gate.py check REQUEST-007
  ```

  The decision for an item that reads interactions is pinned by
  `test_the_handoff_is_blocked_although_the_evidence_is_clear` and
  `test_the_actor_check_applies_unless_the_evidence_names_such_a_metric`. The same decision on the
  real track is in the last-but-one bullet.
- **Red first.** The helper and the new cases were written before the script changed: 55 tests, the 45
  old ones passing and 7 of the 10 new ones failing (14 failures and 2 errors, counting sub-tests). Two more cases were added after
  the first run on the real item found the reason defect above, and failed before the fix. Three
  cases for the scope were added after the decision on the scope: the exemption case failed before
  the change, and the other two guard the other side (the check stays on, and the marts check is not
  scoped). Two reviews of the diff then found paths where something unreadable or unexpected let an
  item through: a mart missing from the warehouse, a filter hidden in a comment, a `NOT` or a `CASE`
  around the filter, an extract with no rows, interpreter output that is not text, and an actor padded
  with a space or written in another case. Each got a case that failed before its fix. The second
  review also showed that four guards of the filter reader (`NOT`, `CASE`, `;` and a line comment)
  were refused by other checks and pinned by no case. Each now has a case with exactly one actor
  filter, so counting filters cannot be what refuses it. Thirteen mutations of the script each turn a
  test red on a scratch copy: a lost `read_only=True`, a lost `-I`, strict decoding, a missing mart
  not reported, block comments not stripped, line comments not stripped, an extract with no rows
  accepted, a trimmed actor, each of the four guards of the filter reader (`NOT`, `CASE`, `;`, `OR`),
  and any `CASE` in the mart refused. The last one turns 33 red, because the real mart has a `CASE`
  and must not be refused for it.
- **Reported, not versioned.** Throwaway projects with clear evidence, an intake note and a
  `track.yaml` pointing at the real track, for a write of `delivery/figures-REQUEST-007.csv`. For an
  item whose metric is `first_response_minutes_p50`, the gate of `1c2c19b` let the write through
  (exit 0) and the new gate blocked it (exit 2) with the message above. For an item whose metric is
  `self_service_rate`, both let it through (exit 0). Neither run failed with `marts` or
  `cannot_evaluate`, so the real query ran through the real interpreter and every mart it listed has
  rows.
- **The pinned path, red first.** The helper moved to the real layout (project and
  `portwell-analytics` side by side) and the three cases of the pin were written before the script
  changed: the 66 cases passed, the case of a `track.yaml` repointed at a clean copy (relative and
  absolute) and the case of a missing pinned track failed, and the case of the pinned track written
  another way (absolute, trailing slash, `../decoy/../portwell-analytics`) passed, as it must. Then
  all 69 passed. On a throwaway project beside a clone of the real track, with clear evidence, an
  intake note that names `first_response_minutes_p50` and `track.yaml` repointed at a clean copy of
  the real extract and marts with `assist` added to the filter, the gate of `9526e46` exits 0 on
  `check` and the new one exits 1 with `context_repository is another directory than the pinned
  track`; a `Write` of `delivery/figures-REQUEST-007.csv` through the hook exits 2. Pointed back at
  the real track, it is blocked on `assist` (296 interactions). That clone was not built, so the
  marts check answered `warehouse.duckdb does not exist`; the run with a built warehouse was not
  repeated after the pin. `git status --porcelain` in the track printed nothing.
- **Not verified.** A live session at the repository root with the new checks. It needs an interactive
  session, as in Module 2.

## Known limitations

- The path of the track is pinned in the script (`TRACK_REPOSITORY`). Repointing `context_repository`
  in `track.yaml` at a directory with a clean extract, a mart filter that names `assist` and a
  stand-in interpreter used to make an item that the real track blocks pass; it is now
  `cannot_evaluate` (see "Evidence"). What is left is the class of the Module 2 limitation: the model
  can edit the script, and the read-only hook covers `Write` and `Edit` only, so a shell command could
  still replace `../portwell-analytics` itself, for example with a link to another directory (the
  gate resolves links, and a link that resolves to the pinned path is accepted). Review of the diff
  is the defense. A clone of the track under another name or in another place is refused until
  `TRACK_REPOSITORY` is changed in a reviewed commit.
- The reader of the mart filter is a heuristic. It expects exactly one `actor IN (...)` under a
  `WHERE`, with no `CASE`, `NOT` or `OR` in between; a mart in another shape is `cannot_evaluate`. A
  mart that keeps that shape and changes meaning elsewhere, such as a join that drops tickets, is not
  seen.
- The actor check is skipped on the word of a note the model writes. The `metric_name` of the intake
  or route note decides whether the check applies, so a model that writes `self_service_rate` for an
  item that delivers first response figures switches the check off. Only that one metric is exempt.
  One note is enough to skip the check, so a single line in the intake note does it; no note that
  names a metric, an unknown metric and two notes that disagree leave the check on. This is the
  weakness the control removes elsewhere, kept here on purpose so that a self-service item is not
  held by a defect in first response.
- The check of marts is not scoped: a missing or empty mart blocks every item, whatever its metric.
  The marts the warehouse must hold are the tables the SQL under `project/models/marts` creates. A
  stale empty table of the `marts` schema that no SQL creates also blocks.
- With today's extract, every item whose metric reads interactions is held until the owner decides
  about `assist` or the mart is corrected. Both exits depend on people outside the group.
- The gate reads the warehouse that exists now. It is a gitignored file, and nothing ties it to the
  build of this item. `staging.extract_metadata` records the build time and not the extract time (C10).
- The actor check reads the extract CSV and the marts check reads the warehouse. A warehouse built from
  another source (`run.py --live` points at a repository that is not cloned here) is not the CSV the
  gate counts.
- A mart with rows is not a correct mart. The check is that the build produced something.
- The tests of the interpreter use a stand-in shell script. They show how the gate reads an answer
  and that it fails closed. One of them records the arguments and pins `-I`, `-c`, the path of the
  warehouse and `read_only=True` in the text of the query. None runs the query: it was run for real,
  in the run reported above. The stand-in works on POSIX systems only.
- The path `.venv/bin/python` is the default of the track's `setup.sh`. If `VENV` is set to another
  directory, the gate cannot run and fails closed.
- `customer` as a non-response actor is an assumption. Whether `assist` counts is the owner's
  decision and is open.
- The gate runs the interpreter of the track repository from a hook. The query is read-only and the
  interpreter runs in isolated mode. The 30 second limit is a value with no measurement behind it
  beyond a query that takes about a tenth of a second.
- A `delivery/` directory copied next to evidence that has no `track.yaml` beside it is now blocked,
  because the gate cannot find the track.
- The version of the metric definition in the marts (POLICY-13) is not covered: the marts are in the
  read-only track repository.
- The remaining limitations of Module 2 are unchanged, including the four decisions not taken.

## Next improvement

- **TODO for the next review, by decision of the group:** adopt `onFailure: "block"` (documented for
  command hooks from Claude Code v2.1.295). It would turn a script error (exit 1) and a missing
  `python3` (exit 127) into a block on `PreToolUse`. It also makes a broken gate block the `Edit` that
  would repair it, so the repair has to be made outside the session. It is not set and was not tested.
- Find a source for the metric of an item that the model does not write, so the scope of the actor
  check does not rest on a note the model fills in.
- Ask the owner of the metric about `assist` and `customer`.
- Moving the control from the project settings to an organizational one (managed settings) is not
  part of this change. It needs administrator access, and nobody has confirmed that the group has it.

## Who did what

Provisional: the rest of the group is to add its part.

- **Yuri Alves:** designed the control and wrote the two checks of the track (`coverage` and
  `marts`), the per-check reasons of `format_block`, the sentence in `skills/handoff/SKILL.md`, the
  21 cases for them and this text (`01b2165`, `f20d73b`); ran the gate on the real item and the
  throwaway projects, and fixed what the two reviews of the diff found (`9526e46`).
- **Gabriel Campos:** reviewed the pull request; pinned the path of the track in the gate
  (`TRACK_REPOSITORY`), moved the test helper to the real layout and wrote the three cases of the
  pin red first; reproduced the repointed `track.yaml` against the gate before and after the change,
  and updated this text to match (`463ca69`).

## Review checklist

- [ ] The group confirms that two checks computed inside the existing gate are the Module 3 control.
- [ ] `python3 tests/test_handoff_gate.py` passes on a clean checkout.
- [ ] `git status --porcelain` inside the track repository prints nothing.
- [ ] The group confirms the scope: the actor check applies unless the evidence names an actor-free
  metric, and the marts check applies to every item.
- [ ] The group accepts that the path of the track is pinned in the script to `../portwell-analytics`
  and that every member clones the track there.
- [ ] The owner of the metric is asked whether `assist` and `customer` are outbound responses.
- [ ] The merge method for #1 and #4 is agreed, or the retarget steps in "Stacked on #4" are accepted.
