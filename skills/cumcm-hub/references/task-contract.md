# 任务契约

开题时建议先按全部小问建立“小问—输入—输出—评价标准”矩阵，再拆成任务契约。综合题通常在此基础上扩展为“小问—变量—目标—约束—输出”矩阵，显式区分子模型接口和交付物后再决定模型路线；建议每个小问都有正文中的独立可核验输出，不只在摘要或结论中出现。

## 契约格式

每个 todo 项独立使用一个 Markdown 块：

```markdown
### TASK-<阶段>-<序号>

- task_id:
- subquestion:
- objective:
- variables:
- role: modeler | coder | writer
- inputs:
  - path:
    purpose:
    status: frozen | source
- expected_outputs:
  - path:
    format:
    content:
- acceptance:
  - [ ] 可机械或人工明确判定的条件
  - [ ] 需登记的证据 id、运行记录或图表项
- constraints:
  - 当届规则、命名、单位、禁止事项
- dependencies:
  - task_id:
    required_status: frozen
- review_mode: step
- rework_round: 0
```

`inputs` 和 `expected_outputs` 必须使用竞赛工作区相对路径。禁止使用 `../`、绝对路径、模糊目录或未声明的网络输入。

## 角色边界

- `modeler`：假设、符号、机制、公式、算法、验证方案和编码接口。
- `coder`：数据处理、计算、约束回代、运行记录、结果文件和车道 A 图。
- `writer`：只基于冻结证据写作；车道 B/C 图任务由 writer 加载 `cumcm-diagram`。
- reviewer 不作为生产角色写入 `role`；由 hub 在产出后独立派发，且只评不改。

## 验收条款

每条验收条件必须给出对象与判定方式，例如：

- `results/P1_metrics.csv` 存在，列名和单位与建模件约定一致；
- `results/run-log.md` 记录命令、输入、参数、随机种子和退出状态；
- 所有可行性约束逐条回代，无未解释违反；
- 产出的数字在 `evidence/ledger.md` 有唯一 id；
- 失败路径返回非零状态并保留原因。

“结果合理”“图表美观”“论文完整”不可单独作为验收条款。

## 角色反馈

角色返回：

```markdown
## Task feedback

- task_id:
- verdict: ready_for_review | blocked
- outputs:
- acceptance:
  - 条款 1：PASS/FAIL；证据：
- evidence_to_register:
- assumptions_added:
- unresolved:
- commands_run:
```

`verdict=ready_for_review` 只表示可送审，不表示已冻结。任何失败项或未声明假设都必须返回 hub。

## 返工

评审不通过时，hub 保留原契约，追加评审记录路径、最小修复和 `rework_round + 1`。不得用改写契约删除失败条款。第二轮仍失败则标记 `blocked` 并交用户决策。
