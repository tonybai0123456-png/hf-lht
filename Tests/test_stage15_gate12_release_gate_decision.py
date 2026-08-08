from __future__ import annotations

import copy
import importlib.util
from pathlib import Path
import subprocess
import sys
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[1]
DECISION = ROOT / "Governance/AIOS-Stage15-Gate12-Release-Gate-Decision-v1.yaml"
VALIDATOR = ROOT / "Tests/validate_aios_stage15_gate12_release_gate_decision.py"
STAGE_REGISTRY = ROOT / "Governance/AIOS-Stage-Registry.md"
PROJECT_REGISTRY = ROOT / "Governance/AIOS-Project-Registry.md"


def load_validator():
    spec = importlib.util.spec_from_file_location("gate12_decision_validator", VALIDATOR)
    if spec is None or spec.loader is None:
        raise RuntimeError("Gate 12 decision validator cannot be loaded")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Stage15Gate12ReleaseGateDecisionTests(unittest.TestCase):
    def test_gate12_is_accepted_only_as_governance_gate(self):
        self.assertTrue(DECISION.is_file(), DECISION)
        self.assertTrue(VALIDATOR.is_file(), VALIDATOR)
        validator = load_validator()
        model = yaml.safe_load(DECISION.read_text(encoding="utf-8"))

        self.assertEqual([], validator.validate_repository(ROOT))
        self.assertEqual(
            "accepted_governance_gate_only_release_actions_withheld",
            model["status"],
        )
        material = model["approved_decision_material"]
        self.assertEqual(
            "9bc17fa2ef722f29a8fcf302ef275ef6fbdf3a49",
            material["candidate_commit"],
        )
        self.assertEqual(
            "bf82c13df03e86985d6c9bc190eea9cd2fc87830",
            material["candidate_tree"],
        )
        self.assertEqual(
            "68b6301bcd08316aa191ac5e1e8f69bce44ab7aa",
            material["governance_record_commit"],
        )

        boundary = model["gate12_decision_boundary"]
        self.assertIs(True, boundary["gate_accepted"])
        self.assertIs(True, boundary["governance_gate_only"])
        for key, value in boundary.items():
            if key not in {"gate_accepted", "governance_gate_only", "approval_state"}:
                self.assertIs(False, value, key)

        self.assertEqual(10, len(model["risk_reconciliation"]))
        self.assertTrue(
            all(
                item["state"] == "open_blocked_unaccepted"
                and item["risk_accepted"] is False
                and item["risk_closed"] is False
                for item in model["risk_reconciliation"]
            )
        )
        self.assertEqual([], model["external_actions_performed"])

        before = copy.deepcopy(model)
        result = validator.evaluate_gate12_decision(model)
        self.assertEqual(before, model)
        self.assertEqual(
            "accepted_governance_gate_only_release_actions_withheld",
            result["result"],
        )
        self.assertIs(True, result["gate12_accepted"])
        self.assertIs(False, result["release_action_authorized"])
        self.assertIs(False, result["deployment_authorized"])
        self.assertEqual([], result["external_actions_performed"])

        attacks = []
        wrong_candidate = copy.deepcopy(before)
        wrong_candidate["approved_decision_material"]["candidate_commit"] = "0" * 40
        attacks.append(wrong_candidate)
        ready = copy.deepcopy(before)
        ready["gate12_decision_boundary"]["mark_ready_for_review_authorized"] = True
        attacks.append(ready)
        merged = copy.deepcopy(before)
        merged["repository_state"]["pull_request"]["merged"] = True
        attacks.append(merged)
        accepted_risk = copy.deepcopy(before)
        accepted_risk["risk_reconciliation"][0]["risk_accepted"] = True
        attacks.append(accepted_risk)
        external = copy.deepcopy(before)
        external["external_actions_performed"] = ["release"]
        attacks.append(external)

        for attack in attacks:
            denied = validator.evaluate_gate12_decision(attack)
            self.assertEqual("denied", denied["result"])
            self.assertIs(False, denied["gate12_accepted"])
            self.assertIs(False, denied["release_action_authorized"])
            self.assertIs(False, denied["deployment_authorized"])
            self.assertEqual([], denied["external_actions_performed"])

    def test_gate12_decision_is_the_latest_registry_overlay(self):
        for path in (STAGE_REGISTRY, PROJECT_REGISTRY):
            registry = path.read_text(encoding="utf-8")
            current = (
                registry.split("## Current Stage 15 decision overlay", 1)[1]
                .split("## Pre-freeze exception record", 1)[0]
                .split("## Registry rules", 1)[0]
            )
            for token in (
                "Gate 12 accepted",
                "AIOS-Stage15-Gate12-Release-Gate-Decision-v1.yaml",
                "accepted_governance_gate_only_release_actions_withheld",
                "9bc17fa2ef722f29a8fcf302ef275ef6fbdf3a49",
                "68b6301bcd08316aa191ac5e1e8f69bce44ab7aa",
                "PR #41 remains Draft/open/unmerged",
                "all ten risks remain open, blocked and unaccepted",
                "separate explicit authorization",
            ):
                self.assertIn(token, current)

    def test_gate12_decision_validator_cli_reports_no_action_authority(self):
        completed = subprocess.run(
            [sys.executable, str(VALIDATOR)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertIn("AIOS Stage 15 Gate 12 decision validation PASSED", completed.stdout)
        self.assertIn("gate12_accepted=true", completed.stdout)
        self.assertIn("release_action_authorized=false", completed.stdout)
        self.assertIn("deployment_authorized=false", completed.stdout)
        self.assertIn("external_actions_performed=[]", completed.stdout)


if __name__ == "__main__":
    unittest.main()
