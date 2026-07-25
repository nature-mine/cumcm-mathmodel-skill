from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "cumcm-review" / "scripts" / "check_references.py"

VALID_DOCUMENT = """\
# 测试论文

期刊方法见文献[1]，专著、学位论文和在线来源见文献[2-4]。

## 参考文献

[1] 张三. 示例算法研究[J]. 系统工程, 2020, 1(2): 1-8.
[2] 李四. 示例建模方法[M]. 北京: 科学出版社, 2019.
[3] 王五. 示例优化模型[D]. 上海: 示例大学, 2021.
[4] 示例机构. 示例标准页面[EB/OL]. (2024-01-01)[2026-07-24]. https://example.com/page.
"""


def _load_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("check_references", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _codes(report: dict[str, object]) -> set[str]:
    findings = report["findings"]
    assert isinstance(findings, list)
    return {str(finding["code"]) for finding in findings}


def test_valid_gbt_structure_and_citation_mapping_pass() -> None:
    module = _load_module()
    report = module.analyze_document(VALID_DOCUMENT, document="valid.md")
    assert report["valid"] is True
    assert report["reference_count"] == 4
    assert report["citation_numbers"] == [1, 2, 3, 4]
    assert _codes(report) == {"W_REFERENCE_COUNT"}


def test_ai_tool_entry_uses_official_special_shape_and_need_not_be_cited() -> None:
    module = _load_module()
    document = VALID_DOCUMENT.replace(
        "https://example.com/page.\n",
        ("https://example.com/page.\n[5] ChatGPT, GPT-5, OpenAI, 2026年7月24日\n"),
    )
    report = module.analyze_document(document)
    assert report["valid"] is True
    entries = report["entries"]
    assert isinstance(entries, list)
    assert entries[-1]["type_marker"] == "AI"


def test_injected_format_and_number_errors_are_caught() -> None:
    module = _load_module()
    broken = """\
# 错误样例

正文引用[1-2]。

## 参考文献

[1] 张三. 缺类型条目. 某期刊, 2020.
[3] 李四. 在线条目[EB/OL]. (2024-01-01). https://example.com.
"""
    report = module.analyze_document(broken)
    assert report["valid"] is False
    assert {
        "E_TYPE_MISSING",
        "E_NUMBER_SEQUENCE",
        "E_CITATION_UNLISTED",
        "E_REFERENCE_UNCITED",
        "E_ONLINE_ACCESS_DATE",
    } <= _codes(report)


def test_reference_checker_ignores_calendar_date_as_citation() -> None:
    module = _load_module()
    document = VALID_DOCUMENT.replace("# 测试论文", "# 测试论文\n\n核验日期[2026-07-24]。")
    report = module.analyze_document(document)
    assert report["valid"] is True
    assert report["citation_numbers"] == [1, 2, 3, 4]


def test_cli_returns_zero_for_valid_and_one_for_invalid(tmp_path: Path) -> None:
    module = _load_module()
    (tmp_path / "valid.md").write_text(VALID_DOCUMENT, encoding="utf-8")
    (tmp_path / "invalid.md").write_text("# 无参考文献\n", encoding="utf-8")
    assert module.main(["--workspace", str(tmp_path), "valid.md"]) == 0
    assert module.main(["--workspace", str(tmp_path), "invalid.md"]) == 1


def test_checker_rejects_path_escape(tmp_path: Path) -> None:
    module = _load_module()
    with pytest.raises(ValueError, match="工作区相对路径"):
        module._safe_document_path(tmp_path, "../paper.md")
