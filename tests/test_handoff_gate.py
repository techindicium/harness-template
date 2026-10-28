"""Regression matrix for the handoff gate (scripts/hooks/handoff_gate.py).

Run from the repository root:

    python3 -m unittest tests/test_handoff_gate.py -v

The contract of the gate is its exit code: 2 blocks (adapter), 1 reports (CLI), 0 lets the
action pass. A case that expects 0 is worth as much as one that expects 2: a gate that blocks
honest use gets switched off, and a gate that never blocks is worse than none, so both sides are
pinned. Every bypass route a shell or a path can take to the same artifact has its own case.
"""

import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "hooks" / "handoff_gate.py"
ITEM = "REQUEST-007"
HANDOFF = f"handoff-{ITEM}.md"
FIGURES = f"figures-{ITEM}.csv"

CLEAN = {
    f"approve-{ITEM}.md": "status: approved\napproved_by: Maria Silva\napproved_at: 2026-10-01T10:00:00\n",
    f"verify-{ITEM}.md": (
        "shape_tests_verdict: pass\n"
        "definition_alignment_verdict: aligned\n"
        "period_alignment_verdict: match\n"
        "verify_status: clear\n"
    ),
    f"context-{ITEM}.md": "period_match: true\n",
    f"build-{ITEM}.md": "exit_code: 0\n",
}

# The shape of the real REQUEST-007 evidence: verify blocked, approve refused, partial period.
BLOCKED = {
    f"approve-{ITEM}.md": "status: refused_entry_condition_not_met\napproved_by: none\napproved_at: none\n",
    f"verify-{ITEM}.md": (
        "shape_tests_verdict: pass\n"
        "definition_alignment_verdict: misaligned\n"
        "period_alignment_verdict: mismatch\n"
        "verify_status: blocked\n"
    ),
    f"context-{ITEM}.md": "period_match: false   # the extract stops before the end of the month\n",
    f"build-{ITEM}.md": "exit_code: 0\n",
}

SECTIONS = ("BLOCKED", "WHY", "FOUND", "DO NOT", "NEXT", "ASK THE USER")
PRODUCT_NAMES = re.compile(r"claude|anthropic|openai|gpt|codex|cursor|copilot|gemini", re.I)


def load_gate():
    spec = importlib.util.spec_from_file_location("handoff_gate", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class GateCase(unittest.TestCase):
    """Builds a throwaway project and runs the gate against it."""

    def project(self, evidence):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        proj = Path(tmp.name).resolve()
        for sub in ("evidence", "delivery", "notes", "traces"):
            (proj / sub).mkdir()
        for name, text in evidence.items():
            (proj / "evidence" / name).write_text(text)
        return proj

    def run_gate(self, proj, args, stdin="", cwd=None, env_extra=None, keep_project_env=True):
        env = {k: v for k, v in os.environ.items() if k not in ("CLAUDE_PROJECT_DIR", "HANDOFF_GATE_LOG")}
        if keep_project_env:
            env["CLAUDE_PROJECT_DIR"] = str(proj)
        env.update(env_extra or {})
        done = subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            input=stdin, capture_output=True, text=True, cwd=str(cwd or proj), env=env,
        )
        return done.returncode, done.stderr

    def hook(self, proj, payload, cwd=None):
        payload = {"cwd": str(cwd or proj), **payload}
        return self.run_gate(proj, ["hook"], stdin=json.dumps(payload), cwd=cwd)

    def write(self, proj, path, tool="Write", cwd=None):
        return self.hook(
            proj, {"hook_event_name": "PreToolUse", "tool_name": tool, "tool_input": {"file_path": path}}, cwd
        )

    def bash(self, proj, command, cwd=None):
        return self.hook(
            proj, {"hook_event_name": "PreToolUse", "tool_name": "Bash", "tool_input": {"command": command}}, cwd
        )

    def stop(self, proj, active=False):
        return self.hook(proj, {"hook_event_name": "Stop", "stop_hook_active": active})

    def assertBlocked(self, result, msg=None):
        # Python itself exits 2 when it cannot open the script, which is also the blocking code.
        # Requiring the gate's own message keeps a missing or crashing script from passing as a block.
        code, err = result
        self.assertEqual(code, 2, msg or f"expected exit 2, got {code}: {err}")
        self.assertIn("BLOCKED", err, msg or f"exit 2 without the gate's message: {err}")
        return err

    def assertPasses(self, result, msg=None):
        code, err = result
        self.assertEqual(code, 0, msg or f"expected exit 0, got {code}: {err}")


