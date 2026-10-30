# Gate 2 Baseline Freeze Manifest

- 冻结日期：2026-08-03
- 执行者：Hermes 3.8（提交冻结执行者，经用户明确批准）
- 仓库：`https://github.com/professoryu06/omnigent-zh-cn.git`
- 分支：`docs/fix-plans-core-secondary`

## 冻结基线

| 项 | 值 |
|---|---|
| 冻结 HEAD | `c3c4ebad074ddce6b458c77dfe06e1ab76498e84`（Commit 2 后） |
| 原 HEAD | `dc83140c73ceb12fa165753c1880c19f68da86f4` |
| 提交身份 | `professoryu06 <professoryu06@users.noreply.github.com>`（仓库级 local） |
| 工作树状态 | 仅剩 `nul`（D 类垃圾文件）+ `evidence/`（B 类 grok evidence，不提交不删除） |

## Commit 清单

| # | SHA | 内容 | 文件数 |
|---|---|---|---|
| 1 | `e691d08cbfca5e1a36656ced8a0f317b495ffbbe` | fix(core): codex isolation, prompt delivery fail-loud, ws_tunnel, session and workspace fixes (#2853, BUG-1/2/3/24) | 44（+4601/−156） |
| 2 | `c3c4ebad074ddce6b458c77dfe06e1ab76498e84` | docs(fixes): freeze gate specs, status, progress docs and full handoff chain | 124（+27259/−66） |
| 3 | 本提交 | docs(fixes): record Gate 2 baseline freeze SHA and manifest | 2（STATUS.md + 本文件） |

## 排除项（未提交，保留在磁盘）

- `nul` — D 类异常文件（30B 垃圾产物），另列清理卡
- `evidence/grok-native-01/` — B 类 grok evidence，随 grok 功能卡处理
- B 类 grok/WSL 功能代码 — 在 `omnigent-zh-next` 另仓，28D 已确认

## 边界

- 不宣称 Gate 2 PASS、全仓 GREEN 或 mergeable。
- Gate 2 仍需 Codex 另行验收；基线未冻结前禁止开始 Gate 2（现已冻结）。
- 凭据全部 `[REDACTED]`。

## Gate 2 验收记录（2026-08-03 追加）

- **RUN_ID**：`20260803-232354-gate2-sixrounds-r5`（最终验收轮；前置作废轮 `20260803-223647-gate2-sixrounds-r1` / `-r2` / `-r3` / `20260803-231832-gate2-strict-r4` 均判定 INVALID，证据各自保留，未拼接）
- **结论**：**GATE2_PASS**（六轮 C / E-pos / E-pos-strict / E-neg-warn / E-neg-strict / R 全部执行，AC-1~AC-6 全部满足）
- **证据路径**：`C:\Users\Administrator\omnigent-diagnostics\20260803-232354-gate2-sixrounds-r5\`（runner 日志 ×6、receipt-e-pos.json / receipt-e-pos-strict.json、agent YAML ×6、verify 脚本 + verification ALL PASS）
- **验收报告**：`docs/fixes/handoffs/GATE2_REVIEW_20260803-232354-gate2-sixrounds-r5.md`
- **执行载体**：独立基线 stack（server `127.0.0.1:6868` + host-A + host-B(strict) + runner，全部来自 `F:\codex-ai\git项目部署\tmp\omnigent-review-gate2` @ `5c8b9ce96f7552d380276fe6de04651f2b19531a` 的 venv）；现网 6767 / omnigent-zh-next（PID 394481/361176/147181/363062/375662）未触碰
- **GATE2_PASS 边界**：
  - 仅 `codex-native` Phase 2 apply 实证送达（receipt：`harness_id=codex-native, channel=codex_home_config_toml, chars=52/66, sha256` 与 prompt 实测一致；private config 含 `developer_instructions` 键）
  - `claude-native` 为 warn-only（能力矩阵 `NATIVE_PROMPT_CAPABILITY_MATRIX`），未声称送达；E-neg-warn 出现 `chars=52` fail-loud warning，E-neg-strict 在 `OMNIGENT_STRICT_PROMPT=1` 下注入前失败（exit 1，无模型回复）
  - Gate 2 PASS **不等同**全仓 GREEN、不等同可 merge；merge 决定权专属 Codex（Controller）
  - 本记录为文档记录，不构成 commit/push/merge/tag；凭据一律 `[REDACTED]`
