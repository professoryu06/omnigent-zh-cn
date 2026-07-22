# 复现与验收脚本

在合入 `fix/core-*` / `fix/scale-*` 前，用本目录用例证明 **坏了** 与 **修好**。

## 约定

| 文件/目录 | 用途 |
|-----------|------|
| `matrix-core.md` | 核心 7 项手测/半自动清单 |
| `matrix-scale.md` | 次重要 5 项清单 |
| `fixtures/` | 最小 agent YAML（后续补） |
| `run-core-smoke.ps1` | Windows 烟测入口（后续补） |

## 版本钉扎

```bash
# 记录复现时的 commit
git rev-parse HEAD
omnigent --version   # 或 omnigent-zh --version
```

结果写入 `docs/fixes/STATUS.md` 或 PR body。

## 当前状态

方案文档阶段：矩阵清单已写，自动化脚本随第一个 `fix/core-*` 分支补齐。
