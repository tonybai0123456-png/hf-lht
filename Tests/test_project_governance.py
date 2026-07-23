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

    def test_stage15_governance_design_is_planned_and_unassigned(self):
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
            "| Planned |",
            "implementation unassigned",
            "方案 B",
            "written specification approved",
            "implementation plan reviewed at `8984a1720cf716ab832590b2dd6748d628677edc`",
            "correction required",
            "corrected implementation plan awaits independent human review",
            "no real pilot",
        ):
            self.assertIn(token, stage15)

        for token in (
            "Stage 14 Archived / Stage 15 Planned",
            "no active execution Stage",
            "Issue #40",
            "PR #41",
            "implementation unassigned",
            "written specification approved",
            "implementation plan reviewed at `8984a1720cf716ab832590b2dd6748d628677edc`",
            "correction required",
            "corrected implementation plan awaits independent human review",
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

    def test_stage15_implementation_plan_is_present_but_requires_correction(self):
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
        expected_result = re.compile(r"\b(?:Expected|expect|expects|confirm|verify|proves?|pass(?:es|ed)?)\b", re.IGNORECASE)
        commit_command = re.compile(r"git commit -m \"[^\"]+\"")
        code_change_language = re.compile(r"```(?:python|yaml|markdown|diff)\n", re.MULTILINE)

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
                self.assertRegex(section, expected_result)
                self.assertRegex(section, commit_command)
                if re.search(r"(?i)\b(create|modify|implement|add|write|update|replace)\b", section):
                    self.assertRegex(section, code_change_language)

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

    def test_ci_is_pull_request_only_and_read_only(self):
        self.assertIn("pull_request:", self.workflow)
        self.assertNotIn("push:", self.workflow)
        self.assertIn("permissions:\n  contents: read", self.workflow)
        self.assertIn("persist-credentials: false", self.workflow)
        for prohibited in ("contents: write", "pull-requests: write", "git push"):
            self.assertNotIn(prohibited, self.workflow)


if __name__ == "__main__":
    unittest.main()
