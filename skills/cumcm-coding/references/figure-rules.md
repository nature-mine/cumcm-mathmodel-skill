<!--
Adapted from repository: https://github.com/Haojae/scipilot-figure-skill
Upstream license: MIT
Upstream copyright: Copyright (c) 2026 Haojae
Referenced upstream paths:
- references/viz_pitfalls.md
- references/publication_checklist.md

This file selects and rewrites visualization checks relevant to CUMCM data
figures, adds contest-workspace provenance and reproducibility rules, and
omits journal-specific publication requirements.
It does not reproduce the upstream code examples or publication workflow.

MIT License

Copyright (c) 2026 Haojae

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

# 数据图规则

车道 A 只承载由真实数据或模型结果生成的定量图。

## 先确定论证目标

出图前写一句“这张图要让评委看见什么”，再结合 `data_profile.md` 决定图型。没有明确 claim、数据源或生成脚本的图不得进入论文。

| 数据关系 | 首选图型 | 必查事项 |
|---|---|---|
| 随时间变化 | 折线图 | 时间顺序、断点、置信带 |
| 类别间比较 | 点图、箱线图、小提琴图 | 样本量、原始点、误差定义 |
| 两连续变量关系 | 散点图 | 趋势、异常点、相关不等于因果 |
| 多变量相关 | 相关热力图 | 样本量、共线性、配色中心 |
| 单变量分布 | 直方图、ECDF、KDE | 箱宽/带宽、偏态、长尾 |
| 模型预测性能 | 预测-真实、残差图 | 基线、测试集隔离、不确定性 |
| 分类性能 | ROC、PR、混淆矩阵 | 类别不平衡、阈值与归一化 |
| 灵敏度 | 参数-响应曲线、龙卷风图 | 扰动基准、范围和单位 |
| 优化权衡 | Pareto 前沿、目标-约束图 | 可行性、支配关系、场景 |
| 空间分布 | 地图、等值线 | 坐标系、比例尺、插值说明 |
| 网络结构 | 网络图 | 节点/边语义、稀疏化规则 |
| 层级构成 | 堆叠条形、面积图 | 总量基准、层级顺序；少用饼图 |

## 论证质量建议

以下属于经验性质量建议，不是官方合规要求：

- 敏感性图建议标明参数基准线、临界点及跨越临界点后的决策变化，避免只展示响应曲线。
- 方案比较图建议同时报告目标值与约束满足情况，避免把目标更优但不可行的方案呈现为推荐结果。
- 定稿前优先剔除三类低效图表：没有正文解释的截图、没有单位的三维曲面、没有基准却只声称“趋势很好”的拟合图。
- 生成脚本建议在渲染前核对所需数据列、输入数组维度和比值计算的零分母；缺列或维度不一致时保留显式失败，不临时补造字段。
- 多序列图建议提供清晰图例或在曲线末端直接标注；标签使用正文中的变量名称，不沿用内部字段名，图例优先放在不遮挡数据与误差区间的位置。
- 连续色阶建议配带变量名和单位的 colorbar；用于跨图比较时，建议锁定色阶范围与中心，避免同色代表不同数值。

## 禁止和限制

- 禁止双 Y 轴制造不可比趋势；确需两尺度时拆成对齐子图。
- 禁止彩虹色图、3D 柱状图、装饰阴影和无意义渐变。
- 小样本不得只画均值柱；展示原始点和分布，并明确误差棒是 SD、SEM 还是 CI。
- 不用饼图承载细微差异或过多类别；优先排序条形图。
- 坐标轴不得截断到夸大差异；非零起点必须有理由并醒目标明。
- 平滑、插值、聚合和异常值剔除必须在图注或方法中可追溯。
- 不把训练集性能当作泛化结果，不选择性隐藏不利场景。
- 不在图内写无法从结果文件追溯的数字。

## 中文与版式

- 显式设置可用的 CJK 字体候选，并设置 `axes.unicode_minus = False`。
- 字号按论文 100% 缩放检查；图例、刻度、单位和面板标签必须可读。
- 同一变量跨图使用一致颜色、单位、范围和命名。
- 颜色之外再用线型、点型或纹理编码；灰度打印和常见色觉缺陷下仍可区分。
- 图题说明结论，图注说明数据、场景、样本量、误差与缩写，不重复正文。

## 可复现与自检

每张图登记：

```markdown
| id | lane | status | claim | data_source | method | run_log | chapter | path | provenance | review |
```

车道 A 使用 `status=done`；`method` 写生成脚本，`provenance` 写结果文件与命令。

按以下闭环最多执行 3 轮：

1. 从结果文件重新渲染；
2. 程序检查尺寸、空白输出、字体警告和文件非空；建议把中文、负号、特殊符号缺字以及文字裁切设为导出终检失败项；
3. 以论文 100% 比例查看标签、遮挡、图例是否压住证据、单位和视觉层级；
4. 只修改生成脚本后重新渲染，禁止直接修图掩盖数据问题。

PNG 用于兼容交付；可行时同时保存 SVG/PDF。位图不得靠上采样冒充高分辨率。
