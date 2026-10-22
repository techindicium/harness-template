"""Model-free self-test for the verify context contract hooks.

Run:  python tests/verify_contract_selftest.py

Each case feeds a fixture hook input (JSON on stdin) to scripts/hooks/verify_contract.py, in a
throwaway project directory, and checks the exit code, the JSON on stdout and the state files.
No model and no Claude Code session are involved. Standard library only.

The test also fixes three things the hook must follow:
- the contract file layout (harness/verify-contract.json, built here as a fixture);
- the state layout (.claude/verify-state/<session_id>/ for the marker and the read registry,
  traces/verify-runs/<session_id>.jsonl for the run trace);
- the wording tags in block messages that tell the model what to do next.
"""
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
HOOK = Path(os.environ.get("VERIFY_HOOK_PATH") or (REPO / "scripts" / "hooks" / "verify_contract.py"))
SKILL_MD = REPO / "skills" / "verify" / "SKILL.md"
DATA_LINE_DEFINITION = "every non-blank line after the table header"
SESSION = "sess-1"
SKILL_NAME = "portwell-group-harness:verify"
FINDINGS = []  # observations that are not failures


class Result:
    def __init__(self, rc, out, err):
        self.rc = rc
        self.out = out
        self.err = err
        try:
            self.json = json.loads(out) if out.strip() else None
        except ValueError:
            self.json = None

    def decision(self):
        """'deny' / 'block' / 'allow-silent' / 'other' from the hook output."""
        if self.rc == 2:
            return "exit2"
        j = self.json or {}
        hso = j.get("hookSpecificOutput", {})
        if hso.get("permissionDecision") == "deny":
            return "deny"
        if j.get("decision") == "block":
            return "block"
        if not self.out.strip() and self.rc == 0:
            return "silent"
        return "other"

    def reason(self):
        j = self.json or {}
        return (j.get("hookSpecificOutput", {}).get("permissionDecisionReason")
                or j.get("reason") or self.err or "")

    def __repr__(self):
        return f"rc={self.rc} out={self.out[:300]!r} err={self.err[:300]!r}"


def make_contract(limit=30, max_blocks=3, max_denials=3):
    return {
        "skill": SKILL_NAME,
        "activation": {"skill_names": [SKILL_NAME], "read_paths": ["skills/verify/SKILL.md"]},
        "required_reads": [
            {"path": "skills/verify/SKILL.md"},
            {"path": "traces/transition-log.md", "whole_file": True},
            {"path": "lifecycle.md"},
            {"path": "traces/worked-case.md"},
        ],
        "prohibited_path_names": ["SEED-MANIFEST.md"],
        "prohibited_substrings": ["heldout"],
        "roots": ["${project}", "${context_repository}"],
        "read_tools": ["Read", "Grep", "Glob"],
        "write_tools": ["Write", "Edit"],
        "protected": [".claude/**", "scripts/hooks/**", "harness/verify-contract.json", "traces/verify-runs/**"],
        "context_limit": limit,
        "context_limit_note": "provisional, no measurement behind it",
        "max_blocks": max_blocks,
        "max_denials": max_denials,
        "log_check": {"path": "traces/transition-log.md", "report_block_heading": "Context read"},
    }


