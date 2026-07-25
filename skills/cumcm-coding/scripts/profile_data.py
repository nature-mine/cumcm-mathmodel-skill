#!/usr/bin/env python3
"""Deterministic data profiling for CUMCM attachments.

Adapted from:
  scipilot-figure-skill/scripts/profile_data.py
  https://github.com/Haojae/scipilot-figure-skill

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

This version adds a workspace-relative path contract, writes a stable report
file, narrows input formats to CSV/TSV/XLSX, and emits Chinese CUMCM guidance.
Runtime dependencies intentionally stay outside this pack's pyproject; the
cumcm-env-doctor Tier 0 contract supplies numpy, pandas and openpyxl.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import warnings
from pathlib import Path
from typing import Any

TYPE_CONTINUOUS = "continuous"
TYPE_CATEGORICAL = "categorical"
TYPE_ORDINAL = "ordinal"
TYPE_DATETIME = "datetime"
TYPE_BOOLEAN = "boolean"
TYPE_TEXT = "text"
TYPE_UNKNOWN = "unknown"
SUPPORTED_SUFFIXES = {".csv", ".tsv", ".xlsx"}


def _load_dependencies() -> tuple[Any, Any]:
    try:
        import numpy as np
        import pandas as pd
    except ModuleNotFoundError as error:
        raise RuntimeError(
            "缺少 Tier 0 依赖 numpy/pandas/openpyxl；先运行 cumcm-env-doctor 并按报告安装。"
        ) from error
    return np, pd


def _safe_workspace_path(
    workspace: Path,
    raw_path: str | Path,
    *,
    must_exist: bool,
) -> Path:
    candidate = Path(raw_path)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise ValueError(f"路径必须是工作区相对路径且不能包含 '..'：{raw_path}")

    root = workspace.resolve()
    resolved = (root / candidate).resolve()
    try:
        resolved.relative_to(root)
    except ValueError as error:
        raise ValueError(f"路径越出工作区：{raw_path}") from error
    if must_exist and not resolved.is_file():
        raise ValueError(f"输入文件不存在：{raw_path}")
    return resolved


def _read_dataframe(path: Path, pd: Any, *, sheet_name: str | None = None) -> Any:
    suffix = path.suffix.lower()
    if suffix not in SUPPORTED_SUFFIXES:
        supported = ", ".join(sorted(SUPPORTED_SUFFIXES))
        raise ValueError(f"不支持 {suffix or '无扩展名'}；仅支持 {supported}")
    try:
        if suffix == ".xlsx":
            return pd.read_excel(path, engine="openpyxl", sheet_name=sheet_name or 0)
        return pd.read_csv(path, sep="\t" if suffix == ".tsv" else ",")
    except ImportError as error:
        raise RuntimeError(f"读取 {suffix} 缺少 Tier 0 依赖：{error}") from error


def _xlsx_sheet_names(path: Path, pd: Any) -> list[str]:
    try:
        with pd.ExcelFile(path, engine="openpyxl") as workbook:
            return [str(name) for name in workbook.sheet_names]
    except ImportError as error:
        raise RuntimeError(f"读取 .xlsx 缺少 Tier 0 依赖：{error}") from error


def _detect_column_type(series: Any, pd: Any) -> str:
    if pd.api.types.is_datetime64_any_dtype(series):
        return TYPE_DATETIME
    if pd.api.types.is_bool_dtype(series):
        return TYPE_BOOLEAN
    if pd.api.types.is_numeric_dtype(series):
        non_null = series.dropna()
        if not non_null.empty and non_null.isin({0, 1}).all() and non_null.nunique() <= 2:
            return TYPE_BOOLEAN
        if not non_null.empty and non_null.nunique() <= 7 and (non_null % 1 == 0).all():
            return TYPE_ORDINAL
        return TYPE_CONTINUOUS
    if isinstance(series.dtype, pd.CategoricalDtype):
        return TYPE_ORDINAL if series.cat.ordered else TYPE_CATEGORICAL
    if pd.api.types.is_object_dtype(series) or pd.api.types.is_string_dtype(series):
        non_null = series.dropna()
        if non_null.empty:
            return TYPE_UNKNOWN
        sample = non_null.iloc[: min(10, len(non_null))]
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                pd.to_datetime(sample, errors="raise")
            return TYPE_DATETIME
        except (TypeError, ValueError):
            pass
        unique_count = int(non_null.nunique())
        unique_ratio = unique_count / max(len(non_null), 1)
        return TYPE_CATEGORICAL if unique_count <= 30 and unique_ratio < 0.5 else TYPE_TEXT
    return TYPE_UNKNOWN


def _label_skew(skew: float | None) -> str:
    if skew is None or math.isnan(skew):
        return "unknown"
    magnitude = abs(skew)
    if magnitude < 0.5:
        return "approximately symmetric"
    if magnitude < 1.0:
        return "moderately skewed"
    return "highly skewed"


def _profile_continuous(series: Any, np: Any) -> dict[str, Any]:
    clean = series.dropna()
    if clean.empty:
        return {"n": 0}

    values = clean.to_numpy(dtype=float)
    q1 = float(clean.quantile(0.25))
    q3 = float(clean.quantile(0.75))
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    outliers = int(((clean < lower) | (clean > upper)).sum()) if len(clean) >= 4 else 0
    standard_deviation = float(clean.std(ddof=1)) if len(clean) > 1 else 0.0
    if len(clean) < 3 or standard_deviation == 0:
        skewness = 0.0 if standard_deviation == 0 else None
    else:
        mean = float(values.mean())
        skewness = float(np.mean(((values - mean) / standard_deviation) ** 3))
    minimum = float(clean.min())
    maximum = float(clean.max())
    needs_log_axis = len(clean) >= 5 and minimum > 0 and maximum / minimum > 100
    return {
        "n": int(len(clean)),
        "mean": float(clean.mean()),
        "median": float(clean.median()),
        "sd": standard_deviation,
        "min": minimum,
        "q1": q1,
        "q3": q3,
        "max": maximum,
        "skewness": skewness,
        "skew_label": _label_skew(skewness),
        "n_outliers_iqr": outliers,
        "outlier_lo": lower,
        "outlier_hi": upper,
        "needs_log_axis": needs_log_axis,
    }


def _profile_categorical(series: Any) -> dict[str, Any]:
    counts = series.dropna().value_counts()
    return {
        "n": int(series.notna().sum()),
        "n_unique": int(len(counts)),
        "categories": [(str(name), int(count)) for name, count in counts.iloc[:20].items()],
        "min_group_n": int(counts.min()) if len(counts) else 0,
        "max_group_n": int(counts.max()) if len(counts) else 0,
        "small_groups_flag": bool(len(counts) and counts.min() < 10),
    }


def _correlations(dataframe: Any, columns: list[str]) -> list[dict[str, Any]]:
    pairs: list[dict[str, Any]] = []
    for index, first in enumerate(columns):
        for second in columns[index + 1 :]:
            paired = dataframe[[first, second]].dropna()
            if len(paired) < 5:
                continue
            coefficient = float(paired[first].corr(paired[second], method="pearson"))
            if math.isnan(coefficient):
                continue
            pairs.append(
                {
                    "a": first,
                    "b": second,
                    "r": coefficient,
                    "n": int(len(paired)),
                }
            )
    return sorted(pairs, key=lambda item: -abs(item["r"]))


def _group_summary(dataframe: Any, group_columns: list[str]) -> dict[str, Any] | None:
    if not group_columns:
        return None
    counts = dataframe.groupby(group_columns, dropna=False).size()
    if counts.empty:
        return {
            "by": group_columns,
            "n_groups": 0,
            "min_n_per_group": 0,
            "median_n_per_group": 0.0,
            "max_n_per_group": 0,
            "small_groups_flag": False,
            "tiny_groups_flag": False,
        }
    return {
        "by": group_columns,
        "n_groups": int(len(counts)),
        "min_n_per_group": int(counts.min()),
        "median_n_per_group": float(counts.median()),
        "max_n_per_group": int(counts.max()),
        "small_groups_flag": bool(counts.min() < 10),
        "tiny_groups_flag": bool(counts.min() < 3),
    }


def _chart_suggestions(
    columns: dict[str, dict[str, Any]],
    group_summary: dict[str, Any] | None,
) -> list[str]:
    continuous = [name for name, info in columns.items() if info["type"] == TYPE_CONTINUOUS]
    categorical = [
        name
        for name, info in columns.items()
        if info["type"] in {TYPE_CATEGORICAL, TYPE_BOOLEAN, TYPE_ORDINAL}
    ]
    datetimes = [name for name, info in columns.items() if info["type"] == TYPE_DATETIME]
    suggestions: list[str] = []
    if datetimes and continuous:
        suggestions.append(f"{datetimes[0]} 与 {continuous[0]}：折线图并标明时间断点")
    if categorical and continuous:
        if group_summary and group_summary["small_groups_flag"]:
            suggestions.append("分类与连续变量且有小组样本：箱线/小提琴图叠加原始点")
        else:
            suggestions.append("分类与连续变量：箱线图、点图或说明误差定义的区间图")
    if len(continuous) >= 2:
        suggestions.append("连续变量关系：散点图；多变量时补充相关热力图")
    if continuous and not categorical and not datetimes:
        suggestions.append("连续变量分布：直方图、ECDF 或箱线图")
    for name in continuous:
        if columns[name].get("needs_log_axis"):
            suggestions.append(f"{name} 跨越两个以上数量级且全正：评估对数轴")
    return suggestions or ["先明确图要论证的结论，再按数据形态选择图型"]


def profile_data(
    source: str | Path,
    *,
    workspace: str | Path = ".",
    group_columns: list[str] | None = None,
    sheet_name: str | None = None,
) -> dict[str, Any]:
    """Profile one table from a workspace-relative CSV, TSV or XLSX file."""
    np, pd = _load_dependencies()
    workspace_path = Path(workspace)
    source_path = _safe_workspace_path(workspace_path, source, must_exist=True)
    if sheet_name is not None and source_path.suffix.lower() != ".xlsx":
        raise ValueError("--sheet 只适用于 XLSX 输入")
    dataframe = _read_dataframe(source_path, pd, sheet_name=sheet_name)
    groups = group_columns or []
    missing_groups = [name for name in groups if name not in dataframe.columns]
    if missing_groups:
        raise ValueError(f"分组列不存在：{', '.join(missing_groups)}")

    columns: dict[str, dict[str, Any]] = {}
    report_warnings: list[str] = []
    for raw_name in dataframe.columns:
        name = str(raw_name)
        series = dataframe[raw_name]
        column_type = _detect_column_type(series, pd)
        total = int(len(series))
        missing = int(series.isna().sum())
        info: dict[str, Any] = {
            "type": column_type,
            "n_total": total,
            "n_null": missing,
            "missing_rate": missing / total if total else 0.0,
        }
        if info["missing_rate"] > 0.2:
            report_warnings.append(f"列 {name} 缺失率超过 20%，建模前需说明处理。")
        if column_type == TYPE_CONTINUOUS:
            info.update(_profile_continuous(series, np))
        elif column_type in {TYPE_CATEGORICAL, TYPE_BOOLEAN, TYPE_ORDINAL}:
            info.update(_profile_categorical(series))
            if info["small_groups_flag"]:
                report_warnings.append(f"列 {name} 存在 n<10 的类别，出图应展示原始点。")
        elif column_type == TYPE_DATETIME:
            parsed = pd.to_datetime(series, errors="coerce").dropna()
            if not parsed.empty:
                info["min"] = str(parsed.min())
                info["max"] = str(parsed.max())
        columns[name] = info

    continuous_columns = [name for name, info in columns.items() if info["type"] == TYPE_CONTINUOUS]
    groups_info = _group_summary(dataframe, groups)
    result = {
        "source": str(Path(source)),
        "n_rows": int(dataframe.shape[0]),
        "n_cols": int(dataframe.shape[1]),
        "columns": columns,
        "correlations": _correlations(dataframe, continuous_columns),
        "group_summary": groups_info,
        "warnings": report_warnings,
        "chart_suggestions": _chart_suggestions(columns, groups_info),
    }
    if sheet_name is not None:
        result["sheet"] = sheet_name
    return result


def profile_workbook(
    source: str | Path,
    *,
    workspace: str | Path = ".",
    group_columns: list[str] | None = None,
) -> dict[str, Any]:
    """Profile every worksheet in a workspace-relative XLSX workbook."""
    _, pd = _load_dependencies()
    workspace_path = Path(workspace)
    source_path = _safe_workspace_path(workspace_path, source, must_exist=True)
    if source_path.suffix.lower() != ".xlsx":
        raise ValueError("全工作表剖析只适用于 XLSX 输入")
    sheet_names = _xlsx_sheet_names(source_path, pd)
    return {
        "source": str(Path(source)),
        "sheet_count": len(sheet_names),
        "sheets": {
            name: profile_data(
                source,
                workspace=workspace_path,
                group_columns=group_columns,
                sheet_name=name,
            )
            for name in sheet_names
        },
    }


def _markdown_cell(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def render_report(info: dict[str, Any]) -> str:
    """Render a stable Chinese Markdown report."""
    lines = [
        "# 数据剖析报告",
        "",
        f"- 来源：`{info['source']}`",
        f"- 规模：{info['n_rows']} 行 × {info['n_cols']} 列",
        "",
        "## 列概况",
        "",
        "| 列 | 类型 | 有效 n | 缺失 | 摘要 |",
        "|---|---|---:|---:|---|",
    ]
    for name, column in info["columns"].items():
        summary = ""
        if column["type"] == TYPE_CONTINUOUS and column.get("n", 0):
            summary = (
                f"mean={column['mean']:.4g}, median={column['median']:.4g}, "
                f"sd={column['sd']:.4g}, range=[{column['min']:.4g}, {column['max']:.4g}], "
                f"IQR异常={column['n_outliers_iqr']}"
            )
        elif column["type"] in {TYPE_CATEGORICAL, TYPE_BOOLEAN, TYPE_ORDINAL}:
            categories = ", ".join(f"{key}({count})" for key, count in column["categories"][:5])
            summary = f"{column['n_unique']} 类：{categories}"
        elif column["type"] == TYPE_DATETIME:
            summary = f"{column.get('min', '?')} → {column.get('max', '?')}"
        lines.append(
            "| {name} | {type_name} | {valid} | {missing} ({rate:.1%}) | {summary} |".format(
                name=_markdown_cell(name),
                type_name=column["type"],
                valid=column["n_total"] - column["n_null"],
                missing=column["n_null"],
                rate=column["missing_rate"],
                summary=_markdown_cell(summary),
            )
        )

    lines.extend(["", "## 相关性", ""])
    if info["correlations"]:
        for pair in info["correlations"][:10]:
            lines.append(
                f"- `{pair['a']}` ↔ `{pair['b']}`：Pearson r={pair['r']:.3f}，n={pair['n']}"
            )
    else:
        lines.append("- 连续列不足或成对有效样本少于 5，未计算 Pearson 相关。")

    if info["group_summary"]:
        group = info["group_summary"]
        lines.extend(
            [
                "",
                "## 分组样本量",
                "",
                f"- 分组列：`{'`, `'.join(group['by'])}`",
                f"- 组数：{group['n_groups']}",
                (
                    f"- 每组 n：min={group['min_n_per_group']}，"
                    f"median={group['median_n_per_group']:.1f}，"
                    f"max={group['max_n_per_group']}"
                ),
            ]
        )

    lines.extend(["", "## 异常与风险", ""])
    lines.extend(f"- {item}" for item in info["warnings"])
    if not info["warnings"]:
        lines.append("- 未触发缺失率或小样本类别的机械警告。")

    lines.extend(["", "## 初步图型建议", ""])
    lines.extend(f"- {item}" for item in info["chart_suggestions"])
    lines.extend(
        [
            "",
            "> 本报告只描述数据形态，不构成模型结论。最终选图必须从论文 claim 出发。",
            "",
        ]
    )
    return "\n".join(lines)


def render_workbook_report(info: dict[str, Any]) -> str:
    """Render all worksheet profiles into one stable Markdown report."""
    lines = [
        "# 数据剖析报告",
        "",
        f"- 来源：`{info['source']}`",
        f"- 工作表：{info['sheet_count']} 张",
    ]
    for sheet_name, sheet_info in info["sheets"].items():
        lines.extend(["", f"## 工作表：{_markdown_cell(sheet_name)}", ""])
        sheet_lines = render_report(sheet_info).splitlines()
        for line in sheet_lines[1:]:
            lines.append(f"#{line}" if line.startswith("## ") else line)
    return "\n".join(lines).rstrip() + "\n"


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="剖析 CUMCM 工作区内的 CSV/TSV/XLSX 附件")
    parser.add_argument("source", help="相对于工作区的输入文件")
    parser.add_argument("--workspace", default=".", help="竞赛工作区，默认当前目录")
    parser.add_argument("--group", action="append", default=[], help="分组列，可重复")
    parser.add_argument("--sheet", help="仅剖析指定 XLSX 工作表；默认剖析全部工作表")
    parser.add_argument("--json", action="store_true", help="输出结构化 JSON")
    parser.add_argument("--output", help="相对于工作区的输出路径")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    try:
        source = _safe_workspace_path(Path(args.workspace), args.source, must_exist=True)
        if source.suffix.lower() == ".xlsx" and args.sheet is None:
            info = profile_workbook(
                args.source,
                workspace=args.workspace,
                group_columns=args.group,
            )
            render = render_workbook_report
        else:
            info = profile_data(
                args.source,
                workspace=args.workspace,
                group_columns=args.group,
                sheet_name=args.sheet,
            )
            render = render_report
        default_output = "data_profile.json" if args.json else "data_profile.md"
        output = _safe_workspace_path(
            Path(args.workspace),
            args.output or default_output,
            must_exist=False,
        )
        output.parent.mkdir(parents=True, exist_ok=True)
        content = (
            json.dumps(info, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
            if args.json
            else render(info)
        )
        output.write_text(content, encoding="utf-8")
    except (OSError, RuntimeError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2

    print(f"WROTE {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
