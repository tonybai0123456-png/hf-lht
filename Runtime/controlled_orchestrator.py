#!/usr/bin/env python3
"""Synthetic-only, no-write Controlled Orchestrator Harness v0."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Callable

import yaml

CANONICAL_AGENT_IDS = {
    "CEO",
    "Marketing",
    "Retail",
    "CRM",
    "Shopify",
    "Developer",
    "Data",
    "CustomerService",
}


class HarnessPolicyError(ValueError):
    """Raised when a run violates the synthetic-only safety boundary."""


def load_workflow(path: Path | str) -> dict[str, Any]:
    """Load one split workflow document."""
    document = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(document, dict) or not document.get("workflow_id"):
        raise ValueError("workflow document must be a mapping with workflow_id")
    return document


def load_payload(path: Path | str) -> dict[str, Any]:
    """Load a YAML or JSON harness input payload."""
    document = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(document, dict):
        raise ValueError("input payload must be a mapping")
    return document


class ControlledOrchestrator:
    """Interpret workflow steps without invoking tools or external systems."""

    def __init__(self, now: Callable[[], datetime] | None = None) -> None:
        self._now = now or (lambda: datetime.now(timezone.utc))
        self._seen_idempotency_keys: set[str] = set()

    def _timestamp(self) -> str:
        return self._now().astimezone(timezone.utc).isoformat().replace("+00:00", "Z")

    @staticmethod
    def _enforce_policy(payload: dict[str, Any]) -> None:
        metadata = payload.get("metadata", {})
        inputs = payload.get("inputs", {})
        if not isinstance(metadata, dict) or not isinstance(inputs, dict):
            raise HarnessPolicyError("metadata and inputs must be mappings")
        if not metadata.get("run_id"):
            raise HarnessPolicyError("metadata.run_id is required")
        if metadata.get("company") != "汇沣电商":
            raise HarnessPolicyError("only company=汇沣电商 is accepted; cross-company mixing is prohibited")
        if metadata.get("data_classification") != "synthetic":
            raise HarnessPolicyError("only data_classification=synthetic is accepted")
        if metadata.get("dry_run") is not True:
            raise HarnessPolicyError("dry_run must be true")
        if metadata.get("allow_external_writes") is not False:
            raise HarnessPolicyError("allow_external_writes must be false")
        brand = inputs.get("brand")
        if brand == "shared":
            if metadata.get("shared_brand_approved") is not True:
                raise HarnessPolicyError("shared brand scope requires explicit approval")
            breakdown = inputs.get("brand_breakdown")
            if not isinstance(breakdown, dict) or not {"BUW", "PC"}.issubset(breakdown):
                raise HarnessPolicyError("shared brand scope requires BUW and PC breakdown")
        elif brand is not None and brand not in {"BUW", "PC"}:
            raise HarnessPolicyError("brand must be BUW or PC unless an approved shared view is declared")

    @staticmethod
    def _resolve_accountable_agent(workflow: dict[str, Any], payload: dict[str, Any]) -> str:
        accountable = workflow.get("accountable_agent")
        if isinstance(accountable, str):
            if accountable not in CANONICAL_AGENT_IDS:
                raise HarnessPolicyError("accountable_agent must use a canonical Agent ID")
            return accountable
        if not isinstance(accountable, dict) or accountable.get("type") != "runtime_selection":
            raise HarnessPolicyError("accountable_agent must be canonical or a runtime selector")
        inputs = payload["inputs"]
        owner = inputs.get(str(accountable.get("input_field")))
        outcome = inputs.get(str(accountable.get("selection_basis")))
        expected = accountable.get("mapping", {}).get(outcome)
        if owner not in accountable.get("allowed_values", []) or owner not in CANONICAL_AGENT_IDS:
            raise HarnessPolicyError("workflow_owner_agent is not allowed")
        if expected != owner:
            raise HarnessPolicyError("workflow_owner_agent does not match primary_business_outcome")
        return str(owner)

    @staticmethod
    def _idempotency_key(workflow: dict[str, Any], payload: dict[str, Any]) -> str:
        metadata = payload["metadata"]
        return ":".join(
            [
                str(workflow["workflow_id"]),
                str(metadata.get("business_entity", "unknown")),
                str(metadata.get("period", "unknown")),
                str(metadata.get("trigger_event_id", "unknown")),
            ]
        )

    def _audit(self, event: str, status: str, **details: Any) -> dict[str, Any]:
        return {"at": self._timestamp(), "event": event, "status": status, **details}

    @staticmethod
    def _handoff(
        workflow: dict[str, Any],
        payload: dict[str, Any],
        from_agent: str,
        to_agent: str,
        step: dict[str, Any],
    ) -> dict[str, Any]:
        inputs = payload["inputs"]
        metadata = payload["metadata"]
        return {
            "from_agent": from_agent,
            "to_agent": to_agent,
            "situation": inputs.get("anomaly_type") or workflow.get("trigger", {}).get("type"),
            "requested_outcome": f"complete workflow step {step['id']}",
            "evidence": inputs.get("evidence_links", []),
            "scope_in": workflow.get("business_outcome"),
            "scope_out": ["external_write", "production_execution", "human_decision"],
            "acceptance_criteria": workflow.get("completion_conditions", []),
            "risk_level": "low",
            "approval_required": step.get("action_class") == "prepare_only",
            "deadline_or_review_date": inputs.get("deadline_or_review_date"),
            "data_cutoff": metadata.get("period"),
            "confidence": "medium",
            "originating_run_id": metadata["run_id"],
        }

    @staticmethod
    def _approval_owners(step: dict[str, Any]) -> list[str]:
        owner = step.get("approval_owner")
        if isinstance(owner, str) and owner:
            return [owner]
        if isinstance(owner, list) and owner:
            return [str(item) for item in owner]
        return ["Tony", "Stone"]

    def run(self, workflow: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
        """Simulate one workflow until completion or the first safety gate."""
        self._enforce_policy(payload)
        inputs = payload.get("inputs", {})
        if not isinstance(inputs, dict):
            raise ValueError("payload.inputs must be a mapping")

        missing = [field for field in workflow.get("required_inputs", []) if field not in inputs]
        accountable_agent = self._resolve_accountable_agent(workflow, payload) if not missing else (
            workflow.get("accountable_agent")
            if isinstance(workflow.get("accountable_agent"), str)
            else "CEO"
        )
        key = self._idempotency_key(workflow, payload)
        metadata = payload["metadata"]
        evidence_links = list(inputs.get("evidence_links", []))
        domain_payload: dict[str, Any] = {
            "harness_version": "0.1.0",
            "workflow_id": workflow["workflow_id"],
            "idempotency_key": key,
            "dry_run": True,
            "synthetic_only": True,
            "external_writes_performed": False,
            "duplicate_run": False,
            "completed_steps": [],
            "pending_step": None,
            "audit_log": [],
        }
        base: dict[str, Any] = {
            "run_id": metadata["run_id"],
            "agent": accountable_agent,
            "status": "partial",
            "reporting_period": {
                "period": metadata.get("period"),
                "data_updated_through": metadata.get("period"),
            },
            "executive_status": "Yellow",
            "summary": "Controlled synthetic workflow simulation is in progress.",
            "kpi_snapshot": {
                "items": [],
                "not_applicable_reason": "Synthetic control-flow validation does not calculate business KPIs.",
            },
            "completed": [],
            "in_progress": [],
            "business_impact": "Synthetic-only validation; no external or production effect.",
            "findings": [],
            "recommended_actions": [],
            "decisions_required": [],
            "risks_and_exceptions": [],
            "evidence_used": evidence_links,
            "confidence": "medium",
            "missing_information": [],
            "approval_request": {},
            "handoffs": [],
            "blockers": [],
            "next_priorities": [],
            "next_review": None,
            "domain_payload": domain_payload,
        }

        if key in self._seen_idempotency_keys:
            base["status"] = "rejected"
            base["executive_status"] = "Red"
            base["summary"] = "Duplicate idempotency key rejected without rerunning steps."
            domain_payload["duplicate_run"] = True
            domain_payload["audit_log"].append(self._audit("duplicate_run_rejected", "rejected"))
            base["risks_and_exceptions"].append(
                {
                    "risk": "duplicate_run",
                    "business_impact": "A duplicate run could repeat a workflow action.",
                    "confidence": "high",
                    "evidence": key,
                    "recommended_action": "Review the existing run instead of rerunning it.",
                }
            )
            return base
        self._seen_idempotency_keys.add(key)

        if missing:
            base["status"] = "blocked"
            base["executive_status"] = "Red"
            base["summary"] = "Required workflow inputs are missing; no steps were simulated."
            base["missing_information"] = missing
            base["blockers"] = missing
            base["next_priorities"] = [f"Provide required input: {field}" for field in missing]
            domain_payload["audit_log"].append(
                self._audit("required_inputs_missing", "blocked", missing_inputs=missing)
            )
            return base

        domain_payload["audit_log"].append(self._audit("run_started", "partial"))
        previous_owner = accountable_agent
        for step in workflow.get("steps", []):
            step_id = str(step["id"])
            owner = str(step.get("owner", accountable_agent))
            if owner not in CANONICAL_AGENT_IDS:
                raise HarnessPolicyError(f"step owner must use a canonical Agent ID: {owner}")
            action_class = step.get("action_class")

            if owner != previous_owner:
                base["handoffs"].append(
                    self._handoff(workflow, payload, previous_owner, owner, step)
                )
                domain_payload["audit_log"].append(
                    self._audit("handoff_prepared", "partial", step_id=step_id, to_agent=owner)
                )
            previous_owner = owner

            if action_class == "prohibited":
                base["status"] = "rejected"
                base["executive_status"] = "Red"
                base["summary"] = f"Prohibited step {step_id} was rejected without execution."
                domain_payload["pending_step"] = step_id
                domain_payload["audit_log"].append(
                    self._audit("prohibited_step_rejected", "rejected", step_id=step_id)
                )
                return base

            if action_class == "prepare_only":
                base["status"] = "needs_approval"
                base["summary"] = f"Workflow paused before {step_id}; an approval package was prepared."
                domain_payload["pending_step"] = step_id
                approval_owners = self._approval_owners(step)
                base["approval_request"] = {
                    "workflow_id": workflow["workflow_id"],
                    "step_id": step_id,
                    "approval_owners": approval_owners,
                    "approval_status": "pending",
                    "requested_action": step_id,
                    "reason": "prepare_only steps cannot execute in Harness v0",
                    "evidence_links": evidence_links,
                    "synthetic_only": True,
                    "execution_performed": False,
                }
                base["decisions_required"] = [
                    {
                        "decision": f"Approve or reject {step_id}",
                        "options": ["approve", "reject", "request_more_evidence"],
                        "recommended_option": "request_more_evidence" if not evidence_links else "review",
                        "latest_decision_time": inputs.get("deadline_or_review_date"),
                    }
                ]
                base["in_progress"] = [
                    {
                        "item": step_id,
                        "owner": owner,
                        "target_date": inputs.get("deadline_or_review_date"),
                        "current_status": "awaiting_human_approval",
                    }
                ]
                base["next_priorities"] = [f"Obtain explicit approval from {', '.join(approval_owners)}"]
                domain_payload["audit_log"].append(
                    self._audit("approval_package_prepared", "needs_approval", step_id=step_id)
                )
                return base

            if action_class != "automatic_low_risk":
                raise ValueError(f"unknown action_class for {step_id}: {action_class}")
            domain_payload["completed_steps"].append(step_id)
            base["completed"].append({"item": step_id, "evidence_links": evidence_links})
            domain_payload["audit_log"].append(
                self._audit("step_simulated", "partial", step_id=step_id, owner=owner)
            )

        base["status"] = "completed"
        base["executive_status"] = "Green"
        base["summary"] = "All low-risk workflow steps were simulated successfully."
        domain_payload["audit_log"].append(self._audit("run_completed", "completed"))
        return base


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workflow", required=True, type=Path)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    try:
        result = ControlledOrchestrator().run(load_workflow(args.workflow), load_payload(args.input))
    except (HarnessPolicyError, OSError, ValueError, yaml.YAMLError) as exc:
        print(f"CONTROLLED ORCHESTRATOR REJECTED: {exc}")
        return 2

    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
