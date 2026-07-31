# 架构决策记录

本文记录 `omnigent-zh-cn` 的已确认架构取舍。它用于指导后续智能体，不能替代
上游 Omnigent 文档或模型服务商的使用条款。

## ADR-001：多工具指令一致性采用 Omnigento，但不把它当作运行时组件

**状态：建议采用，尚未接入。**

[rugovit/omnigento](https://github.com/rugovit/omnigento) 的作用是维护一个权威的
项目指令来源，并生成供 Codex、Claude Code、Copilot、Cursor 等工具读取的指令视图。

- 适合解决 `AGENTS.md`、`CLAUDE.md`、Copilot 指令等内容长期漂移的问题。
- 不负责 Omnigent harness 配置、模型路由、tmux、MCP 服务或多 CLI 调度。
- 接入时必须在独立分支先执行迁移和差异审查；现有指令文件中包含的发布、平台和
  安全约束必须完整迁入权威来源后再生成视图。

## ADR-002：图谱记忆以实验性 WSL2 侧车方式验证，不进入当前稳定主链路

**状态：后续 PoC。**

[johnymontana/omnigent-graph](https://github.com/johnymontana/omnigent-graph) 通过 MCP
侧车提供跨会话、跨智能体的图谱记忆。它可记录研究证据、架构决策、推理轨迹和审查
发现，从而让主理人、Kimi、Claude、Qwen、Hermes 在新会话或 Fork 后继续获得项目上下文。

- 它补足共享记忆，不修复 CLI 登录、Windows PTY、tmux 稳定性、模型地区可用性或
  Hermes 首次投递语义。
- 上游项目仍是 Alpha，且示例面向官方 `omnigent`；接入时需要验证与
  `omnigent-zh` 的兼容性，不能直接照抄安装命令。
- Obsidian 仍是人工可读、可审计的项目知识主库；图谱只作为机器可查询的记忆索引，
  不得成为阻断任务执行的策略依赖。
- PoC 应在 WSL2 独立工作区完成：先启动记忆侧车，只选一个研究智能体和一个审查智能体，
  验证跨会话召回、故障降级和项目隔离，再考虑团队级使用。

## ADR-003：固定出口网络与 tmux 的边界

**状态：待选型。**

tmux 不提供 VPN 或代理能力。固定出口必须由 tmux 启动之前已经建立的 WSL2 网络层或
进程代理层提供，并至少满足以下条件：

1. DNS 和 IPv6 不得绕过预期出口。
2. 出口失联时必须阻断受管 CLI 的外网流量，不能静默回落到直连。
3. `localhost`、Omnigent 本地服务和 WSL2 内部地址必须明确配置为不走外部代理。
4. 固定出口只能用于服务条款、法律和账号资格允许的访问；它不能保证或绕过模型服务
   的地区、账号或风控限制。
5. VPN 凭据、模型 API Key、订阅链接和代理认证信息只能保存在本机受控配置中，禁止提交
   到 Git、Agent YAML、tmux 配置或聊天记录。

后续方案必须包含出口健康检查、DNS/IPv6 泄漏检查、断线阻断验证和 tmux 重启后的恢复测试。
