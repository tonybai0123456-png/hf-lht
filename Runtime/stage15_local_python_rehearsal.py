#!/usr/bin/env python3
"""Fail-closed local Python rehearsal for BUW Stage 15 synthetic evidence."""

from __future__ import annotations

import copy
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import io
import json
import os
from pathlib import Path, PurePosixPath
import platform
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
from typing import Any, Mapping, Sequence

import yaml
from yaml.tokens import AliasToken, AnchorToken, ScalarToken


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = Path(
    "Governance/AIOS-Stage15-Local-Python-Rehearsal-Contract-v1.yaml"
)
SCHEMA_PATH = Path(
    "Governance/AIOS-Stage15-Local-Python-Rehearsal-Receipt-Schema-v1.yaml"
)
FIXTURE_PATH = Path(
    "Tests/Fixtures/nonproduction-readiness/local-python-rehearsal-synthetic.yaml"
)

RESULTS = (
    "local_python_test_deployment_rehearsal_passed_not_cloud_proof",
    "local_python_test_deployment_rehearsal_denied",
    "local_python_test_deployment_rehearsal_blocked",
)
REASON_CODES = (
    "SOURCE_COMMIT_INVALID",
    "SOURCE_HEAD_CHANGED",
    "SOURCE_TREE_MISMATCH",
    "SOURCE_WORKTREE_DIRTY",
    "ARCHIVE_MEMBER_UNSAFE",
    "FILE_INVENTORY_MISMATCH",
    "LOCAL_PYTHON_UNAVAILABLE",
    "LOCAL_DEPENDENCY_UNAVAILABLE",
    "CREDENTIAL_LIKE_ENVIRONMENT_PRESENT",
    "ENVIRONMENT_NOT_ALLOWLISTED",
    "NETWORK_OPERATION_ATTEMPTED",
    "INFRASTRUCTURE_MATERIAL_DENIED",
    "COMMAND_NOT_ALLOWLISTED",
    "COMMAND_TIMEOUT",
    "COMPANY_SCOPE_DENIED",
    "BRAND_SCOPE_DENIED",
    "NON_SYNTHETIC_DATA_DENIED",
    "CAPABILITY_FIELD_NONEMPTY",
    "CAPABILITY_FIELD_MISPLACED",
    "SECRET_LIKE_MATERIAL_DENIED",
    "EXTERNAL_LOCATOR_DENIED",
    "AUTHORITY_CLAIM_DENIED",
    "SMOKE_OUTPUT_NONDETERMINISTIC",
    "RECEIPT_SCHEMA_INVALID",
    "CLEANUP_TARGET_UNSAFE",
    "CLEANUP_NOT_VERIFIED",
    "REPOSITORY_CHANGED",
    "MALFORMED_INPUT",
    "UNEXPECTED_RUNTIME_FAILURE",
)
RISK_STATES = {
    f"PR-RISK-{number:03d}": "open_blocked_unaccepted"
    for number in range(1, 11)
}
RECEIPT_KEYS = (
    "schema_version",
    "run_id",
    "started_at_utc",
    "finished_at_utc",
    "company",
    "brand",
    "stage",
    "mode",
    "result",
    "source_commit",
    "source_tree",
    "file_inventory_sha256",
    "python_runtime",
    "local_dependencies",
    "fixture_ids",
    "fixture_checksums",
    "ordered_checks",
    "smoke_result",
    "normalized_smoke_sha256",
    "network_guard",
    "material_scan",
    "cleanup",
    "risk_states",
    "stage10_state",
    "pr41_state",
    "cloud_capability_proven",
    "pilot_authorized",
    "production_ready",
    "release_authorized",
    "deployment_authorized",
    "risks_accepted",
    "external_actions_performed",
    "reason_codes",
    "evidence_refs",
    "required_human_decisions",
)
CHILD_ENVIRONMENT_KEYS = (
    "PATH",
    "LANG",
    "LC_ALL",
    "TMPDIR",
    "PYTHONNOUSERSITE",
    "PYTHONDONTWRITEBYTECODE",
    "PYTHONPATH",
    "AIOS_NETWORK_GUARD_LOG",
)
FORBIDDEN_ENVIRONMENT_FRAGMENTS = (
    "TOKEN",
    "SECRET",
    "PASSWORD",
    "PASSWD",
    "API_KEY",
    "APIKEY",
    "CREDENTIAL",
    "AUTH",
    "COOKIE",
    "SESSION",
    "DATABASE_URL",
    "DB_URL",
    "WEBHOOK",
    "AWS_",
    "AZURE_",
    "GOOGLE_APPLICATION_CREDENTIALS",
    "GITHUB_TOKEN",
    "OPENAI_",
    "SHOPIFY_",
    "META_",
    "FACEBOOK_",
    "SLACK_",
)
CAPABILITY_KEYS = frozenset({"external_endpoints", "connectors", "credentials"})
ALLOWED_EMPTY_CAPABILITY_PATHS = frozenset(
    {
        "$.environment.external_endpoints",
        "$.environment.connectors",
        "$.environment.credentials",
    }
)
ORDERED_ALLOWED_EMPTY_CAPABILITY_PATHS = (
    "$.environment.external_endpoints",
    "$.environment.connectors",
    "$.environment.credentials",
)
POLICY_DENIAL_CODES = frozenset(
    {
        "ARCHIVE_MEMBER_UNSAFE",
        "CREDENTIAL_LIKE_ENVIRONMENT_PRESENT",
        "ENVIRONMENT_NOT_ALLOWLISTED",
        "NETWORK_OPERATION_ATTEMPTED",
        "INFRASTRUCTURE_MATERIAL_DENIED",
        "COMMAND_NOT_ALLOWLISTED",
        "COMPANY_SCOPE_DENIED",
        "BRAND_SCOPE_DENIED",
        "NON_SYNTHETIC_DATA_DENIED",
        "CAPABILITY_FIELD_NONEMPTY",
        "CAPABILITY_FIELD_MISPLACED",
        "SECRET_LIKE_MATERIAL_DENIED",
        "EXTERNAL_LOCATOR_DENIED",
        "AUTHORITY_CLAIM_DENIED",
        "MALFORMED_INPUT",
    }
)
EPHEMERAL_KEYS = frozenset(
    {
        "at",
        "timestamp",
        "started_at_utc",
        "finished_at_utc",
        "run_id",
        "originating_run_id",
        "temporary_path",
        "python_executable",
    }
)
MARKER_NAME = ".stage15-rehearsal-marker"
HEX_40 = re.compile(r"^[0-9a-f]{40}$")
HEX_64 = re.compile(r"^[0-9a-f]{64}$")


def _error(path: str, code: str) -> str:
    return f"{path}:{code}"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _dedupe(values: Sequence[str]) -> list[str]:
    return list(dict.fromkeys(str(value) for value in values))


