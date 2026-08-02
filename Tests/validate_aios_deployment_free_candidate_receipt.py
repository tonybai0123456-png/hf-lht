from __future__ import annotations

import copy
from pathlib import Path
from typing import Any, Callable

import yaml
from yaml.tokens import AliasToken, AnchorToken, ScalarToken


ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = Path("Governance/AIOS-Deployment-Free-Candidate-Receipt-v1.yaml")
GUIDE_PATH = Path("Tests/AIOS-Deployment-Free-Candidate-Receipt-Validation.md")
CANDIDATE_PATH = Path(
    "Governance/AIOS-Deployment-Free-Candidate-Evidence-v1.yaml"
)
AUDIT_PATH = Path("Governance/AIOS-Predeployment-Completion-Audit-v1.yaml")
PROPOSALS_PATH = Path("Governance/AIOS-Stage15-Human-Gate-Proposals-v1.yaml")
MAPPING_PATH = Path(
    "Governance/AIOS-Nonproduction-Readiness-Stage10-14-Mapping-v1.yaml"
)

CHANGED_PATHS = (
    ".github/workflows/validate-aios-nonproduction-readiness.yml",
    ".gitignore",
    "Governance/AIOS-Deployment-Free-Candidate-Evidence-v1.yaml",
    "Governance/AIOS-Nonproduction-Readiness-Acceptance-Matrix-v1.yaml",
    "Governance/AIOS-Nonproduction-Readiness-Integration-Model-v1.yaml",
    "Governance/AIOS-Nonproduction-Readiness-Integration-v1.md",
    "Governance/AIOS-Nonproduction-Readiness-Stage10-14-Mapping-v1.yaml",
    "Governance/AIOS-Predeployment-Completion-Audit-v1.yaml",
    "Governance/AIOS-Project-Registry.md",
    "Governance/AIOS-Stage-Registry.md",
    "Governance/AIOS-Stage15-Human-Gate-Proposals-v1.yaml",
    "Tests/AIOS-Deployment-Free-Candidate-Validation.md",
    "Tests/AIOS-Nonproduction-Readiness-Validation.md",
    "Tests/AIOS-Predeployment-Completion-Audit-Validation.md",
    "Tests/AIOS-Stage15-Human-Gate-Proposals-Validation.md",
    "Tests/Fixtures/nonproduction-readiness/synthetic-local-integration.yaml",
    "Tests/test_deployment_free_candidate.py",
    "Tests/test_nonproduction_readiness.py",
    "Tests/test_operational_resilience.py",
    "Tests/test_predeployment_completion_audit.py",
    "Tests/test_project_governance.py",
    "Tests/test_stage15_human_gate_proposals.py",
    "Tests/validate_aios_deployment_free_candidate.py",
    "Tests/validate_aios_nonproduction_readiness.py",
    "Tests/validate_aios_operational_resilience.py",
    "Tests/validate_aios_predeployment_completion_audit.py",
    "Tests/validate_aios_stage15_human_gate_proposals.py",
    "docs/superpowers/plans/"
    "2026-07-23-nonproduction-readiness-remediation-integration.md",
    "docs/superpowers/specs/"
    "2026-07-23-nonproduction-readiness-remediation-integration-design.md",
)
CI_RECORDS = (
    (
        "Validate AIOS Architecture and Security Foundations",
        62,
        30609596588,
        "success",
    ),
    ("Validate AIOS Privacy and Data Governance", 53, 30609596630, "success"),
    (
        "Validate AIOS Production Readiness Assessment",
        70,
        30609596617,
        "success",
    ),
    ("Validate AIOS Support Controlled Pilot", 29, 30609596590, "success"),
    ("Validate AIOS Workflow Schema", 61, 30609596618, "success"),
    ("Validate AIOS Project Governance", 74, 30609596635, "success"),
    ("Validate Runtime Orchestrator v1", 83, 30609596625, "success"),
    ("Validate AIOS Operational Resilience", 46, 30609596639, "success"),
    ("Validate AIOS Non-production Readiness", 12, 30609596718, "success"),
)
RISK_EVIDENCE = (
    ("PR-RISK-001", ["EV-ENVIRONMENT"]),
    ("PR-RISK-002", ["EV-IDENTITY"]),
    ("PR-RISK-003", ["EV-DATA"]),
    ("PR-RISK-004", ["EV-DATA", "EV-EVIDENCE"]),
    ("PR-RISK-005", ["EV-OBSERVATION", "EV-EVIDENCE"]),
    ("PR-RISK-006", ["EV-RECOVERY"]),
    ("PR-RISK-007", ["EV-INCIDENT"]),
    ("PR-RISK-008", ["EV-SUPPORT"]),
    ("PR-RISK-009", ["EV-IDENTITY", "EV-DATA"]),
    ("PR-RISK-010", ["EV-ENVIRONMENT", "EV-EVIDENCE"]),
)
RISK_OWNERS = (
    ("Stone", ["Developer Agent"]),
    ("Stone", ["Developer Agent"]),
    ("Tony", ["Data Agent"]),
    ("Tony", ["Data Agent"]),
    ("Stone", ["Developer Agent", "Data Agent"]),
    ("Stone", ["Developer Agent"]),
    ("Stone", ["Developer Agent"]),
    ("Stone", ["CustomerService Agent"]),
    ("Tony", ["Data Agent", "CEO Agent"]),
    ("Tony", ["CEO Agent"]),
)
EVIDENCE_IDS = (
    "EV-ENVIRONMENT",
    "EV-IDENTITY",
    "EV-DATA",
    "EV-EVIDENCE",
    "EV-OBSERVATION",
    "EV-RECOVERY",
    "EV-INCIDENT",
    "EV-SUPPORT",
)
PENDING_GATES = (
    "HG-PILOT-EVIDENCE",
    "HG-RELEASE",
)
WITHHELD_AUTHORITIES = (
    "merge",
    "publication",
    "archive",
    "real_data",
    "credentials_and_permissions",
    "connectors",
    "external_infrastructure_and_accounts",
    "real_pilot",
    "risk_acceptance",
    "release",
    "deployment",
)
FALSE_CLAIMS = {
    "risk_accepted": False,
    "real_pilot_performed": False,
    "pilot_authorized": False,
    "production_ready": False,
    "release_authorized": False,
    "deployment_authorized": False,
    "real_data_used": False,
    "connector_used": False,
    "infrastructure_provisioned": False,
    "credentials_used": False,
}


