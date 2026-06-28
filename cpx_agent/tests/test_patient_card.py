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
            "schema_version",
            "publication",
            "evidence",
            "evaluation_metadata",
            "case_id",
            "title",
            "patient_profile",
            "disclosure_policy",
            "conversation_style",
            "cpx_checklist",
            "safety_notes",
            "adaptive_curriculum",
            "clinical_assessment_rubric",
        }
        self.assertLessEqual(required, set(self.card))

    def test_card_is_explicitly_demo_only_and_formative(self) -> None:
        self.assertEqual(self.card["schema_version"], "1.2.0")
        self.assertEqual(self.card["publication"]["status"], "demo_only")
        self.assertEqual(
            self.card["publication"]["content_type"],
            "synthetic_educational_case",
        )
        self.assertEqual(
            self.card["evaluation_metadata"]["formal_validation_status"],
            "not_validated",
        )
        self.assertTrue(self.card["evidence"]["sources"])

    def test_hidden_diagnosis_is_internal_only(self) -> None:
        profile = self.card["patient_profile"]
        self.assertIn("hidden_diagnosis", profile)
        self.assertIn("hidden_diagnosis", self.card["disclosure_policy"]["never_disclose"])
        self.assertTrue(self.card["safety_notes"]["do_not_reveal_hidden_diagnosis"])

    def test_checklist_items_have_runtime_contract(self) -> None:
        checklist = self.card["cpx_checklist"]
        self.assertGreater(len(checklist), 0)
        for item in checklist:
            self.assertIsInstance(item.get("id"), str)
            self.assertIsInstance(item.get("label"), str)
            self.assertIsInstance(item.get("keywords"), list)
            self.assertTrue(item["keywords"])
            self.assertIsInstance(item.get("patient_response"), str)
            self.assertTrue(item["patient_response"])
            self.assertIsInstance(item.get("weakness_tag"), str)
            self.assertIsInstance(item.get("critical"), bool)
            self.assertIsInstance(item.get("why_it_matters"), str)
            self.assertTrue(item["why_it_matters"])

    def test_clinical_assessment_rubric_is_private_and_data_driven(self) -> None:
        rubric = self.card["clinical_assessment_rubric"]
        self.assertGreater(len(rubric), 0)
        for item in rubric:
            self.assertIsInstance(item.get("field"), str)
            self.assertIsInstance(item.get("criterion"), dict)
            self.assertIsInstance(item.get("feedback_pass"), str)
            self.assertIsInstance(item.get("feedback_review"), str)
            self.assertIsInstance(item.get("why_it_matters"), str)


if __name__ == "__main__":
    unittest.main()
