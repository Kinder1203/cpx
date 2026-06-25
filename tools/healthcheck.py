from __future__ import annotations

import argparse
import subprocess
import sys
import tomllib
from pathlib import Path
from typing import Any

import yaml

try:
    from tools.project_state_mcp import lookup_validation_for_path
except ModuleNotFoundError:
    from project_state_mcp import lookup_validation_for_path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_PATHS = [
    "README.md",
    "AGENTS.md",
    "REPO_DESIGN_GUIDE.md",
    ".gitignore",
    "requirements.txt",
    ".codex/config.toml",
    ".codex/CONTEXT_POLICY.md",
    ".codex/state/global_state.yaml",
    ".codex/state/cpx_agent_state.yaml",
    ".codex/state/validation_map.yaml",
    ".codex/state/mcp_policy.yaml",
    ".codex/state/artifact_policy.yaml",
    ".codex/mcp_profiles/README.md",
    ".codex/mcp_profiles/app_ui_optional.toml",
    ".agents/skills/README.md",
    ".agents/skills/app-product-spec/SKILL.md",
    ".agents/skills/app-design-system/SKILL.md",
    ".agents/skills/app-ui-qa/SKILL.md",
    "cpx_agent/README.md",
    "cpx_agent/AGENTS.md",
    "cpx_agent/docs/cpx_protocol.md",
    "cpx_agent/docs/demo_plan.md",
    "cpx_agent/prompts/patient_role.md",
    "cpx_agent/prompts/evaluator.md",
    "cpx_agent/prompts/safety.md",
    "cpx_agent/data/README.md",
    "cpx_agent/data/patient_cards/chest_pain_example.json",
    "cpx_agent/tests/README.md",
    "docs/app/README.md",
    "docs/app/prd.md",
    "docs/app/functional_spec.md",
    "docs/app/user_flows.md",
    "docs/app/wireframes.md",
    "docs/app/design.md",
    "docs/app/serious_simulation_direction.md",
    "docs/app/frontend_stack_decision.md",
    "docs/app/pixel_asset_pipeline.md",
    "docs/app/design_reference_intake.md",
    "docs/app/visual_quality_bar.md",
    "tools/README.md",
    "tools/bootstrap_codex.py",
    "tools/project_state_mcp.py",
    "tools/prompt_harness.py",
]

ACTIVE_SKILLS = {
    "cpx-orient",
    "pre-implementation-grill",
    "cpx-guard",
    "prompt-harness",
    "diagnose-failure",
    "state-hygiene",
    "context-checkpoint",
    "app-product-spec",
    "app-design-system",
    "app-ui-qa",
}

DISABLED_PLUGINS = {
    "binance@openai-curated-remote",
    "data-analytics@openai-curated-remote",
    "figma@openai-curated-remote",
    "openai-developers@openai-curated-remote",
    "github@openai-curated",
    "google-drive@openai-curated",
    "documents@openai-primary-runtime",
    "spreadsheets@openai-primary-runtime",
    "presentations@openai-primary-runtime",
    "pdf@openai-primary-runtime",
    "computer-use@openai-bundled",
    "browser@openai-bundled",
    "chrome@openai-bundled",
}


def _yaml(relative: str) -> dict[str, Any]:
    parsed = yaml.safe_load((ROOT / relative).read_text(encoding="utf-8"))
    if not isinstance(parsed, dict):
        raise ValueError(f"{relative} must be a YAML mapping")
    return parsed


def _line(ok: bool, message: str) -> str:
    return f"{'OK  ' if ok else 'FAIL'} {message}"


def check_layout() -> tuple[list[str], bool]:
    lines: list[str] = []
    passed = True
    for relative in REQUIRED_PATHS:
        exists = (ROOT / relative).exists()
        passed &= exists
        lines.append(_line(exists, f"required path: {relative}"))
    return lines, passed


