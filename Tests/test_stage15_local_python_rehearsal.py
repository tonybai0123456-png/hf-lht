from __future__ import annotations

import copy
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

import yaml


ROOT = Path(__file__).resolve().parents[1]
RUNNER_PATH = ROOT / "Runtime/stage15_local_python_rehearsal.py"
CONTRACT_PATH = (
    ROOT / "Governance/AIOS-Stage15-Local-Python-Rehearsal-Contract-v1.yaml"
)
SCHEMA_PATH = (
    ROOT
    / "Governance/AIOS-Stage15-Local-Python-Rehearsal-Receipt-Schema-v1.yaml"
)
RECEIPT_PATH = (
    ROOT / "Governance/AIOS-Stage15-Local-Python-Rehearsal-Receipt-v1.json"
)
MANDATORY_RETURN_PATH = (
    ROOT
    / "Governance/AIOS-Stage15-Local-Python-Rehearsal-Mandatory-Return-v1.yaml"
)
FIXTURE_PATH = (
    ROOT
    / "Tests/Fixtures/nonproduction-readiness/local-python-rehearsal-synthetic.yaml"
)
SYNTHETIC_WORKFLOW_PATH = (
    ROOT
    / "Tests/Fixtures/nonproduction-readiness/local-python-store-anomaly-workflow.yaml"
)
SYNTHETIC_INPUT_PATH = (
    ROOT
    / "Tests/Fixtures/nonproduction-readiness/local-python-store-anomaly-input.yaml"
)
VALIDATOR_PATH = ROOT / "Tests/validate_aios_stage15_local_python_rehearsal.py"
GUIDE_PATH = ROOT / "Tests/AIOS-Stage15-Local-Python-Rehearsal-Validation.md"

