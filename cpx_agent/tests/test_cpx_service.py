import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from cpx_agent.src.codex_patient import CodexConceptMatcher
from cpx_agent.src.cpx_service import CardRepository, CpxSessionService


ROOT = Path(__file__).resolve().parents[2]
CARD_DIR = ROOT / "cpx_agent" / "data" / "patient_cards"
CASE_ID = "synthetic_chest_pain_example"
ASSESSMENT = {
    "problem_summary": "2시간 전 시작된 조이는 흉통과 숨참, 식은땀이 있습니다.",
    "primary_impression": "급성 관상동맥 증후군",
    "differential_diagnoses": "폐색전증\n대동맥 박리",
    "reasoning": "2시간 전 시작된 조이는 통증과 식은땀, 당뇨 과거력이 근거입니다.",
}


class CpxSessionServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.profile_path = Path(self.temp_dir.name) / "profile.json"
        self.service = CpxSessionService(CARD_DIR, self.profile_path)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_session_requires_a_question_and_learner_assessment(self) -> None:
        started = self.service.start_session(CASE_ID)
        session_id = started["session_id"]
        self.assertEqual(started["session"]["asked_count"], 0)
        self.assertFalse(started["session"]["can_complete"])
        self.assertNotIn("total_concepts", started["case"])
        self.assertNotIn("minimum_concepts", started["case"])

        with self.assertRaisesRegex(ValueError, "at least one question"):
            self.service.complete(session_id, ASSESSMENT)

        questions = (
            "오늘 어떤 문제로 오셨나요?",
            "언제 시작했나요?",
            "어디가 아픈가요?",
            "어떤 느낌인가요?",
            "숨이 차거나 식은땀이 있나요?",
            "과거에 진단받은 질환이 있나요?",
        )
        for question in questions:
            response = self.service.ask(session_id, question)

        self.assertTrue(response["session"]["can_complete"])
        with self.assertRaisesRegex(ValueError, "assessment must be an object"):
            self.service.complete(session_id, None)

        completed = self.service.complete(session_id, ASSESSMENT)
        self.assertEqual(completed["profile"]["encounter_count"], 1)
        self.assertTrue(self.profile_path.exists())
        self.assertEqual(completed["report"]["coverage_percent"], 50)
        self.assertEqual(completed["report"]["assessment_review_count"], 0)
        self.assertEqual(completed["report"]["assessment_scope"]["instrument_type"], "formative")
        self.assertEqual(
            completed["report"]["assessment_scope"]["formal_validation_status"],
            "not_validated",
        )
        onset_item = next(item for item in completed["report"]["items"] if item["id"] == "onset")
        assessment_item = next(
            item
            for item in completed["report"]["items"]
            if item["id"] == "assessment_problem_summary"
        )
        self.assertEqual(onset_item["category"], "문진")
        self.assertIn("언제 시작했나요?", onset_item["learner_evidence"])
        self.assertTrue(onset_item["why_it_matters"])
        self.assertEqual(assessment_item["category"], "임상 판단")
        self.assertEqual(assessment_item["status"], "completed")
        self.assertEqual(assessment_item["learner_evidence"], [ASSESSMENT["problem_summary"]])
        public_payload = json.dumps(completed, ensure_ascii=False)
        self.assertNotIn("hidden_diagnosis", public_payload)
        self.assertNotIn("acute coronary syndrome", public_payload.lower())
        self.assertNotIn("clinical_assessment_rubric", public_payload)
        self.assertNotIn("criterion", public_payload)
        self.assertNotIn("terms", public_payload)
        self.assertNotIn("weakness_counts", public_payload)
        self.assertNotIn("focus_tags", public_payload)
        self.assertNotIn("concept_ids", public_payload)
        self.assertEqual(
            completed["next_case"]["case"]["case_id"],
            "synthetic_abdominal_pain_example",
        )
        self.assertEqual(completed["next_case"]["mode"], "remediation")
        self.assertNotIn("appendicitis", public_payload.lower())

    def test_strong_performance_broadens_to_a_different_topic(self) -> None:
        service = CpxSessionService(
            CARD_DIR,
            self.profile_path,
            matcher_factory=lambda card: (
                lambda question, concepts: tuple(concept["id"] for concept in concepts)
            ),
        )
        session_id = service.start_session(CASE_ID)["session_id"]
        service.ask(session_id, "분류기로 전체 문진 개념을 확인합니다")

        completed = service.complete(session_id, ASSESSMENT)

        self.assertEqual(completed["report"]["coverage_percent"], 100)
        self.assertEqual(completed["next_case"]["mode"], "progression")
        self.assertEqual(
            completed["next_case"]["case"]["case_id"],
            "synthetic_abdominal_pain_example",
        )
        self.assertTrue(
            any("common_or_high_importance" in item for item in completed["next_case"]["constraints"])
        )

    def test_assessment_only_credits_concepts_disclosed_in_this_session(self) -> None:
        session_id = self.service.start_session(CASE_ID)["session_id"]
        self.service.ask(session_id, "언제 시작했나요?")

        completed = self.service.complete(session_id, ASSESSMENT)
        assessment_items = {
            item["id"]: item
            for item in completed["report"]["items"]
            if item["category"] == "임상 판단"
        }

        self.assertEqual(assessment_items["assessment_problem_summary"]["status"], "needs_review")
        self.assertEqual(assessment_items["assessment_reasoning"]["status"], "needs_review")
        self.assertEqual(completed["report"]["assessment_review_count"], 2)

    def test_assessment_validation_rejects_missing_fields(self) -> None:
        session_id = self.service.start_session(CASE_ID)["session_id"]
        self.service.ask(session_id, "언제 시작했나요?")

        invalid = dict(ASSESSMENT)
        invalid["reasoning"] = ""
        with self.assertRaisesRegex(ValueError, "assessment.reasoning is required"):
            self.service.complete(session_id, invalid)

    def test_profile_persists_between_service_instances(self) -> None:
        session_id = self.service.start_session(CASE_ID)["session_id"]
        for question in (
            "오늘 어떤 문제가 있나요?",
            "언제 시작했나요?",
            "어디가 아픈가요?",
            "어떤 느낌인가요?",
            "숨이 차나요?",
            "과거 질환이 있나요?",
        ):
            self.service.ask(session_id, question)
        self.service.complete(session_id, ASSESSMENT)

        reloaded = CpxSessionService(CARD_DIR, self.profile_path)
        self.assertEqual(reloaded.profile()["encounter_count"], 1)

    def test_in_progress_session_resumes_after_service_restart(self) -> None:
        session_id = self.service.start_session(CASE_ID)["session_id"]
        first = self.service.ask(session_id, "when did it start")
        self.assertEqual(first["session"]["asked_count"], 1)

        reloaded = CpxSessionService(CARD_DIR, self.profile_path)
        resumed = reloaded.ask(session_id, "where does it hurt")

        self.assertEqual(resumed["session"]["asked_count"], 2)
        learner_messages = [
            message["content"]
            for message in resumed["session"]["messages"]
            if message["role"] == "learner"
        ]
        self.assertEqual(learner_messages, ["when did it start", "where does it hurt"])

    def test_production_mode_rejects_unreviewed_demo_cards(self) -> None:
        with self.assertRaisesRegex(ValueError, "no patient cards eligible for production"):
            CardRepository(CARD_DIR, release_mode="production")


