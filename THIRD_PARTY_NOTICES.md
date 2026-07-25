# 第三方代码与内容声明

本包本身使用根 `LICENSE` 中的 MIT License。以下文件包含或改编自第三方项目的代码或内容：

## scipilot-figure-skill

- 文件：`skills/cumcm-coding/scripts/profile_data.py`
- 上游：`scipilot-figure-skill/scripts/profile_data.py`
- 作者声明：Copyright (c) 2026 Haojae
- 许可证：MIT
- 修改：增加工作区相对路径约束、固定报告输出、收窄输入格式并改写为 CUMCM 中文报告。

完整的上游版权与 MIT 许可文本保留在该源文件头部。

## My-MathModeling-skills

- 文件：`skills/cumcm-writing/references/award-style-profile.md`
- 上游：`github.com/capwitf/My-MathModeling-skills`
- 参考路径：
  - `math-templates/references/national-prize-style-profile.md`
  - `math-templates/references/section-format-controls.md`
  - `math-templates/assets/contest-project-template/paper/section_templates_national.md`
- 作者声明：Copyright (c) 2026 capwitf
- 许可证：MIT
- 修改：将章节信息密度、证据闭环和版面一致性原则改写为本包的自适应风格画像；未引入固定目录、填空段落或句式库。

完整的上游版权与 MIT 许可文本保留在该参考文件头部。

## nature-skills

- 文件：`skills/cumcm-diagram/scripts/schematic_prompt.py`
- 上游：`nature-skills/skills/nature-figure/scripts/generate_openrouter_schematic.py`
- 许可证：Apache License 2.0
- 修改：移除 API、密钥、网络请求和图像保存逻辑，只保留 provider-neutral prompt/payload，并新增 CUMCM 图号、占位和路径安全契约。

Apache License 2.0 全文见 [licenses/Apache-2.0.txt](licenses/Apache-2.0.txt)。

## chinese-thesis-workbench-skill

- 文件：`skills/cumcm-writing/scripts/docx_export.py`
- 上游：`chinese-thesis-workbench-skill/scripts/docx/generate_thesis_docx.py`
- 作者声明：Copyright (c) 2026 Zyhsec
- 许可证：MIT
- 修改：收窄为 CUMCM Markdown 契约，增加工作区路径约束、确定性 ZIP 元数据、图示占位槽、附录源程序逐文件导入和支撑材料分类清单。

完整的上游版权与 MIT 许可文本保留在该源文件头部。
