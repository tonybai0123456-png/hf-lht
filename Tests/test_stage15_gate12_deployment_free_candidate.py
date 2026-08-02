from pathlib import Path
import copy
import importlib.util
import subprocess
import sys
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "Governance/AIOS-Deployment-Free-Candidate-Evidence-v1.yaml"
AUDIT = ROOT / "Governance/AIOS-Predeployment-Completion-Audit-v1.yaml"
GATE11_DECISION = (
    ROOT
    / "Governance/AIOS-Stage15-Gate11-Synthetic-Rehearsal-Evidence-Decision-v1.yaml"
)
STAGE_REGISTRY = ROOT / "Governance/AIOS-Stage-Registry.md"
PROJECT_REGISTRY = ROOT / "Governance/AIOS-Project-Registry.md"
PACKET = ROOT / "Governance/AIOS-Stage15-Gate12-Deployment-Free-Decision-Packet-v1.yaml"
PACKET_VALIDATOR = ROOT / "Tests/validate_aios_stage15_gate12_decision_packet.py"


def load_packet_validator():
    spec = importlib.util.spec_from_file_location("gate12_packet_validator", PACKET_VALIDATOR)
    if spec is None or spec.loader is None:
        raise RuntimeError("Gate 12 packet validator cannot be loaded")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Stage15Gate12DeploymentFreeCandidateTests(unittest.TestCase):
    def test_final_packet_is_exact_fail_closed_and_cli_verified(self):
        validator = load_packet_validator()
        packet = yaml.safe_load(PACKET.read_text(encoding="utf-8"))
        self.assertEqual([], validator.validate_repository(ROOT))
        self.assertEqual([], validator.validate_decision_packet(packet))
        self.assertEqual(
            "ready_for_gate12_decision_release_withheld",
            validator.evaluate_decision_packet(packet)["result"],
        )
        attacked = copy.deepcopy(packet)
        attacked["claims"]["release_authorized"] = True
        denied = validator.evaluate_decision_packet(attacked)
        self.assertEqual("denied", denied["result"])
        self.assertEqual([], denied["external_actions_performed"])
        completed = subprocess.run(
            [sys.executable, str(PACKET_VALIDATOR)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertIn("result=ready_for_gate12_decision_release_withheld", completed.stdout)

    def test_current_candidate_records_gate11_and_only_gate12_remains(self):
        candidate = yaml.safe_load(CANDIDATE.read_text(encoding="utf-8"))
        gate11 = yaml.safe_load(GATE11_DECISION.read_text(encoding="utf-8"))

        self.assertTrue(gate11["gate11_decision_boundary"]["gate_accepted"])
        gates = {item["gate_id"]: item for item in candidate["gate_ledger"]}
        self.assertTrue(gates["HG-PILOT-EVIDENCE"]["accepted"])
        self.assertEqual("accepted", gates["HG-PILOT-EVIDENCE"]["state"])
        self.assertFalse(gates["HG-RELEASE"]["accepted"])
        self.assertEqual(
            ["HG-RELEASE"],
            candidate["candidate_decision"]["remaining_human_gates"],
        )
        self.assertEqual(
            "ready_for_gate12_decision_release_withheld",
            candidate["candidate_decision"]["result"],
        )
        self.assertEqual([], candidate["external_actions_performed"])

    def test_predeployment_audit_is_complete_only_for_no_deployment_scope(self):
        audit = yaml.safe_load(AUDIT.read_text(encoding="utf-8"))
        states = {
            item["requirement_id"]: item["state"]
            for item in audit["requirement_ledger"]
        }
        self.assertEqual("proven_complete", states["PREDEP-08"])
        self.assertEqual("proven_complete", states["PREDEP-09"])
        self.assertEqual([], audit["human_decision_queue"])
        self.assertEqual(
            "deployment_free_work_complete_gate12_decision_pending",
            audit["completion_decision"]["result"],
        )
        self.assertFalse(audit["completion_decision"]["release_gate_authorized"])
        self.assertEqual([], audit["external_actions_performed"])

    def test_current_registries_do_not_report_gate11_as_pending(self):
        for path in (STAGE_REGISTRY, PROJECT_REGISTRY):
            text = path.read_text(encoding="utf-8")
            current_overlay = (
                text.split("## Current Stage 15 decision overlay", 1)[1]
                .split("## Pre-freeze exception record", 1)[0]
                .split("## Registry rules", 1)[0]
            )
            self.assertIn("Gate 11 accepted", current_overlay)
            self.assertIn("Gate 12", current_overlay)
            self.assertIn("deployment_free_work_complete_gate12_decision_pending", current_overlay)
            self.assertIn("AIOS-Stage15-Gate12-Deployment-Free-Decision-Packet-v1.yaml", current_overlay)
            self.assertIn("9bc17fa2ef722f29a8fcf302ef275ef6fbdf3a49", current_overlay)
            self.assertNotIn("Gate 11 remains unaccepted", current_overlay)


if __name__ == "__main__":
    unittest.main()
