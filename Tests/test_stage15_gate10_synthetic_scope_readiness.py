import copy
import importlib.util
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "Tests/validate_aios_stage15_gate10_synthetic_scope_readiness.py"
AUDIT = ROOT / (
    "Governance/AIOS-Stage15-Gate10-Synthetic-Rehearsal-Scope-Readiness-Audit-v1.yaml"
)


def load_validator():
    spec = importlib.util.spec_from_file_location(
        "gate10_scope_readiness_validator", VALIDATOR
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("Gate 10 synthetic-scope readiness validator cannot be loaded")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Stage15Gate10SyntheticScopeReadinessTests(unittest.TestCase):
    def test_gate10_approval_authorizes_zero_participant_rehearsal_scope_only(self):
        validator = load_validator()
        audit, gate9, proposals, candidate, fixture = (
            validator.load_repository_assets(ROOT)
        )

        self.assertEqual(
            "accepted_zero_participant_synthetic_rehearsal_scope_no_real_pilot",
            audit["status"],
        )
        self.assertEqual("HG-PILOT-EVIDENCE", audit["next_gate"])
        self.assertEqual(
            {
                "real_customers": 0,
                "employees_or_real_operators": 0,
                "stores": 0,
                "production_or_staging_environments": 0,
                "real_cases_orders_accounts_or_messages": 0,
            },
            audit["zero_participant_boundary"],
        )
        self.assertIs(True, audit["gate10_decision_boundary"]["gate_accepted"])
        self.assertEqual(
            "accepted",
            audit["gate10_decision_boundary"]["approval_state"],
        )
        self.assertEqual(
            "Owner authorization / Issue #47",
            audit["gate10_decision_boundary"]["decision_evidence"],
        )
        self.assertIs(
            False,
            audit["gate10_decision_boundary"]["real_pilot_authorized"],
        )
        self.assertIs(
            False,
            audit["gate10_decision_boundary"]["external_actions_allowed"],
        )

        gate10 = proposals["proposals"][3]
        self.assertIs(True, gate10["accepted"])
        self.assertEqual("accepted", gate10["state"])
        self.assertEqual(
            "Owner authorization / Issue #47",
            gate10["decision_evidence"],
        )
        self.assertIs(True, candidate["gate_ledger"][9]["accepted"])
        self.assertEqual("accepted", candidate["gate_ledger"][9]["state"])
        self.assertEqual(
            ["HG-RELEASE"],
            candidate["candidate_decision"]["remaining_human_gates"],
        )
        self.assertEqual(
            ["HG-RELEASE"],
            fixture["required_human_gates"],
        )

        result = validator.evaluate_assets(
            audit, gate9, proposals, candidate, fixture
        )
        self.assertEqual(
            "accepted_zero_participant_synthetic_rehearsal_scope_no_real_pilot",
            result["result"],
        )
        self.assertEqual("HG-PILOT-EVIDENCE", result["next_gate"])
        self.assertIs(True, result["gate10_accepted"])
        self.assertIs(False, result["claims"]["real_pilot_performed"])
        self.assertIs(False, result["claims"]["pilot_authorized"])
        self.assertIs(False, result["claims"]["risk_accepted"])
        self.assertIs(False, result["claims"]["production_ready"])
        self.assertIs(False, result["claims"]["release_authorized"])
        self.assertIs(False, result["claims"]["deployment_authorized"])
        self.assertEqual([], result["external_actions_performed"])

    def test_gate10_scope_is_accepted_but_never_authorizes_real_pilot(self):
        validator = load_validator()
        audit, gate9, proposals, candidate, fixture = validator.load_repository_assets(
            ROOT
        )

        self.assertEqual(
            "accepted_zero_participant_synthetic_rehearsal_scope_no_real_pilot",
            audit["status"],
        )
        self.assertEqual("HG-PILOT-EVIDENCE", audit["next_gate"])
        self.assertEqual(
            {
                "real_customers": 0,
                "employees_or_real_operators": 0,
                "stores": 0,
                "production_or_staging_environments": 0,
                "real_cases_orders_accounts_or_messages": 0,
            },
            audit["zero_participant_boundary"],
        )
        self.assertIs(True, audit["gate10_decision_boundary"]["gate_accepted"])
        self.assertIs(False, audit["gate10_decision_boundary"]["real_pilot_authorized"])
        self.assertIs(False, audit["gate10_decision_boundary"]["external_actions_allowed"])

        self.assertIs(True, gate9["gate9_decision_boundary"]["gate_accepted"])
        self.assertTrue(
            all(
                item["treatment_authorized"] is True
                and item["risk_accepted"] is False
                and item["production_action_allowed"] is False
                for item in gate9["risk_treatment_readiness"]
            )
        )

        gate10 = proposals["proposals"][3]
        self.assertEqual("HG-PILOT-SCOPE", gate10["gate_id"])
        self.assertIs(True, gate10["accepted"])
        self.assertEqual("accepted", gate10["state"])
        self.assertEqual("Tony", gate10["human_approver"])
        self.assertEqual("Stone", gate10["backup_and_escalation_contact"])
        self.assertEqual("Developer Agent", gate10["technical_owner"])

        self.assertTrue(
            all(candidate["gate_ledger"][index]["accepted"] is True for index in range(9))
        )
        self.assertIs(True, candidate["gate_ledger"][9]["accepted"])
        self.assertEqual("accepted", candidate["gate_ledger"][9]["state"])
        self.assertEqual("BLOCKED / NO-GO", candidate["risk_posture"]["stage10"])
        self.assertIs(False, candidate["risk_posture"]["risk_acceptance"])

        self.assertEqual("local_synthetic_disposable", fixture["environment"]["mode"])
        self.assertEqual([], fixture["environment"]["external_endpoints"])
        self.assertEqual([], fixture["environment"]["connectors"])
        self.assertEqual([], fixture["environment"]["credentials"])
        self.assertEqual([], fixture["requested_external_actions"])

        result = validator.evaluate_assets(
            audit, gate9, proposals, candidate, fixture
        )
        self.assertEqual(
            "accepted_zero_participant_synthetic_rehearsal_scope_no_real_pilot",
            result["result"],
        )
        self.assertEqual("HG-PILOT-EVIDENCE", result["next_gate"])
        self.assertIs(True, result["gate10_accepted"])
        self.assertIs(False, result["claims"]["pilot_authorized"])
        self.assertEqual([], result["external_actions_performed"])

    def test_assets_exist_and_repository_is_consistent(self):
        self.assertTrue(AUDIT.is_file())
        self.assertTrue(VALIDATOR.is_file())
        validator = load_validator()
        self.assertEqual([], validator.validate_repository(ROOT))

    def test_evaluation_is_deterministic_and_does_not_mutate_inputs(self):
        validator = load_validator()
        assets = validator.load_repository_assets(ROOT)
        before = copy.deepcopy(assets)

        first = validator.evaluate_assets(*assets)
        second = validator.evaluate_assets(*assets)

        self.assertEqual(before, assets)
        self.assertEqual(first, second)
        self.assertEqual(
            "accepted_zero_participant_synthetic_rehearsal_scope_no_real_pilot",
            first["result"],
        )
        self.assertIs(True, first["gate10_accepted"])
        self.assertEqual([], first["external_actions_performed"])

    def test_boundary_drift_and_premature_authority_fail_closed(self):
        validator = load_validator()
        audit, gate9, proposals, candidate, fixture = validator.load_repository_assets(
            ROOT
        )

        nonzero_participant = copy.deepcopy(audit)
        nonzero_participant["zero_participant_boundary"]["real_customers"] = 1

        revoked_proposal_approval = copy.deepcopy(proposals)
        revoked_proposal_approval["proposals"][3]["accepted"] = False
        revoked_proposal_approval["proposals"][3]["state"] = (
            "proposed_awaiting_explicit_owner_approval"
        )

        revoked_candidate_approval = copy.deepcopy(candidate)
        revoked_candidate_approval["gate_ledger"][9]["accepted"] = False
        revoked_candidate_approval["gate_ledger"][9]["state"] = (
            "proposed_awaiting_explicit_owner_approval"
        )

        revoked_gate9 = copy.deepcopy(gate9)
        revoked_gate9["gate9_decision_boundary"]["gate_accepted"] = False

        external_endpoint = copy.deepcopy(fixture)
        external_endpoint["environment"]["external_endpoints"] = [
            "https://example.invalid"
        ]

        connector = copy.deepcopy(fixture)
        connector["environment"]["connectors"] = ["synthetic-but-not-allowed"]

        real_data = copy.deepcopy(fixture)
        real_data["data_contract"]["provenance"] = "production"
        real_data["data_contract"]["classification"] = "customer_personal"

        external_action = copy.deepcopy(fixture)
        external_action["requested_external_actions"] = ["send_message"]

        real_ticket = copy.deepcopy(fixture)
        real_ticket["support_handoff"]["ticket_created"] = True

        cyclic = {}
        cyclic["self"] = cyclic

        attacks = (
            (nonzero_participant, gate9, proposals, candidate, fixture),
            (audit, gate9, revoked_proposal_approval, candidate, fixture),
            (audit, gate9, proposals, revoked_candidate_approval, fixture),
            (audit, revoked_gate9, proposals, candidate, fixture),
            (audit, gate9, proposals, candidate, external_endpoint),
            (audit, gate9, proposals, candidate, connector),
            (audit, gate9, proposals, candidate, real_data),
            (audit, gate9, proposals, candidate, external_action),
            (audit, gate9, proposals, candidate, real_ticket),
            (cyclic, gate9, proposals, candidate, fixture),
            (None, gate9, proposals, candidate, fixture),
        )
        for assets in attacks:
            with self.subTest(first_asset_type=type(assets[0]).__name__):
                result = validator.evaluate_assets(*assets)
                self.assertEqual("denied", result["result"])
                self.assertIs(False, result["gate10_accepted"])
                self.assertEqual([], result["external_actions_performed"])
                self.assertTrue(
                    all(value is False for value in result["claims"].values())
                )

    def test_cli_reports_accepted_zero_participant_scope(self):
        completed = subprocess.run(
            [sys.executable, str(VALIDATOR)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertIn(
            "AIOS Stage 15 Gate 10 synthetic-scope readiness validation PASSED",
            completed.stdout,
        )
        self.assertIn(
            "result=accepted_zero_participant_synthetic_rehearsal_scope_no_real_pilot",
            completed.stdout,
        )
        self.assertIn("next_gate=HG-PILOT-EVIDENCE", completed.stdout)
        self.assertIn("gate10_accepted=true", completed.stdout)
        self.assertIn("pilot_authorized=false", completed.stdout)
        self.assertIn("external_actions_performed=[]", completed.stdout)


if __name__ == "__main__":
    unittest.main()
