---
name: cumcm-writing
description: "依据冻结证据撰写 CUMCM 中文论文、组织附录与 AI 披露材料，并生成 DOCX 交付。执行论文契约或整理成稿时使用。"
---

# CUMCM 论文写作

依据冻结的建模、结果和证据写论文，再确定性导出 DOCX。不得在写作期重算结果、修改模型口径、补造数字或凭记忆生成参考文献。

## 前置输入

开始前读取：

1. writer 任务契约、startup lock、当届 `cumcm-profile.md`、[论文结构](references/paper-structure.md)和 [版面规则](references/layout-rules.md)；
2. 已冻结的建模件、结果、运行记录和 `evidence/ledger.md`；
3. `figure_registry.md` 与所有可用图表；
4. 已核实的文献来源和 `ai_usage_log.md`。

只允许把 `evidence/ledger.md` 中 `status=frozen` 的条目写成量化结论。车道 B 初稿和车道 C 占位可以预留版位，但不得充当证据或写成已定稿图。
从空白工作区起稿时，复制[论文 Markdown 模板](templates/paper-template.md)到
`paper/paper.md`；[可直接查看的 DOCX 模板](templates/paper-template.docx)用于确认骨架和推荐
版式，不能跳过当届规则复核后直接提交。

## 写作步骤

### 1. 建立证据到章节的映射

- 为每个子问题列出“机制/方法 → 结果 → 验证 → 解释 → 局限”的证据链。
- 每个数字、表格和车道 A 图绑定唯一 `evidence_id`。
- 发现正文所需结论未冻结、单位冲突或上下游口径不一致时返回 `blocked`，不得在写作期修算。

### 2. 先写摘要骨架

摘要按“问题—方法—关键量化结果—结论”四要素组织，并逐个回应子问题；建议在关键结果或结论中至少给出一项验证或稳健性结论。关键数字只能来自冻结证据；最终正文完成后再回填和压缩摘要。

### 3. 展开正文

- 依照论文结构组织，不添加目录。
- 假设沿用建模件编号，并在公式或推导使用处回指。
- 公式前说明目的，公式后解释变量、单位和它如何回答题目；块级可编辑公式使用版面规则中的 `[[EQUATION latex="..."]]` 指令。
- 每个结果紧邻验证和含义解释，避免只堆表格或泛泛复述。
- 单列模型评价、优缺点和改进方向；局限必须与适用范围一致。
- 正文不出现“agent、prompt、派发、冻结、P0”等内部流程词。

### 4. 补齐图示

- 数据结果图使用 coder 已登记的车道 A 图，不在写作期重画或改数。
- 技术路线、求解流程、模型结构等精确图，加载 `$cumcm-diagram` 走车道 B，产 `.drawio` 可编辑初稿。
- 机制插画、图形摘要等画面式概念图，加载 `$cumcm-diagram` 走车道 C，只产 prompt/payload 和带标注占位。
- 图号、章节、状态和路径必须与 `figure_registry.md` 一致。

### 5. 核实引用与附录

- 方法期的“引用需求”不是参考文献。联网后逐条核对标题、作者、年份、来源和 URL；禁止凭记忆补齐字段。
- 正文引用编号与文末列表一一对应，不为数量凑无关文献。
- 附录完整源程序由 `scripts/docx_export.py` 从 `code/` 确定性导入；writer 不手抄、不节选、不改写代码。
- 支撑材料清单区分 `input/` 原始赛题附件与必须提交的 `data/` 派生材料、源程序。

### 6. 执行集中文风 pass

- 读取[文风质量规则](references/style-quality.md)与[高水平参赛论文风格画像](references/award-style-profile.md)，只在正文和摘要完成、量化结果冻结后执行一轮。
- 逐段处理术语漂移、程式化连接、空泛大词、均匀铺陈和拗口节奏，不以检测器分数为目标。
- 修改前后逐项对照 frozen 数字、单位、方向性结论、限制条件、图表编号和引用编号；任一变化都必须回退。

### 7. 整理 AI 披露素材

- 按当届官方规则保留正文相应位置标注、AI 工具参考条目和“AI 工具使用详情”素材。
- 从 `ai_usage_log.md` 整理，不遗漏人工采纳/修改情况，不写密钥或无关隐私。
- AI 辅助不得被描述为替代参赛队完成核心建模与分析。

### 8. 导出并视觉自检

先按 [版面规则](references/layout-rules.md)检查图表、公式指令和 Markdown 表格，再运行：

```bash
python skills/cumcm-writing/scripts/docx_export.py \
  --workspace . \
  --source paper/paper.md \
  --output paper/cumcm-paper.docx
```

导出器自动生成页码字段、附录完整源程序和 `paper/support_manifest.json`。随后优先用 OfficeCLI 执行 validate、issues、outline 和整份 PNG 渲染，实际查看摘要分页、图表尺寸、占位槽、编号、附录代码缩进及支撑材料分类；发现问题后修改源稿或配置并完整重跑。OfficeCLI 不可用时按版面规则中的降级路径处理，不得只凭脚本退出码宣布排版通过。

## 必须产出

以任务契约为准，至少包含：

- `paper/` 下的 Markdown 论文稿；
- `paper/` 下的最终 DOCX 与 `support_manifest.json`；
- 证据到章节、表图和引用的映射；
- 车道 B 初稿与车道 C 占位需求；
- 附录代码导入清单和支撑材料清单；
- AI 披露素材与未解决风险。

完成后按 `Task feedback` 逐条反馈。`ready_for_review` 只表示可送独立评审；出现非 frozen 数字、引用未核实、占位图冒充证据、官方约束不明或 DOCX 未完成视觉自检时必须返回 `blocked`。