def _exact_keys(value: Any, expected: tuple[str, ...], path: str) -> list[str]:
    if not isinstance(value, dict):
        return [_error(path, "mapping_required")]
    if tuple(value.keys()) != expected:
        return [_error(path, "exact_keys_required")]
    return []


def _fail_closed(validator, value: Any, path: str) -> list[str]:
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


def load_closed_yaml(path: Path) -> dict[str, Any]:
    """Load a repository-controlled mapping while rejecting YAML indirection."""
    candidate = Path(path)
    if candidate.is_symlink():
        raise ValueError(f"{candidate}:symlink_denied")
    text = candidate.read_text(encoding="utf-8")
    try:
        for token in yaml.scan(text):
            if isinstance(token, (AnchorToken, AliasToken)):
                raise ValueError(f"{candidate}:yaml_alias_denied")
            if isinstance(token, ScalarToken) and token.value == "<<":
                raise ValueError(f"{candidate}:yaml_merge_denied")
        loaded = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise ValueError(f"{candidate}:invalid_yaml") from exc
    if not isinstance(loaded, dict):
        raise ValueError(f"{candidate}:mapping_required")
    return loaded


def _validate_contract_impl(contract: Any) -> list[str]:
    keys = (
        "contract_version",
        "stage",
        "mode",
        "scope",
        "allowed_results",
        "reason_codes",
        "environment",
        "allowed_empty_capability_paths",
        "fixture_ids",
        "allowed_commands",
        "risk_states",
        "stage10_state",
        "pr41_state",
        "authority_claims",
        "maximum_claim",
        "required_human_decisions",
        "external_actions_performed",
    )
    errors = _exact_keys(contract, keys, "$")
    if errors:
        return errors
    if contract["contract_version"] != "aios_stage15_local_python_rehearsal_contract/v1":
        errors.append(_error("$.contract_version", "invalid"))
    if contract["stage"] != "Stage 15 / NR-01":
        errors.append(_error("$.stage", "invalid"))
    if contract["mode"] != "local_isolated_python_synthetic_only":
        errors.append(_error("$.mode", "invalid"))
    if contract["scope"] != {
        "company": "汇沣电商",
        "brand": "BUW",
        "excluded_entities": ["PC", "六合通"],
    }:
        errors.append(_error("$.scope", "invalid"))
    if contract["allowed_results"] != list(RESULTS):
        errors.append(_error("$.allowed_results", "invalid"))
    if contract["reason_codes"] != list(REASON_CODES):
        errors.append(_error("$.reason_codes", "invalid"))
    expected_environment = {
        "allowed_child_names": list(CHILD_ENVIRONMENT_KEYS),
        "forbidden_parent_name_fragments": list(FORBIDDEN_ENVIRONMENT_FRAGMENTS),
    }
    if contract["environment"] != expected_environment:
        errors.append(_error("$.environment", "invalid"))
    expected_commands = {
        "exact_git_argv_templates": [
            ["git", "status", "--porcelain", "--untracked-files=all"],
            ["git", "rev-parse", "--verify", "COMMIT^{commit}"],
            ["git", "rev-parse", "COMMIT^{tree}"],
            ["git", "archive", "--format=tar", "COMMIT"],
        ],
        "exact_python_modules": [
            ["-m", "unittest", "Tests.test_stage15_local_python_rehearsal", "-v"],
            ["-m", "compileall", "-q", "Runtime", "Tests"],
        ],
        "exact_python_scripts": [
            [
                "Runtime/controlled_orchestrator.py",
                "--workflow",
                "Tests/Fixtures/nonproduction-readiness/local-python-store-anomaly-workflow.yaml",
                "--input",
                "Tests/Fixtures/nonproduction-readiness/local-python-store-anomaly-input.yaml",
            ],
            ["Tests/validate_aios_stage15_local_python_rehearsal.py"],
        ],
    }
    if contract["allowed_commands"] != expected_commands:
        errors.append(_error("$.allowed_commands", "invalid"))
    if contract["allowed_empty_capability_paths"] != list(
        ORDERED_ALLOWED_EMPTY_CAPABILITY_PATHS
    ):
        errors.append(_error("$.allowed_empty_capability_paths", "invalid"))
    if contract["fixture_ids"] != ["NR-LOCAL-PYTHON-REHEARSAL-001"]:
        errors.append(_error("$.fixture_ids", "invalid"))
    if contract["risk_states"] != RISK_STATES:
        errors.append(_error("$.risk_states", "invalid"))
    if contract["stage10_state"] != "BLOCKED / NO-GO":
        errors.append(_error("$.stage10_state", "invalid"))
    if contract["pr41_state"] != "draft_open_unmerged":
        errors.append(_error("$.pr41_state", "invalid"))
    if contract["authority_claims"] != {
        "cloud_capability_proven": False,
        "pilot_authorized": False,
        "production_ready": False,
        "release_authorized": False,
        "deployment_authorized": False,
        "risks_accepted": False,
    }:
        errors.append(_error("$.authority_claims", "AUTHORITY_CLAIM_DENIED"))
    if contract["maximum_claim"] != RESULTS[0]:
        errors.append(_error("$.maximum_claim", "invalid"))
    if not isinstance(contract["required_human_decisions"], list) or not all(
        isinstance(item, str) and item for item in contract["required_human_decisions"]
    ):
        errors.append(_error("$.required_human_decisions", "invalid"))
    if contract["external_actions_performed"] != []:
        errors.append(_error("$.external_actions_performed", "AUTHORITY_CLAIM_DENIED"))
    return errors


def validate_contract(contract: Any) -> list[str]:
    return _fail_closed(_validate_contract_impl, contract, "$")


def _walk_capabilities(value: Any, path: str, seen: set[int]) -> list[str]:
    if isinstance(value, (dict, list)):
        identity = id(value)
        if identity in seen:
            return [_error(path, "MALFORMED_INPUT")]
        seen.add(identity)
    errors: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if key in CAPABILITY_KEYS:
                if child_path not in ALLOWED_EMPTY_CAPABILITY_PATHS:
                    errors.append(_error(child_path, "CAPABILITY_FIELD_MISPLACED"))
                elif child != []:
                    errors.append(_error(child_path, "CAPABILITY_FIELD_NONEMPTY"))
            errors.extend(_walk_capabilities(child, child_path, seen))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            errors.extend(_walk_capabilities(child, f"{path}[{index}]", seen))
    return errors


