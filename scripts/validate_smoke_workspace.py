#!/usr/bin/env python3
"""Validate an external M5 end-to-end smoke workspace."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import stat
import sys
import zipfile
from collections.abc import Callable
from pathlib import Path
from typing import Any

PACK_ROOT = Path(__file__).resolve().parents[1]
REQUIRED_FILES = (
    "env_report.md",
    "env_report.json",
    "plan.md",
    "todo.md",
    "data_profile.md",
    "data_profile.json",
    "ai_usage_log.md",
    "evidence/ledger.md",
    "figure_registry.md",
    "results/run-log.md",
    "results/summary.json",
    "paper/paper.md",
    "paper/cumcm-paper.docx",
    "paper/cumcm-paper.pdf",
    "paper/support_manifest.json",
    "support/AI工具使用详情.md",
    "support/AI工具使用详情.docx",
    "support/AI工具使用详情.pdf",
    "reviews/review_writing_round1.md",
    "reviews/final_seat_A_round1.md",
    "reviews/final_seat_B_round1.md",
    "reviews/final_seat_C_round1.md",
    "reviews/final_summary_round1.md",
)
WRITE_BITS = stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH
MAX_ELECTRONIC_FILE_BYTES = 20 * 1024 * 1024
CHINESE_INTERNAL_WORKFLOW_TERMS = ("派发", "冻结", "里程碑", "车道", "占位槽")
ENGLISH_INTERNAL_WORKFLOW_PATTERN = re.compile(
    r"(?<![A-Za-z0-9_])(?:agent|prompt|P0)(?![A-Za-z0-9_])",
    re.IGNORECASE,
)
DIRECTIVE_PATTERN = re.compile(r"^\s*\[\[(FIGURE|PLACEHOLDER)\s+(.+)\]\]\s*$")
DIRECTIVE_FIELD_PATTERN = re.compile(r'([A-Za-z_][A-Za-z0-9_-]*)="([^"]*)"')
NUMBERED_HEADING_PATTERN = re.compile(r"^#{2,6}\s+(\d+(?:\.\d+)*)\b")


class SmokeValidationFailure(Exception):
    """Raised when an M5 smoke acceptance condition is not met."""


def _load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeError) as error:
        raise SmokeValidationFailure(f"{path.name} 不是有效 UTF-8 JSON") from error
    if not isinstance(payload, dict):
        raise SmokeValidationFailure(f"{path.name} 顶层必须是对象")
    return payload


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _require_external_workspace(workspace: Path) -> str:
    workspace = workspace.resolve()
    if not workspace.is_dir():
        raise SmokeValidationFailure(f"冒烟工作区不存在：{workspace}")
    try:
        workspace.relative_to(PACK_ROOT)
    except ValueError:
        return f"包外工作区：{workspace}"
    raise SmokeValidationFailure("M5 冒烟工作区必须位于 Skill 包外")


def _require_files(workspace: Path) -> str:
    missing = [relative for relative in REQUIRED_FILES if not (workspace / relative).is_file()]
    phase_patterns = {
        "contracts/*.md": 6,
        "reports/analysis_modeling_*.md": 4,
        "reports/code_feedback_*.md": 1,
        "reviews/review_model_*.md": 4,
        "reviews/review_code_*.md": 1,
        "code/*.py": 1,
    }
    phase_counts = {
        pattern: len(list(workspace.glob(pattern))) for pattern in phase_patterns
    }
    missing.extend(
        f"{pattern}（至少 {minimum}）"
        for pattern, minimum in phase_patterns.items()
        if phase_counts[pattern] < minimum
    )
    if missing:
        raise SmokeValidationFailure("缺少 M5 交付件：" + ", ".join(missing))
    return (
        f"{len(REQUIRED_FILES)} 个固定交付件存在；"
        f"建模/代码评审={phase_counts['reviews/review_model_*.md']}/"
        f"{phase_counts['reviews/review_code_*.md']}"
    )


def _validate_inputs(
    workspace: Path,
    problem_source: Path | None,
    attachment_source: Path | None,
) -> str:
    input_files = sorted(path for path in (workspace / "input").iterdir() if path.is_file())
    if len(input_files) != 2:
        raise SmokeValidationFailure(f"input/ 应只含题面和附件两个文件，实际 {len(input_files)}")
    for path in input_files:
        if stat.S_IMODE(path.stat().st_mode) & WRITE_BITS:
            raise SmokeValidationFailure(f"输入副本仍可写：{path.name}")

    pairs = (
        ("题面", problem_source),
        ("附件", attachment_source),
    )
    for label, source in pairs:
        if source is None:
            continue
        source = source.resolve()
        if not source.is_file():
            raise SmokeValidationFailure(f"{label}源文件不存在：{source}")
        target = workspace / "input" / source.name
        if not target.is_file():
            raise SmokeValidationFailure(f"input/ 缺少与{label}源同名的只读副本：{source.name}")
        if _sha256(source) != _sha256(target):
            raise SmokeValidationFailure(f"{label}源文件与冒烟副本 SHA-256 不一致")
    return "2 个输入副本均只读，已提供源文件的 SHA-256 一致"


def _validate_environment(workspace: Path) -> str:
    payload = _load_json(workspace / "env_report.json")
    if payload.get("overall_status") != "OK":
        raise SmokeValidationFailure("env_report overall_status 不是 OK")
    tiers = payload.get("tiers")
    if not isinstance(tiers, dict) or not isinstance(tiers.get("tier0"), dict):
        raise SmokeValidationFailure("env_report 缺少 tiers.tier0")
    summary = tiers["tier0"].get("summary")
    if not isinstance(summary, dict):
        raise SmokeValidationFailure("env_report 缺少 Tier 0 汇总")
    if summary.get("ok") != summary.get("total") or summary.get("miss") != 0:
        raise SmokeValidationFailure("Tier 0 未全部通过")
    return f"环境 overall=OK，Tier 0={summary.get('ok')}/{summary.get('total')}"


def _validate_profile(workspace: Path, expected_sheet_count: int) -> str:
    payload = _load_json(workspace / "data_profile.json")
    sheets = payload.get("sheets")
    if payload.get("sheet_count") != expected_sheet_count:
        raise SmokeValidationFailure(
            f"数据剖析工作表数应为 {expected_sheet_count}，实际 {payload.get('sheet_count')}"
        )
    if not isinstance(sheets, dict) or len(sheets) != expected_sheet_count:
        raise SmokeValidationFailure("data_profile.sheets 与 sheet_count 不一致")
    invalid = [
        name
        for name, sheet in sheets.items()
        if not isinstance(sheet, dict)
        or not isinstance(sheet.get("n_rows"), int)
        or not isinstance(sheet.get("n_cols"), int)
    ]
    if invalid:
        raise SmokeValidationFailure(f"工作表剖析缺少行列统计：{invalid}")
    return f"XLSX 全表剖析 {expected_sheet_count}/{expected_sheet_count}"


def _validate_paper_language(workspace: Path) -> str:
    paper = workspace / "paper/paper.md"
    findings: list[str] = []
    for line_number, line in enumerate(paper.read_text(encoding="utf-8").splitlines(), 1):
        directive = DIRECTIVE_PATTERN.fullmatch(line)
        if directive is not None and directive.group(1) == "PLACEHOLDER":
            continue
        for term in CHINESE_INTERNAL_WORKFLOW_TERMS:
            if term in line:
                findings.append(f"第 {line_number} 行 `{term}`")
        findings.extend(
            f"第 {line_number} 行 `{match.group(0)}`"
            for match in ENGLISH_INTERNAL_WORKFLOW_PATTERN.finditer(line)
        )
    if findings:
        raise SmokeValidationFailure("论文正文泄漏内部流程词：" + "；".join(findings))
    return "论文正文未泄漏内部流程词（合法 PLACEHOLDER 指令已豁免）"


def _parse_registry_rows(path: Path) -> dict[str, dict[str, str]]:
    columns: list[str] | None = None
    rows: dict[str, dict[str, str]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.lstrip().startswith("|"):
            continue
        cells = [cell.strip().strip("`") for cell in line.strip().strip("|").split("|")]
        if columns is None:
            if {"id", "chapter", "path"}.issubset(cells):
                columns = cells
            continue
        if not cells or all(set(cell) <= {"-", ":"} for cell in cells):
            continue
        if len(cells) != len(columns):
            raise SmokeValidationFailure("figure_registry.md 存在列数不一致的登记行")
        row = dict(zip(columns, cells, strict=True))
        figure_id = row.get("id", "")
        if not figure_id.startswith("FIG-"):
            continue
        if figure_id in rows:
            raise SmokeValidationFailure(f"figure_registry.md 重复登记：{figure_id}")
        rows[figure_id] = row
    if columns is None:
        raise SmokeValidationFailure("figure_registry.md 缺少 id/chapter/path 表头")
    return rows


def _read_declared_placeholder_chapter(path: Path) -> str | None:
    if path.suffix.lower() != ".md" or not path.is_file():
        return None
    match = re.search(
        r"^\s*-\s*拟放章节[：:]\s*(\S.*?)\s*$",
        path.read_text(encoding="utf-8"),
        re.MULTILINE,
    )
    return match.group(1).strip() if match is not None else None


def _validate_figure_chapters(workspace: Path) -> str:
    registry_rows = _parse_registry_rows(workspace / "figure_registry.md")
    current_chapter: str | None = None
    placements: list[tuple[str, str, str, dict[str, str]]] = []
    for line in (workspace / "paper/paper.md").read_text(encoding="utf-8").splitlines():
        heading = NUMBERED_HEADING_PATTERN.match(line)
        if heading is not None:
            current_chapter = heading.group(1)
        directive = DIRECTIVE_PATTERN.fullmatch(line)
        if directive is None:
            continue
        fields = dict(DIRECTIVE_FIELD_PATTERN.findall(directive.group(2)))
        figure_id = fields.get("id")
        if figure_id is None:
            raise SmokeValidationFailure(f"{directive.group(1)} 指令缺少 id")
        if current_chapter is None:
            raise SmokeValidationFailure(f"{figure_id} 位于首个编号章节之前")
        placements.append((figure_id, current_chapter, directive.group(1), fields))

    failures: list[str] = []
    for figure_id, paper_chapter, kind, fields in placements:
        registry = registry_rows.get(figure_id)
        if registry is None:
            failures.append(f"{figure_id} 未登记")
            continue
        registry_chapter = registry["chapter"]
        if registry_chapter != paper_chapter:
            failures.append(
                f"{figure_id} 登记章节={registry_chapter}、正文章节={paper_chapter}"
            )
        if kind != "PLACEHOLDER":
            continue
        directive_chapter = fields.get("chapter")
        if directive_chapter != paper_chapter:
            failures.append(
                f"{figure_id} 指令章节={directive_chapter or '缺失'}、正文章节={paper_chapter}"
            )
        relative_path = Path(registry["path"])
        if relative_path.is_absolute() or ".." in relative_path.parts:
            failures.append(f"{figure_id} path 不是安全相对路径：{relative_path}")
            continue
        placeholder_path = workspace / relative_path
        declared_chapter = _read_declared_placeholder_chapter(placeholder_path)
        if declared_chapter is not None and declared_chapter != paper_chapter:
            failures.append(
                f"{figure_id} 占位说明章节={declared_chapter}、正文章节={paper_chapter}"
            )
        prompt_path = placeholder_path.with_name(f"{figure_id}_prompt.json")
        if prompt_path.is_file():
            prompt_chapter = _load_json(prompt_path).get("chapter")
            if str(prompt_chapter) != paper_chapter:
                failures.append(
                    f"{figure_id} prompt 章节={prompt_chapter}、正文章节={paper_chapter}"
                )
    if failures:
        raise SmokeValidationFailure("图表章节不一致：" + "；".join(failures))
    return f"正文 {len(placements)} 个图表指令与 registry/占位材料章节一致"


def _validate_results_and_evidence(workspace: Path) -> str:
    summary = _load_json(workspace / "results/summary.json")
    required_summary = {
        "valid_classified_samples",
        "valid_artifacts",
        "unknown_samples",
        "q1",
        "q2",
        "q3",
        "q4",
    }
    missing = sorted(required_summary - summary.keys())
    if missing:
        raise SmokeValidationFailure(f"results/summary.json 缺少字段：{missing}")

    ledger = (workspace / "evidence/ledger.md").read_text(encoding="utf-8")
    evidence_rows = re.findall(r"^\|\s*E-[^|]+\|.*$", ledger, re.MULTILINE)
    if len(evidence_rows) < 4 or any("| frozen |" not in row for row in evidence_rows):
        raise SmokeValidationFailure("证据账本应至少含 4 条且全部为 frozen")

    registry = (workspace / "figure_registry.md").read_text(encoding="utf-8")
    lane_a = re.findall(r"^\|\s*FIG-[^|]+\|\s*A\s*\|.*\|\s*done\s*\|", registry, re.MULTILINE)
    lane_b = re.findall(r"^\|\s*FIG-[^|]+\|\s*B\s*\|.*\|\s*draft\s*\|", registry, re.MULTILINE)
    lane_c = re.findall(
        r"^\|\s*FIG-[^|]+\|\s*C\s*\|.*\|\s*placeholder\s*\|",
        registry,
        re.MULTILINE,
    )
    if not lane_a or not lane_b or not lane_c:
        raise SmokeValidationFailure("figure_registry 未同时闭合 A=done、B=draft、C=placeholder")
    return (
        f"结果四问齐全；evidence={len(evidence_rows)} 条 frozen；"
        f"figures A/B/C={len(lane_a)}/{len(lane_b)}/{len(lane_c)}"
    )


def _validate_manifest_and_docx(workspace: Path) -> str:
    payload = _load_json(workspace / "paper/support_manifest.json")
    entries = payload.get("entries")
    if not isinstance(entries, list) or not entries:
        raise SmokeValidationFailure("支撑材料清单为空")

    categories: dict[str, list[bool]] = {}
    for entry in entries:
        if not isinstance(entry, dict):
            raise SmokeValidationFailure("支撑材料清单条目必须是对象")
        relative = entry.get("path")
        category = entry.get("category")
        included = entry.get("included")
        recorded_hash = entry.get("sha256")
        if (
            not isinstance(relative, str)
            or not isinstance(category, str)
            or not isinstance(included, bool)
            or not isinstance(recorded_hash, str)
        ):
            raise SmokeValidationFailure("支撑材料清单条目字段无效")
        path = (workspace / relative).resolve()
        try:
            path.relative_to(workspace.resolve())
        except ValueError as error:
            raise SmokeValidationFailure(f"清单路径越出工作区：{relative}") from error
        if not path.is_file() or _sha256(path) != recorded_hash:
            raise SmokeValidationFailure(f"清单文件缺失或 SHA-256 不一致：{relative}")
        categories.setdefault(category, []).append(included)

    for category in ("data", "code", "support"):
        if category not in categories or categories[category] != [True] * len(
            categories[category]
        ):
            raise SmokeValidationFailure(f"清单中的 {category}/ 必须全部纳入")
    if "input" not in categories or categories["input"] != [False] * len(
        categories["input"]
    ):
        raise SmokeValidationFailure("清单中的 input/ 必须全部排除")

    docx = workspace / "paper/cumcm-paper.docx"
    pdf = workspace / "paper/cumcm-paper.pdf"
    if docx.stat().st_size > MAX_ELECTRONIC_FILE_BYTES:
        raise SmokeValidationFailure("论文 DOCX 超过 20 MiB")
    if pdf.stat().st_size > MAX_ELECTRONIC_FILE_BYTES:
        raise SmokeValidationFailure("论文 PDF 超过 20 MiB")
    try:
        with zipfile.ZipFile(docx) as archive:
            document_xml = archive.read("word/document.xml").decode("utf-8")
            footer_xml = archive.read("word/footer1.xml").decode("utf-8")
    except (KeyError, UnicodeError, zipfile.BadZipFile) as error:
        raise SmokeValidationFailure("论文 DOCX 结构无效") from error
    if "源程序：" not in document_xml or " PAGE " not in footer_xml:
        raise SmokeValidationFailure("论文 DOCX 缺少完整源程序附录或 PAGE 域")
    return (
        f"manifest input 排除、data/code/support 纳入；"
        f"DOCX={docx.stat().st_size} B，PDF={pdf.stat().st_size} B"
    )


def _validate_reviews_and_status(workspace: Path) -> str:
    final_summary = (workspace / "reviews/final_summary_round1.md").read_text(
        encoding="utf-8"
    )
    isolated_mode = (
        "review_mode: isolated_subagents" in final_summary
        or "三席上下文隔离" in final_summary
    )
    fallback_mode = (
        "review_mode: sequential_fallback" in final_summary
        or "三席非上下文隔离" in final_summary
    )
    if isolated_mode == fallback_mode:
        raise SmokeValidationFailure(
            "最终评审汇总必须且只能声明 isolated_subagents 或 sequential_fallback"
        )

    for seat in ("A", "B", "C"):
        text = (workspace / f"reviews/final_seat_{seat}_round1.md").read_text(
            encoding="utf-8"
        )
        for token in ("submit_ready: yes", "## P0", "## P1"):
            if token not in text:
                raise SmokeValidationFailure(f"最终评审席 {seat} 缺少字段：{token}")
        if isolated_mode:
            if "reviewer: isolated" not in text:
                raise SmokeValidationFailure(f"隔离评审席 {seat} 未声明 reviewer: isolated")
            if "self-review, 独立性受限" in text:
                raise SmokeValidationFailure(f"隔离评审席 {seat} 错误标记为 self-review")
        elif "self-review, 独立性受限" not in text:
            raise SmokeValidationFailure(f"顺序降级评审席 {seat} 未披露独立性受限")

    for token in ("中位数总分", "P0 并集", "P1 并集"):
        if token not in final_summary:
            raise SmokeValidationFailure(f"最终评审汇总缺少：{token}")
    if final_summary.count("- 空。") < 2:
        raise SmokeValidationFailure("最终评审汇总的 P0/P1 并集未清空")

    todo = (workspace / "todo.md").read_text(encoding="utf-8")
    if re.search(r"\|\s*(?:pending|in_progress|ready_for_review)\s*\|", todo):
        raise SmokeValidationFailure("todo.md 仍有未冻结任务")
    if todo.count("| frozen |") < 8:
        raise SmokeValidationFailure("todo.md 的 frozen 任务数量不足")
    mode_label = "A/B/C 隔离评审" if isolated_mode else "A/B/C 顺序降级评审"
    return f"写作分步评审通过，{mode_label}与汇总齐全，任务全部冻结"


def validate_smoke_workspace(
    workspace: Path,
    *,
    problem_source: Path | None = None,
    attachment_source: Path | None = None,
    expected_sheet_count: int = 3,
) -> tuple[str, ...]:
    workspace = workspace.resolve()
    checks: tuple[Callable[[], str], ...] = (
        lambda: _require_external_workspace(workspace),
        lambda: _require_files(workspace),
        lambda: _validate_inputs(workspace, problem_source, attachment_source),
        lambda: _validate_environment(workspace),
        lambda: _validate_profile(workspace, expected_sheet_count),
        lambda: _validate_paper_language(workspace),
        lambda: _validate_results_and_evidence(workspace),
        lambda: _validate_figure_chapters(workspace),
        lambda: _validate_manifest_and_docx(workspace),
        lambda: _validate_reviews_and_status(workspace),
    )
    return tuple(check() for check in checks)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="验证包外 M5 端到端冒烟工作区")
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--problem-source", type=Path)
    parser.add_argument("--attachment-source", type=Path)
    parser.add_argument("--expected-sheet-count", type=int, default=3)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.expected_sheet_count < 1:
        print("FAIL：--expected-sheet-count 必须是正整数", file=sys.stderr)
        return 2
    try:
        messages = validate_smoke_workspace(
            args.workspace,
            problem_source=args.problem_source,
            attachment_source=args.attachment_source,
            expected_sheet_count=args.expected_sheet_count,
        )
    except (OSError, SmokeValidationFailure) as error:
        print(f"FAIL：{error}", file=sys.stderr)
        return 1
    for message in messages:
        print(f"PASS：{message}")
    print(f"M5 smoke validation passed：{len(messages)} 项检查全部通过")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
