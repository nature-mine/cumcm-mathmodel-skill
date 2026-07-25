# 图表登记表

在竞赛工作区根创建 `figure_registry.md`。每张图一行，id 稳定且不复用。

```markdown
| id | lane | type | status | claim | source | method | chapter | path | provenance | review |
|---|---|---|---|---|---|---|---|---|---|---|
```

## 字段

- `id`：`FIG-P<i>-<nn>` 或全局 `FIG-G-<nn>`。
- `lane`：只用 `A`、`B`、`C`。
- `type`：如 `line`、`heatmap`、`roadmap`、`model-structure`、`concept-scene`。
- `status`：
  - A 使用 `done`；
  - B 使用 `draft`；
  - C 使用 `placeholder`；
  - 已被替代时使用 `superseded` 并在 `provenance` 指向新 id。
- `claim`：该图允许帮助表达的最窄结论；B/C 不得写量化 claim。
- `source`：真实输入或冻结材料路径。
- `method`：A 为生成脚本，B 为 `drawio`/`dot`，C 为 `schematic_prompt.py`。
- `chapter`：拟放置章节。
- `path`：主要交付文件；其他文件写入 `provenance`。
- `provenance`：A 记结果与 run-log；B 记 `.drawio` 与导出初稿；C 记 payload 与占位。
- `review`：最近评审路径；未评审写 `pending`。

## 车道示例

```markdown
| FIG-P1-01 | A | sensitivity-line | done | 参数扰动下目标值变化 | results/P1_sensitivity.csv | code/plot_P1.py | 6.1 | figures/P1_sensitivity.png | results/run-log.md; figures/P1_sensitivity.svg | pending |
| FIG-G-01 | B | roadmap | draft | 展示三问技术路线与依赖 | reports/analysis_modeling_P1.md | drawio | 2 | figures/FIG-G-01.drawio | figures/FIG-G-01_draft.png | pending |
| FIG-G-02 | C | concept-scene | placeholder | 解释机制的概念画面，不作为证据 | reports/analysis_modeling_P2.md | schematic_prompt.py | 6.2 | figures/FIG-G-02_placeholder.md | figures/FIG-G-02_prompt.json | pending |
```

## 一致性门禁

- id、lane、status、path 必须与 `evidence/ledger.md` 的关联项一致。
- A 图没有生成脚本、结果或 run-log 时不得标记 `done`。
- B 图即使导出成功，在用户人工定稿前仍是 `draft`。
- C 图在生成、人工核实并另行登记前始终是 `placeholder`。
- B/C 可以进入论文占位，但不能成为 frozen 数字证据。
- 原图被替换时保留旧行，不删除 provenance。
