"""Layer A of the Module 4 eval: the dev cases in cases.json, run against the handoff gate.

Run from the repository root:

    python3 tests/eval/test_eval_cases.py

A case names the evidence it is built from, the track it runs on, and the exit code `check` has to
return. Two rules are scored, both by exact match on exit codes. R1: the exit code of
`handoff_gate.py check <ID>`, with the gate's own message when it blocks. R2: the hook refuses the
two artifacts of the handoff (exit 2) exactly when the case expects `check` to exit 1, and lets them
through (exit 0) otherwise. Layer A never writes the artifact, so it does not score the half of R2
that says the file does not exist. Which check blocked is pinned by the test named in `covered_by`,
not here.

The cases reuse the evidence and the helpers of the regression matrix of the gate. `covered_by` names
the test there that already pins the scenario; this file adds the table, not new coverage of the gate.
"""

import json
import sys
import unittest
from pathlib import Path

sys.dont_write_bytecode = True  # the helpers are imported from source; leave no __pycache__ beside them
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # tests/, where the helpers live

import test_handoff_gate
from test_handoff_gate import ASSIST_TRACK, BLOCKED, CLEAN, FIGURES, HANDOFF, ITEM, GateCase, with_metric

CASES = json.loads(Path(__file__).with_name("cases.json").read_text())


def clear_but_misaligned():
    evidence = dict(CLEAN)
    evidence[f"verify-{ITEM}.md"] = evidence[f"verify-{ITEM}.md"].replace("aligned", "misaligned", 1)
    return evidence


EVIDENCE = {
    "clean": CLEAN,
    "blocked": BLOCKED,
    "self-service": with_metric("self_service_rate"),
    "first-response": with_metric("first_response_minutes_p50"),
    "notes-disagree": with_metric("self_service_rate", route="first_response_minutes_p50"),
    "clear-but-misaligned": clear_but_misaligned(),
}
TRACKS = {"clean": None, "assist": ASSIST_TRACK}


class TestEvalCases(GateCase):
    def project_for(self, case):
        return self.project(EVIDENCE[case["evidence"]], TRACKS[case["track"]])

    def test_both_sides_are_pinned(self):
        # A table with no case that expects a pass, or none that expects a block, scores nothing.
        self.assertEqual({case["expect_check_exit"] for case in CASES}, {0, 1})

    def test_covered_by_names_a_test_that_exists(self):
        # A renamed test would leave the pointer false and the suite green; a helper is not a test.
        for case in CASES:
            with self.subTest(case["id"]):
                name, method = case["covered_by"].split(".")
                found = method.startswith("test") and callable(getattr(getattr(test_handoff_gate, name, None), method, None))
                self.assertTrue(found, f"{case['id']}: no test {case['covered_by']} in the regression matrix")

    def test_r1_check_exits_as_the_case_expects(self):
        for case in CASES:
            with self.subTest(case["id"]):
                code, err = self.run_gate(self.project_for(case), ["check", ITEM], keep_project_env=False)
                self.assertEqual(code, case["expect_check_exit"], f"R1 for {case['id']}: {err}")
                if case["expect_check_exit"]:
                    # Python also exits 1 on an uncaught error: a block needs the gate's own message.
                    self.assertIn("BLOCKED", err, f"R1 for {case['id']}: exit 1 without the gate's message: {err}")

    def test_r2_the_hook_refuses_the_artifacts_when_the_case_expects_a_block(self):
        for case in CASES:
            proj = self.project_for(case)
            for artifact in (proj / "evidence" / HANDOFF, proj / "delivery" / FIGURES):
                with self.subTest(f"{case['id']}: {artifact.name}"):
                    result = self.write(proj, str(artifact))
                    if case["expect_check_exit"]:
                        self.assertBlocked(result, f"R2 for {case['id']}: expected a block, got {result}")
                    else:
                        self.assertPasses(result, f"R2 for {case['id']}: expected a pass, got {result}")


if __name__ == "__main__":
    unittest.main()