def check_state() -> tuple[list[str], bool]:
    lines: list[str] = []
    passed = True
    global_state = _yaml(".codex/state/global_state.yaml")
    cpx = _yaml(".codex/state/cpx_agent_state.yaml")
    stance = cpx.get("current_stance", {})
    contract = cpx.get("cpx_contract", {})
    prompt_contract = cpx.get("prompt_contract", {})
    state_budget = cpx.get("project_structure", {}).get("state_budget", {})
    checks = {
        "active track is cpx_agent only": global_state.get("tracks", {}).get("active") == ["cpx_agent"],
        "status is hackathon scaffold": cpx.get("status") == "hackathon_preparation_scaffold",
        "app framework undecided": stance.get("app_framework_decided") is False,
        "llm provider undecided": stance.get("llm_provider_decided") is False,
        "api key not required now": stance.get("api_key_required_now") is False,
        "design priority recorded": stance.get("design_priority") == "ui_ux_quality_over_backend_completeness_for_demo",
        "backend demo stance recorded": stance.get("backend_stance") == "demo_or_mocked_backend_until_day_of_requirements_are_known",
        "real patient data disallowed": stance.get("real_patient_data_allowed") is False,
        "diagnosis/treatment product goal disabled": stance.get("diagnosis_or_treatment_product_goal") is False,
        "hidden diagnosis not shown": stance.get("hidden_diagnosis_may_be_shown_to_user") is False,
        "patient-card driven": contract.get("patient_card_driven") is True,
        "patient role only": contract.get("patient_role_only") is True,
        "reveal only when asked": contract.get("reveal_only_when_asked") is True,
        "evaluate after encounter": contract.get("evaluate_after_encounter") is True,
        "blocks hidden diagnosis leak": "hidden_diagnosis_leak" in prompt_contract.get("must_block", []),
        "blocks doctor role switch": "doctor_role_switch" in prompt_contract.get("must_block", []),
        "state line budget recorded": state_budget.get("active_state_soft_max_lines") == 800,
        "state size budget recorded": state_budget.get("active_state_soft_max_kib") == 36,
    }
    for label, result in checks.items():
        passed &= result
        lines.append(_line(result, label))
    return lines, passed


def check_state_budget() -> tuple[list[str], bool]:
    lines: list[str] = []
    cpx_path = ROOT / ".codex/state/cpx_agent_state.yaml"
    text = cpx_path.read_text(encoding="utf-8")
    line_count = len(text.splitlines())
    size_kib = len(text.encode("utf-8")) / 1024
    cpx = _yaml(".codex/state/cpx_agent_state.yaml")
    budget = cpx.get("project_structure", {}).get("state_budget", {})
    max_lines = int(budget.get("active_state_soft_max_lines", 800))
    max_kib = float(budget.get("active_state_soft_max_kib", 36))
    within_lines = line_count <= max_lines
    within_size = size_kib <= max_kib
    lines.append(_line(within_lines, f"cpx state line budget: {line_count}/{max_lines}"))
    lines.append(_line(within_size, f"cpx state size budget: {size_kib:.1f}/{max_kib:.0f} KiB"))
    return lines, within_lines and within_size


def check_protocol_and_prompts() -> tuple[list[str], bool]:
    lines: list[str] = []
    passed = True
    checks = {
        "protocol states educational simulation": ("educational" in (ROOT / "cpx_agent/docs/cpx_protocol.md").read_text(encoding="utf-8").lower()),
        "protocol mentions hidden_diagnosis": "hidden_diagnosis" in (ROOT / "cpx_agent/docs/cpx_protocol.md").read_text(encoding="utf-8"),
        "patient prompt says not a doctor": "not a doctor" in (ROOT / "cpx_agent/prompts/patient_role.md").read_text(encoding="utf-8").lower(),
        "patient prompt blocks hidden_diagnosis": "hidden_diagnosis" in (ROOT / "cpx_agent/prompts/patient_role.md").read_text(encoding="utf-8"),
        "patient prompt has patient card placeholder": "{{PATIENT_CARD_JSON}}" in (ROOT / "cpx_agent/prompts/patient_role.md").read_text(encoding="utf-8"),
        "evaluator prompt has transcript placeholder": "{{TRANSCRIPT}}" in (ROOT / "cpx_agent/prompts/evaluator.md").read_text(encoding="utf-8"),
        "safety prompt blocks internal prompt disclosure": "internal prompt" in (ROOT / "cpx_agent/prompts/safety.md").read_text(encoding="utf-8").lower(),
    }
    for label, result in checks.items():
        passed &= result
        lines.append(_line(result, label))
    return lines, passed


