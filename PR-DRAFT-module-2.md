# Module 2: a context contract for the `verify` skill, enforced by hooks (Grupo 3, PDLC)

Draft for review. The pull request has not been opened.

## Summary

This PR adds one extension to the Module 1 harness: a context contract for the `verify` skill, enforced by Claude Code hooks (`PreToolUse`, `PostToolUse`, `Stop`). While a `verify` run is active, the hook denies prohibited reads and all writes, and it blocks the end of the run until the required files were actually read and the report states the right number of lines of the transition log.

The evidence is in two layers that are kept apart below. A model-free self-test and a mutation table prove the **logic** of the hook. One live session, which is exploratory, shows a `Stop` block reaching the model and the model correcting its report. The PR does **not** prove that Claude Code honors a `deny` in `auto` mode, the before/after comparison the workbook asks for, or that the group's skill runs as a skill. See "What is NOT proven".

Scope: the narrow reading of Module 2 (one extension surface with a context contract, a permission limit, a trace and recovery). The two safe tools of the wider reading in `STUDENT-GUIDE.md` are not built and wait for the track assistant's answer.

## Decision owned

The extension owns two decisions during a `verify` run:

1. **May this tool call happen?** `Read`, `Grep`, `Glob`, `Write` and `Edit` can be denied. `Bash` is recorded and never denied.
2. **May this run end?** Only when the required context was read and the report's stated line count for `traces/transition-log.md` equals the real count.

It does not decide the verdict (PASS or FAIL), whether evidence is sufficient, or anything about BLOCKER-01.

## Inputs and outputs

**Inputs**
- Hook events on stdin as JSON: the common fields (`session_id`, `cwd`, `permission_mode`, `transcript_path`, `hook_event_name`) plus `tool_name` and `tool_input` for the tool events, and `last_assistant_message` for `Stop`.
- The contract, `harness/verify-contract.json`: required reads, prohibited names and substrings, the two roots (the project and the `context_repository` of `track.yaml`), write tools, protected paths, the context limit, the number of checks and denials.
- The skill text and the transition log, read by the hook only to count data lines.

**Outputs**
- `PreToolUse` deny: `{"hookSpecificOutput": {"permissionDecision": "deny", "permissionDecisionReason": "..."}}`, exit 0. The reason carries a recovery action.
- `Stop` block: `{"decision": "block", "reason": "..."}`. At the last check, `{"systemMessage": "..."}` and the run ends.
- A run trace, one JSON line per decision, in `traces/verify-runs/<session_id>.jsonl`. Raw per-session state (a marker and the read registry) stays in `.claude/verify-state/` and is not part of the PR.
- Exit code 1 (a visible, non-blocking error) when the hook script is missing, by a guard in the configured command. See "Findings".

The control is inert unless a run is active. A run starts on a `Skill` call to `portwell-group-harness:verify` or on a read of `skills/verify/SKILL.md` (the weaker trigger).

## Permission boundary

| Action | Rule | Strength |
| :- | :- | :- |
| `Read`, `Grep`, `Glob` on a prohibited path (`SEED-MANIFEST.md`, any `heldout`) or outside the two roots | Denied. Paths are resolved (`..`) before the check | Prevented |
| `Grep` over a folder that holds a prohibited path | Denied (a recursive search would read it) | Prevented. The scan fails open above 20,000 entries |
| `Read`, `Grep`, `Glob` beyond the limit (30, provisional, counts these three tools only) | Denied | Prevented. The value has no measurement behind it |
| `Write`, `Edit` | Always denied during a run | Prevented |
| `Write`, `Edit` on the control (`.claude/**`, `scripts/hooks/**`, the contract, the traces) | Denied with a "protected" message | Prevented |
| `Bash` | Allowed and recorded, with flags for write-looking commands and prohibited path text | Recorded only. Not prevented |
| `NotebookEdit` | Not in the matcher | Not covered |

## Refusal behavior

Every refusal says what to do next. Examples: a prohibited path is refused with "report the fact as 'unknown' with the pointer. Do not retry this path"; a write with "Return the report in the final message"; a missing required read at `Stop` with the file and why (never tried, tried but did not complete because another hook may have blocked it, or read only in part). Three denials in one run halt it: every further call is denied and the author is named as the escalation point.

## Stop and escalation conditions

