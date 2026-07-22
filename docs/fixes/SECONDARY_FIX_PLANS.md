# 次重要问题修复方案（稳定性 / 性能）

> 目标：双机/长跑/fan-out 下 **不断线、不拖垮、UI 可用**。  
> 正确性核心未落地前，本层以 **L0 运维** 为主，避免过早大改 server 热路径。

---

## 总原则

1. **先量后改**：用现有日志/metrics 证明瓶颈再上 L1。  
2. **可回滚**：性能补丁必须单独分支、单独 tag（`fix-scale.N`），方便回退。  
3. **不牺牲正确性**：缓存必须有失效条件（对照 #3016 教训）。

---

## #3012 host JWT 过期后 reconnect 永久 403

### 功能目标
`omnigent login` 认证的 host，在 session JWT 过期后，**自动续期或可无交互恢复**，reconnect 不再永久 403。

### 方案 A — 止血（L0，推荐先做）
| 项 | 内容 |
|----|------|
| 做法 | ① 提高 TTL 环境变量（仅推迟）；② **cron/计划任务** 在 TTL-1h 执行 `omnigent login`（或设备码流程）；③ 文档 runbook：403 时先查 token 过期再查权限 |
| 改点 | `ops/host-relogin/` 脚本 + Windows 任务计划 / systemd timer |
| 分支 | `ops/host-jwt-relogin` |
| 验收 | 模拟过期后脚本可恢复 tunnel，无需猜「版本不兼容」 |

### 方案 B — 功能修复（L1）
| 项 | 内容 |
|----|------|
| 做法 | login 存储 refresh 材料；host reconnect 时刷新 access token（对齐 device-auth 已有 refresh，或 managed runner mint 模式） |
| 改点 | `cli_auth.py` store_token/load_token、`host/connect.py` 取 token、server host tunnel 鉴权错误信息（过期要明示） |
| 测试 | 过期 token → refresh → tunnel 200；refresh 失效 → 明确 error |
| 分支 | `fix/scale-jwt-renew-3012` |

### 方案 C — 上游完整（L2）
| 项 | 内容 |
|----|------|
| 做法 | `omnigent login` 默认走 device-auth + refresh；OIDC/accounts 统一；错误文案区分 expired vs unauthorized |
| PR | `fix(server): renew host session credentials after JWT expiry (#3012)` |
| 说明 | issue 正文称已有实现进行中，**先 watch 上游 PR**，避免重复造轮子；无动静再 L1 |

---

## #3004 每个 streamed event 重载 conversation + ACL

### 功能目标
单 turn 流式路径查询次数显著下降（数量级：从 ~13k/turn 降到可接受范围），fan-out 下 pool 不打满。

### 方案 A — 止血（L0）
| 项 | 内容 |
|----|------|
| 做法 | 限制并行 agent 数；关非必要 UI 订阅；DB 连接池调大仅作缓冲 |
| 分支 | `ops/fanout-limits` |

### 方案 B — 功能修复（L1，推荐）
| 项 | 内容 |
|----|------|
| 做法 | 在 turn/stream 上下文缓存 conversation metadata + ACL；事件循环内复用；写路径使缓存失效 |
| 改点 | server stream/event 处理（`comp:server`） |
| 测试 | 单 turn 事件 N 次，DB query 计数近似 O(1) 于事件数 |
| 分支 | `fix/scale-stream-acl-3004` |

### 方案 C — 上游完整（L2）
| 项 | 内容 |
|----|------|
| 做法 | 引入 request-scoped unit of work；指标：`stream_event_queries` histogram |
| PR | `perf(server): cache conversation+ACL across stream events (#3004)` |

---

## #3003 Policy engine 每次评估重建

### 功能目标
policy 评估热路径不再每次 `build_policy_engine` + 全树扫描；tool call 延迟明显下降。

### 方案 A — 止血（L0）
| 项 | 内容 |
|----|------|
| 做法 | 减少 policy 触发频率；gate 条件尽量用确定性检查（文件/测试）而非每 tool policy |
| 分支 | `ops/policy-light-gates` |

