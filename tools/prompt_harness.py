from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from cpx_agent.src.bad_news_backend import (
    BadNewsCaseRepository,
    build_checklist_evaluator_prompt,
    build_patient_system_prompt,
    build_ppi_evaluator_prompt,
)


DEFAULT_DATA_DIR = ROOT / "cpx_agent" / "data" / "bad_news"
DEFAULT_CASE_ID = "B05-breast-cancer"
DEFAULT_DIFFICULTY = "중간"
DEFAULT_INITIAL_EMOTION = "분노"


def _resolve_data_dir(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def _case_errors(case: dict[str, Any], checklist: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for key in (
        "case_id",
        "case_title",
        "display_name",
        "chart_visible_to_learner",
        "instruction_to_learner",
        "patient_persona",
        "checklist_scope",
    ):
        if key not in case:
            errors.append(f"missing case key: {key}")
    scope = case.get("checklist_scope", {})
    if not isinstance(scope, dict):
        return [*errors, "checklist_scope must be an object"]
    core = checklist.get("core_checklist", {})
    critical = checklist.get("critical_fail", {})
    for code in scope.get("core_required", []):
        if code not in core:
            errors.append(f"unknown core checklist item: {code}")
    for code in scope.get("critical_fail_watchlist", []):
        if code not in critical:
            errors.append(f"unknown critical fail item: {code}")
    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate and render imported bad-news CPX prompts.")
    parser.add_argument("--data-dir", default=str(DEFAULT_DATA_DIR.relative_to(ROOT)))
    parser.add_argument("--bad-news-case", "--case-id", dest="case_id", default=DEFAULT_CASE_ID)
    parser.add_argument("--difficulty", default=DEFAULT_DIFFICULTY)
    parser.add_argument("--initial-emotion", default=DEFAULT_INITIAL_EMOTION)
    parser.add_argument("--transcript")
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--print-patient-prompt", action="store_true")
    parser.add_argument("--print-checklist-prompt", action="store_true")
    parser.add_argument("--print-ppi-prompt", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    data_dir = _resolve_data_dir(args.data_dir)
    repository = BadNewsCaseRepository(data_dir)
    case = repository.get(args.case_id)
    checklist = repository.checklist
    errors = _case_errors(case, checklist)
    if errors:
        for error in errors:
            print(f"FAIL {error}")
        return 1

    if args.validate_only:
        print(f"OK bad-news case valid: {args.case_id}")
        return 0

    if args.print_patient_prompt:
        print(build_patient_system_prompt(case, args.difficulty, args.initial_emotion))
        return 0

    if args.print_checklist_prompt:
        print(build_checklist_evaluator_prompt(case, checklist, args.initial_emotion))
        if args.transcript:
            print("\n[Transcript]\n" + args.transcript)
        return 0

    if args.print_ppi_prompt:
        print(build_ppi_evaluator_prompt(case, checklist, args.initial_emotion))
        if args.transcript:
            print("\n[Transcript]\n" + args.transcript)
        return 0

    print(f"OK bad-news case valid: {args.case_id}")
    print("Use --print-patient-prompt, --print-checklist-prompt, or --print-ppi-prompt to render prompts.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
