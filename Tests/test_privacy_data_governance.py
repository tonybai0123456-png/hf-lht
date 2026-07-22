from copy import deepcopy
from pathlib import Path
import unittest

import yaml

from Tests.validate_aios_privacy_data_governance import (
    evaluate_request,
    validate_model,
    validate_repository,
)


ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / "Governance" / "AIOS-Privacy-Data-Governance-Model-v1.yaml"
MAPPING_PATH = ROOT / "Governance" / "AIOS-Privacy-Data-Governance-Stage10-Mapping-v1.yaml"
ACCEPTANCE_PATH = ROOT / "Governance" / "AIOS-Privacy-Data-Governance-Acceptance-Matrix-v1.yaml"
WORKFLOW_PATH = ROOT / ".github" / "workflows" / "validate-aios-privacy-data-governance.yml"
UNASSIGNED = "unassigned / governance decision required"

VALID_REQUEST = {
    "request_id": "SYN-DG-001",
    "synthetic": True,
    "company": "汇沣电商",
    "brand": "BUW",
    "asset_id": "synthetic_customer_contact",
    "subject_type": "synthetic_customer",
    "categories": ["contact"],
    "fields": ["synthetic_email"],
    "purpose_id": "service_response",
    "basis_decision_id": "BASIS-SYN-001",
    "actor_role": "Data Steward",
    "action": "read",
    "retention_rule_id": "RET-SYN-030D",
    "lineage": {
        "source": "synthetic_fixture",
        "destination": "in_memory_validation",
    },
}


class PrivacyDataGovernanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model = yaml.safe_load(MODEL_PATH.read_text(encoding="utf-8"))

    def test_repository_package_is_complete(self):
        self.assertEqual([], validate_repository(ROOT))

    def test_model_is_valid_and_synthetic_request_is_allowed(self):
        self.assertEqual([], validate_model(self.model))
        self.assertEqual([], evaluate_request(self.model, VALID_REQUEST))

    def test_fail_closed_request_mutations(self):
        cases = [
            ({"synthetic": False}, "real_or_unmarked_data"),
            ({"brand": "PC"}, "cross_boundary"),
            ({"purpose_id": "unknown"}, "unknown_purpose"),
            ({"basis_decision_id": ""}, "missing_basis_decision"),
            (
                {"fields": ["synthetic_email", "synthetic_free_text"]},
                "excessive_fields",
            ),
            ({"actor_role": "Runtime Service Identity"}, "unauthorized_access"),
            ({"retention_rule_id": "RET-FOREVER"}, "invalid_retention"),
            ({"lineage": {}}, "missing_lineage"),
            ({"automatic_real_deletion": True}, "automatic_real_deletion"),
            ({"production_authorized": True}, "production_or_legal_claim"),
            ({"legal_approval_granted": True}, "production_or_legal_claim"),
        ]
        for mutation, reason in cases:
            with self.subTest(mutation=mutation):
                request = deepcopy(VALID_REQUEST)
                request.update(mutation)
                self.assertIn(reason, evaluate_request(self.model, request))

    def test_subject_request_and_consent_require_human_gates(self):
        request = deepcopy(VALID_REQUEST)
        request["purpose_id"] = "preference_management"
        request["basis_decision_id"] = "BASIS-SYN-002"
        request["fields"] = ["synthetic_preference"]
        self.assertIn("missing_consent_or_preference", evaluate_request(self.model, request))

        request = deepcopy(VALID_REQUEST)
        request["action"] = "delete"
        self.assertIn("human_approval_required", evaluate_request(self.model, request))

    def test_invented_owner_or_authority_is_rejected(self):
        model = deepcopy(self.model)
        model["metadata"]["owner_state"] = "named without approval"
        self.assertIn("metadata.owner_state must remain unassigned", validate_model(model))

        model = deepcopy(self.model)
        model["decision"]["real_data_authorized"] = True
        self.assertIn(
            "decision.real_data_authorized must be false",
            validate_model(model),
        )

    def test_mapping_preserves_all_ten_unaccepted_risks(self):
        mapping = yaml.safe_load(MAPPING_PATH.read_text(encoding="utf-8"))
        rows = mapping["mappings"]
        self.assertEqual(
            {f"PR-RISK-{number:03d}" for number in range(1, 11)},
            {row["stage10_risk_id"] for row in rows},
        )
        for row in rows:
            self.assertIn(row["residual_status"], {"open", "blocked"})
            self.assertFalse(row["risk_accepted"])
            self.assertFalse(row["production_action_allowed"])
            self.assertEqual(UNASSIGNED, row["owner_state"])
            self.assertTrue(row["evidence_paths"])

    def test_acceptance_cannot_grant_legal_real_data_or_production_authority(self):
        acceptance = yaml.safe_load(ACCEPTANCE_PATH.read_text(encoding="utf-8"))
        self.assertEqual("policy_review_candidate", acceptance["overall_decision"]["result"])
        for key, value in acceptance["overall_decision"].items():
            if key != "result":
                self.assertFalse(value, key)
        self.assertEqual(8, len(acceptance["criteria"]))
        for criterion in acceptance["criteria"]:
            self.assertEqual(UNASSIGNED, criterion["owner_state"])
            self.assertFalse(criterion["production_action_allowed"])
            self.assertTrue(criterion["evidence_paths"])

    def test_ci_is_pull_request_only_and_read_only(self):
        workflow = WORKFLOW_PATH.read_text(encoding="utf-8")
        for required in (
            "pull_request:",
            "permissions:\n  contents: read",
            "persist-credentials: false",
            "validate_aios_privacy_data_governance.py",
            "unittest discover",
            "validate_aios_workflow_schema.py",
            "compileall",
        ):
            self.assertIn(required, workflow)
        for prohibited in (
            "push:",
            "workflow_dispatch:",
            "contents: write",
            "pull-requests: write",
            "git push",
        ):
            self.assertNotIn(prohibited, workflow)


if __name__ == "__main__":
    unittest.main()
