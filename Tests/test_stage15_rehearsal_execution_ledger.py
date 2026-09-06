from pathlib import Path
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "Governance" / "AIOS-Stage15-Local-Python-Rehearsal-Execution-Ledger-v1.yaml"

EXPECTED_RUNS = {
    "STAGE15-LOCAL-ad8373c2401e": {
        "source_commit": "ad8373c2401ee80daf2425a2faf84cdef1874610",
        "source_tree": "4bbf8fd1d4371dd4788b965315b27b6899165b4a",
    },
    "STAGE15-LOCAL-33e2216976b7": {
        "source_commit": "33e2216976b73ebaff4368ca8b8d5dc206ebf894",
        "source_tree": "eff75180da120fa7deffdd15b1daa2a13bcb8ab5",
    },
}


class Stage15RehearsalExecutionLedgerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ledger = yaml.safe_load(LEDGER.read_text(encoding="utf-8"))

    def test_ledger_is_fail_closed_until_explicit_owner_disposition(self):
        self.assertEqual("human_owner_disposition_required", self.ledger["status"])
        state = self.ledger["machine_derived_state"]
        self.assertFalse(state["cross_asset_count_reconciled"])
        self.assertTrue(state["issue52_evidence_acceptance_blocked"])
        self.assertTrue(state["issue53_ready_for_review_blocked"])
        self.assertEqual(
            "execution_count_authorization_reconciliation_required_before_evidence_acceptance",
            state["maximum_machine_conclusion"],
        )

    def test_all_distinct_recorded_executions_are_preserved(self):
        rows = self.ledger["recorded_executions"]
        self.assertEqual(2, len(rows))
        by_id = {row["run_id"]: row for row in rows}
        self.assertEqual(set(EXPECTED_RUNS), set(by_id))
        self.assertEqual(2, len(set(by_id)))
        for run_id, expected in EXPECTED_RUNS.items():
            row = by_id[run_id]
            self.assertTrue(row["execution_occurred"])
            self.assertEqual(expected["source_commit"], row["source_commit"])
            self.assertEqual(expected["source_tree"], row["source_tree"])
            self.assertEqual("pending_explicit_tony_disposition", row["authorization_treatment"])
            self.assertEqual("pending_explicit_tony_disposition", row["evidence_eligibility_for_issue52"])
            self.assertEqual("not_determined", row["invalidated_or_superseded"])

    def test_machine_derived_count_comes_from_recorded_execution_rows(self):
        rows = self.ledger["recorded_executions"]
        state = self.ledger["machine_derived_state"]
        self.assertEqual(len(rows), state["distinct_recorded_execution_count"])
        unresolved = [
            row["run_id"]
            for row in rows
            if row["authorization_treatment"] == "pending_explicit_tony_disposition"
        ]
        self.assertEqual(len(unresolved), state["unresolved_authorization_disposition_count"])
        self.assertEqual(unresolved, state["unresolved_execution_ids"])
        self.assertEqual(1, self.ledger["authorization_ceiling"]["authorized_execution_count"])
        self.assertEqual(1, state["authorized_execution_ceiling"])
        self.assertEqual(1, state["mandatory_return_declared_valid_run_count"])

    def test_invalidated_preacceptance_attempt_is_kept_separate(self):
        attempts = self.ledger["invalidated_preacceptance_attempts"]
        self.assertEqual(1, len(attempts))
        self.assertEqual("e87f7fdc7ae235d365afc8f44816c5854877f1b2", attempts[0]["commit"])
        self.assertEqual("stone_stopped_receipt_invalid_not_committed", attempts[0]["disposition"])

    def test_no_downstream_authority_is_granted(self):
        self.assertTrue(all(value is False for value in self.ledger["downstream_authority"].values()))
        self.assertEqual([], self.ledger["external_actions_performed"])

    def test_anti_rewrite_rules_are_explicit(self):
        rules = set(self.ledger["append_only_rules"])
        self.assertIn("preserve_every_distinct_recorded_run_id", rules)
        self.assertIn("never_relabel_a_recorded_execution_invalid_without_explicit_human_disposition", rules)
        self.assertIn("resolve_authorization_and_evidence_eligibility_only_from_explicit_owner_disposition", rules)
        self.assertIn("do_not_execute_another_rehearsal_to_repair_governance_evidence", rules)


if __name__ == "__main__":
    unittest.main()