- A denied call: the run continues, with the recovery message.
- Third denial in one run: the run is halted.
- `Stop` check fails: the first and second checks block, the third ends the run with `status: escalated` and a warning to the author. The limit of three is an author hypothesis, the same as in `lifecycle.md`, and is not validated.
- A user interrupt or an API error: the contract is not checked (a documented limit of `Stop` hooks).

## Evidence

### Layer 1: self-test and mutation (proves the hook logic)

Command: `python tests/verify_contract_selftest.py`. It feeds fixture hook inputs to the script in a throwaway project and checks exit codes, output JSON and state files. No model and no Claude Code session are involved.

Final result, run against the active `.claude/settings.json`, with no tests skipped:

```
Ran 43 tests in 46.077s
OK
selftest exit code: 0
```

Hashes of the files this result is about (first 16 characters of sha256): hook `1566f5d7e81bc2a6`, contract `c7fe7e615bb97be8`, settings `f055fe45e4d7de7d` (the active settings and `harness/settings.definitive.json` are identical, and a test checks it), self-test `4799b31a7e53b2f8`.

How the self-test was built: written first and run red against a stub that only exits 0, then the hook was written until it passed. Two outside observations then added red tests before fixes: a `..` that escaped the roots, and a recursive `Grep` over a folder that holds a prohibited file. A third change, tolerance for backticks around the path in the `Context read` line, also started from a red test.

**Mutation table, against the final hook.** For each rule, the rule is switched off in a **copy** of the hook (or of the configuration), the self-test is run against the copy, and the matching test must go red. The real files are never edited. Their hashes are compared before and after, and a baseline run closes the table.

MUTATION_TABLE_PLACEHOLDER

### Layer 2: one live session, Run 0 (exploratory)

Marked exploratory because: **no failure was induced** (the request was only a command, with no instruction that pushes toward the failure); the **plugin was not loaded** (the session came from the VS Code extension, and `/portwell-group-harness:verify` was an unknown command to Claude Code); the **skill was followed by reading its path**, by the model, by hand, and the model said so in its report.

What the transcript and the run trace show (observed):

- The hooks configured in the project's `.claude/settings.json` fired in a fresh session in `auto` permission mode.
- The run activated by the weaker trigger (a read of `skills/verify/SKILL.md`).
- The first report was **blocked** at `Stop` for the format of the `Context read` line: the model wrote the log path in backticks followed by the count, and the hook did not match it. The block message reached the model as "Stop hook feedback".
- The model answered "Verify report, corrected. The first version put backticks around the log path, so the hook couldn't match the data-line count", gave the report again, and the second check passed (`status: satisfied`).
- Nine reads were allowed and six `Bash` calls recorded. No call was denied. No hook error notice appeared.

What this layer supports: a `Stop` block, delivered by the hook, changed what the model did on the next round. What it does not support: anything about a `deny`, about the failure the extension was built for, or about the skill running as a skill.

## What is NOT proven

- **That Claude Code honors a `deny` from `PreToolUse` in `auto` mode.** No call was denied in the live session. The documentation says a `deny` holds in every permission mode. That is the documentation's claim, not an observation here.
- **The before/after comparison the workbook asks for.** Runs A (control off), B (control on, failure induced) and C (a prohibited read) from `docs/module-2-run-prompts.md` were not done.
- **That the group's skill runs as a skill.** In every live session so far the Module 1 skill was read by path. The namespaced command was unknown (plugin not loaded), and the bare `/verify` loads a skill bundled with Claude Code.
- **That the final hook passes the full mutation table**, except as the table above states for the final hook's hash.
- That the guard for a missing script works under the shell Claude Code uses for a missing script (it ran under that shell with the script present, and was tested for the missing case through `cmd.exe` only).

## The failure that was induced, and the failures that were observed

**No failure was induced in a live run.** The planned induced failure ("Do not read `traces/transition-log.md`") is in the run prompts and was not run.

Failures that were **observed** (they motivated or shaped the build):

1. **Exit 2 on a missing script.** When the hook script does not exist, Python exits with code 2, and exit 2 blocks a tool call. With a plain `python script` command, a missing or misnamed script would block every covered tool call. Observed in the first red run. The configured command now checks that the script exists and exits 1 instead (a visible, non-blocking error).
2. **The mandatory context was not read** in the preparation run: `verify` lists `traces/transition-log.md` under "Required context" and did not read it, and its report said "The only log line is line 1" when the log had two. This is the failure the contract exists for. It was observed in a run of the unmodified harness, not reproduced under the control.
3. **A name collision.** `/verify` loads a skill bundled with Claude Code, not the Module 1 skill of the same name. Observed in two sessions.