def _error(path: str, code: str) -> str:
    return f"{path}:{code}"


def _exact_keys(value: Any, expected: tuple[str, ...], path: str) -> list[str]:
    if not isinstance(value, dict):
        return [_error(path, "mapping_required")]
    if tuple(value.keys()) != expected:
        return [_error(path, "exact_keys_required")]
    return []


def _fail_closed(
    validator: Callable[[Any], list[str]], value: Any, path: str
) -> list[str]:
    try:
        copied = copy.deepcopy(value)
        errors = validator(copied)
        if not isinstance(errors, list) or not all(
            isinstance(error, str) for error in errors
        ):
            return [_error(path, "validator_contract_error")]
        return errors
    except Exception as exc:
        return [_error(path, f"validation_exception:{type(exc).__name__}")]


def _load_controlled_yaml(path: Path) -> dict[str, Any]:
    if path.is_symlink():
        raise ValueError(f"{path}: symlink is not allowed")
    text = path.read_text(encoding="utf-8")
    try:
        for token in yaml.scan(text):
            if isinstance(token, (AnchorToken, AliasToken)):
                raise ValueError(f"{path}: anchors and aliases are not allowed")
            if isinstance(token, ScalarToken) and token.value == "<<":
                raise ValueError(f"{path}: merge keys are not allowed")
        loaded = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise ValueError(f"{path}: invalid YAML") from exc
    if not isinstance(loaded, dict):
        raise ValueError(f"{path}: controlled YAML must be a mapping")
    return loaded


def load_candidate_receipt(root: Path = ROOT) -> dict[str, Any]:
    resolved_root = root.resolve()
    path = resolved_root / MODEL_PATH
    if path.resolve().parent != (resolved_root / "Governance").resolve():
        raise ValueError("candidate receipt path escapes repository")
    return _load_controlled_yaml(path)