### 方案 B — 功能修复（L1，推荐）
| 项 | 内容 |
|----|------|
| 做法 | 进程内复用 policy engine；conversation tree 增量缓存；评估接口只传 delta |
| 改点 | `comp:policies` + server 评估入口 |
| 测试 | 连续 100 次评估，engine 构建次数 = 1（或配置变更时 +1） |
| 分支 | `fix/scale-policy-cache-3003` |

### 方案 C — 上游完整（L2）
| 项 | 内容 |
|----|------|
| 做法 | 与 #3004 统一缓存层；避免两套失效语义 |
| PR | `perf(policies): reuse policy engine across evaluations (#3003)` |

---

## #2702 Native idle-detection 高频 tmux capture-pane

### 功能目标
多 terminal fan-out 时 idle 检测不再主导 runner CPU。

### 方案 A — 止血（L0）
| 项 | 内容 |
|----|------|
| 做法 | 控制同时 native terminal 数量；能用 SDK 的路径少开 native TUI |
| 分支 | `ops/native-fanout-cap` |

### 方案 B — 功能修复（L1，推荐）
| 项 | 内容 |
|----|------|
| 做法 | 降频 + 多 pane 批处理 capture；或改用 tmux pipe-pane / 事件驱动代替轮询 |
| 改点 | runner native idle watcher（`comp:runner`/`comp:harnesses`） |
| 测试 | 16 terminal 时 CPU 占用对比基线下降（脚本采样） |
| 分支 | `fix/scale-idle-tmux-2702` |

### 方案 C — 上游完整（L2）
| 项 | 内容 |
|----|------|
| 做法 | 可配置 `idle_poll_hz`；文档写清默认与 fan-out 建议 |
| PR | `perf(runner): reduce native idle-detection tmux overhead (#2702)` |

---

## #3001 GET /v1/sessions 预取全部 conversation id

### 功能目标
sessions 列表延迟与 **page size** 相关，而非 O(全部可访问会话)。

### 方案 A — 止血（L0）
| 项 | 内容 |
|----|------|
| 做法 | 少开 Web UI 狂刷；会话归档/清理 |
| 分支 | 可不建分支，runbook 即可 |

### 方案 B — 功能修复（L1）
| 项 | 内容 |
|----|------|
| 做法 | 列表查询分页下推；去掉「每请求预取全部 id」 |
| 改点 | server sessions list handler |
| 测试 | 1000 sessions 时 p95 不再固定 ~230ms+线性恶化 |
| 分支 | `fix/scale-sessions-list-3001` |

### 方案 C — 上游完整（L2）
| 项 | 内容 |
|----|------|
| 做法 | 与 Web UI 虚拟列表联动 |
| PR | `perf(server): paginate sessions list without full id prefetch (#3001)` |

---

## 次重要层实施节奏

| 阶段 | 做什么 | 版本 |
|------|--------|------|
| 现在 | #3012 L0 定时 re-login + fan-out 限流 | `ops/*` 合 main 可不打 fix-scale tag |
| 核心 fix-core.N 之后 | #3004 / #3003（server 热路径） | `v*-zhcn.fix-scale.1` |
| 多 native 并行痛时 | #2702 | `fix-scale.2` |
| UI 抱怨时 | #3001 | `fix-scale.3` |

```bash
git checkout -b fix/scale-jwt-renew-3012 main
# ...
git commit -m "fix(server): renew host credentials after JWT expiry (#3012)"
gh pr create --base main
# merge 后
git tag -a v0.6.0-zhcn.fix-scale.1 -m "scale: jwt renew + ..."
git push origin v0.6.0-zhcn.fix-scale.1
```

---

## 验收矩阵（次重要）

| ID | 操作 | 期望 |
|----|------|------|
| S-3012 | token 过期后 reconnect | 自动恢复或明确「已过期请 login」 |
| S-3004 | 单 turn 流式 | 查询次数显著下降 |
| S-3003 | 连续 policy 评估 | 不再每次全量 rebuild |
| S-2702 | 多 native terminal | runner CPU 明显下降 |
| S-3001 | 大量 sessions 列表 | 延迟随 page 改善 |
