from __future__ import annotations

import copy
import importlib.util
from pathlib import Path
import subprocess
import sys
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[1]
DECISION = (
    ROOT
    / "Governance/AIOS-Stage15-Gate11-Synthetic-Rehearsal-Evidence-Decision-v1.yaml"
)
VALIDATOR = ROOT / "Tests/validate_aios_stage15_gate11_synthetic_evidence_decision.py"
STAGE_REGISTRY = ROOT / "Governance/AIOS-Stage-Registry.md"
PROJECT_REGISTRY = ROOT / "Governance/AIOS-Project-Registry.md"


def load_validator():
    spec = importlib.util.spec_from_file_location("gate11_decision_validator", VALIDATOR)
    if spec is None or spec.loader is None:
        raise RuntimeError("Gate 11 decision validator cannot be loaded")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Stage15Gate11SyntheticEvidenceDecisionTests(unittest.TestCase):
    def test_exact_gate11_decision_is_accepted_without_release_authority(self):
        self.assertTrue(DECISION.is_file(), DECISION)
        self.assertTrue(VALIDATOR.is_file(), VALIDATOR)
        validator = load_validator()
        model = yaml.safe_load(DECISION.read_text(encoding="utf-8"))

        self.assertEqual([], validator.validate_repository(ROOT))
        self.assertEqual(
            "accepted_synthetic_rehearsal_evidence_only_no_release_authority",
            model["status"],
        )
        self.assertEqual("HG-RELEASE", model["next_gate"])
        self.assertEqual(
            "247ffe84f49517fbf74b4e2878f30ad594540cb0",
            model["approved_evidence_package"]["commit"],
        )
        self.assertEqual(
            "19ef0e6d7d51e020c264f70e3c261373cbe115e5",
            model["approved_evidence_package"]["tree"],
        )
        boundary = model["gate11_decision_boundary"]
        self.assertEqual("Stone", boundary["human_approver"])
        self.assertEqual("Tony", boundary["backup_and_escalation_contact"])
        self.assertEqual("Data Agent", boundary["technical_owner"])
        self.assertEqual(
            ["Developer Agent", "CustomerService Agent"],
            boundary["contributors"],
        )
        self.assertIs(True, boundary["gate_accepted"])
        self.assertIs(False, boundary["release_authorized"])
        self.assertIs(False, boundary["external_actions_allowed"])
        self.assertTrue(
            all(
                risk["state"] == "open_blocked_unaccepted"
                and risk["risk_accepted"] is False
                for risk in model["risk_evidence_reconciliation"]
            )
        )
        self.assertIs(True, model["claims"]["gate11_accepted"])
        self.assertTrue(
            all(
                value is False
                for key, value in model["claims"].items()
                if key != "gate11_accepted"
            )
        )
        self.assertEqual([], model["external_actions_performed"])

        before = copy.deepcopy(model)
        result = validator.evaluate_gate11_decision(model)
        self.assertEqual(before, model)
        self.assertEqual(
            "accepted_synthetic_rehearsal_evidence_only_no_release_authority",
            result["result"],
        )
        self.assertEqual("HG-RELEASE", result["next_gate"])
        self.assertIs(True, result["gate11_accepted"])
        self.assertIs(False, result["release_authorized"])
        self.assertEqual([], result["external_actions_performed"])

        attacks = []
        wrong_commit = copy.deepcopy(before)
        wrong_commit["approved_evidence_package"]["commit"] = "0" * 40
        attacks.append(wrong_commit)
        real_actor = copy.deepcopy(before)
        real_actor["synthetic_support_case_closure"]["actor_is_real_person"] = True
        attacks.append(real_actor)
        accepted_risk = copy.deepcopy(before)
        accepted_risk["risk_evidence_reconciliation"][0]["risk_accepted"] = True
        attacks.append(accepted_risk)
        release = copy.deepcopy(before)
        release["gate11_decision_boundary"]["release_authorized"] = True
        attacks.append(release)
        external = copy.deepcopy(before)
        external["external_actions_performed"] = ["ticket_created"]
        attacks.append(external)

        for attack in attacks:
            denied = validator.evaluate_gate11_decision(attack)
            self.assertEqual("denied", denied["result"])
            self.assertIs(False, denied["gate11_accepted"])
            self.assertIs(False, denied["release_authorized"])
            self.assertEqual([], denied["external_actions_performed"])

    def test_gate11_decision_is_registered_as_latest_overlay(self):
        for path in (STAGE_REGISTRY, PROJECT_REGISTRY):
            registry = path.read_text(encoding="utf-8")
            for token in (
                "Gate 11 accepted",
                "AIOS-Stage15-Gate11-Synthetic-Rehearsal-Evidence-Decision-v1.yaml",
                "247ffe84f49517fbf74b4e2878f30ad594540cb0",
                "gates7_through_11_accepted_release_gate_withheld",
                "Gate 12 is the only valid next governance decision",
                "Stone is the human evidence approver",
                "Tony is backup and escalation contact",
                "Data Agent is technical evidence verification owner",
                "all ten risks remain open, blocked and unaccepted",
                "Gate 12 remains expressly withheld",
            ):
                self.assertIn(token, registry)

    def test_gate11_decision_validator_cli_reports_acceptance_without_release(self):
        completed = subprocess.run(
            [sys.executable, str(VALIDATOR)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertIn(
            "AIOS Stage 15 Gate 11 synthetic-evidence decision validation PASSED",
            completed.stdout,
        )
        self.assertIn("gate11_accepted=true", completed.stdout)
        self.assertIn("next_gate=HG-RELEASE", completed.stdout)
        self.assertIn("release_authorized=false", completed.stdout)
        self.assertIn("external_actions_performed=[]", completed.stdout)


if __name__ == "__main__":
    unittest.main()
