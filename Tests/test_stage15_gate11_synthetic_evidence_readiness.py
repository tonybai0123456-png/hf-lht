from __future__ import annotations

import copy
import importlib.util
from pathlib import Path
import subprocess
import sys
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[1]
MODEL = (
    ROOT
    / "Governance/AIOS-Stage15-Gate11-Synthetic-Rehearsal-Evidence-Readiness-Audit-v1.yaml"
)
VALIDATOR = ROOT / "Tests/validate_aios_stage15_gate11_synthetic_evidence_readiness.py"


def load_validator():
    spec = importlib.util.spec_from_file_location("gate11_evidence_validator", VALIDATOR)
    if spec is None or spec.loader is None:
        raise RuntimeError("Gate 11 evidence validator cannot be loaded")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Stage15Gate11SyntheticEvidenceReadinessTests(unittest.TestCase):
    def test_gate11_evidence_is_complete_but_stone_approval_remains_required(self):
        self.assertTrue(MODEL.is_file(), MODEL)
        self.assertTrue(VALIDATOR.is_file(), VALIDATOR)
        validator = load_validator()
        model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))

        self.assertEqual([], validator.validate_repository(ROOT))
        self.assertEqual(
            "ready_for_stone_human_evidence_decision_not_approved",
            model["status"],
        )
        self.assertEqual("HG-PILOT-EVIDENCE", model["next_gate"])
        self.assertIs(False, model["gate11_decision_boundary"]["gate_accepted"])
        self.assertEqual("Stone", model["gate11_decision_boundary"]["human_approver"])
        self.assertEqual(
            "d757768e3a06d5443cafec1934011711cb039766",
            model["source_evidence"]["source_commit"],
        )
        self.assertEqual(152, model["source_evidence"]["local_verification"]["tests_passed"])
        self.assertEqual(13, model["source_evidence"]["local_verification"]["validators_passed"])
        self.assertEqual(9, len(model["source_evidence"]["exact_head_ci"]))
        self.assertTrue(
            all(run["conclusion"] == "success" for run in model["source_evidence"]["exact_head_ci"])
        )
        self.assertEqual(
            list(validator.EVIDENCE_IDS),
            [record["evidence_id"] for record in model["synthetic_evidence_results"]],
        )
        self.assertTrue(
            all(record["result"] == "verified_synthetic" for record in model["synthetic_evidence_results"])
        )
        self.assertEqual(
            list(validator.RISK_IDS),
            [record["risk_id"] for record in model["risk_evidence_reconciliation"]],
        )
        self.assertTrue(
            all(
                record["state"] == "open_blocked_unaccepted"
                and record["risk_accepted"] is False
                for record in model["risk_evidence_reconciliation"]
            )
        )
        self.assertEqual(
            {
                "case_id": "SYNTHETIC-CASE-001",
                "record_type": "synthetic_role_simulation_no_real_participant",
                "synthetic_actor_id": "SYNTHETIC-HUMAN-ROLE-CS-001",
                "actor_is_real_person": False,
                "case_disposition": "stopped_withdrawn_and_closed",
                "ticket_created": False,
                "external_message_sent": False,
                "human_closure_record_complete": True,
            },
            model["synthetic_support_case_closure"],
        )
        self.assertTrue(all(value is False for value in model["claims"].values()))
        self.assertEqual([], model["external_actions_performed"])

        before = copy.deepcopy(model)
        result = validator.evaluate_gate11_readiness(model)
        self.assertEqual(before, model)
        self.assertEqual(
            "ready_for_stone_human_evidence_decision_not_approved",
            result["result"],
        )
        self.assertIs(False, result["gate11_accepted"])
        self.assertEqual([], result["external_actions_performed"])

        attacks = []
        accepted = copy.deepcopy(before)
        accepted["gate11_decision_boundary"]["gate_accepted"] = True
        attacks.append(accepted)
        real_actor = copy.deepcopy(before)
        real_actor["synthetic_support_case_closure"]["actor_is_real_person"] = True
        attacks.append(real_actor)
        accepted_risk = copy.deepcopy(before)
        accepted_risk["risk_evidence_reconciliation"][0]["risk_accepted"] = True
        attacks.append(accepted_risk)
        external = copy.deepcopy(before)
        external["external_actions_performed"] = ["ticket_created"]
        attacks.append(external)

        for attack in attacks:
            denied = validator.evaluate_gate11_readiness(attack)
            self.assertEqual("denied", denied["result"])
            self.assertIs(False, denied["gate11_accepted"])
            self.assertEqual([], denied["external_actions_performed"])

    def test_gate11_validator_cli_reports_readiness_without_approval(self):
        completed = subprocess.run(
            [sys.executable, str(VALIDATOR)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertIn(
            "AIOS Stage 15 Gate 11 synthetic-evidence readiness validation PASSED",
            completed.stdout,
        )
        self.assertIn("gate11_accepted=false", completed.stdout)
        self.assertIn("external_actions_performed=[]", completed.stdout)


if __name__ == "__main__":
    unittest.main()
