#!/usr/bin/env python3
"""Deterministic synthetic-only Runtime Orchestrator v1."""

from __future__ import annotations

import copy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any

import yaml

from Runtime.controlled_orchestrator import (
    CANONICAL_AGENT_IDS,
    ControlledOrchestrator,
    HarnessPolicyError,
    load_workflow,
)


RUNTIME_VERSION = "1.0"
REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
PUBLISHED_WORKFLOWS = {
    "agent_reports_to_ceo_decision_queue": "Schemas/Workflows/agent-report-ceo-decision-queue.yaml",
    "customer_complaint_remediation": "Schemas/Workflows/customer-complaint-remediation.yaml",
    "marketing_crm_campaign": "Schemas/Workflows/marketing-crm-campaign.yaml",
    "shopify_to_developer_draft_pr": "Schemas/Workflows/shopify-developer-draft-pr.yaml",
    "store_anomaly_investigation": "Schemas/Workflows/store-anomaly.yaml",
}

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

TOP_LEVEL_FIELDS = {
    "runtime_version",
    "run_id",
    "agent",
    "mode",
    "requested_by",
    "requested_at",
    "business_context",
    "task",
    "evidence",
    "constraints",
    "approval_context",
}
BUSINESS_CONTEXT_REQUIRED_FIELDS = {
    "company",
    "brand",
    "scope_level",
    "department",
    "decision_owner",
    "operating_owner",
}
BUSINESS_CONTEXT_ALLOWED_FIELDS = BUSINESS_CONTEXT_REQUIRED_FIELDS | {"store_code"}
TASK_FIELDS = {
    "workflow_id",
    "objective",
    "requested_output",
    "acceptance_criteria",
    "deadline_or_review_date",
    "requested_next_action",
    "reporting_period",
    "workflow_inputs",
}
EVIDENCE_FIELDS = {
    "source_type",
    "source_name",
    "source_link_or_id",
    "data_cutoff",
    "owner",
    "confidence",
    "limitations",
}
CONSTRAINT_FIELDS = {
    "prohibited_actions",
    "privacy_classification",
    "budget_limit_or_unknown",
    "time_limit",
    "known_business_rules",
    "dry_run",
    "allow_external_writes",
}
APPROVAL_FIELDS = {
    "risk_level",
    "approval_required",
    "approval_owner",
    "approval_status",
    "approval_evidence",
}
SCOPE_LEVELS = {
    "company",
    "brand",
    "department",
    "store",
    "channel",
    "customer-case",
    "system",
}
CONFIDENCE_VALUES = {"high", "medium", "low", "unknown"}
RISK_LEVELS = {"low", "medium", "high", "critical"}
REQUIRED_PROHIBITIONS = {"external_write", "production_execution", "human_decision"}
ALLOWED_ACTION_CLASSES = {"automatic_low_risk", "prepare_only", "prohibited"}


class RuntimePolicyError(ValueError):
    """Raised when a Runtime request fails the Stage 8 safety policy."""


class RunIdCollisionError(RuntimePolicyError):
    """Raised when a run_id is reused with different canonical content."""


