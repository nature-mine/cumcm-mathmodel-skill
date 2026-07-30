<!--
Adapted from repository: https://github.com/ZyhSechub/chinese-thesis-workbench-skill
Referenced upstream paths:
- references/standards/style-extraction.md
- references/delivery/final-delivery-check.md
Upstream license: MIT
Upstream copyright: Copyright (c) 2026 Zyhsec

This file adapts visible-style observation and final-delivery checks to the
CUMCM Markdown-to-DOCX workflow. It does not promise exact template cloning.

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

# DOCX 版面与导出规则

## 规则边界

每届开赛先读取 `cumcm-hub/references/cumcm-profile.md` 并按当届通知复核数字。A4、摘要单页、正文不设目录、正文页数上限、页边距、电子文件大小和附录要求属于会变化的竞赛约束，不能凭往届记忆执行。

`templates/cumcm-docx-spec.yaml` 是本包推荐版式，不是官方统一字体规范。赛区另有要求时，把覆盖后的完整配置放进竞赛工作区，再通过 `--spec` 传给导出脚本。覆盖配置的四边页边距仍不得低于当届已核实下限。

## 外部模板观察与 spec 映射

需要按赛区模板或其他正式样式起稿时，只在源文件副本上观察目录层级、标题与正文、摘要与关键词、图题与表题、参考文献和附录的可见样式，并记录分页、对齐、字体字号、行距、段前段后和首行缩进。观察记录按以下状态分开：

| 状态 | 含义 | 后续动作 |
|---|---|---|
| 已观察 | 能从可见内容或文档结构直接确认 | 记录具体位置与样式表现 |
| 不能确认 | 仅凭当前文件无法判断精确规则 | 保留未知，不按经验补值 |
| 需官方确认 | 涉及当届或赛区硬性要求 | 回到正式通知或模板说明核验 |
| 候选映射 | 可对应到版式配置字段，但尚未实施 | 人工核对后写入完整覆盖配置 |

观察或解析结果不能直接驱动导出器，也不得把工具生成的 JSON 或样式统计自动当作 `--spec`。应人工形成完整覆盖配置，逐项核对字段含义与当届页边距下限，再导出、渲染并查看实际页面。该流程用于接近已确认的版式要求，不承诺对外部模板作像素级复刻。

从空白工作区起稿时，把[内置 Markdown 模板](../templates/paper-template.md)复制为
`paper/paper.md`；[内置 DOCX 模板](../templates/paper-template.docx)由同一源稿确定性生成，只用于
预览骨架与推荐版式。源稿已经演示表格、车道 B/C 占位和真实图片指令的启用时机，定稿前必须
清除全部 `【待替换】`。

## Markdown 输入契约

- `#` 用于论文题目；`##`、`###`、`####` 依次进入三级标题。
- 不生成目录。摘要后的第一个 `##` 自动另起一页，附录由导出脚本另起一页。
- 普通 Markdown 表格前必须紧跟一行 `[[TABLE caption="表题"]]`。导出器自动按出现顺序生成“表 1、表 2……”，表题置于表格上方，表格使用三线表。
- 真实图使用单行指令：

  ```text
  [[FIGURE id="FIG-A-01" path="figures/result.png" caption="灵敏度分析结果"]]
  ```

- 未定稿的车道 B/C 图使用单行指令：

  ```text
  [[PLACEHOLDER id="FIG-G-01" lane="C" chapter="2.1" expected="供需反馈机制示意图"]]
  ```

字段值含空格时必须加引号。图按出现顺序生成“图 1、图 2……”，图题置于图下。`id` 必须与 `figure_registry.md` 一致；占位槽明确显示 figure id、车道、章节和期望内容，不能被误当成结果证据。

