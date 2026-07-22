from copy import deepcopy
from pathlib import Path
import unittest

import yaml

from Tests.validate_aios_operational_resilience import (
    evaluate_scenario,
    validate_model,
    validate_repository,
)


ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / "Governance" / "AIOS-Operational-Resilience-Model-v1.yaml"
FIXTURE_PATH = (
    ROOT
    / "Tests"
    / "Fixtures"
    / "operational-resilience"
    / "synthetic-service-degradation.yaml"
)
MAPPING_PATH = (
    ROOT / "Governance" / "AIOS-Operational-Resilience-Stage10-12-Mapping-v1.yaml"
)
ACCEPTANCE_PATH = (
    ROOT / "Governance" / "AIOS-Operational-Resilience-Acceptance-Matrix-v1.yaml"
)
WORKFLOW_PATH = ROOT / ".github" / "workflows" / "validate-aios-operational-resilience.yml"
STAGE_REGISTRY = ROOT / "Governance" / "AIOS-Stage-Registry.md"
PROJECT_REGISTRY = ROOT / "Governance" / "AIOS-Project-Registry.md"
UNASSIGNED = "unassigned / governance decision required"


class OperationalResilienceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model = yaml.safe_load(MODEL_PATH.read_text(encoding="utf-8"))
        cls.fixture = yaml.safe_load(FIXTURE_PATH.read_text(encoding="utf-8"))

    def test_repository_package_is_complete(self):
        self.assertEqual([], validate_repository(ROOT))

    def test_valid_synthetic_scenario_stops_at_human_gate(self):
        self.assertEqual([], validate_model(self.model))
        result = evaluate_scenario(self.model, self.fixture)
        self.assertEqual("needs_human_approval", result["result"])
        self.assertEqual([], result["reason_codes"])
        self.assertEqual(
            [
                "incident_declaration",
                "failover",
                "restoration",
                "external_communication",
                "exception",
                "risk_acceptance",
                "release",
            ],
            result["required_human_gates"],
        )
        self.assertFalse(result["external_actions_performed"])
        self.assertGreaterEqual(len(result["evidence_refs"]), 3)

    def test_required_fail_closed_scenario_mutations(self):
        cases = [
            ({"synthetic": False}, "real_or_unmarked_signal"),
            ({"company": "六合通"}, "cross_boundary"),
            ({"brand": "PC"}, "cross_boundary"),
            ({"service_id": "unknown"}, "unknown_service"),
            ({"dependency_ids": ["unknown"]}, "unknown_dependency"),
            ({"severity": "SEV-0"}, "invalid_severity"),
            ({"impact": "catastrophic"}, "invalid_impact"),
            ({"signal_type": "unknown_failure"}, "unknown_failure_mode"),
            (
                {"continuity_target": {"tier_id": "CT-1", "rto_minutes": 5, "rpo_minutes": 5}},
                "unsupported_rto_rpo",
            ),
            ({"recovery_evidence": []}, "missing_recovery_evidence"),
            ({"human_gates": []}, "missing_human_gate"),
            ({"requested_action": "perform_failover"}, "unsafe_continuity_action"),
            ({"claims": {"sla_achieved": True}}, "achievement_claim"),
        ]
        for mutation, reason in cases:
            with self.subTest(reason=reason):
                scenario = deepcopy(self.fixture)
                scenario.update(mutation)
                result = evaluate_scenario(self.model, scenario)
                self.assertEqual("denied", result["result"])
                self.assertIn(reason, result["reason_codes"])
                self.assertFalse(result["external_actions_performed"])

    def test_failure_taxonomy_and_incident_record_contract_are_required(self):
        model = deepcopy(self.model)
        model.pop("failure_modes")
        self.assertIn("failure_modes must be a non-empty list", validate_model(model))

        model = deepcopy(self.model)
        model.pop("incident_record_contract")
        self.assertIn(
            "incident_record_contract must require synthetic fields and prohibit persistence",
            validate_model(model),
        )

    def test_recovery_evidence_state_and_external_action_fail_closed(self):
        scenario = deepcopy(self.fixture)
        scenario["recovery_evidence"][0]["state"] = "restore_test_passed"
        result = evaluate_scenario(self.model, scenario)
        self.assertIn("invalid_recovery_evidence_state", result["reason_codes"])
        self.assertIn("achievement_claim", result["reason_codes"])

        scenario = deepcopy(self.fixture)
        scenario["external_actions_performed"] = True
        result = evaluate_scenario(self.model, scenario)
        self.assertIn("unsafe_continuity_action", result["reason_codes"])

    def test_unknown_and_wildcard_values_never_fall_back_to_allow(self):
        for field, value, reason in (
            ("service_id", "*", "unknown_service"),
            ("dependency_ids", ["*"], "unknown_dependency"),
            ("severity", "", "invalid_severity"),
            ("impact", None, "invalid_impact"),
            ("company", "*", "cross_boundary"),
            ("brand", "shared", "cross_boundary"),
        ):
            with self.subTest(field=field):
                scenario = deepcopy(self.fixture)
                scenario[field] = value
                self.assertIn(reason, evaluate_scenario(self.model, scenario)["reason_codes"])

    def test_model_rejects_operational_authority_and_capability_claims(self):
        for flag in (
            "incident_authority_granted",
            "failover_authorized",
            "restoration_authorized",
            "external_communication_authorized",
            "exception_authorized",
            "risk_acceptance_granted",
            "pilot_authorized",
            "release_authorized",
            "production_ready",
            "sla_slo_achieved",
            "backup_restore_tested",
            "real_incident_capability",
        ):
            with self.subTest(flag=flag):
                model = deepcopy(self.model)
                model["decision"][flag] = True
                self.assertIn(f"decision.{flag} must be false", validate_model(model))

    def test_model_requires_unassigned_owners_and_design_only_targets(self):
        model = deepcopy(self.model)
        model["services"][0]["owner_state"] = "Operations Manager"
        self.assertIn("services[0].owner_state must remain unassigned", validate_model(model))

        model = deepcopy(self.model)
        model["continuity_tiers"][0]["claim_state"] = "achieved_slo"
        self.assertIn(
            "continuity_tiers[0].claim_state must be design_target_only",
            validate_model(model),
        )

        model = deepcopy(self.model)
        model["recovery_evidence_requirements"][0]["claim_state"] = "tested"
        self.assertIn(
            "recovery_evidence_requirements[0].claim_state must be design_requirement_only",
            validate_model(model),
        )

    def test_mapping_preserves_stage10_risks_and_stage11_12_traceability(self):
        mapping = yaml.safe_load(MAPPING_PATH.read_text(encoding="utf-8"))
        entries = mapping["mappings"]
        self.assertEqual(
            {f"PR-RISK-{number:03d}" for number in range(1, 11)},
            {entry["stage10_risk_id"] for entry in entries},
        )
        for entry in entries:
            self.assertIn(entry["residual_status"], {"open", "blocked"})
            self.assertFalse(entry["risk_accepted"])
            self.assertFalse(entry["production_action_allowed"])
            self.assertEqual(UNASSIGNED, entry["owner_state"])
            self.assertTrue(entry["stage11_evidence"])
            self.assertTrue(entry["stage12_evidence"])
            self.assertTrue(entry["or01_control"])

    def test_acceptance_is_design_only_and_cannot_grant_authority(self):
        acceptance = yaml.safe_load(ACCEPTANCE_PATH.read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(acceptance["criteria"]), 10)
        for criterion in acceptance["criteria"]:
            self.assertTrue(criterion["design_only"])
            self.assertEqual("pass", criterion["expected"])
            self.assertTrue(criterion["evidence_paths"])
        for flag, value in acceptance["authority_boundary"].items():
            self.assertFalse(value, flag)

    def test_ci_is_pull_request_only_and_read_only(self):
        workflow = WORKFLOW_PATH.read_text(encoding="utf-8")
        self.assertIn("pull_request:", workflow)
        self.assertNotIn("push:", workflow)
        self.assertNotIn("workflow_dispatch:", workflow)
        self.assertIn("permissions:\n  contents: read", workflow)
        self.assertIn("persist-credentials: false", workflow)
        for prohibited in (
            "contents: write",
            "pull-requests: write",
            "issues: write",
            "git push",
            "curl ",
            "wget ",
        ):
            self.assertNotIn(prohibited, workflow)

    def test_registry_stops_at_reported_and_stage14_remains_planned(self):
        stage_registry = STAGE_REGISTRY.read_text(encoding="utf-8")
        project_registry = PROJECT_REGISTRY.read_text(encoding="utf-8")
        stage13 = next(line for line in stage_registry.splitlines() if line.startswith("| 13 |"))
        stage14 = next(line for line in stage_registry.splitlines() if line.startswith("| 14 |"))
        self.assertIn("Issue #32", stage13)
        self.assertIn("019f8a35-6d4e-7c60-b35a-79de8626d4e3", stage13)
        self.assertIn("feat/aios-operational-resilience-v1", stage13)
        self.assertIn("| Reported |", stage13)
        self.assertNotIn("| Reviewed |", stage13)
        self.assertNotIn("| Archived |", stage13)
        self.assertIn("No Execution Thread assigned", stage14)
        self.assertIn("| Planned |", stage14)
        self.assertIn("Stage 13 Reported / Stage 14 Planned", project_registry)


if __name__ == "__main__":
    unittest.main()
