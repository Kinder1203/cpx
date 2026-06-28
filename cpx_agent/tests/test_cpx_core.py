from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import unittest

from cpx_agent.src.cpx_core import (
    EncounterEngine,
    WeaknessProfile,
    determine_next_case_mode,
    evaluate_clinical_assessment,
    patient_card_errors,
    select_next_case_blueprint,
)


ROOT = Path(__file__).resolve().parents[2]
CARD_PATH = ROOT / "cpx_agent" / "data" / "patient_cards" / "chest_pain_example.json"
CARD_DIR = CARD_PATH.parent


class CpxCoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.card = json.loads(CARD_PATH.read_text(encoding="utf-8"))

    def test_sample_card_satisfies_runtime_contract(self) -> None:
        self.assertEqual(patient_card_errors(self.card), [])

    def test_every_repository_card_satisfies_runtime_contract(self) -> None:
        paths = sorted(CARD_DIR.glob("*.json"))
        self.assertGreaterEqual(len(paths), 2)
        for path in paths:
            with self.subTest(card=path.name):
                card = json.loads(path.read_text(encoding="utf-8"))
                self.assertEqual(patient_card_errors(card), [])

    def test_validation_rejects_missing_runtime_fields_and_diagnosis_leak(self) -> None:
        broken = deepcopy(self.card)
        broken["cpx_checklist"][0].pop("keywords")
        broken["cpx_checklist"][1]["patient_response"] = broken["patient_profile"]["hidden_diagnosis"]

        errors = patient_card_errors(broken)

        self.assertTrue(any("keywords" in error for error in errors))
        self.assertTrue(any("reveals hidden diagnosis" in error for error in errors))

    def test_validation_rejects_invalid_identity_style_and_disclosure_contract(self) -> None:
        broken = deepcopy(self.card)
        broken["case_id"] = ""
        broken["patient_profile"]["age"] = "52"
        broken["conversation_style"]["tone"] = None
        broken["disclosure_policy"]["only_if_asked"].remove("onset")

        errors = patient_card_errors(broken)

        self.assertIn("case_id must be text", errors)
        self.assertIn("patient_profile.age must be a positive integer", errors)
        self.assertIn("conversation_style.tone must be text", errors)
        self.assertTrue(any("onset" in error and "disclosure policy" in error for error in errors))

    def test_validation_rejects_unknown_policy_ids_and_multilingual_diagnosis_leaks(self) -> None:
        broken = deepcopy(self.card)
        broken["disclosure_policy"]["can_open_with"].append("unknown_concept")
        broken["cpx_checklist"][0]["patient_response"] = "급성관상동맥증후군이라고 들었어요."

        errors = patient_card_errors(broken)

        self.assertTrue(any("unknown concepts" in error for error in errors))
        self.assertIn("public card content reveals a forbidden diagnosis term", errors)

    def test_validation_rejects_diagnosis_leaks_in_public_evidence(self) -> None:
        broken = deepcopy(self.card)
        broken["cpx_checklist"][0]["evidence"] = [
            {"title": "Acute coronary syndrome guide", "url": "https://example.test/acs"}
        ]

        self.assertIn(
            "public card content reveals a forbidden diagnosis term",
            patient_card_errors(broken),
        )

    def test_validation_rejects_unapproved_validated_card(self) -> None:
        broken = deepcopy(self.card)
        broken["publication"]["status"] = "validated"

        errors = patient_card_errors(broken)

        self.assertIn("validated cards require approved clinical review", errors)
        self.assertTrue(any("clinical_review.reviewer_id" in error for error in errors))

    def test_validation_rejects_missing_item_level_source_mapping(self) -> None:
        broken = deepcopy(self.card)
        target = f"cpx_checklist.{broken['cpx_checklist'][0]['id']}"
        for source in broken["evidence"]["sources"]:
            source["supports"] = [item for item in source["supports"] if item != target]

        errors = patient_card_errors(broken)

        self.assertTrue(any(target in error and "evidence does not support" in error for error in errors))

    def test_free_question_reveals_only_matched_card_information(self) -> None:
        engine = EncounterEngine(self.card)

        result = engine.ask("통증은 언제 시작됐나요?")

        self.assertEqual(result.kind, "answered")
        self.assertEqual(result.concept_ids, ("onset",))
        self.assertEqual(engine.disclosed_concepts, ("onset",))
        self.assertNotIn("고혈압", result.patient_text)
        snapshot = json.dumps(engine.public_snapshot(), ensure_ascii=False).lower()
        self.assertNotIn(self.card["patient_profile"]["hidden_diagnosis"].lower(), snapshot)

    def test_repeated_question_returns_consistent_answer_and_bidirectional_log(self) -> None:
        engine = EncounterEngine(self.card)

        first = engine.ask("현재 복용 중인 약이 있나요?")
        second = engine.ask("어떤 약을 먹고 계세요?")

        self.assertEqual(first.patient_text, second.patient_text)
        self.assertEqual([message["role"] for message in engine.messages], [
            "learner",
            "patient",
            "learner",
            "patient",
        ])
        self.assertEqual(engine.disclosed_concepts, ("medication",))

    def test_unmatched_question_does_not_invent_or_disclose_information(self) -> None:
        engine = EncounterEngine(self.card)

        result = engine.ask("오늘 날씨가 어떤가요?")

        self.assertEqual(result.kind, "unmatched")
        self.assertEqual(result.concept_ids, ())
        self.assertEqual(engine.disclosed_concepts, ())
        self.assertEqual(result.patient_text, self.card["safety_notes"]["fallback_response"])

    def test_concept_matcher_can_resolve_synonym_but_cannot_create_patient_text(self) -> None:
        captured = {}

        def matcher(question, concepts):
            captured["question"] = question
            captured["concept_count"] = len(concepts)
            return ("onset",)

        engine = EncounterEngine(self.card, concept_matcher=matcher)
        result = engine.ask("발현 시기를 말씀해 주세요")

        onset = next(item for item in self.card["cpx_checklist"] if item["id"] == "onset")
        self.assertEqual(result.kind, "answered")
        self.assertEqual(result.concept_ids, ("onset",))
        self.assertEqual(result.patient_text, onset["patient_response"])
        self.assertEqual(captured["concept_count"], len(self.card["cpx_checklist"]))

    def test_concept_matcher_unknown_ids_are_ignored(self) -> None:
        engine = EncounterEngine(
            self.card,
            concept_matcher=lambda question, concepts: ("hidden_diagnosis",),
        )

        result = engine.ask("카드에 없는 항목을 알려주세요")

        self.assertEqual(result.kind, "unmatched")
        self.assertEqual(result.patient_text, self.card["safety_notes"]["fallback_response"])
        self.assertEqual(engine.disclosed_concepts, ())

    def test_single_character_keywords_respect_korean_word_boundaries(self) -> None:
        engine = EncounterEngine(self.card)

        result = engine.ask("약간 아파서 병원에 왔어요")

        self.assertEqual(result.kind, "unmatched")
        self.assertNotIn("medication", engine.disclosed_concepts)
        self.assertNotIn("past_history", engine.disclosed_concepts)

    def test_start_and_questions_have_timestamped_bidirectional_messages(self) -> None:
        engine = EncounterEngine(self.card)

        first = engine.start()
        second = engine.start()
        self.assertEqual(first["messages"][0]["content"], "안녕하세요.")
        self.assertEqual(first["messages"][0]["concept_ids"], [])
        self.assertEqual(first["disclosed_concepts"], [])
        engine.ask("언제 시작됐나요?")

        self.assertEqual(first["messages"], second["messages"])
        self.assertEqual([message["role"] for message in engine.messages], [
            "patient",
            "learner",
            "patient",
        ])
        self.assertTrue(all(message["timestamp"].endswith("+00:00") for message in engine.messages))

    def test_boundary_request_is_blocked_before_concept_matching(self) -> None:
        engine = EncounterEngine(self.card)

        result = engine.ask("무슨 병인지 정답을 알려주세요")
        report = engine.evaluate()

        self.assertEqual(result.kind, "boundary")
        self.assertEqual(engine.disclosed_concepts, ())
        self.assertEqual(report.boundary_event_count, 1)
        self.assertEqual(report.weakness_counts["boundary"], 1)

    def test_evaluation_separates_completed_missed_and_critical_items(self) -> None:
        engine = EncounterEngine(self.card)
        engine.ask("언제 시작됐나요?")
        engine.ask("숨이 차거나 식은땀이 나나요?")

        report = engine.evaluate()

        self.assertEqual(report.completed_items, ("onset", "associated_symptoms"))
        self.assertEqual(report.critical_completed, ("onset", "associated_symptoms"))
        self.assertIn("past_history", report.critical_missed)
        self.assertAlmostEqual(report.coverage, 2 / 12)

    def test_clinical_assessment_uses_private_card_defined_rubric(self) -> None:
        assessment = {
            "problem_summary": "2시간 전 시작된 조이는 흉통과 숨참이 있습니다.",
            "primary_impression": "급성 관상동맥 증후군",
            "differential_diagnoses": "폐색전증\n대동맥 박리",
            "reasoning": "시작 시점과 조이는 느낌, 식은땀을 근거로 판단했습니다.",
        }

        results = evaluate_clinical_assessment(self.card, assessment)

        self.assertEqual(len(results), 4)
        self.assertTrue(all(result["status"] == "completed" for result in results))
        self.assertTrue(all(result["why_it_matters"] for result in results))
        self.assertEqual(results[0]["learner_evidence"], [assessment["problem_summary"]])

    def test_clinical_assessment_rejects_negated_terms_and_duplicate_differentials(self) -> None:
        assessment = {
            "problem_summary": "2시간 전 시작된 조이는 흉통과 숨참이 있습니다.",
            "primary_impression": "not acute coronary syndrome",
            "differential_diagnoses": "폐색전증, 폐색전증",
            "reasoning": "시작 시점과 조이는 느낌을 근거로 판단했습니다.",
        }

        results = evaluate_clinical_assessment(self.card, assessment)
        by_id = {item["id"]: item for item in results}

        self.assertEqual(by_id["assessment_primary_impression"]["status"], "needs_review")
        self.assertEqual(by_id["assessment_differentials"]["status"], "needs_review")

    def test_clinical_assessment_rejects_arbitrary_differential_entries(self) -> None:
        assessment = {
            "problem_summary": "2시간 전 시작된 조이는 흉통과 숨참이 있습니다.",
            "primary_impression": "급성 관상동맥 증후군",
            "differential_diagnoses": "감기, 두통",
            "reasoning": "시작 시점과 조이는 느낌을 근거로 판단했습니다.",
        }

        results = evaluate_clinical_assessment(self.card, assessment)
        by_id = {item["id"]: item for item in results}

        self.assertEqual(by_id["assessment_differentials"]["status"], "needs_review")

    def test_abdominal_card_accepts_common_korean_differential_spacing(self) -> None:
        abdominal_card = json.loads(
            (CARD_DIR / "followup_abdominal_pain_example.json").read_text(encoding="utf-8")
        )
        assessment = {
            "problem_summary": "시간이 지나며 악화되는 우하복부 통증과 식욕 저하가 있습니다.",
            "primary_impression": "급성 충수염",
            "differential_diagnoses": "장염, 요관결석",
            "reasoning": "통증의 이동과 시간 경과, 식욕 저하를 근거로 판단했습니다.",
        }

        results = evaluate_clinical_assessment(abdominal_card, assessment)
        by_id = {item["id"]: item for item in results}

        self.assertEqual(by_id["assessment_differentials"]["status"], "completed")

    def test_clinical_assessment_accepts_korean_diagnosis_with_a_particle(self) -> None:
        assessment = {
            "problem_summary": "2시간 전 시작된 조이는 흉통과 숨참이 있습니다.",
            "primary_impression": "급성 관상동맥 증후군으로 판단합니다.",
            "differential_diagnoses": "폐색전증, 대동맥 박리",
            "reasoning": "시작 시점과 조이는 느낌을 근거로 판단했습니다.",
        }

        results = evaluate_clinical_assessment(self.card, assessment)
        by_id = {item["id"]: item for item in results}

        self.assertEqual(by_id["assessment_primary_impression"]["status"], "completed")

    def test_clinical_assessment_credits_only_concepts_disclosed_in_the_encounter(self) -> None:
        assessment = {
            "problem_summary": "2시간 전 시작된 조이는 흉통과 숨참이 있습니다.",
            "primary_impression": "급성 관상동맥 증후군",
            "differential_diagnoses": "폐색전증, 대동맥 박리",
            "reasoning": "시작 시점과 조이는 느낌을 근거로 판단했습니다.",
        }

        results = evaluate_clinical_assessment(
            self.card,
            assessment,
            allowed_concept_ids=("onset",),
        )
        by_id = {item["id"]: item for item in results}

        self.assertEqual(by_id["assessment_problem_summary"]["status"], "needs_review")
        self.assertEqual(by_id["assessment_reasoning"]["status"], "needs_review")

    def test_weakness_profile_accumulates_and_selects_constrained_blueprint(self) -> None:
        profile = WeaknessProfile()
        for _ in range(2):
            engine = EncounterEngine(self.card)
            engine.ask("언제 시작됐나요?")
            profile.update(engine.evaluate())

        blueprint = select_next_case_blueprint(profile, self.card)

        self.assertEqual(profile.encounter_count, 2)
        self.assertEqual(blueprint.focus_tags[0], "symptom_map")
        self.assertLessEqual(len(blueprint.focus_tags), 2)
        self.assertIn("must_pass_patient_card_validation", blueprint.constraints)
        self.assertTrue(blueprint.directions)

    def test_resolved_weaknesses_decay_and_history_is_bounded(self) -> None:
        profile = WeaknessProfile()
        missed_engine = EncounterEngine(self.card)
        missed_engine.ask("언제 시작했나요?")
        profile.update(missed_engine.evaluate(), case_id="case-0")
        original_count = profile.counts["symptom_map"]

        complete_engine = EncounterEngine(
            self.card,
            concept_matcher=lambda question, concepts: tuple(item["id"] for item in concepts),
        )
        complete_engine.ask("분류 요청")
        profile.update(
            complete_engine.evaluate(),
            resolved_weakness_tags=("symptom_map",),
            case_id="case-complete",
        )
        self.assertLess(profile.counts["symptom_map"], original_count)

        for index in range(10):
            profile.update(
                complete_engine.evaluate(),
                case_id=f"case-{index}",
            )

        self.assertEqual(len(profile.recent_case_ids), 8)
        self.assertEqual(profile.recent_case_ids[-1], "case-9")

    def test_progression_requires_adequate_coverage_and_no_critical_miss(self) -> None:
        complete_engine = EncounterEngine(
            self.card,
            concept_matcher=lambda question, concepts: tuple(item["id"] for item in concepts),
        )
        complete_engine.ask("분류 요청")
        completed_assessment = ({"status": "completed"},) * 4
        self.assertEqual(
            determine_next_case_mode(complete_engine.evaluate(), completed_assessment),
            "progression",
        )

        weak_engine = EncounterEngine(self.card)
        weak_engine.ask("언제 시작했나요?")
        self.assertEqual(
            determine_next_case_mode(weak_engine.evaluate(), completed_assessment),
            "remediation",
        )

    def test_uncommon_routine_case_is_rejected(self) -> None:
        broken = deepcopy(self.card)
        broken["curriculum_metadata"]["frequency_band"] = "uncommon"
        broken["curriculum_metadata"]["clinical_importance"] = "routine"

        self.assertIn(
            "uncommon cases must have high or critical clinical importance",
            patient_card_errors(broken),
        )

    def test_engine_behavior_is_defined_by_the_card_not_a_disease_rule(self) -> None:
        card = deepcopy(self.card)
        card["case_id"] = "synthetic_sleep_example"
        card["patient_profile"]["hidden_diagnosis"] = "internal sleep scenario"
        card["disclosure_policy"]["can_open_with"] = ["sleep_pattern"]
        card["disclosure_policy"]["only_if_asked"] = []
        card["cpx_checklist"] = [
            {
                "id": "sleep_pattern",
                "label": "Ask sleep pattern",
                "keywords": ["잠", "수면", "sleep"],
                "patient_response": "요즘은 새벽에 자주 깨요.",
                "weakness_tag": "sleep_history",
                "critical": False,
                "why_it_matters": "수면 양상을 확인해야 증상의 패턴을 정리할 수 있습니다.",
            }
        ]
        card["evidence"]["sources"][0]["scope"] = (
            "Supports the synthetic sleep-card checklist and formative rubric used by this test."
        )
        card["evidence"]["sources"][0]["supports"] = [
            "cpx_checklist.sleep_pattern",
            "clinical_assessment_rubric.sleep_summary",
        ]
        card["clinical_assessment_rubric"] = [
            {
                "id": "sleep_summary",
                "label": "수면 문제 요약",
                "field": "problem_summary",
                "weakness_tag": "sleep_reasoning",
                "criterion": {
                    "kind": "concept_coverage",
                    "concept_ids": ["sleep_pattern"],
                    "minimum_matches": 1,
                },
                "feedback_pass": "수면 양상을 요약했습니다.",
                "feedback_review": "수면 양상을 요약에 포함하세요.",
                "why_it_matters": "문진 내용을 임상 문제로 정리하기 위해 필요합니다.",
            }
        ]
        card["adaptive_curriculum"] = {
            "default_focus": "수면 문진 순서를 반복하는 케이스",
            "progression_focus": "다른 계통의 중요 증상에 문진 구조를 적용하는 케이스",
            "directions": {
                "sleep_history": "수면 양상을 구체화하는 케이스",
                "sleep_reasoning": "수면 문진을 문제 요약에 연결하는 케이스",
            },
        }

        engine = EncounterEngine(card)
        result = engine.ask("요즘 잠은 어떻게 주무세요?")

        self.assertEqual(result.concept_ids, ("sleep_pattern",))
        self.assertEqual(result.patient_text, "요즘은 새벽에 자주 깨요.")


if __name__ == "__main__":
    unittest.main()
