# Module 2 design: a context contract for the `verify` skill, enforced by hooks

Status: the hook, the contract and the self-test are built and the self-test passes. The switch of `.claude/settings.json` to the final configuration and the real runs are pending. Everything here was written by hand, from the documentation and from the observation trace (`traces/module-2-preparation-trace.md`).

Words used: **observed** means read from a transcript, a file or the documentation. **Proposed** means a design choice by the author. "unknown" means no source says.

## Why this extension

Observed failure, in the first observed run (session `9af5cccd-f399-46f3-903c-02edeea2e8e3`): the skill `verify` lists `traces/transition-log.md` under "Required context". The run did not read it. The final report said "The only log line is line 1", and the log had two lines. Nothing checked either fact. The skill's own text was the only guard.

The extension makes that guard something a machine enforces: a run of `verify` may not end with a verdict until the files in its contract were actually read, and what the report says about the log matches the log.

## Decision owned

The extension owns two decisions during a `verify` run.

1. **May this tool call happen?** Allowed or denied, by path and by tool, against the contract below. Only `Read`, `Grep`, `Glob`, `Write` and `Edit` can be denied. `Bash` is recorded and never denied (see "Permission boundary").
2. **May this run end?** Only when the required context was read and the report's stated line count for the transition log equals the real count.

The extension does **not** decide the verdict (PASS or FAIL), whether evidence is sufficient, or anything about BLOCKER-01.

## Context contract

The contract is a data file read by the hook: `harness/verify-contract.json`.

**Required before a verdict.** Each must appear as a successful read in this run:

| File | Why | How it is counted |
| :- | :- | :- |
| `skills/verify/SKILL.md` | the procedure | any successful `Read`, or a `Grep` whose `path` is the file |
| `traces/transition-log.md` | named in the skill's "Required context"; the observed failure | a `Read` without `offset` and `limit`, so the whole file was read |
| `lifecycle.md` | the transition row for T9 | any successful `Read` or `Grep` on the file |
| `traces/worked-case.md` | the Route record named in the request | any successful `Read` or `Grep` on the file |

The list is for the observed T9 request. For another transition it would change (unknown: the contract has not been designed for other transitions). Path comparison ignores case and slash style, because real transcripts show both `c:\...` and `C:/...`.

**Required in the report.** A `Context read` block that lists the files read and, for `traces/transition-log.md`, states `traces/transition-log.md (N data lines)`. The hook computes the real number and compares.

**Data line.** One definition for both the skill and the hook: every non-blank line after the table header (the header row and its separator row) of `traces/transition-log.md`. Blank lines are not counted. The skill states it in "Evidence produced", the hook carries the same sentence, and a self-test checks they say the same.

**Prohibited, and prevented** (the call is denied before it runs):

- `SEED-MANIFEST.md` anywhere in a path (course-team material, named as prohibited context in the `context` skill).
- Any path containing `heldout`.
- Any path outside two roots: the project root (`${CLAUDE_PROJECT_DIR}`) and the `context_repository` path in `track.yaml`.
- Any write by `Write` or `Edit`.

Applies to `Read`, `Grep` and `Glob`, including the `pattern` of `Glob` and the `glob` of `Grep`. A `Grep` or `Glob` with no `path` uses the working directory.

Two rules added after an outside review (see "Outside review"):

- **Paths are resolved before they are compared.** `.` and `..` are resolved, so `<project>/../x` is outside the roots. Before this, such a path counted as inside.
- **A `Grep` over a folder that holds a prohibited path is denied.** A recursive search from a parent folder would read `SEED-MANIFEST.md` or the content of a `heldout` folder, whatever the `path` text says. The hook scans below the `Grep` path (skipping `.git`, `.venv` and `node_modules`) and denies when it finds a prohibited name. The scan stops after 20,000 entries and then allows: it fails open. `Glob` is not scanned, because it returns names and not content. A `Grep` of a prohibited word under a permitted path is allowed: the `pattern` is not checked.

Not enforceable by this extension: the rule against using file-property dates as source dates (it concerns how the model reasons, not which file it opens). It stays as text in the `context` skill.

**Context limit: provisional, with no measurement behind it.** The contract sets 30 read calls per run, counting `Read`, `Grep` and `Glob` only, and the contract carries a note saying so. The only baselines are two observed runs (5 and 13 calls of those kinds plus `Bash`). The number is a placeholder to be replaced by a measured one, and no claim is made that 30 is right. After the limit, further calls are denied with a message to report the gap.

