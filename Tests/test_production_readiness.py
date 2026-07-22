from copy import deepcopy
from pathlib import Path
import unittest

from Tests.validate_aios_production_readiness import (
    ROOT,
    UNASSIGNED,
    validate_matrix,
    validate_repository,
    validate_risks,
)


class ProductionReadinessValidationTests(unittest.TestCase):
    def test_repository_readiness_evidence_is_complete(self):
        self.assertEqual([], validate_repository(ROOT))

    def test_invented_risk_owner_is_rejected(self):
        risks = {
            "risks": [
                {
                    "id": "RISK-TEST",
                    "category": "support",
                    "risk": "test risk",
                    "impact": "test impact",
                    "mitigation": "test mitigation",
                    "next_evidence": "test evidence",
                    "owner_state": "Invented Owner",
                    "acceptance_status": "not_accepted",
                    "acceptance_authority": "BUW AIOS Official Governance Thread",
                    "production_action_allowed": False,
                    "evidence_paths": ["README.md"],
                }
            ]
        }
        errors = validate_risks(risks, ROOT)
        self.assertIn("risks[0].owner_state must remain unassigned", errors)

    def test_risk_acceptance_and_production_action_fail_closed(self):
        risks = {
            "risks": [
                {
                    "id": "RISK-TEST",
                    "category": "security",
                    "risk": "test risk",
                    "impact": "test impact",
                    "mitigation": "test mitigation",
                    "next_evidence": "test evidence",
                    "owner_state": UNASSIGNED,
                    "acceptance_status": "accepted",
                    "acceptance_authority": "BUW AIOS Official Governance Thread",
                    "production_action_allowed": True,
                    "evidence_paths": ["README.md"],
                }
            ]
        }
        errors = validate_risks(risks, ROOT)
        self.assertIn("risks[0].acceptance_status must be not_accepted", errors)
        self.assertIn("risks[0] must deny production action", errors)

    def test_ready_claim_is_rejected(self):
        matrix = {
            "metadata": {
                "stage": 10,
                "stage_id": "PR-01",
                "issue": 21,
                "governance_version": "2.1",
                "main_baseline": "6cffaed4f4bc693aa897864396ae097b972bff80",
                "execution_thread": "019f8937-ac22-71a2-bb35-d8f6d2e0f55f",
                "branch": "feat/aios-production-readiness-v1",
                "mode": "prepare_only",
                "stage_status": "Executing",
            },
            "six_system_questions": {
                "business_loop": "x",
                "core_objects": "x",
                "data_flow": "x",
                "operators": "x",
                "ai_human_boundary": "x",
                "proof": "x",
            },
            "assessment_decision": {
                "recommendation": "ready",
                "production_ready": True,
                "release_authorized": True,
                "decision_authority": "BUW AIOS Official Governance Thread",
            },
            "business_boundaries": {
                "BUW": "separate",
                "PC": "separate",
                "汇沣电商": "company",
                "六合通": "excluded",
                "cross_boundary_default": "deny",
            },
            "readiness_gates": [],
            "human_approval_gates": [],
        }
        errors = validate_matrix(deepcopy(matrix), ROOT)
        self.assertIn("assessment recommendation must remain blocked", errors)
        self.assertIn("production_ready must be false", errors)
        self.assertIn("release_authorized must be false", errors)


if __name__ == "__main__":
    unittest.main()
