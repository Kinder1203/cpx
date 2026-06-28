from __future__ import annotations

import unittest
import struct
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
APP_DIR = ROOT / "app"


class AppVerticalSliceTests(unittest.TestCase):
    def read_app_file(self, relative: str) -> str:
        return (APP_DIR / relative).read_text(encoding="utf-8")

    def png_size(self, relative: str) -> tuple[int, int]:
        data = (APP_DIR / relative).read_bytes()
        self.assertEqual(data[:8], b"\x89PNG\r\n\x1a\n")
        return struct.unpack(">II", data[16:24])

    def test_app_files_and_visual_assets_exist(self) -> None:
        expected = [
            "index.html",
            "styles.css",
            "app.js",
            "README.md",
            "assets/pixel/clinic_room.png",
            "assets/pixel/learner_idle.png",
            "assets/pixel/learner_think.png",
            "assets/pixel/learner_typing.png",
            "assets/pixel/patient_idle.png",
            "assets/pixel/emotion/patient_anger.png",
            "assets/pixel/emotion/patient_bargaining.png",
            "assets/pixel/emotion/patient_denial.png",
            "assets/pixel/emotion/patient_depression.png",
        ]
        for relative in expected:
            with self.subTest(relative=relative):
                self.assertTrue((APP_DIR / relative).exists())

    def test_app_keeps_single_free_question_encounter_surface(self) -> None:
        html = self.read_app_file("index.html")
        for element_id in [
            "patientBubble",
            "patientSprite",
            "learnerBubble",
            "composer",
            "freeQuestion",
            "reportPanel",
            "nextCaseBtn",
            "recordModal",
        ]:
            with self.subTest(element_id=element_id):
                self.assertIn(f'id="{element_id}"', html)
        for removed_id in [
            "infoBtn",
            "caseReadiness",
            "assessmentPanel",
            "assessmentForm",
            "assessmentSummary",
            "assessmentPrimary",
            "assessmentDifferentials",
            "assessmentReasoning",
            "caseSelect",
            "emotionSelect",
            "caseInfo",
        ]:
            with self.subTest(removed_id=removed_id):
                self.assertNotIn(f'id="{removed_id}"', html)
        self.assertIn("CODE MEDI CPX ROOM", html)
        self.assertIn("Patient role only", html)
        self.assertIn("Demo case", html)
        self.assertIn("대화 시작", html)
        self.assertIn("대화 종료", html)
        self.assertNotIn("Validated case", html)
        self.assertIn("진단 스프레드시트", html)
        self.assertNotIn("문진 시작", html)
        self.assertNotIn('id="choicePanel"', html)
        self.assertNotIn('id="decisionBoard"', html)
        self.assertNotIn('class="status-row"', html)
        self.assertNotIn('class="cadence-rail"', html)
        self.assertNotIn("역할 경계 유지", html)
        self.assertNotIn("문진 진행 중", html)
        self.assertNotIn("확인 0/9", html)
        self.assertNotIn("턴", html)

    def test_browser_bundle_contains_no_patient_answers_or_private_keys(self) -> None:
        bundle = "\n".join(
            self.read_app_file(relative).lower()
            for relative in ("index.html", "styles.css", "app.js", "README.md")
        )
        forbidden = [
            "hidden_diagnosis",
            "acute coronary syndrome",
            "evaluator_notes",
            "checklist_answers",
            "patient_response",
        ]
        for needle in forbidden:
            with self.subTest(needle=needle):
                self.assertNotIn(needle, bundle)
        self.assertEqual(list((APP_DIR / "fixtures").rglob("*.json")), [])

    def test_app_uses_server_session_contract_instead_of_local_matching(self) -> None:
        script = self.read_app_file("app.js")
        for route in ["/api/cases", "/api/sessions"]:
            self.assertIn(route, script)
        self.assertIn("payload.result.kind", script)
        self.assertIn("payload.next_case", script)
        self.assertIn('const EMOTION_OPTIONS = ["부정", "분노", "협상", "우울"]', script)
        self.assertIn("const EMOTION_SPRITE_CLASS", script)
        self.assertIn('"부정": "emotion-denial"', script)
        self.assertIn('"분노": "emotion-anger"', script)
        self.assertIn('"협상": "emotion-bargaining"', script)
        self.assertIn('"우울": "emotion-depression"', script)
        self.assertIn("function randomItem(items)", script)
        self.assertIn("function setPatientEmotionSprite(emotion)", script)
        self.assertIn("case_id: caseItem.case_id", script)
        self.assertIn("initial_emotion: initialEmotion", script)
        self.assertIn("setPatientEmotionSprite(state.initialEmotion)", script)
        self.assertIn("setPatientEmotionSprite(null)", script)
        self.assertIn("function visibleMessages()", script)
        self.assertIn("const transcript = visibleMessages();", script)
        self.assertIn('latestPatient?.content || "대화 시작을 누른 뒤 질문을 입력하면 환자가 답변합니다."', script)
        self.assertIn('elements.finishBtn.addEventListener("click", finishEncounter)', script)
        self.assertNotIn('elements.caseSelect.addEventListener("change"', script)
        self.assertNotIn('elements.emotionSelect.addEventListener("change"', script)
        self.assertNotIn("renderCaseControls", script)
        self.assertNotIn("selectCase", script)
        self.assertNotIn("matchQuestionConcepts", script)
        self.assertNotIn("fetchPatientResponse", script)
        self.assertNotIn("FIXTURE_URL", script)
        self.assertNotIn("innerHTML", script)

    def test_adaptive_report_uses_server_feedback_without_forced_links(self) -> None:
        html = self.read_app_file("index.html")
        script = self.read_app_file("app.js")
        self.assertIn('id="weaknessTags"', html)
        self.assertIn('id="nextCaseList"', html)
        self.assertIn("다음 연습 목표", html)
        self.assertIn("state.nextCase?.directions", script)
        self.assertIn("state.nextCase?.case", script)
        self.assertIn("startRandomFollowupCase", script)
        self.assertIn('setText(elements.nextCaseBtn, "랜덤 케이스 시작")', script)
        self.assertNotIn("startRecommendedCase", script)
        self.assertIn("item.why_it_matters", script)
        self.assertIn("item.learner_evidence", script)
        self.assertIn("item.evidence", script)
        self.assertNotIn("evidence_library", script)
        self.assertNotIn("adaptive_next_case", script)
        self.assertNotIn("obsidian", script.lower())
        self.assertNotIn("graphify", script.lower())

    def test_report_overlay_has_focus_and_escape_handling(self) -> None:
        html = self.read_app_file("index.html")
        script = self.read_app_file("app.js")
        self.assertIn('id="reportPanel" aria-label="CPX educational report" tabindex="-1"', html)
        self.assertIn("elements.reportPanel.focus({ preventScroll: true })", script)
        self.assertIn("else if (!elements.reportPanel.hidden) closeReport()", script)

    def test_console_owns_scroll_without_desktop_gutter_offset(self) -> None:
        css = self.read_app_file("styles.css")
        self.assertIn(".cpx-device", css)
        self.assertIn("overflow-y: auto", css)
        self.assertIn("scrollbar-width: none", css)
        self.assertIn(".cpx-device::-webkit-scrollbar", css)
        self.assertNotIn("scrollbar-gutter: stable", css)
        self.assertIn("100dvh", css)
        self.assertIn("@media (max-width: 620px)", css)
        self.assertIn("env(safe-area-inset-top)", css)
        self.assertIn("image-rendering: pixelated", css)
        self.assertIn("transform: scale(1.45)", css)
        self.assertIn(".patient-zone::before", css)
        self.assertIn(".learner-zone::before", css)
        self.assertIn('background-image: var(--patient-sprite-sheet, url("./assets/pixel/patient_idle.png"))', css)
        self.assertIn("animation: sprite-patient 2400ms step-end infinite", css)
        self.assertIn('url("./assets/pixel/emotion/patient_denial.png")', css)
        self.assertIn('url("./assets/pixel/emotion/patient_anger.png")', css)
        self.assertIn('url("./assets/pixel/emotion/patient_bargaining.png")', css)
        self.assertIn('url("./assets/pixel/emotion/patient_depression.png")', css)
        self.assertIn('background-image: url("./assets/pixel/learner_think.png")', css)
        self.assertIn("step-end", css)
        for animation_name in (
            "sprite-patient",
            "sprite-learner-idle",
            "sprite-learner-think",
            "sprite-learner-typing",
            "sprite-coach-idle",
            "sprite-coach-write",
        ):
            self.assertIn(f"@keyframes {animation_name}", css)
        self.assertNotIn("vw", css)

    def test_emotion_spritesheets_match_patient_idle_canvas(self) -> None:
        baseline = self.png_size("assets/pixel/patient_idle.png")
        self.assertEqual(baseline, (2508, 627))
        for relative in [
            "assets/pixel/emotion/patient_anger.png",
            "assets/pixel/emotion/patient_bargaining.png",
            "assets/pixel/emotion/patient_denial.png",
            "assets/pixel/emotion/patient_depression.png",
        ]:
            with self.subTest(relative=relative):
                self.assertEqual(self.png_size(relative), baseline)

    def test_overlays_are_positioned_inside_the_device(self) -> None:
        css = self.read_app_file("styles.css")
        record_rule = css.split(".record-modal {", 1)[1].split("}", 1)[0]
        overlay_rule = css.split(".report-sheet {", 1)[1].split("}", 1)[0]
        self.assertIn("position: absolute", record_rule)
        self.assertIn("position: absolute", overlay_rule)
        self.assertIn("overflow: hidden", overlay_rule)
        self.assertNotIn("position: fixed", record_rule)

    def test_overlays_reset_device_scroll_before_opening(self) -> None:
        script = self.read_app_file("app.js")
        self.assertIn(
            'elements.recordModal.parentElement.scrollTo({ top: 0, behavior: "auto" })',
            script,
        )
        self.assertIn(
            'elements.reportPanel.parentElement.scrollTo({ top: 0, behavior: "auto" })',
            script,
        )

    def test_report_uses_internal_scrolling(self) -> None:
        css = self.read_app_file("styles.css")
        self.assertIn(".report-list-panel", css)
        self.assertIn(".report-detail", css)
        self.assertIn("overflow-y: auto", css)
        device_rule = css.split(".cpx-device {", 1)[1].split("}", 1)[0]
        list_panel_rule = css.split(".report-list-panel {", 1)[1].split("}", 1)[0]
        missed_list_rule = css.split(".missed-list {", 1)[1].split("}", 1)[0]
        self.assertIn("display: grid", device_rule)
        self.assertIn("minmax(390px, 1fr)", device_rule)
        self.assertIn("overflow: hidden", list_panel_rule)
        self.assertIn("overflow-y: auto", missed_list_rule)

    def test_fixture_information_control_is_removed(self) -> None:
        html = self.read_app_file("index.html")
        script = self.read_app_file("app.js")
        self.assertNotIn('id="infoBtn"', html)
        self.assertNotIn('id="caseReadiness"', html)
        self.assertNotIn("showFixtureInformation", script)
        self.assertNotIn('elements.infoBtn.setAttribute("aria-expanded"', script)
        self.assertNotIn('elements.infoBtn.addEventListener("click"', script)
        self.assertNotIn("턴", script)


if __name__ == "__main__":
    unittest.main()
