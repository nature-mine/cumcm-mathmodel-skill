---
name: cumcm-hub
description: "编排 CUMCM 国赛端到端工作流、任务契约、阶段验收与返工闭环。用户要求启动、继续或统筹 CUMCM 建模竞赛项目时使用。"
---

# CUMCM 主控

以文件为状态源，按“主 agent 发契约 → 角色执行 → 独立评审 → 主 agent 验收”的循环推进。不得把对话记忆当作唯一状态，不得宣传或执行“全自动出赛论文”。

## 启动必读

1. 读取 [赛制参数](references/cumcm-profile.md)，并以当届官网与赛区通知复核。
2. 读取 [全流程与阶段交接](references/workflow.md)，确认竞赛工作区结构和当前阶段。
3. 首先调用 `cumcm-env-doctor`；只有 Tier 0 全部为 `OK` 才允许进入正式分析。
4. 建任务前读取 [任务契约](references/task-contract.md)；选路线时读取 [问题分型](references/problem-typing.md)；冻结结果前读取 [证据账本](references/evidence-ledger.md)。

## 八步主流程

### 1. 环境自检

调用 `cumcm-env-doctor` 建立或检查 uv 环境，读取 `env_report.md` 与 `env_report.json`。

- Tier 0 有 `MISS`：状态写为 `blocked`，只给最小安装命令，不继续正式分析。
- Tier 1 缺失：记录为按题型安装项，路线确认后再安装。
- Tier 2 或联网通路缺失：记录降级方式，不阻塞。
- 不自动修改宿主 MCP 配置，不静默安装系统工具。

### 2. Startup lock

在读取题面、附件和当届规则后，把下列问题一次性列给用户；信息不全时执行 `stop_and_report`，不得猜测：

```markdown
## Startup lock

1. 本次竞赛是否为 CUMCM？选择哪一道题（A/B/C/D）？
2. `input/` 中哪份是题面、哪份是官方附件？是否还有缺失文件？
3. 题面要求回答哪些子问题？每问的显式交付物是什么？
4. 最终需要哪些文件（DOCX、提交用 PDF、支撑材料 ZIP/RAR）？
5. 使用哪一版官方规则与赛区补充规则？页数、大小、匿名和截止时间是否已锁定？
6. 模型路线采用“逐问确认”，还是用户显式选择“全权委托”？
```

用户回答后，把题号、子问题、交付物、输入源、规则来源、路线确认方式和未知项写入竞赛工作区 `plan.md` 顶部。任何未知硬约束保留为 `unknown -> blocked`，不得用默认值掩盖。

### 3. 读题、数据剖析与分型

- 主 agent 亲自读取题面和附件；`input/` 只读，清洗或修复数据另存 `data/`。
- 有表格附件时调用 `cumcm-coding/scripts/profile_data.py` 生成 `data_profile.md`。
- 按 [问题分型](references/problem-typing.md) 标注评价、优化、预测、机理或综合类型。
- 区分题面事实、数据事实、外部来源与建模假设；无法验证的内容不得写成事实。

### 4. 拆解

建立子问题依赖 DAG，更新 `plan.md` 和 `todo.md`。每个节点必须有输入、输出、前置条件、角色、验收条款和证据登记要求；没有可判定验收条件的节点不得派发。

### 5. 模型路线确认

对每个子问题给出 2–3 条候选路线，逐条说明：

- 与题意和数据的匹配；
- 关键变量、目标、约束或评价指标；
- 实现成本、验证负担、失败风险；
- 推荐路线及拒绝其他路线的理由。

呈现协议：候选以编号列表逐问呈现，推荐路线排第一并标注“（推荐）”。宿主提供结构化提问工具
（如 Claude Code 的 AskUserQuestion）时用它呈现同一组选项，用户的选择即作为该问的路线签认
记录；没有对等工具时以编号列表等待用户回复编号。

用户可以指定候选之外的路线。此时 hub 按上述同一比较框架对该路线给出匹配、成本与风险评估后
照办，不得以“不在候选中”为由拒绝或擅自改回推荐路线；评估结论与分歧一并写入 `plan.md`。每问
确认后在 `plan.md` 记录 `route_source: candidate | user_defined` 与所选路线。

用户确认后才进入建模。只有用户明确选择“全权委托”时可跳过逐问确认，并把该授权写入 `plan.md`。

### 6. 契约派发循环

按 [任务契约](references/task-contract.md) 逐项派发：

1. 主 agent 写契约；
2. 对应角色逐条完成并自报验收；
3. 主 agent 调 `cumcm-review` 做分步评审；
4. 通过后登记 [证据账本](references/evidence-ledger.md) 并冻结；
5. 未通过时附原评审意见返工。

每个任务最多返工 2 轮。仍不通过时停止该分支，报告失败证据、已尝试修复和需要用户选择的分歧，不得软化为“基本通过”。

### 7. 阶段推进与返工传播

