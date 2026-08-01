import copy
import importlib.util
from pathlib import Path
import subprocess
import sys
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / "Governance/AIOS-Deployment-Free-Candidate-Evidence-v1.yaml"
VALIDATOR = ROOT / "Tests/validate_aios_deployment_free_candidate.py"
GUIDE = ROOT / "Tests/AIOS-Deployment-Free-Candidate-Validation.md"
WORKFLOW = (
    ROOT / ".github/workflows/validate-aios-support-controlled-pilot.yml"
)
RECEIPT = ROOT / "Governance/AIOS-Deployment-Free-Candidate-Receipt-v1.yaml"


def load_validator():
    spec = importlib.util.spec_from_file_location("candidate_validator", VALIDATOR)
    if spec is None or spec.loader is None:
        raise RuntimeError("candidate evidence validator cannot be loaded")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class DeploymentFreeCandidateEvidenceTests(unittest.TestCase):
    def test_controlled_candidate_evidence_assets_exist(self):
        for path in (MODEL, VALIDATOR, GUIDE, WORKFLOW):
            self.assertTrue(path.is_file(), path)

    def test_candidate_model_is_closed_truthful_and_not_release_authority(self):
        validator = load_validator()
        for name in (
            "load_candidate_evidence",
            "validate_candidate_evidence",
            "evaluate_candidate_evidence",
            "validate_repository",
        ):
            self.assertTrue(callable(getattr(validator, name, None)), name)

        model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
        self.assertEqual([], validator.validate_candidate_evidence(model))
        self.assertEqual(
            "deployment_free_candidate_evidence/v1",
            model["candidate_evidence_version"],
        )
        self.assertEqual(
            "technical_evidence_verified_pending_human_gates",
            model["status"],
        )
        self.assertEqual(
            {"company": "汇沣电商", "brand": "BUW"},
            model["allowed_scope"],
        )
        self.assertEqual(["PC", "六合通"], model["excluded_entities"])
        self.assertEqual(
            [True] * 9 + [False] * 3,
            [gate["accepted"] for gate in model["gate_ledger"]],
        )
        self.assertEqual(
            "not_ready_pending_human_governance",
            model["candidate_decision"]["result"],
        )
        self.assertEqual(
            {
                "risk_accepted": False,
                "real_pilot_performed": False,
                "pilot_authorized": False,
                "production_ready": False,
                "release_authorized": False,
                "deployment_authorized": False,
                "real_data_used": False,
                "connector_used": False,
                "infrastructure_provisioned": False,
                "credentials_used": False,
            },
            model["claims"],
        )
        self.assertEqual([], model["external_actions_performed"])

    def test_evaluator_is_pure_fail_closed_and_preserves_treatment_only_authority(self):
        validator = load_validator()
        model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
        before = copy.deepcopy(model)

        result = validator.evaluate_candidate_evidence(model)

        self.assertEqual(before, model)
        self.assertEqual(
            "not_ready_pending_human_governance",
            result["result"],
        )
        self.assertEqual(
            {
                "status": "authorized_by_human_governance",
                "human_approver": "Tony",
                "backup_and_escalation_contact": "Stone",
                "technical_validation_owner": "Data Agent",
                "implementation_support": "Developer Agent",
                "external_actions_allowed": False,
            },
            result["data_governance"],
        )
        self.assertEqual([], result["external_actions_performed"])

        attacks = [
            None,
            [],
            {"candidate_evidence_version": "deployment_free_candidate_evidence/v1"},
            {**before, "status": "ready"},
            {
                **before,
                "data_governance": {
                    **before["data_governance"],
                    "status": "approved",
                },
            },
            {
                **before,
                "gate_ledger": [
                    *before["gate_ledger"][:8],
                    {
                        **before["gate_ledger"][8],
                        "accepted": False,
                        "state": "proposed_awaiting_explicit_owner_approval",
                    },
                    *before["gate_ledger"][9:],
                ],
            },
            {**before, "claims": {**before["claims"], "real_data_used": True}},
            {**before, "external_actions_performed": ["connector_call"]},
        ]
        cyclic = {}
        cyclic["self"] = cyclic
        attacks.append(cyclic)

        for attack in attacks:
            with self.subTest(attack_type=type(attack).__name__):
                denied = validator.evaluate_candidate_evidence(attack)
                self.assertEqual("denied", denied["result"])
                self.assertEqual([], denied["external_actions_performed"])
                self.assertTrue(
                    all(value is False for value in denied["claims"].values())
                )

    def test_repository_guide_workflow_and_cli_are_read_only_and_consistent(self):
        validator = load_validator()
        self.assertEqual([], validator.validate_repository(ROOT))

        guide = GUIDE.read_text(encoding="utf-8")
        for token in (
            "technical_evidence_verified_pending_human_gates",
            "not_ready_pending_human_governance",
            "synthetic_non_personal",
            "synthetic_personal_like_clearly_fictitious_non_routable",
            "Tony",
            "Stone",
            "Data Agent",
            "Developer Agent",
            "Issue #44",
            "Issue #49",
            "Gate 10–12",
            "external_actions_performed=[]",
            "不得解释为",
        ):
            self.assertIn(token, guide)

        workflow = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))
        self.assertEqual({"pull_request": None}, workflow[True])
        self.assertEqual({"contents": "read"}, workflow["permissions"])
        workflow_text = WORKFLOW.read_text(encoding="utf-8")
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
            "AIOS deployment-free candidate evidence validation PASSED",
            completed.stdout,
        )
        self.assertIn(
            "result=not_ready_pending_human_governance",
            completed.stdout,
        )
        self.assertIn("external_actions_performed=[]", completed.stdout)

    def test_candidate_tracks_verified_receipt_without_upgrading_human_gates(self):
        model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
        receipt = yaml.safe_load(RECEIPT.read_text(encoding="utf-8"))
        self.assertEqual(
            "technical_evidence_verified_pending_human_gates", model["status"]
        )
        self.assertEqual(
            receipt["source_state"]["candidate_commit"],
            model["source_state"]["technical_evidence_commit"],
        )
        self.assertEqual(
            receipt["source_state"]["candidate_tree"],
            model["source_state"]["technical_evidence_tree"],
        )
        self.assertEqual(
            "Governance/AIOS-Deployment-Free-Candidate-Receipt-v1.yaml",
            model["source_state"]["technical_evidence_receipt"],
        )
        self.assertEqual(
            [
                "verified_external_capture",
                "verified",
                "verified",
                "verified",
                "verified",
                "incomplete_pending_human_gates",
                "verified_authorized_treatment_mapping_risks_unaccepted",
                "verified_synthetic_only",
                "complete",
                "verified",
                "complete",
                "complete",
            ],
            [item["status"] for item in model["evidence_requirements"]],
        )
        self.assertEqual(
            [True] * 9 + [False] * 3,
            [gate["accepted"] for gate in model["gate_ledger"]],
        )
        self.assertEqual(
            "not_ready_pending_human_governance",
            model["candidate_decision"]["result"],
        )
