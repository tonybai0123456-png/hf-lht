#!/usr/bin/env python3
"""Behavior tests for the Stage 8 synthetic-only Runtime Orchestrator v1."""

from copy import deepcopy
from pathlib import Path
import socket
import subprocess
import unittest
from unittest.mock import patch
import urllib.request

import yaml

from Runtime.controlled_orchestrator import load_workflow
import Runtime.runtime_orchestrator as runtime_module
from Runtime.runtime_orchestrator import (
    RunIdCollisionError,
    RuntimeOrchestrator,
    RuntimePolicyError,
)


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_ROOT = ROOT / "Tests" / "Fixtures" / "runtime-orchestrator"
STORE_FIXTURE = FIXTURE_ROOT / "store-anomaly.yaml"
STORE_WORKFLOW = ROOT / "Schemas" / "Workflows" / "store-anomaly.yaml"

RUNTIME_OUTPUT_FIELDS = {
    "run_id",
    "agent",
    "status",
    "reporting_period",
    "executive_status",
    "summary",
    "kpi_snapshot",
    "completed",
    "in_progress",
    "business_impact",
    "findings",
    "recommended_actions",
    "decisions_required",
    "risks_and_exceptions",
    "evidence_used",
    "confidence",
    "missing_information",
    "approval_request",
    "handoffs",
    "blockers",
    "next_priorities",
    "next_review",
    "domain_payload",
}

FIXTURE_EXPECTATIONS = {
    "agent-reports-to-ceo.yaml": ("agent_reports_to_ceo_decision_queue", "CEO", 3),
    "customer-complaint.yaml": ("customer_complaint_remediation", "CustomerService", 3),
    "marketing-crm-campaign.yaml": ("marketing_crm_campaign", "Marketing", 3),
    "shopify-developer.yaml": ("shopify_to_developer_draft_pr", "Shopify", 5),
    "store-anomaly.yaml": ("store_anomaly_investigation", "Retail", 2),
}


def set_nested(document: dict, path: tuple[str, ...], value: object) -> None:
    target = document
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value


def load_request(path: Path) -> dict:
    document = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(document, dict):
        raise AssertionError("synthetic test fixture must be a mapping")
    return document


