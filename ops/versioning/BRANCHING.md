# 分支、Tag 与 GitHub 工作流

适用仓库：`professoryu06/omnigent-zh-cn`（完整源码分发，非 submodule）。  
上游：`omnigent-ai/omnigent`（见根目录 [UPSTREAM.md](../../UPSTREAM.md)）。

---

## 1. 保护区

| 分支/资源 | 规则 |
|-----------|------|
| `main` | 禁止直推功能提交；仅 PR 合并 |
| `v*-zhcn*` tags | 已发布不改写；热修新 tag |
| 上游 `omnigent-ai/omnigent` | 只读 remote；贡献走 fork + PR |

建议在 GitHub 设置：

- Branch protection on `main`：Require PR、Require status checks  
- 可选：Restrict who can push tags matching `v*`

---

## 2. 分支类型

| 前缀 | 用途 | 生命周期 |
|------|------|----------|
| `fix/core-*` | 正确性补丁 | 合 main 后删远程分支 |
| `fix/scale-*` | 性能/长跑补丁 | 同上 |
| `ops/*` | 运维脚本、runbook、L0 止血 | 可保留或合后删 |
| `docs/*` | 仅文档 | 合后删 |
| `upstream/sync-YYYYMMDD` | 上游同步 | 合后删 |
| `upstream-pr/*` | 准备提交上游的干净分支 | PR 结束后删 |
| `repro/*` | 复现矩阵 | 可长期 |

---

## 3. Commit 信息

```
fix(harnesses): deliver native agent prompt (#2853)

ops(host): add JWT relogin timer for #3012

docs(fixes): add core/secondary fix plans

test(runner): cover workspace cache poison (#3016)
```

- 类型：`fix` `feat` `perf` `ops` `docs` `test` `chore`  
- scope：`harnesses` `runner` `server` `policies` `repr` `host` …  
- body 必挂上游 issue 号，便于 CHANGELOG 与 STATUS 表。

---

## 4. Tag 语义

```
v0.6.0-zhcn.0              # 与上游/分发对齐的基线
v0.6.0-zhcn.fix-core.1     # 核心正确性波次 1
v0.6.0-zhcn.fix-core.2     # 核心波次 2
v0.6.0-zhcn.fix-scale.1    # 稳定性/性能波次 1
repro-core-20260722        # 复现快照（可选 annotated）
```

打 tag：

```bash
git checkout main
git pull origin main
git tag -a v0.6.0-zhcn.fix-core.1 -m "Core correctness: #2853 #3016 ..."
git push origin v0.6.0-zhcn.fix-core.1
```

在 [CHANGELOG.md](../../CHANGELOG.md) 增加对应小节。

---

## 5. PR 模板（建议标题）

```
fix(runner): do not cache failed workspace projection (#3016)
```

Body 最少包含：

1. **功能目标**（修完用户能怎样）  
2. **方案** A/B/C 选了哪条  
3. **测试** 命令与结果  
4. **风险 / 回滚**（revert commit 或回退上一 tag）  
5. **上游** 是否计划贡献

---

## 6. 远程约定

```bash
git remote -v
# origin    https://github.com/professoryu06/omnigent-zh-cn.git
# upstream  https://github.com/omnigent-ai/omnigent.git   # 需 git remote add
```

同步上游（人工，不自动 merge）：

```bash
git remote add upstream https://github.com/omnigent-ai/omnigent.git  # once
git fetch upstream
git checkout -b upstream/sync-$(date +%Y%m%d) main
git merge upstream/main   # 或 cherry-pick；解决冲突时保留 zh-cn 边界
# 见 UPSTREAM.md
```

---

## 7. 与「分析报告」的关系

- 分析报告：筛选 *哪些 issue 值得跟*  
- `docs/fixes/*`：*怎么修、怎么版本化*  
- 代码分支：*真正改功能*  
- tag：*可安装/可回滚的发布点*

三者分离，禁止在分析文档里直接贴大段未审查补丁当正式修复。
