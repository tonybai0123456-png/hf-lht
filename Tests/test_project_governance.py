import ast
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / "Governance" / "AIOS-Project-Governance-Baseline-v1.md"
PROJECT_REGISTRY = ROOT / "Governance" / "AIOS-Project-Registry.md"
STAGE_REGISTRY = ROOT / "Governance" / "AIOS-Stage-Registry.md"
WORKFLOW = ROOT / ".github" / "workflows" / "validate-aios-project-governance.yml"
STAGE15_SPEC = (
    ROOT
    / "docs"
    / "superpowers"
    / "specs"
    / "2026-07-23-nonproduction-readiness-remediation-integration-design.md"
)
STAGE15_PLAN = (
    ROOT
    / "docs"
    / "superpowers"
    / "plans"
    / "2026-07-23-nonproduction-readiness-remediation-integration.md"
)
STAGE15_VALIDATOR = ROOT / "Tests" / "validate_aios_nonproduction_readiness.py"
STAGE15_TEST = ROOT / "Tests" / "test_nonproduction_readiness.py"
STAGE15_POLICY = (
    ROOT / "Governance" / "AIOS-Nonproduction-Readiness-Integration-v1.md"
)
STAGE15_MODEL = (
    ROOT
    / "Governance"
    / "AIOS-Nonproduction-Readiness-Integration-Model-v1.yaml"
)
STAGE15_FIXTURE = (
    ROOT
    / "Tests"
    / "Fixtures"
    / "nonproduction-readiness"
    / "synthetic-local-integration.yaml"
)
STAGE15_MAPPING = (
    ROOT
    / "Governance"
    / "AIOS-Nonproduction-Readiness-Stage10-14-Mapping-v1.yaml"
)
STAGE15_MATRIX = (
    ROOT
    / "Governance"
    / "AIOS-Nonproduction-Readiness-Acceptance-Matrix-v1.yaml"
)
STAGE15_GUIDE = ROOT / "Tests" / "AIOS-Nonproduction-Readiness-Validation.md"
STAGE15_WORKFLOW = (
    ROOT / ".github" / "workflows" / "validate-aios-nonproduction-readiness.yml"
)