class TestCore(GateCase):
    def setUp(self):
        self.gate = load_gate()

    def test_person_names(self):
        names = ["Maria Silva", "José da Silva", "Declan Byrne"]
        not_names = [
            "", "UNKNOWN", "unknown", "none", "null", "TBD", "N/A", "Analytics lead", "the owner",
            "<name>", "[name UNKNOWN]", "UNKNOWN (Analytics lead)", "approver", "12345", "pending",
        ]
        for value in names:
            with self.subTest(value=value):
                self.assertTrue(self.gate.is_person(value))
        for value in not_names:
            with self.subTest(value=value):
                self.assertFalse(self.gate.is_person(value))

    def test_clean_evidence_has_no_failures(self):
        proj = self.project(CLEAN)
        self.assertEqual(self.gate.check_item(proj / "evidence", ITEM), [])

    def test_real_blocked_shape_fails_every_stage_but_build(self):
        proj = self.project(BLOCKED)
        checks = {f["check"] for f in self.gate.check_item(proj / "evidence", ITEM)}
        self.assertEqual(checks, {"approval", "verify", "period"})

    def test_missing_evidence_is_a_failure(self):
        proj = self.project({})
        failures = self.gate.check_item(proj / "evidence", ITEM)
        self.assertEqual({f["check"] for f in failures}, {"approval", "verify", "period", "build"})
        self.assertTrue(all(f["found"] == "missing" for f in failures))

    def test_clear_status_with_unclean_verdict_is_incoherent(self):
        evidence = dict(CLEAN)
        evidence[f"verify-{ITEM}.md"] = evidence[f"verify-{ITEM}.md"].replace("aligned", "misaligned", 1)
        proj = self.project(evidence)
        checks = {f["check"] for f in self.gate.check_item(proj / "evidence", ITEM)}
        self.assertEqual(checks, {"incoherent"})

    def test_approved_by_values(self):
        for value, ok in [("Maria Silva", True), ("UNKNOWN", False), ("Analytics lead", False), ("<name>", False), ("", False)]:
            with self.subTest(value=value):
                evidence = dict(CLEAN)
                evidence[f"approve-{ITEM}.md"] = f"status: approved\napproved_by: {value}\napproved_at: 2026-10-01\n"
                proj = self.project(evidence)
                failures = self.gate.check_item(proj / "evidence", ITEM)
                self.assertEqual(failures == [], ok)

    def test_targets_in_text(self):
        found = self.gate.find_targets(f"cd evidence && echo x > ../evidence/{HANDOFF}")
        self.assertEqual([(t.name, t.item_id) for t in found], [(HANDOFF, ITEM)])
        self.assertEqual(self.gate.find_targets("echo handoff and figures"), [])
        self.assertEqual(self.gate.find_targets("notes/handoff-summary.md"), [])


