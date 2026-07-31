import copy
import importlib.util
from pathlib import Path
import subprocess
import sys
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / "Governance/AIOS-Predeployment-Completion-Audit-v1.yaml"
VALIDATOR = ROOT / "Tests/validate_aios_predeployment_completion_audit.py"
GUIDE = ROOT / "Tests/AIOS-Predeployment-Completion-Audit-Validation.md"
WORKFLOW = (
    ROOT / ".github/workflows/validate-aios-support-controlled-pilot.yml"
)


def load_validator():
    spec = importlib.util.spec_from_file_location(
        "predeployment_audit_validator", VALIDATOR
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("predeployment audit validator cannot be loaded")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class PredeploymentCompletionAuditTests(unittest.TestCase):
    def test_controlled_audit_assets_exist(self):
        for path in (MODEL, VALIDATOR, GUIDE, WORKFLOW):
            self.assertTrue(path.is_file(), path)

    def test_audit_ledger_separates_proven_pending_and_withheld_work(self):
        validator = load_validator()
        model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))

        self.assertEqual([], validator.validate_completion_audit(model))
        self.assertEqual(
            "incomplete_pending_ordered_human_governance", model["status"]
        )
        self.assertEqual(
            {"company": "汇沣电商", "brand": "BUW"},
            model["allowed_scope"],
        )
        self.assertEqual(["PC", "六合通"], model["excluded_entities"])
        self.assertEqual(
            "36716abc76373d053c75e68352f46589f4ddc8f1",
            model["audited_source_state"]["technical_receipt_source_commit"],
        )
        self.assertEqual(
            "Governance/AIOS-Deployment-Free-Candidate-Receipt-v1.yaml",
            model["audited_source_state"]["technical_receipt"],
        )
        self.assertEqual(
            [
                "proven_complete",
                "proven_complete",
                "proven_complete",
                "proven_complete",
                "proven_complete",
                "pending_human_governance",
                "pending_human_governance",
                "pending_human_governance",
                "partial_pending_human_gates",
                "intentionally_withheld",
                "intentionally_excluded",
                "intentionally_excluded_or_withheld",
            ],
            [item["state"] for item in model["requirement_ledger"]],
        )
        self.assertEqual(
            [
                "HG-RISK-DISPOSITION",
                "HG-PILOT-SCOPE",
                "HG-PILOT-EVIDENCE",
            ],
            [item["gate_id"] for item in model["human_decision_queue"]],
        )
        self.assertEqual(
            "not_complete_pending_human_governance",
            model["completion_decision"]["result"],
        )
        self.assertFalse(model["completion_decision"]["release_gate_authorized"])
        self.assertTrue(
            model["completion_decision"]["deployment_free_evidence_only"]
        )
        self.assertTrue(all(value is False for value in model["claims"].values()))
        self.assertEqual([], model["external_actions_performed"])

    def test_evaluator_is_pure_and_fail_closed(self):
        validator = load_validator()
        model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
        before = copy.deepcopy(model)

        result = validator.evaluate_completion_audit(model)

        self.assertEqual(before, model)
        self.assertEqual(
            "not_complete_pending_human_governance", result["result"]
        )
        self.assertEqual([], result["external_actions_performed"])
        self.assertTrue(all(value is False for value in result["claims"].values()))

        attacks = [
            None,
            [],
            {"audit_version": "predeployment_completion_audit/v1"},
            {**before, "status": "complete"},
            {
                **before,
                "human_decision_queue": [
                    {**before["human_decision_queue"][0], "accepted": True},
                    *before["human_decision_queue"][1:],
                ],
            },
            {
                **before,
                "requirement_ledger": [
                    *before["requirement_ledger"][:5],
                    {
                        **before["requirement_ledger"][5],
                        "state": "proven_complete",
                    },
                    *before["requirement_ledger"][6:],
                ],
            },
            {**before, "claims": {**before["claims"], "production_ready": True}},
            {**before, "external_actions_performed": ["connector_call"]},
        ]
        cyclic = {}
        cyclic["self"] = cyclic
        attacks.append(cyclic)

        for attack in attacks:
            with self.subTest(attack_type=type(attack).__name__):
                denied = validator.evaluate_completion_audit(attack)
                self.assertEqual("denied", denied["result"])
                self.assertEqual([], denied["external_actions_performed"])
                self.assertTrue(
                    all(value is False for value in denied["claims"].values())
                )

    def test_repository_cross_checks_guide_workflow_and_cli(self):
        validator = load_validator()
        self.assertEqual([], validator.validate_repository(ROOT))

        guide = GUIDE.read_text(encoding="utf-8")
        for token in (
            "incomplete_pending_ordered_human_governance",
            "not_complete_pending_human_governance",
            "proven_complete",
            "pending_human_governance",
            "intentionally_withheld",
            "intentionally_excluded",
            "Gate 9–11",
            "Issue #44",
            "Issue #49",
            "Stage 10",
            "BLOCKED / NO-GO",
            "external_actions_performed=[]",
            "不得解释为",
        ):
            self.assertIn(token, guide)

        workflow_text = WORKFLOW.read_text(encoding="utf-8")
        workflow = yaml.safe_load(workflow_text)
        self.assertEqual({"pull_request": None}, workflow[True])
        self.assertEqual({"contents": "read"}, workflow["permissions"])
        for forbidden in (
            "workflow_dispatch",
            "schedule:",
            "contents: write",
            "pull-requests: write",
            "persist-credentials: true",
        ):
            self.assertNotIn(forbidden, workflow_text)
        for command in (
            "python3 -m unittest discover -s Tests -p 'test_*.py' -v",
            "python3 -m compileall Tests",
        ):
            self.assertIn(command, workflow_text)

        completed = subprocess.run(
            [sys.executable, str(VALIDATOR)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertIn(
            "AIOS predeployment completion audit validation PASSED",
            completed.stdout,
        )
        self.assertIn(
            "result=not_complete_pending_human_governance",
            completed.stdout,
        )
        self.assertIn("external_actions_performed=[]", completed.stdout)


if __name__ == "__main__":
    unittest.main()
