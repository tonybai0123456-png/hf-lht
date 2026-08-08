from __future__ import annotations

import copy
import tempfile
import unittest
from pathlib import Path

from Tests.validate_aios_stage15_post_gate12_reconciliation import (
    _load_controlled_yaml,
    evaluate_reconciliation,
    load_reconciliation,
    validate_reconciliation,
    validate_repository,
)


class Stage15PostGate12ReconciliationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.model = load_reconciliation()

    def test_repository_reconciliation_is_valid(self) -> None:
        self.assertEqual(validate_repository(), [])
        result = evaluate_reconciliation(self.model)
        self.assertEqual(result["result"], "lifecycle_handoff_ready_actions_withheld")
        self.assertEqual(result["external_actions_performed"], [])
        self.assertTrue(all(value is False for value in result["claims"].values()))

    def test_downstream_authority_expansion_is_denied(self) -> None:
        mutated = copy.deepcopy(self.model)
        mutated["controlled_state"]["downstream_authorities"]["merge"] = True
        result = evaluate_reconciliation(mutated)
        self.assertEqual(result["result"], "denied")
        self.assertTrue(
            any("all_false_required" in code for code in result["reason_codes"])
        )

    def test_risk_acceptance_or_reordering_is_denied(self) -> None:
        mutated = copy.deepcopy(self.model)
        mutated["controlled_state"]["risks"][0]["state"] = "accepted"
        mutated["lifecycle_handoff_queue"].reverse()
        errors = validate_reconciliation(mutated)
        self.assertTrue(any("exact_open_risks_required" in error for error in errors))
        self.assertTrue(any("exact_ordered_queue_required" in error for error in errors))

    def test_source_record_drift_is_denied(self) -> None:
        mutated = copy.deepcopy(self.model)
        mutated["source_records"]["historical_predeployment_audit"][
            "recorded_status"
        ] = "gate12_already_accepted"
        result = evaluate_reconciliation(mutated)
        self.assertEqual(result["result"], "denied")

    def test_malformed_and_cyclic_inputs_fail_closed(self) -> None:
        malformed_values = [None, [], "invalid", 42, {"record_version": []}]
        for value in malformed_values:
            with self.subTest(value=value):
                result = evaluate_reconciliation(value)
                self.assertEqual(result["result"], "denied")

        cyclic = copy.deepcopy(self.model)
        cyclic["controlled_state"]["downstream_authorities"]["cycle"] = cyclic
        result = evaluate_reconciliation(cyclic)
        self.assertEqual(result["result"], "denied")
        self.assertEqual(result["external_actions_performed"], [])

    def test_yaml_anchors_aliases_and_merge_keys_are_rejected(self) -> None:
        documents = (
            "root: &anchor\n  value: 1\ncopy: *anchor\n",
            "base: &base\n  value: 1\nmerged:\n  <<: *base\n",
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "controlled.yaml"
            for document in documents:
                with self.subTest(document=document):
                    path.write_text(document, encoding="utf-8")
                    with self.assertRaises(ValueError):
                        _load_controlled_yaml(path)


if __name__ == "__main__":
    unittest.main()