def _validate_fixture_impl(fixture: Any) -> list[str]:
    keys = (
        "fixture_version",
        "scenario_id",
        "scope",
        "environment",
        "data_contract",
        "workflow",
        "expected",
        "requested_external_actions",
    )
    errors = _exact_keys(fixture, keys, "$")
    if errors:
        return errors
    if fixture["fixture_version"] != "aios_stage15_local_python_rehearsal_fixture/v1":
        errors.append(_error("$.fixture_version", "invalid"))
    if fixture["scenario_id"] != "NR-LOCAL-PYTHON-REHEARSAL-001":
        errors.append(_error("$.scenario_id", "invalid"))
    if fixture["scope"].get("company") != "汇沣电商":
        errors.append(_error("$.scope.company", "COMPANY_SCOPE_DENIED"))
    if fixture["scope"].get("brand") != "BUW":
        errors.append(_error("$.scope.brand", "BRAND_SCOPE_DENIED"))
    errors.extend(
        _exact_keys(
            fixture["scope"], ("company", "brand"), "$.scope"
        )
    )
    expected_environment = {
        "mode": "local_isolated_python_synthetic_only",
        "external_endpoints": [],
        "connectors": [],
        "credentials": [],
    }
    if fixture["environment"] != expected_environment:
        errors.append(_error("$.environment", "CAPABILITY_FIELD_NONEMPTY"))
    errors.extend(_walk_capabilities(fixture, "$", set()))
    expected_data = {
        "provenance": "repository_controlled_synthetic_fixture",
        "classification": "synthetic_non_personal",
        "personal_like_data": "none",
        "contactable": False,
        "routable": False,
        "retention": "task_local_until_verified_cleanup",
        "deletion": "deterministic_cleanup_required",
    }
    if fixture["data_contract"] != expected_data:
        errors.append(_error("$.data_contract", "NON_SYNTHETIC_DATA_DENIED"))
    if fixture["workflow"] != {
        "workflow_path": "Tests/Fixtures/nonproduction-readiness/local-python-store-anomaly-workflow.yaml",
        "input_path": "Tests/Fixtures/nonproduction-readiness/local-python-store-anomaly-input.yaml",
        "dry_run": True,
        "allow_external_writes": False,
    }:
        errors.append(_error("$.workflow", "invalid"))
    if fixture["expected"] != {
        "accountable_agent": "Retail",
        "status": "needs_approval",
        "pending_step": "assign_supervisor_response",
        "approval_status": "pending",
        "synthetic_only": True,
        "external_writes_performed": False,
    }:
        errors.append(_error("$.expected", "invalid"))
    if fixture["requested_external_actions"] != []:
        errors.append(_error("$.requested_external_actions", "AUTHORITY_CLAIM_DENIED"))
    return _dedupe(errors)


def validate_fixture(fixture: Any) -> list[str]:
    return _fail_closed(_validate_fixture_impl, fixture, "$")


def _validate_receipt_impl(receipt: Any) -> list[str]:
    errors = _exact_keys(receipt, RECEIPT_KEYS, "$")
    if errors:
        return errors
    constants = {
        "schema_version": "aios_stage15_local_python_rehearsal_receipt/v1",
        "company": "汇沣电商",
        "brand": "BUW",
        "stage": "Stage 15 / NR-01",
        "mode": "local_isolated_python_synthetic_only",
        "stage10_state": "BLOCKED / NO-GO",
        "pr41_state": "draft_open_unmerged",
        "cloud_capability_proven": False,
        "pilot_authorized": False,
        "production_ready": False,
        "release_authorized": False,
        "deployment_authorized": False,
        "risks_accepted": False,
    }
    for key, expected in constants.items():
        if receipt[key] != expected:
            errors.append(_error(f"$.{key}", "AUTHORITY_CLAIM_DENIED"))
    if receipt["result"] not in RESULTS:
        errors.append(_error("$.result", "invalid"))
    for field in ("source_commit", "source_tree"):
        if not isinstance(receipt[field], str) or not HEX_40.fullmatch(receipt[field]):
            errors.append(_error(f"$.{field}", "invalid"))
    if not isinstance(receipt["file_inventory_sha256"], str) or not HEX_64.fullmatch(
        receipt["file_inventory_sha256"]
    ):
        errors.append(_error("$.file_inventory_sha256", "invalid"))
    if receipt["normalized_smoke_sha256"] is not None and (
        not isinstance(receipt["normalized_smoke_sha256"], str)
        or not HEX_64.fullmatch(receipt["normalized_smoke_sha256"])
    ):
        errors.append(_error("$.normalized_smoke_sha256", "invalid"))
    runtime = receipt["python_runtime"]
    errors.extend(
        _exact_keys(
            runtime,
            (
                "implementation",
                "version",
                "executable_label",
                "user_site_enabled",
                "online_install_used",
            ),
            "$.python_runtime",
        )
    )
    if not isinstance(runtime, dict) or runtime.get("implementation") != "CPython":
        errors.append(_error("$.python_runtime", "invalid"))
    elif (
        runtime.get("executable_label") != "approved_local_python"
        or runtime.get("user_site_enabled") is not False
        or runtime.get("online_install_used") is not False
    ):
        errors.append(_error("$.python_runtime", "invalid"))
    errors.extend(
        _exact_keys(receipt["local_dependencies"], ("PyYAML",), "$.local_dependencies")
    )
    if receipt["fixture_ids"] != ["NR-LOCAL-PYTHON-REHEARSAL-001"]:
        errors.append(_error("$.fixture_ids", "invalid"))
    checksums = receipt["fixture_checksums"]
    if (
        not isinstance(checksums, dict)
        or tuple(checksums) != ("NR-LOCAL-PYTHON-REHEARSAL-001",)
        or not isinstance(checksums["NR-LOCAL-PYTHON-REHEARSAL-001"], str)
        or not HEX_64.fullmatch(checksums["NR-LOCAL-PYTHON-REHEARSAL-001"])
    ):
        errors.append(_error("$.fixture_checksums", "invalid"))
    if not isinstance(receipt["ordered_checks"], list):
        errors.append(_error("$.ordered_checks", "invalid"))
    if not isinstance(receipt["smoke_result"], dict):
        errors.append(_error("$.smoke_result", "invalid"))
    for field, keys in (
        ("network_guard", ("active", "attempted_operations")),
        (
            "material_scan",
            (
                "credentials_found",
                "real_data_found",
                "external_endpoints_found",
                "nonempty_connectors_found",
                "infrastructure_material_found",
            ),
        ),
        (
            "cleanup",
            (
                "execution_directory_removed",
                "bytecode_directory_removed",
                "evidence_directory_preserved",
                "repository_unchanged",
            ),
        ),
    ):
        errors.extend(_exact_keys(receipt[field], keys, f"$.{field}"))
    if not isinstance(receipt["network_guard"].get("active"), bool) or not isinstance(
        receipt["network_guard"].get("attempted_operations"), list
    ):
        errors.append(_error("$.network_guard", "invalid"))
    if not all(
        type(receipt["material_scan"].get(key)) is bool
        for key in receipt["material_scan"]
    ):
        errors.append(_error("$.material_scan", "invalid"))
    if not all(type(receipt["cleanup"].get(key)) is bool for key in receipt["cleanup"]):
        errors.append(_error("$.cleanup", "invalid"))
    if receipt["risk_states"] != RISK_STATES:
        errors.append(_error("$.risk_states", "invalid"))
    if receipt["external_actions_performed"] != []:
        errors.append(_error("$.external_actions_performed", "AUTHORITY_CLAIM_DENIED"))
    if not isinstance(receipt["reason_codes"], list) or any(
        code not in REASON_CODES for code in receipt["reason_codes"]
    ):
        errors.append(_error("$.reason_codes", "invalid"))
    for field in ("evidence_refs", "required_human_decisions"):
        if not isinstance(receipt[field], list) or not all(
            isinstance(item, str) for item in receipt[field]
        ):
            errors.append(_error(f"$.{field}", "invalid"))
    if receipt["result"] == RESULTS[0]:
        if receipt["reason_codes"]:
            errors.append(_error("$.reason_codes", "must_be_empty_for_pass"))
        if receipt["normalized_smoke_sha256"] is None:
            errors.append(_error("$.normalized_smoke_sha256", "required_for_pass"))
        if any(receipt["material_scan"].values()):
            errors.append(_error("$.material_scan", "must_be_false_for_pass"))
        expected_cleanup = {
            "execution_directory_removed": True,
            "bytecode_directory_removed": True,
            "evidence_directory_preserved": False,
            "repository_unchanged": True,
        }
        if receipt["cleanup"] != expected_cleanup:
            errors.append(_error("$.cleanup", "required_for_pass"))
    elif not receipt["reason_codes"]:
        errors.append(_error("$.reason_codes", "required_for_non_pass"))
    rendered = json.dumps(receipt, ensure_ascii=False, default=str)
    if str(Path.home()) in rendered:
        errors.append(_error("$", "SECRET_LIKE_MATERIAL_DENIED"))
    return _dedupe(errors)