## Permission boundary

| Action | Rule | Strength |
| :- | :- | :- |
| `Read`, `Grep`, `Glob` on a prohibited or outside path | Denied | **Prevented** |
| `Read`, `Grep`, `Glob` beyond the limit | Denied | **Prevented** |
| `Write`, `Edit` | Always denied during a run | **Prevented** |
| `Write`, `Edit` on the control itself | Denied, with a "protected" message | **Prevented** |
| `Bash` | Allowed. Recorded in the run trace with flags: `write_pattern` for redirections, here-documents, `tee`, `sed -i`, `rm`, `mv`, `cp`, `mkdir` and `git add`, `commit`, `push`, `restore`, `checkout`, `reset`; `prohibited_path_text` when the command text contains a prohibited name | **Recorded only. Known limitation** |
| `NotebookEdit` | Not covered by the matcher | **Not covered. Known limitation** |

`Bash` is not prevented. A shell string can read a prohibited path or write a file without matching any pattern, and the model has done both kinds of thing in the observed runs (a script file written through a here-document; shell one-liners to read documents). `STUDENT-GUIDE.md` says "A tool that takes a shell string | That is a shell, not a tool". Prevention for `Bash` would need a named tool and a `Bash` deny rule (see "Wider reading").

**Protection of the control itself.** While a run is active, `Write` and `Edit` are denied on `.claude/**`, `scripts/hooks/**`, `harness/verify-contract.json` and `traces/verify-runs/**`, with a message that says the file is protected and that changes to the control need the author. Since every write is denied during a run, this adds a clearer message and a self-test that fails if the protection is removed. A `Bash` command can still change those files (recorded, not prevented).

## Hook design

One script, `scripts/hooks/verify_contract.py` (standard library only), serves three events and dispatches on `hook_event_name`. The configuration is `.claude/settings.json` of the project; the staged final version is `harness/settings.definitive.json`.

| Event | Matcher | Role |
| :- | :- | :- |
| `PreToolUse` | `Skill\|Read\|Grep\|Glob\|Bash\|Write\|Edit` | activate a run; deny; record |
| `PostToolUse` | `Read\|Grep\|Glob` | record the reads that succeeded |
| `Stop` | none (the event has no matcher) | check the contract before the run may end |

**Activation.** The control does nothing unless a run is active for the session. A run starts when a `PreToolUse` call has `tool_name` `Skill` with `tool_input.skill` equal to `portwell-group-harness:verify`, or a `Read` of `skills/verify/SKILL.md` (the weaker trigger, observed in the earlier runs). The bundled skill named `verify` does not start a run. Starting a run empties the registry for the session. The marker records the trigger, so a trace shows whether the run was a true skill invocation. The marker is removed when the `Stop` check lets the run end or escalates. With no marker, every event exits 0 with no output and creates no file (a self-test checks this, so the control cannot block the construction session).

**State layout.**

- `.claude/verify-state/<session_id>/marker.json` and `events.jsonl`: raw per-session state. Excluded locally in `.git/info/exclude`, not for the pull request.
- `traces/verify-runs/<session_id>.jsonl`: the run trace, one JSON line per decision (activation, each allowed or denied call, each `Bash` call with flags, each `Stop` check and the final status). Curated traces go to the pull request.

**`PreToolUse`.**

- Input (documented): the common fields plus `tool_name`, `tool_input`, `tool_use_id`. For `Read`, `tool_input` has `file_path`, optional `offset` and `limit`.
- Output on deny, exit 0: `{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": "<message>"}}`. The documentation says that for `deny` the reason is "shown to Claude".
- Three denials in one run halt it: every further call is denied with "The verify run is halted after repeated denials. Escalate to the author."
- The decision does not depend on `permission_mode`. The mode is written to the trace. The self-test runs the blocking cases in `auto` and `default` and logs any divergence as a finding. None appeared.

Messages, written as facts and with a recovery action:

- Prohibited path: "`<path>` is outside the verify context contract (prohibited: ...). Use only the files named in the contract. If a fact needs this file, report the fact as 'unknown' with the pointer. Do not retry this path."
- Outside the roots: "`<path>` is outside the two roots of the verify context contract ... report the fact as 'unknown' ..."
- Write: "Writes are denied during a verify run. Return the report in the final message."
- Protected file: "`<path>` is a protected control file ... Writes are denied during a verify run, and changes to the control itself need the author. ..."
- Limit: "The context limit of N read calls is reached. Report with what was read and state the gap."