EXPECTED_RESULTS = (
    "local_python_test_deployment_rehearsal_passed_not_cloud_proof",
    "local_python_test_deployment_rehearsal_denied",
    "local_python_test_deployment_rehearsal_blocked",
)
EXPECTED_REASON_CODES = (
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


def load_runner():
    spec = importlib.util.spec_from_file_location("stage15_rehearsal", RUNNER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Stage 15 local rehearsal runner cannot be loaded")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def git(cwd: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise AssertionError(completed.stderr)
    return completed.stdout.strip()


def init_repository(root: Path) -> str:
    git(root, "init", "-q")
    git(root, "config", "user.name", "Synthetic Test")
    git(root, "config", "user.email", "synthetic.invalid@example.invalid")
    git(root, "add", ".")
    git(root, "commit", "-qm", "synthetic fixture")
    return git(root, "rev-parse", "HEAD")


class Stage15LocalPythonRehearsalTests(unittest.TestCase):
    maxDiff = None

    def _assets(self):
        runner = load_runner()
        contract = yaml.safe_load(CONTRACT_PATH.read_text(encoding="utf-8"))
        schema = yaml.safe_load(SCHEMA_PATH.read_text(encoding="utf-8"))
        fixture = yaml.safe_load(FIXTURE_PATH.read_text(encoding="utf-8"))
        return runner, contract, schema, fixture

    def test_public_interfaces_and_assets_exist(self):
        self.assertTrue(RUNNER_PATH.is_file(), RUNNER_PATH)
        runner = load_runner()
        for name in (
            "load_closed_yaml",
            "validate_contract",
            "validate_fixture",
            "validate_receipt",
            "build_sanitized_environment",
            "export_exact_candidate",
            "run_guarded_command",
            "normalize_smoke_output",
            "run_rehearsal",
        ):
            self.assertTrue(callable(getattr(runner, name, None)), name)
        for path in (
            CONTRACT_PATH,
            SCHEMA_PATH,
            FIXTURE_PATH,
            VALIDATOR_PATH,
            GUIDE_PATH,
        ):
            self.assertTrue(path.is_file(), path)

    def test_closed_contract_schema_and_fixture_are_valid(self):
        runner, contract, schema, fixture = self._assets()
        self.assertEqual([], runner.validate_contract(contract))
        self.assertEqual([], runner.validate_fixture(fixture))
        self.assertEqual(list(EXPECTED_RESULTS), contract["allowed_results"])
        self.assertEqual(list(EXPECTED_REASON_CODES), contract["reason_codes"])
        self.assertEqual(False, schema["additional_properties"])
        self.assertEqual("汇沣电商", fixture["scope"]["company"])
        self.assertEqual("BUW", fixture["scope"]["brand"])
        self.assertEqual([], fixture["environment"]["external_endpoints"])
        self.assertEqual([], fixture["environment"]["connectors"])
        self.assertEqual([], fixture["environment"]["credentials"])
        self.assertEqual(
            "Tests/Fixtures/nonproduction-readiness/local-python-store-anomaly-workflow.yaml",
            fixture["workflow"]["workflow_path"],
        )
        self.assertEqual(
            "Tests/Fixtures/nonproduction-readiness/local-python-store-anomaly-input.yaml",
            fixture["workflow"]["input_path"],
        )

    def test_fixture_boundary_attacks_fail_closed(self):
        runner, _, _, fixture = self._assets()
        attacks = []
        for company, brand in (("六合通", "BUW"), ("汇沣电商", "PC"), ("*", "BUW")):
            attack = copy.deepcopy(fixture)
            attack["scope"] = {"company": company, "brand": brand}
            attacks.append(attack)
        for field in ("external_endpoints", "connectors", "credentials"):
            attack = copy.deepcopy(fixture)
            attack["environment"][field] = ["synthetic-but-prohibited"]
            attacks.append(attack)
            misplaced = copy.deepcopy(fixture)
            misplaced[field] = []
            attacks.append(misplaced)
        imported = copy.deepcopy(fixture)
        imported["data_contract"]["provenance"] = "customer_export"
        attacks.append(imported)

        for attack in attacks:
            with self.subTest(scope=attack.get("scope"), keys=tuple(attack)):
                self.assertNotEqual([], runner.validate_fixture(attack))

        cyclic: dict[str, object] = {}
        cyclic["self"] = cyclic
        self.assertNotEqual([], runner.validate_fixture(cyclic))
        self.assertNotEqual([], runner.validate_fixture(None))

    def test_closed_yaml_rejects_alias_merge_and_symlink(self):
        runner = load_runner()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            good = root / "good.yaml"
            good.write_text("scope: {company: 汇沣电商, brand: BUW}\n", encoding="utf-8")
            self.assertEqual("BUW", runner.load_closed_yaml(good)["scope"]["brand"])

            for index, content in enumerate(
                (
                    "base: &base {company: 汇沣电商}\nscope: *base\n",
                    "base: &base {company: 汇沣电商}\nscope: {<<: *base, brand: BUW}\n",
                )
            ):
                unsafe = root / f"unsafe-{index}.yaml"
                unsafe.write_text(content, encoding="utf-8")
                with self.assertRaises(ValueError):
                    runner.load_closed_yaml(unsafe)

            link = root / "link.yaml"
            link.symlink_to(good)
            with self.assertRaises(ValueError):
                runner.load_closed_yaml(link)

    def test_environment_is_minimal_and_secret_names_are_denied(self):
        runner = load_runner()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            guard = root / "guard"
            clean = runner.build_sanitized_environment(
                {"PATH": os.environ.get("PATH", ""), "LANG": "C.UTF-8"},
                temporary_root=root,
                guard_path=guard,
            )
            self.assertEqual(
                {
                    "PATH",
                    "LANG",
                    "LC_ALL",
                    "TMPDIR",
                    "PYTHONNOUSERSITE",
                    "PYTHONDONTWRITEBYTECODE",
                    "PYTHONPATH",
                    "AIOS_NETWORK_GUARD_LOG",
                },
                set(clean),
            )
            self.assertEqual("1", clean["PYTHONNOUSERSITE"])
            self.assertTrue((guard / "sitecustomize.py").is_file())

            for name in ("GITHUB_TOKEN", "shopify_api_key", "DATABASE_URL"):
                with self.subTest(name=name), self.assertRaises(ValueError) as raised:
                    runner.build_sanitized_environment(
                        {"PATH": "/usr/bin", name: "must-not-appear"},
                        temporary_root=root,
                        guard_path=guard,
                    )
                self.assertNotIn("must-not-appear", str(raised.exception))

    def test_network_guard_denies_every_pinned_socket_api(self):
        runner = load_runner()
        snippets = (
            "import socket; socket.socket().connect(('127.0.0.1', 9))",
            "import socket; socket.socket().connect_ex(('127.0.0.1', 9))",
            "import socket; socket.create_connection(('127.0.0.1', 9))",
            "import socket; socket.getaddrinfo('example.invalid', 443)",
            "import socket; socket.gethostbyname('example.invalid')",
            "import socket; socket.gethostbyname_ex('example.invalid')",
            "import socket; socket.gethostbyaddr('127.0.0.1')",
            "import socket; socket.getnameinfo(('127.0.0.1', 9), 0)",
            "import socket; socket.socket(socket.AF_INET, socket.SOCK_DGRAM).sendto(b'x', ('127.0.0.1', 9))",
            "import socket; socket.socketpair()",
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            env = runner.build_sanitized_environment(
                {"PATH": os.environ.get("PATH", ""), "LANG": "C.UTF-8"},
                temporary_root=root,
                guard_path=root / "guard",
            )
            for snippet in snippets:
                with self.subTest(snippet=snippet):
                    completed = subprocess.run(
                        [sys.executable, "-c", snippet],
                        env=env,
                        text=True,
                        capture_output=True,
                        check=False,
                    )
                    self.assertNotEqual(0, completed.returncode)
                    self.assertIn("NetworkOperationDenied", completed.stderr)

    def test_network_guard_records_an_attempt_even_when_child_catches_exception(self):
        runner = load_runner()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            environment = runner.build_sanitized_environment(
                {"PATH": os.environ.get("PATH", ""), "LANG": "C.UTF-8"},
                temporary_root=root,
                guard_path=root / "guard",
            )
            script = (
                "import socket\n"
                "try:\n"
                "    socket.socket(socket.AF_INET, socket.SOCK_DGRAM)\n"
                "except Exception:\n"
                "    pass\n"
                "print('caught')\n"
            )
            with mock.patch.object(runner, "_allowed_command", return_value=True):
                result = runner.run_guarded_command(
                    [sys.executable, "-c", script],
                    cwd=root,
                    environment=environment,
                    timeout_seconds=2,
                )
            self.assertEqual("denied", result["status"])
            self.assertEqual(
                ["NETWORK_OPERATION_ATTEMPTED"], result["reason_codes"]
            )
            self.assertIn("socket.socket", result["network_attempts"])

    def test_command_allowlist_denies_shell_network_and_package_tools(self):
        runner = load_runner()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            env = {
                "PATH": os.environ.get("PATH", ""),
                "LANG": "C.UTF-8",
                "LC_ALL": "C.UTF-8",
                "TMPDIR": str(root),
                "PYTHONNOUSERSITE": "1",
                "PYTHONDONTWRITEBYTECODE": "1",
                "PYTHONPATH": str(root),
            }
            for argv in (
                ["curl", "https://example.invalid"],
                ["sh", "-c", "true"],
                [sys.executable, "-m", "pip", "install", "PyYAML"],
                ["git", "archive", "--remote=https://example.invalid/repo", "HEAD"],
                ["git", "status", "--porcelain", "--untracked-files=all", "--ignored"],
            ):
                with self.subTest(argv=argv):
                    result = runner.run_guarded_command(
                        argv, cwd=root, environment=env, timeout_seconds=2
                    )
                    self.assertEqual("denied", result["status"])
                    self.assertIn("COMMAND_NOT_ALLOWLISTED", result["reason_codes"])

    def test_material_scan_is_computed_from_exact_execution_assets(self):
        runner = load_runner()
        fixture = runner.load_closed_yaml(FIXTURE_PATH)
        clean = runner.scan_rehearsal_material(
            fixture=fixture,
            selected_paths=(
                CONTRACT_PATH,
                FIXTURE_PATH,
                SYNTHETIC_WORKFLOW_PATH,
                SYNTHETIC_INPUT_PATH,
                RUNNER_PATH,
                ROOT / "Runtime/controlled_orchestrator.py",
            ),
            inventory_paths=(path.relative_to(ROOT).as_posix() for path in ROOT.rglob("*")),
        )
        self.assertEqual(
            {
                "credentials_found": False,
                "real_data_found": False,
                "external_endpoints_found": False,
                "nonempty_connectors_found": False,
                "infrastructure_material_found": False,
            },
            clean,
        )
        with tempfile.TemporaryDirectory() as directory:
            unsafe = Path(directory) / "unsafe.yaml"
            unsafe.write_text("endpoint: https://example.invalid\n", encoding="utf-8")
            detected = runner.scan_rehearsal_material(
                fixture=fixture,
                selected_paths=(unsafe,),
                inventory_paths=(),
            )
            self.assertTrue(detected["external_endpoints_found"])
            python_attacks = (
                ("url.py", 'SERVICE_URL = "https://example.invalid"\n', "external_endpoints_found"),
                ("credential.py", 'PASSWORD = "not-a-synthetic-secret"\n', "credentials_found"),
                ("private_key.py", 'KEY = "-----BEGIN PRIVATE KEY-----"\n', "credentials_found"),
            )
            for name, content, finding in python_attacks:
                attack = Path(directory) / name
                attack.write_text(content, encoding="utf-8")
                with self.subTest(path=name, finding=finding):
                    python_detected = runner.scan_rehearsal_material(
                        fixture=fixture,
                        selected_paths=(
                            SYNTHETIC_WORKFLOW_PATH,
                            SYNTHETIC_INPUT_PATH,
                            attack,
                        ),
                        inventory_paths=(),
                    )
                    self.assertTrue(python_detected[finding])

    def test_exact_candidate_export_and_unsafe_archive_denial(self):
        runner = load_runner()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "repo"
            root.mkdir()
            (root / "safe.txt").write_text("synthetic\n", encoding="utf-8")
            commit = init_repository(root)
            execution = Path(directory) / "execution"
            evidence = runner.export_exact_candidate(
                repository_root=root,
                source_commit=commit,
                execution_root=execution,
            )
            self.assertRegex(evidence["source_tree"], r"^[0-9a-f]{40}$")
            self.assertRegex(evidence["file_inventory_sha256"], r"^[0-9a-f]{64}$")
            self.assertEqual("synthetic\n", (execution / "safe.txt").read_text())

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "repo"
            root.mkdir()
            (root / "target.txt").write_text("synthetic\n", encoding="utf-8")
            (root / "unsafe-link").symlink_to("target.txt")
            commit = init_repository(root)
            with self.assertRaises(ValueError) as raised:
                runner.export_exact_candidate(
                    repository_root=root,
                    source_commit=commit,
                    execution_root=Path(directory) / "execution",
                )
            self.assertIn("ARCHIVE_MEMBER_UNSAFE", str(raised.exception))

    def test_normalization_is_deterministic_and_redacts_ephemeral_values(self):
        runner = load_runner()
        left = {
            "run_id": "first",
            "timestamp": "2026-08-07T00:00:00Z",
            "result": {"b": 2, "a": 1},
            "temporary_path": "/private/tmp/first",
        }
        right = {
            "temporary_path": "/private/tmp/second",
            "result": {"a": 1, "b": 2},
            "timestamp": "2027-01-01T00:00:00Z",
            "run_id": "second",
        }
        self.assertEqual(
            runner.normalize_smoke_output(left), runner.normalize_smoke_output(right)
        )
        self.assertEqual(
            {"result": {"a": 1, "b": 2}}, runner.normalize_smoke_output(left)
        )

    def test_receipt_schema_is_closed_and_authority_claims_fail(self):
        runner, _, schema, _ = self._assets()
        receipt = runner.empty_receipt(
            result="local_python_test_deployment_rehearsal_blocked",
            source_commit="0" * 40,
            source_tree="0" * 40,
            reason_codes=["LOCAL_DEPENDENCY_UNAVAILABLE"],
        )
        self.assertEqual([], runner.validate_receipt(receipt))
        self.assertEqual(tuple(schema["required_keys"]), tuple(receipt))

        extra = copy.deepcopy(receipt)
        extra["unexpected"] = True
        self.assertNotEqual([], runner.validate_receipt(extra))
        for field in (
            "cloud_capability_proven",
            "pilot_authorized",
            "production_ready",
            "release_authorized",
            "deployment_authorized",
            "risks_accepted",
        ):
            attack = copy.deepcopy(receipt)
            attack[field] = True
            self.assertNotEqual([], runner.validate_receipt(attack), field)
        cyclic: dict[str, object] = {}
        cyclic["self"] = cyclic
        self.assertNotEqual([], runner.validate_receipt(cyclic))

    def test_cleanup_is_contained_to_task_created_paths(self):
        runner = load_runner()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            marker = root / ".stage15-rehearsal-marker"
            marker.write_text("RUN-001", encoding="utf-8")
            child = root / "execution"
            child.mkdir()
            (child / "synthetic.txt").write_text("synthetic", encoding="utf-8")
            self.assertTrue(runner.cleanup_task_path(child, root, "RUN-001"))
            self.assertFalse(child.exists())
            for unsafe in (root, Path.home(), Path("/")):
                with self.subTest(unsafe=unsafe), self.assertRaises(ValueError):
                    runner.cleanup_task_path(unsafe, root, "RUN-001")

    def test_persisted_rehearsal_receipt_is_closed_and_bounded(self):
        runner = load_runner()
        receipt = runner.load_closed_yaml(RECEIPT_PATH)
        self.assertEqual([], runner.validate_receipt(receipt))
        self.assertEqual("STAGE15-LOCAL-33e2216976b7", receipt["run_id"])
        self.assertEqual(
            "33e2216976b73ebaff4368ca8b8d5dc206ebf894",
            receipt["source_commit"],
        )
        self.assertEqual(
            "eff75180da120fa7deffdd15b1daa2a13bcb8ab5",
            receipt["source_tree"],
        )
        self.assertEqual([], receipt["network_guard"]["attempted_operations"])
        self.assertFalse(any(receipt["material_scan"].values()))
        self.assertEqual([], receipt["external_actions_performed"])
        rendered = json.dumps(receipt, ensure_ascii=False)
        self.assertNotIn("李涛", rendered)
        self.assertNotIn("G0011", rendered)
        self.assertIn("SYNTHETIC-ROLE-RETAIL-APPROVER-001", rendered)
        self.assertIn("SYNTHETIC-STORE-001", rendered)
        for field in (
            "cloud_capability_proven",
            "pilot_authorized",
            "production_ready",
            "release_authorized",
            "deployment_authorized",
            "risks_accepted",
        ):
            self.assertFalse(receipt[field], field)

    def test_mandatory_return_matches_receipt_and_preserves_stop_boundaries(self):
        runner = load_runner()
        receipt = runner.load_closed_yaml(RECEIPT_PATH)
        mandatory_return = runner.load_closed_yaml(MANDATORY_RETURN_PATH)
        self.assertEqual(receipt["source_commit"], mandatory_return["source_candidate"]["commit"])
        self.assertEqual(receipt["source_tree"], mandatory_return["source_candidate"]["tree"])
        self.assertEqual(receipt["run_id"], mandatory_return["rehearsal"]["run_id"])
        self.assertEqual(1, mandatory_return["rehearsal"]["valid_run_count"])
        self.assertEqual("passed", mandatory_return["independent_reviews"]["data_agent"]["result"])
        self.assertEqual("passed", mandatory_return["independent_reviews"]["stone"]["result"])
        self.assertEqual(runner.RISK_STATES, mandatory_return["risk_states"])
        self.assertFalse(any(mandatory_return["authority_claims"].values()))
        self.assertEqual([], mandatory_return["external_actions_performed"])

    def test_rehearsal_returns_closed_receipt_and_cleans_execution(self):
        runner = load_runner()
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory) / "repo"
            repo.mkdir()
            for relative in (
                "Runtime/__init__.py",
                "Runtime/controlled_orchestrator.py",
                "Runtime/stage15_local_python_rehearsal.py",
                "Tests/Fixtures/nonproduction-readiness/local-python-store-anomaly-workflow.yaml",
                "Tests/Fixtures/nonproduction-readiness/local-python-store-anomaly-input.yaml",
                "Tests/Fixtures/nonproduction-readiness/local-python-rehearsal-synthetic.yaml",
                "Governance/AIOS-Stage15-Local-Python-Rehearsal-Contract-v1.yaml",
                "Governance/AIOS-Stage15-Local-Python-Rehearsal-Receipt-Schema-v1.yaml",
                "requirements-dev.txt",
            ):
                source = ROOT / relative
                target = repo / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)
            commit = init_repository(repo)
            with mock.patch.dict(
                os.environ,
                {
                    "PATH": os.defpath,
                    "LANG": "C.UTF-8",
                    "LC_ALL": "C.UTF-8",
                },
                clear=True,
            ):
                receipt = runner.run_rehearsal(
                    repository_root=repo,
                    source_commit=commit,
                    contract_path=repo
                    / "Governance/AIOS-Stage15-Local-Python-Rehearsal-Contract-v1.yaml",
                    fixture_path=repo
                    / "Tests/Fixtures/nonproduction-readiness/local-python-rehearsal-synthetic.yaml",
                )
            self.assertEqual([], runner.validate_receipt(receipt))
            self.assertEqual(
                "local_python_test_deployment_rehearsal_passed_not_cloud_proof",
                receipt["result"],
                receipt,
            )
            self.assertTrue(receipt["cleanup"]["execution_directory_removed"])
            self.assertTrue(receipt["cleanup"]["bytecode_directory_removed"])
            self.assertTrue(receipt["cleanup"]["repository_unchanged"])
            self.assertEqual([], receipt["external_actions_performed"])
            rendered = json.dumps(receipt, ensure_ascii=False)
            self.assertNotIn(str(Path.home()), rendered)
            self.assertNotIn("李涛", rendered)
            self.assertNotIn("G0011", rendered)
            self.assertIn("SYNTHETIC-ROLE-RETAIL-APPROVER-001", rendered)
            self.assertIn("SYNTHETIC-STORE-001", rendered)
            self.assertFalse(receipt["cloud_capability_proven"])


if __name__ == "__main__":
    unittest.main()
