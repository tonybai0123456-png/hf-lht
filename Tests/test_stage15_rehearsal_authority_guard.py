from pathlib import Path
import re
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[1]
GUARD = ROOT / "Governance" / "AIOS-Nonproduction-Readiness-Rehearsal-Authorization-Guard-v1.yaml"

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
    "authorization_guard_version", "stage", "stage_id", "scope", "status",
    "owner_decision_entry_point", "frozen_decision_target",
    "implementation_authorized", "rehearsal_execution_authorized",
    "owner_decision_evidence", "required_implementation_assets",
    "unauthorized_state_rule", "future_authorization_rule", "downstream_authority",
    "stage10_state", "risk_state", "external_actions_performed", "notes",
}

EXPECTED_DOWNSTREAM_KEYS = {
    "pr_ready_for_review_authorized", "merge_authorized", "risk_acceptance_authorized",
    "real_pilot_authorized", "real_data_authorized", "credentials_or_permissions_authorized",
    "connectors_or_external_endpoints_authorized", "infrastructure_or_cloud_authorized",
    "production_authorized", "release_authorized", "deployment_authorized",
}


class Stage15RehearsalAuthorityGuardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.guard = yaml.safe_load(GUARD.read_text(encoding="utf-8"))

    def test_guard_contract_is_closed_and_pins_the_decision_target(self):
        self.assertEqual(EXPECTED_TOP_LEVEL_KEYS, set(self.guard))
        self.assertEqual("aios_stage15_rehearsal_authorization_guard/v1", self.guard["authorization_guard_version"])
        self.assertEqual("15", self.guard["stage"])
        self.assertEqual("NR-01", self.guard["stage_id"])
        self.assertEqual("local_isolated_python_rehearsal_preimplementation_guard", self.guard["scope"])
        self.assertEqual({"issue_number": 51, "issue_url": "https://github.com/tonybai0123456-png/hf-lht/issues/51", "human_owner": "Tony"}, self.guard["owner_decision_entry_point"])
        self.assertEqual({"implementation_plan_commit": "2d3d186d1930d18bfd0a8d604240694f11e1af6c", "implementation_plan_tree": "6b26f4f67907dcba68698949c6c303a4b8d9e5f0", "controlled_branch": "gov/aios-stage15-nonproduction-readiness-design"}, self.guard["frozen_decision_target"])

    def test_required_asset_inventory_is_exact_and_unique(self):
        self.assertEqual(EXPECTED_ASSETS, self.guard["required_implementation_assets"])
        self.assertEqual(len(EXPECTED_ASSETS), len(set(EXPECTED_ASSETS)))
        for path in EXPECTED_ASSETS:
            self.assertFalse(Path(path).is_absolute())
            self.assertNotIn("..", Path(path).parts)

    def test_authorization_evidence_matches_owner_decision(self):
        self.assertTrue(self.guard["implementation_authorized"])
        self.assertTrue(self.guard["rehearsal_execution_authorized"])
        self.assertEqual("approve_implementation_and_execution", self.guard["owner_decision_evidence"]["decision"])
        self.assertEqual("Tony", self.guard["owner_decision_evidence"]["actor"])
        self.assertRegex(self.guard["owner_decision_evidence"]["issue_comment_url"], r"^https://github\.com/tonybai0123456-png/hf-lht/issues/51#issuecomment-\d+$")
        self.assertRegex(self.guard["owner_decision_evidence"]["recorded_at_utc"], r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")

    def test_downstream_authority_remains_fully_withheld(self):
        self.assertEqual(EXPECTED_DOWNSTREAM_KEYS, set(self.guard["downstream_authority"]))
        self.assertTrue(all(value is False for value in self.guard["downstream_authority"].values()))
        self.assertEqual("BLOCKED / NO-GO", self.guard["stage10_state"])
        self.assertEqual("open_blocked_unaccepted", self.guard["risk_state"])
        self.assertEqual([], self.guard["external_actions_performed"])

    def test_guard_text_preserves_bounded_scope(self):
        text = GUARD.read_text(encoding="utf-8")
        for required in ("not itself an authorization source", "explicit Tony decision in Issue #51", "one bounded local rehearsal", "No network"):
            self.assertIn(required, text)
        for unresolved in ("TODO", "TBD", "PLACEHOLDER"):
            self.assertNotIn(unresolved, text)


if __name__ == "__main__":
    unittest.main()
