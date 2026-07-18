export const GLOSSARY = {
  session: "会话",
  conversation: "对话",
  host: "主机",
  runner: "执行器",
  agent: "智能体",
  policy: "策略",
  approval: "授权确认",
  worktree: "Git 工作树",
  sandbox: "沙箱",
} as const;

export const PROTECTED_TERMS = new Set([
  "Codex",
  "Claude Code",
  "Hermes",
  "OpenCode",
  "Cursor",
  "Shell",
  "CLI",
  "JSON",
  "HTTP",
]);
