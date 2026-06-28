from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
STATE_DIR = ROOT / ".codex" / "state"
VALIDATION_MAP_PATH = STATE_DIR / "validation_map.yaml"

RESOURCE_SPECS: dict[str, tuple[Path, str]] = {
    "project://global": (STATE_DIR / "global_state.yaml", "text/yaml"),
    "project://skills-index": (ROOT / ".agents" / "skills" / "README.md", "text/markdown"),
    "app://setup": (ROOT / "docs" / "app" / "README.md", "text/markdown"),
    "app://prd": (ROOT / "docs" / "app" / "prd.md", "text/markdown"),
    "app://functional-spec": (ROOT / "docs" / "app" / "functional_spec.md", "text/markdown"),
    "app://user-flows": (ROOT / "docs" / "app" / "user_flows.md", "text/markdown"),
    "app://wireframes": (ROOT / "docs" / "app" / "wireframes.md", "text/markdown"),
    "app://design": (ROOT / "docs" / "app" / "design.md", "text/markdown"),
    "app://serious-simulation-direction": (
        ROOT / "docs" / "app" / "serious_simulation_direction.md",
        "text/markdown",
    ),
    "app://frontend-stack-decision": (ROOT / "docs" / "app" / "frontend_stack_decision.md", "text/markdown"),
    "app://pixel-asset-pipeline": (ROOT / "docs" / "app" / "pixel_asset_pipeline.md", "text/markdown"),
    "app://design-reference-intake": (ROOT / "docs" / "app" / "design_reference_intake.md", "text/markdown"),
    "app://visual-quality-bar": (ROOT / "docs" / "app" / "visual_quality_bar.md", "text/markdown"),
    "cpx-agent://state": (STATE_DIR / "cpx_agent_state.yaml", "text/yaml"),
    "cpx-agent://protocol": (ROOT / "cpx_agent" / "docs" / "cpx_protocol.md", "text/markdown"),
    "cpx-agent://demo-plan": (ROOT / "cpx_agent" / "docs" / "demo_plan.md", "text/markdown"),
    "cpx-agent://patient-role-prompt": (ROOT / "cpx_agent" / "prompts" / "patient_role.md", "text/markdown"),
    "cpx-agent://evaluator-prompt": (ROOT / "cpx_agent" / "prompts" / "evaluator.md", "text/markdown"),
    "cpx-agent://safety-prompt": (ROOT / "cpx_agent" / "prompts" / "safety.md", "text/markdown"),
    "project://artifact-policy": (STATE_DIR / "artifact_policy.yaml", "text/yaml"),
    "project://mcp-policy": (STATE_DIR / "mcp_policy.yaml", "text/yaml"),
    "project://validation-map": (STATE_DIR / "validation_map.yaml", "text/yaml"),
    "project://recent-decisions": (STATE_DIR / "recent_decisions.md", "text/markdown"),
}

TRACK_STATE_URIS = {
    "cpx_agent": "cpx-agent://state",
}