class ProjectGovernanceValidation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.baseline = BASELINE.read_text(encoding="utf-8")
        cls.project_registry = PROJECT_REGISTRY.read_text(encoding="utf-8")
        cls.stage_registry = STAGE_REGISTRY.read_text(encoding="utf-8")
        cls.workflow = WORKFLOW.read_text(encoding="utf-8")

    def test_effective_authority_and_stage_are_explicit(self):
        for required in (
            "Governance/AIOS-Thread-Governance-v2.1.md",
            "BUW AIOS Official Governance Thread",
            "Stage 9",
            "PG-01",
            "Issue #13",
        ):
            self.assertIn(required, self.baseline)

    def test_exactly_one_initial_project_is_registered(self):
        project_ids = re.findall(
            r"^\|\s*([A-Z][A-Z0-9-]+)\s*\|",
            self.project_registry,
            re.MULTILINE,
        )
        self.assertEqual(["BUW-AIOS"], project_ids)

    def test_company_and_brand_boundaries_are_not_collapsed(self):
        for entity in ("BUW", "PC", "汇沣电商", "六合通"):
            self.assertIn(entity, self.baseline)
            self.assertIn(entity, self.project_registry)
        self.assertIn("independent brand", self.baseline)
        self.assertIn("separate company", self.baseline)

    def test_registries_have_distinct_control_roles(self):
        self.assertIn("project identity", self.baseline)
        self.assertIn("Stage assignment", self.baseline)
        self.assertIn("does not replace", self.project_registry)

    def test_fail_closed_and_human_gates_are_mandatory(self):
        for required in (
            "fail closed",
            "Mandatory Return",
            "human approval",
            "Reported does not mean Reviewed",
            "Reviewed does not mean Archived",
        ):
            self.assertIn(required, self.baseline)

    def test_tools_and_chatgpt_project_are_non_authoritative(self):
        self.assertIn("ChatGPT Project is not", self.baseline)
        self.assertIn("Tools execute", self.baseline)
        self.assertIn("working context only", self.project_registry)

    def test_prohibited_interpretations_are_denied(self):
        for denied in (
            "multiple active Execution Threads",
            "self-approve",
            "production",
            "real business data",
            "external writes",
        ):
            self.assertIn(denied, self.baseline)

    def test_stages_10_through_14_are_archived(self):
        stage10 = next(line for line in self.stage_registry.splitlines() if line.startswith("| 10 |"))
        stage11 = next(line for line in self.stage_registry.splitlines() if line.startswith("| 11 |"))
        stage12 = next(line for line in self.stage_registry.splitlines() if line.startswith("| 12 |"))
        stage13 = next(line for line in self.stage_registry.splitlines() if line.startswith("| 13 |"))
        stage14 = next(line for line in self.stage_registry.splitlines() if line.startswith("| 14 |"))
        self.assertIn("BLOCKED / NO-GO", stage10)
        self.assertIn("| Archived |", stage10)
        self.assertIn("PR #26", stage11)
        self.assertIn("| Archived |", stage11)
        self.assertIn("PR #29", stage12)
        self.assertIn("454a719", stage12)
        self.assertIn("| Archived |", stage12)
        for token in ("Issue #32", "Issue #34", "327d9e9", "7b16a5c", "19/19", "80/80", "| Archived |"):
            self.assertIn(token, stage13)
        for token in (
            "Issue #36", "019f8c92-e709-7a83-b06c-fa014cf0b216",
            "feat/aios-support-controlled-pilot-design-v1", "PR #37",
            "| Archived |", "7184d917", "Mandatory Return", "needs_human_governance",
            "Human Governance Thread review passed",
            "142804f", "Published through PR #37", "post-merge",
            "8d6e2af", "Archived by the Governance Thread",
            "no pilot authority",
        ):
            self.assertIn(token, stage14)
        self.assertIn("Stage 13 Archived / Stage 14 Archived", self.project_registry)
        self.assertIn("no active execution Stage", self.project_registry)
        self.assertIn("142804f", self.project_registry)
        self.assertIn("published through PR #37", self.project_registry)

    def test_stage15_is_reported_with_exact_predeployment_evidence(self):
        stage15_rows = [
            line for line in self.stage_registry.splitlines()
            if line.startswith("| 15 |")
        ]
        self.assertEqual(1, len(stage15_rows))
        stage15 = stage15_rows[0]
        for token in (
            "NR-01",
            "Non-production Readiness Remediation and Integration Validation",
            "Issue #40",
            "gov/aios-stage15-nonproduction-readiness-design",
            "PR #41",
            "019fb137-f0bc-7e60-b8ad-efe1a8e250b1",
            "| Reported |",
            "written specification approved",
            "implementation head `698a4557b9ed8627e150341b9eb5dd57ca409928`",
            "tree `0fb49bbb4794949a57b5d661a952948d7931885c`",
            "11/11 focused",
            "14/14 Project Governance",
            "108/108 repository",
            "9/9 exact-head CI",
            "Mandatory Return",
            "needs_human_governance",
            "awaits independent human review",
            "no real pilot",
        ):
            self.assertIn(token, stage15)

        for token in (
            "Stage 14 Archived / Stage 15 Reported",
            "Issue #40",
            "PR #41",
            "019fb137-f0bc-7e60-b8ad-efe1a8e250b1",
            "written specification approved",
            "implementation head `698a4557b9ed8627e150341b9eb5dd57ca409928`",
            "tree `0fb49bbb4794949a57b5d661a952948d7931885c`",
            "11/11 focused",
            "14/14 Project Governance",
            "108/108 repository",
            "9/9 exact-head CI",
            "Mandatory Return submitted",
            "awaits independent human review",
            "needs_human_governance",
        ):
            self.assertIn(token, self.project_registry)

        spec = STAGE15_SPEC.read_text(encoding="utf-8")
        for token in (
            "Business loop",
            "Core objects",
            "Data flow",
            "Operators",
            "AI and human judgment boundary",
            "Proof of operation",
            "PR-RISK-001",
            "PR-RISK-010",
            "needs_human_governance",
            "汇沣电商",
            "BUW",
            "PC",
            "六合通",
            "synthetic",
            "local",
            "fail closed",
            "Stage 10",
            "BLOCKED / NO-GO",
            "dedicated Execution Task",
            "PR #41",
        ):
            self.assertIn(token, spec)
        for unresolved in ("TBD", "TODO", "PLACEHOLDER"):
            self.assertNotIn(unresolved, spec)

    def test_stage15_implementation_plan_is_complete_and_executable(self):
        if not STAGE15_PLAN.is_file():
            self.fail(f"missing Stage 15 implementation plan: {STAGE15_PLAN}")
        plan = STAGE15_PLAN.read_text(encoding="utf-8")
        for token in (
            "# Non-production Readiness Remediation and Integration Implementation Plan",
            "**Goal:**",
            "**Architecture:**",
            "**Tech Stack:**",
            "## Global Constraints",
            "Governance/AIOS-Nonproduction-Readiness-Integration-v1.md",
            "Governance/AIOS-Nonproduction-Readiness-Integration-Model-v1.yaml",
            "Governance/AIOS-Nonproduction-Readiness-Stage10-14-Mapping-v1.yaml",
            "Governance/AIOS-Nonproduction-Readiness-Acceptance-Matrix-v1.yaml",
            "Tests/Fixtures/nonproduction-readiness/synthetic-local-integration.yaml",
            "Tests/validate_aios_nonproduction_readiness.py",
            "Tests/test_nonproduction_readiness.py",
            "Tests/AIOS-Nonproduction-Readiness-Validation.md",
            ".github/workflows/validate-aios-nonproduction-readiness.yml",
            "load_repository_yaml(root: Path, relative_path: Path) -> dict[str, Any]",
            "validate_model(model: dict[str, Any]) -> list[str]",
            "validate_fixture(fixture: dict[str, Any]) -> list[str]",
            "evaluate_nonproduction_readiness(",
            "validate_repository(root: Path) -> list[str]",
            "needs_human_governance",
            "dedicated Execution Task",
            "implementation branch",
            "Stage 15 `Reported`",
        ):
            self.assertIn(token, plan)
        for task_number in range(1, 13):
            self.assertIn(f"## Task {task_number}:", plan)
        for unresolved in ("TBD", "TODO", "PLACEHOLDER"):
            self.assertNotIn(unresolved, plan)

    def test_stage15_plan_tasks_are_machine_checkable(self):
        """Reject task-level plans that are prose-only or lack runnable evidence."""
        plan = STAGE15_PLAN.read_text(encoding="utf-8")
        task_matches = list(
            re.finditer(
                r"(?ms)^## Task (\d+):.*?(?=^## Task \d+:|^## Plan self-review checklist|\Z)",
                plan,
            )
        )
        self.assertEqual([str(number) for number in range(1, 13)], [match.group(1) for match in task_matches])

        code_fence = re.compile(r"```(?:bash|python|yaml|markdown|diff)\n.+?\n```", re.DOTALL)
        run_command = re.compile(r"(?m)^\s*(?:python3|git|test|gh|python -m pip)\b")
        evidence_language = re.compile(
            r"\b(?:Expected|expect|expects|confirm|verify|proves?|pass(?:es|ed)?|validat(?:e|es|ed|ion)|run)\b",
            re.IGNORECASE,
        )
        commit_command = re.compile(r"git commit -m \"[^\"]+\"")

        for match in task_matches:
            task_number = match.group(1)
            section = match.group(0)
            with self.subTest(task=task_number):
                self.assertIn("**Files**", section)
                self.assertIn("**Interfaces**", section)
                self.assertRegex(section, r"(?m)^- \[ \] ")
                fences = code_fence.findall(section)
                self.assertGreaterEqual(len(fences), 2, "task must contain runnable/code evidence fences")
                self.assertTrue(any(run_command.search(fence) for fence in fences), "task must contain an exact runnable command")
                self.assertRegex(section, evidence_language)
                self.assertRegex(section, commit_command)

        for requirement_id in (
            "AC-ENVIRONMENT",
            "AC-IDENTITY",
            "AC-DATA",
            "AC-EVIDENCE",
            "AC-OBSERVATION",
            "AC-RECOVERY",
            "AC-INCIDENT",
            "AC-SUPPORT",
            "AC-RISK-MAPPING",
            "AC-AUTHORITY",
        ):
            self.assertIn(requirement_id, plan)
        for policy_section in (
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
        ):
            self.assertIn(policy_section, plan)
        for return_field in (
            "exact remote head and tree",
            "changed-file allowlist",
            "final-head CI links",
            "maximum result `needs_human_governance`",
        ):
            self.assertIn(return_field, plan)

    def test_stage15_plan_pins_capability_and_malformed_input_regressions(self):
        """Keep the exact fail-closed correction contract machine-checkable."""
        plan = STAGE15_PLAN.read_text(encoding="utf-8")
        for token in (
            "ALLOWED_EMPTY_CAPABILITY_PATHS",
            "$.environment.external_endpoints",
            "$.environment.connectors",
            "$.environment.credentials",
            "allowed_empty_capability",
            "forbidden_capability_value",
            "test_empty_capability_fields_are_allowed",
            "test_nonempty_or_misplaced_capability_fields_are_denied",
            "test_malformed_input_types_are_denied_without_exceptions",
            "except (AttributeError, KeyError, TypeError, ValueError)",
            "self.assertEqual(\"needs_human_governance\", result[\"result\"])",
            "self.assertEqual(\"denied\", result[\"result\"])",
        ):
            self.assertIn(token, plan)

        self.assertNotIn(
            'if normalized in FORBIDDEN_KEYS:\n                errors.append(_error(f"{path}.{key}", "forbidden_key"))',
            plan,
        )

    def test_stage15_as_built_closure_is_executable_not_token_only(self):
        plan = STAGE15_PLAN.read_text(encoding="utf-8")
        self.assertIn("## As-built executable closure", plan)
        for token in (
            "load_controlled_yaml_text",
            "_scan_capabilities",
            "ALLOWED_EMPTY_CAPABILITY_PATHS",
            "_fail_closed",
            "yaml.scan",
            "AnchorToken",
            "AliasToken",
            "ScalarToken",
            "validation_exception",
            "python3 Tests/validate_aios_nonproduction_readiness.py",
            "python3 -m unittest Tests.test_nonproduction_readiness -v",
            "python3 -m unittest discover -s Tests -p 'test_*.py' -v",
        ):
            self.assertIn(token, plan)

        assets = (
            STAGE15_VALIDATOR,
            STAGE15_TEST,
            STAGE15_POLICY,
            STAGE15_MODEL,
            STAGE15_FIXTURE,
            STAGE15_MAPPING,
            STAGE15_MATRIX,
            STAGE15_GUIDE,
            STAGE15_WORKFLOW,
        )
        for asset in assets:
            self.assertTrue(asset.is_file(), asset)
            self.assertGreater(asset.stat().st_size, 100, asset)

        validator_source = STAGE15_VALIDATOR.read_text(encoding="utf-8")
        validator_tree = ast.parse(validator_source)
        defined = {
            node.name
            for node in validator_tree.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        }
        self.assertTrue(
            {
                "load_repository_yaml",
                "load_controlled_yaml_text",
                "validate_model",
                "validate_fixture",
                "evaluate_nonproduction_readiness",
                "validate_repository",
            }.issubset(defined)
        )

        policy = STAGE15_POLICY.read_text(encoding="utf-8")
        sections = re.split(r"(?m)^## ", policy)[1:]
        section_bodies = {
            section.splitlines()[0]: "\n".join(section.splitlines()[1:]).strip()
            for section in sections
        }
        for heading in (
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
        ):
            self.assertIn(heading, section_bodies)
            self.assertGreater(len(section_bodies[heading]), 80, heading)

    def test_ci_is_pull_request_only_and_read_only(self):
        self.assertIn("pull_request:", self.workflow)
        self.assertNotIn("push:", self.workflow)
        self.assertIn("permissions:\n  contents: read", self.workflow)
        self.assertIn("persist-credentials: false", self.workflow)
        for prohibited in ("contents: write", "pull-requests: write", "git push"):
            self.assertNotIn(prohibited, self.workflow)


if __name__ == "__main__":
    unittest.main()
