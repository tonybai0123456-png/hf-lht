#!/usr/bin/env python3
"""Synthetic-only, no-write Controlled Orchestrator Harness v0."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Callable

import yaml


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
        if metadata.get("data_classification") != "synthetic":
            raise HarnessPolicyError("only data_classification=synthetic is accepted")
        if metadata.get("dry_run") is not True:
            raise HarnessPolicyError("dry_run must be true")
        if metadata.get("allow_external_writes") is not False:
            raise HarnessPolicyError("allow_external_writes must be false")

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
        from_owner: str,
        to_owner: str,
        step_id: str,
    ) -> dict[str, Any]:
        inputs = payload["inputs"]
        metadata = payload["metadata"]
        values: dict[str, Any] = {
            "situation": inputs.get("anomaly_type"),
            "business_outcome": workflow.get("business_outcome"),
            "evidence_links": inputs.get("evidence_links", []),
            "owner_agent": to_owner,
            "risk_level": "synthetic_test",
            "data_cutoff": metadata.get("period"),
            "confidence": "synthetic_only",
            "requested_action": step_id,
            "deadline": None,
            "next_step": step_id,
        }
        required = workflow.get("handoff_contract", {}).get("required_fields", [])
        return {
            "from_owner": from_owner,
            "to_owner": to_owner,
            "step_id": step_id,
            "contract": {field: values.get(field, "synthetic-dry-run") for field in required},
        }

    def run(self, workflow: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
        """Simulate one workflow until completion or the first safety gate."""
        self._enforce_policy(payload)
        inputs = payload.get("inputs", {})
        if not isinstance(inputs, dict):
            raise ValueError("payload.inputs must be a mapping")

        key = self._idempotency_key(workflow, payload)
        base: dict[str, Any] = {
            "harness_version": "0.1.0",
            "workflow_id": workflow["workflow_id"],
            "idempotency_key": key,
            "dry_run": True,
            "synthetic_only": True,
            "external_writes_performed": False,
            "duplicate_run": False,
            "completed_steps": [],
            "pending_step": None,
            "missing_inputs": [],
            "handoff_packages": [],
            "approval_package": None,
            "audit_log": [],
        }

        if key in self._seen_idempotency_keys:
            base["status"] = "rejected"
            base["duplicate_run"] = True
            base["audit_log"].append(self._audit("duplicate_run_rejected", "rejected"))
            return base
        self._seen_idempotency_keys.add(key)

        missing = [field for field in workflow.get("required_inputs", []) if field not in inputs]
        if missing:
            base["status"] = "blocked"
            base["missing_inputs"] = missing
            base["audit_log"].append(
                self._audit("required_inputs_missing", "blocked", missing_inputs=missing)
            )
            return base

        base["status"] = "partial"
        base["audit_log"].append(self._audit("run_started", "partial"))
        previous_owner = str(workflow.get("accountable_agent"))
        for step in workflow.get("steps", []):
            step_id = str(step["id"])
            owner = str(step.get("owner", workflow.get("accountable_agent")))
            action_class = step.get("action_class")

            if owner != previous_owner:
                base["handoff_packages"].append(
                    self._handoff(workflow, payload, previous_owner, owner, step_id)
                )
                base["audit_log"].append(
                    self._audit("handoff_prepared", "partial", step_id=step_id, to_owner=owner)
                )
            previous_owner = owner

            if action_class == "prohibited":
                base["status"] = "rejected"
                base["pending_step"] = step_id
                base["audit_log"].append(
                    self._audit("prohibited_step_rejected", "rejected", step_id=step_id)
                )
                return base

            if action_class == "prepare_only":
                base["status"] = "needs_approval"
                base["pending_step"] = step_id
                base["approval_package"] = {
                    "workflow_id": workflow["workflow_id"],
                    "step_id": step_id,
                    "requested_approver": owner,
                    "requested_action": step_id,
                    "reason": "prepare_only steps cannot execute in Harness v0",
                    "evidence_links": inputs.get("evidence_links", []),
                    "synthetic_only": True,
                    "execution_performed": False,
                }
                base["audit_log"].append(
                    self._audit("approval_package_prepared", "needs_approval", step_id=step_id)
                )
                return base

            if action_class != "automatic_low_risk":
                raise ValueError(f"unknown action_class for {step_id}: {action_class}")
            base["completed_steps"].append(step_id)
            base["audit_log"].append(
                self._audit("step_simulated", "partial", step_id=step_id, owner=owner)
            )

        base["status"] = "completed"
        base["audit_log"].append(self._audit("run_completed", "completed"))
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
