from copy import deepcopy
import unittest

from Tests.validate_aios_architecture_security_foundations import (
    ROOT,
    UNASSIGNED,
    validate_acceptance,
    validate_mapping,
    validate_model,
    validate_repository,
    validate_threats,
)


class ArchitectureSecurityFoundationsTests(unittest.TestCase):
    def test_repository_package_is_complete(self):
        self.assertEqual([], validate_repository(ROOT))

    def test_invented_owner_and_risk_acceptance_are_rejected(self):
        data = {"threats": [{"category": category, "owner_state": UNASSIGNED, "acceptance_status": "not_accepted", "production_action_allowed": False, "evidence_paths": ["README.md"]} for category in ("identity", "secrets", "data_boundary", "connector", "execution", "audit", "supply_chain")]}
        data["threats"][0]["owner_state"] = "Named Person"
        data["threats"][0]["acceptance_status"] = "accepted"
        errors = validate_threats(data, ROOT)
        self.assertIn("threats[0].owner_state must remain unassigned", errors)
        self.assertIn("threats[0] must remain unaccepted and deny production action", errors)

    def test_provisioned_identity_secret_and_connector_are_rejected(self):
        model = self._minimal_model()
        model["trust_zones"][0]["provisioned"] = True
        model["identity_and_access"]["identities_created"] = True
        model["secrets_lifecycle"]["secret"] = "forbidden"
        model["connector_boundary"]["enabled_connectors"] = ["business-api"]
        errors = validate_model(model)
        self.assertTrue(any("provisioned must be false" in error for error in errors))
        self.assertIn("identity design must deny by default and create no identities", errors)
        self.assertIn("secrets lifecycle must not contain secret material fields", errors)
        self.assertIn("connector boundary must deny by default with no enabled connector or external write", errors)

    def test_collapsed_business_boundary_and_ready_claim_are_rejected(self):
        model = self._minimal_model()
        del model["business_boundaries"]["PC"]
        model["decision"]["production_ready"] = True
        errors = validate_model(model)
        self.assertIn("business boundaries must separate BUW, PC, 汇沣电商 and 六合通 with default deny", errors)
        self.assertIn("decision.production_ready must be false", errors)

    def test_stage10_risk_cannot_be_closed(self):
        mapping = {"mappings": [{"stage10_risk_id": f"PR-RISK-{i:03d}", "owner_state": UNASSIGNED, "residual_status": "open", "risk_accepted": False, "production_action_allowed": False, "evidence_paths": ["README.md"]} for i in range(1, 11)]}
        mapping["mappings"][0]["residual_status"] = "closed"
        mapping["mappings"][0]["risk_accepted"] = True
        errors = validate_mapping(mapping, ROOT)
        self.assertIn("mappings[0].residual_status must remain open or blocked", errors)
        self.assertIn("mappings[0] must not accept risk or allow production action", errors)

    def test_acceptance_cannot_authorize_production(self):
        acceptance = {"overall_decision": {"result": "design_review_candidate", "production_ready": True, "deployment_authorized": False, "pilot_authorized": False, "release_authorized": False}, "criteria": []}
        self.assertIn("acceptance overall_decision.production_ready must be false", validate_acceptance(acceptance, ROOT))

    @staticmethod
    def _minimal_model():
        return {
            "metadata": {"stage": 11, "stage_id": "AF-01", "issue": 24, "governance_version": "2.2", "main_baseline": "45944a50ea33e61ad2683082441d2dac75812906", "execution_thread": "019f89ac-e3b7-7b90-ad27-286708c407e0", "branch": "feat/aios-architecture-security-foundations-v1", "mode": "design_only", "stage_status": "Executing"},
            "six_system_questions": {key: "answer" for key in ("business_loop", "core_objects", "data_flow", "operators", "ai_human_boundary", "proof")},
            "business_boundaries": {"BUW": "separate", "PC": "separate", "汇沣电商": "company", "六合通": "excluded", "cross_boundary_default": "deny"},
            "trust_zones": [{"id": zone, "provisioned": False, "owner_state": UNASSIGNED} for zone in ("governance_control", "human_access", "ingress_policy", "orchestration_runtime", "durable_control_state", "audit_observability", "connector_boundary", "external_business_systems")],
            "target_components": [],
            "identity_and_access": {"least_privilege_default": "deny", "identities_created": False},
            "secrets_lifecycle": {"design_only": True, "secrets_created": False},
            "connector_boundary": {"default": "deny", "enabled_connectors": [], "external_writes_allowed": False},
            "decision": {"production_ready": False, "deployment_authorized": False, "pilot_authorized": False, "release_authorized": False, "risk_acceptance_granted": False},
        }


if __name__ == "__main__":
    unittest.main()
