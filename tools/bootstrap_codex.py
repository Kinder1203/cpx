from __future__ import annotations

import subprocess
import sys
import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPO_CODEX_CONFIG = ROOT / ".codex" / "config.toml"


def _line(ok: bool, message: str) -> str:
    return f"{'OK  ' if ok else 'FAIL'} {message}"


def _exists(relative: str) -> tuple[bool, str]:
    path = ROOT / relative
    return path.exists(), relative


def main() -> int:
    ok = True
    print("Bootstrap status")
    for relative in [
        "AGENTS.md",
        "README.md",
        "REPO_DESIGN_GUIDE.md",
        ".gitignore",
        ".codex/config.toml",
        ".codex/CONTEXT_POLICY.md",
        ".codex/state/global_state.yaml",
        ".codex/state/cpx_agent_state.yaml",
        ".codex/state/mcp_policy.yaml",
        ".agents/skills/README.md",
        "docs/app/serious_simulation_direction.md",
        "docs/app/frontend_stack_decision.md",
        "docs/app/pixel_asset_pipeline.md",
        "tools/project_state_mcp.py",
        "tools/healthcheck.py",
        "tools/prompt_harness.py",
    ]:
        exists, label = _exists(relative)
        ok &= exists
        print(_line(exists, f"required path: {label}"))

    if REPO_CODEX_CONFIG.exists():
        with REPO_CODEX_CONFIG.open("rb") as handle:
            parsed = tomllib.load(handle)
        configured = set(parsed.get("mcp_servers", {}))
        mcp_ok = configured == {"project-state"}
        ok &= mcp_ok
        print(_line(mcp_ok, "repo-default MCP is project-state only"))
        compact_ok = parsed.get("model_auto_compact_token_limit") == 80000
        output_ok = parsed.get("tool_output_token_limit") == 6000
        plugins = parsed.get("plugins", {})
        disabled_plugins = [
            "binance@openai-curated-remote",
            "data-analytics@openai-curated-remote",
            "openai-developers@openai-curated-remote",
            "github@openai-curated",
            "google-drive@openai-curated",
            "browser@openai-bundled",
            "chrome@openai-bundled",
        ]
        plugins_ok = all(
            isinstance(plugins.get(plugin), dict) and plugins[plugin].get("enabled") is False
            for plugin in disabled_plugins
        )
        ok &= compact_ok and output_ok and plugins_ok
        print(_line(compact_ok, "auto compact token limit is 80k"))
        print(_line(output_ok, "tool output token limit is 6k"))
        print(_line(plugins_ok, "default app plugins are disabled"))

    completed = subprocess.run(
        [sys.executable, "tools/project_state_mcp.py", "--print-session-start", "cpx_agent"],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        timeout=30,
        check=False,
    )
    state_ok = completed.returncode == 0 and "case_db_driven" in completed.stdout
    ok &= state_ok
    print(_line(state_ok, "project-state session-start works"))

    print()
    print("Use `python tools/healthcheck.py` for the full structural check.")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