- 需要块级可编辑公式时使用单行指令：

  ```text
  [[EQUATION latex="y_i=\alpha+\beta x_i+\epsilon_i"]]
  ```

  `latex` 字段只写表达式，不带 `$...$` 定界符；`latex` 值必须始终用一对英文双引号包裹；引号内内容逐字符进入转换（`\frac`、`\\` 等原样保留，不存在转义层）；值内不得使用英文双引号字符。导出器先用纯 Python `latex2mathml` 转成 MathML，再用包内转换资源生成 Word 可编辑 OMML，正常安装依赖后运行期不联网。花括号不配对、命令未知、操作数缺失或落入暂不支持的 MathML 元素时，导出必须显式失败且不写 DOCX，不能把原始命令静默放进论文。

  公式建议保持可编辑，不以截图替代。需要在正文引用的公式，应在终稿中统一核对编号和引用；指令本身不替作者判断哪些公式需要编号。

## 图表与页面

- 真实图片只指定宽度，由 `python-docx` 保持纵横比；宽度取配置上限与版心宽度的较小值，不得越过页边距。
- 图内文字在 DOCX 100% 比例下必须可读。车道 A 和已定稿车道 B 使用真实图；未定稿 B/C 保持显式占位，禁止用空白或伪造数据替代。
- 图题在图下，表题在表上；图表必须在正文中按编号引用。表格跨页时优先保持表头可识别，避免把关键结果挤成不可读的小字。
- 图表体量建议以支撑判断为准，不设数量目标；页数上限优先，避免为凑数加入不能推进论证的图表。
- 正文建议保持紧凑，避免无内容的大段空行；需要分隔内容时优先使用标题层级和段落间距。
- 页数是上限，不是填满目标。正文优先保留“机制/方法—结果—验证—解释—局限”的完整证据链，删去重复复述和无证据铺陈。
- 页脚必须含实时 `PAGE` 字段。OfficeCLI 或其他无分页字段引擎的预览可能只显示缓存值，结构检查以字段存在为准。

## 附录与支撑材料

`docx_export.py` 扫描 `code/` 中全部非隐藏、非编译产物的 UTF-8 文件，按相对路径排序，以“源程序：路径”为小标题逐文件完整导入。正文写作者不得手抄、节选或润色附录代码。代码使用小号等宽字体，保留制表符、换行和缩进，长行交给 Word 在版心内软换行。

支撑材料清单同时写入 DOCX 和 `support_manifest.json`：

- `input/`：赛题原始附件，清单标记“不进入支撑材料压缩包”；
- `data/`：自主查阅或派生数据，标记“进入”；
- `code/`：全部源程序，标记“进入”，并记录 SHA-256。

没有使用程序时，附录必须明确写“本论文没有用到程序”。

## 视觉自检

导出后优先执行：

```bash
officecli validate paper/cumcm-paper.docx
officecli view paper/cumcm-paper.docx issues
officecli view paper/cumcm-paper.docx outline
officecli view paper/cumcm-paper.docx screenshot --grid auto -o /tmp/cumcm-paper.png
```

实际查看整份 PNG，再对可疑页面单页放大。至少核对：摘要与正文分页、页边距、标题层级、图表顺序和尺寸、占位槽标注、页码字段、附录代码的等宽字体/缩进/软换行、支撑材料分类。修改后重跑完整检查。

终稿交付前还应核对：

- 中文、西文和数字没有无意的字体混用、缺字替代或局部样式漂移；
- 不存在 `【待替换】` 等未完成正文提示；
- 批注、修订痕迹和待处理说明均已逐项解决；
- 正文没有残留 `**`、反引号、裸 Markdown 链接等源稿标记。

`officecli view ... issues` 可能把摘要/关键词的块式无缩进、代码中的连续空格与中英文源文件名报告为问题；这些需结合所在段落判定。不得为清零告警而给摘要强加首行缩进，或合并源程序中的空格。

OfficeCLI 不可用时，依次降级为 `libreoffice/soffice` 转 PDF 后用 `pdftoppm` 渲染，或明确提示人工在 Word/WPS 中打开核对。结构校验通过不能替代视觉检查。