class TestBypassIsBlocked(GateCase):
    """Every route to the same artifact reaches the same decision."""

    def setUp(self):
        self.proj = self.project(BLOCKED)

    def test_write_tool_paths(self):
        p = self.proj
        (p / "alias.md").symlink_to(p / "evidence" / HANDOFF)
        cases = [
            ("absolute", str(p / "evidence" / HANDOFF), None),
            ("relative", f"evidence/{HANDOFF}", p),
            ("dot-slash and dotdot", f"./evidence/../evidence/{HANDOFF}", p),
            ("bare name after cd", HANDOFF, p / "evidence"),
            ("dotdot from a subdirectory", f"../evidence/{HANDOFF}", p / "notes"),
            ("symlink with another name", str(p / "alias.md"), None),
            ("uppercase", f"EVIDENCE/{HANDOFF.upper()}", p),
            ("delivery file", str(p / "delivery" / FIGURES), None),
        ]
        for label, path, cwd in cases:
            with self.subTest(label):
                self.assertBlocked(self.write(p, path, cwd=cwd))

    def test_edit_tool(self):
        self.assertBlocked(self.write(self.proj, str(self.proj / "evidence" / HANDOFF), tool="Edit"))

    def test_shell_forms(self):
        p = self.proj
        cases = [
            ("redirect", f"echo x > evidence/{HANDOFF}"),
            ("append", f"echo x >> evidence/{HANDOFF}"),
            ("cd then bare name", f"cd evidence && echo x > {HANDOFF}"),
            ("cd on its own line", f"cd evidence\necho x > {HANDOFF}"),
            ("tee", f"cat foo | tee evidence/{HANDOFF}"),
            ("sed -i", f"sed -i s/a/b/ evidence/{HANDOFF}"),
            ("cp", f"cp /tmp/x.md evidence/{HANDOFF}"),
            ("mv with dot-slash", f"mv /tmp/x.md ./evidence/{HANDOFF}"),
            ("touch", f"touch evidence/{HANDOFF}"),
            ("absolute path", f"cp /tmp/x.md {p}/evidence/{HANDOFF}"),
            ("python inline", f"python3 -c \"open('evidence/{HANDOFF}', 'w').write('x')\""),
            ("bash -c", f"bash -c 'echo x > evidence/{HANDOFF}'"),
            ("wrapped by a proxy", f"rtk proxy 'echo x > evidence/{HANDOFF}'"),
            ("sudo", f"sudo cp a evidence/{HANDOFF}"),
            ("cat that redirects", f"cat evidence/approve-{ITEM}.md > evidence/{HANDOFF}"),
            ("git add", f"git add evidence/{HANDOFF}"),
            ("delivery csv", f"echo x > delivery/{FIGURES}"),
            ("chained after a read", f"ls evidence && echo x > evidence/{HANDOFF}"),
        ]
        for label, command in cases:
            with self.subTest(label):
                self.assertBlocked(self.bash(p, command))

    def test_unreadable_payload_that_names_an_artifact_fails_closed(self):
        cases = [
            ("not json", f"this is not json but names evidence/{HANDOFF}"),
            ("tool_input is not an object", json.dumps({"hook_event_name": "PreToolUse", "tool_name": "Bash", "tool_input": f"x {HANDOFF}"})),
        ]
        for label, raw in cases:
            with self.subTest(label):
                self.assertBlocked(self.run_gate(self.proj, ["hook"], stdin=raw))

    def test_stop_audit_catches_what_the_shell_parser_cannot_see(self):
        (self.proj / "evidence" / HANDOFF).write_text("written by a script, name built at run time\n")
        self.assertBlocked(self.stop(self.proj))


class TestHonestUseIsNotBlocked(GateCase):
    def test_clean_evidence_lets_the_handoff_through(self):
        proj = self.project(CLEAN)
        self.assertPasses(self.write(proj, str(proj / "evidence" / HANDOFF)))
        self.assertPasses(self.bash(proj, f"cp /tmp/x.md delivery/{FIGURES}"))

    def test_paths_that_are_not_artifacts(self):
        proj = self.project(BLOCKED)
        for path in ("notes/foo.md", f"evidence/approve-{ITEM}.md", "notes/handoff-summary.md", "traces/gate-decisions.jsonl"):
            with self.subTest(path):
                self.assertPasses(self.write(proj, str(proj / path)))

    def test_reading_an_artifact_is_allowed_even_when_not_cleared(self):
        proj = self.project(BLOCKED)
        for command in (
            f"cat evidence/{HANDOFF}",
            f"head -5 evidence/{HANDOFF}",
            f"grep -n x evidence/{HANDOFF}",
            f"wc -l evidence/{HANDOFF}",
            f"ls -l evidence/{HANDOFF}",
            f"diff evidence/{HANDOFF} /tmp/other.md",
            f"git diff -- evidence/{HANDOFF}",
            "git status",
            f"git log --oneline -- evidence/{HANDOFF}",
            f"rtk proxy 'cat evidence/{HANDOFF}'",
            "echo handoff and figures",
            f"cat evidence/approve-{ITEM}.md",
        ):
            with self.subTest(command):
                self.assertPasses(self.bash(proj, command))

    def test_other_tools_are_ignored(self):
        proj = self.project(BLOCKED)
        payload = {"hook_event_name": "PreToolUse", "tool_name": "Read", "tool_input": {"file_path": str(proj / "evidence" / HANDOFF)}}
        self.assertPasses(self.hook(proj, payload))

    def test_unreadable_payload_without_a_protected_name_passes(self):
        proj = self.project(BLOCKED)
        self.assertPasses(self.run_gate(proj, ["hook"], stdin="not json at all"))


