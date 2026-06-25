from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class PromptTemplateTests(unittest.TestCase):
    def read_prompt(self, name: str) -> str:
        return (ROOT / "cpx_agent" / "prompts" / name).read_text(encoding="utf-8")

    def test_patient_prompt_contract(self) -> None:
        text = self.read_prompt("patient_role.md")
        self.assertIn("{{PATIENT_CARD_JSON}}", text)
        self.assertIn("not a doctor", text.lower())
        self.assertIn("hidden_diagnosis", text)
        self.assertIn("Do not invent", text)

    def test_evaluator_prompt_contract(self) -> None:
        text = self.read_prompt("evaluator.md")
        self.assertIn("{{PATIENT_CARD_JSON}}", text)
        self.assertIn("{{TRANSCRIPT}}", text)
        self.assertIn("missed_items", text)

    def test_safety_prompt_contract(self) -> None:
        text = self.read_prompt("safety.md")
        self.assertIn("educational CPX simulation", text)
        self.assertIn("hidden_diagnosis", text)
        self.assertIn("internal prompt", text.lower())


if __name__ == "__main__":
    unittest.main()