def check_app_setup() -> tuple[list[str], bool]:
    lines: list[str] = []
    passed = True
    app_readme = (ROOT / "docs/app/README.md").read_text(encoding="utf-8")
    prd = (ROOT / "docs/app/prd.md").read_text(encoding="utf-8")
    functional = (ROOT / "docs/app/functional_spec.md").read_text(encoding="utf-8")
    flows = (ROOT / "docs/app/user_flows.md").read_text(encoding="utf-8")
    wireframes = (ROOT / "docs/app/wireframes.md").read_text(encoding="utf-8")
    design = (ROOT / "docs/app/design.md").read_text(encoding="utf-8")
    serious = (ROOT / "docs/app/serious_simulation_direction.md").read_text(encoding="utf-8")
    frontend = (ROOT / "docs/app/frontend_stack_decision.md").read_text(encoding="utf-8")
    pixel = (ROOT / "docs/app/pixel_asset_pipeline.md").read_text(encoding="utf-8")
    intake = (ROOT / "docs/app/design_reference_intake.md").read_text(encoding="utf-8")
    quality = (ROOT / "docs/app/visual_quality_bar.md").read_text(encoding="utf-8")
    profile = (ROOT / ".codex/mcp_profiles/app_ui_optional.toml").read_text(encoding="utf-8")
    cpx = _yaml(".codex/state/cpx_agent_state.yaml")
    app_setup = cpx.get("app_setup", {})
    checks = {
        "app docs mention Playwright": "Playwright" in app_readme,
        "app docs mention Figma": "Figma" in app_readme,
        "PRD records non-goals": "Non-Goals" in prd,
        "functional spec records MVP screens": "MVP Screens" in functional,
        "user flows include encounter": "Run Encounter" in flows,
        "wireframes include desktop": "Desktop" in wireframes,
        "design doc has token contract": "Token Contract" in design,
        "design doc has Figma direction": "Figma" in design,
        "design doc records demo priority": "UI/UX quality" in design,
        "serious simulation doc records pixel CPX direction": (
            "2D pixel" in serious and "CPX" in serious and "serious simulation" in serious
        ),
        "serious simulation doc uses safe state wording": "Patient Stability" in serious and "Critical Safety Event" in serious,
        "serious simulation doc preserves hidden-field safety": "Hidden diagnosis" in serious and "evaluator keys" in serious,
        "frontend stack doc records default React Vite path": "React + Vite + TypeScript" in frontend,
        "frontend stack doc keeps framework undecided until scaffold": "app_framework_decided" in frontend and "false" in frontend,
        "frontend stack doc blocks default heavy systems": "Do not add by default" in frontend and "Database" in frontend,
        "pixel pipeline doc records sprite metadata contract": "Metadata Contract" in pixel and "spritesheets" in pixel,
        "pixel pipeline doc uses CSS steps first": "CSS `steps()`" in pixel,
        "pixel pipeline doc records provenance": "provenance" in pixel and "license" in pixel.lower(),
        "design intake gates Figma Community": "Figma Community" in intake,
        "design intake checks license": "license" in intake.lower(),
        "visual quality bar has anti-AI rules": "Anti-AI Rules" in quality,
        "visual quality bar checks desktop": "Desktop should show" in quality,
        "visual quality bar checks mobile": "Mobile should show" in quality,
        "optional Playwright MCP snippet present": "@playwright/mcp@latest" in profile,
        "optional Figma MCP snippet present": "https://mcp.figma.com/mcp" in profile,
        "optional MCP profile not auto-loaded": "Not loaded automatically" in profile,
        "state points to app docs": app_setup.get("docs_dir") == "docs/app",
        "state points to visual quality bar": app_setup.get("visual_quality_bar") == "docs/app/visual_quality_bar.md",
        "state points to serious simulation direction": app_setup.get("serious_simulation_direction") == "docs/app/serious_simulation_direction.md",
        "state points to frontend stack decision": app_setup.get("frontend_stack_decision") == "docs/app/frontend_stack_decision.md",
        "state points to pixel asset pipeline": app_setup.get("pixel_asset_pipeline") == "docs/app/pixel_asset_pipeline.md",
        "state records default frontend path": app_setup.get("default_frontend_path") == "react_vite_typescript_until_scaffold_or_day_of_switch_condition",
        "state records pixel asset contract": app_setup.get("pixel_asset_contract") == "sprite_sheets_with_metadata_css_steps_first",
        "state keeps optional MCP disabled": app_setup.get("keep_disabled_by_default") is True,
    }
    for label, result in checks.items():
        passed &= result
        lines.append(_line(result, label))
    return lines, passed


