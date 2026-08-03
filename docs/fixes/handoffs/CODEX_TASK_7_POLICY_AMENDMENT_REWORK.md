# CODEX TASK 7 POLICY AMENDMENT REWORK — 修复 Gate 1 表格结构

**执行者：** Hermes（政策文档返工执行者）  
**日期：** 2026-07-29  
**源工作树：** `F:\codex-ai\git项目部署\tmp\omnigent-review`  
**当前状态：** 九条政策内容完整，但Markdown Pass/Fail表被新增正文截断；政策落地验收不通过。Gate 1仍待判定；Gate 2未执行、未判定；不可 merge。  
**阶段边界：** 只移动`PRE_MERGE_GATES.md`中的两条原有表格行，恢复表格连续性。不得改变九条安全条件、批准记录或任何政策语义；不得运行测试。

## 1. 问题

当前`docs/fixes/PRE_MERGE_GATES.md` §1.2顺序为：

1. 表头；
2. 绝对全绿行；
3. 相对main行；
4. 空行，表格在此结束；
5. `#### 相对 PASS 安全条件`及正文；
6. 政策修订记录；
7. `集成树出现 main 没有的失败`行；
8. `仅 Windows 定向 67 绿`行。

因此最后两行已不属于Markdown表格，只会作为孤立的pipe文本渲染，破坏Pass/Fail规则结构。

这不是政策内容问题，不允许借返工改写规则。

## 2. 精确文件

只允许：

- 修改：`docs/fixes/PRE_MERGE_GATES.md`
- 新建：`docs/fixes/handoffs/HERMES_COMPLETION_7_POLICY_AMENDMENT_REWORK.md`

不得修改STATUS、POST_FIX、旧handoff、源码/tests/config/lockfile/CI或r2–r6 evidence。

## 3. 唯一改法

把以下两条现有行：

```markdown
| 集成树出现 main **没有**的失败或 error | **Gate 1 FAIL** — 阻塞 merge |
| 仅 Windows 定向 67 绿 | **不足** — Gate 1 未满足 |
```

从政策修订记录之后移动到相对main表格行之后、`#### 相对 PASS 安全条件`之前。

最终必须精确呈现以下结构：

```markdown
| 结果 | 判定 |
|------|------|
| 集成树 `pytest -q` **绝对全绿**（0 failed, 0 errors） | **Gate 1 PASS（绝对全绿）** |
| clean main **已有**失败，且候选树失败 nodeid **⊆** main 失败集（同环境、同依赖、同隔离状态） | **Gate 1 PASS（相对 main 无新增失败）** — 必须同时满足下列"相对 PASS 安全条件"；任一缺失均不得 PASS |
| 集成树出现 main **没有**的失败或 error | **Gate 1 FAIL** — 阻塞 merge |
| 仅 Windows 定向 67 绿 | **不足** — Gate 1 未满足 |

#### 相对 PASS 安全条件
```

九条安全条件及政策修订记录必须保持逐字不变。不得调整编号、分类名、归一化规则、显式批准要求或免责声明。

## 4. 文档验证

不得运行pytest/Ruff/Gate。只运行：

```powershell
git diff --check -- docs/fixes/PRE_MERGE_GATES.md

$p = 'docs/fixes/PRE_MERGE_GATES.md'
$lines = Get-Content -LiteralPath $p -Encoding UTF8
$idxHeader = [Array]::IndexOf($lines, '| 结果 | 判定 |')
$idxAbsolute = [Array]::IndexOf($lines, '| 集成树 `pytest -q` **绝对全绿**（0 failed, 0 errors） | **Gate 1 PASS（绝对全绿）** |')
$idxRelative = ($lines | Select-String -SimpleMatch '| clean main **已有**失败').LineNumber - 1
$idxFail = ($lines | Select-String -SimpleMatch '| 集成树出现 main **没有**的失败或 error').LineNumber - 1
$idxWindows = ($lines | Select-String -SimpleMatch '| 仅 Windows 定向 67 绿').LineNumber - 1
$idxSafety = [Array]::IndexOf($lines, '#### 相对 PASS 安全条件')

if (-not ($idxHeader -ge 0 -and
          $idxAbsolute -eq $idxHeader + 2 -and
          $idxRelative -eq $idxAbsolute + 1 -and
          $idxFail -eq $idxRelative + 1 -and
          $idxWindows -eq $idxFail + 1 -and
          $idxSafety -eq $idxWindows + 2)) {
    throw 'Gate 1 markdown table structure invalid'
}
'GATE1_TABLE_STRUCTURE_OK'

rg -n "documented_main_code_failure|归一化语义指纹|candidate-only|显式.*批准|不等于全仓.*GREEN|Gate 2|可merge" `
  docs/fixes/PRE_MERGE_GATES.md
```

还必须用编辑前后SHA-256确认：

- 九条安全条件正文完全相同；
- 政策修订记录完全相同；
- STATUS、POST_FIX和全部旧handoff未变；
- HEAD与四保护blob未变。

## 5. 禁止项

- 不得改写、压缩、增删九条安全条件或批准记录。
- 不得修改STATUS、POST_FIX、旧handoff、源码/tests/config/lockfile/CI/evidence。
- 不得把Gate 1写成PASS；本轮仅修复文档结构。
- 不得运行pytest、Ruff、Gate 1、Gate 2、AgentCenter、浏览器E2E或真实CLI smoke。
- 不得启动/终止WSL进程或清理tmux/host/server。
- 不得stage/commit/push/merge/tag、发版或编辑PR/Issue。
- 不得宣称Gate 2 PASS或可merge。

## 6. 完成报告与标准

`HERMES_COMPLETION_7_POLICY_AMENDMENT_REWORK.md`必须记录：

1. 仅移动两条表格行，无文字变化。
2. `GATE1_TABLE_STRUCTURE_OK`与`git diff --check`真实输出/exit。
3. 九条安全条件、批准记录、STATUS、POST_FIX、旧handoff的前后SHA-256一致。
4. HEAD与四保护blob一致。
5. 未运行任何测试/Gate，未修改其他文件。
6. Gate 1仍待Codex只读验收；Gate 2未执行、未判定；不可merge。
7. 无commit/push/merge/tag。