class Fixture:
    """A throwaway project plus a throwaway context repository."""

    def __init__(self, log_rows=2, limit=30):
        self._tmp = tempfile.TemporaryDirectory()
        base = Path(self._tmp.name)
        self.project = base / "project"
        self.context_repo = base / "context_repo"
        for rel, text in {
            "skills/verify/SKILL.md": "---\nname: verify\n---\n# Verify\n",
            "lifecycle.md": "# Lifecycle\n| T9 | row |\n",
            "traces/worked-case.md": "# Worked case\n### B1\n",
            "traces/transition-log.md": self._log(log_rows),
            "track.yaml": f"group: Grupo 3\ncontext_repository: '{self.context_repo}'\n",
            "harness/verify-contract.json": json.dumps(make_contract(limit=limit), indent=2),
        }.items():
            p = self.project / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(text, encoding="utf-8")
        for rel in ("SEED-MANIFEST.md", "data/notes.txt", "heldout/case.txt"):
            p = self.context_repo / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text("x\n", encoding="utf-8")
        self.snapshot_before = self.tree()

    @staticmethod
    def _log(rows):
        head = ("# Transition log\n\n| item | from | to |\n| :- | :- | :- |\n")
        return head + "".join(f"| BLOCKER-01 | (start) | OPEN_UNOWNED | row {i} |\n" for i in range(rows))

    def tree(self):
        return sorted(str(p.relative_to(self.project)) for p in self.project.rglob("*") if p.is_file())

    def new_files(self):
        return [f for f in self.tree() if f not in self.snapshot_before]

    # paths, in the two styles seen in real transcripts
    def p(self, rel):
        return str(self.project / rel)

    def pwin(self, rel):
        return str(self.project / rel).replace("/", "\\").upper()

    def ctx(self, rel):
        return str(self.context_repo / rel)

    def state_dir(self, session=SESSION):
        return self.project / ".claude" / "verify-state" / session

    def trace_path(self, session=SESSION):
        return self.project / "traces" / "verify-runs" / f"{session}.jsonl"

    def trace(self, session=SESSION):
        p = self.trace_path(session)
        if not p.exists():
            return []
        return [json.loads(line) for line in p.read_text(encoding="utf-8").splitlines() if line.strip()]

    def marker(self, session=SESSION):
        p = self.state_dir(session) / "marker.json"
        return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None

    def cleanup(self):
        self._tmp.cleanup()

    # hook invocation
    def run(self, event, raw=None):
        env = dict(os.environ)
        env["CLAUDE_PROJECT_DIR"] = str(self.project).replace("\\", "/")
        data = raw if raw is not None else json.dumps(event)
        proc = subprocess.run([sys.executable, str(HOOK)], input=data, capture_output=True, text=True,
                              env=env, timeout=30, cwd=str(self.project))
        return Result(proc.returncode, proc.stdout, proc.stderr)

    def base(self, name, mode="auto", session=SESSION):
        return {"session_id": session, "cwd": str(self.project), "hook_event_name": name,
                "permission_mode": mode, "transcript_path": str(self.project / "t.jsonl")}

    def pre(self, tool, tool_input, mode="auto", session=SESSION):
        e = self.base("PreToolUse", mode, session)
        e.update({"tool_name": tool, "tool_input": tool_input, "tool_use_id": "tu-1"})
        return self.run(e)

    def post(self, tool, tool_input, mode="auto", session=SESSION):
        e = self.base("PostToolUse", mode, session)
        e.update({"tool_name": tool, "tool_input": tool_input, "tool_response": {"ok": True}, "tool_use_id": "tu-1"})
        return self.run(e)

    def stop(self, message, active=False, mode="auto", session=SESSION):
        e = self.base("Stop", mode, session)
        e.update({"stop_hook_active": active, "last_assistant_message": message})
        return self.run(e)

    # scenario helpers
    def activate(self, session=SESSION):
        return self.pre("Skill", {"skill": SKILL_NAME}, session=session)

    def read_ok(self, rel, whole=True, style="p", session=SESSION):
        path = self.pwin(rel) if style == "win" else self.p(rel)
        tool_input = {"file_path": path}
        if not whole:
            tool_input.update({"offset": 1, "limit": 5})
        self.pre("Read", tool_input, session=session)
        return self.post("Read", tool_input, session=session)

    def read_all_required(self, session=SESSION):
        for rel in ("skills/verify/SKILL.md", "traces/transition-log.md", "lifecycle.md", "traces/worked-case.md"):
            self.read_ok(rel, session=session)


def report(count, with_block=True):
    block = ("## Context read\n- skills/verify/SKILL.md\n"
             f"- traces/transition-log.md ({count} data lines)\n- lifecycle.md\n- traces/worked-case.md\n\n"
             if with_block else "")
    return block + "## Verify report\n**Verdict: FAIL.** T9 is refused.\n"


class FixtureCase(unittest.TestCase):
    log_rows = 2
    limit = 30

    def setUp(self):
        self.fx = Fixture(log_rows=self.log_rows, limit=self.limit)

    def tearDown(self):
        self.fx.cleanup()

    def assertDecision(self, res, expected, msg=""):
        self.assertEqual(res.decision(), expected, f"{msg} | got {res!r}")