def validate_receipt(receipt: Any) -> list[str]:
    return _fail_closed(_validate_receipt_impl, receipt, "$")


def _write_network_guard(guard_path: Path, log_path: Path) -> None:
    guard_path.mkdir(parents=True, exist_ok=True)
    source = '''\
import os
import socket

class NetworkOperationDenied(RuntimeError):
    pass

_LOG_PATH = os.environ.get("AIOS_NETWORK_GUARD_LOG", "")

def _record(operation):
    if not _LOG_PATH:
        return
    descriptor = os.open(_LOG_PATH, os.O_APPEND | os.O_CREAT | os.O_WRONLY, 0o600)
    try:
        os.write(descriptor, (operation + "\\n").encode("ascii"))
    finally:
        os.close(descriptor)

def _deny(operation):
    def denied(*args, **kwargs):
        _record(operation)
        raise NetworkOperationDenied("network operation denied by Stage 15 local rehearsal")
    return denied

def _deny_socket(*args, **kwargs):
    _record("socket.socket")
    raise NetworkOperationDenied("network operation denied by Stage 15 local rehearsal")

socket.socket = _deny_socket
socket.SocketType = _deny_socket
socket.socketpair = _deny("socket.socketpair")
socket.fromfd = _deny("socket.fromfd")
socket.create_connection = _deny("socket.create_connection")
socket.getaddrinfo = _deny("socket.getaddrinfo")
socket.gethostbyname = _deny("socket.gethostbyname")
socket.gethostbyname_ex = _deny("socket.gethostbyname_ex")
socket.gethostbyaddr = _deny("socket.gethostbyaddr")
socket.getnameinfo = _deny("socket.getnameinfo")
'''
    (guard_path / "sitecustomize.py").write_text(source, encoding="utf-8")
    log_path.write_text("", encoding="utf-8")


def build_sanitized_environment(
    source: Mapping[str, str],
    *,
    temporary_root: Path,
    guard_path: Path,
) -> dict[str, str]:
    """Build a minimal child environment without retaining sensitive values."""
    try:
        names = [str(name) for name in source]
    except Exception as exc:
        raise ValueError("MALFORMED_INPUT") from exc
    for name in names:
        upper = name.upper()
        if any(fragment in upper for fragment in FORBIDDEN_ENVIRONMENT_FRAGMENTS):
            raise ValueError("CREDENTIAL_LIKE_ENVIRONMENT_PRESENT")
    temp_root = Path(temporary_root).resolve()
    guard = Path(guard_path).resolve()
    if guard == temp_root or temp_root not in guard.parents:
        raise ValueError("ENVIRONMENT_NOT_ALLOWLISTED")
    log_path = guard / "network-attempts.log"
    _write_network_guard(guard, log_path)
    lang = str(source.get("LANG") or "C.UTF-8")
    environment = {
        "PATH": str(source.get("PATH") or "/usr/bin:/bin"),
        "LANG": lang,
        "LC_ALL": str(source.get("LC_ALL") or lang),
        "TMPDIR": str(temp_root),
        "PYTHONNOUSERSITE": "1",
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONPATH": str(guard),
        "AIOS_NETWORK_GUARD_LOG": str(log_path),
    }
    if tuple(environment) != CHILD_ENVIRONMENT_KEYS:
        raise ValueError("ENVIRONMENT_NOT_ALLOWLISTED")
    return environment


def _run_local(
    argv: Sequence[str], cwd: Path, *, binary: bool = False, timeout: int = 30
) -> subprocess.CompletedProcess:
    return subprocess.run(
        list(argv),
        cwd=cwd,
        text=not binary,
        capture_output=True,
        check=False,
        timeout=timeout,
    )


def _require_clean_repository(repository_root: Path) -> None:
    completed = _run_local(
        ["git", "status", "--porcelain", "--untracked-files=all"],
        repository_root,
    )
    if completed.returncode != 0:
        raise ValueError("SOURCE_COMMIT_INVALID")
    if completed.stdout.strip():
        raise ValueError("SOURCE_WORKTREE_DIRTY")


def _safe_member_path(name: str) -> PurePosixPath:
    candidate = PurePosixPath(name)
    if candidate.is_absolute() or ".." in candidate.parts or not candidate.parts:
        raise ValueError("ARCHIVE_MEMBER_UNSAFE")
    return candidate


