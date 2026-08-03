# CODEX REVIEW 15 — 阶段 15 native D0/D1 只读验收

> **验收者：** Codex（只读验收/编排）
> **工作树：** `F:\codex-ai\git项目部署\tmp\omnigent-review`
> **验收对象：** `docs/fixes/handoffs/GROK_DIAGNOSIS_15.md`
> **RUN_ID：** `20260730-160451-dc83140-grok-appserver-426-r1`
> **Evidence：** `C:\Users\Administrator\omnigent-diagnostics\20260730-160451-dc83140-grok-appserver-426-r1`
> **冻结 HEAD：** `dc83140c73ceb12fa165753c1880c19f68da86f4`

## 1. 验收结论

**ACCEPT_WITH_NOTES**

接受 Grok 的唯一诊断分类：

```text
DIAG_D1_READY_FOR_D2
```

该结论仅表示：

- 在本 RUN、用户已开启 TUN 且 Grok 只观察不改动的条件下；
- 固定的同一份 native Codex 完成了可信 D0；
- D1 收到了真实 assistant/model item、assistant sentinel 和 `turn/completed`；
- 本轮没有观测到 10100/426 或 app-server `error` method；
- 已具备另开全新 RUN、执行一次 Omnigent C/D2 对照的前置条件。

它不表示 Gate 2 PASS，不证明 r4 的产品路径 240 秒 idle 已修复，也不证明 TUN 是根因或唯一修复。Gate 2 r4 仍为 **FAIL**，当前不可 merge。

本次验收没有重跑 D0、D1、D2、pytest、Ruff、Gate 1 或 Gate 2；没有修改源码、tests、政策、`STATUS.md` 或旧 handoff；没有 commit/push/merge/tag。

## 2. Identity、冻结文件与仓库范围

Evidence 中的 start/end 与当前只读复核均显示：

- HEAD start=end=`dc83140c73ceb12fa165753c1880c19f68da86f4`
- branch=`docs/fix-plans-core-secondary`
- 八个冻结 blob start/end 均 `match=True`
- 当前重新计算的八个 blob 仍与冻结值一致
- `git-status-start.txt` 与 `git-status-end.txt` 除 UTC 行外一致

| 文件 | 冻结/当前 blob | 结果 |
|---|---|---|
| `omnigent/server/routes/_workspace_validation.py` | `5bf5e587b9177a9ecbce572b11656edac31ea7fe` | 匹配 |
| `omnigent/server/routes/sessions.py` | `0375e5f951d82c01c9f67e8cf7b41a90aff10330` | 匹配 |
| `tests/server/routes/test_workspace_validation.py` | `63291bfa4bc47c196e04a218c82b782ecb613786` | 匹配 |
| `tests/server/routes/test_workspace_validation_helpers.py` | `4cae0f53cb724c991a1c502c2919e37da7b7737a` | 匹配 |
| `tests/runner/test_session_workspace_cache.py` | `02cce3ca6e28233d5d0cac350a7be6316ff582d2` | 匹配 |
| `tests/runner/test_app_codex_native_model.py` | `be43ec45816e8ece4192822506df8072580910e0` | 匹配 |
| `tests/runner/test_runner_idle_active_work.py` | `58b24b7d8375d816c54449cb3cd5a9b907d3ebf8` | 匹配 |
| `tests/runner/transports/ws_tunnel/test_serve.py` | `6116218097f2352c467524fd0ddf0838315aa524` | 匹配 |

Tracked 源码/tests/政策文件在本 RUN 前后没有状态或大小漂移。由于 `git-status-*.txt` 将全部未跟踪 handoff 折叠为 `docs/fixes/handoffs/`，它不能逐文件证明“唯一新增文件”这一条；但没有证据显示 Grok 改动了允许范围外的 tracked 文件。这是验收备注，不影响本轮业务诊断。

## 3. 新 RUN、预检与未拼接旧证据