def _require_mapping(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise RuntimePolicyError(f"{field} must be a mapping")
    return value


def _require_exact_fields(
    value: dict[str, Any],
    required: set[str],
    allowed: set[str],
    field: str,
) -> None:
    missing = sorted(required - set(value))
    unknown = sorted(set(value) - allowed)
    if missing or unknown:
        raise RuntimePolicyError(f"{field} fields invalid: missing={missing}, unknown={unknown}")


def _is_missing(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return not value.strip()
    if isinstance(value, (list, dict)):
        return not value
    return False


def _require_nonempty_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise RuntimePolicyError(f"{field} must be a non-empty string")
    return value


def _require_nonempty_string_list(value: Any, field: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise RuntimePolicyError(f"{field} must be a non-empty list")
    if any(not isinstance(item, str) or not item.strip() for item in value):
        raise RuntimePolicyError(f"{field} must contain only non-empty strings")
    return value


def _parse_requested_at(value: Any) -> datetime:
    rendered = _require_nonempty_string(value, "requested_at")
    try:
        parsed = datetime.fromisoformat(rendered.replace("Z", "+00:00"))
    except ValueError as exc:
        raise RuntimePolicyError("requested_at must be ISO-8601") from exc
    if parsed.tzinfo is None:
        raise RuntimePolicyError("requested_at must include a timezone")
    return parsed.astimezone(timezone.utc)


class RuntimeOrchestrator:
    """Validate and execute fixed published workflows through Harness v0."""

    def __init__(self) -> None:
        self._runs: dict[str, tuple[str, dict[str, Any]]] = {}

    @staticmethod
    def _canonical_request(request: dict[str, Any]) -> str:
        if not isinstance(request, dict):
            raise RuntimePolicyError("Runtime request must be a mapping")
        _require_nonempty_string(request.get("run_id"), "run_id")
        try:
            return json.dumps(
                request,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            )
        except (TypeError, ValueError) as exc:
            raise RuntimePolicyError("Runtime request must be JSON-compatible") from exc

    @staticmethod
    def _load_published_workflow(workflow_id: str) -> tuple[dict[str, Any], str]:
        source = PUBLISHED_WORKFLOWS.get(workflow_id)
        if source is None:
            raise RuntimePolicyError("workflow_id is not in the published allowlist")
        try:
            workflow = load_workflow(REPOSITORY_ROOT / source)
        except (OSError, ValueError, yaml.YAMLError) as exc:
            raise RuntimePolicyError("published workflow could not be loaded safely") from exc
        if workflow.get("workflow_id") != workflow_id:
            raise RuntimePolicyError("published workflow ID does not match its allowlist entry")
        if workflow.get("schema_version") != "1.0" or workflow.get("workflow_version") != "1.0":
            raise RuntimePolicyError("published workflow must use schema and workflow version 1.0")
        steps = workflow.get("steps")
        if not isinstance(steps, list) or not steps:
            raise RuntimePolicyError("published workflow steps must be a non-empty list")
        for step in steps:
            if not isinstance(step, dict) or step.get("action_class") not in ALLOWED_ACTION_CLASSES:
                raise RuntimePolicyError("published workflow contains an unknown action class")
        return workflow, source

    @staticmethod
    def _expected_agent(workflow: dict[str, Any], inputs: dict[str, Any]) -> str:
        accountable = workflow.get("accountable_agent")
        if isinstance(accountable, str):
            if accountable not in CANONICAL_AGENT_IDS:
                raise RuntimePolicyError("published workflow uses a non-canonical accountable Agent")
            return accountable
        if not isinstance(accountable, dict) or accountable.get("type") != "runtime_selection":
            raise RuntimePolicyError("published workflow accountability is invalid")
        owner = inputs.get(accountable.get("input_field"))
        outcome = inputs.get(accountable.get("selection_basis"))
        mapping = accountable.get("mapping")
        allowed_values = accountable.get("allowed_values")
        if not isinstance(mapping, dict) or not isinstance(allowed_values, list):
            raise RuntimePolicyError("published runtime accountability selector is invalid")
        expected = mapping.get(outcome)
        if owner not in allowed_values or owner not in CANONICAL_AGENT_IDS or owner != expected:
            raise RuntimePolicyError("workflow owner does not match the published selection rule")
        return str(owner)

    def _validate_request(
        self, request: dict[str, Any]
    ) -> tuple[dict[str, Any], str, dict[str, Any]]:
        _require_exact_fields(request, TOP_LEVEL_FIELDS, TOP_LEVEL_FIELDS, "request")
        if request["runtime_version"] != RUNTIME_VERSION:
            raise RuntimePolicyError("runtime_version must be 1.0")
        if request["mode"] != "validate":
            raise RuntimePolicyError("Runtime Orchestrator v1 accepts only mode=validate")
        _require_nonempty_string(request["run_id"], "run_id")
        _require_nonempty_string(request["requested_by"], "requested_by")
        _parse_requested_at(request["requested_at"])
        if request["agent"] not in CANONICAL_AGENT_IDS:
            raise RuntimePolicyError("agent must use a canonical Agent ID")

        context = _require_mapping(request["business_context"], "business_context")
        _require_exact_fields(
            context,
            BUSINESS_CONTEXT_REQUIRED_FIELDS,
            BUSINESS_CONTEXT_ALLOWED_FIELDS,
            "business_context",
        )
        if context["company"] != "汇沣电商":
            raise RuntimePolicyError("only company=汇沣电商 is accepted; 六合通 mixing is prohibited")
        if context["brand"] not in {"BUW", "PC"}:
            raise RuntimePolicyError("brand must be BUW or PC; shared and unknown are rejected")
        if context["scope_level"] not in SCOPE_LEVELS:
            raise RuntimePolicyError("scope_level is invalid")
        for field in ("department", "decision_owner", "operating_owner"):
            _require_nonempty_string(context[field], f"business_context.{field}")
        if context["scope_level"] == "store":
            _require_nonempty_string(context.get("store_code"), "business_context.store_code")
        elif "store_code" in context:
            raise RuntimePolicyError("store_code is allowed only for store scope")

        task = _require_mapping(request["task"], "task")
        _require_exact_fields(task, TASK_FIELDS, TASK_FIELDS, "task")
        for field in (
            "workflow_id",
            "objective",
            "requested_output",
            "deadline_or_review_date",
            "requested_next_action",
            "reporting_period",
        ):
            _require_nonempty_string(task[field], f"task.{field}")
        _require_nonempty_string_list(
            task["acceptance_criteria"], "task.acceptance_criteria"
        )
        inputs = _require_mapping(task["workflow_inputs"], "task.workflow_inputs")
        if "brand" in inputs or "evidence_links" in inputs:
            raise RuntimePolicyError("brand and evidence_links must come from the Runtime envelope")

        evidence = request["evidence"]
        if not isinstance(evidence, list) or not evidence:
            raise RuntimePolicyError("evidence must be a non-empty list")
        for index, item in enumerate(evidence):
            item = _require_mapping(item, f"evidence[{index}]")
            _require_exact_fields(item, EVIDENCE_FIELDS, EVIDENCE_FIELDS, f"evidence[{index}]")
            for field in EVIDENCE_FIELDS - {"confidence"}:
                _require_nonempty_string(item[field], f"evidence[{index}].{field}")
            if item["source_type"] != "synthetic":
                raise RuntimePolicyError("every evidence item must be synthetic")
            if not item["source_link_or_id"].startswith("synthetic://"):
                raise RuntimePolicyError("every evidence identifier must use synthetic://")
            if item["confidence"] not in CONFIDENCE_VALUES:
                raise RuntimePolicyError("evidence confidence is invalid")

        constraints = _require_mapping(request["constraints"], "constraints")
        _require_exact_fields(constraints, CONSTRAINT_FIELDS, CONSTRAINT_FIELDS, "constraints")
        if constraints["privacy_classification"] != "synthetic":
            raise RuntimePolicyError("privacy_classification must be synthetic")
        if constraints["dry_run"] is not True:
            raise RuntimePolicyError("dry_run must be true")
        if constraints["allow_external_writes"] is not False:
            raise RuntimePolicyError("allow_external_writes must be false")
        prohibited = _require_nonempty_string_list(
            constraints["prohibited_actions"], "constraints.prohibited_actions"
        )
        if not REQUIRED_PROHIBITIONS.issubset(set(prohibited)):
            raise RuntimePolicyError("prohibited_actions must include every Stage 8 safety boundary")
        if _is_missing(constraints["budget_limit_or_unknown"]):
            raise RuntimePolicyError("budget_limit_or_unknown is required")
        _require_nonempty_string(constraints["time_limit"], "constraints.time_limit")
        _require_nonempty_string_list(
            constraints["known_business_rules"], "constraints.known_business_rules"
        )

        approval = _require_mapping(request["approval_context"], "approval_context")
        _require_exact_fields(approval, APPROVAL_FIELDS, APPROVAL_FIELDS, "approval_context")
        if approval["risk_level"] not in RISK_LEVELS:
            raise RuntimePolicyError("approval risk_level is invalid")
        if not isinstance(approval["approval_required"], bool):
            raise RuntimePolicyError("approval_required must be boolean")
        if approval["approval_evidence"] != []:
            raise RuntimePolicyError("Runtime v1 does not accept input approval evidence")
        if approval["approval_required"]:
            if approval["approval_status"] != "pending":
                raise RuntimePolicyError("required approval must remain pending")
            _require_nonempty_string(approval["approval_owner"], "approval_context.approval_owner")
        elif approval["approval_status"] != "not_required" or approval["approval_owner"] is not None:
            raise RuntimePolicyError("non-required approval must use not_required and no owner")

        workflow, source = self._load_published_workflow(task["workflow_id"])
        published_fields = set(workflow.get("required_inputs", [])) | set(
            workflow.get("optional_inputs", [])
        )
        adapter_fields = {"brand", "evidence_links"}
        unknown_inputs = sorted(set(inputs) - (published_fields - adapter_fields))
        if unknown_inputs:
            raise RuntimePolicyError(f"workflow_inputs contains unpublished fields: {unknown_inputs}")
        if "store_code" in inputs and inputs["store_code"] != context.get("store_code"):
            raise RuntimePolicyError("workflow store_code conflicts with business_context")
        adapted_inputs = {
            **inputs,
            "brand": context["brand"],
            "evidence_links": [item["source_link_or_id"] for item in evidence],
        }
        missing_inputs = sorted(
            field
            for field in workflow.get("required_inputs", [])
            if field not in adapted_inputs or _is_missing(adapted_inputs[field])
        )
        if missing_inputs:
            raise RuntimePolicyError(f"required workflow inputs are missing: {missing_inputs}")
        expected_agent = self._expected_agent(workflow, adapted_inputs)
        if request["agent"] != expected_agent:
            raise RuntimePolicyError("request agent does not match workflow accountability")
        return workflow, source, adapted_inputs

    @staticmethod
    def _execute_once(
        request: dict[str, Any],
        fingerprint: str,
        workflow: dict[str, Any],
        source: str,
        adapted_inputs: dict[str, Any],
    ) -> dict[str, Any]:
        context = request["business_context"]
        task = request["task"]
        constraints = request["constraints"]
        business_entity = f"{context['brand']}:{context.get('store_code', context['scope_level'])}"
        payload = {
            "metadata": {
                "run_id": request["run_id"],
                "company": context["company"],
                "data_classification": constraints["privacy_classification"],
                "dry_run": constraints["dry_run"],
                "allow_external_writes": constraints["allow_external_writes"],
                "trigger_event_id": request["run_id"],
                "business_entity": business_entity,
                "period": task["reporting_period"],
            },
            "inputs": adapted_inputs,
        }
        fixed_time = _parse_requested_at(request["requested_at"])
        try:
            result = ControlledOrchestrator(now=lambda: fixed_time).run(workflow, payload)
        except (HarnessPolicyError, ValueError) as exc:
            raise RuntimePolicyError("Controlled Harness rejected the adapted request") from exc
        if set(result) != RUNTIME_OUTPUT_FIELDS:
            raise RuntimePolicyError("Controlled Harness returned an incompatible Runtime envelope")
        domain_payload = result.get("domain_payload")
        if not isinstance(domain_payload, dict):
            raise RuntimePolicyError("Controlled Harness domain_payload is invalid")
        if domain_payload.get("external_writes_performed") is not False:
            raise RuntimePolicyError("Controlled Harness did not prove the no-write boundary")
        domain_payload["runtime_orchestrator_version"] = RUNTIME_VERSION
        domain_payload["request_fingerprint"] = fingerprint
        domain_payload["workflow_source"] = source
        return result

    def execute(self, request: dict[str, Any]) -> dict[str, Any]:
        """Validate and execute one deterministic synthetic dry-run."""
        canonical_request = self._canonical_request(request)
        fingerprint = hashlib.sha256(canonical_request.encode("utf-8")).hexdigest()
        normalized = json.loads(canonical_request)
        run_id = normalized["run_id"]
        previous = self._runs.get(run_id)
        if previous is not None:
            previous_fingerprint, previous_result = previous
            if previous_fingerprint != fingerprint:
                raise RunIdCollisionError(
                    "run_id already exists with different canonical request"
                )
            return copy.deepcopy(previous_result)
        workflow, source, adapted_inputs = self._validate_request(normalized)
        result = self._execute_once(
            normalized,
            fingerprint,
            workflow,
            source,
            adapted_inputs,
        )
        self._runs[run_id] = (fingerprint, copy.deepcopy(result))
        return copy.deepcopy(result)
