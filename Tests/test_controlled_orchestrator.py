#!/usr/bin/env python3
"""Behavior tests for the synthetic-only Controlled Orchestrator Harness v0."""

from pathlib import Path
import unittest

from Runtime.controlled_orchestrator import (
    ControlledOrchestrator,
    HarnessPolicyError,
    load_payload,
    load_workflow,
)


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_PATH = ROOT / "Schemas" / "Workflows" / "store-anomaly.yaml"
FIXTURE_PATH = ROOT / "Tests" / "Fixtures" / "store-anomaly-synthetic-input.yaml"


def synthetic_payload() -> dict:
    return {
        "metadata": {
            "data_classification": "synthetic",
            "dry_run": True,
            "allow_external_writes": False,
            "trigger_event_id": "synthetic-store-alert-001",
            "business_entity": "BUW:G0011",
            "period": "2026-07-19",
        },
        "inputs": {
            "brand": "BUW",
            "store_code": "G0011",
            "period": "2026-07-19",
            "anomaly_type": "settlement_delay_and_reception_order",
            "evidence_links": ["synthetic://store/G0011/alert/001"],
            "current_actions": ["synthetic store report recorded"],
        },
    }


class ControlledOrchestratorTests(unittest.TestCase):
    def test_harness_module_exists(self) -> None:
        self.assertTrue(
            (ROOT / "Runtime" / "controlled_orchestrator.py").is_file(),
            "Controlled Orchestrator Harness module is missing",
        )

    def test_valid_synthetic_run_stops_at_approval_gate(self) -> None:
        runner = ControlledOrchestrator()
        result = runner.run(load_workflow(WORKFLOW_PATH), synthetic_payload())

        self.assertEqual(result["status"], "needs_approval")
        self.assertEqual(
            result["completed_steps"],
            ["validate_scope", "request_data_validation"],
        )
        self.assertEqual(result["pending_step"], "assign_supervisor_response")
        self.assertEqual(result["approval_package"]["requested_approver"], "李涛")
        self.assertFalse(result["external_writes_performed"])
        self.assertTrue(result["handoff_packages"])
        self.assertGreaterEqual(len(result["audit_log"]), 3)

    def test_missing_required_input_blocks_without_steps(self) -> None:
        payload = synthetic_payload()
        del payload["inputs"]["store_code"]

        result = ControlledOrchestrator().run(load_workflow(WORKFLOW_PATH), payload)

        self.assertEqual(result["status"], "blocked")
        self.assertEqual(result["missing_inputs"], ["store_code"])
        self.assertEqual(result["completed_steps"], [])

    def test_non_synthetic_input_is_rejected_by_policy(self) -> None:
        payload = synthetic_payload()
        payload["metadata"]["data_classification"] = "production"

        with self.assertRaises(HarnessPolicyError):
            ControlledOrchestrator().run(load_workflow(WORKFLOW_PATH), payload)

    def test_external_write_request_is_rejected_by_policy(self) -> None:
        payload = synthetic_payload()
        payload["metadata"]["allow_external_writes"] = True

        with self.assertRaises(HarnessPolicyError):
            ControlledOrchestrator().run(load_workflow(WORKFLOW_PATH), payload)

    def test_duplicate_idempotency_key_does_not_rerun(self) -> None:
        runner = ControlledOrchestrator()
        workflow = load_workflow(WORKFLOW_PATH)
        first = runner.run(workflow, synthetic_payload())
        second = runner.run(workflow, synthetic_payload())

        self.assertEqual(first["status"], "needs_approval")
        self.assertEqual(second["status"], "rejected")
        self.assertTrue(second["duplicate_run"])
        self.assertEqual(second["completed_steps"], [])

    def test_prohibited_step_is_never_executed(self) -> None:
        workflow = load_workflow(WORKFLOW_PATH)
        workflow["steps"][0]["action_class"] = "prohibited"

        result = ControlledOrchestrator().run(workflow, synthetic_payload())

        self.assertEqual(result["status"], "rejected")
        self.assertEqual(result["pending_step"], "validate_scope")
        self.assertEqual(result["completed_steps"], [])
        self.assertFalse(result["external_writes_performed"])

    def test_repository_fixture_runs_end_to_end(self) -> None:
        result = ControlledOrchestrator().run(
            load_workflow(WORKFLOW_PATH),
            load_payload(FIXTURE_PATH),
        )

        self.assertEqual(result["workflow_id"], "store_anomaly_investigation")
        self.assertEqual(result["status"], "needs_approval")
        self.assertEqual(result["approval_package"]["requested_approver"], "李涛")


if __name__ == "__main__":
    unittest.main()