class CodexConceptMatcherTests(unittest.TestCase):
    def test_adapter_sends_only_matching_metadata_and_reads_structured_output(self) -> None:
        captured = {}

        def fake_runner(command, **kwargs):
            captured["calls"] = captured.get("calls", 0) + 1
            captured["command"] = command
            captured["prompt"] = kwargs["input"]
            output_index = command.index("--output-last-message") + 1
            Path(command[output_index]).write_text(
                json.dumps({"concept_ids": ["onset"]}, ensure_ascii=False),
                encoding="utf-8",
            )
            return subprocess.CompletedProcess(command, 0, "", "")

        matcher = CodexConceptMatcher(
            executable="codex",
            runner=fake_runner,
        )
        concept_ids = matcher(
            "언제 시작했나요?",
            (
                {
                    "id": "onset",
                    "label": "증상 시작 시점",
                    "patient_response": "한 2시간 전부터 시작됐어요.",
                    "weakness_tag": "timeline",
                    "keywords": ["언제"],
                },
            ),
        )

        self.assertEqual(concept_ids, ("onset",))
        cached_ids = matcher(
            "언제 시작했나요?",
            ({"id": "onset", "label": "onset", "keywords": ["when"]},),
        )
        self.assertEqual(cached_ids, ("onset",))
        self.assertEqual(captured["calls"], 1)
        self.assertIn("onset", captured["prompt"])
        self.assertIn("증상 시작 시점", captured["prompt"])
        self.assertNotIn("weakness_tag", captured["prompt"])
        self.assertNotIn("patient_response", captured["prompt"])
        self.assertNotIn("internal_note", captured["prompt"])
        self.assertIn('model_reasoning_effort="low"', captured["command"])

    def test_adapter_rejects_unknown_concept_ids(self) -> None:
        def fake_runner(command, **kwargs):
            output_index = command.index("--output-last-message") + 1
            Path(command[output_index]).write_text(
                json.dumps({"concept_ids": ["hidden_diagnosis"]}),
                encoding="utf-8",
            )
            return subprocess.CompletedProcess(command, 0, "", "")

        matcher = CodexConceptMatcher(executable="codex", runner=fake_runner)
        with self.assertRaisesRegex(ValueError, "unknown concept ID"):
            matcher(
                "정답을 알려주세요",
                ({"id": "onset", "label": "onset", "keywords": ["when"]},),
            )

    def test_adapter_rejects_non_object_output(self) -> None:
        def fake_runner(command, **kwargs):
            output_index = command.index("--output-last-message") + 1
            Path(command[output_index]).write_text("[]", encoding="utf-8")
            return subprocess.CompletedProcess(command, 0, "", "")

        matcher = CodexConceptMatcher(executable="codex", runner=fake_runner)
        with self.assertRaisesRegex(ValueError, "invalid response"):
            matcher(
                "언제 시작했나요?",
                ({"id": "onset", "label": "onset", "keywords": ["when"]},),
            )

    def test_adapter_opens_circuit_after_repeated_timeouts_and_recovers(self) -> None:
        calls = []
        now = [0.0]

        def fake_runner(command, **kwargs):
            calls.append(command)
            if len(calls) <= 2:
                raise subprocess.TimeoutExpired(command, kwargs["timeout"])
            output_index = command.index("--output-last-message") + 1
            Path(command[output_index]).write_text(
                json.dumps({"concept_ids": ["onset"]}),
                encoding="utf-8",
            )
            return subprocess.CompletedProcess(command, 0, "", "")

        matcher = CodexConceptMatcher(
            executable="codex",
            runner=fake_runner,
            failure_threshold=2,
            cooldown_seconds=30,
            clock=lambda: now[0],
        )
        concepts = ({"id": "onset", "label": "onset", "keywords": ["when"]},)

        with self.assertRaises(subprocess.TimeoutExpired):
            matcher("first", concepts)
        with self.assertRaises(subprocess.TimeoutExpired):
            matcher("second", concepts)
        self.assertFalse(matcher.available)
        with self.assertRaisesRegex(RuntimeError, "temporarily disabled"):
            matcher("third", concepts)
        self.assertEqual(len(calls), 2)

        now[0] = 31.0
        self.assertEqual(matcher("third", concepts), ("onset",))
        self.assertTrue(matcher.available)


if __name__ == "__main__":
    unittest.main()