- RUN_ID、evidence 根和 runtime 根均指向本次新 RUN。
- Evidence 文件没有引用旧 14/r4 文件作为本 RUN 的 D0/D1 结果。
- `precheck-processes.txt` 记录诊断驱动 self/ancestor PID，并标记 `DIAG_DRIVER_SELF_OR_ANCESTOR`、`excluded=True`。
- 排除 self/ancestor 后：`count=0`、`pass=True`。
- `.codex-tmp` start 直接子项为空。
- Evidence 根在验收时仍存在；未被删除或迁移。

预检中出现旧 RUN 字符串，是当前诊断驱动命令行的匹配摘要，且已明确归属并排除；不是把旧 RUN evidence 拼接为本 RUN 结果。

## 4. Native 固定

| 项目 | 核验结果 |
|---|---|
| native 路径 | `C:\Users\Administrator\.codex\.sandbox-bin\codex.exe` |
| 版本 | `codex-cli 0.144.0-alpha.4` |
| SHA-256 | `b88f944ef63556527caae2ad43f80b88b8be174dc09b09d9b037fc94240a0e91` |
| shim | `False` |
| D0/D1 同一路径与 SHA | `True` |
| 验收时文件仍存在且 SHA 未变 | `True` |
| 模型 | `gpt-5.6-sol` |

Evidence 也记录了默认 `Get-Command`/`shutil.which` 未找到入口，实际 D0/D1 没有依赖 PATH，而是使用同一个绝对 native 路径。

## 5. D0 核验

`d0-meta.txt`、事件摘要与时间线共同支持：

- exit=`0`
- timeout=`False`
- duration≈42.47s
- 4 个可信 JSON 事件：`thread.started`、`turn.started`、`item.completed`、`turn.completed`
- assistant/final sentinel=`True`
- `D0_PASS=True`
- 10100/426=`False`

stderr 中有一次模型列表刷新子进程退出等待超时，但业务 turn 已成功完成并命中 sentinel；该旁路刷新错误不足以推翻 D0 PASS。

## 6. D1 严格业务规则核验

`d1-protocol-steps.txt`、`d1-frames-sanitized.txt` 与 `d1-timeline.txt` 形成一致时间线：

1. `initialize` 响应可映射；
2. `thread/start` 响应可映射；
3. `turn/start` 响应可映射；
4. 先出现 `userMessage item/started` 与 `userMessage item/completed`；
5. 后出现真实 `agentMessage` 的 `item/started`、多条 delta 和 `item/completed`；
6. assistant sentinel 命中；
7. 最后收到 `turn/completed`；
8. 同 turn 未见 `error` method，未见 10100/426。

因此：

```text
userMessage_echo_not_counted=True
assistant_item=true
assistant_sentinel=true
terminal_state=turn/completed
error_method=false
D1_PASS=true
```

`d1-meta.txt` 的进程 exit 记录为 `-1`，而业务终态、assistant item 和 sentinel 均在进程停止前已经落证；这不推翻 D1 的协议/业务 PASS。但后续 D2 必须分别冻结“业务终态”和“进程退出原因”，不能用 `-1` 代替可信产品 exit。

D2 明确记录为：

```text
NOT_EXECUTED_BY_TASK_DESIGN
```

没有发现本 RUN 执行 D2 的证据。

## 7. TUN 与 10100/426 边界

可接受的原始观测为：

- start：`adapter_name=Meta|status=Up`
- end：`adapter_name=Meta|status=Up`
- end：`up_tun_like_adapter_count=1`
- 10100 LISTEN start/end 均为 `False`
- D0/D1 均未观测到 `127.0.0.1:10100/v1/responses`、426 或相关 error method
- 验收时再次只读查看，`Meta`/`Meta Tunnel` 仍为 `Up`

验收备注：

- `tun-status-start.txt` 的 `up_tun_like_adapter_count` 为空；
- `tun-status-end.txt` 虽然原始 adapter 行是 `Meta|status=Up`，派生字段却写成 `meta_up_at_end=False`、`tun_state_changed=True`；
- 报告已主动披露这是单对象 `.Count` 处理导致的记录脚本问题。

