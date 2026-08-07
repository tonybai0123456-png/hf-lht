from pathlib import Path
import re
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[1]
GUARD = (
    ROOT
    / "Governance"
    / "AIOS-Nonproduction-Readiness-Rehearsal-Authorization-Guard-v1.yaml"
)

EXPECTED_ASSETS = [
    "Governance/AIOS-Stage15-Local-Python-Rehearsal-Contract-v1.yaml",
    "Governance/AIOS-Stage15-Local-Python-Rehearsal-Receipt-Schema-v1.yaml",
    "Runtime/stage15_local_python_rehearsal.py",
    "Tests/Fixtures/nonproduction-readiness/local-python-rehearsal-synthetic.yaml",
    "Tests/test_stage15_local_python_rehearsal.py",
    "Tests/validate_aios_stage15_local_python_rehearsal.py",
    "Tests/AIOS-Stage15-Local-Python-Rehearsal-Validation.md",
]

EXPECTED_TOP_LEVEL_KEYS = {
    "authorization_guard_version",
    "stage",
    "stage_id",
    "scope",
    "status",
    "owner_decision_entry_point",
    "frozen_decision_target",
    "implementation_authorized",
    "rehearsal_execution_authorized",
    "owner_decision_evidence",
    "required_implementation_assets",
    "unauthorized_state_rule",
    "future_authorization_rule",
    "downstream_authority",
    "stage10_state",
    "risk_state",
    "external_actions_performed",
    "notes",
}

EXPECTED_DOWNSTREAM_KEYS = {
    "pr_ready_for_review_authorized",
    "merge_authorized",
    "risk_acceptance_authorized",
    "real_pilot_authorized",
    "real_data_authorized",
    "credentials_or_permissions_authorized",
    "connectors_or_external_endpoints_authorized",
    "infrastructure_or_cloud_authorized",
    "production_authorized",
    "release_authorized",
    "deployment_authorized",
}


class Stage15RehearsalAuthorityGuardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.guard = yaml.safe_load(GUARD.read_text(encoding="utf-8"))

    def test_guard_contract_is_closed_and_pins_the_decision_target(self):
        self.assertIsInstance(self.guard, dict)
        self.assertEqual(EXPECTED_TOP_LEVEL_KEYS, set(self.guard))
        self.assertEqual(
            "aios_stage15_rehearsal_authorization_guard/v1",
            self.guard["authorization_guard_version"],
        )
        self.assertEqual("15", self.guard["stage"])
        self.assertEqual("NR-01", self.guard["stage_id"])
        self.assertEqual(
            "local_isolated_python_rehearsal_preimplementation_guard",
            self.guard["scope"],
        )

        entry = self.guard["owner_decision_entry_point"]
        self.assertEqual(
            {
                "issue_number": 51,
                "issue_url": "https://github.com/tonybai0123456-png/hf-lht/issues/51",
                "human_owner": "Tony",
            },
            entry,
        )

        target = self.guard["frozen_decision_target"]
        self.assertEqual(
            {
                "implementation_plan_commit": "2d3d186d1930d18bfd0a8d604240694f11e1af6c",
                "implementation_plan_tree": "6b26f4f67907dcba68698949c6c303a4b8d9e5f0",
                "controlled_branch": "gov/aios-stage15-nonproduction-readiness-design",
            },
            target,
        )

    def test_required_asset_inventory_is_exact_and_unique(self):
        assets = self.guard["required_implementation_assets"]
        self.assertEqual(EXPECTED_ASSETS, assets)
        self.assertEqual(len(assets), len(set(assets)))
        for path in assets:
            self.assertFalse(Path(path).is_absolute())
            self.assertNotIn("..", Path(path).parts)

    def test_no_rehearsal_implementation_asset_exists_before_implementation_authorization(self):
        if self.guard["implementation_authorized"]:
            self.skipTest("Implementation is explicitly authorized; absence guard no longer applies")
        for relative_path in EXPECTED_ASSETS:
            self.assertFalse(
                (ROOT / relative_path).exists(),
                f"unauthorized rehearsal implementation asset exists: {relative_path}",
            )

    def test_authorization_cannot_be_inferred_or_partially_escalated(self):
        implementation_authorized = self.guard["implementation_authorized"]
        execution_authorized = self.guard["rehearsal_execution_authorized"]
        evidence = self.guard["owner_decision_evidence"]

        self.assertIs(type(implementation_authorized), bool)
        self.assertIs(type(execution_authorized), bool)
        self.assertEqual(
            {"decision", "actor", "issue_comment_url", "recorded_at_utc"},
            set(evidence),
        )

        if not implementation_authorized:
            self.assertEqual("awaiting_explicit_owner_decision", self.guard["status"])
            self.assertFalse(execution_authorized)
            self.assertEqual(
                {
                    "decision": None,
                    "actor": None,
                    "issue_comment_url": None,
                    "recorded_at_utc": None,
                },
                evidence,
            )
            return

        self.assertIn(
            evidence["decision"],
            {"approve_implementation_only", "approve_implementation_and_execution"},
        )
        self.assertEqual("Tony", evidence["actor"])
        self.assertRegex(
            evidence["issue_comment_url"],
            r"^https://github\.com/tonybai0123456-png/hf-lht/issues/51#issuecomment-\d+$",
        )
        self.assertRegex(
            evidence["recorded_at_utc"],
            r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$",
        )
        if execution_authorized:
            self.assertEqual("approve_implementation_and_execution", evidence["decision"])

    def test_downstream_authority_remains_fully_withheld(self):
        downstream = self.guard["downstream_authority"]
        self.assertEqual(EXPECTED_DOWNSTREAM_KEYS, set(downstream))
        self.assertTrue(all(value is False for value in downstream.values()))
        self.assertEqual("BLOCKED / NO-GO", self.guard["stage10_state"])
        self.assertEqual("open_blocked_unaccepted", self.guard["risk_state"])
        self.assertEqual([], self.guard["external_actions_performed"])

    def test_guard_text_denies_general_continue_as_authorization(self):
        text = GUARD.read_text(encoding="utf-8")
        for required in (
            "not itself an authorization source",
            "general instruction to continue construction",
            "must not be interpreted as implementation or rehearsal-execution authorization",
            "explicit Tony decision recorded in Issue #51",
        ):
            self.assertIn(required, text)
        for unresolved in ("TODO", "TBD", "PLACEHOLDER"):
            self.assertNotIn(unresolved, text)


if __name__ == "__main__":
    unittest.main()