def _read_text(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Missing project file: {path.relative_to(ROOT).as_posix()}")
    return path.read_text(encoding="utf-8")


def _load_yaml(path: Path) -> dict[str, Any]:
    parsed = yaml.safe_load(_read_text(path))
    if not isinstance(parsed, dict):
        raise ValueError(f"State file must parse to a mapping: {path.relative_to(ROOT).as_posix()}")
    return parsed


def _resource_payload(uri: str) -> dict[str, Any]:
    path, media_type = RESOURCE_SPECS[uri]
    raw = _read_text(path)
    payload: dict[str, Any] = {
        "uri": uri,
        "path": path.relative_to(ROOT).as_posix(),
        "media_type": media_type,
        "content": raw,
    }
    if path.suffix in {".yaml", ".yml"}:
        parsed = _load_yaml(path)
        payload["metadata"] = {
            "schema_version": parsed.get("schema_version"),
            "last_reviewed": parsed.get("last_reviewed"),
            "owner": parsed.get("owner"),
        }
    return payload


def _normalize_repo_path(path_value: str) -> str:
    path_str = path_value.strip().replace("\\", "/")
    if not path_str:
        raise ValueError("path must not be empty")
    candidate = Path(path_str)
    if candidate.is_absolute():
        try:
            path_str = candidate.resolve().relative_to(ROOT).as_posix()
        except ValueError:
            path_str = candidate.as_posix()
    while path_str.startswith("./"):
        path_str = path_str[2:]
    return path_str.rstrip("/")


def _path_matches(path_value: str, prefix: str) -> bool:
    normalized_prefix = _normalize_repo_path(prefix)
    return path_value == normalized_prefix or path_value.startswith(normalized_prefix + "/")


def _load_validation_entries() -> list[dict[str, Any]]:
    parsed = _load_yaml(VALIDATION_MAP_PATH)
    entries = parsed.get("entries")
    if not isinstance(entries, list) or not entries:
        raise ValueError("validation_map.yaml must contain a non-empty entries list")
    if not all(isinstance(entry, dict) for entry in entries):
        raise ValueError("validation_map.yaml entries must be mappings")
    return entries


def lookup_validation_for_path(path_value: str) -> dict[str, Any]:
    normalized_path = _normalize_repo_path(path_value)
    best_entry: dict[str, Any] | None = None
    best_prefix = ""

    for entry in _load_validation_entries():
        prefix_value = entry.get("prefix")
        if not isinstance(prefix_value, str):
            raise ValueError("validation_map.yaml entry is missing a string prefix")
        normalized_prefix = _normalize_repo_path(prefix_value)
        if _path_matches(normalized_path, normalized_prefix) and len(normalized_prefix) > len(best_prefix):
            best_entry = entry
            best_prefix = normalized_prefix

    if best_entry is None:
        raise ValueError(f"No validation mapping found for path: {normalized_path}")

    commands = best_entry.get("commands")
    docs_to_reopen = best_entry.get("docs_to_reopen")
    track = best_entry.get("track")
    notes = best_entry.get("notes")
    if not isinstance(commands, list) or not all(isinstance(value, str) for value in commands):
        raise ValueError(f"validation_map entry '{best_prefix}' has invalid commands")
    if not isinstance(docs_to_reopen, list) or not all(isinstance(value, str) for value in docs_to_reopen):
        raise ValueError(f"validation_map entry '{best_prefix}' has invalid docs_to_reopen")
    if not isinstance(track, str) or not isinstance(notes, str):
        raise ValueError(f"validation_map entry '{best_prefix}' is missing track or notes")

    return {
        "path": normalized_path,
        "track": track,
        "matched_prefix": best_prefix,
        "commands": commands,
        "docs_to_reopen": docs_to_reopen,
        "notes": notes,
        "source": VALIDATION_MAP_PATH.relative_to(ROOT).as_posix(),
    }


def build_root_summary() -> dict[str, Any]:
    global_state = _load_yaml(STATE_DIR / "global_state.yaml")
    tracks = global_state.get("tracks", {})
    return {
        "project": global_state.get("project"),
        "tracks": tracks.get("active", []) if isinstance(tracks, dict) else tracks,
        "reading_order": global_state.get("reading_order", []),
        "source_of_truth": global_state.get("source_of_truth", {}),
        "principles": global_state.get("principles", []),
        "current_focus": global_state.get("current_focus", {}),
        "forbidden": global_state.get("forbidden", []),
        "active_mcp": global_state.get("mcp", {}).get("active", []),
        "docs_to_open_first": [
            "README.md",
            "AGENTS.md",
            "REPO_DESIGN_GUIDE.md",
            ".codex/state/global_state.yaml",
        ],
    }


def build_track_summary(track: str) -> dict[str, Any]:
    normalized_track = track.strip().lower()
    if normalized_track not in TRACK_STATE_URIS:
        raise ValueError(f"Unsupported track: {track}")
    global_state = _load_yaml(STATE_DIR / "global_state.yaml")
    track_state = _resource_payload(TRACK_STATE_URIS[normalized_track])
    parsed = _load_yaml(ROOT / track_state["path"])
    return {
        "track": normalized_track,
        "state_path": track_state["path"],
        "last_reviewed": track_state.get("metadata", {}).get("last_reviewed"),
        "reading_order": global_state.get("reading_order", []),
        "source_of_truth": parsed.get("source_of_truth", {}),
        "status": parsed.get("status"),
        "current_stance": parsed.get("current_stance", {}),
        "cpx_contract": parsed.get("cpx_contract", {}),
        "prompt_contract": parsed.get("prompt_contract", {}),
        "harness": parsed.get("harness", {}),
        "project_structure": parsed.get("project_structure", {}),
        "day_of_event_rules": parsed.get("day_of_event_rules", []),
    }


def build_session_start(track: str, path_value: str | None = None) -> dict[str, Any]:
    summary = build_track_summary(track)
    stance = summary["current_stance"]
    compact_stance = {
        key: stance.get(key)
        for key in (
            "event",
            "expected_product",
            "stage",
            "confirmed_topic",
            "app_framework_decided",
            "patient_utterance_owner",
            "codex_cli_model_calls_required",
            "api_key_required_now",
            "real_patient_data_allowed",
            "diagnosis_or_treatment_product_goal",
            "hidden_diagnosis_may_be_shown_to_user",
            "internal_prompt_may_be_shown_to_user",
        )
    }
    session_start: dict[str, Any] = {
        "track": summary["track"],
        "reading_order": summary["reading_order"],
        "state_path": summary["state_path"],
        "last_reviewed": summary["last_reviewed"],
        "source_of_truth": summary["source_of_truth"],
        "current_stance": compact_stance,
        "cpx_contract": summary.get("cpx_contract", {}),
        "active_skills": summary.get("project_structure", {}).get("active_skills", []),
        "harness": summary.get("harness", {}),
        "core_docs_if_track_changes": [
            summary["source_of_truth"]["track_readme"],
            summary["source_of_truth"]["track_agents"],
            summary["source_of_truth"]["protocol"],
        ],
    }
    if path_value:
        session_start["validation_for_path"] = lookup_validation_for_path(path_value)
    else:
        session_start["track_validation"] = summary.get("harness", {}).get("validation", [])
    return session_start


def print_yaml(value: dict[str, Any]) -> None:
    print(yaml.safe_dump(value, sort_keys=False, allow_unicode=True))


def build_server():
    try:
        from fastmcp import FastMCP  # type: ignore
        from starlette.requests import Request  # type: ignore
        from starlette.responses import PlainTextResponse  # type: ignore
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise RuntimeError(
            "FastMCP is not installed. The CLI summary mode works without it; "
            "install FastMCP only if starting the MCP server is needed."
        ) from exc

    mcp = FastMCP(
        name="project-state",
        instructions=(
            "Read-only dynamic state for the CODE MEDI CPX Agent project. "
            "Use session_start(track, path) to bootstrap and validation_for_path(path) "
            "to choose checks for touched files."
        ),
    )

    for uri in RESOURCE_SPECS:
        mcp.resource(uri)(lambda uri=uri: _resource_payload(uri))

    @mcp.tool
    def validation_for_path(path: str) -> dict[str, Any]:
        """Return validation commands and docs to reopen for a repo path."""
        return lookup_validation_for_path(path)

    @mcp.tool
    def session_start(track: str = "cpx_agent", path: str | None = None) -> dict[str, Any]:
        """Return a compact track briefing with optional validation routing."""
        return build_session_start(track, path)

    @mcp.custom_route("/health", methods=["GET"])
    async def health_check(request: Request) -> PlainTextResponse:  # pragma: no cover - HTTP transport only
        del request
        return PlainTextResponse("OK")

    return mcp


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Read-only local MCP server for CPX project dynamic state.")
    parser.add_argument("--print-validation-for", metavar="PATH")
    parser.add_argument("--print-root-summary", action="store_true")
    parser.add_argument("--print-track-summary", choices=("cpx_agent",))
    parser.add_argument("--print-session-start", choices=("cpx_agent",))
    parser.add_argument("--repo-path")
    parser.add_argument("--print-resource", choices=tuple(RESOURCE_SPECS))
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--transport", choices=("stdio", "http"), default="stdio")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--path", default="/mcp")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload: dict[str, Any] | None = None
    if args.print_root_summary:
        payload = build_root_summary()
    elif args.print_validation_for:
        payload = lookup_validation_for_path(args.print_validation_for)
    elif args.print_track_summary:
        payload = build_track_summary(args.print_track_summary)
    elif args.print_session_start:
        payload = build_session_start(args.print_session_start, args.repo_path)
    elif args.print_resource:
        payload = _resource_payload(args.print_resource)

    if payload is not None:
        if args.json:
            print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
        else:
            print_yaml(payload)
        return

    mcp = build_server()
    if args.transport == "http":
        mcp.run(transport="http", host=args.host, port=args.port, path=args.path)
        return
    mcp.run()


if __name__ == "__main__":
    main()
