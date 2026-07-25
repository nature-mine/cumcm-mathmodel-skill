# DOCX 版面与导出规则

## 规则边界

每届开赛先读取 `cumcm-hub/references/cumcm-profile.md` 并按当届通知复核数字。A4、摘要单页、正文不设目录、正文页数上限、页边距、电子文件大小和附录要求属于会变化的竞赛约束，不能凭往届记忆执行。

`templates/cumcm-docx-spec.yaml` 是本包推荐版式，不是官方统一字体规范。赛区另有要求时，把覆盖后的完整配置放进竞赛工作区，再通过 `--spec` 传给导出脚本。覆盖配置的四边页边距仍不得低于当届已核实下限。

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

## 图表与页面

- 真实图片只指定宽度，由 `python-docx` 保持纵横比；宽度取配置上限与版心宽度的较小值，不得越过页边距。
- 图内文字在 DOCX 100% 比例下必须可读。车道 A 和已定稿车道 B 使用真实图；未定稿 B/C 保持显式占位，禁止用空白或伪造数据替代。
- 图题在图下，表题在表上；图表必须在正文中按编号引用。表格跨页时优先保持表头可识别，避免把关键结果挤成不可读的小字。
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

`officecli view ... issues` 可能把摘要/关键词的块式无缩进、代码中的连续空格与中英文源文件名报告为问题；这些需结合所在段落判定。不得为清零告警而给摘要强加首行缩进，或合并源程序中的空格。

OfficeCLI 不可用时，依次降级为 `libreoffice/soffice` 转 PDF 后用 `pdftoppm` 渲染，或明确提示人工在 Word/WPS 中打开核对。结构校验通过不能替代视觉检查。