def _extract_archive(archive: bytes, execution_root: Path) -> None:
    execution_root.mkdir(parents=True, exist_ok=False)
    with tarfile.open(fileobj=io.BytesIO(archive), mode="r:") as handle:
        for member in handle.getmembers():
            relative = _safe_member_path(member.name)
            if (
                member.issym()
                or member.islnk()
                or member.ischr()
                or member.isblk()
                or member.isfifo()
                or not (member.isdir() or member.isfile())
            ):
                raise ValueError("ARCHIVE_MEMBER_UNSAFE")
            destination = execution_root.joinpath(*relative.parts)
            resolved_parent = destination.parent.resolve()
            if execution_root.resolve() not in (
                resolved_parent,
                *resolved_parent.parents,
            ):
                raise ValueError("ARCHIVE_MEMBER_UNSAFE")
            if member.isdir():
                destination.mkdir(parents=True, exist_ok=True)
                continue
            destination.parent.mkdir(parents=True, exist_ok=True)
            extracted = handle.extractfile(member)
            if extracted is None:
                raise ValueError("ARCHIVE_MEMBER_UNSAFE")
            destination.write_bytes(extracted.read())


def _inventory(root: Path) -> tuple[list[dict[str, Any]], str]:
    records = []
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        relative = path.relative_to(root).as_posix()
        data = path.read_bytes()
        records.append(
            {
                "path": relative,
                "size": len(data),
                "sha256": hashlib.sha256(data).hexdigest(),
            }
        )
    canonical = json.dumps(
        records, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return records, hashlib.sha256(canonical).hexdigest()


def scan_rehearsal_material(
    *,
    fixture: Mapping[str, Any],
    selected_paths: Sequence[Path],
    inventory_paths: Sequence[str] | Any,
) -> dict[str, bool]:
    """Compute bounded material findings from the exact execution assets."""
    findings = {
        "credentials_found": False,
        "real_data_found": False,
        "external_endpoints_found": False,
        "nonempty_connectors_found": False,
        "infrastructure_material_found": False,
    }
    try:
        environment = fixture["environment"]
        findings["credentials_found"] = environment["credentials"] != []
        findings["nonempty_connectors_found"] = environment["connectors"] != []
        findings["external_endpoints_found"] = environment["external_endpoints"] != []
        contract = fixture["data_contract"]
        if (
            contract["provenance"] != "repository_controlled_synthetic_fixture"
            or contract["classification"] != "synthetic_non_personal"
            or contract["personal_like_data"] != "none"
            or contract["contactable"] is not False
            or contract["routable"] is not False
        ):
            findings["real_data_found"] = True
    except (KeyError, TypeError):
        findings["real_data_found"] = True

    credential_value = re.compile(
        r"(?im)^\s*(?:password|passwd|secret|token|api[_-]?key|credential)\s*[:=]\s*"
        r"(?!\[\]|\{\}|null\b|none\b|false\b|['\"]?synthetic(?:[-_:/]|$))\S+"
    )
    private_key = re.compile(
        "-----BEGIN " + r"(?:RSA |EC |OPENSSH )?PRIVATE KEY-----"
    )
    external_locator = re.compile(
        r"(?i)\b(?:https?|ftp)://|"
        r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b|"
        r"(?<![A-Z0-9])(?:\d{1,3}\.){3}\d{1,3}(?![A-Z0-9])"
    )
    workflow_document: dict[str, Any] | None = None
    input_document: dict[str, Any] | None = None
    for selected in selected_paths:
        path = Path(selected)
        if not path.is_file() or path.is_symlink():
            raise ValueError("EXTERNAL_LOCATOR_DENIED")
        text = path.read_text(encoding="utf-8")
        if path.suffix.lower() == ".py":
            try:
                compile(text, path.name, "exec")
            except (OSError, SyntaxError, UnicodeError) as exc:
                raise ValueError("MALFORMED_INPUT") from exc
        if private_key.search(text) or credential_value.search(text):
            findings["credentials_found"] = True
        if external_locator.search(text):
            findings["external_endpoints_found"] = True
        if path.name == "local-python-store-anomaly-workflow.yaml":
            workflow_document = yaml.safe_load(text)
        elif path.name == "local-python-store-anomaly-input.yaml":
            input_document = yaml.safe_load(text)

    try:
        if not isinstance(workflow_document, dict) or not isinstance(input_document, dict):
            findings["real_data_found"] = True
        else:
            role_values = list(workflow_document.get("informed_roles", []))
            for step in workflow_document.get("steps", []):
                if isinstance(step, dict):
                    for field in ("approval_owner", "escalate_to"):
                        if field in step:
                            role_values.append(step[field])
            for gate in workflow_document.get("approval_gates", []):
                if isinstance(gate, dict):
                    role_values.extend(gate.get("approvers", []))
            if not role_values or any(
                not isinstance(role, str) or not role.startswith("SYNTHETIC-ROLE-")
                for role in role_values
            ):
                findings["real_data_found"] = True
            metadata = input_document.get("metadata", {})
            inputs = input_document.get("inputs", {})
            if (
                metadata.get("data_classification") != "synthetic"
                or metadata.get("company") != "汇沣电商"
                or not str(metadata.get("business_entity", "")).startswith(
                    "BUW:SYNTHETIC-STORE-"
                )
                or inputs.get("brand") != "BUW"
                or not str(inputs.get("store_code", "")).startswith(
                    "SYNTHETIC-STORE-"
                )
            ):
                findings["real_data_found"] = True
    except (TypeError, ValueError):
        findings["real_data_found"] = True

    infrastructure_name = re.compile(
        r"(?i)(?:^|/)(?:Dockerfile|docker-compose[^/]*\.ya?ml|Chart\.yaml|"
        r"kustomization\.ya?ml|serverless\.ya?ml|cdk\.json|[^/]+\.tf)$"
    )
    try:
        findings["infrastructure_material_found"] = any(
            bool(infrastructure_name.search(str(path))) for path in inventory_paths
        )
    except Exception as exc:
        raise ValueError("MALFORMED_INPUT") from exc
    return findings


def export_exact_candidate(
    *,
    repository_root: Path,
    source_commit: str,
    execution_root: Path,
) -> dict[str, Any]:
    """Export one clean local Git commit and return its canonical inventory."""
    root = Path(repository_root).resolve()
    execution = Path(execution_root).resolve()
    if not HEX_40.fullmatch(str(source_commit)):
        raise ValueError("SOURCE_COMMIT_INVALID")
    _require_clean_repository(root)
    verified = _run_local(
        ["git", "rev-parse", "--verify", f"{source_commit}^{{commit}}"], root
    )
    if verified.returncode != 0 or verified.stdout.strip() != source_commit:
        raise ValueError("SOURCE_COMMIT_INVALID")
    tree = _run_local(["git", "rev-parse", f"{source_commit}^{{tree}}"], root)
    if tree.returncode != 0 or not HEX_40.fullmatch(tree.stdout.strip()):
        raise ValueError("SOURCE_TREE_MISMATCH")
    archived = _run_local(
        ["git", "archive", "--format=tar", source_commit],
        root,
        binary=True,
        timeout=60,
    )
    if archived.returncode != 0:
        raise ValueError("SOURCE_COMMIT_INVALID")
    _extract_archive(archived.stdout, execution)
    records, inventory_hash = _inventory(execution)
    if not records:
        raise ValueError("FILE_INVENTORY_MISMATCH")
    return {
        "source_commit": source_commit,
        "source_tree": tree.stdout.strip(),
        "file_inventory": records,
        "file_inventory_sha256": inventory_hash,
    }


def _redact(text: str, *, cwd: Path) -> str:
    rendered = str(text)
    for value, replacement in (
        (str(Path.home()), "<home>"),
        (str(cwd.resolve()), "<execution_root>"),
        (tempfile.gettempdir(), "<temporary_root>"),
    ):
        if value:
            rendered = rendered.replace(value, replacement)
    return rendered[:16384]


def _allowed_command(argv: Sequence[str], cwd: Path) -> bool:
    if not argv or not all(isinstance(item, str) and item for item in argv):
        return False
    if argv[0] == "git":
        if list(argv) == ["git", "status", "--porcelain", "--untracked-files=all"]:
            return True
        if len(argv) == 4 and argv[:3] == ["git", "rev-parse", "--verify"]:
            return bool(re.fullmatch(r"[0-9a-f]{40}\^\{commit\}", argv[3]))
        if len(argv) == 3 and argv[:2] == ["git", "rev-parse"]:
            return bool(re.fullmatch(r"[0-9a-f]{40}\^\{tree\}", argv[2]))
        if len(argv) == 4 and argv[:3] == ["git", "archive", "--format=tar"]:
            return bool(HEX_40.fullmatch(argv[3]))
        return False
    try:
        is_python = Path(argv[0]).resolve() == Path(sys.executable).resolve()
    except OSError:
        return False
    if not is_python or len(argv) < 2:
        return False
    if list(argv[1:]) in (
        ["-m", "unittest", "Tests.test_stage15_local_python_rehearsal", "-v"],
        ["-m", "compileall", "-q", "Runtime", "Tests"],
    ):
        return True
    if argv[1] == "-m":
        return False
    try:
        script = Path(argv[1]).resolve()
        relative = script.relative_to(cwd.resolve()).as_posix()
    except (OSError, ValueError):
        return False
    if relative == "Tests/validate_aios_stage15_local_python_rehearsal.py":
        return len(argv) == 2
    if relative != "Runtime/controlled_orchestrator.py" or len(argv) != 6:
        return False
    if argv[2] != "--workflow" or argv[4] != "--input":
        return False
    expected = (
        "Tests/Fixtures/nonproduction-readiness/local-python-store-anomaly-workflow.yaml",
        "Tests/Fixtures/nonproduction-readiness/local-python-store-anomaly-input.yaml",
    )
    try:
        selected = (
            Path(argv[3]).resolve().relative_to(cwd.resolve()).as_posix(),
            Path(argv[5]).resolve().relative_to(cwd.resolve()).as_posix(),
        )
    except (OSError, ValueError):
        return False
    return selected == expected


def _network_log_path(environment: Mapping[str, str]) -> Path:
    guard = Path(environment.get("PYTHONPATH", "")).resolve()
    log_path = Path(environment.get("AIOS_NETWORK_GUARD_LOG", "")).resolve()
    if log_path.parent != guard or log_path.name != "network-attempts.log":
        raise ValueError("ENVIRONMENT_NOT_ALLOWLISTED")
    return log_path


def _read_network_attempts(log_path: Path) -> list[str]:
    if not log_path.is_file() or log_path.is_symlink():
        raise ValueError("ENVIRONMENT_NOT_ALLOWLISTED")
    attempts = []
    for line in log_path.read_text(encoding="utf-8").splitlines():
        operation = line.strip()
        if not re.fullmatch(r"socket\.[a-z_]+", operation):
            raise ValueError("MALFORMED_INPUT")
        attempts.append(operation)
    return _dedupe(attempts)


def run_guarded_command(
    argv: Sequence[str],
    *,
    cwd: Path,
    environment: Mapping[str, str],
    timeout_seconds: int,
) -> dict[str, Any]:
    """Run an allowlisted local command without a shell or inherited environment."""
    if not _allowed_command(argv, Path(cwd)):
        return {
            "status": "denied",
            "returncode": None,
            "stdout": "",
            "stderr": "",
            "reason_codes": ["COMMAND_NOT_ALLOWLISTED"],
        }
    if tuple(environment) != CHILD_ENVIRONMENT_KEYS:
        return {
            "status": "denied",
            "returncode": None,
            "stdout": "",
            "stderr": "",
            "reason_codes": ["ENVIRONMENT_NOT_ALLOWLISTED"],
        }
    try:
        network_log = _network_log_path(environment)
        network_log.write_text("", encoding="utf-8")
    except (OSError, ValueError):
        return {
            "status": "denied",
            "returncode": None,
            "stdout": "",
            "stderr": "",
            "reason_codes": ["ENVIRONMENT_NOT_ALLOWLISTED"],
            "network_attempts": [],
        }
    try:
        completed = subprocess.run(
            list(argv),
            cwd=Path(cwd),
            env=dict(environment),
            text=True,
            capture_output=True,
            check=False,
            timeout=timeout_seconds,
            shell=False,
        )
    except subprocess.TimeoutExpired:
        attempts = _read_network_attempts(network_log)
        return {
            "status": "blocked",
            "returncode": None,
            "stdout": "",
            "stderr": "",
            "reason_codes": ["COMMAND_TIMEOUT"],
            "network_attempts": attempts,
        }
    stderr = _redact(completed.stderr, cwd=Path(cwd))
    stdout = _redact(completed.stdout, cwd=Path(cwd))
    attempts = _read_network_attempts(network_log)
    if attempts or "NetworkOperationDenied" in stderr:
        return {
            "status": "denied",
            "returncode": completed.returncode,
            "stdout": stdout,
            "stderr": stderr,
            "reason_codes": ["NETWORK_OPERATION_ATTEMPTED"],
            "network_attempts": attempts,
        }
    return {
        "status": "completed" if completed.returncode == 0 else "blocked",
        "returncode": completed.returncode,
        "stdout": stdout,
        "stderr": stderr,
        "reason_codes": []
        if completed.returncode == 0
        else ["UNEXPECTED_RUNTIME_FAILURE"],
        "network_attempts": [],
    }


def normalize_smoke_output(output: Mapping[str, Any]) -> dict[str, Any]:
    """Remove ephemeral fields and canonicalize a synthetic smoke result."""
    def normalize(value: Any) -> Any:
        if isinstance(value, Mapping):
            return {
                str(key): normalize(child)
                for key, child in sorted(value.items(), key=lambda item: str(item[0]))
                if str(key) not in EPHEMERAL_KEYS
            }
        if isinstance(value, list):
            return [normalize(item) for item in value]
        if isinstance(value, str):
            if value.startswith(str(Path.home())) or value.startswith(tempfile.gettempdir()):
                return "<ephemeral_path>"
            return value
        return value

    try:
        normalized = normalize(copy.deepcopy(dict(output)))
    except Exception as exc:
        raise ValueError("MALFORMED_INPUT") from exc
    if not isinstance(normalized, dict):
        raise ValueError("MALFORMED_INPUT")
    return normalized


def _fixture_checksum(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def empty_receipt(
    *, result: str, source_commit: str, source_tree: str, reason_codes: Sequence[str]
) -> dict[str, Any]:
    now = _utc_now()
    try:
        dependency = importlib.metadata.version("PyYAML")
    except importlib.metadata.PackageNotFoundError:
        dependency = "blocked"
    return {
        "schema_version": "aios_stage15_local_python_rehearsal_receipt/v1",
        "run_id": f"STAGE15-LOCAL-{source_commit[:12] or 'UNKNOWN'}",
        "started_at_utc": now,
        "finished_at_utc": now,
        "company": "汇沣电商",
        "brand": "BUW",
        "stage": "Stage 15 / NR-01",
        "mode": "local_isolated_python_synthetic_only",
        "result": result,
        "source_commit": source_commit if HEX_40.fullmatch(source_commit) else "0" * 40,
        "source_tree": source_tree if HEX_40.fullmatch(source_tree) else "0" * 40,
        "file_inventory_sha256": "0" * 64,
        "python_runtime": {
            "implementation": platform.python_implementation(),
            "version": platform.python_version(),
            "executable_label": "approved_local_python",
            "user_site_enabled": False,
            "online_install_used": False,
        },
        "local_dependencies": {"PyYAML": dependency},
        "fixture_ids": ["NR-LOCAL-PYTHON-REHEARSAL-001"],
        "fixture_checksums": {"NR-LOCAL-PYTHON-REHEARSAL-001": "0" * 64},
        "ordered_checks": [],
        "smoke_result": {},
        "normalized_smoke_sha256": None,
        "network_guard": {"active": True, "attempted_operations": []},
        "material_scan": {
            "credentials_found": False,
            "real_data_found": False,
            "external_endpoints_found": False,
            "nonempty_connectors_found": False,
            "infrastructure_material_found": False,
        },
        "cleanup": {
            "execution_directory_removed": True,
            "bytecode_directory_removed": True,
            "evidence_directory_preserved": False,
            "repository_unchanged": True,
        },
        "risk_states": dict(RISK_STATES),
        "stage10_state": "BLOCKED / NO-GO",
        "pr41_state": "draft_open_unmerged",
        "cloud_capability_proven": False,
        "pilot_authorized": False,
        "production_ready": False,
        "release_authorized": False,
        "deployment_authorized": False,
        "risks_accepted": False,
        "external_actions_performed": [],
        "reason_codes": _dedupe(reason_codes),
        "evidence_refs": [],
        "required_human_decisions": [
            "Stone independent boundary and evidence review",
            "Tony decision on any later PR lifecycle, risk, pilot, release or deployment action",
        ],
    }


def cleanup_task_path(target: Path, temporary_root: Path, run_id: str) -> bool:
    """Remove only a marked child of the current rehearsal temporary root."""
    root = Path(temporary_root).resolve()
    candidate = Path(target).resolve()
    system_temp = Path(tempfile.gettempdir()).resolve()
    marker = root / MARKER_NAME
    if root == system_temp or system_temp not in root.parents:
        raise ValueError("CLEANUP_TARGET_UNSAFE")
    if candidate == root or root not in candidate.parents:
        raise ValueError("CLEANUP_TARGET_UNSAFE")
    if candidate in {Path("/").resolve(), Path.home().resolve()}:
        raise ValueError("CLEANUP_TARGET_UNSAFE")
    if not marker.is_file() or marker.read_text(encoding="utf-8") != run_id:
        raise ValueError("CLEANUP_TARGET_UNSAFE")
    if candidate.exists():
        if candidate.is_dir() and not candidate.is_symlink():
            shutil.rmtree(candidate)
        else:
            candidate.unlink()
    if candidate.exists():
        raise ValueError("CLEANUP_NOT_VERIFIED")
    return True


def _reason_from_exception(exc: Exception) -> str:
    text = str(exc)
    for code in REASON_CODES:
        if code in text:
            return code
    return "UNEXPECTED_RUNTIME_FAILURE"


def _canonical_sha256(value: Any) -> str:
    encoded = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def run_rehearsal(
    *,
    repository_root: Path,
    source_commit: str,
    contract_path: Path,
    fixture_path: Path,
) -> dict[str, Any]:
    """Execute one bounded local synthetic rehearsal and always return a receipt."""
    root = Path(repository_root).resolve()
    receipt = empty_receipt(
        result=RESULTS[2],
        source_commit=str(source_commit),
        source_tree="0" * 40,
        reason_codes=["UNEXPECTED_RUNTIME_FAILURE"],
    )
    receipt["started_at_utc"] = _utc_now()
    before_status = ""
    task_root: Path | None = None
    execution: Path | None = None
    bytecode: Path | None = None
    guard: Path | None = None
    cleanup_errors: list[str] = []
    try:
        _require_clean_repository(root)
        before_status = ""
        try:
            contract_relative = Path(contract_path).resolve().relative_to(root)
            fixture_relative = Path(fixture_path).resolve().relative_to(root)
        except ValueError as exc:
            raise ValueError("EXTERNAL_LOCATOR_DENIED") from exc

        run_id = receipt["run_id"]
        task_root = Path(tempfile.mkdtemp(prefix="buw-stage15-local-rehearsal-"))
        (task_root / MARKER_NAME).write_text(run_id, encoding="utf-8")
        execution = task_root / "execution"
        bytecode = task_root / "bytecode"
        guard = task_root / "guard"
        bytecode.mkdir()

        export = export_exact_candidate(
            repository_root=root,
            source_commit=str(source_commit),
            execution_root=execution,
        )
        receipt["source_tree"] = export["source_tree"]
        receipt["file_inventory_sha256"] = export["file_inventory_sha256"]

        exported_contract = execution / contract_relative
        exported_fixture = execution / fixture_relative
        contract = load_closed_yaml(exported_contract)
        fixture = load_closed_yaml(exported_fixture)
        contract_errors = validate_contract(contract)
        fixture_errors = validate_fixture(fixture)
        if contract_errors or fixture_errors:
            combined = contract_errors + fixture_errors
            reason = _reason_from_exception(ValueError(" ".join(combined)))
            raise ValueError(reason)

        workflow = execution / fixture["workflow"]["workflow_path"]
        payload = execution / fixture["workflow"]["input_path"]
        selected_material = (
            exported_contract,
            exported_fixture,
            workflow,
            payload,
            execution / "Runtime/stage15_local_python_rehearsal.py",
            execution / "Runtime/controlled_orchestrator.py",
        )
        for selected in selected_material:
            resolved = selected.resolve()
            if execution.resolve() not in resolved.parents or not resolved.is_file():
                raise ValueError("EXTERNAL_LOCATOR_DENIED")
        material_scan = scan_rehearsal_material(
            fixture=fixture,
            selected_paths=selected_material,
            inventory_paths=(record["path"] for record in export["file_inventory"]),
        )
        receipt["material_scan"] = material_scan
        if material_scan["credentials_found"]:
            raise ValueError("SECRET_LIKE_MATERIAL_DENIED")
        if material_scan["real_data_found"]:
            raise ValueError("NON_SYNTHETIC_DATA_DENIED")
        if material_scan["external_endpoints_found"]:
            raise ValueError("EXTERNAL_LOCATOR_DENIED")
        if material_scan["nonempty_connectors_found"]:
            raise ValueError("CAPABILITY_FIELD_NONEMPTY")
        if material_scan["infrastructure_material_found"]:
            raise ValueError("INFRASTRUCTURE_MATERIAL_DENIED")

        try:
            dependency = importlib.metadata.version("PyYAML")
        except importlib.metadata.PackageNotFoundError as exc:
            raise ValueError("LOCAL_DEPENDENCY_UNAVAILABLE") from exc
        receipt["local_dependencies"] = {"PyYAML": dependency}
        receipt["fixture_checksums"] = {
            "NR-LOCAL-PYTHON-REHEARSAL-001": _fixture_checksum(exported_fixture)
        }

        environment = build_sanitized_environment(
            os.environ,
            temporary_root=task_root,
            guard_path=guard,
        )
        environment["TMPDIR"] = str(bytecode)
        command = [
            sys.executable,
            str(execution / "Runtime/controlled_orchestrator.py"),
            "--workflow",
            str(workflow),
            "--input",
            str(payload),
        ]
        first = run_guarded_command(
            command,
            cwd=execution,
            environment=environment,
            timeout_seconds=30,
        )
        second = run_guarded_command(
            command,
            cwd=execution,
            environment=environment,
            timeout_seconds=30,
        )
        receipt["network_guard"]["attempted_operations"] = _dedupe(
            list(first.get("network_attempts", []))
            + list(second.get("network_attempts", []))
        )
        for run in (first, second):
            if run["status"] != "completed":
                raise ValueError(run["reason_codes"][0])
        first_output = json.loads(first["stdout"])
        second_output = json.loads(second["stdout"])
        normalized_first = normalize_smoke_output(first_output)
        normalized_second = normalize_smoke_output(second_output)
        if normalized_first != normalized_second:
            raise ValueError("SMOKE_OUTPUT_NONDETERMINISTIC")
        expected = fixture["expected"]
        actual = {
            "accountable_agent": first_output.get("agent"),
            "status": first_output.get("status"),
            "pending_step": first_output.get("domain_payload", {}).get("pending_step"),
            "approval_status": first_output.get("approval_request", {}).get(
                "approval_status"
            ),
            "synthetic_only": first_output.get("domain_payload", {}).get(
                "synthetic_only"
            ),
            "external_writes_performed": first_output.get("domain_payload", {}).get(
                "external_writes_performed"
            ),
        }
        if actual != expected:
            raise ValueError("AUTHORITY_CLAIM_DENIED")
        receipt["smoke_result"] = normalized_first
        receipt["normalized_smoke_sha256"] = _canonical_sha256(normalized_first)
        receipt["ordered_checks"] = [
            "exact_candidate_export_verified",
            "closed_contract_verified",
            "synthetic_fixture_verified",
            "local_dependency_verified_without_install",
            "minimal_environment_and_network_guard_active",
            "controlled_orchestrator_smoke_one_passed",
            "controlled_orchestrator_smoke_two_passed",
            "normalized_smoke_output_deterministic",
            "authority_ceiling_preserved",
        ]
        receipt["evidence_refs"] = [
            contract_relative.as_posix(),
            fixture_relative.as_posix(),
            fixture["workflow"]["workflow_path"],
            fixture["workflow"]["input_path"],
        ]
        receipt["result"] = RESULTS[0]
        receipt["reason_codes"] = []
    except Exception as exc:
        reason = _reason_from_exception(exc)
        receipt["result"] = RESULTS[1] if reason in POLICY_DENIAL_CODES else RESULTS[2]
        receipt["reason_codes"] = [reason]
        receipt["smoke_result"] = {}
        receipt["normalized_smoke_sha256"] = None
    finally:
        if task_root is not None and task_root.exists():
            run_id = receipt["run_id"]
            for path, field in (
                (execution, "execution_directory_removed"),
                (bytecode, "bytecode_directory_removed"),
                (guard, None),
            ):
                if path is None:
                    continue
                try:
                    cleanup_task_path(path, task_root, run_id)
                    if field:
                        receipt["cleanup"][field] = True
                except Exception as exc:
                    cleanup_errors.append(_reason_from_exception(exc))
                    if field:
                        receipt["cleanup"][field] = False
            marker = task_root / MARKER_NAME
            try:
                if marker.is_file():
                    marker.unlink()
                task_root.rmdir()
            except OSError:
                cleanup_errors.append("CLEANUP_NOT_VERIFIED")
        after = _run_local(
            ["git", "status", "--porcelain", "--untracked-files=all"], root
        )
        repository_unchanged = after.returncode == 0 and after.stdout.strip() == before_status
        receipt["cleanup"]["repository_unchanged"] = repository_unchanged
        if not repository_unchanged:
            cleanup_errors.append("REPOSITORY_CHANGED")
        if cleanup_errors:
            receipt["result"] = RESULTS[2]
            receipt["reason_codes"] = _dedupe(
                list(receipt["reason_codes"]) + cleanup_errors
            )
        receipt["finished_at_utc"] = _utc_now()
    schema_errors = validate_receipt(receipt)
    if schema_errors:
        receipt["result"] = RESULTS[1]
        receipt["reason_codes"] = _dedupe(
            list(receipt.get("reason_codes", [])) + ["RECEIPT_SCHEMA_INVALID"]
        )
    return receipt


def main() -> int:
    if len(sys.argv) != 5 or sys.argv[1] != "--repository" or sys.argv[3] != "--commit":
        print("usage: stage15_local_python_rehearsal.py --repository ROOT --commit SHA")
        return 2
    root = Path(sys.argv[2]).resolve()
    receipt = run_rehearsal(
        repository_root=root,
        source_commit=sys.argv[4],
        contract_path=root / CONTRACT_PATH,
        fixture_path=root / FIXTURE_PATH,
    )
    print(json.dumps(receipt, ensure_ascii=False, indent=2))
    return 0 if receipt["result"] == RESULTS[0] else 2


if __name__ == "__main__":
    raise SystemExit(main())
