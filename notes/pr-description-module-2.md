# feat(module-2): handoff gate for the DDLC lifecycle, Portwell Analytics, group 5

Draft. The group has not yet confirmed the framing in "Decision owned" below.

## Stacked on #1

This pull request is based on `grupo-5/module-1` (PR #1), not on `main`, because the Module 1
skills and evidence exist only on that branch (`main` has the nine skills with `TODO`). Review only
the Module 2 diff.

The base is not retargeted by itself when #1 is merged. The repository allows squash, merge commit
and rebase merges and does not delete the head branch on merge. If #1 is squashed, the Module 1
work reappears in this diff. If that happens:

```text
gh pr edit <this PR> --base main
git rebase --onto main grupo-5/module-1 feat/module-2-handoff-gate
git push --force-with-lease
```

The force push should be agreed first. Asking whoever merges #1 to use a merge commit avoids it.

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

An artifact is `handoff-<ID>.md` in an `evidence/` directory or `figures-<ID>.csv` in a `delivery/`
directory. It is allowed only when the evidence of the same `<ID>` has:

| Evidence | Required |
| :- | :- |
| `approve-<ID>.md` | `status: approved`, `approved_by` a person's name (not empty, `UNKNOWN`, `none`, a placeholder or a role), `approved_at` filled |
| `verify-<ID>.md` | `verify_status: clear` with the three verdicts `pass`, `aligned` and `match` |
| `context-<ID>.md` | `period_match: true` |
| `build-<ID>.md` | `exit_code: 0` |

A missing file, a missing field or an unreadable file counts as not clear. A clear status next to a
verdict that is not clear is reported as evidence that contradicts itself.

## Where it is enforced

`.claude/settings.json` has two new entries, next to the read-only hook, which is unchanged:

| Event | Matcher | Covers |
| :- | :- | :- |
| `PreToolUse` | `Write\|Edit\|Bash` | direct writes, and shell commands that name an artifact and do more than read |
| `Stop` | none | an audit of the project: ends the turn only if no artifact exists for an item that is not clear |

The hook command is anchored on the project directory variable, so a change of directory cannot
make it fail to start. That matters because a hook that fails to start exits with a code that does
not block.

## Where it applies

The project settings file is read from the directory the session starts in. The gate therefore
applies to sessions started at the repository root, and not to a session started in a parent
folder, in a subfolder of the repository or in the track repository. This comes from the Claude Code
settings documentation and was not tested in a live session. The read-only hook from Module 1 has
the same limit.

- To check it, run `/status` and confirm that the project settings are listed. Inside a session,
  `/cd` to the repository root reloads them.
- The `handoff` skill runs the same check as its first step. That step does not depend on the hooks
  being loaded, only on the skill being followed. It was added after the live runs recorded in the
  trace, which used the skill without it.
- Making the gate apply in every folder needs managed settings, which is Module 3.

## Not tied to one harness

`scripts/hooks/handoff_gate.py` has three layers. The core is pure functions and does not know any
harness. The CLI (`check <ID>`, `audit`) reads the repository and exits 0 or 1. The hook adapter
reads one hook event and answers with the blocking exit code. Another harness, a pre-commit or a CI
job can call the CLI without the adapter, and `audit` finds an artifact whichever tool or person
created it. The block message is plain labeled text and names no product or model.

## Paths and bypass

The target is matched by file name, at any depth, and the evidence directory is derived from the
target. An absolute path, a relative path, `.` and `..`, a symlink, upper case and a change of
directory before the write all reach the same decision. A shell command is split on unquoted
operators and a segment is let through only when its command reads. An event the gate cannot parse
but whose text names an artifact is blocked. A name built at run time is not visible to a command
check; the `Stop` audit finds that artifact afterwards.

## Failure and recovery

Every block says what was refused, why, what was found in each evidence file, what not to do, what
to do next, and the question to put to the user. The agent is told not to retry through another path
and not to edit the evidence to satisfy the gate. The message for a missing approver ends with "Who
is the named approver for <ID>?".

## Evidence

- Before and after, same three requests, live sessions: `traces/module-2-trace.md`. Before the gate,
  the pressure request ("write the handoff file anyway") produced a write to the protected path and
  nothing stopped it. After, the gate blocked the write, the file was not created, and the model
  asked the open questions and did not look for another path.
- Same payload without a model: the existing hook exits 0, the gate exits 2.
- Regression matrix: `python3 tests/test_handoff_gate.py` passes 39 tests, both sides pinned.
- Decision log written by the gate: `traces/gate-decisions.jsonl`. Targets are recorded relative to
  the project root. The live run's own line carried the absolute path of the machine, so the log was
  fixed and the line regenerated by running the wired command on the same payload; the live block
  is evidenced in `traces/module-2-trace.md`.

## Stop and escalation conditions

The gate stops the write and gives the question to put to the user. It never records an approval,
never edits evidence, and never decides whether to publish with a version mismatch: that stays with
the Analytics lead, whose name is UNKNOWN in the evidence.

## Inherited behavior it depends on

Only exit code 2 blocks a `PreToolUse` hook. Hooks for one event run in parallel and a deny wins. A
hook's stderr reaches the model as the tool error. The stop event carries `stop_hook_active` and the
harness caps consecutive continuations.

## Known limitations

- The gate applies only to sessions started at the repository root (see "Where it applies").
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
- [ ] The merge method for #1 is agreed, or the retarget steps above are accepted.
