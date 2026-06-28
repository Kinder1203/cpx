from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from cpx_agent.src.cpx_core import patient_card_errors


PATIENT_PROMPT = ROOT / "cpx_agent" / "prompts" / "patient_role.md"
EVALUATOR_PROMPT = ROOT / "cpx_agent" / "prompts" / "evaluator.md"


def load_patient_card(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("patient card must be a JSON object")
    return data


def validate_patient_card(card: dict[str, Any]) -> list[str]:
    return patient_card_errors(card)


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
