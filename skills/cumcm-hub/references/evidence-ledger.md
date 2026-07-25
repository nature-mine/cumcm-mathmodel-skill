# 证据账本与数字冻结

## 最小表结构

`evidence/ledger.md` 使用下列表格：

```markdown
| evidence_id | subquestion | claim | value_unit | result_path | code_path | run_log | figure_id | review_path | status | superseded_by |
```

- `evidence_id`：稳定唯一 id，如 `E-P1-001`，不得复用。
- `claim`：该证据允许支持的最窄结论，不写夸张解释。
- `value_unit`：关键数字与单位；非数值证据写 `n/a`。
- `result_path`、`code_path`、`run_log`：竞赛工作区相对路径，至少能回到真实结果和生成过程。
- `figure_id`：没有图写 `n/a`；有图时必须同时存在于 `figure_registry.md`。
- `review_path`：最近一次通过的分步评审。
- `status`：只用 `candidate`、`frozen`、`superseded`、`blocked`。

## 冻结门禁

只有同时满足下列条件才能标记 `frozen`：

1. 产物路径存在且位于竞赛工作区内；
2. 运行记录含命令、输入、参数、种子、退出状态和输出；
3. 数值单位、精度和场景口径明确；
4. 约束、边界或评价指标已按契约验证；
5. 分步评审结论为通过；
6. 相关图表 provenance 已登记。

Writer 只能引用 `frozen` 行。`candidate`、占位图、结构图初稿和诊断结果不得写成最终量化结论。

## 图表 provenance

- 车道 A：登记数据结果、生成脚本、run-log 和导出文件。
- 车道 B：登记 `.drawio` 源文件、导出初稿和 `draft` 状态。
- 车道 C：登记提示词/payload、占位文件和 `placeholder` 状态。

`figure_registry.md` 与账本中的 id、车道、状态和路径必须一致。

## Supersession

冻结项禁止原地改值。需要变更时：

1. 新增一个 `evidence_id`，记录新结果、代码、运行与评审；
2. 旧行改为 `superseded`，`superseded_by` 指向新 id；
3. 在旧行下记录变更原因、受影响 claim、图表和章节；
4. 将所有下游 todo 重置为待验证；
5. 完成一致性复审后，才把新行设为 `frozen`。

不得删除旧行、覆盖旧结果或复用旧 id。

## 路径与真实性

- 所有路径必须相对竞赛工作区，禁止 `../` 与绝对路径。
- 论文中的每个量化结论必须能唯一映射到账本行。
- 账本不是证据本身；文件缺失、运行失败或来源未核验时，该行必须是 `blocked`。
- 外部文献证据另记标题、作者、年份、来源 URL 与核验日期；禁止凭记忆生成条目。
