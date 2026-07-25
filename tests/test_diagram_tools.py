from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from types import ModuleType

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _load_module(name: str, relative: str) -> ModuleType:
    path = ROOT / relative
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_schematic_prompt_writes_provider_neutral_placeholder(tmp_path: Path) -> None:
    module = _load_module(
        "schematic_prompt",
        "skills/cumcm-diagram/scripts/schematic_prompt.py",
    )
    result = module.main(
        [
            "--workspace",
            str(tmp_path),
            "--figure-id",
            "FIG-G-02",
            "--title",
            "供需耦合机制",
            "--chapter",
            "6.2",
            "--purpose",
            "解释供给、需求和反馈之间的概念关系",
            "--element",
            "供给端",
            "--element",
            "需求端",
            "--relationship",
            "供给端与需求端通过反馈闭环连接",
        ]
    )

    assert result == 0
    payload_path = tmp_path / "figures" / "FIG-G-02_prompt.json"
    placeholder_path = tmp_path / "figures" / "FIG-G-02_placeholder.md"
    payload = json.loads(payload_path.read_text(encoding="utf-8"))
    placeholder = placeholder_path.read_text(encoding="utf-8")
    assert payload["lane"] == "C"
    assert payload["status"] == "placeholder"
    assert payload["generation"] == {
        "api_called": False,
        "provider": None,
        "model": None,
        "requires_user_authorization": True,
    }
    assert "不是数据证据" in payload["prompt"]
    assert "此处仅预留概念图槽位" in placeholder


def test_schematic_prompt_rejects_unsafe_figure_id(tmp_path: Path) -> None:
    module = _load_module(
        "schematic_prompt_unsafe",
        "skills/cumcm-diagram/scripts/schematic_prompt.py",
    )
    result = module.main(
        [
            "--workspace",
            str(tmp_path),
            "--figure-id",
            "../FIG-G-02",
            "--title",
            "标题",
            "--chapter",
            "2",
            "--purpose",
            "目的",
            "--element",
            "元素",
        ]
    )
    assert result == 2
    assert not (tmp_path / "figures").exists()


def test_profile_helpers_are_dependency_lazy_and_path_safe(tmp_path: Path) -> None:
    module = _load_module(
        "profile_data",
        "skills/cumcm-coding/scripts/profile_data.py",
    )
    source = tmp_path / "input.csv"
    source.write_text("x,y\n1,2\n", encoding="utf-8")
    assert module._safe_workspace_path(tmp_path, "input.csv", must_exist=True) == source
    with pytest.raises(ValueError, match="工作区相对路径"):
        module._safe_workspace_path(tmp_path, "../outside.csv", must_exist=False)


def test_profile_report_renders_required_sections() -> None:
    module = _load_module(
        "profile_data_report",
        "skills/cumcm-coding/scripts/profile_data.py",
    )
    report = module.render_report(
        {
            "source": "input/sample.csv",
            "n_rows": 5,
            "n_cols": 1,
            "columns": {
                "x": {
                    "type": "continuous",
                    "n_total": 5,
                    "n_null": 0,
                    "missing_rate": 0.0,
                    "n": 5,
                    "mean": 3.0,
                    "median": 3.0,
                    "sd": 1.58,
                    "min": 1.0,
                    "max": 5.0,
                    "n_outliers_iqr": 0,
                }
            },
            "correlations": [],
            "group_summary": None,
            "warnings": [],
            "chart_suggestions": ["连续变量分布：直方图"],
        }
    )
    for heading in ("## 列概况", "## 相关性", "## 异常与风险", "## 初步图型建议"):
        assert heading in report


def test_profile_workbook_report_renders_every_sheet() -> None:
    module = _load_module(
        "profile_data_workbook_report",
        "skills/cumcm-coding/scripts/profile_data.py",
    )
    sheet = {
        "source": "input/sample.xlsx",
        "n_rows": 1,
        "n_cols": 1,
        "columns": {
            "类型": {
                "type": "categorical",
                "n_total": 1,
                "n_null": 0,
                "missing_rate": 0.0,
                "n_unique": 1,
                "categories": [("高钾", 1)],
            }
        },
        "correlations": [],
        "group_summary": None,
        "warnings": [],
        "chart_suggestions": ["先核对样本量"],
    }
    report = module.render_workbook_report(
        {
            "source": "input/sample.xlsx",
            "sheet_count": 2,
            "sheets": {"表单1": sheet, "表单2": sheet},
        }
    )

    assert "# 数据剖析报告" in report
    assert "## 工作表：表单1" in report
    assert "## 工作表：表单2" in report
    assert report.count("### 列概况") == 2