固定顺序为建模 → 编程与数据图 → 论文与非数据图。下游只消费已验收工件。冻结的上游工件发生 supersession 时：

- 标记旧证据已替代；
- 找出所有依赖的代码、结果、图、表、正文与摘要；
- 将受影响 todo 重置为待验证；
- 完成一致性复审后才重新冻结。

### 8. 最终评审与提交门禁

写作角色先执行文风集中检查，且不得改动冻结数字。宿主支持隔离子代理时必须同时派发三个
独立 reviewer agent thread；不允许为了省事改成主 agent 顺序自评。只有能力探测确认当前
宿主本身不提供隔离子代理时，才退化为同上下文 A/B/C 三轮角色复评，并在报告显著注明
独立性受限。宿主有该能力但角色未部署、功能被配置禁用、限权未生效或并发不足时必须
`blocked`，修正配置后重试，不得顺序降级。

Hub 汇总时取各维度中位数、P0 并集，席间任一维度分差达到 15 分则标记争议并交用户复核。最终评审最多返工 2 轮，P0 未清零不得提交。提交前逐项核对：

- 当届正文页数、摘要页、页码、文件格式和大小；
- 全文、附录和支撑材料匿名；
- 附录含支撑材料清单与完整可运行源程序；
- 论文数字、图表、代码、运行记录与证据账本一致；
- AI 正文标注、工具参考条目和“AI 工具使用详情”齐全；
- 无目录，电子版不含承诺书与编号页；
- 联网日志中不存在当届赛题解答、解析或讨论来源。

## 双宿主兼容与能力分派

一个竞赛工作区只选择一个宿主：Codex 或 Claude Code。不得同时部署两套角色定义、在流程中途
换宿主，或把一套宿主的 agent 文件交给另一套宿主解释。

启动时先做能力探测，并把以下字段写入 `plan.md`：

```text
host: codex | claude-code | other
subagent_capability: available | unavailable
agent_mode: isolated_subagents | sequential_fallback
context_mode: clean_thread | shared_context
reviewer_guard: read_only_enforced | instruction_only
```

先判断宿主版本本身是否提供独立 subagent thread。只有明确不提供时才记录
`subagent_capability: unavailable` 并进入顺序兜底；未知状态不得猜成 unavailable。
宿主能力为 `available` 时，必须同时满足以下运行门禁，才开始派发：

1. 能按名称派发 modeler、coder、writer、reviewer 到彼此独立的 agent thread；
2. 新 thread 可只接收任务契约与声明输入，不把整段主会话作为隐式业务输入；
3. reviewer 可被机械限制为只读，且不能自行提升权限；
4. 最终模式可同时运行 3 个 reviewer thread，并在三席全部返回前不向任何席位暴露同席输出。

任一运行门禁因角色文件缺失、功能开关、权限覆盖或并发配置失败时写 `blocked`，给出修复项
后停止；不得把宿主配置错误伪装成“无子代理环境”。门禁满足时记录
`subagent_capability: available` 与 `agent_mode: isolated_subagents`，并使用原生隔离派发：

- Codex：部署 `.codex/agents/*.toml` 后使用 `cumcm-modeler`、`cumcm-coder`、
  `cumcm-writer`、`cumcm-reviewer`。派发时使用空或最小父上下文；当前工具支持时用
  `fork_turns="none"` 或等价选项。Codex agent thread 共享工作区，不等于文件系统隔离。
- Claude Code：部署 `.claude/agents/*.md` 后使用同名四角色；reviewer 的工具面只保留
  `Read/Grep/Glob`。
- 两种宿主都必须只发送 `task_id`、契约路径、声明输入和预期输出。生产角色完成后另起
  reviewer，不让生产角色自评。

最终三席盲评前，hub 先冻结同一份 artifact manifest 和 A/B/C 三份席位 brief，再同时派发
三个只读 `cumcm-reviewer`。reviewer 只在返回消息中给出报告；hub 等三席全部结束后才统一
写入席位报告与汇总，防止共享工作区泄漏先返回席位的意见。汇总必须写明
`review_mode: isolated_subagents`。

只有明确确认宿主版本本身没有 subagent 功能时才使用 `sequential_fallback`：记录
`subagent_capability: unavailable`，同一 agent 按契约顺序切换角色，所有评审写
`self-review, 独立性受限`，最终 A/B/C 顺序执行三轮，汇总写
`review_mode: sequential_fallback` 与 `fallback_reason: subagent_unavailable`，并把隔离复核
列为提交前剩余风险。
宿主差异只能改变执行方式，不能改变契约字段、门禁、返工预算或证据标准。

## 通用阻塞条件

出现下列任一情况立即停止并报告：输入或题号不明、官方规则未锁定、Tier 0 缺失、模型路线未确认且无授权、契约缺字段、代码结果无运行记录、论文引用非冻结数字、参考文献未经核验、匿名或 AI 披露风险未清除。