class TestStopAudit(GateCase):
    def test_orphan_artifact_blocks_the_end_of_the_turn(self):
        proj = self.project(BLOCKED)
        (proj / "evidence" / HANDOFF).write_text("x\n")
        err = self.assertBlocked(self.stop(proj))
        self.assertIn(HANDOFF, err)

    def test_loop_guard_lets_the_turn_end(self):
        proj = self.project(BLOCKED)
        (proj / "evidence" / HANDOFF).write_text("x\n")
        self.assertPasses(self.stop(proj, active=True))

    def test_nothing_to_audit(self):
        self.assertPasses(self.stop(self.project(BLOCKED)))

    def test_cleared_artifact_passes_the_audit(self):
        proj = self.project(CLEAN)
        (proj / "evidence" / HANDOFF).write_text("x\n")
        self.assertPasses(self.stop(proj))


class TestCli(GateCase):
    """The gate works without the hook adapter, and without any project environment variable."""

    def test_check(self):
        blocked = self.project(BLOCKED)
        code, err = self.run_gate(blocked, ["check", ITEM], keep_project_env=False)
        self.assertEqual(code, 1)
        self.assertIn("BLOCKED", err)
        clean = self.project(CLEAN)
        self.assertEqual(self.run_gate(clean, ["check", ITEM], keep_project_env=False)[0], 0)

    def test_audit(self):
        blocked = self.project(BLOCKED)
        (blocked / "evidence" / HANDOFF).write_text("x\n")
        self.assertEqual(self.run_gate(blocked, ["audit"], keep_project_env=False)[0], 1)
        clean = self.project(CLEAN)
        (clean / "evidence" / HANDOFF).write_text("x\n")
        self.assertEqual(self.run_gate(clean, ["audit"], keep_project_env=False)[0], 0)

    def test_cli_works_from_a_subdirectory(self):
        blocked = self.project(BLOCKED)
        self.assertEqual(self.run_gate(blocked, ["check", ITEM], cwd=blocked / "notes", keep_project_env=False)[0], 1)


class TestMessageContract(GateCase):
    """A block has to tell the agent why, what is wrong, what not to do, and what to ask."""

    def message(self, evidence):
        proj = self.project(evidence)
        return self.assertBlocked(self.write(proj, str(proj / "evidence" / HANDOFF)))

    def test_has_every_section_and_names_no_product(self):
        proj = self.project(BLOCKED)
        err = self.assertBlocked(self.write(proj, str(proj / "evidence" / HANDOFF)))
        for section in SECTIONS:
            self.assertRegex(err, rf"(?m)^{section}\b", f"missing section {section}")
        # The random temporary path is not part of the wording being checked.
        self.assertIsNone(PRODUCT_NAMES.search(err.replace(str(proj), "")))

    def test_missing_approver_asks_who_the_approver_is(self):
        self.assertIn(f"Who is the named approver for {ITEM}?", self.message(BLOCKED))

    def test_blocked_verify_asks_where_the_item_goes(self):
        self.assertIn("Correction required or Escalated", self.message(BLOCKED))

    def test_partial_period_asks_about_the_extract(self):
        self.assertIn("does not cover the period", self.message(BLOCKED))

    def test_failed_build(self):
        evidence = dict(CLEAN)
        evidence[f"build-{ITEM}.md"] = "exit_code: 1\n"
        self.assertIn("did not succeed", self.message(evidence))

    def test_incoherent_verify(self):
        evidence = dict(CLEAN)
        evidence[f"verify-{ITEM}.md"] = evidence[f"verify-{ITEM}.md"].replace("aligned", "misaligned", 1)
        self.assertIn("contradicts itself", self.message(evidence))

    def test_forbids_retrying_through_another_path_and_editing_evidence(self):
        err = self.message(BLOCKED)
        self.assertRegex(err, r"(?i)another path")
        self.assertRegex(err, r"(?i)do not edit the evidence")

    def test_audit_message_names_the_artifact(self):
        proj = self.project(BLOCKED)
        (proj / "evidence" / HANDOFF).write_text("x\n")
        err = self.assertBlocked(self.stop(proj))
        for section in SECTIONS:
            self.assertRegex(err, rf"(?m)^{section}\b")
        self.assertIn("removed or the evidence completed", err)


