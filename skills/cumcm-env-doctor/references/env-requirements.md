# 环境分层要求

## Step 0：环境管理器

| 项目 | 理想状态 | 缺失处理 |
|---|---|---|
| uv | `uv` 在 PATH | 建议运行官方安装脚本；用户拒绝时降级 `python -m venv` |
| `.venv` | 位于竞赛工作区 | `uv venv` 创建；已有环境不覆盖 |

uv 安装与 `uv venv` 命令依据 Astral 官方文档核验。环境管理器降级不直接阻塞；实际 Python 与 Tier 0 包仍按下表判定。

## Tier 0：硬性依赖

任一缺失均阻塞。

| 检查 | 导入名/方式 | 用途 | 安装建议 |
|---|---|---|---|
| Python ≥3.10 | 当前解释器 | 运行全部确定性脚本 | 安装 Python 3.10+ |
| NumPy | `numpy` | 数值计算 | `uv add numpy` |
| pandas | `pandas` | 表格与数据处理 | `uv add pandas` |
| SciPy | `scipy` | 科学计算与基础优化 | `uv add scipy` |
| Matplotlib | `matplotlib` | 数据图 | `uv add matplotlib` |
| openpyxl | `openpyxl` | 读取 `.xlsx` 官方附件 | `uv add openpyxl` |
| python-docx | `docx` | DOCX 主交付 | `uv add python-docx` |
| latex2mathml | `latex2mathml` | 把 LaTeX 公式离线转换为可编辑 OMML | `uv add latex2mathml` |
| Skill 包 | 七个 `skills/*/SKILL.md` 与目录名一致 | 宿主加载基础 | 重新安装或修复 Skill 包 |

脚本只能验证 Skill 包结构；宿主是否真正完成显式调用，由 hub 在启动时再验证。

## Tier 1：按题型安装

缺失记为 `MISS`，不阻塞；路线确认后只安装实际需要的包。

| 包 | 导入名 | 常见用途 |
|---|---|---|
| scikit-learn | `sklearn` | 回归、分类、聚类与预处理 |
| statsmodels | `statsmodels` | 统计模型与时间序列 |
| networkx | `networkx` | 图与网络模型 |
| PuLP | `pulp` | 线性/整数规划 |
| OR-Tools | `ortools` | 调度、路径与组合优化 |
| SciPy optimize | `scipy.optimize` | 连续优化 |
| seaborn | `seaborn` | 统计图辅助 |

使用 `uv add <package>`，不得一次性安装全部候选依赖。

## Tier 2：系统工具

缺失记为 `DEGRADED`，永不单独阻塞。

| 工具 | 检测 | 用途 | 降级 |
|---|---|---|---|
| CJK 字体 | `fc-list` 搜索 Noto/思源/黑体/微软雅黑 | 中文图不出现方框 | 建议安装 `fonts-noto-cjk`；绘图使用字体回退链并设置 `axes.unicode_minus=False` |
| draw.io | `drawio` 或 `draw.io` | 车道 B `.drawio` 导出 | 保留 XML 源，用户在网页版导出 |
| Graphviz | `dot` | 结构图备选 | 只保留 `.dot` 或改用 draw.io |
| OfficeCLI | `officecli` | DOCX → HTML/PNG 视觉自检 | 用 LibreOffice + `pdftoppm`，再不行则人工打开 |
| LibreOffice | `soffice` 或 `libreoffice` | OfficeCLI 缺失时转 PDF | OfficeCLI 或人工检查 |
| pdftoppm | `pdftoppm` | PDF 逐页 PNG | OfficeCLI 或人工检查 |

OfficeCLI 命令名与安装方式依据工作区 `reference-skills/OfficeCLI` 的 Apache-2.0 官方 checkout 核验；缺失时报告链接 `https://officecli.ai`，不自动下载。

## 联网通路

通路由宿主实测后传给脚本。至少一个成功通路时为 `OK`；全部不可用或未检测时为 `DEGRADED`。

允许探测官方规则页、方法论文检索和公开数据。竞赛期间严禁以探测为名搜索当届赛题解答、解析、代码或讨论。
