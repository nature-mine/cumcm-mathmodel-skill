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
| 区间保持或事件触发的跳变 | 阶梯图 | 事件顺序、跳变时点；避免折线暗示区间内存在连续线性变化 |
| 两组或双时点差异 | 哑铃图、斜率图 | 两端口径、连接方向、变化量标注 |
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
| 多源多汇的流量或能量转移 | 桑基图 | 节点语义、单位、入流与出流守恒 |
| 调度、排程与任务依赖 | 甘特图 | 起止时间、依赖关系、时间粒度 |

## 论证质量建议

以下属于经验性质量建议，不是官方合规要求：

- 敏感性图建议标明参数基准线、临界点及跨越临界点后的决策变化，避免只展示响应曲线。
- 方案比较图建议同时报告目标值与约束满足情况，避免把目标更优但不可行的方案呈现为推荐结果。
- 定稿前优先剔除三类低效图表：没有正文解释的截图、没有单位的三维曲面、没有基准却只声称“趋势很好”的拟合图。
- 生成脚本建议在渲染前核对所需数据列、输入数组维度和比值计算的零分母；缺列或维度不一致时保留显式失败，不临时补造字段。
- 多序列图建议提供清晰图例或在曲线末端直接标注；标签使用正文中的变量名称，不沿用内部字段名，图例优先放在不遮挡数据与误差区间的位置。
- 连续色阶建议配带变量名和单位的 colorbar；用于跨图比较时，建议锁定色阶范围与中心，避免同色代表不同数值。
- 高级图型只有在能增加论证信息时才使用，不以视觉复杂度替代证据。
- 警惕高频 AI 模板图造成的同质化；雷达图缺少不可替代的多维比较目的时不用，热力图必须明确矩阵语义、尺度、排序和色阶中心，并由正文解释其支持的判断。
- 需要同时呈现总体关系和个体分布时，可在相关热力图的边缘或对称位置组合关键变量的散点图、直方图；组图仍须保证坐标、色标和标签清晰。

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

### 默认候选色板

赛题或赛区没有指定视觉规范、且离散系列需要配色时，可从下表选择一套作为起点。名称只描述视觉取向，不代表对应期刊或组织的官方规范。整篇论文锁定同一套候选，同一变量跨图保持同色。

| 风格候选 | 主色 | 辅色 | 视觉取向 |
|---|---|---|---|
| Nature 风格 | 深靛蓝 `#3B5F8A`、暗红 `#A23B3B`、墨绿 `#4A7C59` | 暖灰 `#B8B8B8`、浅米 `#F0E6D3` | 低饱和、对比明确、整体克制 |
| Science 风格 | 钴蓝 `#307EC7`、砖红 `#D9534F`、琥珀 `#F0AD4E` | 石板灰 `#5D6D7E` | 色彩较明快，同时保持正式感 |
| IEEE 电力风格 | 国网绿 `#009944`、深蓝 `#003366`、橙红 `#E74C3C` | 浅蓝 `#AED6F1`、淡绿 `#A9DFBF` | 偏向电力、能源主题的行业化表达 |

这些候选只处理离散系列，不放宽“禁止彩虹色图”的限制，也不替代连续或发散色阶。相关热力图仍应使用以零点为中心的发散配色，并明确色阶范围。

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