## Findings

- **The `Context read` line format is rigid, and it cost one block round** in the live session. The skill gives the format in backticks around the whole phrase. The model put them around the path only. The hook now accepts a backtick after the path. The tolerance is for the format; the number is still compared with the file.
- **The `write_pattern` flag on `Bash` has false positives.** Three read-only `python -c` commands in the live session were flagged because their regular expressions contain `<` and `>`. It is a record, never a denial.
- **The `Grep` sweep fails open above 20,000 entries.** The value is a placeholder with no measurement behind it.
- **`NotebookEdit` is outside the matcher.** A write through that tool is not covered.
- **`Bash` is recorded, not prevented.** A shell command can read a prohibited file or write a file. Prevention would need a named tool and a `Bash` deny rule, which is the wider reading, pending the assistant.
- **The guard for a missing script was tested through `cmd.exe`.** The shell Claude Code actually uses is unknown. The `python -c` launcher with nested quotes ran without a hook error in the live session, with the script present.
- Also observed: a run can read the control (the contract, the hook and its own trace; writes to them are denied); the context limit of 30 and the limit of three denials or checks are author hypotheses; the field name of the `Skill` tool input that the hook assumes (`skill`) was not exercised.

## Second-session review

A second session of the same model family ran the skill bundled with Claude Code (the bundled `verify`, not the Module 1 skill) on the diff of this branch. It drove the hook through its JSON interface in a scratch copy, without a live session, and it found the `..` escape from the roots. It is **not** an independent review: it is the same model family, it was started by the author, and it did not use the hook in a live session. While checking its report, the author's session found a second gap of the same kind (a recursive `Grep`). Both were fixed after red tests.

## The one change to a Module 1 file

`skills/verify/SKILL.md` is the only Module 1 file changed. The author approved the diff before it was applied. It makes the log read whole-file, returns the report in the final message with a `Context read` block, and defines a data line.

```diff
--- a/skills/verify/SKILL.md
+++ b/skills/verify/SKILL.md
@@ -19,5 +19,5 @@
 - The Route, Act and Context evidence blocks of this run.
 - Each source a pointer cites, opened again at that file and field to confirm what it says.
-- `traces/transition-log.md`, for recorded attempts and the current state.
+- `traces/transition-log.md`, read in full (not a range), for recorded attempts and the current state.
 
 ## Prohibited context
@@ -35,5 +35,5 @@
 5. Apply the explicit rules below.
 6. Apply the "If the evidence is missing" column of the transition. ...
-7. Append the Verify report to `traces/worked-case.md`, under "Stage evidence".
+7. Return the Verify report in the final message, starting with a `Context read` block. Do not write files during a run. A human appends the report to `traces/worked-case.md`.
 
 ### Explicit rule for T9 (IN_ANALYSIS to RESOLVED)
@@ -46,5 +46,7 @@
 ## Evidence produced
-Verify report: transition checked; table of requirements (requirement, status, pointer, note); state check; blocking flags; verdict PASS or FAIL; for FAIL, the refused transition and what is missing.
+Verify report: `Context read` block (files read; the number of data lines in `traces/transition-log.md`, written as `traces/transition-log.md (N data lines)`); transition checked; table of requirements (requirement, status, pointer, note); state check; blocking flags; verdict PASS or FAIL; for FAIL, the refused transition and what is missing.
+
+A data line is every non-blank line after the table header (the header row and its separator row) of `traces/transition-log.md`. Blank lines are not counted.
 
 ## Proposed transition
```

The other eight skills still say "Append ... to `traces/worked-case.md`". They are out of scope here.

## Next steps

1. Runs A, B and C from `docs/module-2-run-prompts.md` (with the "Fallback (weak trigger)" section if the plugin cannot be loaded), recorded in `traces/module-2-after-trace.md`.
2. The full mutation table against the final hook, if the hook changes again after the table in this PR.
3. The track assistant's answers on the scope (one extension, or a set with two safe tools) and on whether three hook events count as one interception point.
4. The "a author" typo in Module 1 files, to be fixed on the Module 1 branch.

## Who did what

Thomaz decided and reviewed every step. The work was AI-assisted (Claude Code) under his direction: the hook, the self-test, the mutation driver and the documents were written by the assistant, and Thomaz approved each step before the next one. It was solo, so no cross-review by another participant took place, which is a limitation.
