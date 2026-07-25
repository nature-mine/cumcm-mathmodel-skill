<!--
Adapted from repository: https://github.com/capwitf/My-MathModeling-skills
Upstream license: MIT
Upstream copyright: Copyright (c) 2026 capwitf
Referenced upstream paths:
- math-templates/references/national-prize-style-profile.md
- math-templates/references/section-format-controls.md
- math-templates/assets/contest-project-template/paper/section_templates_national.md

This file paraphrases and generalizes writing principles. It does not reproduce
the upstream sentence templates or prescribe a fixed contest-paper structure.

MIT License

Copyright (c) 2026 capwitf

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

# 高水平参赛论文风格画像

## 定位与优先级

- 本画像描述高质量论文应呈现的信息，不是获奖承诺、评分细则、固定目录或固定句式库。
- 当届官方规则、题面交付物、startup lock、frozen 证据与可复现记录始终优先。
- “高水平”意味着题意贴合、建模洞察、证据可信、结果可复现和适用边界同时可见。
- 信息不足时降低结论强度或返回补证据，不用修辞填补缺口。

## 自适应结构

- 按题型、子问题依赖和证据负担组织章节，不绑定固定问数、章号或篇幅比例。
- 摘要优先交付答案：逐问给出方法、关键量化结果、验证结论和直接回答；所有数字都能回指 frozen 证据。
- 问题重述只把题面转换成输入、约束、目标和交付物，不复写原题或扩展装饰性背景。
- 问题分析先说明全题分解与信息流，再逐问交代数学类型、关键难点、路线理由、输出和验证安排。
- 每个子问题形成“建模—求解—结果—验证—解释—边界”的闭环，避免模型与对应结果相隔过远。
- 只有多个子问题真正共享坐标、变量、方程、判定逻辑或算法框架时才设置模型准备。
- 数据驱动题可增加影响路线选择的数据分析；优化题可把可行性验证嵌入分问；物理、几何或仿真题可集中共用基础。
- 小节只服务真实写作任务；模板中存在的标题不构成必须保留的目录。

## 信息密度

- 每段承担一个可检查任务，优先保留定义、依据、模型关系、量化结果、验证和边界。
- 假设只保留会改变模型结构、可行性或结论范围的项目，并说明依据与失效条件。
- 核心符号写明含义和单位；公式交代现实来源、变量、约束以及它回答哪个问题。
- 算法说明关键参数、终止条件和复现入口，不用步骤数量制造复杂感。
- 结果陈述包含可定位的数字、单位、场景、基准或约束回代；主观形容词不能替代证据。
- 验证优先覆盖可行性、正确性、稳定性和相对基准差异，并说明结论在哪些条件下失效。
- 模型优点应指出现实难点如何被转化为可计算结构，并挂接公式、表、图或证据条目。
- 局限说明忽略因素及其可能影响；推广说明目标场景、新约束、新数据和必须重做的验证。

## 图表与证据

- 图表必须回答问题、解释机制、展示方案差异或验证结论，不作版面装饰。
- 车道 A 数据图只承载可复现结果；车道 B 可编辑初稿和车道 C 概念图必须显式标明状态。
- 每个图件与 `figure_registry.md` 的 id、章节、车道、状态和来源一致。
- B/C 占位不得写成已完成结果；未定稿图件不能替代 frozen 数字。
- 同一结论选择最利于核查的载体，避免正文、表格和图形重复铺陈。

## 版面与语言一致性

- 标题层级、分问标签、编号、术语和单位在全文保持平行一致。
- 中文正文使用一致的中文标点；公式、图表和引用编号遵守同一套格式。
- 技术语气必须对应实际动作和证据，不维护“高级动词”“国奖常用句”或同义替换词表。
- 章节长度服从任务权重和证据量，不以均匀段落或填满页数为目标。

## 常见失分形态

- 摘要只介绍流程，没有逐问答案或关键数字。
- 问题分析只报模型名称，没有数学归类、选择理由和验证计划。
- 假设不影响模型，符号一词多义，公式缺变量、单位或现实约束说明。
- 结果表图没有直接回答题目，或量化结论无法回指运行记录。
- 灵敏度分析只展示曲线，不说明核心结论是否改变及其失效边界。
- 模型评价只给主观判断，没有证据钩子；推广没有新场景、新约束或数据需求。
- 附录代码、支撑材料、匿名检查或 AI 披露与正文不一致。

## 反模板化门禁

- 本文件只规定段落必须回答的问题，不提供摘要填空句、分问占位段或评价套话。
- 不要求所有论文采用相同目录、标题、章号或段落顺序。
- 每条风格判断都必须由当前题目的对象、变量、约束、结果或证据实例化。
- 删除题目专有信息后仍可原样用于任意论文的段落，应改写为信息要求或删除。
- 风格 pass 不得改变 frozen 数字、单位、方向性结论、限制条件、图表编号或引用编号。