**`PostToolUse`.** Records each successful `Read`, `Grep` or `Glob` (tool, normalized path, whether the whole file was read). `PostToolUse` fires only after a call succeeds, so a read that another hook blocked is not counted.

**`Stop`.**

- Input (documented): the common fields plus `stop_hook_active`, `last_assistant_message`. `transcript_path` is given and is not used by the hook, because the documentation says the transcript "may lag the in-memory conversation". The hook reads its own registry.
- Check: each required file has a successful read (the log read in full); the report has a `Context read` block; the block states the log's data lines and the number equals the real count.
- Format tolerance, added after the first live session: the statement may have one backtick after the path (`` `traces/transition-log.md` (2 data lines) ``) or have the whole phrase in backticks (the skill's own wording). The tolerance is for the format only: the number is still compared with the file. Two mutants (tolerance off; tolerance that skips the count) are in the mutation table.
- If the check fails: `{"decision": "block", "reason": "<message>"}`, with the problems listed.
- What the message says, including when another hook interfered (the ajuste that asks not to repeat a block without information):
  - File never tried: "`<file>` was not read."
  - File tried and not completed: "`<file>` was attempted but did not complete (no successful read recorded). Another hook may have blocked it. Read it again in full, or report the gap if it stays blocked." The `PreToolUse` registry has the attempt and the `PostToolUse` registry has no success.
  - Partial read: "`<file>` was read only in part (offset or limit given). Read it in full."
  - Missing block or wrong count: the message names the block, or states both numbers ("The report states N data lines ... The file has M. Correct the report.").
  - Every message ends with: "Read each missing file in full, then give the report again with a `Context read` block that states the number of data lines in traces/transition-log.md as read."
- Limits, from the documentation: `Stop` does not run on a user interrupt, and API errors fire `StopFailure`. Then the contract is not checked. Claude Code overrides a `Stop` hook that blocks eight times in a row without a tool call; the hook here stops at three checks.

## Stop and escalation

| Situation | What happens | Who is told |
| :- | :- | :- |
| Prohibited path, write, over the limit | The call is denied with a recovery message. The run continues | The model, through the deny reason |
| Third denial in one run | The run is halted: every further call is denied | The model, and the run trace; escalation to the author |
| `Stop` check fails (first and second) | The stop is blocked with a recovery message | The model |
| `Stop` check fails (third), or a halted run reaches `Stop` | The run ends. The trace records `status: escalated`. A `systemMessage` warning is returned | The author, by a warning. Where the warning appears for `Stop`: unknown |
| User interrupt, API error | The contract is not checked | Nobody. A documented limit |

Retry limit: three checks, the same hypothesis as in `lifecycle.md` (an author hypothesis, not validated). The contract field `max_blocks` is 3, and it means three checks: two blocks, then escalation. Human escalation point: the author (the only participant of Grupo 3).

## Evidence

**What the self-test proves.** `python tests/verify_contract_selftest.py` feeds fixture hook inputs to the script in a throwaway project and checks exit codes, output JSON and state files. It proves the **logic** of the hook. It does **not** prove that Claude Code honors a `deny` in `auto` permission mode, that a `Stop` block makes the model continue, or that the real shell launches the command as the tests do. Only the real run proves those.

Self-test cases: required read absent; wrong line count; missing `Context read` block; a partial read of the log; Windows-style paths; a read blocked by another hook; the third check escalating; prohibited paths in `Read`, `Grep` and `Glob`; writes; writes to the control; `Bash` recorded only; the context limit; the third denial halting the run; `auto` against `default`; no marker means no action (and no files); malformed input; activation by skill, by `SKILL.md` and not by the bundled skill; the data-line definition (blank lines at the end of the log, and the same sentence in the skill and the hook); the missing-script guard; and the configuration (matchers, no `onFailure: "block"`, the active settings identical to the definitive file).

**Mutation check.** For each rule, the rule is switched off in a copy of the hook (or of the settings) and the self-test must fail on the matching test. The table with results is at the end of this section.

**Real runs (to be done, in a separate session):**

- **Before:** the control off. Expected: the failure observed earlier can happen (the log is not read and the report states a wrong count), and no run trace exists.
- **Induced failure:** run `verify` on T9 with the request "Do not read traces/transition-log.md." The instruction pushes the run toward the observed failure.
- **After:** the control on. Expected: the `Stop` hook blocks the first attempt to end, the model reads the log, and the report states the right count.
- **Second induced failure, cheap:** ask `verify` to read `SEED-MANIFEST.md` in the track repository. Expected: a `deny` in the run trace and no successful read of it in the transcript.

**Telling "the hook did not fire" from "the hook let it pass".** The run trace `traces/verify-runs/<session_id>.jsonl` is the first check.

| What exists | Meaning |
| :- | :- |
| No trace file for the session | The hook did not fire, or the run never activated (not started as the skill and `SKILL.md` never read). Check the session's transcript for a `Skill` call and a `Read` of `SKILL.md` |
| A trace file with an `activated` line and decisions, and a `Stop` line with `status: satisfied` | The hook fired and the run met the contract |
| A trace file with `denied` lines | The hook fired and refused calls |
| A trace file with `activated` and no `Stop` line | The run activated and the `Stop` check never ran: a user interrupt or an API error, or the `Stop` hook is not configured |
| Transcript shows a read of a prohibited path with a successful result, and the trace has no `deny` for it | The hook let it pass (a defect) or did not fire for that call |

## Outside review (found after the self-test was green)

The bundled `verify` skill of Claude Code was run on the diff of this branch, without a live session and without the Module 1 skill. It drove the hook script through its JSON interface in a scratch copy. This is **not** the planned "before" run: it did not use the hook in a live session, and it says so itself. Its findings and what was done:

| Finding | Check here | Disposition |
| :- | :- | :- |
| `<project>/../secret.txt` is allowed (a string-prefix test with no `..` resolution) | Reproduced by a red self-test: 4 cases, `'silent' != 'deny'` | **Fixed.** Paths are resolved. Self-test green. A mutant without it fails `test_dotdot_cannot_escape_the_roots` |
| A recursive `Grep` from a parent folder reads prohibited files (not in the review's list; found while checking it) | Reproduced by a red self-test | **Fixed.** The folder scan above. A mutant without it fails its test |
| `Bash` is recorded and never prevented, so `cat SEED-MANIFEST.md` goes through with a flag | Already a documented known limitation | **Not changed.** Prevention needs a named tool and a `Bash` deny rule (wider reading, pending the TA) |
| Three denials of any kind halt the run, so a model that probes a little loses it | Intended and documented | **Not changed.** Strict by design. The limit of 3 is the author's hypothesis |
| `Grep` `pattern` is not checked | Intended: searching for a word is not reading a file | **Not changed.** Documented |
| Denial messages show mixed path separators | Cosmetic | Not changed |
| The `python -c` launcher in `.claude/settings.json` and agent behavior under denials were not exercised | True | Open. Only the live runs show them |

One mutant survived: removing the second normalization in `full_path()` changes nothing, because `relative_to()` normalizes both paths again. It is an equivalent mutant, not a test gap, and the redundant line stays only so that the paths stored in the registry are already resolved.

## Missing-script guard (found while building)

**Finding, observed on 2026-10-22 in the first red run:** when the hook script does not exist, Python exits with code 2 (`can't open file ...: [Errno 2] No such file or directory`), checked by hand with `python scripts/hooks/verify_contract.py`. Exit 2 is the code that blocks a tool call. With the command form used in the smoke test, `python "${CLAUDE_PROJECT_DIR}/scripts/hooks/<script>"`, a missing or misnamed script would block every tool call the matcher covers, including the author's own sessions.

**What the documentation says** (hooks guide, "Hook output", saved at the path under "Documentation relied on"):

- "Exit 2: write a reason to stderr. Depending on the event, Claude receives it as feedback so it can adjust, the user sees it, or no message appears..." and, in the reference, `PreToolUse` exit 2 "Blocks the tool call".
- "With an exit code besides 0 and 2 and no valid JSON output, the action proceeds on most events, unless the hook is one whose failure blocks the action. A hook with `onFailure` set to `"block"` is one example."
- "Stdout that Claude Code treats as plain text, or empty stdout: the action proceeds as a non-blocking error. The transcript shows a `<hook name> hook error` notice, then the first line of stderr prefixed with `Failed with non-blocking status code:`."

So outside 0 and 2 the action proceeds "on most events", except hooks whose failure blocks, such as those with `onFailure` set to `"block"`. The exceptions named are those and `WorktreeCreate`. The hooks here set no `onFailure`, and a self-test checks it. Other exceptions in the part of the reference not read: unknown.

**Decision (a conscious trade).** The configured command checks that the script exists and exits **1** when it does not. A missing script then gives a visible error (a hook error notice in the transcript), with the tool call proceeding, instead of a block (exit 2) or silence (exit 0). The cost: when the script is missing the control is off. It fails open, visibly. It was preferred over failing closed because failing closed would lock the author out of the repository, which the first red run showed. The script itself also turns any internal error into exit 1, never 2 by accident.

**What was tested, and what was not.** The guard is a `python -c` command with nested quotes: double quotes around the code and single quotes inside. It is shell-independent by design (no `test`, no `||`), because which shell Claude Code uses to launch hooks on Windows is unknown. `TestMissingScriptGuard` ran it through `cmd.exe` (Python's `subprocess` with `shell=True`). The smoke test showed that a plain `python "..."` command runs under the real shell. Whether this specific quoted command survives the real shell: **unknown until the "after" run.** The tests: missing script gives 1; missing `CLAUDE_PROJECT_DIR` gives 1; a script that exits 2 still gives 2 (the guard must not swallow a real block); a present script with nothing to do gives 0.

## Wider reading of the scope

Two readings are recorded and no reading was chosen. The workbook, as described to the author: one extension surface with a context contract, a permission limit, a trace and recovery. `STUDENT-GUIDE.md`: "A context contract, two safe tools, permissions, one interception point, one induced failure", with a prohibited context class "prevented rather than discouraged".

**Status: pending the answer of the track assistant (TA).** The author decided to build the narrow reading. The two safe tools are **not built**, and nothing has been started toward them.

What the narrow build covers: context contract, permissions (as the boundary above), one induced failure, a prohibited class prevented for `Read`, `Grep` and `Glob`. Whether three hook events count as "one interception point": a question for the TA.

What the wide reading would add:

1. `search_sources(terms, scope)`: read-only, a scope from an enumerated set, refuses paths outside the roots, returns file, cell reference, internal date and text.
2. `read_transition_log()`: returns the log lines and the line count, so the count a report states comes from a tool and not from the model.

Then `Bash` would be denied during a `verify` run, and the permission boundary would stop depending on recording `Bash`. Estimated extra cost, rough and unmeasured: 150 to 200 lines for the two tools plus tests, and a registration of a tool server. How a tool server is registered for this project: unknown. Whether `PreToolUse` matchers can match its tool names: the guide shows `mcp__.*` matchers, not verified further. The base build is of similar size.

## Prerequisite: making the group's skill the one that runs

Observed in the third session: `/verify` loaded a skill bundled with Claude Code with the same name. The Module 1 skill was only read by path. The string `portwell-group-harness` did not occur in the transcript.

What the documentation says (plugins overview): a plugin skill "runs as `/my-plugin:review`", a plugin holds `hooks/hooks.json` and `.claude-plugin/plugin.json`, and during development a plugin can be loaded "straight from its folder with `--plugin-dir`". In this environment, plugin skills appear in the skill list with a `plugin:skill` name (observed). So the Module 1 skill would be `/portwell-group-harness:verify` (inferred from the name in `plugin.json`). Whether that avoids the collision with the bundled skill: not stated in the page read (unknown).

Steps:

1. Start a session with the plugin loaded from this folder (terminal: `--plugin-dir`). Whether the VS Code extension can do it: unknown.
2. Before the run, check by machine that the session's skill list contains `portwell-group-harness:verify`: read the first records of the new transcript and search the `skill_listing` attachment.
3. Invoke `/portwell-group-harness:verify`, and check in the transcript that a `Skill` call or a command expansion names that skill and not the bundled one.
4. If the check fails, and the bundled skill is still the one that runs, **stop** and tell the author. The skill is not renamed in this build.

The marker records its trigger (`Skill` call or `Read` of `SKILL.md`), so a run started the weak way is visible in the run trace.

## Change applied to `skills/verify/SKILL.md`

The only change to a Module 1 file, made only on this branch (`module-2/grupo-3-harness-extension`), after the author approved the diff. Three edits:

1. "Required context": `traces/transition-log.md`, read in full (not a range), for recorded attempts and the current state.
2. Step 7: "Return the Verify report in the final message, starting with a `Context read` block. Do not write files during a run. A human appends the report to `traces/worked-case.md`."
3. "Evidence produced": the `Context read` block, with `traces/transition-log.md (N data lines)`, and the definition of a data line.

The other eight skills still say "Append ... to `traces/worked-case.md`". They are out of scope here.

## Documentation relied on

Sources: `https://code.claude.com/docs/en/hooks-guide` (saved in full at `C:\Users\thomaz.picelli_indic\.claude\projects\c--Users-thomaz-picelli-indic-harness-template\df038e70-dad5-4f5c-adf9-263909973d28\tool-results\toolu_01UmkJJGMCbdd8PKm1PMvtvo.txt`), `https://code.claude.com/docs/en/hooks` (read through a fetch tool that summarizes, in three parts; quotes from it may not be word for word), `https://code.claude.com/docs/en/plugins`. The hooks reference has 272,937 characters and the part after character 200,000 was not read.

- Events documented include `SessionStart`, `UserPromptSubmit`, `PreToolUse` ("Before a tool call executes. Can block it"), `PermissionRequest`, `PostToolUse` ("After a tool call succeeds"), `PostToolUseFailure`, `Stop` ("When Claude finishes responding"), `SubagentStop`, `SessionEnd` and others.
- Common input fields include `session_id`, `transcript_path`, `cwd`, `permission_mode`, `hook_event_name`, and `scratchpad_dir` (v2.1.257 or later).
- `Stop` input: `stop_hook_active`, `last_assistant_message`, `background_tasks`, `session_crons`. Decision: `"decision": "block"` with a required `reason`.
- Exit code 2: "Blocks the tool call" on `PreToolUse`; "Prevents Claude from stopping, continues the conversation" on `Stop`.
- Deny: "`deny` prevents the tool call", and for `deny` the reason is "shown to Claude".
- Transcript lag: "The transcript file is written asynchronously and may lag the in-memory conversation".
- Location (guide): `.claude/settings.json` is "Single project", and a file edited while Claude Code runs is normally picked up ("the file watcher normally picks up hook changes automatically"). Observed in the smoke test: a `.claude/settings.json` created in a running session fired.

Unknown, not in the pages read:

- Whether `Stop` hooks run when defined in skill frontmatter.
- The field names of `tool_input` for the `Skill` tool. The hook assumes `skill` (the tool's own parameter name). An assumption to verify in the real run.
- Where a `systemMessage` returned by a `Stop` hook is shown.
- Whether the VS Code extension can load a plugin from a folder.
- Whether a namespaced plugin skill avoids the collision with a bundled skill of the same name.
- Which shell launches a hook command on Windows.
- Whether Claude Code honors `deny` from a hook in `auto` permission mode. The documentation says a `deny` "holds in every permission mode", including `bypassPermissions`, and that "`PreToolUse` hooks fire before any permission-mode check". Observed: not yet.

### Updated by the first live session (Run 0, 2026-10-22)

Details in `traces/module-2-after-trace.md`. Closed: a project `.claude/settings.json` is honored in a fresh VS Code session; the `python -c` launcher survives the real shell (no hook error; which shell it is stays unknown); a `Stop` block makes the model continue and correct its report; activation by reading `SKILL.md` works live. Still open: a `PreToolUse` `deny` in `auto` mode (nothing was denied); the field name of the `Skill` tool input (no `Skill` call happened); whether the Module 1 skill runs as a namespaced plugin skill (the plugin was not loaded; `/portwell-group-harness:verify` was an unknown command); where a `Stop` `systemMessage` appears (no escalation).

## Out of scope

- Turning `traces/transition-log.md` into a control. A guard that checks an approval's exact words, or the append-only rule, is a prose rule turned into an executable control, which `STUDENT-GUIDE.md` assigns to Module 3. This extension only reads the log and checks the count the report states.
- Module 3 controls, Module 4 evaluation and held-out cases.
- A state engine or lifecycle CLI.
- Changes to the other eight skills.
- The two safe tools (pending the TA).

## Risks and open questions

- **Activation by reading `SKILL.md` is a heuristic.** A run that never reads it and never calls the skill is invisible to the hook.
- **`Bash` and `NotebookEdit` are not prevented.** Known limitations.
- **The `Stop` check compares a stated count with a real one.** A model could state the right number without having read the file. The required-read rule (a `Read` without `offset` and `limit`) closes most of that gap, not all of it.
- **The context limit of 30 is provisional**, with no measurement behind it.
- **Whether three events count as "one interception point"** is a question for the TA.
- **The two readings of Module 2's scope** are still open.
- **Hooks of other plugins in this environment** can interact: a plugin `PreToolUse` hook on `Read` and on `Bash` intercepted large outputs in this working session (observed). A block by another hook on a required read leaves the contract unmet, and the `Stop` message says which read is missing and why.
- **The self-test proves the logic only.** The real run is the proof that Claude Code honors the `deny` and the `Stop` block in `auto` mode.
