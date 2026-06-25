from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CARD_PATH = ROOT / "cpx_agent" / "data" / "patient_cards" / "chest_pain_example.json"


class PatientCardTests(unittest.TestCase):
    def setUp(self) -> None:
        self.card = json.loads(CARD_PATH.read_text(encoding="utf-8"))

    def test_required_sections_exist(self) -> None:
        required = {
            "case_id",
            "title",
            "patient_profile",
            "disclosure_policy",
            "conversation_style",
            "cpx_checklist",
            "safety_notes",
        }
        self.assertLessEqual(required, set(self.card))

    def test_hidden_diagnosis_is_internal_only(self) -> None:
        profile = self.card["patient_profile"]
        self.assertIn("hidden_diagnosis", profile)
        self.assertIn("hidden_diagnosis", self.card["disclosure_policy"]["never_disclose"])
        self.assertTrue(self.card["safety_notes"]["do_not_reveal_hidden_diagnosis"])

    def test_checklist_items_have_ids_and_labels(self) -> None:
        checklist = self.card["cpx_checklist"]
        self.assertGreater(len(checklist), 0)
        for item in checklist:
            self.assertIsInstance(item.get("id"), str)
            self.assertIsInstance(item.get("label"), str)


if __name__ == "__main__":
    unittest.main()
