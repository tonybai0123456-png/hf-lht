import copy
import importlib.util
from pathlib import Path
import subprocess
import sys
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / "Governance/AIOS-Stage15-Human-Gate-Proposals-v1.yaml"
VALIDATOR = ROOT / "Tests/validate_aios_stage15_human_gate_proposals.py"
GUIDE = ROOT / "Tests/AIOS-Stage15-Human-Gate-Proposals-Validation.md"


def load_validator():
    spec = importlib.util.spec_from_file_location("gate_proposal_validator", VALIDATOR)
    if spec is None or spec.loader is None:
        raise RuntimeError("human-gate proposal validator cannot be loaded")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Stage15HumanGateProposalTests(unittest.TestCase):
    def test_controlled_proposal_assets_exist(self):
        for path in (MODEL, VALIDATOR, GUIDE):
            self.assertTrue(path.is_file(), path)

    def test_ordered_proposals_record_gate9_treatment_approval_and_later_gates_pending(self):
        validator = load_validator()
        for name in (
            "load_proposals",
            "validate_proposals",
            "evaluate_proposals",
            "validate_repository",
        ):
            self.assertTrue(callable(getattr(validator, name, None)), name)

        model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
        self.assertEqual([], validator.validate_proposals(model))
        self.assertEqual(
            "gates7_through_9_accepted_gates10_and_11_pending",
            model["status"],
        )
        self.assertEqual(
            {"company": "汇沣电商", "brand": "BUW"},
            model["allowed_scope"],
        )
        self.assertEqual(["PC", "六合通"], model["excluded_entities"])

        proposals = model["proposals"]
        self.assertEqual(
            [
                "HG-PRIVACY-DATA",
                "HG-OPS-RECOVERY-INCIDENT-SUPPORT",
                "HG-RISK-DISPOSITION",
                "HG-PILOT-SCOPE",
                "HG-PILOT-EVIDENCE",
            ],
            [proposal["gate_id"] for proposal in proposals],
        )
        self.assertEqual(
            ["#44", "#45", "#46", "#47", "#48"],
            [proposal["issue"] for proposal in proposals],
        )
        self.assertEqual(
            [True, True, True, False, False],
            [proposal["accepted"] for proposal in proposals],
        )
        self.assertEqual(
            [
                ("Tony", "Data Agent"),
                ("Stone", "Developer Agent"),
                ("Tony", "risk_treatment_evidence_by_mapped_agents"),
                ("Tony", "Developer Agent"),
                ("Stone", "Data Agent"),
            ],
            [
                (
                    proposal["human_approver"],
                    proposal["technical_owner"],
                )
                for proposal in proposals
            ],
        )
        self.assertEqual(
            [
                "synthetic_privacy_data_only",
                "synthetic_operations_recovery_incident_support_only",
                "risk_treatment_direction_without_acceptance",
                "synthetic_rehearsal_only_no_real_pilot",
                "synthetic_rehearsal_evidence_only",
            ],
            [proposal["scope_type"] for proposal in proposals],
        )
        for index, proposal in enumerate(proposals, start=7):
            self.assertEqual(
                model["sequencing"]["gate_order"][: index - 1],
                proposal["prerequisite_gates"],
            )

        gate9 = proposals[2]
        self.assertEqual(10, len(gate9["risk_treatments"]))
        self.assertEqual(
            [f"PR-RISK-{number:03d}" for number in range(1, 11)],
            [risk["risk_id"] for risk in gate9["risk_treatments"]],
        )
        self.assertTrue(
            all(
                risk["disposition"]
                == "mitigate_and_remain_open_blocked_unaccepted"
                and risk["production_action_allowed"] is False
                for risk in gate9["risk_treatments"]
            )
        )
        self.assertEqual(
            {
                "real_customers": 0,
                "employees_or_real_operators": 0,
                "stores": 0,
                "production_or_staging_environments": 0,
                "real_cases_orders_accounts_or_messages": 0,
            },
            proposals[3]["zero_participants"],
        )
        self.assertEqual(
            {
                "evidence_type": "synthetic_rehearsal_only",
                "real_pilot_performed": False,
                "pilot_authorized": False,
                "risk_accepted": False,
                "production_ready": False,
                "release_authorized": False,
            },
            proposals[4]["truth_labels"],
        )
        self.assertEqual(
            "HG-PILOT-SCOPE",
            model["sequencing"]["next_gate"],
        )
        self.assertEqual([], model["external_actions_performed"])

    def test_evaluator_is_pure_and_all_authority_escalation_fails_closed(self):
        validator = load_validator()
        model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
        before = copy.deepcopy(model)

        result = validator.evaluate_proposals(model)

        self.assertEqual(before, model)
        self.assertEqual(
            "not_ready_pending_human_governance",
            result["result"],
        )
        self.assertEqual(
            "HG-PILOT-SCOPE", result["next_gate"]
        )
        self.assertEqual(
            [
                "HG-PRIVACY-DATA",
                "HG-OPS-RECOVERY-INCIDENT-SUPPORT",
                "HG-RISK-DISPOSITION",
            ],
            result["accepted_proposal_gates"],
        )
        self.assertEqual([], result["external_actions_performed"])
        self.assertTrue(all(value is False for value in result["claims"].values()))

        unknown_field = copy.deepcopy(before)
        unknown_field["proposals"][0]["unexpected_authority"] = "approved"
        revoked_gate = copy.deepcopy(before)
        revoked_gate["proposals"][2]["accepted"] = False
        revoked_gate["proposals"][2]["state"] = "proposed_awaiting_explicit_owner_approval"
        changed_owner = copy.deepcopy(before)
        changed_owner["proposals"][2]["risk_treatments"][0][
            "human_treatment_owner"
        ] = "Developer Agent"
        reordered = copy.deepcopy(before)
        reordered["proposals"][3], reordered["proposals"][4] = (
            reordered["proposals"][4],
            reordered["proposals"][3],
        )
        external_action = copy.deepcopy(before)
        external_action["external_actions_performed"] = ["real_ticket_created"]
        cyclic = {}
        cyclic["self"] = cyclic

        for attack in (
            None,
            [],
            {},
            unknown_field,
            revoked_gate,
            changed_owner,
            reordered,
            external_action,
            cyclic,
        ):
            with self.subTest(attack_type=type(attack).__name__):
                denied = validator.evaluate_proposals(attack)
                self.assertEqual("denied", denied["result"])
                self.assertEqual([], denied["accepted_proposal_gates"])
                self.assertEqual([], denied["external_actions_performed"])
                self.assertTrue(
                    all(value is False for value in denied["claims"].values())
                )

    def test_repository_guide_existing_ci_and_cli_are_consistent(self):
        validator = load_validator()
        self.assertEqual([], validator.validate_repository(ROOT))

        guide = GUIDE.read_text(encoding="utf-8")
        for token in (
            "gates7_through_9_accepted_gates10_and_11_pending",
            "not_ready_pending_human_governance",
            "HG-PRIVACY-DATA",
            "HG-OPS-RECOVERY-INCIDENT-SUPPORT",
            "HG-RISK-DISPOSITION",
            "HG-PILOT-SCOPE",
            "HG-PILOT-EVIDENCE",
            "Issue #44",
            "Issue #45",
            "Issue #46",
            "Issue #47",
            "Issue #48",
            "Tony",
            "Stone",
            "Developer Agent",
            "Data Agent",
            "CustomerService Agent",
            "CEO Agent",
            "mitigate_and_remain_open_blocked_unaccepted",
            "synthetic_rehearsal_only_no_real_pilot",
            "synthetic_rehearsal_evidence_only",
            "Gate 12",
            "release expressly withheld",
            "accepted_proposal_gates=['HG-PRIVACY-DATA', 'HG-OPS-RECOVERY-INCIDENT-SUPPORT', 'HG-RISK-DISPOSITION']",
            "external_actions_performed=[]",
        ):
            self.assertIn(token, guide)

        workflow_path = (
            ROOT
            / ".github"
            / "workflows"
            / "validate-aios-support-controlled-pilot.yml"
        )
        workflow = yaml.safe_load(workflow_path.read_text(encoding="utf-8"))
        self.assertEqual({"pull_request": None}, workflow[True])
        self.assertEqual({"contents": "read"}, workflow["permissions"])
        workflow_text = workflow_path.read_text(encoding="utf-8")
        self.assertIn(
            "python3 -m unittest discover -s Tests -p 'test_*.py' -v",
            workflow_text,
        )
        self.assertNotIn("persist-credentials: true", workflow_text)

        completed = subprocess.run(
            [sys.executable, str(VALIDATOR)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertIn(
            "AIOS Stage 15 human-gate proposal validation PASSED",
            completed.stdout,
        )
        self.assertIn(
            "result=not_ready_pending_human_governance",
            completed.stdout,
        )
        self.assertIn(
            "next_gate=HG-PILOT-SCOPE", completed.stdout
        )
        self.assertIn(
            "accepted_proposal_gates=['HG-PRIVACY-DATA', 'HG-OPS-RECOVERY-INCIDENT-SUPPORT', 'HG-RISK-DISPOSITION']",
            completed.stdout,
        )
        self.assertIn("external_actions_performed=[]", completed.stdout)