class TestInactiveByDefault(FixtureCase):
    """Without an active session marker the control must do nothing."""

    def test_pre_write_allowed_and_nothing_recorded(self):
        res = self.fx.pre("Write", {"file_path": self.fx.p("notes.md"), "content": "x"})
        self.assertDecision(res, "silent")
        self.assertEqual(self.fx.new_files(), [], "an inactive hook must not create files")

    def test_pre_prohibited_read_allowed_when_inactive(self):
        res = self.fx.pre("Read", {"file_path": self.fx.ctx("SEED-MANIFEST.md")})
        self.assertDecision(res, "silent")
        self.assertEqual(self.fx.new_files(), [])

    def test_post_records_nothing_when_inactive(self):
        res = self.fx.post("Read", {"file_path": self.fx.p("lifecycle.md")})
        self.assertDecision(res, "silent")
        self.assertEqual(self.fx.new_files(), [])

    def test_stop_allowed_when_inactive(self):
        res = self.fx.stop(report(1))
        self.assertDecision(res, "silent")
        self.assertEqual(self.fx.new_files(), [])

    def test_malformed_input_does_not_crash(self):
        res = self.fx.run(None, raw="this is not json")
        self.assertEqual(res.rc, 0, repr(res))
        self.assertEqual(self.fx.new_files(), [])


class TestActivation(FixtureCase):
    def test_namespaced_skill_call_activates(self):
        res = self.fx.activate()
        self.assertDecision(res, "silent")
        marker = self.fx.marker()
        self.assertIsNotNone(marker, "no marker after the skill call")
        self.assertEqual(marker.get("trigger"), "skill")

    def test_bundled_verify_does_not_activate(self):
        res = self.fx.pre("Skill", {"skill": "verify"})
        self.assertDecision(res, "silent")
        self.assertIsNone(self.fx.marker(), "the bundled skill is not ours")
        self.fx.activate()  # liveness: a do-nothing hook must not pass this test
        self.assertIsNotNone(self.fx.marker(), "control is not alive: our namespaced skill must activate it")

    def test_reading_skill_md_activates_with_weaker_trigger(self):
        self.fx.pre("Read", {"file_path": self.fx.p("skills/verify/SKILL.md")})
        marker = self.fx.marker()
        self.assertIsNotNone(marker)
        self.assertEqual(marker.get("trigger"), "read_skill_md")


