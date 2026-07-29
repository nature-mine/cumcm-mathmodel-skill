<!--
Adapted from repository: https://github.com/ZyhSechub/chinese-thesis-workbench-skill
Upstream license: MIT
Upstream copyright: Copyright (c) 2026 Zyhsec
Referenced upstream path:
- references/delivery/final-delivery-check.md

This file adapts selected final-delivery checks to the CUMCM review and
rework protocol.

MIT License

Copyright (c) 2026 Zyhsec

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
-->

# 分步评审检查单

每次只选一种工件检查单，并同时覆盖“数学核验 / 跨材料一致性 / 官方合规”。`不适用` 必须写理由；`无法验证` 不能视为通过。

## 目录

- [通用输入与输出](#通用输入与输出)
- [建模件](#建模件)
- [代码件](#代码件)
- [论文件](#论文件)
- [返工复审](#返工复审)
- [送回 hub](#送回-hub)

## 通用输入与输出

输入清单：

- `task_id` 与任务契约；
- 待审工件路径；
- 声明的输入、上游 frozen 工件和结果；
- evidence ledger、run-log、figure registry、当届 profile 中与本任务有关的部分。

每条问题写：

```text
[P0|P1|P2] 文件:章节/公式/行/figure_id
事实：
影响：
证据：
最小返工方向：
```

分步结论：

- `通过`：acceptance 全部有证据，无 P0/P1；
- `返工`：任一 acceptance 失败、存在 P0/P1，或关键项无法验证。

## 建模件

### 数学核验

- [ ] 子问题目标、决策对象、输入、输出和题面逐项一致。
- [ ] 题面事实、数据观察、假设和推论分开，没有框架锁死。
- [ ] 假设有编号、依据、范围、失效影响和验证；使用处回指。
- [ ] 符号唯一，类型、维度、单位、取值域和来源完整。
- [ ] 公式量纲、边界、初始条件和参数来源一致。
- [ ] 评价指标方向/权重、优化约束、预测划分、图算法前提或机理守恒按题型检查。
- [ ] 候选路线、基线和推荐权衡结合题意、数据、约束及可验证性，不把方法名当推导。
- [ ] 主模型的关键验证按建议说明对象、基准来源、评价指标、量化结果、结论影响及失效条件。
- [ ] 按场景建议组合验证：预测检查回测、留出或简单基线，优化检查约束与方案对照，机理检查量纲、极限和收敛，路径检查坐标反代、碰撞与回放，随机风险检查分布、尾部与最坏情形，信号反演检查已知样本、重建误差与噪声扰动。
- [ ] 求解说明按建议交代输入、输出、参数、初值、终止条件、软件，以及一次收敛或稳定性检查。
- [ ] 使用置换负对照时默认不少于 1000 次并披露实际次数；降低次数必须说明依据与精度影响。
- [ ] 样本筛选、缺失剔除和不同统计量的分母逐项写明；同一材料出现不同样本量时可追溯差异。
- [ ] 灵敏度结论有实际结果文件支撑且不超出已运行场景；小样本经验高分位阈值披露不稳定性或给出扰动结果。
- [ ] 创新点说明真实增量、适用范围和验证，不强行包装。

框架锁死检查：

- 原始题面是否仍允许另一种实质解释？
- 拆解期的一处误读是否被假设、公式和接口层层固化？
- 是否因为已有算法而反向删改题意或交付物？

### 跨材料一致性

- [ ] 与 startup lock、路线确认和任务 DAG 一致。
- [ ] `data_profile.md` 的样本、字段和缺失事实没有被误写。
- [ ] 编程接口固定输入字段、单位、参数、随机性、输出口径、精度与失败路径。
- [ ] 多模型链按建议显式声明接口变量，上一模型输出在下一模型中按一致单位、时间尺度和索引引用，误差传播有说明。
- [ ] 车道 A 图需求明确 claim 和数据来源。
- [ ] 引用需求只占位，没有凭记忆生成文献条目。

### 官方合规

- [ ] 未引入当届禁止的外部解答、交流或网络材料。
- [ ] 未出现身份信息、密钥或未授权数据。
- [ ] AI 参与已进入 `ai_usage_log.md`。

建模件常见 P0：题意/公式/量纲/硬约束错误、关键参数虚构。主模型没有灵敏度或稳健性分析通常记 P1。

## 代码件

### 数学与实现核验

- [ ] 代码逐式对应冻结建模件，没有悄悄改模型或单位。
- [ ] 输入验证、边界、缺失、异常和失败路径有测试。
- [ ] 所有随机过程固定种子并写入 run-log。
- [ ] 优化解逐条回代硬约束；预测流程无时间/实体/预处理泄漏。
- [ ] 基线、灵敏度、稳健性、消融或边界实验按契约运行。
- [ ] 失败保留非零状态与真实原因，不返回伪成功。
- [ ] 结果文件由代码产生，不存在手工改值或硬编码测例答案。

失败模式检查：

- 实现 bug 是否因为只测正常路径而骗过自审？
- 是否依赖当前样例的行数、顺序、路径或答案常量？
- 是否把求解器失败、空数据、NaN、不可行或异常输出解释成模型特性？
- 是否选择性报告最好一次运行，隐藏失败种子或不利场景？

### 跨材料一致性

- [ ] 输出列名、单位、精度和场景口径与建模接口一致。
- [ ] run-log 含命令、输入、参数、依赖、种子、退出状态和输出。
- [ ] 论文候选数字均有唯一待登记 evidence id。
- [ ] 车道 A 图绑定结果、脚本、run-log；无双 Y 轴、彩虹色、小样本均值柱等反模式。
- [ ] `figure_registry.md` 的 id、status、path 和 provenance 与文件一致。

### 官方合规

- [ ] `input/` 未被修改；派生数据写入 `data/` 并记来源变换。
- [ ] 代码完整可运行，依赖和入口可交付。
- [ ] 未提交凭据、缓存、运行日志之外的私人材料。
- [ ] AI 参与已记录。

代码件常见 P0：结果不可复现、约束违反、数据泄漏、硬编码答案、异常伪装成功、结果与论文口径不一致，或用图表反模式支撑主要结论。

## 论文件

### 数学与证据核验

- [ ] 摘要含问题、方法、每问关键量化结果和结论，并按建议在关键结果或结论中至少给出一项验证或稳健性结论。
- [ ] 每个子问题形成“机制/方法 → 结果 → 验证 → 解释 → 局限”。
- [ ] 每个子问题按建议以关键数值、单位、现实解释和一项验证收束。
- [ ] 所有量化结论只引用 `status=frozen` 的账本行。
- [ ] 公式、假设编号、符号、单位和结果口径与上游一致。
- [ ] 模型选择说明按建议结合题意、数据、约束与可验证性，不以精度或复杂度空泛代替理由。
- [ ] 建议核查误差分析、对比实验、基线、灵敏度、稳健性和不确定性是否被省略或夸大。
- [ ] 模型评价具体说明优缺点、范围和改进所需条件。

### 跨材料一致性

- [ ] 摘要中的模型、结果和验证口径与正文、表格、图注、附录及 ledger 一致。
- [ ] A 图是可复现数据图；B 为可编辑 draft；C 为显式 placeholder。
- [ ] B/C 未充当 frozen 证据，精确结构图未走文生图。
- [ ] 正文图表所在编号章节与 `figure_registry.md` 的 `chapter` 一致；B/C 的占位指令、说明和 prompt 章节也一致。
- [ ] 引用逐条有真实性核验记录，作者、题名、年份、来源、卷期、页码和 DOI 均按原始来源核实；运行 `check_references.py` 检查结构和编号。
- [ ] 附录代码由 `code/` 确定性导入，没有手抄、节选或改写。
- [ ] 支撑材料清单正确区分 `input/` 与 `data/`。
- [ ] 按建议从结论反向追溯到结果、模型和对应小问，模型验证、代码附件和复现入口均可定位。

文风检查：

- 是否大量使用“首先、其次、最后”串联而无逻辑关系；
- 是否各段均匀铺陈、空泛总结、堆砌“显著提升/全面赋能”等大词；
- 是否存在重复复述或缺少数据、图表、推导等证据支撑的判断；
- 是否把方法说明写成 agent/prompt/派发/冻结/P0/里程碑/车道/占位槽等内部流程；单行 `PLACEHOLDER` 指令作为导出控制文本豁免；
- 集中文风 pass 是否保持 frozen 数字和结论不变。

程式化 AI 文风通常为 P1/P2；内部流程语言泄漏进正文为 P0。

最终评审前运行 `scripts/validate_smoke_workspace.py`，对正文内部流程词和图表章节一致性执行机械扫描。扫描只豁免完整单行的合法 `PLACEHOLDER` 指令，不豁免正文叙述。

### 官方合规

- [ ] 使用当届已核实 profile，不沿用往届页数或大小。
- [ ] 无目录；摘要专页、正文、页码、匿名和电子文件要求闭合。
- [ ] 建议核对公式、图表及其编号是否完整、连续，正文引用与对应对象是否一致。
- [ ] 建议通过终稿渲染核对中文、西文和数字字体是否存在明显混乱。
- [ ] 终稿建议清零 `【待替换】`、待补说明、未处理批注和未接受或拒绝的修订记录。
- [ ] 终稿建议清除裸露的 `**`、反引号、Markdown 标题符和 Markdown 链接语法等排版残留。
- [ ] 合法单行 `PLACEHOLDER` 与 figure registry 中已登记的 B/C 工件按既有状态协议单独核验，不作为裸 Markdown 残留误报；提交前仍需确认未完成工件没有冒充定稿证据。
- [ ] 附录含支撑材料清单和全部完整可运行源程序。
- [ ] AI 正文标注、AI 工具参考条目和“AI 工具使用详情”三件套齐全。
- [ ] 全文及支撑材料无身份信息、密钥或禁止联网来源。

论文件常见 P0：

- 摘要缺关键量化结论；
- 非 frozen 数字或实验结果幻觉；
- 引用幻觉；
- 章节证据链缺失导致结论无依据；
- 匿名、页数、附录程序、支撑材料或 AI 披露硬性失败。

## 返工复审

- reviewer 必须重新打开返工后的工件及其证据，逐项复核原问题、受影响接口和相关 acceptance；只阅读返工摘要或变更说明不算复审。
- 返工说明、作者自报通过或勾选结果不能替代工件、账本、代码、运行记录和渲染结果中的新证据。
- 修改可能影响摘要、正文、图表、附录或下游结果时，必须重跑对应一致性与机械检查；原检查结果不得自动沿用。
- 复审报告应逐项给出当前 PASS/FAIL、定位证据和仍需返工的最小范围。

## 送回 hub

报告只给结论和返工方向。不得：

- 直接修改工件；
- 删除失败 acceptance；
- 把 P0 降成措辞建议；
- 替 hub 冻结证据或推进 todo；
- 在第二轮后继续无限返工。

hub 依据原契约创建返工；同一任务最多 2 轮，仍不过则交用户决策。
