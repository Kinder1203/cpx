"""Application service for CPX encounters, reports, and adaptive profiles."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from threading import RLock
from typing import Any, Callable
from uuid import uuid4

from .codex_patient import CodexConceptMatcher
from .cpx_core import (
    LEARNER_ASSESSMENT_FIELDS,
    EncounterEngine,
    WeaknessProfile,
    determine_next_case_mode,
    evaluate_clinical_assessment,
    select_next_case_blueprint,
    validate_patient_card,
)
from .session_store import SessionStore


MatcherFactory = Callable[[dict[str, Any]], Callable[..., tuple[str, ...]] | None]


@dataclass
class SessionState:
    card: dict[str, Any]
    engine: EncounterEngine
    completed: bool = False
    learner_assessment: dict[str, str] | None = None


class CardRepository:
    def __init__(self, card_dir: Path, *, release_mode: str = "demo") -> None:
        if release_mode not in {"demo", "production"}:
            raise ValueError("release_mode must be demo or production")
        allowed_statuses = {"demo_only", "validated"} if release_mode == "demo" else {"validated"}
        self._cards: dict[str, dict[str, Any]] = {}
        for path in sorted(card_dir.glob("*.json")):
            card = json.loads(path.read_text(encoding="utf-8"))
            validate_patient_card(card)
            if card["publication"]["status"] not in allowed_statuses:
                continue
            case_id = card["case_id"]
            if case_id in self._cards:
                raise ValueError(f"duplicate case_id: {case_id}")
            self._cards[case_id] = card
        if not self._cards:
            raise ValueError(
                f"no patient cards eligible for {release_mode} mode in {card_dir}"
            )

    def get(self, case_id: str) -> dict[str, Any]:
        try:
            return self._cards[case_id]
        except KeyError as exc:
            raise KeyError(f"unknown case_id: {case_id}") from exc

    def public_cases(self) -> list[dict[str, Any]]:
        return [self._public_case(card) for card in self._cards.values()]

    def recommend_next(
        self,
        current_case_id: str,
        focus_tags: tuple[str, ...],
        *,
        mode: str = "remediation",
        recent_case_ids: tuple[str, ...] = (),
    ) -> dict[str, Any] | None:
        candidates = []
        requested = set(focus_tags)
        current_topics = set(
            self.get(current_case_id)["curriculum_metadata"]["topic_tags"]
        )
        importance_weight = {"routine": 1, "high": 2, "critical": 3}
        frequency_weight = {"uncommon": 1, "occasional": 2, "common": 3}
        for case_id, card in self._cards.items():
            if case_id == current_case_id:
                continue
            card_tags = {
                item["weakness_tag"]
                for section in (card["cpx_checklist"], card["clinical_assessment_rubric"])
                for item in section
            }
            curriculum = card["curriculum_metadata"]
            utility = (
                importance_weight[curriculum["clinical_importance"]] * 3
                + frequency_weight[curriculum["frequency_band"]]
            )
            topic_overlap = len(current_topics & set(curriculum["topic_tags"]))
            recent_penalty = int(case_id in recent_case_ids)
            weakness_overlap = len(requested & card_tags)
            if mode == "progression":
                rank = (recent_penalty, topic_overlap, -utility, case_id)
            else:
                rank = (-weakness_overlap, recent_penalty, -utility, topic_overlap, case_id)
            candidates.append((rank, card))
        if not candidates:
            return None
        _, selected = min(candidates, key=lambda item: item[0])
        return self._public_case(selected)

    @staticmethod
    def _public_case(card: dict[str, Any]) -> dict[str, Any]:
        profile = card["patient_profile"]
        sex_label = {"male": "남성", "female": "여성"}.get(
            str(profile["sex"]).casefold(),
            "성별 비공개",
        )
        return {
            "case_id": card["case_id"],
            "title": card["title"],
            "safe_metadata": f"{profile['age']}세 {sex_label} · 합성 표준화 환자",
        }


class CpxSessionService:
    def __init__(
        self,
        card_dir: Path,
        profile_path: Path,
        *,
        matcher_factory: MatcherFactory | None = None,
        session_db_path: Path | None = None,
        release_mode: str = "demo",
    ) -> None:
        self.cards = CardRepository(card_dir, release_mode=release_mode)
        self._profile_path = profile_path
        self._profile = self._load_profile()
        self._sessions: dict[str, SessionState] = {}
        self._matcher_factory = matcher_factory
        self._session_store = SessionStore(
            session_db_path or profile_path.with_name("sessions.sqlite3")
        )
        self._lock = RLock()
        self._restore_sessions()

    def list_cases(self) -> dict[str, object]:
        return {"cases": self.cards.public_cases(), "profile": self._public_profile()}

    def start_session(self, case_id: str) -> dict[str, object]:
        with self._lock:
            card = self.cards.get(case_id)
            matcher = self._matcher_factory(card) if self._matcher_factory else None
            engine = EncounterEngine(card, concept_matcher=matcher)
            engine.start()
            session_id = str(uuid4())
            self._sessions[session_id] = SessionState(card=card, engine=engine)
            self._persist_session(session_id, self._sessions[session_id], "started")
            return self._session_payload(session_id, self._sessions[session_id])

    def ask(self, session_id: str, question: str) -> dict[str, object]:
        with self._lock:
            state = self._session(session_id)
            if state.completed:
                raise ValueError("session is already completed")
            result = state.engine.ask(question)
            self._persist_session(
                session_id,
                state,
                "question_answered",
                {"result_kind": result.kind, "concept_ids": list(result.concept_ids)},
            )
            payload = self._session_payload(session_id, state)
            payload["result"] = {"kind": result.kind}
            return payload

    def complete(self, session_id: str, assessment: object) -> dict[str, object]:
        with self._lock:
            state = self._session(session_id)
            if state.completed:
                raise ValueError("session is already completed")
            if not state.engine.can_complete:
                raise ValueError("ask the patient at least one question before submitting")
            clean_assessment = self._validate_assessment(assessment)
            report = state.engine.evaluate()
            assessment_results = evaluate_clinical_assessment(
                state.card,
                clean_assessment,
                allowed_concept_ids=state.engine.disclosed_concepts,
            )
            assessment_weaknesses: dict[str, int] = {}
            for item in assessment_results:
                if item["status"] == "needs_review":
                    tag = str(item["weakness_tag"])
                    assessment_weaknesses[tag] = assessment_weaknesses.get(tag, 0) + 1
            resolved_weakness_tags = {
                item["weakness_tag"]
                for item in state.card["cpx_checklist"]
                if item["id"] in report.completed_items
            }
            resolved_weakness_tags.update(
                str(item["weakness_tag"])
                for item in assessment_results
                if item["status"] == "completed"
            )
            self._profile.update(
                report,
                assessment_weaknesses,
                resolved_weakness_tags=resolved_weakness_tags,
                case_id=state.card["case_id"],
            )
            self._save_profile()
            state.completed = True
            state.learner_assessment = clean_assessment
            next_case_mode = determine_next_case_mode(report, assessment_results)
            blueprint = select_next_case_blueprint(
                self._profile,
                state.card,
                mode=next_case_mode,
            )
            recommended_case = self.cards.recommend_next(
                state.card["case_id"],
                blueprint.focus_tags,
                mode=blueprint.mode,
                recent_case_ids=tuple(self._profile.recent_case_ids),
            )
            self._persist_session(
                session_id,
                state,
                "completed",
                {
                    "coverage_percent": round(report.coverage * 100),
                    "next_case_mode": blueprint.mode,
                },
            )
            return {
                "session_id": session_id,
                "report": self._report_payload(
                    state.card,
                    report.to_dict(),
                    state.engine.messages,
                    assessment_results,
                ),
                "profile": self._public_profile(),
                "next_case": {
                    "mode": blueprint.mode,
                    "directions": list(blueprint.directions),
                    "constraints": list(blueprint.constraints),
                    "case": recommended_case,
                },
            }

    def profile(self) -> dict[str, object]:
        return self._public_profile()

    def _session(self, session_id: str) -> SessionState:
        try:
            return self._sessions[session_id]
        except KeyError as exc:
            raise KeyError(f"unknown session_id: {session_id}") from exc

    def _session_payload(self, session_id: str, state: SessionState) -> dict[str, object]:
        snapshot = state.engine.public_snapshot()
        messages = [
            {
                "role": message["role"],
                "content": message["content"],
                "timestamp": message["timestamp"],
            }
            for message in snapshot["messages"]
        ]
        return {
            "session_id": session_id,
            "case": CardRepository._public_case(state.card),
            "session": {
                "messages": messages,
                "boundary_event_count": snapshot["boundary_event_count"],
                "asked_count": snapshot["asked_count"],
                "can_complete": snapshot["can_complete"],
            },
        }

    def _public_profile(self) -> dict[str, object]:
        return {"encounter_count": self._profile.encounter_count}

    def _restore_sessions(self) -> None:
        for saved in self._session_store.load_all():
            try:
                card = self.cards.get(str(saved["case_id"]))
                matcher = self._matcher_factory(card) if self._matcher_factory else None
                engine = EncounterEngine(card, concept_matcher=matcher)
                engine.restore(saved["engine_state"])
                assessment = saved["learner_assessment"]
                if assessment is not None:
                    assessment = self._validate_assessment(assessment)
                self._sessions[str(saved["session_id"])] = SessionState(
                    card=card,
                    engine=engine,
                    completed=bool(saved["completed"]),
                    learner_assessment=assessment,
                )
            except (KeyError, TypeError, ValueError):
                continue

    def _persist_session(
        self,
        session_id: str,
        state: SessionState,
        event_type: str,
        event_payload: dict[str, object] | None = None,
    ) -> None:
        self._session_store.save(
            session_id,
            state.card["case_id"],
            state.engine.persistence_snapshot(),
            completed=state.completed,
            learner_assessment=state.learner_assessment,
            event_type=event_type,
            event_payload=event_payload,
        )

    @staticmethod
    def _validate_assessment(assessment: object) -> dict[str, str]:
        if not isinstance(assessment, dict):
            raise ValueError("assessment must be an object")
        clean: dict[str, str] = {}
        for field_name in sorted(LEARNER_ASSESSMENT_FIELDS):
            value = assessment.get(field_name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"assessment.{field_name} is required")
            normalized = value.strip()
            if len(normalized) > 2000:
                raise ValueError(f"assessment.{field_name} is too long")
            clean[field_name] = normalized
        return clean

    @staticmethod
    def _report_payload(
        card: dict[str, Any],
        raw: dict[str, Any],
        messages: tuple[dict[str, object], ...],
        assessment_results: tuple[dict[str, object], ...],
    ) -> dict[str, object]:
        completed = set(raw["completed_items"])
        missed = set(raw["missed_items"])
        directions = card["adaptive_curriculum"]["directions"]
        items = []
        for concept in card["cpx_checklist"]:
            status = "completed" if concept["id"] in completed else "missed"
            if concept["id"] not in completed and concept["id"] not in missed:
                continue
            items.append(
                {
                    "id": concept["id"],
                    "label": concept["label"],
                    "status": status,
                    "category": "문진",
                    "critical": concept["critical"],
                    "feedback": (
                        "문진에서 확인했습니다."
                        if status == "completed"
                        else directions.get(concept["weakness_tag"], "다음 문진에서 이 항목을 확인합니다.")
                    ),
                    "why_it_matters": concept["why_it_matters"],
                    "learner_evidence": [
                        str(message["content"])
                        for message in messages
                        if message.get("role") == "learner"
                        and concept["id"] in message.get("concept_ids", [])
                    ],
                    "evidence": list(concept.get("evidence", [])),
                }
            )
        for result in assessment_results:
            items.append(
                {
                    key: value
                    for key, value in result.items()
                    if key != "weakness_tag"
                }
                | {"category": "임상 판단", "critical": False}
            )
        return {
            "assessment_scope": {
                "instrument_type": card["evaluation_metadata"]["instrument_type"],
                "rubric_version": card["evaluation_metadata"]["rubric_version"],
                "formal_validation_status": card["evaluation_metadata"]["formal_validation_status"],
            },
            "coverage_percent": round(float(raw["coverage"]) * 100),
            "critical_completed_count": len(raw["critical_completed"]),
            "critical_missed_count": len(raw["critical_missed"]),
            "boundary_event_count": int(raw["boundary_event_count"]),
            "assessment_review_count": sum(
                1 for item in assessment_results if item["status"] == "needs_review"
            ),
            "communication_notes": list(raw["communication_notes"]),
            "safety_flags": list(raw["safety_flags"]),
            "items": items,
        }

    def _load_profile(self) -> WeaknessProfile:
        if not self._profile_path.exists():
            return WeaknessProfile()
        try:
            payload = json.loads(self._profile_path.read_text(encoding="utf-8"))
            return WeaknessProfile.from_dict(payload)
        except (OSError, ValueError, TypeError, json.JSONDecodeError):
            return WeaknessProfile()

    def _save_profile(self) -> None:
        self._profile_path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self._profile_path.with_suffix(".tmp")
        temporary.write_text(
            json.dumps(self._profile.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        temporary.replace(self._profile_path)


def codex_matcher_factory(card: dict[str, Any]) -> CodexConceptMatcher:
    return CodexConceptMatcher()