class TestStopCheck(FixtureCase):
    def test_missing_required_read_blocks_and_names_the_file(self):
        self.fx.activate()
        for rel in ("skills/verify/SKILL.md", "lifecycle.md", "traces/worked-case.md"):
            self.fx.read_ok(rel)
        res = self.fx.stop(report(2))
        self.assertDecision(res, "block")
        self.assertIn("traces/transition-log.md", res.reason())
        self.assertRegex(res.reason().lower(), r"read .*in full|read each missing file")

    def test_wrong_line_count_blocks_with_both_numbers(self):
        self.fx.activate()
        self.fx.read_all_required()
        res = self.fx.stop(report(1))  # the file has 2 data lines
        self.assertDecision(res, "block")
        reason = res.reason()
        self.assertIn("1", reason)
        self.assertIn("2", reason)
        self.assertIn("traces/transition-log.md", reason)

    def test_missing_context_read_block_blocks(self):
        self.fx.activate()
        self.fx.read_all_required()
        res = self.fx.stop(report(2, with_block=False))
        self.assertDecision(res, "block")
        self.assertIn("Context read", res.reason())

    def test_correct_run_is_allowed_and_clears_marker(self):
        self.fx.activate()
        self.fx.read_all_required()
        res = self.fx.stop(report(2))
        self.assertDecision(res, "silent")
        self.assertIsNone(self.fx.marker(), "marker must be removed when the run may end")
        trace = self.fx.trace()
        self.assertTrue(trace, "no run trace written: the hook did not check anything")
        self.assertEqual(trace[-1].get("status"), "satisfied")
        write = self.fx.pre("Write", {"file_path": self.fx.p("notes.md"), "content": "x"})
        self.assertDecision(write, "silent", "after the run ended, writes are no longer denied")

    def test_backticks_around_the_path_are_accepted(self):
        """Seen in the first live run: the model wrote `path` (N data lines) and was blocked for the format."""
        variants = [
            "- `traces/transition-log.md` (2 data lines)",    # backticks around the path only
            "- `traces/transition-log.md (2 data lines)`",    # the skill's own wording, all in backticks
        ]
        for n, line in enumerate(variants):
            with self.subTest(variant=line):
                session = f"ticks-ok-{n}"
                self.fx.activate(session=session)
                self.fx.read_all_required(session=session)
                message = ("## Context read\n- skills/verify/SKILL.md\n" + line +
                           "\n- lifecycle.md\n- traces/worked-case.md\n\n## Verify report\n**Verdict: FAIL.**\n")
                self.assertDecision(self.fx.stop(message, session=session), "silent")
                trace = self.fx.trace(session)
                self.assertTrue(trace, "no run trace written")
                self.assertEqual(trace[-1].get("status"), "satisfied")

    def test_backticks_do_not_hide_a_wrong_count(self):
        """The tolerance is for the format only. The number is still compared with the file."""
        for n, line in enumerate(["- `traces/transition-log.md` (5 data lines)",
                                  "- `traces/transition-log.md (5 data lines)`"]):
            with self.subTest(variant=line):
                session = f"ticks-bad-{n}"
                self.fx.activate(session=session)
                self.fx.read_all_required(session=session)
                message = ("## Context read\n" + line + "\n\n## Verify report\n**Verdict: FAIL.**\n")
                res = self.fx.stop(message, session=session)
                self.assertDecision(res, "block")
                self.assertIn("states 5 data lines", res.reason())
                self.assertIn("has 2", res.reason())

    def test_partial_read_of_the_log_does_not_count(self):
        self.fx.activate()
        for rel in ("skills/verify/SKILL.md", "lifecycle.md", "traces/worked-case.md"):
            self.fx.read_ok(rel)
        self.fx.read_ok("traces/transition-log.md", whole=False)  # offset and limit given
        res = self.fx.stop(report(2))
        self.assertDecision(res, "block")
        self.assertIn("traces/transition-log.md", res.reason())

    def test_windows_style_paths_count_as_reads(self):
        self.fx.activate()
        for rel in ("skills/verify/SKILL.md", "traces/transition-log.md", "lifecycle.md", "traces/worked-case.md"):
            self.fx.read_ok(rel, style="win")
        res = self.fx.stop(report(2))
        self.assertDecision(res, "silent", "backslashes and upper case must not hide a real read")
        trace = self.fx.trace()
        self.assertTrue(trace, "no run trace written: the hook did not check anything")
        self.assertEqual(trace[-1].get("status"), "satisfied")

    def test_read_blocked_by_another_hook_is_reported_as_such(self):
        """The log read was attempted (PreToolUse seen) but never completed (no PostToolUse)."""
        self.fx.activate()
        for rel in ("skills/verify/SKILL.md", "lifecycle.md", "traces/worked-case.md"):
            self.fx.read_ok(rel)
        self.fx.pre("Read", {"file_path": self.fx.p("traces/transition-log.md")})  # no post
        res = self.fx.stop(report(2))
        self.assertDecision(res, "block")
        reason = res.reason().lower()
        self.assertIn("traces/transition-log.md", reason)
        self.assertIn("attempted", reason)
        self.assertIn("did not complete", reason)
        self.assertIn("another hook", reason)

    def test_third_block_escalates_and_ends_the_run(self):
        self.fx.activate()
        first = self.fx.stop(report(2, with_block=False))
        second = self.fx.stop(report(2, with_block=False), active=True)
        third = self.fx.stop(report(2, with_block=False), active=True)
        self.assertDecision(first, "block")
        self.assertDecision(second, "block")
        self.assertEqual(third.rc, 0, repr(third))
        self.assertNotEqual(third.decision(), "block", "the third check must let the run end")
        self.assertIn("systemMessage", third.json or {}, "the author must be warned")
        self.assertIsNone(self.fx.marker())
        trace = self.fx.trace()
        self.assertTrue(trace, "no run trace written: the hook did not record the escalation")
        self.assertEqual(trace[-1].get("status"), "escalated")


