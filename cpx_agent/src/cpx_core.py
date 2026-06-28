from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timezone
import re
import unicodedata
from typing import Any, Callable, Iterable


REQUIRED_TOP_LEVEL = {
    "schema_version",
    "case_id",
    "title",
    "publication",
    "evidence",
    "evaluation_metadata",
    "patient_profile",
    "disclosure_policy",
    "conversation_style",
    "cpx_checklist",
    "safety_notes",
    "adaptive_curriculum",
    "curriculum_metadata",
    "clinical_assessment_rubric",
}
REQUIRED_PROFILE = {"name", "age", "sex", "chief_complaint", "hidden_diagnosis"}
REQUIRED_CONVERSATION_STYLE = {
    "opening_line",
    "tone",
    "medical_knowledge_level",
    "default_answer_length",
    "emotion",
}
REQUIRED_CHECKLIST_FIELDS = {
    "id",
    "label",
    "keywords",
    "patient_response",
    "weakness_tag",
    "critical",
    "why_it_matters",
}
LEARNER_ASSESSMENT_FIELDS = {
    "problem_summary",
    "primary_impression",
    "differential_diagnoses",
    "reasoning",
}
RUBRIC_CRITERION_KINDS = {"term_match", "term_group_match", "concept_coverage"}
FREQUENCY_BANDS = {"common", "occasional", "uncommon"}
CLINICAL_IMPORTANCE_BANDS = {"routine", "high", "critical"}
PATIENT_CARD_SCHEMA_VERSION = "1.2.0"
PUBLICATION_STATUSES = {"draft", "demo_only", "validated", "retired"}
CLINICAL_REVIEW_STATUSES = {"pending", "approved", "changes_requested"}


def _has_text(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _is_text_list(value: object, *, allow_empty: bool = False) -> bool:
    return (
        isinstance(value, list)
        and (allow_empty or bool(value))
        and all(_has_text(item) for item in value)
    )


def normalize_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value).casefold()
    normalized = re.sub(r"[^0-9a-z가-힣]+", " ", normalized)
    return " ".join(normalized.split())


def _keyword_matches(normalized_question: str, keyword: str) -> bool:
    normalized_keyword = normalize_text(keyword)
    if not normalized_keyword:
        return False

    question_tokens = normalized_question.split()
    keyword_tokens = normalized_keyword.split()
    if len(keyword_tokens) > 1:
        width = len(keyword_tokens)
        return any(
            question_tokens[index : index + width] == keyword_tokens
            for index in range(len(question_tokens) - width + 1)
        )

    token = keyword_tokens[0]
    if token.isascii():
        return token in question_tokens
    if len(token) == 1:
        korean_particles = {
            "은", "는", "이", "가", "을", "를", "의", "에", "에서", "에게", "께",
            "와", "과", "도", "만", "부터", "까지", "로", "으로", "랑", "이랑",
            "나", "이나", "보다", "처럼", "께서",
        }
        return any(
            candidate == token or candidate[len(token) :] in korean_particles
            for candidate in question_tokens
            if candidate.startswith(token)
        )
    return token in normalized_question


def _contains_forbidden_term(text: str, term: str) -> bool:
    return _keyword_matches(normalize_text(text), term)


def _contains_affirmed_term(text: str, term: str) -> bool:
    """Return true only when at least one term occurrence is not obviously negated."""
    text_tokens = normalize_text(text).split()
    term_tokens = normalize_text(term).split()
    if not text_tokens or not term_tokens:
        return False

    negation_before = {
        "no", "not", "without", "denies", "denied", "exclude", "excluding",
        "아닌", "아니고", "없음", "없다", "배제",
    }
    negation_after = {
        "아니다", "아닙니다", "아님", "아닌", "아니라고", "배제", "배제함",
        "unlikely", "excluded",
    }
    width = len(term_tokens)
    for index in range(len(text_tokens) - width + 1):
        candidate_tokens = text_tokens[index : index + width]
        if not all(
            candidate == expected
            or (not expected.isascii() and candidate.startswith(expected))
            for candidate, expected in zip(candidate_tokens, term_tokens)
        ):
            continue
        before = set(text_tokens[max(0, index - 3) : index])
        after = set(text_tokens[index + width : index + width + 4])
        if before & negation_before or after & negation_after:
            continue
        if "가능성" in after and ("낮다" in after or "낮음" in after):
            continue
        return True
    return False