def check_skills() -> tuple[list[str], bool]:
    lines: list[str] = []
    present = {path.parent.name for path in (ROOT / ".agents" / "skills").glob("*/SKILL.md")}
    passed = present == ACTIVE_SKILLS
    lines.append(_line(passed, f"active skill set: {sorted(present)}"))
    for skill in sorted(ACTIVE_SKILLS):
        text = (ROOT / ".agents" / "skills" / skill / "SKILL.md").read_text(encoding="utf-8")
        valid = text.startswith("---\n") and f"name: {skill}" in text
        passed &= valid
        lines.append(_line(valid, f"skill metadata: {skill}"))
    return lines, passed


def check_mcp() -> tuple[list[str], bool]:
    lines: list[str] = []
    passed = True
    with (ROOT / ".codex" / "config.toml").open("rb") as handle:
        config = tomllib.load(handle)
    policy = _yaml(".codex/state/mcp_policy.yaml")
    global_state = _yaml(".codex/state/global_state.yaml")
    configured = set(config.get("mcp_servers", {}))
    defaults = set(policy.get("defaults", {}).get("repo_default", []))
    active = set(global_state.get("mcp", {}).get("active", []))
    checks = {
        "only project-state MCP configured": configured == {"project-state"},
        "MCP policy default matches config": defaults == configured,
        "global active MCP matches config": active == configured,
        "project-state is read only": policy.get("project_state", {}).get("read_only") is True,
        "app UI MCP profile disabled by default": policy.get("optional_profiles", {}).get("app_ui", {}).get("default_enabled") is False,
    }
    for label, result in checks.items():
        passed &= result
        lines.append(_line(result, label))
    return lines, passed


def check_codex_config() -> tuple[list[str], bool]:
    lines: list[str] = []
    passed = True
    with (ROOT / ".codex" / "config.toml").open("rb") as handle:
        config = tomllib.load(handle)
    plugins = config.get("plugins", {})
    memories = config.get("memories", {})
    checks = {
        "project docs capped at 32 KiB": config.get("project_doc_max_bytes") == 32768,
        "auto compact token limit is 80k": config.get("model_auto_compact_token_limit") == 80000,
        "tool output token limit is 6k": config.get("tool_output_token_limit") == 6000,
        "default verbosity is low": config.get("model_verbosity") == "low",
        "memories generation disabled": memories.get("generate_memories") is False,
        "memories usage disabled": memories.get("use_memories") is False,
    }
    for plugin in sorted(DISABLED_PLUGINS):
        plugin_config = plugins.get(plugin)
        checks[f"plugin disabled: {plugin}"] = isinstance(plugin_config, dict) and plugin_config.get("enabled") is False
    for label, result in checks.items():
        passed &= result
        lines.append(_line(result, label))
    return lines, passed


def check_patient_card_harness() -> tuple[list[str], bool]:
    result = subprocess.run(
        [
            sys.executable,
            "tools/prompt_harness.py",
            "--patient-card",
            "cpx_agent/data/patient_cards/chest_pain_example.json",
            "--validate-only",
        ],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        timeout=30,
        check=False,
    )
    ok = result.returncode == 0 and "OK patient card valid" in result.stdout
    return [_line(ok, "prompt harness validates sample patient card")], ok


def check_validation_routes() -> tuple[list[str], bool]:
    lines: list[str] = []
    passed = True
    paths = [
        "README.md",
        "cpx_agent/docs/cpx_protocol.md",
        "cpx_agent/prompts/patient_role.md",
        "cpx_agent/data/patient_cards/chest_pain_example.json",
        "cpx_agent/tests/test_patient_card.py",
        "docs/app/design.md",
        "docs/app/serious_simulation_direction.md",
        "docs/app/frontend_stack_decision.md",
        "docs/app/pixel_asset_pipeline.md",
        "docs/app/visual_quality_bar.md",
        ".codex/mcp_profiles/app_ui_optional.toml",
        ".codex/state/cpx_agent_state.yaml",
        ".agents/skills/cpx-guard/SKILL.md",
        ".agents/skills/app-ui-qa/SKILL.md",
        "tools/project_state_mcp.py",
    ]
    for relative in paths:
        try:
            route = lookup_validation_for_path(relative)
            ok = bool(route.get("commands"))
        except Exception:
            ok = False
        passed &= ok
        lines.append(_line(ok, f"validation route: {relative}"))
    return lines, passed