class TestPreToolUse(FixtureCase):
    def setUp(self):
        super().setUp()
        self.fx.activate()

    def test_prohibited_paths_are_denied_for_read_grep_glob(self):
        cases = [
            ("Read", {"file_path": self.fx.ctx("SEED-MANIFEST.md")}, "SEED-MANIFEST.md"),
            ("Read", {"file_path": self.fx.ctx("heldout/case.txt")}, "heldout"),
            ("Grep", {"pattern": "x", "path": self.fx.ctx("heldout")}, "heldout"),
            ("Glob", {"pattern": "*", "path": str(self.fx.context_repo / "heldout")}, "heldout"),
            ("Read", {"file_path": "C:\\Windows\\win.ini"}, "outside"),
        ]
        for n, (tool, tool_input, tag) in enumerate(cases):
            with self.subTest(tool=tool, tag=tag):
                session = f"prohibited-{n}"  # a fresh run per case: three denials would halt a run
                self.fx.activate(session=session)
                res = self.fx.pre(tool, tool_input, session=session)
                self.assertDecision(res, "deny")
                self.assertIn(tag.lower(), res.reason().lower())
                self.assertIn("unknown", res.reason().lower(), "the message must say what to do instead")

    def test_allowed_reads_pass(self):
        for tool, tool_input in [("Read", {"file_path": self.fx.p("lifecycle.md")}),
                                 ("Read", {"file_path": self.fx.ctx("data/notes.txt")}),
                                 ("Grep", {"pattern": "T9", "path": str(self.fx.project)})]:
            with self.subTest(tool=tool):
                self.assertDecision(self.fx.pre(tool, tool_input), "silent")
        # liveness: a do-nothing hook must not pass this test
        self.assertDecision(self.fx.pre("Read", {"file_path": self.fx.ctx("SEED-MANIFEST.md")}), "deny",
                            "control is not alive: a prohibited read must still be denied")

    def test_dotdot_cannot_escape_the_roots(self):
        """Found by an outside review: <project>/../x was counted as inside the project."""
        cases = [
            ("project parent", str(self.fx.project) + "/../secret.txt"),
            ("project parent, backslashes", str(self.fx.project).replace("/", "\\") + "\\..\\secret.txt"),
            ("context repo parent", self.fx.ctx("data") + "/../../elsewhere.txt"),
            ("relative path that climbs out", "../secret.txt"),
        ]
        for n, (name, path) in enumerate(cases):
            with self.subTest(case=name):
                session = f"dotdot-{n}"
                self.fx.activate(session=session)
                res = self.fx.pre("Read", {"file_path": path}, session=session)
                self.assertDecision(res, "deny", name)
                self.assertIn("outside", res.reason().lower())
        # a path that goes up and comes back inside is still inside, and counts as that file
        self.fx.activate(session="dotdot-inside")
        inside = str(self.fx.project) + "/traces/../lifecycle.md"
        self.assertDecision(self.fx.pre("Read", {"file_path": inside}, session="dotdot-inside"), "silent")

    def test_grep_over_a_folder_that_contains_a_prohibited_file_is_denied(self):
        """A recursive search from a parent folder would read SEED-MANIFEST.md and heldout/ content."""
        self.fx.activate(session="grep-root")
        res = self.fx.pre("Grep", {"pattern": "x", "path": str(self.fx.context_repo)}, session="grep-root")
        self.assertDecision(res, "deny", "the context repository root holds SEED-MANIFEST.md and heldout/")
        self.assertIn("contains a prohibited path", res.reason().lower())
        self.assertIn("unknown", res.reason().lower())
        # folders without prohibited content stay searchable
        self.fx.activate(session="grep-ok")
        for path in (self.fx.ctx("data"), str(self.fx.project)):
            self.assertDecision(self.fx.pre("Grep", {"pattern": "x", "path": path}, session="grep-ok"), "silent", path)

    def test_writes_are_denied(self):
        for tool in ("Write", "Edit"):
            with self.subTest(tool=tool):
                res = self.fx.pre(tool, {"file_path": self.fx.p("traces/worked-case.md"), "content": "x"})
                self.assertDecision(res, "deny")
                self.assertIn("writes are denied", res.reason().lower())
                self.assertIn("final message", res.reason().lower())

    def test_writes_to_the_control_itself_are_denied_as_protected(self):
        targets = [".claude/settings.json", ".claude/verify-state/sess-1/marker.json",
                   "scripts/hooks/verify_contract.py", "harness/verify-contract.json",
                   "traces/verify-runs/sess-1.jsonl"]
        for tool in ("Write", "Edit"):
            for rel in targets:
                with self.subTest(tool=tool, target=rel):
                    session = f"protected-{tool}-{rel}"  # a fresh run per case: three denials would halt a run
                    self.fx.activate(session=re.sub(r"[^A-Za-z0-9_.-]", "_", session))
                    res = self.fx.pre(tool, {"file_path": self.fx.p(rel), "content": "x"},
                                      session=re.sub(r"[^A-Za-z0-9_.-]", "_", session))
                    self.assertDecision(res, "deny")
                    self.assertIn("protected", res.reason().lower())

    def test_bash_is_recorded_not_prevented(self):
        for command in ("cat > out.txt <<EOF\nx\nEOF", "rm notes.md", "cat " + self.fx.ctx("SEED-MANIFEST.md")):
            with self.subTest(command=command[:20]):
                res = self.fx.pre("Bash", {"command": command})
                self.assertDecision(res, "silent", "Bash is a known limitation: recorded only")
        bash_lines = [t for t in self.fx.trace() if t.get("tool") == "Bash"]
        self.assertEqual(len(bash_lines), 3, f"each Bash call must be recorded: {bash_lines}")
        self.assertTrue(all(t.get("decision") == "recorded" for t in bash_lines))
        flagged = [t for t in bash_lines if t.get("flags")]
        self.assertGreaterEqual(len(flagged), 2, "write-looking and prohibited-path commands must be flagged")

    def test_third_denial_halts_the_run(self):
        for i in range(3):
            res = self.fx.pre("Write", {"file_path": self.fx.p(f"n{i}.md"), "content": "x"})
            self.assertDecision(res, "deny", f"denial {i + 1}")
        res = self.fx.pre("Read", {"file_path": self.fx.p("lifecycle.md")})  # an allowed read
        self.assertDecision(res, "deny")
        self.assertIn("halted", res.reason().lower())
        self.assertIn("author", res.reason().lower())
        self.assertEqual((self.fx.marker() or {}).get("status"), "halted")

    def test_permission_mode_does_not_change_the_decision(self):
        """auto versus default. A divergence is a finding, not a failure."""
        scenarios = [
            ("prohibited read", "Read", {"file_path": self.fx.ctx("SEED-MANIFEST.md")}),
            ("write", "Write", {"file_path": self.fx.p("x.md"), "content": "x"}),
            ("write to control", "Edit", {"file_path": self.fx.p(".claude/settings.json")}),
        ]
        for name, tool, tool_input in scenarios:
            with self.subTest(case=name):
                sa, sd = f"mode-auto-{name}".replace(" ", "_"), f"mode-default-{name}".replace(" ", "_")
                self.fx.activate(session=sa)
                self.fx.activate(session=sd)
                auto = self.fx.pre(tool, tool_input, mode="auto", session=sa)
                default = self.fx.pre(tool, tool_input, mode="default", session=sd)
                self.assertDecision(auto, "deny", f"{name} in auto mode")
                if auto.decision() != default.decision() or auto.reason() != default.reason():
                    FINDINGS.append(f"{name}: auto={auto.decision()} default={default.decision()}")