def patient_card_errors(card: object) -> list[str]:
    if not isinstance(card, dict):
        return ["patient card must be a JSON object"]

    errors: list[str] = []
    missing = sorted(REQUIRED_TOP_LEVEL - set(card))
    if missing:
        errors.append(f"missing top-level keys: {missing}")
    for key in ("case_id", "title"):
        if not _has_text(card.get(key)):
            errors.append(f"{key} must be text")

    if card.get("schema_version") != PATIENT_CARD_SCHEMA_VERSION:
        errors.append(f"schema_version must be {PATIENT_CARD_SCHEMA_VERSION}")

    publication = card.get("publication")
    if not isinstance(publication, dict):
        errors.append("publication must be an object")
    else:
        status = publication.get("status")
        if status not in PUBLICATION_STATUSES:
            errors.append("publication.status is not supported")
        if publication.get("content_type") != "synthetic_educational_case":
            errors.append("publication.content_type must be synthetic_educational_case")
        review = publication.get("clinical_review")
        if not isinstance(review, dict):
            errors.append("publication.clinical_review must be an object")
        else:
            review_status = review.get("status")
            if review_status not in CLINICAL_REVIEW_STATUSES:
                errors.append("publication.clinical_review.status is not supported")
            if status == "validated":
                if review_status != "approved":
                    errors.append("validated cards require approved clinical review")
                for key in ("reviewer_id", "reviewed_at", "review_due_at"):
                    if not _has_text(review.get(key)):
                        errors.append(f"validated cards require clinical_review.{key}")

    evaluation_metadata = card.get("evaluation_metadata")
    if not isinstance(evaluation_metadata, dict):
        errors.append("evaluation_metadata must be an object")
    else:
        if evaluation_metadata.get("instrument_type") != "formative":
            errors.append("evaluation_metadata.instrument_type must be formative")
        if not _has_text(evaluation_metadata.get("rubric_version")):
            errors.append("evaluation_metadata.rubric_version must be text")
        if evaluation_metadata.get("formal_validation_status") != "not_validated":
            errors.append("evaluation_metadata.formal_validation_status must be not_validated")

    profile = card.get("patient_profile")
    if not isinstance(profile, dict):
        errors.append("patient_profile must be an object")
        hidden_diagnosis = ""
    else:
        missing_profile = sorted(REQUIRED_PROFILE - set(profile))
        if missing_profile:
            errors.append(f"missing patient_profile keys: {missing_profile}")
        for key in ("name", "sex", "chief_complaint", "hidden_diagnosis"):
            if not _has_text(profile.get(key)):
                errors.append(f"patient_profile.{key} must be text")
        age = profile.get("age")
        if not isinstance(age, int) or isinstance(age, bool) or age <= 0:
            errors.append("patient_profile.age must be a positive integer")
        hidden_diagnosis = str(profile.get("hidden_diagnosis", "")).strip()

    policy = card.get("disclosure_policy")
    if not isinstance(policy, dict):
        errors.append("disclosure_policy must be an object")
    else:
        never_disclose = policy.get("never_disclose")
        if not _is_text_list(never_disclose):
            errors.append("disclosure_policy.never_disclose must be a non-empty string list")
        elif "hidden_diagnosis" not in never_disclose:
            errors.append("hidden_diagnosis must be listed in never_disclose")
        if not _is_text_list(policy.get("can_open_with")):
            errors.append("disclosure_policy.can_open_with must be a non-empty string list")
        if not _is_text_list(policy.get("only_if_asked"), allow_empty=True):
            errors.append("disclosure_policy.only_if_asked must be a string list")

    style = card.get("conversation_style")
    if not isinstance(style, dict):
        errors.append("conversation_style must be an object")
    else:
        missing_style = sorted(REQUIRED_CONVERSATION_STYLE - set(style))
        if missing_style:
            errors.append(f"conversation_style missing fields: {missing_style}")
        for key in REQUIRED_CONVERSATION_STYLE:
            if not _has_text(style.get(key)):
                errors.append(f"conversation_style.{key} must be text")

    checklist = card.get("cpx_checklist")
    checklist_ids: set[str] = set()
    weakness_tags: set[str] = set()
    if not isinstance(checklist, list) or not checklist:
        errors.append("cpx_checklist must be a non-empty list")
    else:
        for index, item in enumerate(checklist):
            if not isinstance(item, dict):
                errors.append(f"cpx_checklist item {index} must be an object")
                continue
            missing_fields = sorted(REQUIRED_CHECKLIST_FIELDS - set(item))
            if missing_fields:
                errors.append(f"cpx_checklist item {index} missing fields: {missing_fields}")
            concept_id = item.get("id")
            if not _has_text(concept_id):
                errors.append(f"cpx_checklist item {index} id must be text")
            elif concept_id in checklist_ids:
                errors.append(f"duplicate cpx_checklist id: {concept_id}")
            else:
                checklist_ids.add(concept_id)
            if not _has_text(item.get("label")):
                errors.append(f"cpx_checklist item {index} label must be text")
            if not _is_text_list(item.get("keywords")):
                errors.append(f"cpx_checklist item {index} keywords must be a non-empty string list")
            response = item.get("patient_response")
            if not _has_text(response):
                errors.append(f"cpx_checklist item {index} patient_response must be text")
            elif hidden_diagnosis and normalize_text(hidden_diagnosis) in normalize_text(response):
                errors.append(f"cpx_checklist item {index} patient_response reveals hidden diagnosis")
            weakness_tag = item.get("weakness_tag")
            if not _has_text(weakness_tag):
                errors.append(f"cpx_checklist item {index} weakness_tag must be text")
            else:
                weakness_tags.add(weakness_tag)
            if not isinstance(item.get("critical"), bool):
                errors.append(f"cpx_checklist item {index} critical must be boolean")
            if not _has_text(item.get("why_it_matters")):
                errors.append(f"cpx_checklist item {index} why_it_matters must be text")

    if isinstance(policy, dict):
        can_open_with = policy.get("can_open_with")
        only_if_asked = policy.get("only_if_asked")
        never_disclose = policy.get("never_disclose")
        public_concepts = {
            item
            for values in (can_open_with, only_if_asked)
            if isinstance(values, list)
            for item in values
            if isinstance(item, str)
        }
        unclassified = sorted(checklist_ids - public_concepts)
        if unclassified:
            errors.append(f"cpx_checklist concepts missing from disclosure policy: {unclassified}")
        unknown_public = sorted(public_concepts - checklist_ids)
        if unknown_public:
            errors.append(f"disclosure policy contains unknown concepts: {unknown_public}")
        if isinstance(can_open_with, list) and len(can_open_with) != len(set(can_open_with)):
            errors.append("disclosure_policy.can_open_with contains duplicates")
        if isinstance(only_if_asked, list) and len(only_if_asked) != len(set(only_if_asked)):
            errors.append("disclosure_policy.only_if_asked contains duplicates")
        if isinstance(can_open_with, list) and isinstance(only_if_asked, list):
            overlap = sorted(set(can_open_with) & set(only_if_asked))
            if overlap:
                errors.append(f"disclosure policy groups overlap: {overlap}")
        private_concepts = checklist_ids & {
            item
            for values in (never_disclose,)
            if isinstance(values, list)
            for item in values
            if isinstance(item, str)
        }
        if private_concepts:
            errors.append(f"private concepts must not be checklist items: {sorted(private_concepts)}")

    safety = card.get("safety_notes")
    if not isinstance(safety, dict):
        errors.append("safety_notes must be an object")
    else:
        for key in ("educational_only", "do_not_offer_treatment", "do_not_reveal_hidden_diagnosis"):
            if safety.get(key) is not True:
                errors.append(f"safety_notes.{key} must be true")
        if not _is_text_list(safety.get("boundary_terms")):
            errors.append("safety_notes.boundary_terms must be a non-empty string list")
        forbidden_terms = safety.get("forbidden_terms")
        if not _is_text_list(forbidden_terms):
            errors.append("safety_notes.forbidden_terms must be a non-empty string list")
        for key in ("boundary_response", "fallback_response"):
            if not _has_text(safety.get(key)):
                errors.append(f"safety_notes.{key} must be text")
        leak_terms = [hidden_diagnosis]
        if isinstance(forbidden_terms, list):
            leak_terms.extend(term for term in forbidden_terms if isinstance(term, str))
        public_patient_texts = [
            str(card.get("case_id", "")),
            str(card.get("title", "")),
        ]
        if isinstance(checklist, list):
            for item in checklist:
                if not isinstance(item, dict):
                    continue
                public_patient_texts.extend(
                    str(item.get(key, ""))
                    for key in ("id", "label", "patient_response", "why_it_matters")
                )
                evidence = item.get("evidence", [])
                if isinstance(evidence, list):
                    for entry in evidence:
                        if isinstance(entry, dict):
                            public_patient_texts.extend(
                                str(entry.get(key, "")) for key in ("title", "url")
                            )
        public_patient_texts.extend(
            str(safety.get(key, "")) for key in ("boundary_response", "fallback_response")
        )
        rubric = card.get("clinical_assessment_rubric")
        if isinstance(rubric, list):
            for item in rubric:
                if isinstance(item, dict):
                    public_patient_texts.extend(
                        str(item.get(key, ""))
                        for key in (
                            "id",
                            "label",
                            "feedback_pass",
                            "feedback_review",
                            "why_it_matters",
                        )
                    )
        adaptive = card.get("adaptive_curriculum")
        if isinstance(adaptive, dict):
            public_patient_texts.append(str(adaptive.get("default_focus", "")))
            directions = adaptive.get("directions")
            if isinstance(directions, dict):
                public_patient_texts.extend(str(value) for value in directions.values())
        if any(
            term.strip() and _contains_forbidden_term(text, term)
            for term in leak_terms
            for text in public_patient_texts
        ):
            errors.append("public card content reveals a forbidden diagnosis term")

    rubric = card.get("clinical_assessment_rubric")
    if not isinstance(rubric, list) or not rubric:
        errors.append("clinical_assessment_rubric must be a non-empty list")
    else:
        rubric_ids: set[str] = set()
        for index, item in enumerate(rubric):
            prefix = f"clinical_assessment_rubric item {index}"
            if not isinstance(item, dict):
                errors.append(f"{prefix} must be an object")
                continue
            for key in (
                "id",
                "label",
                "field",
                "weakness_tag",
                "feedback_pass",
                "feedback_review",
                "why_it_matters",
            ):
                if not _has_text(item.get(key)):
                    errors.append(f"{prefix} {key} must be text")
            rubric_id = item.get("id")
            if _has_text(rubric_id):
                if rubric_id in rubric_ids:
                    errors.append(f"duplicate clinical assessment rubric id: {rubric_id}")
                rubric_ids.add(rubric_id)
            field_name = item.get("field")
            if _has_text(field_name) and field_name not in LEARNER_ASSESSMENT_FIELDS:
                errors.append(f"{prefix} field is not supported: {field_name}")
            weakness_tag = item.get("weakness_tag")
            if _has_text(weakness_tag):
                weakness_tags.add(weakness_tag)

            criterion = item.get("criterion")
            if not isinstance(criterion, dict):
                errors.append(f"{prefix} criterion must be an object")
                continue
            kind = criterion.get("kind")
            if kind not in RUBRIC_CRITERION_KINDS:
                errors.append(f"{prefix} criterion.kind is not supported")
            elif kind == "term_match" and not _is_text_list(criterion.get("terms")):
                errors.append(f"{prefix} criterion.terms must be a non-empty string list")
            elif kind == "concept_coverage":
                concept_ids = criterion.get("concept_ids")
                minimum_matches = criterion.get("minimum_matches")
                if not _is_text_list(concept_ids):
                    errors.append(f"{prefix} criterion.concept_ids must be a non-empty string list")
                elif unknown := sorted(set(concept_ids) - checklist_ids):
                    errors.append(f"{prefix} criterion contains unknown concepts: {unknown}")
                if (
                    not isinstance(minimum_matches, int)
                    or isinstance(minimum_matches, bool)
                    or minimum_matches <= 0
                    or (isinstance(concept_ids, list) and minimum_matches > len(concept_ids))
                ):
                    errors.append(f"{prefix} criterion.minimum_matches is invalid")
            elif kind == "term_group_match":
                term_groups = criterion.get("term_groups")
                minimum_matches = criterion.get("minimum_matches")
                valid_groups = (
                    isinstance(term_groups, list)
                    and bool(term_groups)
                    and all(_is_text_list(group) for group in term_groups)
                )
                if not valid_groups:
                    errors.append(f"{prefix} criterion.term_groups must be a non-empty list of string lists")
                if (
                    not isinstance(minimum_matches, int)
                    or isinstance(minimum_matches, bool)
                    or minimum_matches <= 0
                    or (isinstance(term_groups, list) and minimum_matches > len(term_groups))
                ):
                    errors.append(f"{prefix} criterion.minimum_matches is invalid")

    adaptive = card.get("adaptive_curriculum")
    if not isinstance(adaptive, dict):
        errors.append("adaptive_curriculum must be an object")
    else:
        if not _has_text(adaptive.get("default_focus")):
            errors.append("adaptive_curriculum.default_focus must be text")
        if not _has_text(adaptive.get("progression_focus")):
            errors.append("adaptive_curriculum.progression_focus must be text")
        directions = adaptive.get("directions")
        if not isinstance(directions, dict):
            errors.append("adaptive_curriculum.directions must be an object")
        else:
            missing_directions = sorted(tag for tag in weakness_tags if not _has_text(directions.get(tag)))
            if missing_directions:
                errors.append(f"adaptive_curriculum missing directions: {missing_directions}")

    curriculum = card.get("curriculum_metadata")
    if not isinstance(curriculum, dict):
        errors.append("curriculum_metadata must be an object")
    else:
        if not _is_text_list(curriculum.get("topic_tags")):
            errors.append("curriculum_metadata.topic_tags must be a non-empty string list")
        frequency = curriculum.get("frequency_band")
        if frequency not in FREQUENCY_BANDS:
            errors.append("curriculum_metadata.frequency_band is not supported")
        importance = curriculum.get("clinical_importance")
        if importance not in CLINICAL_IMPORTANCE_BANDS:
            errors.append("curriculum_metadata.clinical_importance is not supported")
        if frequency == "uncommon" and importance not in {"high", "critical"}:
            errors.append("uncommon cases must have high or critical clinical importance")

    evidence = card.get("evidence")
    if not isinstance(evidence, dict):
        errors.append("evidence must be an object")
    else:
        if not _is_text_list(evidence.get("synthetic_fields")):
            errors.append("evidence.synthetic_fields must be a non-empty string list")
        sources = evidence.get("sources")
        supported_targets: set[str] = set()
        source_ids: set[str] = set()
        if not isinstance(sources, list) or not sources:
            errors.append("evidence.sources must be a non-empty list")
        else:
            for index, source in enumerate(sources):
                prefix = f"evidence source {index}"
                if not isinstance(source, dict):
                    errors.append(f"{prefix} must be an object")
                    continue
                for key in ("id", "kind", "title", "publisher", "published_at", "url", "accessed_at", "scope"):
                    if not _has_text(source.get(key)):
                        errors.append(f"{prefix} {key} must be text")
                source_id = source.get("id")
                if _has_text(source_id):
                    if source_id in source_ids:
                        errors.append(f"duplicate evidence source id: {source_id}")
                    source_ids.add(source_id)
                url = source.get("url")
                if _has_text(url) and not str(url).startswith("https://"):
                    errors.append(f"{prefix} url must use https")
                supports = source.get("supports")
                if not _is_text_list(supports):
                    errors.append(f"{prefix} supports must be a non-empty string list")
                else:
                    supported_targets.update(supports)
        expected_targets = {
            f"cpx_checklist.{concept_id}" for concept_id in checklist_ids
        }
        if isinstance(rubric, list):
            expected_targets.update(
                f"clinical_assessment_rubric.{item['id']}"
                for item in rubric
                if isinstance(item, dict) and _has_text(item.get("id"))
            )
        unsupported = sorted(expected_targets - supported_targets)
        if unsupported:
            errors.append(f"evidence does not support card targets: {unsupported}")

    return errors


