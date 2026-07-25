# 非数据图规则

本规则只处理车道 B 精确结构图和车道 C 概念图。流程借鉴本地 `MathModelAgent-skills/4drawio` 的“可编辑源 + CLI 可选导出”思想；该项目未附许可证，本文和 XML 示例均为独立编写，不复制其文案或模板。

## 车道 B 选型

| 图意 | 建议结构 |
|---|---|
| 整体技术路线 | 自左向右或自上而下的阶段链，标明子问题依赖 |
| 单问求解流程 | 输入 → 处理/算法 → 判定/循环 → 输出 |
| 模型结构 | 模块、状态量、参数与反馈边 |
| 数据处理流程 | 原始附件 → 清洗 → 特征 → 模型输入，标记派生文件 |
| 指标体系 | 目标层 → 准则层 → 指标层 |
| 决策规则 | 菱形分支，边上写简短条件 |

不为凑数量作图。坐标图、热力图、敏感性曲线和结果比较属于车道 A。

## `.drawio` 最小结构

文件使用未压缩的 diagrams.net XML，便于 diff 和审查：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<mxfile host="app.diagrams.net">
  <diagram id="fig-example" name="Page-1">
    <mxGraphModel grid="1" page="1" pageWidth="1169" pageHeight="827">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
        <mxCell id="n1" value="输入" style="rounded=1;whiteSpace=wrap;html=1;"
                vertex="1" parent="1">
          <mxGeometry x="80" y="100" width="140" height="54" as="geometry"/>
        </mxCell>
        <mxCell id="n2" value="模型" style="rounded=1;whiteSpace=wrap;html=1;"
                vertex="1" parent="1">
          <mxGeometry x="300" y="100" width="140" height="54" as="geometry"/>
        </mxCell>
        <mxCell id="e1" style="edgeStyle=orthogonalEdgeStyle;html=1;"
                edge="1" parent="1" source="n1" target="n2">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

要求：

- `mxCell` id 全局唯一，边的 `source`/`target` 必须存在；
- XML 特殊字符正确转义，不在标签中嵌入长段公式或 Markdown；
- 同级节点尺寸、字体、圆角和色系一致；
- 主要阅读方向唯一，尽量使用正交边，避免边穿过节点；
- 节点标签优先用动宾短语；变量符号与正文一致；
- 画布四周留白，最终 100% 比例下标签可读；
- 不放学校、队员、赛区或其他身份信息。

## 导出与降级

依次探测 `drawio`、`draw.io`、`draw.io.exe`。可用时：

```bash
drawio --export --format png --crop --output figures/fig_model_draft.png \
  figures/fig_model.drawio
```

CLI 不可用时保留 `.drawio`，在交接中注明可用 diagrams.net 网页版打开并导出。

需要预览结构或排查边关系时，可另写 DOT：

```bash
dot -Tsvg figures/fig_model.dot -o figures/fig_model_preview.svg
dot -Tpng figures/fig_model.dot -o figures/fig_model_preview.png
```

Graphviz 命令依据 Graphviz 官方输出文档核对。DOT 只是预览降级，不替代 `.drawio` 交付。

## 结构自检

最多执行 3 轮“导出 → 查看 → 修复”：

1. XML 解析成功，文件非空；
2. 所有契约要求的节点、分支和反馈关系存在；
3. 节点无明显重叠，边不穿过核心节点；
4. 文字、方向、单位和符号与冻结建模件一致；
5. 导出图没有裁切、乱码、过小文字或身份信息。

无法导出不等于结构失败；记录降级并保留可编辑源。结构内容不确定才是 `blocked`。

## 车道 C 边界

概念图 prompt 只描述已经在冻结材料中出现的实体、机制和关系。明确要求：

- 平面、简洁、可后续重绘的画面语言；
- 短标签、克制配色、清晰主次；
- 不生成定量坐标、数据曲线、p 值、精确测量、机构 logo 或评奖标识；
- 不把概念画面表述为实验或计算证据；
- 默认只产 payload 和占位，API 调用需用户另行明确授权。