def load_hook_module():
    import importlib.util
    spec = importlib.util.spec_from_file_location("verify_contract_under_test", HOOK)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestDataLineDefinition(FixtureCase):
    """The skill and the hook must count the lines of the transition log the same way."""

    def test_skill_and_hook_state_the_same_definition(self):
        skill = SKILL_MD.read_text(encoding="utf-8")
        hook = HOOK.read_text(encoding="utf-8")
        self.assertIn(DATA_LINE_DEFINITION, skill, "skills/verify/SKILL.md does not define a data line as expected")
        self.assertIn(DATA_LINE_DEFINITION, hook, "the hook does not carry the same definition")

    def test_counting_function_follows_the_definition(self):
        count = load_hook_module().count_data_rows
        header = "# T\n\n| a | b |\n| :- | :- |\n"
        self.assertEqual(count(header), 0)
        self.assertEqual(count(header + "| 1 | x |\n| 2 | y |\n"), 2)
        self.assertEqual(count(header + "| 1 | x |\n| 2 | y |\n\n\n"), 2, "blank lines at the end are not data lines")
        self.assertEqual(count(header + "| 1 | x |\n\n| 2 | y |\n"), 2, "a blank line in the middle is not a data line")
        self.assertEqual(count(header + "| 1 | x |\nnote after the table\n"), 2, "every non-blank line counts")

    def test_stop_accepts_the_right_count_when_the_log_ends_with_blank_lines(self):
        log = self.fx.project / "traces" / "transition-log.md"
        log.write_text(log.read_text(encoding="utf-8") + "\n\n", encoding="utf-8")
        self.fx.activate()
        self.fx.read_all_required()
        self.assertDecision(self.fx.stop(report(2)), "silent", "2 data lines plus blank lines at the end")
        self.fx.activate(session="s2")
        self.fx.read_all_required(session="s2")
        res = self.fx.stop(report(3), session="s2")
        self.assertDecision(res, "block", "blank lines must not be counted as a third data line")
        self.assertIn("2", res.reason())


