#!/usr/bin/env python3
"""Validate AIOS Workflow Schema v1 and split workflow instances."""

from __future__ import annotations

import copy
import sys
from pathlib import Path
from typing import Any

import yaml

EXPECTED_IDS = {
    "store_anomaly_investigation",
    "customer_complaint_remediation",
    "shopify_to_developer_draft_pr",
    "marketing_crm_campaign",
    "agent_reports_to_ceo_decision_queue",
}
EXPECTED_STATUSES = {"completed", "partial", "blocked", "needs_approval", "escalated", "rejected"}
EXPECTED_ACTIONS = {"automatic_low_risk", "prepare_only", "prohibited"}


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def validate_contract(contract: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    require(contract.get("kind") == "AIOSWorkflowSchema", "contract.kind is invalid", errors)
    wc = contract.get("workflow_contract", {})
    require(set(wc.get("runtime_status_enum", [])) == EXPECTED_STATUSES, "runtime status enum is incomplete", errors)
    require(set(wc.get("action_class_enum", [])) == EXPECTED_ACTIONS, "action class enum is incomplete", errors)
    rules = wc.get("rules", {})
    require(rules.get("single_accountable_agent") is True, "single accountable rule is not enabled", errors)
    require(set(rules.get("missing_required_input_status", [])) == {"blocked", "partial"}, "missing-input behavior is invalid", errors)
    require(rules.get("prepare_only_requires_approval_package") is True, "prepare-only approval-package rule is not enabled", errors)
    require(rules.get("prohibited_never_executes") is True, "prohibited-action rule is not enabled", errors)
    require(rules.get("approval_transition_must_be_explicit") is True, "explicit approval-transition rule is not enabled", errors)
    require(wc.get("retry_policy", {}).get("max_attempts", 0) >= 1, "retry policy is missing", errors)
    require(wc.get("timeout_policy", {}).get("stale_status") == "escalated", "stale workflow handling is invalid", errors)
    idem = wc.get("idempotency", {})
    require(idem.get("required") is True and "{workflow_id}" in idem.get("key_template", ""), "idempotency contract is invalid", errors)
    require(bool(wc.get("audit", {}).get("required_fields")), "audit contract is missing", errors)
    return errors


def validate_workflow(workflow: dict[str, Any], contract: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    wid = workflow.get("workflow_id", "<unknown>")
    required = set(contract["workflow_contract"].get("required_fields", []))
    missing = sorted(required - workflow.keys())
    require(not missing, f"{wid}: missing fields: {', '.join(missing)}", errors)
    require(isinstance(workflow.get("accountable_agent"), str) and bool(workflow["accountable_agent"].strip()), f"{wid}: accountable_agent must be one non-empty string", errors)
    require(isinstance(workflow.get("required_inputs"), list) and bool(workflow["required_inputs"]), f"{wid}: required_inputs must be non-empty", errors)

    steps = workflow.get("steps", [])
    require(isinstance(steps, list) and bool(steps), f"{wid}: steps are missing", errors)
    step_ids: set[str] = set()
    for step in steps if isinstance(steps, list) else []:
        sid = step.get("id")
        require(isinstance(sid, str) and bool(sid), f"{wid}: step id is missing", errors)
        require(sid not in step_ids, f"{wid}: duplicate step id {sid}", errors)
        step_ids.add(sid)
        require(step.get("action_class") in EXPECTED_ACTIONS, f"{wid}: invalid action class in {sid}", errors)

    transitions = workflow.get("transitions", [])
    require(isinstance(transitions, list) and bool(transitions), f"{wid}: transitions are missing", errors)
    for transition in transitions if isinstance(transitions, list) else []:
        require(transition.get("from") in EXPECTED_STATUSES and transition.get("to") in EXPECTED_STATUSES, f"{wid}: invalid transition status", errors)
        require(bool(transition.get("when")), f"{wid}: transition condition is missing", errors)

    gates = workflow.get("approval_gates", [])
    require(isinstance(gates, list), f"{wid}: approval_gates must be a list", errors)
    if any(step.get("action_class") == "prepare_only" for step in steps):
        require(bool(gates), f"{wid}: prepare-only step has no approval gate", errors)
    for gate in gates if isinstance(gates, list) else []:
        require(gate.get("output") == "approval_package", f"{wid}: approval gate output must be approval_package", errors)
        require(bool(gate.get("approvers")), f"{wid}: approval gate has no approver", errors)

    require(bool(workflow.get("handoff_contract", {}).get("required_fields")), f"{wid}: handoff fields are missing", errors)
    require(bool(workflow.get("evidence_requirements")), f"{wid}: evidence requirements are missing", errors)
    require(bool(workflow.get("completion_conditions")), f"{wid}: completion conditions are missing", errors)
    require(workflow.get("audit", {}).get("enabled") is True, f"{wid}: audit is not enabled", errors)

    if wid == "store_anomaly_investigation":
        notes = " ".join(str(step.get("notes", "")) for step in steps)
        require("李涛" in notes and "动态派遣" in notes, f"{wid}: dynamic supervisor dispatch fact is missing", errors)
        require(any(step.get("escalate_to") == "Stone" for step in steps), f"{wid}: escalation to Stone is missing", errors)
    return errors


def synthetic_negative_tests(contract: dict[str, Any], workflow: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    cases = []
    missing_owner = copy.deepcopy(workflow)
    missing_owner["accountable_agent"] = ""
    cases.append(("missing accountable owner", missing_owner))
    missing_inputs = copy.deepcopy(workflow)
    missing_inputs["required_inputs"] = []
    cases.append(("missing required inputs", missing_inputs))
    bad_gate = copy.deepcopy(workflow)
    if bad_gate.get("approval_gates"):
        bad_gate["approval_gates"][0]["output"] = "invalid_output"
        cases.append(("invalid approval output", bad_gate))
    bad_transition = copy.deepcopy(workflow)
    bad_transition["transitions"][0]["to"] = "unknown"
    cases.append(("invalid transition", bad_transition))
    for name, mutated in cases:
        if not validate_workflow(mutated, contract):
            failures.append(f"synthetic negative case did not fail: {name}")
    return failures


def load_yaml(path: Path) -> Any:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def main() -> int:
    schema_path = Path(sys.argv[1] if len(sys.argv) > 1 else "Schemas/AIOS-Workflow-Schema-v1.yaml")
    split_dir = Path("Schemas/Workflows")
    try:
        documents = list(yaml.safe_load_all(schema_path.read_text(encoding="utf-8")))
        split_paths = sorted(split_dir.glob("*.yaml"))
        split_workflows = [load_yaml(path) for path in split_paths]
    except (OSError, yaml.YAMLError) as exc:
        print(f"FAILED: cannot parse schema files: {exc}")
        return 2

    errors: list[str] = []
    require(len(documents) == 6, "schema must contain one contract and five workflows", errors)
    require(len(split_workflows) == 5, "split workflow directory must contain five YAML files", errors)
    if not documents or not isinstance(documents[0], dict):
        print("FAILED: contract document is missing")
        return 1

    contract = documents[0]
    embedded = [doc for doc in documents[1:] if isinstance(doc, dict)]
    errors.extend(validate_contract(contract))
    embedded_by_id = {str(w.get("workflow_id", "")): w for w in embedded}
    split_by_id = {str(w.get("workflow_id", "")): w for w in split_workflows if isinstance(w, dict)}
    require(set(embedded_by_id) == EXPECTED_IDS, "embedded workflow instance set is incomplete", errors)
    require(set(split_by_id) == EXPECTED_IDS, "split workflow instance set is incomplete", errors)
    require(len(split_by_id) == len(split_workflows), "split workflow ids are not unique", errors)

    contract_version = str(contract.get("schema_version", ""))
    for wid, workflow in split_by_id.items():
        require(str(workflow.get("schema_version", "")) == contract_version, f"{wid}: split schema version mismatch", errors)
        comparable = dict(workflow)
        comparable.pop("schema_version", None)
        require(comparable == embedded_by_id.get(wid), f"{wid}: split file differs from embedded workflow", errors)

    for workflow in embedded:
        errors.extend(validate_workflow(workflow, contract))
    for workflow in split_workflows:
        if isinstance(workflow, dict):
            errors.extend(validate_workflow(workflow, contract))
    if embedded:
        errors.extend(synthetic_negative_tests(contract, embedded[0]))

    if errors:
        print("AIOS Workflow Schema v1 validation FAILED")
        for error in errors:
            print(f"- {error}")
        return 1

    print("AIOS Workflow Schema v1 validation PASSED")
    print(f"- parsed embedded documents: {len(documents)}")
    print(f"- validated embedded workflows: {len(embedded)}")
    print(f"- validated split workflow files: {len(split_workflows)}")
    print("- cross-file consistency: PASS")
    print("- synthetic negative cases: 4")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
