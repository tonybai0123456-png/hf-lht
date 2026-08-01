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
    def test_gate9_approval_authorizes_treatment_only_without_accepting_risk(self):
        validator = load_validator()
        audit, risk_register, proposals, candidate = validator.load_repository_assets(
            ROOT
        )

        self.assertEqual(
            "accepted_treatment_direction_risks_remain_open_blocked_unaccepted",
            audit["status"],
        )
        self.assertEqual("HG-PILOT-SCOPE", audit["next_gate"])
        self.assertEqual(
            {
                "human_approver": "Tony",
                "overall_risk_owner": "Tony",
                "independent_reviewer_and_escalation_contact": "Stone",
                "gate_accepted": True,
                "approval_state": "accepted",
                "disposition": "mitigate_and_remain_open_blocked_unaccepted",
                "risk_acceptance": False,
                "risk_closure": False,
                "production_action_allowed": False,
                "decision_evidence": "Owner authorization / Issue #46",
            },
            audit["gate9_decision_boundary"],
        )
        self.assertEqual(10, len(audit["risk_treatment_readiness"]))
        self.assertTrue(
            all(
                record["disposition"]
                == "mitigate_and_remain_open_blocked_unaccepted"
                and record["treatment_authorized"] is True
                and record["risk_accepted"] is False
                and record["production_action_allowed"] is False
                for record in audit["risk_treatment_readiness"]
            )
        )

        gate9 = proposals["proposals"][2]
        self.assertIs(True, gate9["accepted"])
        self.assertEqual("accepted", gate9["state"])
        self.assertEqual("Tony", gate9["overall_risk_owner"])
        self.assertEqual(
            "Stone",
            gate9["independent_reviewer_and_escalation_contact"],
        )
        self.assertEqual("HG-PILOT-SCOPE", proposals["sequencing"]["next_gate"])

        self.assertEqual(
            {
                "stage10": "BLOCKED / NO-GO",
                "risk_count": 10,
                "risk_state": "open_blocked_unaccepted",
                "treatment_ownership": "authorized_for_treatment_evidence_only",
                "risk_acceptance": False,
            },
            candidate["risk_posture"],
        )
        self.assertIs(True, candidate["gate_ledger"][8]["accepted"])
        self.assertEqual("accepted", candidate["gate_ledger"][8]["state"])
        self.assertEqual(
            ["HG-PILOT-SCOPE", "HG-PILOT-EVIDENCE", "HG-RELEASE"],
            candidate["candidate_decision"]["remaining_human_gates"],
        )

        self.assertTrue(
            all(
                risk["owner_state"] == "unassigned / governance decision required"
                and risk["acceptance_status"] == "not_accepted"
                and risk["production_action_allowed"] is False
                for risk in risk_register["risks"]
            )
        )

        result = validator.evaluate_assets(audit, risk_register, proposals, candidate)
        self.assertEqual(
            "accepted_treatment_direction_risks_remain_open_blocked_unaccepted",
            result["result"],
        )
        self.assertEqual("HG-PILOT-SCOPE", result["next_gate"])
        self.assertIs(True, result["gate9_accepted"])
        self.assertIs(False, result["claims"]["risk_accepted"])
        self.assertIs(False, result["claims"]["risk_closed"])
        self.assertIs(False, result["claims"]["production_ready"])
        self.assertEqual([], result["external_actions_performed"])

    def test_assets_exist_and_repository_is_consistent(self):
        self.assertTrue(AUDIT.is_file())
        self.assertTrue(VALIDATOR.is_file())
        validator = load_validator()
        self.assertEqual([], validator.validate_repository(ROOT))

    def test_valid_state_records_treatment_approval_but_not_risk_acceptance(self):
        validator = load_validator()
        assets = validator.load_repository_assets(ROOT)
        before = copy.deepcopy(assets)

        result = validator.evaluate_assets(*assets)

        self.assertEqual(before, assets)
        self.assertEqual(
            "accepted_treatment_direction_risks_remain_open_blocked_unaccepted",
            result["result"],
        )
        self.assertEqual("HG-PILOT-SCOPE", result["next_gate"])
        self.assertIs(True, result["gate9_accepted"])
        self.assertEqual([], result["external_actions_performed"])
        self.assertIs(False, result["claims"]["risk_accepted"])
        self.assertIs(False, result["claims"]["risk_closed"])

    def test_authority_escalation_and_cross_asset_drift_fail_closed(self):
        validator = load_validator()
        audit, risk_register, proposals, candidate = validator.load_repository_assets(ROOT)

        changed_owner = copy.deepcopy(audit)
        changed_owner["risk_treatment_readiness"][0]["human_treatment_owner"] = "Developer Agent"

        revoked_gate9 = copy.deepcopy(proposals)
        revoked_gate9["proposals"][2]["accepted"] = False
        revoked_gate9["proposals"][2]["state"] = "proposed_awaiting_explicit_owner_approval"

        accepted_risk = copy.deepcopy(risk_register)
        accepted_risk["risks"][2]["acceptance_status"] = "accepted"

        production_action = copy.deepcopy(risk_register)
        production_action["risks"][5]["production_action_allowed"] = True

        accepted_risk_candidate = copy.deepcopy(candidate)
        accepted_risk_candidate["risk_posture"]["risk_acceptance"] = True

        cyclic = {}
        cyclic["self"] = cyclic

        attacks = (
            (changed_owner, risk_register, proposals, candidate),
            (audit, risk_register, revoked_gate9, candidate),
            (audit, accepted_risk, proposals, candidate),
            (audit, production_action, proposals, candidate),
            (audit, risk_register, proposals, accepted_risk_candidate),
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
            "result=accepted_treatment_direction_risks_remain_open_blocked_unaccepted",
            completed.stdout,
        )
        self.assertIn("next_gate=HG-PILOT-SCOPE", completed.stdout)
        self.assertIn("gate9_accepted=true", completed.stdout)
        self.assertIn("external_actions_performed=[]", completed.stdout)


if __name__ == "__main__":
    unittest.main()
