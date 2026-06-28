from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path

from cpx_agent.src.bad_news_backend import BadNewsSessionService, load_project_env


ROOT = Path(__file__).resolve().parents[2]
BAD_NEWS_DIR = ROOT / "cpx_agent" / "data" / "bad_news"


class FakeBadNewsLlm:
    def complete(self, system_prompt: str, conversation_text: str, *, model: str) -> str:
        if "PPI" in system_prompt:
            return json.dumps(
                {
                    "ppi_results": {
                        "1": {"rating": "우수함", "reason": "질문을 차분히 이어갔습니다."},
                        "2": {"rating": "부족함", "reason": "환자의 걱정 탐색이 짧았습니다."},
                        "3": {"rating": "우수함", "reason": "쉬운 표현으로 설명했습니다."},
                        "4": {"rating": "우수함", "reason": "공감 표현이 있었습니다."},
                        "5": {"rating": "부족함", "reason": "마무리 구조가 약했습니다."},
                        "6": {
                            "rating": "평가 제외",
                            "reason": "이번 케이스는 신체진찰을 시행하지 않음",
                        },
                    },
                    "narrative_feedback": {
                        "strengths": ["결과를 단계적으로 설명했습니다."],
                        "areas_to_improve": ["환자의 감정을 더 확인해야 합니다."],
                        "must_fix": [],
                    },
                },
                ensure_ascii=False,
            )
        if "채점관" in system_prompt:
            return json.dumps(
                {
                    "core_results": {
                        "E1-1": {"result": "O", "evidence": "안녕하세요, 담당 의사입니다."},
                        "E1-2": {"result": "X", "evidence": ""},
                        "E2-3": {"result": "O", "evidence": "많이 놀라셨겠습니다."},
                    },
                    "critical_fails_triggered": [],
                    "critical_fail_evidence": {},
                    "emotion_response": {
                        "detected_emotions": ["분노"],
                        "reached_acceptance": False,
                        "results": {
                            "A1": {"result": "O", "evidence": "화가 나실 수 있습니다."},
                            "A2": {"result": "X", "evidence": ""},
                        },
                    },
                },
                ensure_ascii=False,
            )
        return "왜 이제야 이런 결과를 말씀하시는 거예요? 너무 당황스럽고 화가 납니다."


class BadNewsBackendTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.service = BadNewsSessionService(
            BAD_NEWS_DIR,
            Path(self.temp_dir.name) / "reports",
            llm_client=FakeBadNewsLlm(),
            chat_model="fake-chat",
            eval_model="fake-eval",
        )

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_case_db_loads_ready_bad_news_cases(self) -> None:
        cases = self.service.cases.public_backend_cases()

        self.assertEqual(len(cases), 10)
        self.assertTrue(all(case["ready_for_play"] for case in cases))
        self.assertIn("B05-breast-cancer", {case["case_id"] for case in cases})
        self.assertIn("E2-4", self.service.cases.checklist["core_checklist"])
        self.assertIn("분노", self.service.cases.checklist["emotion_checklists"])

    def test_existing_app_contract_uses_llm_patient_and_checkpoint_report(self) -> None:
        started = self.service.start_session(
            "B05-breast-cancer",
            difficulty="중",
            initial_emotion="분노",
        )
        session_id = str(started["session_id"])

        answered = self.service.ask(session_id, "안녕하세요. 저는 담당 의사입니다.")
        self.assertEqual(answered["result"]["kind"], "answered")
        self.assertTrue(answered["session"]["can_complete"])
        self.assertEqual(answered["session"]["messages"][-1]["role"], "patient")
        self.assertIn("화가", answered["session"]["messages"][-1]["content"])

        completed = self.service.complete(session_id, {})

        self.assertEqual(completed["profile"]["encounter_count"], 1)
        self.assertEqual(completed["next_case"]["mode"], "remediation")
        self.assertIn("checklist_axis", completed["report"])
        self.assertIn("ppi_axis", completed["report"])
        self.assertGreater(completed["report"]["coverage_percent"], 0)
        self.assertTrue(
            any(item["id"] == "E1-2" and item["status"] == "missed" for item in completed["report"]["items"])
        )
        report_id = completed["report"]["report_id"]
        saved_report = self.service.get_report(str(report_id))
        self.assertEqual(saved_report["case_id"], "B05-breast-cancer")
        public_payload = json.dumps(completed, ensure_ascii=False)
        self.assertNotIn("hidden_diagnosis", public_payload)
        self.assertNotIn("internal prompt", public_payload.lower())

    def test_imported_backend_contract_is_available_without_fastapi_dependency(self) -> None:
        started = self.service.start_backend_session(
            case_id="B05-breast-cancer",
            difficulty="하",
            initial_emotion="분노",
        )
        session_id = str(started["session_id"])

        self.assertEqual(started["case_id"], "B05-breast-cancer")
        self.assertEqual(started["initial_emotion"], "분노")
        self.assertIn("chart", started)
        self.assertIn("core_labels", started)

        turn = self.service.take_turn(session_id, "검사 결과를 설명드리겠습니다.")
        self.assertIn("patient_reply", turn)
        self.assertEqual(turn["turn_count"], 1)

        evaluated = self.service.evaluate_backend_session(session_id)
        self.assertIn("checklist_axis", evaluated)
        self.assertIn("ppi_axis", evaluated)
        self.assertIn("recommendation", evaluated)


class ProjectEnvTests(unittest.TestCase):
    def test_load_project_env_reads_key_values_without_overwriting_process_env(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            env_path = Path(temp_dir) / ".env"
            env_path.write_text(
                "\n".join(
                    [
                        "OPENAI_API_KEY=from-file",
                        "OPENAI_MODEL_CHAT=gpt-4o-mini",
                        "COMMENT_WITHOUT_EQUALS",
                        "# ignored",
                    ]
                ),
                encoding="utf-8",
            )
            original_key = os.environ.get("OPENAI_API_KEY")
            original_model = os.environ.get("OPENAI_MODEL_CHAT")
            try:
                os.environ["OPENAI_API_KEY"] = "from-process"
                os.environ.pop("OPENAI_MODEL_CHAT", None)

                load_project_env(env_path)

                self.assertEqual(os.environ["OPENAI_API_KEY"], "from-process")
                self.assertEqual(os.environ["OPENAI_MODEL_CHAT"], "gpt-4o-mini")
            finally:
                if original_key is None:
                    os.environ.pop("OPENAI_API_KEY", None)
                else:
                    os.environ["OPENAI_API_KEY"] = original_key
                if original_model is None:
                    os.environ.pop("OPENAI_MODEL_CHAT", None)
                else:
                    os.environ["OPENAI_MODEL_CHAT"] = original_model


if __name__ == "__main__":
    unittest.main()
