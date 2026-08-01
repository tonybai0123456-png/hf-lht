import copy
import importlib.util
from pathlib import Path
import subprocess
import sys
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / "Governance/AIOS-Deployment-Free-Candidate-Receipt-v1.yaml"
VALIDATOR = ROOT / "Tests/validate_aios_deployment_free_candidate_receipt.py"
GUIDE = ROOT / "Tests/AIOS-Deployment-Free-Candidate-Receipt-Validation.md"


def load_validator():
    spec = importlib.util.spec_from_file_location("candidate_receipt", VALIDATOR)
    if spec is None or spec.loader is None:
        raise RuntimeError("candidate receipt validator cannot be loaded")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class DeploymentFreeCandidateReceiptTests(unittest.TestCase):
    def test_receipt_assets_exist(self):
        for path in (MODEL, VALIDATOR, GUIDE):
            self.assertTrue(path.is_file(), path)

    def test_receipt_captures_exact_source_manifest_replay_ci_and_risks(self):
        validator = load_validator()
        model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))

        self.assertEqual([], validator.validate_candidate_receipt(model))
        self.assertEqual(
            "verified_technical_evidence_pending_human_gates", model["status"]
        )
        self.assertEqual(
            "36716abc76373d053c75e68352f46589f4ddc8f1",
            model["source_state"]["candidate_commit"],
        )
        self.assertEqual(
            "ec48f7c537162b32f6bc35947d9e49758e1b53bd",
            model["source_state"]["candidate_tree"],
        )
        self.assertEqual(29, model["changed_file_manifest"]["count"])
        self.assertEqual(
            29, len(model["changed_file_manifest"]["paths"])
        )
        self.assertEqual(
            "git_archive_clean_export",
            model["clean_reproduction"]["source_method"],
        )
        self.assertEqual(127, model["clean_reproduction"]["tests_passed"])
        self.assertEqual(10, model["clean_reproduction"]["validators_passed"])
        self.assertEqual(9, len(model["exact_head_ci"]))
        self.assertTrue(
            all(run["conclusion"] == "success" for run in model["exact_head_ci"])
        )
        self.assertEqual(10, len(model["risk_evidence_and_treatment_mapping"]))
        self.assertTrue(
            all(
                risk["risk_state"] == "open_blocked_unaccepted"
                and risk["risk_accepted"] is False
                and risk["treatment_authorized"] is True
                for risk in model["risk_evidence_and_treatment_mapping"]
            )
        )
        self.assertEqual(
            "not_ready_pending_human_governance",
            model["candidate_decision"]["result"],
        )
        self.assertTrue(all(value is False for value in model["claims"].values()))
        self.assertEqual([], model["external_actions_performed"])

    def test_evaluator_is_pure_and_fails_closed(self):
        validator = load_validator()
        model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
        before = copy.deepcopy(model)

        result = validator.evaluate_candidate_receipt(model)

        self.assertEqual(before, model)
        self.assertEqual(
            "not_ready_pending_human_governance", result["result"]
        )
        self.assertEqual([], result["external_actions_performed"])
        self.assertTrue(all(value is False for value in result["claims"].values()))

        attacks = [
            None,
            [],
            {"receipt_version": "deployment_free_candidate_receipt/v1"},
            {**before, "status": "ready"},
            {
                **before,
                "changed_file_manifest": {
                    **before["changed_file_manifest"],
                    "count": 28,
                },
            },
            {
                **before,
                "clean_reproduction": {
                    **before["clean_reproduction"],
                    "tests_passed": 126,
                },
            },
            {
                **before,
                "exact_head_ci": [
                    {**before["exact_head_ci"][0], "conclusion": "failure"},
                    *before["exact_head_ci"][1:],
                ],
            },
            {
                **before,
                "risk_evidence_and_treatment_mapping": [
                    {
                        **before["risk_evidence_and_treatment_mapping"][0],
                        "risk_accepted": True,
                    },
                    *before["risk_evidence_and_treatment_mapping"][1:],
                ],
            },
            {**before, "claims": {**before["claims"], "production_ready": True}},
            {**before, "external_actions_performed": ["external_write"]},
        ]
        cyclic = {}
        cyclic["self"] = cyclic
        attacks.append(cyclic)

        for attack in attacks:
            with self.subTest(attack_type=type(attack).__name__):
                denied = validator.evaluate_candidate_receipt(attack)
                self.assertEqual("denied", denied["result"])
                self.assertEqual([], denied["external_actions_performed"])
                self.assertTrue(
                    all(value is False for value in denied["claims"].values())
                )

    def test_repository_guide_cross_checks_and_cli(self):
        validator = load_validator()
        self.assertEqual([], validator.validate_repository(ROOT))
        guide = GUIDE.read_text(encoding="utf-8")
        for token in (
            "36716abc76373d053c75e68352f46589f4ddc8f1",
            "ec48f7c537162b32f6bc35947d9e49758e1b53bd",
            "29",
            "127/127",
            "10/10",
            "9/9",
            "git archive",
            "requirements-dev.txt",
            "PyYAML 6.0.3",
            "open_blocked_unaccepted",
            "Gate 10–11",
            "Issue #49",
            "external_actions_performed=[]",
            "不得解释为",
        ):
            self.assertIn(token, guide)

        completed = subprocess.run(
            [sys.executable, str(VALIDATOR)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertIn(
            "AIOS deployment-free candidate receipt validation PASSED",
            completed.stdout,
        )
        self.assertIn(
            "result=not_ready_pending_human_governance",
            completed.stdout,
        )
        self.assertIn("external_actions_performed=[]", completed.stdout)


if __name__ == "__main__":
    unittest.main()
