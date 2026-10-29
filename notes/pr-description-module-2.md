# feat(module-2): handoff gate for the DDLC lifecycle, Portwell Analytics, group 5

Draft. The group has not yet confirmed the framing in "Decision owned".

## Stacked on #1

This pull request is based on `grupo-5/module-1` (PR #1), not on `main`, because the Module 1
skills and evidence exist only on that branch (`main` has the nine skills with `TODO`). Review only
the Module 2 diff.

The base is not retargeted by itself when #1 is merged. The repository allows squash, merge commit
and rebase merges and does not delete the head branch on merge. If #1 is squashed, the Module 1
work reappears in this diff. If that happens:

```text
gh api --method PATCH repos/techindicium/harness-template/pulls/<this PR> --field base=main
git rebase --onto main grupo-5/module-1 feat/module-2-handoff-gate
git push --force-with-lease
```

The retarget uses the REST API because `gh pr edit` fails on this repository with a Projects
(classic) error. The force push should be agreed first. Asking whoever merges #1 to use a merge
commit avoids it.

## Intended outcome

A rule that lived only as prose in the `handoff` skill becomes a check on the execution path: an
artifact of Handoff for an item cannot be written unless the evidence of the same item says it is
clear. Section 2.6 of the workbook calls a rule that exists only as prose advisory.

## Decision owned

One decision: **may a Handoff artifact exist for this item?** It joins the Verify and Approve
conditions that Handoff already declares as entry conditions, so the control is one gate with one
decision. The workbook asks for exactly one extension; the group chose "verify plus the approver
gate", and this is the reading that keeps it to one. If the group prefers one half only, the checks
are a list at the top of the script and one can be dropped without changing the structure.

## What it checks

An artifact is a file named `handoff-<ID>.md` (kept in `evidence/`) or `figures-<ID>.csv` (kept in
`delivery/`), in any directory. It is allowed only when the evidence of the same `<ID>` has:

| Evidence | Required |
| :- | :- |
| `approve-<ID>.md` | `approved_by` a person's name (not empty, `UNKNOWN`, `none`, a placeholder or a role), `approved_at` an ISO date. `status` is not read: the `approve` and `handoff` skills define the approval as these two fields and `status` as a label |
| `verify-<ID>.md` | `verify_status: clear` with the three verdicts `pass`, `aligned` and `match` |
| `context-<ID>.md` | `period_match: true` |
| `build-<ID>.md` | `exit_code: 0` |

A missing file, a missing field, an unreadable file or a field that appears twice with different
values counts as not clear. A clear status next to a verdict that is not clear is reported as
evidence that contradicts itself.

## Where it is enforced

`.claude/settings.json` has two new entries, next to the read-only hook, which is unchanged:

| Event | Matcher | Covers |
| :- | :- | :- |
| `PreToolUse` | `Write\|Edit\|Bash` | direct writes, and shell commands that name an artifact and do more than read |
| `Stop` | none | an audit of the project, in any directory: if an artifact exists for an item that is not clear, the first stop is refused and the next one is let through (loop guard) |

The hook command is anchored on the project directory variable, so a change of directory cannot
make it fail to start. That matters because a failure to start is not a decision of the gate: a
missing script makes `python3` exit 2, which blocks every Write, Edit and Bash call with Python's
message, while a missing `python3` or an error in the script exits with a code that blocks nothing.

## Where it applies

The project settings file is read from the directory the session starts in. The gate therefore
applies to sessions started at the repository root, and not to a session started in a parent
folder, in a subfolder of the repository or in the track repository. This comes from the Claude Code
settings documentation and was not tested in a live session. The read-only hook from Module 1 has
the same limit.

- To check it, run `/status` and confirm that the project settings are listed. Inside a session,
  `/cd` to the repository root reloads them (Claude Code v2.1.246 or later).
- The `handoff` skill runs the same check as its first step and stops on any non-zero exit. That
  step does not depend on the hooks being loaded, only on the skill being followed. It was added
  after the live runs recorded in the trace, which used the skill without it.
- Making the gate apply in every folder needs a control outside the project settings, such as
  managed settings, which apply wherever the session starts. The workbook places the organizational
  control in Module 3.

## Not tied to one harness

`scripts/hooks/handoff_gate.py` has three layers. The core is pure functions and does not know any
harness. The CLI (`check <ID>`, `audit`) reads the repository and exits 0 when clear and 1 when not
(64 on a usage error). The hook adapter
reads one hook event and answers with the blocking exit code. Another harness, a pre-commit or a CI
job can call the CLI without the adapter, and `audit` finds an artifact whichever tool or person
created it. The block message is plain labeled text and names no product or model.

## Paths and bypass

The target is matched by file name, at any depth, and the evidence directory is derived from the
target. An absolute path, a relative path, `.` and `..`, a symlink, upper case and a change of
directory before the write all reach the same decision. A shell command is split on unquoted
operators and a segment is let through only when its command only reads (no redirect, no command
substitution, no output option) or only removes, so a stray artifact can be cleaned up. An event the
gate cannot parse
but whose text names an artifact is blocked. A name built at run time is not visible to a command
check; the `Stop` audit finds that artifact afterwards.

## Failure and recovery

Every block says what was refused, why, what was found in each evidence file, what not to do, what
to do next, and the question to put to the user. The agent is told not to retry through another path
and not to edit the evidence to satisfy the gate. The message for a missing approver asks "Who is
the named approver for <ID>?", then one question for each other failed check.

## Evidence

A reviewer can check some of this from the branch and not the rest. Section 12 of
`traces/module-2-trace.md` lists each point as reproducible, in the repository, or reported.

- **Reproducible.** Same payload without a model: the existing hook exits 0, the gate exits 2. The
  commands are in section 12 of the trace. Regression matrix: `python3 tests/test_handoff_gate.py`
  passes 45 tests, both sides pinned.
- **In the repository.** Decision log written by the gate: `traces/gate-decisions.jsonl`. Targets are
  recorded relative to the project root. The live run's own line carried the absolute path of the
  machine, so the log was fixed and the line regenerated by running the wired command on the same
  payload.
- **Reported, not versioned.** Before and after, same three requests, in live sessions
  (`traces/module-2-trace.md`, section 4). Before the gate, the pressure request ("write the handoff
  file anyway") produced a write to the protected path and nothing stopped it. After, the gate
  blocked the write, the file was not created, and the model asked the open questions and did not
  look for another path. The raw records of those sessions are not committed, because they carry
  local paths and the names of the operator's own plugins and servers. They stay on the operator's
  machine and a reviewer cannot open them, so these rows are claims, not evidence a reviewer can
  check.

## Stop and escalation conditions

The gate stops the write and gives the question to put to the user. It never records an approval,
never edits evidence, and never decides whether to publish with a version mismatch: that stays with
the Analytics lead, whose name is UNKNOWN in the evidence.

## Inherited behavior it depends on

Only exit code 2 blocks a `PreToolUse` hook. Hooks for one event run in parallel and a deny wins
over the other decisions. On a block, a hook's stderr reaches the model as the tool error, and on
`Stop` as the reason to continue. The stop event carries `stop_hook_active`, true while the session
is already continuing because of a stop hook, and the harness caps consecutive continuations (eight
by default, counted again after each tool call). These come from the Claude Code hooks
documentation.

## Known limitations

- The gate applies only to sessions started at the repository root (see "Where it applies").
- The records of the live sessions are not versioned, so a reviewer cannot check the before and
  after sessions. The payload runs and the regression matrix can be re-run (see "Evidence").
- The gate trusts fields the model can also write: it catches evidence that contradicts itself, not
  a consistent falsehood.
- A refusal record cannot be written at the protected path, because the gate keys on the path and
  not the content. Not decided how to record refusals.
- The model could edit the settings or the script to switch the gate off; review of the diff is the
  defense in this module.
- Live sessions allowed no `Bash`, so a shell bypass was not tried live. The matrix and payload runs
  cover it.
- A redelivery reuses the file name, so the gate cannot tell it from a first delivery.
- Whether the working directory in the hook payload follows an earlier change of directory in the
  same session was not measured.
- The audit is not wired into a pre-commit or a CI job.
- Only `handoff-<ID>.md` and `figures-<ID>.csv` are protected. The restatement delivery
  `delivery/restatement-<ID>.csv` that the recover skill defines, and any renamed variant such as a
  `-v2` suffix, are not matched. Whether to widen the set is not decided.
- The evidence directory is derived from where the artifact is, so clean evidence placed next to a
  copied `delivery/` directory satisfies the gate for the copy. Anchoring it on the project root is
  not decided.
- The `Stop` audit is a single nudge. The loop guard lets the next stop through, so an artifact
  that nobody removes stays and is flagged again at the end of each later turn.
- The shell check is textual. A command that names an artifact and is not on the read-only list
  (`sed -n`, `awk`, `find`, a commit message or a heredoc body that mentions the name) is treated
  as a write and blocked while the item is not clear.
- Only exit code 2 blocks. A syntax or import error in the script (exit 1) or a missing `python3`
  (exit 127) lets the action through. Claude Code documents `onFailure: "block"` for command hooks
  from v2.1.295, which turns those failures into a block on `PreToolUse` and has no effect on
  `Stop`. It is not set and was not tested here.
- Every gated decision, `allow` included, is appended to the versioned
  `traces/gate-decisions.jsonl`. Whether the log stays versioned is not decided.
- The approver check is a list of words. A value that is not a person and is not on the list, such
  as a job title that uses no listed word, passes.

## Next improvement

Decide how a refusal is recorded without a path the gate protects. Add an independent check on the
build output that does not rely on fields the model writes. Run the audit in a pre-commit or CI job.
Move the control from the project settings to an organizational one (Module 3).

## Who did what

To be filled by the group. This section is intentionally empty.

## Review checklist

- [ ] The group confirms that one gate with one decision is the extension for this module.
- [ ] `python3 tests/test_handoff_gate.py` passes on a clean checkout.
- [ ] `git status --porcelain` inside the track repository (the context repository named in
  `track.yaml`) prints nothing.
- [ ] The merge method for #1 is agreed, or the retarget steps in "Stacked on #1" are accepted.
