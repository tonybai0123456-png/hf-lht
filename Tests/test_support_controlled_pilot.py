from __future__ import annotations

import copy
import importlib.util
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / "Governance/AIOS-Support-Controlled-Pilot-Model-v1.yaml"
VALIDATOR = ROOT / "Tests/validate_aios_support_controlled_pilot.py"


def load_validator():
    spec = importlib.util.spec_from_file_location("support_pilot_validator", VALIDATOR)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class SupportControlledPilotTests(unittest.TestCase):
    def test_identity_version_order_and_schema_attacks_deny(self):
        validator = load_validator()
        model = validator.load_repository_yaml(ROOT, validator.MODEL_PATH)
        fixture = validator.load_repository_yaml(ROOT, validator.FIXTURE_PATH)
        cases = {
            "missing_id": lambda r, e: r.pop("support_request_id"),
            "wildcard_id": lambda r, e: r.__setitem__("scope_id", "SCOPE-SYN-*"),
            "wrong_prefix": lambda r, e: r.__setitem__(
                "pilot_candidate_id", "SR-SYN-001"
            ),
            "mixed_version": lambda r, e: e.__setitem__(
                "model_version", "support_controlled_pilot_eligibility/v2"
            ),
            "duplicate_evidence": lambda r, e: e["evidence_refs"].append(
                e["evidence_refs"][0]
            ),
            "reordered_evidence": lambda r, e: e["evidence_refs"].reverse(),
            "unknown_field": lambda r, e: r.__setitem__("extension", True),
        }
        for name, mutate in cases.items():
            with self.subTest(name=name):
                request = copy.deepcopy(fixture["request"])
                evidence = copy.deepcopy(fixture["evidence_bundle"])
                mutate(request, evidence)
                decision = validator.evaluate_eligibility(model, request, evidence)
                self.assertEqual("denied", decision["result"])
                self.assertTrue(decision["reason_codes"])
                self.assertEqual([], decision["required_human_gates"])
                self.assertEqual([], decision["external_actions_performed"])

    def test_valid_fixture_needs_human_governance_without_side_effects(self):
        validator = load_validator()
        model = validator.load_repository_yaml(ROOT, validator.MODEL_PATH)
        fixture = validator.load_repository_yaml(ROOT, validator.FIXTURE_PATH)
        before = copy.deepcopy((model, fixture))
        first = validator.evaluate_eligibility(
            model, fixture["request"], fixture["evidence_bundle"]
        )
        second = validator.evaluate_eligibility(
            model, fixture["request"], fixture["evidence_bundle"]
        )
        self.assertEqual(first, second)
        self.assertEqual(before, (model, fixture))
        self.assertEqual("needs_human_governance", first["result"])
        self.assertEqual([], first["reason_codes"])
        self.assertEqual(
            [g["gate_id"] for g in model["human_gates"]],
            first["required_human_gates"],
        )
        self.assertEqual([], first["external_actions_performed"])
        self.assertEqual(
            {
                "result",
                "model_version",
                "support_request_id",
                "support_case_id",
                "pilot_candidate_id",
                "scope_id",
                "reason_codes",
                "required_human_gates",
                "evidence_refs",
                "upstream_risk_states",
                "audit_record",
                "decision_record",
                "external_actions_performed",
            },
            set(first),
        )

    def test_loader_accepts_only_allowlisted_repository_yaml(self):
        validator = load_validator()
        loaded = validator.load_repository_yaml(ROOT, validator.MODEL_PATH)
        self.assertEqual(
            "support_controlled_pilot_eligibility/v1", loaded["model_version"]
        )
        for unsafe in (
            Path("../outside.yaml"),
            Path("Governance/AIOS-Stage-Registry.md"),
            Path("/tmp/input.yaml"),
        ):
            with self.subTest(unsafe=unsafe), self.assertRaises(ValueError):
                validator.load_repository_yaml(ROOT, unsafe)

    def test_model_has_exact_identity_boundary_outcomes_and_gate_order(self):
        validator = load_validator()
        model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
        self.assertEqual([], validator.validate_model(model))
        self.assertEqual(
            "support_controlled_pilot_eligibility/v1", model["model_version"]
        )
        self.assertEqual(
            {"company": "汇沣电商", "brand": "BUW"}, model["allowed_scope"]
        )
        self.assertEqual(["PC", "六合通"], model["excluded_entities"])
        self.assertEqual(
            ["denied", "needs_human_governance"], model["allowed_results"]
        )
        self.assertEqual(
            [
                "HG-WRITTEN-SPEC-APPROVAL",
                "HG-IMPLEMENTATION-EVIDENCE-ACCEPTANCE",
                "HG-NAMED-OWNER-APPOINTMENT",
                "HG-REAL-SCOPE-AND-DATA-AUTHORIZATION",
                "HG-STAGE10-RISK-DISPOSITION",
                "HG-STAGE11-13-EVIDENCE-ACCEPTANCE",
                "HG-SUPPORT-STOP-WITHDRAWAL-ACCEPTANCE",
                "HG-METRIC-AND-EVIDENCE-ACCEPTANCE",
                "HG-BOUNDED-AUTHORITY-DEFINITION",
                "HG-REAL-PILOT-ENTRY-DECISION",
            ],
            [gate["gate_id"] for gate in model["human_gates"]],
        )


if __name__ == "__main__":
    unittest.main()
