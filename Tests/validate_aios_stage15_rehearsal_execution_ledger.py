#!/usr/bin/env python3
"""Validate Stage 15 rehearsal execution history and fail-closed authorization state."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
LEDGER_PATH = Path("Governance/AIOS-Stage15-Local-Python-Rehearsal-Execution-Ledger-v1.yaml")
MANDATORY_RETURN_PATH = Path("Governance/AIOS-Stage15-Local-Python-Rehearsal-Mandatory-Return-v1.yaml")
AUTHORIZATION_GUARD_PATH = Path("Governance/AIOS-Nonproduction-Readiness-Rehearsal-Authorization-Guard-v1.yaml")
PROJECT_REGISTRY_PATH = Path("Governance/AIOS-Project-Registry.md")
STAGE_REGISTRY_PATH = Path("Governance/AIOS-Stage-Registry.md")

PENDING = "pending_explicit_tony_disposition"
EXPECTED_MAXIMUM_CONCLUSION = (
    "execution_count_authorization_reconciliation_required_before_evidence_acceptance"
)


def _load_yaml(path: Path) -> dict[str, Any]:
    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ValueError(f"{path}: mapping required")
    return loaded


def validate_repository(root: Path = ROOT) -> list[str]:
    resolved = Path(root).resolve()
    required = (
        LEDGER_PATH,
        MANDATORY_RETURN_PATH,
        AUTHORIZATION_GUARD_PATH,
        PROJECT_REGISTRY_PATH,
        STAGE_REGISTRY_PATH,
    )
    errors = [f"missing:{path.as_posix()}" for path in required if not (resolved / path).is_file()]
    if errors:
        return errors

    ledger = _load_yaml(resolved / LEDGER_PATH)
    mandatory_return = _load_yaml(resolved / MANDATORY_RETURN_PATH)
    guard = _load_yaml(resolved / AUTHORIZATION_GUARD_PATH)
    guard_text = (resolved / AUTHORIZATION_GUARD_PATH).read_text(encoding="utf-8")
    project_registry = (resolved / PROJECT_REGISTRY_PATH).read_text(encoding="utf-8")
    stage_registry = (resolved / STAGE_REGISTRY_PATH).read_text(encoding="utf-8")

    if ledger.get("ledger_version") != "aios_stage15_local_python_rehearsal_execution_ledger/v1":
        errors.append("ledger:version_drift")
    if ledger.get("status") != "human_owner_disposition_required":
        errors.append("ledger:unexpected_status_before_issue55_human_disposition")

    rows = ledger.get("recorded_executions")
    if not isinstance(rows, list):
        errors.append("ledger:recorded_executions_list_required")
        rows = []
    run_ids = [str(row.get("run_id")) for row in rows if isinstance(row, dict)]
    if len(run_ids) != len(set(run_ids)):
        errors.append("ledger:duplicate_run_id")
    if len(rows) != 2:
        errors.append(f"ledger:distinct_recorded_execution_count_expected_2:actual_{len(rows)}")

    for row in rows:
        if not isinstance(row, dict):
            errors.append("ledger:execution_row_mapping_required")
            continue
        run_id = str(row.get("run_id"))
        source_commit = str(row.get("source_commit"))
        source_tree = str(row.get("source_tree"))
        if row.get("execution_occurred") is not True:
            errors.append(f"ledger:execution_occurred_must_be_true:{run_id}")
        if row.get("authorization_treatment") != PENDING:
            errors.append(f"ledger:authorization_treatment_must_remain_pending:{run_id}")
        if row.get("evidence_eligibility_for_issue52") != PENDING:
            errors.append(f"ledger:evidence_eligibility_must_remain_pending:{run_id}")
        if row.get("invalidated_or_superseded") != "not_determined":
            errors.append(f"ledger:invalidation_must_not_be_inferred:{run_id}")
        for registry_name, registry_text in (
            ("project_registry", project_registry),
            ("stage_registry", stage_registry),
        ):
            for token_name, token in (
                ("run_id", run_id),
                ("source_commit", source_commit),
                ("source_tree", source_tree),
            ):
                if token not in registry_text:
                    errors.append(f"{registry_name}:missing_{token_name}:{run_id}")

    state = ledger.get("machine_derived_state")
    if not isinstance(state, dict):
        errors.append("ledger:machine_derived_state_mapping_required")
        state = {}
    unresolved = [
        row["run_id"]
        for row in rows
        if isinstance(row, dict) and row.get("authorization_treatment") == PENDING
    ]
    if state.get("distinct_recorded_execution_count") != len(rows):
        errors.append("ledger:derived_execution_count_mismatch")
    if state.get("unresolved_authorization_disposition_count") != len(unresolved):
        errors.append("ledger:derived_unresolved_count_mismatch")
    if state.get("unresolved_execution_ids") != unresolved:
        errors.append("ledger:derived_unresolved_ids_mismatch")
    if state.get("cross_asset_count_reconciled") is not False:
        errors.append("ledger:cross_asset_count_must_remain_unreconciled")
    if state.get("issue52_evidence_acceptance_blocked") is not True:
        errors.append("ledger:issue52_must_be_blocked")
    if state.get("issue53_ready_for_review_blocked") is not True:
        errors.append("ledger:issue53_must_be_blocked")
    if state.get("maximum_machine_conclusion") != EXPECTED_MAXIMUM_CONCLUSION:
        errors.append("ledger:maximum_machine_conclusion_drift")

    ceiling = ledger.get("authorization_ceiling", {})
    if ceiling.get("authorized_execution_count") != 1:
        errors.append("ledger:authorization_ceiling_must_be_one")
    if guard.get("status") != "authorized_for_implementation_and_one_local_rehearsal":
        errors.append("authorization_guard:status_drift")
    if guard.get("owner_decision_evidence", {}).get("actor") != "Tony":
        errors.append("authorization_guard:owner_actor_drift")
    # The legacy guard contains an unquoted `Issue #51` note. YAML treats the
    # hash as a comment delimiter, so inspect the controlled raw text here
    # rather than silently trusting the truncated parsed scalar.
    if "one bounded local rehearsal" not in guard_text:
        errors.append("authorization_guard:one_rehearsal_ceiling_missing")

    declared_count = mandatory_return.get("rehearsal", {}).get("valid_run_count")
    if state.get("mandatory_return_declared_valid_run_count") != declared_count:
        errors.append("ledger:mandatory_return_declared_count_snapshot_drift")
    if declared_count != 1:
        errors.append("mandatory_return:declared_valid_run_count_drift")
    if len(rows) <= declared_count:
        errors.append("ledger:expected_cross_asset_execution_count_conflict_not_present")

    invalidated = ledger.get("invalidated_preacceptance_attempts")
    if not isinstance(invalidated, list) or len(invalidated) != 1:
        errors.append("ledger:single_invalidated_preacceptance_attempt_required")
    else:
        attempt = invalidated[0]
        if attempt.get("commit") != "e87f7fdc7ae235d365afc8f44816c5854877f1b2":
            errors.append("ledger:invalidated_preacceptance_commit_drift")
        if attempt.get("disposition") != "stone_stopped_receipt_invalid_not_committed":
            errors.append("ledger:invalidated_preacceptance_disposition_drift")

    downstream = ledger.get("downstream_authority")
    if not isinstance(downstream, dict) or not downstream:
        errors.append("ledger:downstream_authority_mapping_required")
    elif any(value is not False for value in downstream.values()):
        errors.append("ledger:downstream_authority_escalation")
    if ledger.get("external_actions_performed") != []:
        errors.append("ledger:external_actions_present")

    rules = set(ledger.get("append_only_rules", []))
    for required_rule in (
        "preserve_every_distinct_recorded_run_id",
        "never_relabel_a_recorded_execution_invalid_without_explicit_human_disposition",
        "resolve_authorization_and_evidence_eligibility_only_from_explicit_owner_disposition",
        "do_not_execute_another_rehearsal_to_repair_governance_evidence",
    ):
        if required_rule not in rules:
            errors.append(f"ledger:missing_append_only_rule:{required_rule}")

    return list(dict.fromkeys(errors))


def main() -> int:
    errors = validate_repository(ROOT)
    if errors:
        print("AIOS Stage 15 rehearsal execution ledger validation FAILED")
        for error in errors:
            print(f"- {error}")
        return 1
    print("AIOS Stage 15 rehearsal execution ledger validation PASSED")
    print("recorded_execution_count=2")
    print("authorized_execution_ceiling=1")
    print("human_owner_disposition_required=true")
    print("issue52_evidence_acceptance_blocked=true")
    print("issue53_ready_for_review_blocked=true")
    print("external_actions_performed=[]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
