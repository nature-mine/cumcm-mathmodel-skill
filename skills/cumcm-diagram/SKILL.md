---
name: cumcm-diagram
description: "路由 CUMCM 论文中的数据图、精确结构图与概念图，并维护初稿、提示词和占位登记。规划或生成非数据图时使用。"
---

# CUMCM 图示

为 writer 判断图表车道，并交付可追溯的结构图初稿或概念图占位。先读取 [非数据图规则](references/diagram-rules.md) 与 [图表登记表](references/figure-registry.md)。

## 三车道路由

先问“这张图是证据、结构，还是概念画面”：

| 车道 | 判定 | 负责角色 | 产物 | 状态 |
|---|---|---|---|---|
| A 数据图 | 坐标、长度、颜色或面积编码真实数据/结果 | coder | 生成脚本 + PNG，宜另存 SVG/PDF | `done` |
| B 精确结构图 | 节点、层级、连接、分支和标签必须准确可编辑 | writer + 本 Skill | `.drawio` 源文件 + 可选导出初稿 | `draft` |
| C 概念图 | 机制、场景或图形摘要以画面表达，不承载定量证据 | writer + 本 Skill | prompt/payload + 带标注占位 | `placeholder` |

混合需求先拆图。含真实数据的面板归 A；结构关系归 B；只有真正画面式、允许人工重绘的部分才归 C。

**铁律：技术路线图、求解流程、模型结构、数据处理流程、指标体系等精确结构图永远走车道 B，绝不用文生图。**

## 车道 A：退回 coder

如果图依赖真实结果、坐标轴或统计量：

1. 不在本 Skill 重算或重画；
2. 返回所需 claim、数据字段、章节和图型建议；
3. 由 coder 按 `cumcm-coding/references/figure-rules.md` 生成并登记。

## 车道 B：生成可编辑初稿

1. 从冻结建模件、结果和论文结构提取真实节点、关系、输入与输出。
2. 写入 `figures/<figure_id>.drawio`；一个文件只表达一个主结论。
3. XML 中使用唯一 id、清晰层级、短标签、统一样式和显式几何位置。
4. 若 `drawio`、`draw.io` 或 `draw.io.exe` CLI 可用，导出 PNG 初稿；否则保留 `.drawio` 并记录人工导出方法。
5. 可用 Graphviz `dot` 生成 SVG/PNG 作为结构预览降级，但不得用 DOT 文件替代必须交付的 `.drawio` 源。
6. 检查 XML 可解析、节点完整、边端点存在、标签无歧义、无明显重叠或交叉。

即使已成功导出，车道 B 在用户人工定稿前仍为 `draft`。

## 车道 C：生成 prompt 与占位

运行 `scripts/schematic_prompt.py`，显式提供 figure id、标题、章节、目的、画面元素、关系和排除项。脚本只写：

- `figures/<figure_id>_prompt.json`：可复现的中立 payload；
- `figures/<figure_id>_placeholder.md`：供论文/DOCX 预留的带标注槽位。

默认不调用任何图像 API，不读取密钥，不生成图片。概念图不得包含虚构数字、数据曲线、机构标识、未证实机制或长文字标签；用户后续生成和重绘后再单独审查。

## 登记与交接

每张图在工作区根 `figure_registry.md` 登记稳定 id、车道、类型、状态、claim、来源、产生方式、章节、路径、provenance 和 review：

- A：脚本 + 结果 + run-log；
- B：`.drawio` + 可选导出初稿；
- C：prompt/payload + 占位文件。

状态和路径必须与 `evidence/ledger.md` 交叉一致。B/C 不得登记为 frozen 证据，不得支持量化结论。

## 反馈契约

按 writer 契约逐条返回图型判定、实际产物、CLI/降级状态、自检结果和待登记行。精确结构无法从冻结材料确定、概念图可能被误解为数据证据、或输出路径不安全时返回 `blocked`。