def check_project_state_cli() -> tuple[list[str], bool]:
    lines: list[str] = []
    passed = True
    commands = [
        (["--print-root-summary"], "cpx_agent"),
        (["--print-track-summary", "cpx_agent"], "hackathon_preparation_scaffold"),
        (["--print-session-start", "cpx_agent", "--repo-path", "cpx_agent/prompts/patient_role.md"], "patient_card_driven"),
        (["--print-resource", "app://design"], "Token Contract"),
        (["--print-resource", "app://serious-simulation-direction"], "Patient Stability"),
        (["--print-resource", "app://frontend-stack-decision"], "React + Vite + TypeScript"),
        (["--print-resource", "app://pixel-asset-pipeline"], "sprite sheets"),
        (["--print-resource", "app://visual-quality-bar"], "Anti-AI Rules"),
        (["--print-validation-for", "cpx_agent/prompts/patient_role.md"], "prompt"),
    ]
    for args, needle in commands:
        result = subprocess.run(
            [sys.executable, "tools/project_state_mcp.py", *args],
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=30,
            check=False,
        )
        ok = result.returncode == 0 and needle in result.stdout
        passed &= ok
        lines.append(_line(ok, f"project-state {' '.join(args)}"))
    return lines, passed


def check_bootstrap_cli() -> tuple[list[str], bool]:
    result = subprocess.run(
        [sys.executable, "tools/bootstrap_codex.py"],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        timeout=30,
        check=False,
    )
    ok = result.returncode == 0 and "project-state session-start works" in result.stdout
    return [_line(ok, "bootstrap_codex status check")], ok


def check_artifact_policy() -> tuple[list[str], bool]:
    lines: list[str] = []
    policy = _yaml(".codex/state/artifact_policy.yaml")
    rules = [str(rule).lower() for rule in policy.get("rules", [])]
    joined = "\n".join(rules)
    checks = {
        "generated sessions not source of truth": "generated session logs" in joined and "source of truth" in joined,
        "real patient data disallowed": "real patient data" in joined,
        "secrets disallowed": "api keys" in joined or "secrets" in joined,
        "deletion requires instruction": "do not delete generated artifacts" in joined,
    }
    passed = all(checks.values())
    for label, result in checks.items():
        lines.append(_line(result, label))
    return lines, passed


def check_changed_paths(paths: list[str] | None) -> tuple[list[str], bool]:
    if not paths:
        return [_line(True, "no explicit path-routing request")], True
    lines: list[str] = []
    passed = True
    for value in paths:
        try:
            route = lookup_validation_for_path(value)
            ok = bool(route.get("matched_prefix"))
        except Exception:
            ok = False
        passed &= ok
        lines.append(_line(ok, f"changed path route: {value}"))
    return lines, passed


def main() -> int:
    parser = argparse.ArgumentParser(description="CODE MEDI CPX Agent structural healthcheck")
    parser.add_argument("--paths", nargs="+")
    args = parser.parse_args()

    sections = [
        ("Layout", check_layout),
        ("State", check_state),
        ("State Budget", check_state_budget),
        ("Protocol and Prompts", check_protocol_and_prompts),
        ("App Setup", check_app_setup),
        ("Skills", check_skills),
        ("MCP", check_mcp),
        ("Codex Config", check_codex_config),
        ("Prompt Harness", check_patient_card_harness),
        ("Validation Routing", check_validation_routes),
        ("Project State", check_project_state_cli),
        ("Bootstrap", check_bootstrap_cli),
        ("Artifacts", check_artifact_policy),
        ("Requested Paths", lambda: check_changed_paths(args.paths)),
    ]
    overall = True
    for title, function in sections:
        print(f"[{title}]")
        lines, passed = function()
        overall &= passed
        for line in lines:
            print(line)
        print()
    return 0 if overall else 1


if __name__ == "__main__":
    raise SystemExit(main())
