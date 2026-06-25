# Optional MCP Profiles

The active repo config stays intentionally small: only `project-state` is enabled by default.
Files in this folder are reference profiles for focused sessions. Copy a reviewed block into
`.codex/config.toml` only when the task needs it, then remove it when the task is done.

## App UI Profile

Use `.codex/mcp_profiles/app_ui_optional.toml` for:

- Playwright MCP: iterative UI exploration where persistent browser state is worth the token
  cost.
- Figma MCP: selected Figma frame/component work, design-system extraction, or live UI capture.

Do not enable remote MCP servers just because they are available. Record the reason in the task
or state update, and keep secrets/auth outside the repository.