def validate_patient_card(card: object) -> None:
    errors = patient_card_errors(card)
    if errors:
        raise ValueError("; ".join(errors))


def match_question_concepts(question: str, card: dict[str, Any]) -> tuple[str, ...]:
    normalized_question = normalize_text(question)
    if not normalized_question:
        return ()

    scored: list[tuple[int, int, str]] = []
    for order, concept in enumerate(card["cpx_checklist"]):
        matched = {
            normalize_text(keyword)
            for keyword in concept["keywords"]
            if _keyword_matches(normalized_question, keyword)
        }
        if matched:
            score = sum(max(len(keyword.replace(" ", "")), 2) for keyword in matched)
            scored.append((-score, order, concept["id"]))
    scored.sort()
    return tuple(concept_id for _, _, concept_id in scored)


@dataclass(frozen=True)
class AskResult:
    kind: str
    learner_text: str
    patient_text: str
    concept_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class EvaluationReport:
    completed_items: tuple[str, ...]
    missed_items: tuple[str, ...]
    critical_completed: tuple[str, ...]
    critical_missed: tuple[str, ...]
    boundary_event_count: int
    weakness_counts: dict[str, int]
    communication_notes: tuple[str, ...] = ()
    safety_flags: tuple[str, ...] = ()

    @property
    def coverage(self) -> float:
        total = len(self.completed_items) + len(self.missed_items)
        return len(self.completed_items) / total if total else 0.0

    def to_dict(self) -> dict[str, object]:
        return {
            "completed_items": list(self.completed_items),
            "missed_items": list(self.missed_items),
            "critical_completed": list(self.critical_completed),
            "critical_missed": list(self.critical_missed),
            "boundary_event_count": self.boundary_event_count,
            "weakness_counts": dict(self.weakness_counts),
            "communication_notes": list(self.communication_notes),
            "safety_flags": list(self.safety_flags),
            "coverage": self.coverage,
        }