class RuntimeOrchestratorTests(unittest.TestCase):
    def store_request(self) -> dict:
        return load_request(STORE_FIXTURE)

    def test_all_published_workflows_stop_at_approval(self) -> None:
        for fixture_name, (workflow_id, agent, completed_count) in FIXTURE_EXPECTATIONS.items():
            with self.subTest(fixture=fixture_name):
                result = RuntimeOrchestrator().execute(load_request(FIXTURE_ROOT / fixture_name))

                self.assertEqual(result["status"], "needs_approval")
                self.assertEqual(result["agent"], agent)
                self.assertEqual(result["domain_payload"]["workflow_id"], workflow_id)
                self.assertEqual(
                    len(result["domain_payload"]["completed_steps"]), completed_count
                )
                self.assertFalse(result["domain_payload"]["external_writes_performed"])

    def test_output_uses_complete_runtime_contract(self) -> None:
        result = RuntimeOrchestrator().execute(self.store_request())

        self.assertEqual(set(result), RUNTIME_OUTPUT_FIELDS)
        self.assertEqual(result["domain_payload"]["runtime_orchestrator_version"], "1.0")
        self.assertEqual(len(result["domain_payload"]["request_fingerprint"]), 64)
        self.assertEqual(
            result["domain_payload"]["workflow_source"],
            "Schemas/Workflows/store-anomaly.yaml",
        )

    def test_results_and_audit_are_deterministic(self) -> None:
        request = self.store_request()
        first = RuntimeOrchestrator().execute(request)
        second = RuntimeOrchestrator().execute(deepcopy(request))

        self.assertEqual(first, second)
        self.assertTrue(first["domain_payload"]["audit_log"])
        self.assertEqual(
            {entry["at"] for entry in first["domain_payload"]["audit_log"]},
            {"2026-07-22T08:00:00Z"},
        )

    def test_identical_run_id_returns_copy_without_rerun(self) -> None:
        runner = RuntimeOrchestrator()
        request = self.store_request()

        with patch.object(runner, "_execute_once", wraps=runner._execute_once) as execute_once:
            first = runner.execute(request)
            second = runner.execute(deepcopy(request))

        self.assertEqual(execute_once.call_count, 1)
        self.assertEqual(first, second)
        self.assertIsNot(first, second)
        self.assertIsNot(first["domain_payload"], second["domain_payload"])

    def test_changed_request_with_same_run_id_rejects_collision(self) -> None:
        runner = RuntimeOrchestrator()
        request = self.store_request()
        runner.execute(request)
        changed = deepcopy(request)
        changed["task"]["objective"] = "Different synthetic objective"

        with self.assertRaises(RunIdCollisionError):
            runner.execute(changed)

    def test_policy_mutations_fail_closed(self) -> None:
        mutations = [
            (("runtime_version",), "2.0"),
            (("business_context", "company"), "六合通"),
            (("business_context", "brand"), "shared"),
            (("constraints", "privacy_classification"), "production"),
            (("constraints", "dry_run"), False),
            (("constraints", "allow_external_writes"), True),
            (("approval_context", "approval_status"), "approved"),
            (("task", "workflow_id"), "unknown_workflow"),
        ]
        for field_path, value in mutations:
            with self.subTest(field_path=field_path, value=value):
                request = self.store_request()
                set_nested(request, field_path, value)
                with self.assertRaises(RuntimePolicyError):
                    RuntimeOrchestrator().execute(request)

    def test_malformed_policy_collections_fail_closed_with_policy_error(self) -> None:
        mutations = [
            (("task", "acceptance_criteria"), [None]),
            (("constraints", "known_business_rules"), [None]),
            (
                ("constraints", "prohibited_actions"),
                ["external_write", "production_execution", "human_decision", {}],
            ),
        ]
        for field_path, value in mutations:
            with self.subTest(field_path=field_path):
                request = self.store_request()
                set_nested(request, field_path, value)
                with self.assertRaises(RuntimePolicyError):
                    RuntimeOrchestrator().execute(request)

    def test_arbitrary_path_and_dynamic_code_fields_are_rejected(self) -> None:
        path_request = self.store_request()
        path_request["workflow_path"] = "/tmp/untrusted.yaml"
        with self.assertRaises(RuntimePolicyError):
            RuntimeOrchestrator().execute(path_request)

        code_request = self.store_request()
        code_request["task"]["code"] = "print('untrusted')"
        with self.assertRaises(RuntimePolicyError):
            RuntimeOrchestrator().execute(code_request)

    def test_runtime_module_exposes_no_path_based_request_loader(self) -> None:
        self.assertFalse(hasattr(runtime_module, "load_request"))

    def test_missing_required_workflow_input_is_rejected_before_execution(self) -> None:
        request = self.store_request()
        del request["task"]["workflow_inputs"]["anomaly_type"]
        runner = RuntimeOrchestrator()

        with patch.object(runner, "_execute_once", wraps=runner._execute_once) as execute_once:
            with self.assertRaises(RuntimePolicyError):
                runner.execute(request)

        execute_once.assert_not_called()

    def test_conflicting_store_scope_is_rejected(self) -> None:
        request = self.store_request()
        request["task"]["workflow_inputs"]["store_code"] = "OTHER"

        with self.assertRaises(RuntimePolicyError):
            RuntimeOrchestrator().execute(request)

    def test_agent_must_match_workflow_accountability(self) -> None:
        request = self.store_request()
        request["agent"] = "Marketing"

        with self.assertRaises(RuntimePolicyError):
            RuntimeOrchestrator().execute(request)

    def test_pc_brand_remains_explicit_and_separate(self) -> None:
        request = self.store_request()
        request["run_id"] = "SYN-RO-STORE-PC-001"
        request["business_context"]["brand"] = "PC"

        result = RuntimeOrchestrator().execute(request)

        self.assertTrue(result["domain_payload"]["idempotency_key"].startswith("store_anomaly_investigation:PC:G0011:"))

    def test_prohibited_step_is_rejected_without_execution(self) -> None:
        workflow = load_workflow(STORE_WORKFLOW)
        workflow["steps"][0]["action_class"] = "prohibited"

        with patch("Runtime.runtime_orchestrator.load_workflow", return_value=workflow):
            result = RuntimeOrchestrator().execute(self.store_request())

        self.assertEqual(result["status"], "rejected")
        self.assertEqual(result["completed"], [])
        self.assertEqual(result["domain_payload"]["completed_steps"], [])
        self.assertFalse(result["domain_payload"]["external_writes_performed"])

    def test_fixture_runs_do_not_call_write_process_or_network_surfaces(self) -> None:
        with (
            patch.object(Path, "write_text", side_effect=AssertionError("write attempted")),
            patch.object(subprocess, "run", side_effect=AssertionError("process attempted")),
            patch.object(subprocess, "Popen", side_effect=AssertionError("process attempted")),
            patch.object(socket, "create_connection", side_effect=AssertionError("network attempted")),
            patch.object(urllib.request, "urlopen", side_effect=AssertionError("network attempted")),
        ):
            for fixture_name in FIXTURE_EXPECTATIONS:
                result = RuntimeOrchestrator().execute(
                    load_request(FIXTURE_ROOT / fixture_name)
                )
                self.assertFalse(result["domain_payload"]["external_writes_performed"])

    def test_runtime_operator_documentation_exists(self) -> None:
        documentation = ROOT / "Tests" / "Runtime-Orchestrator-v1.md"

        self.assertTrue(documentation.is_file())
        text = documentation.read_text(encoding="utf-8")
        self.assertIn("Runtime Orchestrator v1", text)
        self.assertIn("no external writes", text)

    def test_runtime_ci_is_pull_request_only_and_read_only(self) -> None:
        workflow = ROOT / ".github" / "workflows" / "validate-runtime-orchestrator.yml"

        self.assertTrue(workflow.is_file())
        text = workflow.read_text(encoding="utf-8")
        self.assertIn("pull_request:", text)
        self.assertNotIn("\n  push:", text)
        self.assertIn("permissions:\n  contents: read", text)
        self.assertNotIn("contents: write", text)
        self.assertNotIn("pull-requests: write", text)


if __name__ == "__main__":
    unittest.main()