def _validate_candidate_receipt_impl(model: Any) -> list[str]:
    keys = (
        "receipt_version",
        "stage",
        "stage_id",
        "status",
        "allowed_scope",
        "excluded_entities",
        "source_state",
        "changed_file_manifest",
        "clean_reproduction",
        "exact_head_ci",
        "risk_evidence_and_treatment_mapping",
        "synthetic_control_evidence",
        "governance_overlay",
        "withheld_authorities",
        "candidate_decision",
        "claims",
        "external_actions_performed",
    )
    errors = _exact_keys(model, keys, "$")
    if errors:
        return errors
    if model["receipt_version"] != "deployment_free_candidate_receipt/v1":
        errors.append(_error("$.receipt_version", "invalid"))
    if model["stage"] != "15" or model["stage_id"] != "NR-01":
        errors.append(_error("$.stage", "invalid"))
    if model["status"] != "verified_technical_evidence_pending_human_gates":
        errors.append(_error("$.status", "premature_or_invalid"))
    if model["allowed_scope"] != {"company": "汇沣电商", "brand": "BUW"}:
        errors.append(_error("$.allowed_scope", "invalid"))
    if model["excluded_entities"] != ["PC", "六合通"]:
        errors.append(_error("$.excluded_entities", "invalid"))

    expected_source = {
        "base_commit": "403f97ea56678185398ee52fff2b35eeff7a700f",
        "candidate_commit": "36716abc76373d053c75e68352f46589f4ddc8f1",
        "candidate_tree": "ec48f7c537162b32f6bc35947d9e49758e1b53bd",
        "pull_request": "#41 / Draft / open / unmerged",
        "receipt_record_commit_state": "external_capture_after_push",
    }
    if model["source_state"] != expected_source:
        errors.append(_error("$.source_state", "exact_source_required"))

    manifest = model["changed_file_manifest"]
    errors.extend(
        _exact_keys(manifest, ("count", "paths"), "$.changed_file_manifest")
    )
    if (
        not isinstance(manifest, dict)
        or type(manifest.get("count")) is not int
        or manifest.get("count") != len(CHANGED_PATHS)
        or manifest.get("paths") != list(CHANGED_PATHS)
    ):
        errors.append(
            _error("$.changed_file_manifest", "exact_ordered_manifest_required")
        )

    expected_reproduction = {
        "source_method": "git_archive_clean_export",
        "source_command": (
            "git archive 36716abc76373d053c75e68352f46589f4ddc8f1"
        ),
        "dependency_manifest": "requirements-dev.txt",
        "dependency_resolution": "PyYAML 6.0.3",
        "tests_passed": 127,
        "tests_total": 127,
        "validators_passed": 10,
        "validators_total": 10,
        "compilation": "passed",
        "diff_check": "passed",
        "sensitive_material_scan": "passed",
        "performed_date": "2026-07-31",
    }
    if model["clean_reproduction"] != expected_reproduction:
        errors.append(
            _error("$.clean_reproduction", "exact_clean_evidence_required")
        )

    ci_records = model["exact_head_ci"]
    if not isinstance(ci_records, list) or len(ci_records) != len(CI_RECORDS):
        errors.append(_error("$.exact_head_ci", "exact_length_required"))
    else:
        for index, (record, expected) in enumerate(zip(ci_records, CI_RECORDS)):
            path = f"$.exact_head_ci[{index}]"
            errors.extend(
                _exact_keys(
                    record,
                    ("workflow", "run_number", "run_id", "conclusion"),
                    path,
                )
            )
            if not isinstance(record, dict):
                continue
            actual = (
                record.get("workflow"),
                record.get("run_number"),
                record.get("run_id"),
                record.get("conclusion"),
            )
            if actual != expected:
                errors.append(_error(path, "exact_success_receipt_required"))

    risk_records = model["risk_evidence_and_treatment_mapping"]
    if not isinstance(risk_records, list) or len(risk_records) != 10:
        errors.append(
            _error(
                "$.risk_evidence_and_treatment_mapping",
                "exact_length_required",
            )
        )
    else:
        for index, (record, risk_data, owner_data) in enumerate(
            zip(risk_records, RISK_EVIDENCE, RISK_OWNERS)
        ):
            path = f"$.risk_evidence_and_treatment_mapping[{index}]"
            errors.extend(
                _exact_keys(
                    record,
                    (
                        "risk_id",
                        "evidence_ids",
                        "human_treatment_owner",
                        "technical_support_agents",
                        "disposition",
                        "risk_state",
                        "risk_accepted",
                        "treatment_authorized",
                    ),
                    path,
                )
            )
            if not isinstance(record, dict):
                continue
            expected = {
                "risk_id": risk_data[0],
                "evidence_ids": risk_data[1],
                "human_treatment_owner": owner_data[0],
                "technical_support_agents": owner_data[1],
                "disposition": "mitigate_and_remain_open_blocked_unaccepted",
                "risk_state": "open_blocked_unaccepted",
                "risk_accepted": False,
                "treatment_authorized": True,
            }
            if record != expected:
                errors.append(
                    _error(
                        path,
                        "authorized_treatment_mapping_risks_unaccepted_required",
                    )
                )

    expected_controls = {
        "classification": "repository_controlled_synthetic_only",
        "evidence_ids": list(EVIDENCE_IDS),
        "real_data_used": False,
        "external_connector_used": False,
        "infrastructure_or_account_material_used": False,
    }
    if model["synthetic_control_evidence"] != expected_controls:
        errors.append(
            _error("$.synthetic_control_evidence", "synthetic_only_required")
        )
    expected_overlay = {
        "accepted_gates": [
            "HG-PRIVACY-DATA",
            "HG-OPS-RECOVERY-INCIDENT-SUPPORT",
            "HG-RISK-DISPOSITION",
            "HG-PILOT-SCOPE",
        ],
        "decision_evidence": [
            "Owner authorization / Issue #44",
            "Owner authorization / Issue #45",
            "Owner authorization / Issue #46",
            "Owner authorization / Issue #47",
        ],
        "allowed_data_classes": [
            "synthetic_non_personal",
            "synthetic_personal_like_clearly_fictitious_non_routable",
        ],
        "human_approver": "Tony",
        "backup_and_escalation_contact": "Stone",
        "technical_validation_owner": "Data Agent",
        "implementation_support": "Developer Agent",
        "operations_human_approver": "Stone",
        "operations_backup_and_escalation_contact": "Tony",
        "operations_technical_owner": "Developer Agent",
        "operations_evidence_contributors": [
            "CustomerService Agent",
            "Data Agent",
        ],
        "operations_scope_type": (
            "synthetic_operations_recovery_incident_support_only"
        ),
        "risk_treatment_human_approver": "Tony",
        "overall_risk_owner": "Tony",
        "independent_reviewer_and_escalation_contact": "Stone",
        "risk_treatment_technical_evidence_contributors": [
            "Developer Agent",
            "Data Agent",
            "CustomerService Agent",
            "CEO Agent",
        ],
        "risk_treatment_disposition": (
            "mitigate_and_remain_open_blocked_unaccepted"
        ),
        "treatment_ownership_authorized": True,
        "rehearsal_scope_type": "synthetic_rehearsal_only_no_real_pilot",
        "rehearsal_human_approver": "Tony",
        "rehearsal_backup_and_escalation_contact": "Stone",
        "rehearsal_technical_owner": "Developer Agent",
        "rehearsal_evidence_contributors": [
            "CustomerService Agent",
            "Data Agent",
        ],
        "rehearsal_zero_participants": {
            "real_customers": 0,
            "employees_or_real_operators": 0,
            "stores": 0,
            "production_or_staging_environments": 0,
            "real_cases_orders_accounts_or_messages": 0,
        },
        "synthetic_rehearsal_scope_authorized": True,
        "next_gate": "HG-PILOT-EVIDENCE",
        "real_data_authorized": False,
        "real_operations_authorized": False,
        "credentials_connectors_infrastructure_or_accounts_authorized": False,
        "pilot_risk_acceptance_merge_release_or_deployment_authorized": False,
        "external_actions_performed": [],
    }
    if model["governance_overlay"] != expected_overlay:
        errors.append(_error("$.governance_overlay", "gate7_overlay_required"))
    if model["withheld_authorities"] != list(WITHHELD_AUTHORITIES):
        errors.append(
            _error("$.withheld_authorities", "exact_withholding_required")
        )

    expected_decision = {
        "result": "not_ready_pending_human_governance",
        "technically_verified_source": True,
        "remaining_human_gates": list(PENDING_GATES),
        "release_gate_authorized": False,
        "deployment_free_evidence_only": True,
    }
    if model["candidate_decision"] != expected_decision:
        errors.append(
            _error("$.candidate_decision", "human_governance_stop_required")
        )
    if (
        not isinstance(model["claims"], dict)
        or model["claims"] != FALSE_CLAIMS
        or not all(type(value) is bool for value in model["claims"].values())
    ):
        errors.append(_error("$.claims", "exact_false_claims_required"))
    if model["external_actions_performed"] != []:
        errors.append(_error("$.external_actions_performed", "must_be_empty"))
    return list(dict.fromkeys(errors))