class TestContextLimit(FixtureCase):
    limit = 3

    def test_limit_reached_denies_with_a_message_to_report_the_gap(self):
        self.fx.activate()
        for i in range(3):
            self.assertDecision(self.fx.pre("Read", {"file_path": self.fx.p("lifecycle.md")}), "silent", f"call {i + 1}")
        res = self.fx.pre("Read", {"file_path": self.fx.p("lifecycle.md")})
        self.assertDecision(res, "deny")
        self.assertIn("context limit", res.reason().lower())
        self.assertIn("gap", res.reason().lower())


def settings_path():
    """The settings file under test. VERIFY_SETTINGS_PATH points at a staged copy before the switch."""
    override = os.environ.get("VERIFY_SETTINGS_PATH")
    return (REPO / override) if override else REPO / ".claude" / "settings.json"


def load_settings():
    path = settings_path()
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


class TestMissingScriptGuard(unittest.TestCase):
    """Python exits with 2 when the script file is missing, and exit 2 blocks the tool call.
    The configured command must exit 1 (a visible, non-blocking error) instead: never 0, never 2."""

    def command(self):
        entries = load_settings().get("hooks", {}).get("PreToolUse", [])
        commands = [h.get("command", "") for e in entries for h in e.get("hooks", [])]
        self.assertTrue(commands, "no PreToolUse command configured")
        return commands[0]

    def run_command(self, project, stdin="{}", env_extra=None, drop_project_dir=False):
        env = dict(os.environ)
        env["CLAUDE_PROJECT_DIR"] = str(project).replace("\\", "/")
        if drop_project_dir:
            env.pop("CLAUDE_PROJECT_DIR")
        env.update(env_extra or {})
        return subprocess.run(self.command(), shell=True, input=stdin, capture_output=True, text=True,
                              env=env, timeout=30)

    def test_missing_script_exits_1(self):
        with tempfile.TemporaryDirectory() as tmp:
            proc = self.run_command(tmp)
            self.assertEqual(proc.returncode, 1, f"rc={proc.returncode} err={proc.stderr[:200]!r}")

    def test_missing_project_dir_variable_exits_1(self):
        with tempfile.TemporaryDirectory() as tmp:
            proc = self.run_command(tmp, drop_project_dir=True)
            self.assertEqual(proc.returncode, 1, f"rc={proc.returncode} err={proc.stderr[:200]!r}")

    def test_script_exit_2_is_passed_through(self):
        """The guard must not swallow a real block."""
        with tempfile.TemporaryDirectory() as tmp:
            script = Path(tmp) / "scripts" / "hooks" / "verify_contract.py"
            script.parent.mkdir(parents=True)
            script.write_text("import sys\nsys.stdin.read()\nsys.exit(2)\n", encoding="utf-8")
            proc = self.run_command(tmp)
            self.assertEqual(proc.returncode, 2, f"rc={proc.returncode} err={proc.stderr[:200]!r}")

    def test_real_script_present_and_inactive_exits_0(self):
        fx = Fixture()
        try:
            dest = fx.project / "scripts" / "hooks" / "verify_contract.py"
            dest.parent.mkdir(parents=True)
            dest.write_text(HOOK.read_text(encoding="utf-8"), encoding="utf-8")
            event = json.dumps({"hook_event_name": "PreToolUse", "session_id": "g1", "tool_name": "Read",
                                "tool_input": {"file_path": str(fx.project / "lifecycle.md")}})
            proc = self.run_command(fx.project, stdin=event)
            self.assertEqual(proc.returncode, 0, f"rc={proc.returncode} err={proc.stderr[:200]!r}")
            self.assertEqual(proc.stdout.strip(), "")
        finally:
            fx.cleanup()