@dataclass
class WeaknessProfile:
    counts: Counter[str] = field(default_factory=Counter)
    encounter_count: int = 0
    recent_case_ids: list[str] = field(default_factory=list)

    def update(
        self,
        report: EvaluationReport,
        additional_weakness_counts: dict[str, int] | None = None,
        *,
        resolved_weakness_tags: Iterable[str] = (),
        case_id: str | None = None,
    ) -> None:
        for tag in set(resolved_weakness_tags):
            if self.counts[tag] <= 1:
                self.counts.pop(tag, None)
            else:
                self.counts[tag] -= 1
        self.counts.update(report.weakness_counts)
        if additional_weakness_counts:
            self.counts.update(additional_weakness_counts)
        self.encounter_count += 1
        if case_id:
            self.recent_case_ids = [
                previous for previous in self.recent_case_ids if previous != case_id
            ]
            self.recent_case_ids.append(case_id)
            self.recent_case_ids = self.recent_case_ids[-8:]

    def ranked(self) -> tuple[str, ...]:
        return tuple(tag for tag, _ in sorted(self.counts.items(), key=lambda item: (-item[1], item[0])))

    def to_dict(self) -> dict[str, object]:
        return {
            "encounter_count": self.encounter_count,
            "counts": dict(self.counts),
            "recent_case_ids": list(self.recent_case_ids),
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "WeaknessProfile":
        counts = payload.get("counts", {})
        clean_counts = {
            str(tag): int(count)
            for tag, count in counts.items()
            if isinstance(tag, str) and isinstance(count, int) and count > 0
        }
        encounter_count = payload.get("encounter_count", 0)
        recent_case_ids = payload.get("recent_case_ids", [])
        clean_recent_case_ids = (
            [case_id for case_id in recent_case_ids if _has_text(case_id)][-8:]
            if isinstance(recent_case_ids, list)
            else []
        )
        return cls(
            Counter(clean_counts),
            encounter_count if isinstance(encounter_count, int) else 0,
            clean_recent_case_ids,
        )


@dataclass(frozen=True)
class NextCaseBlueprint:
    source_case_id: str
    mode: str
    focus_tags: tuple[str, ...]
    directions: tuple[str, ...]
    constraints: tuple[str, ...] = (
        "release_eligible_template_only",
        "must_pass_patient_card_validation",
        "must_preserve_limited_disclosure",
        "prefer_common_or_high_importance_cases",
        "do_not_generate_from_weaknesses_alone",
        "require_clinical_review_before_production_use",
    )

    def to_dict(self) -> dict[str, object]:
        return {
            "source_case_id": self.source_case_id,
            "mode": self.mode,
            "focus_tags": list(self.focus_tags),
            "directions": list(self.directions),
            "constraints": list(self.constraints),
        }


class EncounterEngine:
    def __init__(
        self,
        card: dict[str, Any],
        concept_matcher: Callable[[str, tuple[dict[str, Any], ...]], Iterable[str]] | None = None,
    ):
        validate_patient_card(card)
        self._card = card
        self._concepts = {item["id"]: item for item in card["cpx_checklist"]}
        self._asked: set[str] = set()
        self._disclosed: list[str] = []
        self._messages: list[dict[str, object]] = []
        self._boundary_events: list[str] = []
        self._concept_matcher = concept_matcher
        self._started = False

    @property
    def messages(self) -> tuple[dict[str, object], ...]:
        return tuple(dict(message) for message in self._messages)

    @property
    def disclosed_concepts(self) -> tuple[str, ...]:
        return tuple(self._disclosed)

    @property
    def asked_count(self) -> int:
        return len(self._asked)

    @property
    def can_complete(self) -> bool:
        return any(message["role"] == "learner" for message in self._messages)

    def _contains_boundary_request(self, question: str) -> bool:
        normalized = normalize_text(question)
        return any(
            normalize_text(term) in normalized
            for term in self._card["safety_notes"]["boundary_terms"]
        )

    def _record(self, role: str, content: str, concept_ids: Iterable[str] = ()) -> None:
        self._messages.append(
            {
                "role": role,
                "content": content,
                "concept_ids": list(concept_ids),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

    def start(self) -> dict[str, object]:
        if not self._started:
            self._record("patient", self._card["conversation_style"]["opening_line"])
            self._started = True
        return self.public_snapshot()

    def ask(self, question: str) -> AskResult:
        learner_text = question.strip()
        if not learner_text:
            raise ValueError("question must not be empty")
        self._record("learner", learner_text)

        if self._contains_boundary_request(learner_text):
            self._boundary_events.append(learner_text)
            patient_text = self._card["safety_notes"]["boundary_response"]
            self._record("patient", patient_text)
            return AskResult("boundary", learner_text, patient_text)

        concept_ids = match_question_concepts(learner_text, self._card)
        if not concept_ids and self._concept_matcher is not None:
            try:
                proposed_ids = self._concept_matcher(
                    learner_text,
                    tuple(self._concepts.values()),
                )
                concept_ids = tuple(
                    dict.fromkeys(
                        concept_id
                        for concept_id in proposed_ids
                        if isinstance(concept_id, str) and concept_id in self._concepts
                    )
                )
            except Exception:
                concept_ids = ()
        if not concept_ids:
            patient_text = self._card["safety_notes"]["fallback_response"]
            self._record("patient", patient_text)
            return AskResult("unmatched", learner_text, patient_text)

        self._messages[-1]["concept_ids"] = list(concept_ids)

        responses: list[str] = []
        for concept_id in concept_ids:
            concept = self._concepts[concept_id]
            responses.append(concept["patient_response"])
            self._asked.add(concept_id)
            if concept_id not in self._disclosed:
                self._disclosed.append(concept_id)
        patient_text = " ".join(dict.fromkeys(responses))
        self._record("patient", patient_text, concept_ids)
        return AskResult("answered", learner_text, patient_text, concept_ids)

    def evaluate(self) -> EvaluationReport:
        completed: list[str] = []
        missed: list[str] = []
        critical_completed: list[str] = []
        critical_missed: list[str] = []
        weakness_counts: Counter[str] = Counter()

        for concept in self._card["cpx_checklist"]:
            target = completed if concept["id"] in self._asked else missed
            target.append(concept["id"])
            if concept["critical"]:
                critical_target = critical_completed if concept["id"] in self._asked else critical_missed
                critical_target.append(concept["id"])
            if concept["id"] not in self._asked:
                weakness_counts[concept["weakness_tag"]] += 1
        if self._boundary_events:
            weakness_counts["boundary"] += len(self._boundary_events)

        communication_notes: list[str] = []
        if "chief_complaint" in self._concepts:
            if "chief_complaint" in self._asked:
                communication_notes.append("환자의 주호소를 직접 확인했습니다.")
            else:
                communication_notes.append("환자가 가장 불편한 점을 먼저 확인하는 열린 질문이 필요합니다.")
                weakness_counts["communication"] += 1
        safety_flags = (
            ("진단명 또는 치료 지시 요청이 있어 환자 역할 경계를 유지했습니다.",)
            if self._boundary_events
            else ()
        )

        return EvaluationReport(
            completed_items=tuple(completed),
            missed_items=tuple(missed),
            critical_completed=tuple(critical_completed),
            critical_missed=tuple(critical_missed),
            boundary_event_count=len(self._boundary_events),
            weakness_counts=dict(weakness_counts),
            communication_notes=tuple(communication_notes),
            safety_flags=safety_flags,
        )

    def public_snapshot(self) -> dict[str, object]:
        return {
            "case_id": self._card["case_id"],
            "disclosed_concepts": list(self._disclosed),
            "messages": [dict(message) for message in self._messages],
            "boundary_event_count": len(self._boundary_events),
            "asked_count": len(self._asked),
            "can_complete": self.can_complete,
        }

    def persistence_snapshot(self) -> dict[str, object]:
        """Return private state needed to resume a local educational session."""
        return {
            "case_id": self._card["case_id"],
            "asked": sorted(self._asked),
            "disclosed": list(self._disclosed),
            "messages": [dict(message) for message in self._messages],
            "boundary_events": list(self._boundary_events),
            "started": self._started,
        }

    def restore(self, snapshot: object) -> None:
        """Restore a snapshot produced by ``persistence_snapshot`` after validation."""
        if not isinstance(snapshot, dict) or snapshot.get("case_id") != self._card["case_id"]:
            raise ValueError("session snapshot does not match patient card")
        asked = snapshot.get("asked")
        disclosed = snapshot.get("disclosed")
        messages = snapshot.get("messages")
        boundary_events = snapshot.get("boundary_events")
        if not _is_text_list(asked, allow_empty=True) or set(asked) - set(self._concepts):
            raise ValueError("session snapshot contains invalid asked concepts")
        if not _is_text_list(disclosed, allow_empty=True) or set(disclosed) - set(self._concepts):
            raise ValueError("session snapshot contains invalid disclosed concepts")
        if not isinstance(messages, list) or not all(isinstance(item, dict) for item in messages):
            raise ValueError("session snapshot messages are invalid")
        clean_messages: list[dict[str, object]] = []
        for message in messages:
            role = message.get("role")
            content = message.get("content")
            concept_ids = message.get("concept_ids", [])
            timestamp = message.get("timestamp")
            if role not in {"learner", "patient"} or not _has_text(content):
                raise ValueError("session snapshot message is invalid")
            if not _is_text_list(concept_ids, allow_empty=True) or set(concept_ids) - set(self._concepts):
                raise ValueError("session snapshot message concepts are invalid")
            if not _has_text(timestamp):
                raise ValueError("session snapshot timestamp is invalid")
            clean_messages.append(
                {"role": role, "content": content, "concept_ids": list(concept_ids), "timestamp": timestamp}
            )
        if not _is_text_list(boundary_events, allow_empty=True):
            raise ValueError("session snapshot boundary events are invalid")
        if not isinstance(snapshot.get("started"), bool):
            raise ValueError("session snapshot started flag is invalid")
        self._asked = set(asked)
        self._disclosed = list(dict.fromkeys(disclosed))
        self._messages = clean_messages
        self._boundary_events = list(boundary_events)
        self._started = snapshot["started"]


def evaluate_clinical_assessment(
    card: dict[str, Any],
    assessment: dict[str, str],
    *,
    allowed_concept_ids: Iterable[str] | None = None,
) -> tuple[dict[str, object], ...]:
    """Evaluate learner-authored reasoning against a private, card-defined rubric."""
    validate_patient_card(card)
    allowed_concepts = set(allowed_concept_ids) if allowed_concept_ids is not None else None
    results: list[dict[str, object]] = []
    for rubric_item in card["clinical_assessment_rubric"]:
        field_name = rubric_item["field"]
        learner_text = assessment.get(field_name, "").strip()
        criterion = rubric_item["criterion"]
        kind = criterion["kind"]
        passed = False

        if kind == "term_match":
            passed = any(
                _contains_affirmed_term(learner_text, term)
                for term in criterion["terms"]
            )
        elif kind == "concept_coverage":
            expected = set(criterion["concept_ids"])
            if allowed_concepts is not None:
                expected &= allowed_concepts
            matched = set(match_question_concepts(learner_text, card)) & expected
            passed = len(matched) >= criterion["minimum_matches"]
        elif kind == "term_group_match":
            matched_groups = sum(
                any(_contains_affirmed_term(learner_text, term) for term in term_group)
                for term_group in criterion["term_groups"]
            )
            passed = matched_groups >= criterion["minimum_matches"]

        results.append(
            {
                "id": rubric_item["id"],
                "label": rubric_item["label"],
                "status": "completed" if passed else "needs_review",
                "weakness_tag": rubric_item["weakness_tag"],
                "feedback": (
                    rubric_item["feedback_pass"]
                    if passed
                    else rubric_item["feedback_review"]
                ),
                "why_it_matters": rubric_item["why_it_matters"],
                "learner_evidence": [learner_text] if learner_text else [],
                "evidence": list(rubric_item.get("evidence", [])),
            }
        )
    return tuple(results)


def select_next_case_blueprint(
    profile: WeaknessProfile,
    card: dict[str, Any],
    *,
    max_focus: int = 2,
    mode: str = "remediation",
) -> NextCaseBlueprint:
    validate_patient_card(card)
    if mode not in {"remediation", "progression"}:
        raise ValueError(f"unsupported next-case mode: {mode}")
    adaptive = card["adaptive_curriculum"]
    directions = adaptive["directions"]
    if mode == "progression":
        focus_tags = ()
        selected_directions = (adaptive["progression_focus"],)
    else:
        focus_tags = tuple(tag for tag in profile.ranked() if tag in directions)[:max_focus]
        selected_directions = tuple(directions[tag] for tag in focus_tags)
        if not selected_directions:
            selected_directions = (adaptive["default_focus"],)
    return NextCaseBlueprint(
        source_case_id=card["case_id"],
        mode=mode,
        focus_tags=focus_tags,
        directions=selected_directions,
    )


def determine_next_case_mode(
    report: EvaluationReport,
    assessment_results: Iterable[dict[str, object]],
) -> str:
    """Choose focused remediation unless the current encounter is sufficiently complete."""
    assessment_review_count = sum(
        1 for item in assessment_results if item.get("status") == "needs_review"
    )
    is_ready_to_broaden = (
        report.coverage >= 0.75
        and not report.critical_missed
        and report.boundary_event_count == 0
        and assessment_review_count <= 1
    )
    return "progression" if is_ready_to_broaden else "remediation"
