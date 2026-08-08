#!/usr/bin/env python3
"""Cross-check the Stage 15 local Python rehearsal repository assets."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
RUNNER_PATH = Path("Runtime/stage15_local_python_rehearsal.py")
CONTRACT_PATH = Path(
    "Governance/AIOS-Stage15-Local-Python-Rehearsal-Contract-v1.yaml"
)
SCHEMA_PATH = Path(
    "Governance/AIOS-Stage15-Local-Python-Rehearsal-Receipt-Schema-v1.yaml"
)
RECEIPT_PATH = Path(
    "Governance/AIOS-Stage15-Local-Python-Rehearsal-Receipt-v1.json"
)
MANDATORY_RETURN_PATH = Path(
    "Governance/AIOS-Stage15-Local-Python-Rehearsal-Mandatory-Return-v1.yaml"
)
FIXTURE_PATH = Path(
    "Tests/Fixtures/nonproduction-readiness/local-python-rehearsal-synthetic.yaml"
)
SYNTHETIC_WORKFLOW_PATH = Path(
    "Tests/Fixtures/nonproduction-readiness/local-python-store-anomaly-workflow.yaml"
)
SYNTHETIC_INPUT_PATH = Path(
    "Tests/Fixtures/nonproduction-readiness/local-python-store-anomaly-input.yaml"
)
TEST_PATH = Path("Tests/test_stage15_local_python_rehearsal.py")
GUIDE_PATH = Path("Tests/AIOS-Stage15-Local-Python-Rehearsal-Validation.md")
DESIGN_PATH = Path(
    "docs/superpowers/specs/2026-08-03-stage15-local-python-test-deployment-rehearsal-design.md"
)
PLAN_PATH = Path(
    "docs/superpowers/plans/2026-08-03-stage15-local-python-test-deployment-rehearsal.md"
)
WORKFLOW_PATH = Path(".github/workflows/validate-aios-nonproduction-readiness.yml")
STAGE_REGISTRY_PATH = Path("Governance/AIOS-Stage-Registry.md")
PROJECT_REGISTRY_PATH = Path("Governance/AIOS-Project-Registry.md")
RISK_PATH = Path("Governance/AIOS-Production-Readiness-Risk-Register-v1.yaml")
GATE12_PATH = Path("Governance/AIOS-Stage15-Gate12-Release-Gate-Decision-v1.yaml")
RECONCILIATION_PATH = Path(
    "Governance/AIOS-Nonproduction-Readiness-Post-Gate12-Reconciliation-v1.yaml"
)


def _load_runner(root: Path):
    path = root / RUNNER_PATH
    spec = importlib.util.spec_from_file_location("stage15_rehearsal_validator", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("local rehearsal runner cannot be loaded")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_yaml(path: Path) -> dict[str, Any]:
    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ValueError(f"{path}: mapping required")
    return loaded


def validate_repository(root: Path = ROOT) -> list[str]:
    resolved = Path(root).resolve()
    required = (
        RUNNER_PATH,
        CONTRACT_PATH,
        SCHEMA_PATH,
        RECEIPT_PATH,
        MANDATORY_RETURN_PATH,
        FIXTURE_PATH,
        SYNTHETIC_WORKFLOW_PATH,
        SYNTHETIC_INPUT_PATH,
        TEST_PATH,
        GUIDE_PATH,
        DESIGN_PATH,
        PLAN_PATH,
        WORKFLOW_PATH,
        STAGE_REGISTRY_PATH,
        PROJECT_REGISTRY_PATH,
        RISK_PATH,
        GATE12_PATH,
        RECONCILIATION_PATH,
    )
    errors = [f"missing:{path.as_posix()}" for path in required if not (resolved / path).is_file()]
    if errors:
        return errors
    runner = _load_runner(resolved)
    contract = runner.load_closed_yaml(resolved / CONTRACT_PATH)
    fixture = runner.load_closed_yaml(resolved / FIXTURE_PATH)
    schema = runner.load_closed_yaml(resolved / SCHEMA_PATH)
    receipt = runner.load_closed_yaml(resolved / RECEIPT_PATH)
    mandatory_return = runner.load_closed_yaml(resolved / MANDATORY_RETURN_PATH)
    errors.extend(runner.validate_contract(contract))
    errors.extend(runner.validate_fixture(fixture))
    errors.extend(runner.validate_receipt(receipt))
    if receipt.get("result") != runner.RESULTS[0]:
        errors.append("receipt:passed_not_cloud_proof_required")
    if receipt.get("source_commit") != "33e2216976b73ebaff4368ca8b8d5dc206ebf894":
        errors.append("receipt:source_commit_drift")
    if receipt.get("source_tree") != "eff75180da120fa7deffdd15b1daa2a13bcb8ab5":
        errors.append("receipt:source_tree_drift")
    if any(receipt.get("material_scan", {}).values()):
        errors.append("receipt:material_scan_must_be_all_false")
    if receipt.get("network_guard", {}).get("attempted_operations") != []:
        errors.append("receipt:network_attempts_must_be_empty")
    if tuple(mandatory_return) != (
        "record_version",
        "stage",
        "status",
        "scope",
        "authorization",
        "source_candidate",
        "test_driven_development",
        "rehearsal",
        "independent_reviews",
        "risk_states",
        "governance_state",
        "authority_claims",
        "limitations",
        "external_actions_performed",
    ):
        errors.append("mandatory_return:exact_keys_required")
    if mandatory_return.get("source_candidate", {}).get("commit") != receipt.get(
        "source_commit"
    ):
        errors.append("mandatory_return:source_commit_drift")
    if mandatory_return.get("source_candidate", {}).get("tree") != receipt.get(
        "source_tree"
    ):
        errors.append("mandatory_return:source_tree_drift")
    if mandatory_return.get("rehearsal", {}).get("run_id") != receipt.get("run_id"):
        errors.append("mandatory_return:run_id_drift")
    if mandatory_return.get("rehearsal", {}).get("valid_run_count") != 1:
        errors.append("mandatory_return:one_valid_run_required")
    if mandatory_return.get("independent_reviews") != {
        "data_agent": {
            "result": "passed",
            "conclusion": "schema_inventory_fixture_smoke_material_network_cleanup_and_boundaries_match",
        },
        "stone": {
            "result": "passed",
            "conclusion": "post_rehearsal_boundary_review_passed_mandatory_return_allowed",
        },
        "review_exceptions": [],
    }:
        errors.append("mandatory_return:independent_review_drift")
    if mandatory_return.get("risk_states") != runner.RISK_STATES:
        errors.append("mandatory_return:risk_state_drift")
    if mandatory_return.get("external_actions_performed") != []:
        errors.append("mandatory_return:external_actions_present")
    if any(mandatory_return.get("authority_claims", {}).values()):
        errors.append("mandatory_return:authority_escalation")
    material_scan = runner.scan_rehearsal_material(
        fixture=fixture,
        selected_paths=(
            resolved / CONTRACT_PATH,
            resolved / FIXTURE_PATH,
            resolved / SYNTHETIC_WORKFLOW_PATH,
            resolved / SYNTHETIC_INPUT_PATH,
            resolved / RUNNER_PATH,
            resolved / "Runtime/controlled_orchestrator.py",
        ),
        inventory_paths=(
            path.relative_to(resolved).as_posix()
            for path in resolved.rglob("*")
            if path.is_file()
        ),
    )
    if any(material_scan.values()):
        errors.append(f"material_scan:unexpected_findings:{material_scan}")
    if tuple(schema) != (
        "schema_version",
        "additional_properties",
        "required_keys",
        "nested_required_keys",
        "constant_values",
    ):
        errors.append("schema:exact_keys_required")
    if schema.get("additional_properties") is not False:
        errors.append("schema:additional_properties_must_be_false")
    if tuple(schema.get("required_keys", [])) != runner.RECEIPT_KEYS:
        errors.append("schema:required_keys_drift")

    risk = _load_yaml(resolved / RISK_PATH)
    risk_rows = risk.get("risks", [])
    if not isinstance(risk_rows, list):
        errors.append("risk_register:risks_list_required")
    else:
        rows_by_id = {
            str(row.get("id")): row
            for row in risk_rows
            if isinstance(row, dict)
        }
        for risk_id in runner.RISK_STATES:
            row = rows_by_id.get(risk_id)
            if row is None:
                errors.append(f"risk_register:missing:{risk_id}")
                continue
            if row.get("acceptance_status") != "not_accepted":
                errors.append(f"risk_register:accepted:{risk_id}")
            if row.get("production_action_allowed") is not False:
                errors.append(f"risk_register:production_action_allowed:{risk_id}")

    reconciliation = _load_yaml(resolved / RECONCILIATION_PATH)
    controlled = reconciliation.get("controlled_state", {})
    pull_request = controlled.get("pull_request", {}) if isinstance(controlled, dict) else {}
    if pull_request != {"number": 41, "state": "open", "draft": True, "merged": False}:
        errors.append("reconciliation:pr41_must_remain_draft_open_unmerged")
    current_risks = controlled.get("risks", []) if isinstance(controlled, dict) else []
    current_states = {
        str(row.get("risk_id")): row.get("state")
        for row in current_risks
        if isinstance(row, dict)
    }
    if current_states != runner.RISK_STATES:
        errors.append("reconciliation:risk_states_drift")

    for path, tokens in (
        (
            STAGE_REGISTRY_PATH,
            ("Stage 15", "Reviewed", "BLOCKED / NO-GO"),
        ),
        (
            PROJECT_REGISTRY_PATH,
            ("Stage 15", "PR #41", "BLOCKED / NO-GO"),
        ),
        (
            GATE12_PATH,
            ("HG-RELEASE", "false", "BLOCKED / NO-GO"),
        ),
        (
            RECONCILIATION_PATH,
            ("lifecycle_handoff_ready_actions_withheld", "deployment_authorized: false"),
        ),
        (
            WORKFLOW_PATH,
            (
                "test_stage15_local_python_rehearsal",
                "validate_aios_stage15_local_python_rehearsal.py",
            ),
        ),
    ):
        text = (resolved / path).read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                errors.append(f"{path.as_posix()}:missing_token:{token}")

    for path in (DESIGN_PATH, PLAN_PATH, GUIDE_PATH):
        text = (resolved / path).read_text(encoding="utf-8")
        for token in (
            "local_python_test_deployment_rehearsal_passed_not_cloud_proof",
            "no network",
            "no credentials",
            "external_actions_performed",
        ):
            if token.lower() not in text.lower():
                errors.append(f"{path.as_posix()}:missing_token:{token}")
    return list(dict.fromkeys(errors))


def main() -> int:
    errors = validate_repository(ROOT)
    if errors:
        print("AIOS Stage 15 local Python rehearsal validation FAILED")
        for error in errors:
            print(f"- {error}")
        return 1
    print("AIOS Stage 15 local Python rehearsal validation PASSED")
    print("maximum_claim=local_python_test_deployment_rehearsal_passed_not_cloud_proof")
    print("cloud_capability_proven=false")
    print("external_actions_performed=[]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