class TestTrace(GateCase):
    def records(self, proj):
        path = proj / "traces" / "gate-decisions.jsonl"
        if not path.exists():
            return []
        return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]

    def test_block_is_recorded(self):
        proj = self.project(BLOCKED)
        self.assertBlocked(self.write(proj, str(proj / "evidence" / HANDOFF)))
        (record,) = self.records(proj)
        self.assertEqual((record["decision"], record["item"], record["event"]), ("block", ITEM, "PreToolUse"))
        self.assertEqual(set(record["failed"]), {"approval", "verify", "period"})
        for key in ("ts", "tool", "target"):
            self.assertIn(key, record)
        self.assertEqual(record["target"], f"evidence/{HANDOFF}")

    def test_log_never_holds_the_path_of_the_machine(self):
        proj = self.project(BLOCKED)
        (proj / "alias.md").symlink_to(proj / "evidence" / HANDOFF)
        for path, cwd in ((str(proj / "evidence" / HANDOFF), None), (f"../evidence/{HANDOFF}", proj / "notes"), (str(proj / "alias.md"), None)):
            self.assertBlocked(self.write(proj, path, cwd=cwd))
        log = (proj / "traces" / "gate-decisions.jsonl").read_text()
        self.assertNotIn(str(proj), log)
        self.assertEqual({json.loads(line)["target"] for line in log.splitlines()}, {f"evidence/{HANDOFF}"})

    def test_target_outside_the_project_is_recorded_in_full(self):
        proj = self.project(BLOCKED)
        elsewhere = self.project(BLOCKED)
        self.assertBlocked(self.write(proj, str(elsewhere / "evidence" / HANDOFF)))
        (record,) = self.records(proj)
        self.assertEqual(record["target"], str(elsewhere / "evidence" / HANDOFF))

    def test_allow_of_a_controlled_target_is_recorded(self):
        proj = self.project(CLEAN)
        self.assertPasses(self.write(proj, str(proj / "evidence" / HANDOFF)))
        (record,) = self.records(proj)
        self.assertEqual((record["decision"], record["failed"]), ("allow", []))

    def test_uncontrolled_path_leaves_no_record(self):
        proj = self.project(BLOCKED)
        self.assertPasses(self.write(proj, str(proj / "notes" / "foo.md")))
        self.assertEqual(self.records(proj), [])

    def test_log_location_can_be_overridden(self):
        proj = self.project(BLOCKED)
        elsewhere = proj / "notes" / "elsewhere.jsonl"
        payload = {"cwd": str(proj), "hook_event_name": "PreToolUse", "tool_name": "Write", "tool_input": {"file_path": str(proj / "evidence" / HANDOFF)}}
        self.run_gate(proj, ["hook"], stdin=json.dumps(payload), env_extra={"HANDOFF_GATE_LOG": str(elsewhere)})
        self.assertTrue(elsewhere.exists())
        self.assertEqual(self.records(proj), [])


class TestRealEvidence(GateCase):
    """The evidence the group recorded for REQUEST-007 blocks the handoff, untouched."""

    def test_repository_evidence_blocks(self):
        source = REPO / "evidence"
        if not source.joinpath(f"verify-{ITEM}.md").exists():
            self.skipTest("REQUEST-007 evidence is not in this checkout")
        proj = self.project({})
        for stage in ("approve", "verify", "context", "build"):
            name = f"{stage}-{ITEM}.md"
            (proj / "evidence" / name).write_text((source / name).read_text())
        err = self.assertBlocked(self.write(proj, str(proj / "evidence" / HANDOFF)))
        self.assertIn("verify", err)
        self.assertIn("approved_by", err)


if __name__ == "__main__":
    unittest.main()
