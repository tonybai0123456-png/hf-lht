from pathlib import Path
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "Governance" / "AIOS-Stage15-Rehearsal-Execution-Disposition-Contract-v1.yaml"
LEDGER = ROOT / "Governance" / "AIOS-Stage15-Local-Python-Rehearsal-Execution-Ledger-v1.yaml"

EXPECTED_RUN_IDS = [
    "STAGE15-LOCAL-ad8373c2401e",
    "STAGE15-LOCAL-33e2216976b7",
]


class Stage15RehearsalExecutionDispositionContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = yaml.safe_load(CONTRACT.read_text(encoding="utf-8"))
        cls.ledger = yaml.safe_load(LEDGER.read_text(encoding="utf-8"))

    def test_contract_is_preparation_only_and_has_no_human_decision(self):
        self.assertEqual("awaiting_explicit_tony_disposition", self.contract["status"])
        decision = self.contract["current_decision_record"]
        self.assertFalse(decision["recorded"])
        self.assertIsNone(decision["record_url"])
        self.assertIsNone(decision["actor"])
        self.assertEqual([], decision["per_execution_disposition"])

    def test_contract_covers_exact_append_only_execution_set(self):
        self.assertEqual(EXPECTED_RUN_IDS, self.contract["required_execution_ids"])
        ledger_ids = [row["run_id"] for row in self.ledger["recorded_executions"]]
        self.assertEqual(EXPECTED_RUN_IDS, ledger_ids)
        self.assertEqual(2, len(set(ledger_ids)))

    def test_original_authorization_boundary_remains_one_run(self):
        boundary = self.contract["original_authorization_boundary"]
        self.assertEqual("Tony", boundary["owner"])
        self.assertEqual(1, boundary["authorized_execution_count"])
        self.assertEqual(51, boundary["source_issue"])
        self.assertEqual(5211821955, boundary["source_comment_id"])
        self.assertEqual("one_bounded_local_isolated_python_rehearsal_only", boundary["rule"])

    def test_generic_continue_and_machine_evidence_cannot_resolve_issue55(self):
        invalid = set(self.contract["anti_replay_invalid_substitutes"])
        self.assertIn("recurring_or_general_continue_instruction", invalid)
        self.assertIn("machine_authored_packet_or_recommendation", invalid)
        self.assertIn("green_tests_validators_or_actions", invalid)
        self.assertIn("silence_or_failure_to_object", invalid)
        requirements = self.contract["human_decision_requirements"]
        self.assertEqual("Tony", requirements["actor_must_be"])
        self.assertEqual(55, requirements["issue_must_be"])
        self.assertTrue(requirements["decision_must_cover_every_required_execution_id"])

    def test_ratification_option_cannot_expand_lifecycle_authority(self):
        constraints = self.contract["ratification_constraints"][
            "separately_ratified_bounded_governance_exception"
        ]
        self.assertTrue(constraints["historical_execution_record_must_be_preserved"])
        self.assertTrue(constraints["does_not_rewrite_original_one_run_authorization"])
        self.assertTrue(constraints["does_not_authorize_another_rehearsal"])
        self.assertTrue(constraints["does_not_authorize_ready_for_review"])
        self.assertTrue(constraints["does_not_authorize_merge"])
        self.assertTrue(constraints["does_not_authorize_risk_acceptance"])
        self.assertTrue(constraints["does_not_authorize_real_pilot_or_real_data"])
        self.assertTrue(constraints["does_not_authorize_permissions_connectors_infrastructure"])
        self.assertTrue(constraints["does_not_authorize_production_release_or_deployment"])

    def test_all_downstream_authority_remains_false(self):
        self.assertTrue(all(value is False for value in self.contract["downstream_authority"].values()))
        self.assertEqual([], self.contract["external_actions_performed"])


if __name__ == "__main__":
    unittest.main()