def validate_candidate_receipt(model: Any) -> list[str]:
    return _fail_closed(_validate_candidate_receipt_impl, model, "$receipt")


def evaluate_candidate_receipt(model: Any) -> dict[str, Any]:
    errors = validate_candidate_receipt(model)
    if errors:
        return {
            "result": "denied",
            "reason_codes": [f"VALIDATION_ERROR:{error}" for error in errors],
            "claims": dict(FALSE_CLAIMS),
            "external_actions_performed": [],
        }
    return {
        "result": "not_ready_pending_human_governance",
        "reason_codes": list(PENDING_GATES),
        "claims": dict(FALSE_CLAIMS),
        "external_actions_performed": [],
    }


def validate_repository(root: Path = ROOT) -> list[str]:
    try:
        model = load_candidate_receipt(root)
        candidate = _load_controlled_yaml(root / CANDIDATE_PATH)
        audit = _load_controlled_yaml(root / AUDIT_PATH)
        proposals = _load_controlled_yaml(root / PROPOSALS_PATH)
        mapping = _load_controlled_yaml(root / MAPPING_PATH)
        guide = (root / GUIDE_PATH).read_text(encoding="utf-8")
    except (OSError, ValueError) as exc:
        return [_error("$repository", f"load_error:{type(exc).__name__}")]
    errors = validate_candidate_receipt(model)

    missing_paths = [
        path for path in CHANGED_PATHS if not (root / path).is_file()
    ]
    if missing_paths:
        errors.append(_error("$repository.manifest", "path_missing"))

    candidate_gates = candidate.get("gate_ledger")
    gate_truth = (
        [record.get("accepted") for record in candidate_gates]
        if isinstance(candidate_gates, list)
        and all(isinstance(record, dict) for record in candidate_gates)
        else []
    )
    if (
        candidate.get("status")
        != "technical_evidence_verified_pending_human_gates"
        or gate_truth != [True] * 10 + [False] * 2
        or candidate.get("external_actions_performed") != []
    ):
        errors.append(_error("$repository.candidate", "alignment_required"))

    if (
        audit.get("status")
        != "incomplete_pending_ordered_human_governance"
        or audit.get("completion_decision", {}).get("result")
        != "not_complete_pending_human_governance"
        or audit.get("external_actions_performed") != []
    ):
        errors.append(_error("$repository.audit", "alignment_required"))

    proposal_risks = None
    proposal_records = proposals.get("proposals")
    if isinstance(proposal_records, list):
        gate9 = next(
            (
                record
                for record in proposal_records
                if isinstance(record, dict)
                and record.get("gate_id") == "HG-RISK-DISPOSITION"
            ),
            None,
        )
        if isinstance(gate9, dict):
            proposal_risks = gate9.get("risk_treatments")
    receipt_risks = model.get("risk_evidence_and_treatment_mapping")
    if not isinstance(proposal_risks, list) or not isinstance(receipt_risks, list):
        errors.append(_error("$repository.proposals", "risk_mapping_required"))
    else:
        proposal_owner_view = [
            (
                record.get("risk_id"),
                record.get("human_treatment_owner"),
                record.get("technical_support_agents"),
                record.get("disposition"),
                record.get("production_action_allowed"),
            )
            for record in proposal_risks
            if isinstance(record, dict)
        ]
        receipt_owner_view = [
            (
                record.get("risk_id"),
                record.get("human_treatment_owner"),
                record.get("technical_support_agents"),
                record.get("disposition"),
                False,
            )
            for record in receipt_risks
            if isinstance(record, dict)
        ]
        if proposal_owner_view != receipt_owner_view:
            errors.append(_error("$repository.proposals", "owner_alignment_required"))

    mapping_records = mapping.get("risk_mappings")
    expected_mapping_view = [
        (risk_id, evidence_ids, "open_blocked_unaccepted")
        for risk_id, evidence_ids in RISK_EVIDENCE
    ]
    actual_mapping_view = (
        [
            (
                record.get("risk_id"),
                record.get("evidence_ids"),
                record.get("state"),
            )
            for record in mapping_records
            if isinstance(record, dict)
        ]
        if isinstance(mapping_records, list)
        else []
    )
    if actual_mapping_view != expected_mapping_view:
        errors.append(_error("$repository.mapping", "evidence_alignment_required"))

    guide_tokens = (
        "36716abc76373d053c75e68352f46589f4ddc8f1",
        "ec48f7c537162b32f6bc35947d9e49758e1b53bd",
        "29",
        "127/127",
        "10/10",
        "9/9",
        "git archive",
        "requirements-dev.txt",
        "PyYAML 6.0.3",
        "open_blocked_unaccepted",
        "Gate 11",
        "Issue #49",
        "external_actions_performed=[]",
        "不得解释为",
    )
    for token in guide_tokens:
        if token not in guide:
            errors.append(_error("$repository.guide", f"missing_token:{token}"))
    return list(dict.fromkeys(errors))


def main() -> int:
    errors = validate_repository(ROOT)
    if errors:
        print("AIOS deployment-free candidate receipt validation FAILED")
        for error in errors:
            print(f"- {error}")
        return 1
    result = evaluate_candidate_receipt(load_candidate_receipt(ROOT))
    print("AIOS deployment-free candidate receipt validation PASSED")
    print(f"result={result['result']}")
    print("external_actions_performed=[]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
