# 全流程与阶段交接

## 竞赛工作区

所有相对路径均相对于用户竞赛工作区，不是 Skill 包目录。

```text
input/                              题面与官方附件，只读
data/                               清洗和派生数据
plan.md                             startup lock、阶段计划、授权
todo.md                             任务 DAG 与状态
data_profile.md                     附件剖析
reports/analysis_modeling_P<i>.md   各子问题建模件
code/                               可运行源程序
results/                            结果与 run-log.md
figures/                            数据图、.drawio 初稿、概念图占位
figure_registry.md                  图表登记
ai_usage_log.md                     AI 使用日志
evidence/ledger.md                  证据账本
reviews/                            分步和最终评审
paper/                              DOCX、PDF 与交付素材
```

`input/` 只允许读取。清洗、修复或格式转换必须另存 `data/`，并在运行记录中写明上游文件和变换。

## 宿主执行模式

每个竞赛工作区只使用一个宿主。startup lock 前完成能力探测，并在 `plan.md` 记录：

```text
host: codex | claude-code | other
subagent_capability: available | unavailable
agent_mode: isolated_subagents | sequential_fallback
context_mode: clean_thread | shared_context
reviewer_guard: read_only_enforced | instruction_only
```

宿主版本提供独立 agent thread 时记录 `subagent_capability: available`，并在最小上下文派发、
只读 reviewer 和三席并发门禁均满足后使用 `isolated_subagents`。各角色只收到契约与声明
输入；最终 reviewer 只返回消息，hub 等三席全部结束后再写评审文件。角色未部署、功能被
配置禁用、限权未生效或并发不足时必须 `blocked`，不得降级。只有确认宿主版本本身没有
subagent 功能时才使用 `sequential_fallback`，写
`fallback_reason: subagent_unavailable` 并披露评审独立性受限。

## 状态

任务状态只使用：

- `pending`：前置条件未满足；
- `ready`：可派发；
- `in_progress`：角色正在执行；
- `review`：等待独立评审；
- `rework`：评审不通过；
- `frozen`：评审通过且证据已登记；
- `blocked`：缺少输入、权限、规则或连续两轮返工失败；
- `superseded`：被新版本替代，保留追溯。

不得把 `draft`、`大致完成` 或 `基本通过` 当作门禁状态。

## 阶段门禁

| 阶段 | 最小输入 | 必须输出 | 放行条件 |
|---|---|---|---|
| 环境 | Skill 包、竞赛工作区 | `env_report.md`、`env_report.json` | Tier 0 全部 `OK` |
| 读题 | 完整题面、附件、当届规则 | startup lock、`data_profile.md`（有数据时） | 题号、子问题、交付物和规则已锁定 |
| 建模 | 读题件、路线确认 | `reports/analysis_modeling_P<i>.md` | 分步评审通过并登记待编码接口 |
| 编程 | 冻结建模件、输入数据 | `code/`、`results/`、run-log、车道 A 图 | 可复现、约束回代、数字登记均通过 |
| 写作 | 冻结结果与账本 | 论文正文、车道 B 初稿、车道 C 占位、DOCX 素材 | 只引用冻结证据，分步评审通过 |
| 最终 | 完整论文包 | 三席报告、返工记录、提交清单 | 隔离模式真实或降级已披露；P0 清零且官方合规项闭合 |

## 交接

每次交接必须包含任务契约、实际产物路径、逐条验收结果、未解决风险、证据 id 和允许的下一角色。下游不得自行猜测上游公式、单位、字段、随机种子或结果口径。

## Stop and report

阻塞时输出：

```markdown
## BLOCKED

- 阻塞点：
- 已确认事实：
- 缺失证据或权限：
- 已尝试动作：
- 不继续的原因：
- 用户可选择：
  1. ...
  2. ...
```

只列会实质改变下一步的选项。不得为维持流程而虚构缺失值。

## AI 使用日志

在拆解、路线选择、角色产出、评审和返工后向 `ai_usage_log.md` 追加：

```markdown
| 时间 | 环节 | 工具与版本 | 使用目的 | 关键交互摘要 | 产出路径 | 人工采纳/修改 |
```

记录重要提示与回复要点，不记录密钥或无关私人信息。联网检索另记查询目的、来源 URL 和是否涉及当届赛题；当届赛题解答或讨论一律禁止访问。
