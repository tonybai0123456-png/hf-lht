from copy import deepcopy
import hashlib
from pathlib import Path
import unittest

import yaml

from Tests.validate_aios_operational_resilience import (
    evaluate_scenario,
    validate_current_registry_lifecycle,
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
        record = result["incident_record"]
        self.assertEqual(
            self.model["incident_record_contract"]["required_fields"],
            list(record),
        )
        self.assertEqual(self.fixture["scenario_id"], record["scenario_id"])
        self.assertEqual("2.2", record["policy_version"])
        for field in (
            "synthetic",
            "company",
            "brand",
            "service_id",
            "dependency_ids",
            "signal_type",
            "severity",
            "impact",
        ):
            self.assertEqual(self.fixture[field], record[field], field)
        self.assertEqual(result["result"], record["decision"])
        self.assertEqual(result["reason_codes"], record["reason_codes"])
        self.assertEqual(result["required_human_gates"], record["human_gates"])
        self.assertEqual(result["evidence_refs"], record["evidence_refs"])

    def test_missing_or_empty_scenario_identity_is_denied(self):
        for value in (None, "", "   "):
            with self.subTest(value=value):
                scenario = deepcopy(self.fixture)
                if value is None:
                    scenario.pop("scenario_id")
                else:
                    scenario["scenario_id"] = value
                result = evaluate_scenario(self.model, scenario)
                self.assertEqual("denied", result["result"])
                self.assertIn("missing_scenario_id", result["reason_codes"])
                self.assertEqual(
                    value.strip() if isinstance(value, str) else "",
                    result["incident_record"]["scenario_id"],
                )

    def test_scenario_collections_must_be_exact_and_unique(self):
        cases = []

        duplicate_dependency = deepcopy(self.fixture)
        duplicate_dependency["dependency_ids"].append(
            duplicate_dependency["dependency_ids"][0]
        )
        cases.append((duplicate_dependency, "duplicate_dependency"))

        reordered_dependencies = deepcopy(self.fixture)
        reordered_dependencies["dependency_ids"].reverse()
        cases.append((reordered_dependencies, "dependency_contract_mismatch"))

        duplicate_evidence = deepcopy(self.fixture)
        duplicate_evidence["recovery_evidence"].append(
            deepcopy(duplicate_evidence["recovery_evidence"][0])
        )
        cases.append((duplicate_evidence, "duplicate_recovery_evidence"))

        reordered_evidence = deepcopy(self.fixture)
        reordered_evidence["recovery_evidence"].reverse()
        cases.append(
            (reordered_evidence, "recovery_evidence_contract_mismatch")
        )

        duplicate_gate = deepcopy(self.fixture)
        duplicate_gate["human_gates"].append(duplicate_gate["human_gates"][0])
        cases.append((duplicate_gate, "duplicate_human_gate"))

        reordered_gates = deepcopy(self.fixture)
        reordered_gates["human_gates"].reverse()
        cases.append((reordered_gates, "human_gate_contract_mismatch"))

        non_scalar_dependency = deepcopy(self.fixture)
        non_scalar_dependency["dependency_ids"] = [{}]
        cases.append((non_scalar_dependency, "unknown_dependency"))

        non_scalar_gate = deepcopy(self.fixture)
        non_scalar_gate["human_gates"] = [{}]
        cases.append((non_scalar_gate, "human_gate_contract_mismatch"))

        for scenario, reason in cases:
            with self.subTest(reason=reason):
                result = evaluate_scenario(self.model, scenario)
                self.assertEqual("denied", result["result"])
                self.assertIn(reason, result["reason_codes"])

    def test_malformed_extra_recovery_evidence_entries_are_denied(self):
        for malformed in ({}, "invalid", None, {"id": ""}, {"id": "   "}):
            with self.subTest(malformed=malformed):
                scenario = deepcopy(self.fixture)
                scenario["recovery_evidence"].append(malformed)
                result = evaluate_scenario(self.model, scenario)
                self.assertEqual("denied", result["result"])
                self.assertIn(
                    "recovery_evidence_contract_mismatch",
                    result["reason_codes"],
                )

    def test_claim_contract_requires_exact_false_keys(self):
        required_claims = set(self.fixture["claims"])
        cases = []

        empty = deepcopy(self.fixture)
        empty["claims"] = {}
        cases.append((empty, "invalid_claim_contract"))

        missing = deepcopy(self.fixture)
        missing["claims"].pop(next(iter(required_claims)))
        cases.append((missing, "invalid_claim_contract"))

        unknown = deepcopy(self.fixture)
        unknown["claims"]["unknown_claim"] = False
        cases.append((unknown, "invalid_claim_contract"))

        non_boolean = deepcopy(self.fixture)
        non_boolean["claims"]["sla_achieved"] = 0
        cases.append((non_boolean, "invalid_claim_contract"))

        truthy = deepcopy(self.fixture)
        truthy["claims"]["restore_tested"] = True
        cases.append((truthy, "achievement_claim"))

        for scenario, reason in cases:
            with self.subTest(reason=reason):
                result = evaluate_scenario(self.model, scenario)
                self.assertEqual("denied", result["result"])
                self.assertIn(reason, result["reason_codes"])

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

    def test_model_rejects_every_unsafe_contract_mutation(self):
        cases = (
            (
                "automatic incident declaration",
                lambda model: model["incident_lifecycle"].__setitem__(
                    "incident_declaration_automatic", True
                ),
                "incident_lifecycle must be exact, manual, and unassigned",
            ),
            (
                "automatic containment",
                lambda model: model["incident_lifecycle"].__setitem__(
                    "containment_automatic", True
                ),
                "incident_lifecycle must be exact, manual, and unassigned",
            ),
            (
                "automatic recovery",
                lambda model: model["incident_lifecycle"].__setitem__(
                    "recovery_automatic", True
                ),
                "incident_lifecycle must be exact, manual, and unassigned",
            ),
            (
                "automatic closure",
                lambda model: model["incident_lifecycle"].__setitem__(
                    "closure_automatic", True
                ),
                "incident_lifecycle must be exact, manual, and unassigned",
            ),
            (
                "incident lifecycle owner",
                lambda model: model["incident_lifecycle"].__setitem__(
                    "owner_state", "Incident Manager"
                ),
                "incident_lifecycle must be exact, manual, and unassigned",
            ),
            (
                "unsafe runbook mode",
                lambda model: model["runbook_contract"].__setitem__(
                    "execution_mode", "execute"
                ),
                "runbook_contract must be exact, prepare-only, and unassigned",
            ),
            (
                "runbook owner",
                lambda model: model["runbook_contract"].__setitem__(
                    "owner_state", "Runbook Owner"
                ),
                "runbook_contract must be exact, prepare-only, and unassigned",
            ),
            (
                "runbook real commands",
                lambda model: model["runbook_contract"].__setitem__(
                    "real_commands_allowed", True
                ),
                "runbook_contract must be exact, prepare-only, and unassigned",
            ),
            (
                "paging",
                lambda model: model["escalation_contract"].__setitem__(
                    "paging_enabled", True
                ),
                "escalation_contract must be exact, non-operational, and unassigned",
            ),
            (
                "escalation owner",
                lambda model: model["escalation_contract"].__setitem__(
                    "owner_state", "On-call Manager"
                ),
                "escalation_contract must be exact, non-operational, and unassigned",
            ),
            (
                "external communication",
                lambda model: model["escalation_contract"].__setitem__(
                    "external_communication_enabled", True
                ),
                "escalation_contract must be exact, non-operational, and unassigned",
            ),
            (
                "alert delivery",
                lambda model: model["observability_contract"].__setitem__(
                    "alert_delivery_enabled", True
                ),
                "observability_contract must be exact, disconnected, and unassigned",
            ),
            (
                "observability owner",
                lambda model: model["observability_contract"].__setitem__(
                    "owner_state", "Monitoring Owner"
                ),
                "observability_contract must be exact, disconnected, and unassigned",
            ),
            (
                "monitoring connector",
                lambda model: model["observability_contract"].__setitem__(
                    "monitoring_connector_enabled", True
                ),
                "observability_contract must be exact, disconnected, and unassigned",
            ),
            (
                "durable telemetry",
                lambda model: model["observability_contract"].__setitem__(
                    "durable_telemetry_claimed", True
                ),
                "observability_contract must be exact, disconnected, and unassigned",
            ),
            (
                "mutable audit",
                lambda model: model["audit_contract"].__setitem__(
                    "append_only_design", False
                ),
                "audit_contract must be exact, non-persistent, and unassigned",
            ),
            (
                "audit owner",
                lambda model: model["audit_contract"].__setitem__(
                    "owner_state", "Audit Owner"
                ),
                "audit_contract must be exact, non-persistent, and unassigned",
            ),
            (
                "persistent audit",
                lambda model: model["audit_contract"].__setitem__(
                    "persistent_store_provisioned", True
                ),
                "audit_contract must be exact, non-persistent, and unassigned",
            ),
            (
                "personal audit content",
                lambda model: model["audit_contract"].__setitem__(
                    "raw_personal_content_allowed", True
                ),
                "audit_contract must be exact, non-persistent, and unassigned",
            ),
            (
                "audit credentials",
                lambda model: model["audit_contract"].__setitem__(
                    "credentials_allowed", True
                ),
                "audit_contract must be exact, non-persistent, and unassigned",
            ),
            (
                "unsafe allowed action",
                lambda model: model["allowed_prepare_actions"].append(
                    "perform_failover"
                ),
                "allowed_prepare_actions must equal the authorized prepare-only actions",
            ),
            (
                "missing prohibited action",
                lambda model: model["prohibited_real_actions"].remove(
                    "perform_restore"
                ),
                "prohibited_real_actions must equal the authorized real-action denials",
            ),
        )
        for name, mutate, expected in cases:
            with self.subTest(name=name):
                model = deepcopy(self.model)
                mutate(model)
                self.assertIn(expected, validate_model(model))

    def test_model_identity_collections_require_unique_non_empty_ids(self):
        model = deepcopy(self.model)
        model["dependencies"].append(deepcopy(model["dependencies"][0]))
        self.assertIn(
            "dependencies must contain unique non-empty ids",
            validate_model(model),
        )

        model = deepcopy(self.model)
        model["recovery_evidence_requirements"].append(
            deepcopy(model["recovery_evidence_requirements"][0])
        )
        self.assertIn(
            "recovery_evidence_requirements must contain unique non-empty ids",
            validate_model(model),
        )

        for section in (
            "continuity_tiers",
            "severity_levels",
            "impact_classes",
            "failure_modes",
        ):
            with self.subTest(section=section):
                model = deepcopy(self.model)
                model[section].append(deepcopy(model[section][0]))
                self.assertIn(
                    f"{section} must contain unique non-empty ids",
                    validate_model(model),
                )

    def test_evaluator_does_not_trust_mutated_action_sets(self):
        model = deepcopy(self.model)
        model["allowed_prepare_actions"].append("perform_failover")
        model["prohibited_real_actions"].remove("perform_failover")
        scenario = deepcopy(self.fixture)
        scenario["requested_action"] = "perform_failover"
        result = evaluate_scenario(model, scenario)
        self.assertEqual("denied", result["result"])
        self.assertIn("unsafe_continuity_action", result["reason_codes"])

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

    def test_registry_records_archived_stage13_and_reviewed_stage14(self):
        stage_registry = STAGE_REGISTRY.read_text(encoding="utf-8")
        project_registry = PROJECT_REGISTRY.read_text(encoding="utf-8")
        stage13 = next(line for line in stage_registry.splitlines() if line.startswith("| 13 |"))
        stage14 = next(line for line in stage_registry.splitlines() if line.startswith("| 14 |"))
        for token in (
            "Issue #32", "Issue #34", "019f8a35-6d4e-7c60-b35a-79de8626d4e3",
            "feat/aios-operational-resilience-v1", "327d9e9", "7b16a5c",
            "19/19", "80/80", "| Archived |", "no production/staging",
            "risk acceptance", "pilot", "release",
        ):
            self.assertIn(token, stage13)
        frozen_stage13 = {
            ROOT / "Governance/AIOS-Operational-Resilience-v1.md": "e453f6b13a1ce0f12c2867208fcc45163580dd20fe24853789bbf00ede4f8d96",
            ROOT / "Governance/AIOS-Operational-Resilience-Model-v1.yaml": "fc3c42dab820a1a38b05dfa5e81829b779e9c0802dd72527cb9fc1053c51e35e",
            ROOT / "Governance/AIOS-Operational-Resilience-Acceptance-Matrix-v1.yaml": "ff961770e395629f4ea14bd6099c10e107160e1b49241cf1dd57248d55b16406",
            ROOT / "Governance/AIOS-Operational-Resilience-Stage10-12-Mapping-v1.yaml": "8a8b62fafac828ef560766c07da427695f1758d6bc65f714d2e4db1f822da7bb",
        }
        for path, expected_sha256 in frozen_stage13.items():
            self.assertEqual(expected_sha256, hashlib.sha256(path.read_bytes()).hexdigest())
        stage13_model = yaml.safe_load(
            (ROOT / "Governance/AIOS-Operational-Resilience-Model-v1.yaml").read_text(encoding="utf-8")
        )
        self.assertFalse(stage13_model["decision"]["risk_acceptance_granted"])
        self.assertFalse(stage13_model["decision"]["production_ready"])
        for token in (
            "Issue #36", "019f8c92-e709-7a83-b06c-fa014cf0b216",
            "feat/aios-support-controlled-pilot-design-v1", "PR #37",
            "| Reviewed |", "7184d917", "Mandatory Return", "needs_human_governance",
            "Human Governance Thread review passed", "no pilot authority",
        ):
            self.assertIn(token, stage14)
        self.assertIn("Stage 13 Archived / Stage 14 Reviewed", project_registry)

    def test_stage14_reviewed_lifecycle_and_authority_escalation_fail_closed(self):
        stage_registry = STAGE_REGISTRY.read_text(encoding="utf-8")
        project_registry = PROJECT_REGISTRY.read_text(encoding="utf-8")
        self.assertEqual([], validate_current_registry_lifecycle(stage_registry, project_registry))

        for status in ("Reported", "Archived"):
            with self.subTest(stage_status=status):
                mutated = stage_registry.replace("| Reviewed |", f"| {status} |")
                errors = validate_current_registry_lifecycle(mutated, project_registry)
                self.assertTrue(any("must preserve evidence-backed Reviewed status" in error for error in errors), errors)

        mutations = {
            "pilot": stage_registry.replace("no pilot authority", "pilot authority granted"),
            "self_approval": stage_registry.replace(
                "Human Governance Thread review passed",
                "self-approved review passed",
            ),
            "released": stage_registry.replace("no pilot authority", "release authorized"),
        }
        for name, mutated in mutations.items():
            with self.subTest(stage_mutation=name):
                errors = validate_current_registry_lifecycle(mutated, project_registry)
                self.assertTrue(any("exceeds Reviewed authority" in error for error in errors), errors)

        for status in ("Reported", "Archived"):
            with self.subTest(project_status=status):
                mutated_project = project_registry.replace(
                    "Stage 13 Archived / Stage 14 Reviewed",
                    f"Stage 13 Archived / Stage 14 {status}",
                )
                errors = validate_current_registry_lifecycle(stage_registry, mutated_project)
                self.assertTrue(any("must preserve Stage 14 Reviewed" in error for error in errors), errors)

        mutated_project = project_registry.replace(
            "Human Governance Thread review passed",
            "self-approved review passed and ready for pilot",
        )
        errors = validate_current_registry_lifecycle(stage_registry, mutated_project)
        self.assertTrue(any("Project Registry exceeds Reviewed authority" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
