from __future__ import annotations

import ast
import copy
import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "Tests/validate_aios_nonproduction_readiness.py"
MODEL = ROOT / "Governance/AIOS-Nonproduction-Readiness-Integration-Model-v1.yaml"
FIXTURE = (
    ROOT
    / "Tests/Fixtures/nonproduction-readiness/synthetic-local-integration.yaml"
)
MAPPING = (
    ROOT
    / "Governance/AIOS-Nonproduction-Readiness-Stage10-14-Mapping-v1.yaml"
)
MATRIX = (
    ROOT
    / "Governance/AIOS-Nonproduction-Readiness-Acceptance-Matrix-v1.yaml"
)
POLICY = ROOT / "Governance/AIOS-Nonproduction-Readiness-Integration-v1.md"
GUIDE = ROOT / "Tests/AIOS-Nonproduction-Readiness-Validation.md"
WORKFLOW = ROOT / ".github/workflows/validate-aios-nonproduction-readiness.yml"


def load_validator():
    spec = importlib.util.spec_from_file_location("nr_validator", VALIDATOR)
    if spec is None or spec.loader is None:
        raise RuntimeError("Stage 15 validator cannot be loaded")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class NonproductionReadinessTests(unittest.TestCase):
    def _assets(self):
        validator = load_validator()
        model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
        fixture = yaml.safe_load(FIXTURE.read_text(encoding="utf-8"))
        return validator, model, fixture

    def test_public_interfaces_and_controlled_assets_exist(self):
        validator = load_validator()
        for name in (
            "load_repository_yaml",
            "validate_model",
            "validate_fixture",
            "evaluate_nonproduction_readiness",
            "validate_repository",
        ):
            self.assertTrue(callable(getattr(validator, name)))
        for path in (MODEL, FIXTURE, MAPPING, MATRIX, POLICY, GUIDE, WORKFLOW):
            self.assertTrue(path.is_file(), path)

    def test_model_and_fixture_are_closed_and_valid(self):
        validator, model, fixture = self._assets()
        self.assertEqual([], validator.validate_model(model))
        self.assertEqual([], validator.validate_fixture(fixture))
        self.assertEqual("nonproduction_readiness_integration/v1", model["model_version"])
        self.assertEqual({"company": "汇沣电商", "brand": "BUW"}, model["allowed_scope"])
        self.assertEqual(["PC", "六合通"], model["excluded_entities"])
        self.assertEqual(["denied", "needs_human_governance"], model["allowed_results"])
        self.assertEqual("BLOCKED / NO-GO", model["stage10_posture"])
        self.assertEqual(
            [f"PR-RISK-{number:03d}" for number in range(1, 11)],
            [row["risk_id"] for row in model["risks"]],
        )
        self.assertEqual(
            [
                "HG-SPEC-APPROVAL",
                "HG-PLAN-APPROVAL",
                "HG-EXECUTION-ASSIGNMENT",
                "HG-IMPLEMENTATION-EVIDENCE",
                "HG-NAMED-OWNER",
                "HG-ARCH-SECURITY",
                "HG-PRIVACY-DATA",
                "HG-OPS-RECOVERY-INCIDENT-SUPPORT",
                "HG-RISK-DISPOSITION",
                "HG-PILOT-SCOPE",
                "HG-PILOT-EVIDENCE",
                "HG-RELEASE",
            ],
            [row["gate_id"] for row in model["human_gates"]],
        )
        self.assertEqual(
            [True, True, True] + [False] * 9,
            [row["authorized"] for row in model["human_gates"]],
        )

    def test_valid_package_stops_at_human_governance_without_side_effects(self):
        validator, model, fixture = self._assets()
        before = copy.deepcopy((model, fixture))
        first = validator.evaluate_nonproduction_readiness(model, fixture)
        second = validator.evaluate_nonproduction_readiness(model, fixture)
        self.assertEqual(first, second)
        self.assertEqual(before, (model, fixture))
        self.assertEqual("needs_human_governance", first["result"])
        self.assertEqual([], first["reason_codes"])
        self.assertEqual(list(validator.EVIDENCE_IDS), first["evidence_refs"])
        self.assertEqual(
            list(validator.PENDING_GATE_IDS),
            first["required_human_gates"],
        )
        self.assertEqual(
            {risk_id: "open_blocked_unaccepted" for risk_id in validator.RISK_IDS},
            first["risk_states"],
        )
        self.assertEqual([], first["external_actions_performed"])
        self.assertEqual(
            {
                "risk_accepted": False,
                "pilot_authorized": False,
                "production_ready": False,
                "release_authorized": False,
            },
            first["claims"],
        )

    def test_empty_capability_fields_are_allowed_only_at_canonical_paths(self):
        validator, model, fixture = self._assets()
        self.assertEqual([], fixture["environment"]["external_endpoints"])
        self.assertEqual([], fixture["environment"]["connectors"])
        self.assertEqual([], fixture["environment"]["credentials"])
        self.assertEqual(
            "needs_human_governance",
            validator.evaluate_nonproduction_readiness(model, fixture)["result"],
        )
        cases = {
            "nonempty endpoint": lambda value: value["environment"].__setitem__(
                "external_endpoints", ["https://example.invalid"]
            ),
            "nonempty connector": lambda value: value["environment"].__setitem__(
                "connectors", ["crm"]
            ),
            "nonempty credential": lambda value: value["environment"].__setitem__(
                "credentials", ["secret"]
            ),
            "misplaced connector": lambda value: value.__setitem__("connectors", []),
            "nested credential": lambda value: value["identity"].__setitem__(
                "credentials", []
            ),
            "secret alias": lambda value: value["identity"].__setitem__(
                "api_key", "synthetic"
            ),
        }
        for label, mutate in cases.items():
            with self.subTest(label=label):
                changed = copy.deepcopy(fixture)
                mutate(changed)
                self.assertEqual(
                    "denied",
                    validator.evaluate_nonproduction_readiness(model, changed)["result"],
                )

    def test_malformed_input_types_and_cycles_are_denied_without_exceptions(self):
        validator, model, fixture = self._assets()
        cases = (
            None,
            [],
            "invalid",
            1,
            {"scope": []},
            {"environment": "invalid"},
            {"risk_states": []},
        )
        for value in cases:
            with self.subTest(value=repr(value)):
                decision = validator.evaluate_nonproduction_readiness(model, value)
                self.assertEqual("denied", decision["result"])
                self.assertTrue(decision["reason_codes"])
        cyclic: dict[str, object] = {}
        cyclic["self"] = cyclic
        decision = validator.evaluate_nonproduction_readiness(model, cyclic)
        self.assertEqual("denied", decision["result"])
        self.assertTrue(decision["reason_codes"])

    def test_loader_rejects_unallowlisted_alias_merge_and_cyclic_yaml(self):
        validator = load_validator()
        self.assertEqual(
            "nonproduction_readiness_integration/v1",
            validator.load_repository_yaml(ROOT, validator.MODEL_PATH)["model_version"],
        )
        for path in (
            Path("../outside.yaml"),
            Path("/tmp/outside.yaml"),
            Path("Governance/AIOS-Stage-Registry.md"),
        ):
            with self.subTest(path=path), self.assertRaises(ValueError):
                validator.load_repository_yaml(ROOT, path)
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            cases = {
                "anchor.yaml": "root: &base {value: 1}\ncopy: *base\n",
                "merge.yaml": "base: &base {value: 1}\nroot:\n  <<: *base\n",
                "cycle.yaml": "root: &root\n  child: *root\n",
            }
            for name, content in cases.items():
                path = root / name
                path.write_text(content, encoding="utf-8")
                with self.subTest(name=name), self.assertRaises(ValueError):
                    validator.load_controlled_yaml_text(path, content)

    def test_business_data_evidence_and_authority_attacks_are_denied(self):
        validator, model, baseline = self._assets()
        mutations = {
            "pc": lambda value: value["scope"].__setitem__("brand", "PC"),
            "lht": lambda value: value["scope"].__setitem__("company", "六合通"),
            "wildcard": lambda value: value["scope"].__setitem__("brand", "*"),
            "real principal": lambda value: value["identity"].__setitem__(
                "simulated", False
            ),
            "real data": lambda value: value["data_contract"].__setitem__(
                "provenance", "production"
            ),
            "external action": lambda value: value[
                "requested_external_actions"
            ].append("send"),
            "accepted risk": lambda value: value["risk_states"].__setitem__(
                "PR-RISK-001", "accepted"
            ),
            "authorized gate": lambda value: value[
                "required_human_gates"
            ].remove("HG-RELEASE"),
            "ready claim": lambda value: value["claims"].__setitem__(
                "production_ready", True
            ),
            "component missing": lambda value: value["component_results"].pop(),
            "evidence unknown": lambda value: value["component_results"][0].__setitem__(
                "evidence_id", "EV-UNKNOWN"
            ),
            "checksum forged": lambda value: value["evidence_store"]["records"][
                0
            ].__setitem__("checksum", "0" * 64),
            "paging": lambda value: value["observation"].__setitem__("paging", True),
            "restore failed": lambda value: value["recovery"].__setitem__(
                "restore_verified", False
            ),
            "real incident": lambda value: value["incident_tabletop"].__setitem__(
                "real_incident_declared", True
            ),
            "real owner": lambda value: value["support_handoff"].__setitem__(
                "owner", "Tony"
            ),
            "ticket": lambda value: value["support_handoff"].__setitem__(
                "ticket_created", True
            ),
        }
        for label, mutate in mutations.items():
            with self.subTest(label=label):
                fixture = copy.deepcopy(baseline)
                mutate(fixture)
                decision = validator.evaluate_nonproduction_readiness(model, fixture)
                self.assertEqual("denied", decision["result"])
                self.assertEqual([], decision["external_actions_performed"])

    def test_repository_mapping_matrix_policy_and_guide_are_complete(self):
        validator = load_validator()
        self.assertEqual([], validator.validate_repository(ROOT))
        mapping = yaml.safe_load(MAPPING.read_text(encoding="utf-8"))
        matrix = yaml.safe_load(MATRIX.read_text(encoding="utf-8"))
        self.assertEqual(
            [f"PR-RISK-{number:03d}" for number in range(1, 11)],
            [row["risk_id"] for row in mapping["risk_mappings"]],
        )
        self.assertTrue(
            all(
                row["state"] == "open_blocked_unaccepted"
                for row in mapping["risk_mappings"]
            )
        )
        self.assertEqual(
            ["AC-ENVIRONMENT", "AC-IDENTITY", "AC-DATA", "AC-EVIDENCE",
             "AC-OBSERVATION", "AC-RECOVERY", "AC-INCIDENT", "AC-SUPPORT",
             "AC-RISK-MAPPING", "AC-AUTHORITY"],
            [row["requirement_id"] for row in matrix["requirements"]],
        )
        test_tree = ast.parse(Path(__file__).read_text(encoding="utf-8"))
        implemented_tests = {
            node.name
            for node in ast.walk(test_tree)
            if isinstance(node, ast.FunctionDef)
            and node.name.startswith("test_")
        }
        linked_tests = {
            test_id
            for requirement in matrix["requirements"]
            for test_id in requirement["test_ids"]
        }
        self.assertEqual(set(), linked_tests - implemented_tests)

        broken_test_link = copy.deepcopy(matrix)
        broken_test_link["requirements"][0]["test_ids"] = [
            "test_does_not_exist"
        ]
        self.assertTrue(validator._validate_matrix(broken_test_link))

        broken_evidence_link = copy.deepcopy(matrix)
        broken_evidence_link["requirements"][0]["evidence_ids"] = [
            "EV-DATA"
        ]
        self.assertTrue(validator._validate_matrix(broken_evidence_link))
        policy = POLICY.read_text(encoding="utf-8")
        for token in (
            "Business loop",
            "Core objects",
            "Data flow",
            "Operators",
            "AI and human judgment boundary",
            "Proof of operation",
            "Authority ceiling",
            "Component contracts",
            "Risk mapping",
            "Stop and withdrawal",
            "Lifecycle",
            "BLOCKED / NO-GO",
            "needs_human_governance",
            "汇沣电商",
            "BUW",
            "PC",
            "六合通",
        ):
            self.assertIn(token, policy)
        guide = GUIDE.read_text(encoding="utf-8")
        self.assertIn("AIOS non-production readiness validation PASSED", guide)
        self.assertIn("does not authorize deployment", guide)

    def test_evaluator_is_pure_and_does_not_use_io_network_process_or_environment(self):
        source = VALIDATOR.read_text(encoding="utf-8")
        tree = ast.parse(source)
        evaluator = next(
            node
            for node in tree.body
            if isinstance(node, ast.FunctionDef)
            and node.name == "evaluate_nonproduction_readiness"
        )
        prohibited_names = {
            "open",
            "print",
            "input",
            "exec",
            "eval",
            "system",
            "popen",
            "run",
            "urlopen",
            "request",
            "getenv",
            "environ",
        }
        used = {
            node.func.id
            for node in ast.walk(evaluator)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
        }
        used.update(
            node.func.attr
            for node in ast.walk(evaluator)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
        )
        self.assertEqual(set(), used & prohibited_names)

    def test_cli_is_cwd_independent_and_exact(self):
        for cwd in (ROOT, ROOT / "Tests"):
            result = subprocess.run(
                [sys.executable, str(VALIDATOR)],
                cwd=cwd,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertEqual(
                "AIOS non-production readiness validation PASSED\n"
                "result=needs_human_governance\n"
                "external_actions_performed=[]\n",
                result.stdout,
            )

    def test_ci_is_pull_request_only_read_only_and_constrained(self):
        workflow = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("pull_request:", workflow)
        self.assertNotIn("push:", workflow)
        self.assertNotIn("workflow_dispatch:", workflow)
        self.assertIn("permissions:\n  contents: read", workflow)
        self.assertIn("persist-credentials: false", workflow)
        for command in (
            "python -m pip install --requirement requirements-dev.txt",
            "python3 Tests/validate_aios_nonproduction_readiness.py",
            "python3 -m unittest Tests.test_nonproduction_readiness -v",
            "python3 -m unittest Tests.test_project_governance -v",
            "python3 -m unittest discover -s Tests -p 'test_*.py' -v",
            "python3 Tests/validate_aios_workflow_schema.py",
            "python3 -m compileall -q Runtime Tests",
        ):
            self.assertIn(command, workflow)
        for denied in (
            "contents: write",
            "pull-requests: write",
            "issues: write",
            "git push",
            "curl ",
            "wget ",
            "secrets.",
            "environment:",
            "deployment",
        ):
            self.assertNotIn(denied, workflow)


if __name__ == "__main__":
    unittest.main()
