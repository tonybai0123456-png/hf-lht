import copy
import importlib.util
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "Tests/validate_aios_stage15_gate9_risk_treatment_readiness.py"
AUDIT = ROOT / "Governance/AIOS-Stage15-Gate9-Risk-Treatment-Readiness-Audit-v1.yaml"


def load_validator():
    spec = importlib.util.spec_from_file_location("gate9_readiness_validator", VALIDATOR)
    if spec is None or spec.loader is None:
        raise RuntimeError("Gate 9 readiness validator cannot be loaded")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Stage15Gate9RiskTreatmentReadinessTests(unittest.TestCase):
    def test_assets_exist_and_repository_is_consistent(self):
        self.assertTrue(AUDIT.is_file())
        self.assertTrue(VALIDATOR.is_file())
        validator = load_validator()
        self.assertEqual([], validator.validate_repository(ROOT))

    def test_valid_state_is_decision_ready_but_not_approved(self):
        validator = load_validator()
        assets = validator.load_repository_assets(ROOT)
        before = copy.deepcopy(assets)

        result = validator.evaluate_assets(*assets)

        self.assertEqual(before, assets)
        self.assertEqual(
            "ready_for_explicit_owner_decision_not_approved",
            result["result"],
        )
        self.assertEqual("HG-RISK-DISPOSITION", result["next_gate"])
        self.assertIs(False, result["gate9_accepted"])
        self.assertEqual([], result["external_actions_performed"])
        self.assertTrue(all(value is False for value in result["claims"].values()))

    def test_authority_escalation_and_cross_asset_drift_fail_closed(self):
        validator = load_validator()
        audit, risk_register, proposals, candidate = validator.load_repository_assets(ROOT)

        changed_owner = copy.deepcopy(audit)
        changed_owner["risk_treatment_readiness"][0]["human_treatment_owner"] = "Developer Agent"

        accepted_gate9 = copy.deepcopy(proposals)
        accepted_gate9["proposals"][2]["accepted"] = True
        accepted_gate9["proposals"][2]["state"] = "accepted"

        accepted_risk = copy.deepcopy(risk_register)
        accepted_risk["risks"][2]["acceptance_status"] = "accepted"

        production_action = copy.deepcopy(risk_register)
        production_action["risks"][5]["production_action_allowed"] = True

        authorized_candidate = copy.deepcopy(candidate)
        authorized_candidate["risk_posture"]["treatment_ownership"] = "authorized"

        cyclic = {}
        cyclic["self"] = cyclic

        attacks = (
            (changed_owner, risk_register, proposals, candidate),
            (audit, risk_register, accepted_gate9, candidate),
            (audit, accepted_risk, proposals, candidate),
            (audit, production_action, proposals, candidate),
            (audit, risk_register, proposals, authorized_candidate),
            (cyclic, risk_register, proposals, candidate),
            (None, risk_register, proposals, candidate),
        )
        for assets in attacks:
            with self.subTest(first_asset_type=type(assets[0]).__name__):
                result = validator.evaluate_assets(*assets)
                self.assertEqual("denied", result["result"])
                self.assertIs(False, result["gate9_accepted"])
                self.assertEqual([], result["external_actions_performed"])
                self.assertTrue(
                    all(value is False for value in result["claims"].values())
                )

    def test_cli_reports_controlled_readiness(self):
        completed = subprocess.run(
            [sys.executable, str(VALIDATOR)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertIn(
            "AIOS Stage 15 Gate 9 risk-treatment readiness validation PASSED",
            completed.stdout,
        )
        self.assertIn(
            "result=ready_for_explicit_owner_decision_not_approved",
            completed.stdout,
        )
        self.assertIn("next_gate=HG-RISK-DISPOSITION", completed.stdout)
        self.assertIn("gate9_accepted=false", completed.stdout)
        self.assertIn("external_actions_performed=[]", completed.stdout)


if __name__ == "__main__":
    unittest.main()