class TestConfiguration(unittest.TestCase):
    """The shipped configuration, not a fixture."""

    def setUp(self):
        self.settings = load_settings()

    def entries(self, event):
        return self.settings.get("hooks", {}).get(event, [])

    def matcher_covers(self, event, tools):
        pattern = "|".join(e.get("matcher", "") for e in self.entries(event) if e.get("matcher"))
        return all(re.fullmatch(pattern, t) is not None for t in tools) if pattern else False

    def commands(self, event):
        return [h.get("command", "") for e in self.entries(event) for h in e.get("hooks", [])]

    def test_pretooluse_matcher_covers_all_required_tools(self):
        self.assertTrue(self.matcher_covers("PreToolUse", ["Read", "Grep", "Glob", "Bash", "Write", "Edit", "Skill"]),
                        "PreToolUse must cover Read|Grep|Glob|Bash|Write|Edit (and Skill for activation)")

    def test_posttooluse_matcher_covers_the_read_tools(self):
        self.assertTrue(self.matcher_covers("PostToolUse", ["Read", "Grep", "Glob"]))

    def test_stop_hook_is_configured(self):
        self.assertTrue(self.entries("Stop"), "no Stop hook configured")

    def test_all_hooks_call_the_contract_script_and_not_the_smoke_test(self):
        commands = [c for ev in ("PreToolUse", "PostToolUse", "Stop") for c in self.commands(ev)]
        self.assertTrue(commands, "no hook commands configured")
        for c in commands:
            self.assertIn("verify_contract.py", c)
            self.assertNotIn("smoke.py", c)

    def test_shipped_contract_matches_the_design(self):
        path = REPO / "harness" / "verify-contract.json"
        self.assertTrue(path.exists(), "harness/verify-contract.json is missing")
        contract = json.loads(path.read_text(encoding="utf-8"))
        required = {r["path"] for r in contract.get("required_reads", [])}
        self.assertEqual(required, {"skills/verify/SKILL.md", "traces/transition-log.md",
                                    "lifecycle.md", "traces/worked-case.md"})
        self.assertIn("SEED-MANIFEST.md", contract.get("prohibited_path_names", []))
        self.assertIn("heldout", contract.get("prohibited_substrings", []))
        self.assertEqual(contract.get("max_blocks"), 3)
        self.assertIn("provisional", contract.get("context_limit_note", ""))

    def test_no_hook_sets_onfailure_block(self):
        """Hooks with onFailure "block" are the documented exception to non-blocking failures."""
        def has_block(node):
            if isinstance(node, dict):
                return node.get("onFailure") == "block" or any(has_block(v) for v in node.values())
            if isinstance(node, list):
                return any(has_block(v) for v in node)
            return False

        for path in (REPO / ".claude" / "settings.json", REPO / "harness" / "settings.definitive.json",
                     settings_path()):
            with self.subTest(file=str(path)):
                self.assertTrue(path.exists(), f"{path} is missing")
                self.assertFalse(has_block(json.loads(path.read_text(encoding="utf-8"))),
                                 "a hook sets onFailure to block")

    def test_active_settings_are_identical_to_the_definitive_file(self):
        if os.environ.get("VERIFY_SETTINGS_PATH"):
            self.skipTest("staged mode (VERIFY_SETTINGS_PATH is set): checked after the switch, without it")
        active = (REPO / ".claude" / "settings.json").read_text(encoding="utf-8").replace("\r\n", "\n")
        definitive = (REPO / "harness" / "settings.definitive.json").read_text(encoding="utf-8").replace("\r\n", "\n")
        self.assertEqual(active, definitive, ".claude/settings.json differs from harness/settings.definitive.json")

    def test_the_hook_script_exists(self):
        self.assertTrue(HOOK.exists(), f"{HOOK} is missing")


if __name__ == "__main__":
    result = unittest.main(verbosity=2, exit=False)
    if FINDINGS:
        print("\nFINDINGS (not failures):")
        for f in FINDINGS:
            print(" -", f)
    code = 0 if result.result.wasSuccessful() else 1
    print(f"selftest exit code: {code}")
    sys.exit(code)
