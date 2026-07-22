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
HANDOFF_FIELDS = {
    "from_agent",
    "to_agent",
    "situation",
    "requested_outcome",
    "evidence",
    "scope_in",
    "scope_out",
    "acceptance_criteria",
    "risk_level",
    "approval_required",
    "deadline_or_review_date",
    "data_cutoff",
    "confidence",
    "originating_run_id",
}


def synthetic_payload() -> dict:
    return {
        "metadata": {
            "run_id": "SYN-RET-0001",
            "company": "汇沣电商",
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
        self.assertTrue(RUNTIME_OUTPUT_FIELDS.issubset(result))
        self.assertEqual(result["agent"], "Retail")
        self.assertEqual(
            result["domain_payload"]["completed_steps"],
            ["validate_scope", "request_data_validation"],
        )
        self.assertEqual(result["domain_payload"]["pending_step"], "assign_supervisor_response")
        self.assertEqual(result["approval_request"]["approval_owners"], ["李涛"])
        self.assertFalse(result["domain_payload"]["external_writes_performed"])
        self.assertTrue(result["handoffs"])
        self.assertGreaterEqual(len(result["domain_payload"]["audit_log"]), 3)

    def test_handoffs_use_runtime_contract_and_exclude_human_approvers(self) -> None:
        result = ControlledOrchestrator().run(load_workflow(WORKFLOW_PATH), synthetic_payload())

        self.assertEqual([item["to_agent"] for item in result["handoffs"]], ["Data", "Retail"])
        self.assertTrue(all(set(item) == HANDOFF_FIELDS for item in result["handoffs"]))
        self.assertTrue(all(item["risk_level"] in {"low", "medium", "high", "critical"} for item in result["handoffs"]))
        self.assertTrue(all(item["confidence"] in {"high", "medium", "low", "unknown"} for item in result["handoffs"]))
        self.assertNotIn("李涛", {item["to_agent"] for item in result["handoffs"]})
        self.assertEqual(result["approval_request"]["approval_owners"], ["李涛"])

    def test_missing_required_input_blocks_without_steps(self) -> None:
        payload = synthetic_payload()
        del payload["inputs"]["store_code"]

        result = ControlledOrchestrator().run(load_workflow(WORKFLOW_PATH), payload)

        self.assertEqual(result["status"], "blocked")
        self.assertEqual(result["missing_information"], ["store_code"])
        self.assertEqual(result["completed"], [])

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
        self.assertTrue(second["domain_payload"]["duplicate_run"])
        self.assertEqual(second["completed"], [])

    def test_prohibited_step_is_never_executed(self) -> None:
        workflow = load_workflow(WORKFLOW_PATH)
        workflow["steps"][0]["action_class"] = "prohibited"

        result = ControlledOrchestrator().run(workflow, synthetic_payload())

        self.assertEqual(result["status"], "rejected")
        self.assertEqual(result["domain_payload"]["pending_step"], "validate_scope")
        self.assertEqual(result["completed"], [])
        self.assertFalse(result["domain_payload"]["external_writes_performed"])

    def test_repository_fixture_runs_end_to_end(self) -> None:
        result = ControlledOrchestrator().run(
            load_workflow(WORKFLOW_PATH),
            load_payload(FIXTURE_PATH),
        )

        self.assertEqual(result["domain_payload"]["workflow_id"], "store_anomaly_investigation")
        self.assertEqual(result["status"], "needs_approval")
        self.assertEqual(result["approval_request"]["approval_owners"], ["李涛"])

    def test_cross_company_input_is_rejected(self) -> None:
        payload = synthetic_payload()
        payload["metadata"]["company"] = "六合通"

        with self.assertRaises(HarnessPolicyError):
            ControlledOrchestrator().run(load_workflow(WORKFLOW_PATH), payload)

    def test_shared_brand_requires_explicit_approval_and_breakdown(self) -> None:
        payload = synthetic_payload()
        payload["inputs"]["brand"] = "shared"

        with self.assertRaises(HarnessPolicyError):
            ControlledOrchestrator().run(load_workflow(WORKFLOW_PATH), payload)

    def test_marketing_crm_resolves_one_owner_from_primary_outcome(self) -> None:
        workflow = load_workflow(ROOT / "Schemas" / "Workflows" / "marketing-crm-campaign.yaml")
        payload = synthetic_payload()
        payload["inputs"] = {
            "brand": "BUW",
            "objective": "synthetic recall design",
            "audience": "synthetic segment",
            "channel": "email_draft_only",
            "market_scope": "US",
            "period": "2026-07-21",
            "evidence_links": ["synthetic://campaign/001"],
            "primary_business_outcome": "lifecycle_or_recall",
            "workflow_owner_agent": "CRM",
        }

        result = ControlledOrchestrator().run(workflow, payload)

        self.assertEqual(result["agent"], "CRM")
        self.assertEqual(result["status"], "needs_approval")

    def test_marketing_crm_rejects_owner_outcome_mismatch(self) -> None:
        workflow = load_workflow(ROOT / "Schemas" / "Workflows" / "marketing-crm-campaign.yaml")
        payload = synthetic_payload()
        payload["inputs"] = {
            "brand": "BUW",
            "objective": "synthetic recall design",
            "audience": "synthetic segment",
            "channel": "email_draft_only",
            "market_scope": "US",
            "period": "2026-07-21",
            "evidence_links": ["synthetic://campaign/002"],
            "primary_business_outcome": "lifecycle_or_recall",
            "workflow_owner_agent": "Marketing",
        }

        with self.assertRaises(HarnessPolicyError):
            ControlledOrchestrator().run(workflow, payload)

    def test_unknown_approval_owner_defaults_to_tony_and_stone(self) -> None:
        workflow = load_workflow(ROOT / "Schemas" / "Workflows" / "marketing-crm-campaign.yaml")
        payload = synthetic_payload()
        payload["inputs"] = {
            "brand": "BUW",
            "objective": "synthetic acquisition draft",
            "audience": "synthetic segment",
            "channel": "draft_only",
            "market_scope": "US",
            "period": "2026-07-21",
            "evidence_links": ["synthetic://campaign/003"],
            "primary_business_outcome": "acquisition_or_content",
            "workflow_owner_agent": "Marketing",
        }

        result = ControlledOrchestrator().run(workflow, payload)

        self.assertEqual(result["status"], "needs_approval")
        self.assertEqual(result["approval_request"]["approval_owners"], ["Tony", "Stone"])


if __name__ == "__main__":
    unittest.main()