原始 start/end adapter 行支持“本 RUN 起止均为 Up”，所以不将分类降为 `DIAG_INCONCLUSIVE`；但下一张 D2 卡必须强制数组化并记录一致的布尔字段，禁止再次依赖矛盾派生值。

本 RUN 没有 TUN OFF 对照，阶段 14 REWORK evidence 又不可用。因此唯一允许的边界是：

```text
本 RUN、TUN 开启状态下，固定 native D0/D1 可用且未见 10100/426。
```

不得写成“已证明 TUN 是唯一根因”。

## 8. Cleanup、manifest 与 leak-scan

- 六个冻结 PID 均 `dead=True`。
- runtime 已删除，验收时仍不存在。
- D2 port=`NOT_APPLICABLE`。
- 10100/TUN 均记录为 observe-only/not-modified。
- `.codex-tmp` start/end 直接子项集合均为空；验收时当前子项数仍为 0。
- 三个本 RUN private home 均记录绝对目标、叶名、`under_codex_tmp=True`、reparse 处理与逐项删除结果；最终均 `exists_after=False`。
- `cleanup.txt`：`leftover=0`、`evidence_root_exists=True`。
- manifest 含 42 个文件；验收重新计算 42 个 SHA-256，`bad_count=0`。
- leak-scan 扫描 43/43 文件，prompt/credential/auth-config/symlink-target hits 均为 0，`pass=True`。
- `leak-scan.txt` 是 evidence 最后修改文件；其后 evidence 未被改写。

清理日志首部有一条异常的：

```text
skip_missing=omnigent-codex-home-d0-6012c4bdomnigent-codex-home-d1-a7b61532
```

它是两个叶名被拼接的冗余日志项；后续三个真实 home 均分别有 BEGIN/绝对路径/叶名/reparse/删除结果，且 end 集合为空。故记为日志质量备注，不否定清理结果。下一 RUN 不得复用该拼接逻辑。

## 9. 相对阶段 14 的缺口关闭情况

| 既有缺口 | 阶段 15 证据 | 验收 |
|---|---|---|
| evidence 丢失，无法审计 | 新 evidence 根仍存在，manifest 全哈希匹配 | 已关闭 |
| self/ancestor 预检不可信 | 明确排除，`count=0/pass=True` | 已关闭 |
| D0/D1 native 身份不统一 | 同一路径、版本、SHA-256 | 已关闭 |
| userMessage/输入 sentinel 被误计 | 帧中先区分 userMessage，后证明 agentMessage | 已关闭 |
| D1 无真实 assistant 输出 | agentMessage item + sentinel + `turn/completed` | 已关闭 |
| D1 不通过后仍跑 D2 | 本轮 D1 通过，但仍按卡未跑 D2 | 已关闭 |
| cleanup 仅有汇总 | 有 PID、绝对路径、叶名、reparse、逐项结果 | 已关闭（附日志备注） |
| leak-scan 顺序/计数不可验 | scan 最后、43=43、hits=0 | 已关闭 |
| TUN 因果被过度推断 | 报告明确只写本 RUN 相关性 | 已关闭（起止派生字段需修正） |

## 10. Gate、merge 与下一步

- Gate 1：**PASS（相对 main）**，不是全仓 GREEN。
- Gate 2 r4：仍为 **FAIL**。
- 阶段 15：不是 Gate 2 verdict。
- 当前：**不可 merge**。

下一步唯一建议：按 `docs/fixes/handoffs/CODEX_TASK_16.md` 开全新 RUN，只执行一次 Omnigent C/D2，固定 `HARNESS_CODEX_PATH` 到上述 native，模型固定 `gpt-5.6-sol`，保持产品 240 秒 idle watchdog 不变，并做约 1 秒粒度的 spawn/事件 relay 观测。

若 D2 指向需要改源码，只能停止并交回 Codex，由 Codex 另发 Hermes 开发卡；Grok 不得现场修复。

