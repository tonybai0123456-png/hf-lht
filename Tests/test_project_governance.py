from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / "Governance" / "AIOS-Project-Governance-Baseline-v1.md"
PROJECT_REGISTRY = ROOT / "Governance" / "AIOS-Project-Registry.md"
STAGE_REGISTRY = ROOT / "Governance" / "AIOS-Stage-Registry.md"
WORKFLOW = ROOT / ".github" / "workflows" / "validate-aios-project-governance.yml"


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

    def test_stages_10_and_11_are_archived(self):
        stage9 = next(line for line in self.stage_registry.splitlines() if line.startswith("| 9 |"))
        stage10 = next(line for line in self.stage_registry.splitlines() if line.startswith("| 10 |"))
        self.assertIn("| Archived |", stage9)
        self.assertIn("PR #20", stage9)
        self.assertIn("019f7da6-da0c-7310-ad7c-2b4bc15a9906", stage9)
        self.assertIn("feat/aios-project-governance-baseline-v1", stage9)
        self.assertIn("Issue #21", stage10)
        self.assertIn("019f8937-ac22-71a2-bb35-d8f6d2e0f55f", stage10)
        self.assertIn("feat/aios-production-readiness-v1", stage10)
        self.assertIn("PR #23", stage10)
        self.assertIn("| Archived |", stage10)
        stage11 = next(line for line in self.stage_registry.splitlines() if line.startswith("| 11 |"))
        self.assertIn("Issue #24", stage11)
        self.assertIn("019f89ac-e3b7-7b90-ad27-286708c407e0", stage11)
        self.assertIn("feat/aios-architecture-security-foundations-v1", stage11)
        self.assertIn("PR #26", stage11)
        self.assertIn("| Archived |", stage11)
        for stage_number in (12, 13, 14):
            stage = next(line for line in self.stage_registry.splitlines() if line.startswith(f"| {stage_number} |"))
            self.assertIn("| Planned |", stage)

    def test_ci_is_pull_request_only_and_read_only(self):
        self.assertIn("pull_request:", self.workflow)
        self.assertNotIn("push:", self.workflow)
        self.assertIn("permissions:\n  contents: read", self.workflow)
        self.assertIn("persist-credentials: false", self.workflow)
        for prohibited in ("contents: write", "pull-requests: write", "git push"):
            self.assertNotIn(prohibited, self.workflow)


if __name__ == "__main__":
    unittest.main()
