# CUMCM 竞赛工作流

本模板供 Claude Code 主 agent 执行 `$cumcm-hub` 的八步流程。它只说明原生 subagent 的派发顺序，不替代 Skill 规则、任务契约、人工确认点或评审门禁。

## 启动方式

向主 agent 提供竞赛工作区路径，并要求：

> 加载 `$cumcm-hub`，以当前目录作为竞赛工作区，按 `.claude/workflows/cumcm-contest.md` 执行。先做环境自检和 startup lock；任何信息缺失按 stop-and-report 停下。

主 agent 始终拥有计划、状态、派发和冻结权。subagent 每次只收到一个任务契约和声明输入；不要把整段主会话当作隐式输入。

## 八步

### 1. 环境自检

加载 `$cumcm-env-doctor`。先建立/确认 uv 环境并生成 `env_report.md` 与 `env_report.json`；只让 Tier 0 缺失阻塞，Tier 1/2 记按需安装或降级。

### 2. Startup lock

主 agent 锁定题号、子问题、输入附件、交付物和当届/赛区约束，写入竞赛工作区 `plan.md`。任何未知项保持 `unknown` 并停下提问，不凭记忆补赛制数字。

### 3. 读题、数据剖析与分型

主 agent 亲自读取 `input/`。有附件时用 `cumcm-coding/scripts/profile_data.py` 生成 `data_profile.md`；按 `$cumcm-hub` 的分型规则判定评价、优化、预测、机理或综合。

### 4. 拆解

主 agent 把子问题拆成任务 DAG，维护 `plan.md`、`todo.md`、证据账本和图表登记。每个节点声明依赖、角色、输出和验收。

### 5. 模型路线确认

每个子问题给出 2–3 条候选路线、权衡和推荐，等待用户确认。只有用户明确选择“全权委托”才可代选；这不取消后续评审门禁。

### 6. 契约派发循环

对每个 `ready` 任务：

1. 主 agent 按 task-contract 创建一个契约；
2. `role=modeler` 派给 `cumcm-modeler`；
3. `role=coder` 派给 `cumcm-coder`；
4. `role=writer` 派给 `cumcm-writer`；B/C 图由 writer 加载 `$cumcm-diagram`；
5. 收到 `Task feedback` 后，另起独立 `cumcm-reviewer` 做分步评审；
6. 通过才由主 agent登记证据并冻结；不通过附评审意见返工。

同一任务最多返工 2 轮；第二轮仍不过，标记 `blocked` 并交用户决策。评审者只评不改。

### 7. 阶段推进与返工传播

严格按“全部建模 → 全部编程与车道 A 图 → 论文与车道 B/C 图”推进。上游 frozen 工件被 supersede 时，主 agent 将受影响的下游 todo 重置并重新评审，不允许局部改数后继续。

### 8. 最终评审与提交门禁

writer 完成集中文风 pass 后，主 agent 先冻结同一份 artifact manifest，再同时启动 3 个
彼此隔离且只读的 `cumcm-reviewer` 实例。每席只收到本席 brief、最终工件和 manifest，
只在返回消息中给出报告。hub 等三席全部返回后才落盘并汇总中位数、P0 并集和争议项；
汇总写 `review_mode: isolated_subagents`。

最终返工最多 2 轮；P0 未清零不得交付。提交前按最新 `cumcm-profile.md` 核对摘要、正文、匿名、页数、文件大小、附录源程序、支撑材料和 AI 披露三件套。

## 无隔离子代理环境降级

仅当能力探测确认宿主版本本身不提供独立 subagent thread 时，同一 agent 才按契约顺序切换
`$cumcm-modeling`、`$cumcm-coding`、`$cumcm-writing` 和 `$cumcm-review` 角色。宿主支持
subagent 但角色未部署、功能被配置禁用、限权未生效或并发不足时必须 `blocked`，不得降级。
所有降级评审显著标注 `self-review, 独立性受限`，不得把 A/B/C 顺序复评称为三席盲评；
汇总写 `review_mode: sequential_fallback` 与 `fallback_reason: subagent_unavailable`，
后续可在任一支持隔离子代理的宿主中复核。

## 每次派发最小消息

```markdown
- task_id:
- role:
- contract_path:
- declared_inputs:
- expected_outputs:
- acceptance:
- rework_round:
- reviewer_brief: step | final-seat-A | final-seat-B | final-seat-C
```

不得在派发消息中塞入未登记数字、其他评审席意见或未声明的网络材料。
