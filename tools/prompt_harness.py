from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PATIENT_PROMPT = ROOT / "cpx_agent" / "prompts" / "patient_role.md"
EVALUATOR_PROMPT = ROOT / "cpx_agent" / "prompts" / "evaluator.md"

REQUIRED_TOP_LEVEL = {
    "case_id",
    "title",
    "patient_profile",
    "disclosure_policy",
    "conversation_style",
    "cpx_checklist",
    "safety_notes",
}

REQUIRED_PROFILE = {
    "name",
    "age",
    "sex",
    "chief_complaint",
    "hidden_diagnosis",
}


def load_patient_card(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("patient card must be a JSON object")
    return data


def validate_patient_card(card: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    missing = sorted(REQUIRED_TOP_LEVEL - set(card))
    if missing:
        errors.append(f"missing top-level keys: {missing}")

    profile = card.get("patient_profile")
    if not isinstance(profile, dict):
        errors.append("patient_profile must be an object")
    else:
        missing_profile = sorted(REQUIRED_PROFILE - set(profile))
        if missing_profile:
            errors.append(f"missing patient_profile keys: {missing_profile}")

    policy = card.get("disclosure_policy")
    if not isinstance(policy, dict):
        errors.append("disclosure_policy must be an object")
    else:
        never = policy.get("never_disclose")
        if not isinstance(never, list):
            errors.append("disclosure_policy.never_disclose must be a list")
        elif "hidden_diagnosis" not in never:
            errors.append("hidden_diagnosis must be listed in never_disclose")

    checklist = card.get("cpx_checklist")
    if not isinstance(checklist, list) or not checklist:
        errors.append("cpx_checklist must be a non-empty list")
    else:
        for index, item in enumerate(checklist):
            if not isinstance(item, dict) or not item.get("id") or not item.get("label"):
                errors.append(f"cpx_checklist item {index} must include id and label")

    safety = card.get("safety_notes")
    if not isinstance(safety, dict):
        errors.append("safety_notes must be an object")
    else:
        if safety.get("do_not_reveal_hidden_diagnosis") is not True:
            errors.append("safety_notes.do_not_reveal_hidden_diagnosis must be true")
        if safety.get("do_not_offer_treatment") is not True:
            errors.append("safety_notes.do_not_offer_treatment must be true")

    return errors


def render_prompt(template_path: Path, card: dict[str, Any], transcript: str | None = None) -> str:
    template = template_path.read_text(encoding="utf-8")
    patient_card_json = json.dumps(card, ensure_ascii=False, indent=2, sort_keys=True)
    rendered = template.replace("{{PATIENT_CARD_JSON}}", patient_card_json)
    if transcript is not None:
        rendered = rendered.replace("{{TRANSCRIPT}}", transcript)
    return rendered


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate and render CPX patient-card prompts.")
    parser.add_argument("--patient-card", required=True)
    parser.add_argument("--transcript")
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--print-patient-prompt", action="store_true")
    parser.add_argument("--print-evaluator-prompt", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    card_path = Path(args.patient_card)
    if not card_path.is_absolute():
        card_path = ROOT / card_path
    card = load_patient_card(card_path)
    errors = validate_patient_card(card)
    if errors:
        for error in errors:
            print(f"FAIL {error}")
        return 1

    if args.validate_only:
        print(f"OK patient card valid: {card_path.relative_to(ROOT).as_posix()}")
        return 0

    if args.print_patient_prompt:
        print(render_prompt(PATIENT_PROMPT, card))
        return 0

    if args.print_evaluator_prompt:
        transcript = args.transcript or ""
        print(render_prompt(EVALUATOR_PROMPT, card, transcript=transcript))
        return 0

    print(f"OK patient card valid: {card_path.relative_to(ROOT).as_posix()}")
    print("Use --print-patient-prompt or --print-evaluator-prompt to render a template.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
