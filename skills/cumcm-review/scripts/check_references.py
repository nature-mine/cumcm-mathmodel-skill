#!/usr/bin/env python3
"""Check bibliography structure and numeric citation correspondence in Markdown."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path

HEADING_PATTERN = re.compile(
    r"^(?P<marks>#{1,6})\s*(?:参考文献|references)\s*[:：]?\s*$",
    re.I,
)
ENTRY_PATTERN = re.compile(r"^\s*\[(?P<number>\d+)]\s*(?P<content>\S.*?)\s*$")
CITATION_PATTERN = re.compile(r"\[(?P<group>\d+(?:\s*(?:[,，;；]|[-–—])\s*\d+)*)\](?!\s*\()")
TYPE_PATTERN = re.compile(
    r"\[(?P<type>J(?:/OL)?|M(?:/OL)?|D|C|N|R|S|P|DB|CP|EB/OL)]",
    re.I,
)
YEAR_PATTERN = re.compile(r"(?<!\d)(?:18|19|20)\d{2}(?!\d)")
DATE_PATTERN = re.compile(
    r"(?:"
    r"(?:18|19|20)\d{2}[-/.]\d{1,2}[-/.]\d{1,2}"
    r"|(?:18|19|20)\d{2}年\d{1,2}月\d{1,2}日"
    r")"
)
URL_PATTERN = re.compile(r"https?://\S+", re.I)
ACCESS_DATE_PATTERN = re.compile(
    r"\[(?:"
    r"(?:18|19|20)\d{2}[-/.]\d{1,2}[-/.]\d{1,2}"
    r"|(?:18|19|20)\d{2}年\d{1,2}月\d{1,2}日"
    r")]"
)
FENCED_CODE_PATTERN = re.compile(r"```.*?```|~~~.*?~~~", re.DOTALL)
INLINE_CODE_PATTERN = re.compile(r"`[^`\n]+`")
AI_TOOL_PATTERN = re.compile(
    r"(?:AI|GPT|ChatGPT|Claude|Codex|Gemini|DeepSeek|模型|人工智能工具)",
    re.I,
)
MAX_CITATION_RANGE = 1000


@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    message: str
    line: int | None = None
    reference_number: int | None = None


@dataclass(frozen=True)
class ReferenceEntry:
    number: int
    content: str
    line: int
    type_marker: str | None
    is_ai_tool: bool


def _safe_document_path(workspace: Path, raw_path: str | Path) -> Path:
    candidate = Path(raw_path)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise ValueError(f"路径必须是工作区相对路径且不能包含 '..'：{raw_path}")
    root = workspace.resolve()
    resolved = (root / candidate).resolve()
    try:
        resolved.relative_to(root)
    except ValueError as error:
        raise ValueError(f"路径越出工作区：{raw_path}") from error
    if not resolved.is_file():
        raise ValueError(f"文档不存在：{raw_path}")
    return resolved


def _find_reference_section(lines: list[str]) -> tuple[int, int] | None:
    for index, line in enumerate(lines):
        match = HEADING_PATTERN.fullmatch(line.strip())
        if match is None:
            continue
        level = len(match.group("marks"))
        for end in range(index + 1, len(lines)):
            heading = re.match(r"^(#{1,6})\s+", lines[end])
            if heading is not None and len(heading.group(1)) <= level:
                return index + 1, end
        return index + 1, len(lines)
    return None


def _looks_like_ai_tool(content: str) -> bool:
    parts = [part.strip() for part in re.split(r"[,，]", content) if part.strip()]
    if len(parts) != 4 or AI_TOOL_PATTERN.search(content) is None:
        return False
    return DATE_PATTERN.search(parts[-1]) is not None


def _parse_reference_entries(
    lines: list[str],
    start: int,
    end: int,
) -> tuple[list[ReferenceEntry], list[Finding]]:
    entries: list[ReferenceEntry] = []
    findings: list[Finding] = []
    for index in range(start, end):
        raw_line = lines[index]
        line = raw_line.strip()
        if not line or line == "---":
            continue
        match = ENTRY_PATTERN.fullmatch(raw_line)
        if match is None:
            findings.append(
                Finding(
                    "error",
                    "E_REFERENCE_LINE",
                    "参考文献区存在未按“[编号] 条目”单行书写的内容",
                    line=index + 1,
                )
            )
            continue

        content = match.group("content").strip()
        type_match = TYPE_PATTERN.search(content)
        marker = type_match.group("type").upper() if type_match else None
        is_ai_tool = marker is None and _looks_like_ai_tool(content)
        entries.append(
            ReferenceEntry(
                number=int(match.group("number")),
                content=content,
                line=index + 1,
                type_marker="AI" if is_ai_tool else marker,
                is_ai_tool=is_ai_tool,
            )
        )
    return entries, findings


def _entry_finding(
    entry: ReferenceEntry,
    code: str,
    message: str,
) -> Finding:
    return Finding(
        "error",
        code,
        message,
        line=entry.line,
        reference_number=entry.number,
    )


def _validate_ai_tool_entry(entry: ReferenceEntry) -> list[Finding]:
    parts = [part.strip() for part in re.split(r"[,，]", entry.content) if part.strip()]
    findings: list[Finding] = []
    if len(parts) < 4:
        findings.append(
            _entry_finding(
                entry,
                "E_AI_TOOL_FIELDS",
                "AI 工具条目至少需要工具名称、版本/型号、开发机构和使用日期",
            )
        )
    if DATE_PATTERN.search(parts[-1]) is None:
        findings.append(_entry_finding(entry, "E_AI_TOOL_DATE", "AI 工具条目缺少使用日期"))
    return findings


def _validate_online_fields(entry: ReferenceEntry) -> list[Finding]:
    findings: list[Finding] = []
    if URL_PATTERN.search(entry.content) is None:
        findings.append(_entry_finding(entry, "E_ONLINE_URL", "在线文献缺少 HTTP(S) URL"))
    if ACCESS_DATE_PATTERN.search(entry.content) is None:
        findings.append(
            _entry_finding(
                entry,
                "E_ONLINE_ACCESS_DATE",
                "在线文献缺少方括号形式的引用日期",
            )
        )
    return findings


def _validate_entry_structure(entry: ReferenceEntry) -> list[Finding]:
    if entry.is_ai_tool:
        return _validate_ai_tool_entry(entry)

    findings: list[Finding] = []
    type_match = TYPE_PATTERN.search(entry.content)
    if type_match is None:
        return [
            _entry_finding(
                entry,
                "E_TYPE_MISSING",
                "缺少或不支持文献类型标识，如 [J]、[M]、[D]、[EB/OL]",
            )
        ]

    prefix = entry.content[: type_match.start()].strip().rstrip(".。")
    prefix_parts = [part.strip() for part in re.split(r"[.。]", prefix) if part.strip()]
    if len(prefix_parts) < 2:
        findings.append(
            _entry_finding(
                entry,
                "E_AUTHOR_TITLE",
                "类型标识前应至少包含责任者和题名，并以句点分隔",
            )
        )

    suffix = entry.content[type_match.end() :].strip()
    if not suffix.startswith((".", "。")):
        findings.append(
            _entry_finding(
                entry,
                "E_MARKER_PUNCTUATION",
                "文献类型标识后应使用句点连接出处字段",
            )
        )
    if not entry.content.endswith((".", "。")):
        findings.append(_entry_finding(entry, "E_TERMINAL_PUNCTUATION", "条目末尾缺少句点"))
    if YEAR_PATTERN.search(entry.content) is None:
        findings.append(_entry_finding(entry, "E_YEAR_MISSING", "条目缺少四位年份"))

    marker = type_match.group("type").upper()
    source_fields = suffix.lstrip(".。").strip()
    if marker.startswith("J"):
        if not re.search(r"[^,，.。]+[,，]\s*(?:18|19|20)\d{2}", source_fields):
            findings.append(
                _entry_finding(
                    entry,
                    "E_JOURNAL_FIELDS",
                    "期刊条目应在 [J] 后包含期刊名和年份",
                )
            )
    elif marker.startswith("M") or marker == "D":
        if ":" not in source_fields and "：" not in source_fields:
            findings.append(
                _entry_finding(
                    entry,
                    "E_PUBLICATION_FIELDS",
                    "专著/学位论文应包含“出版地: 出版者/机构”字段",
                )
            )
    if marker.endswith("/OL"):
        findings.extend(_validate_online_fields(entry))
    return findings


def _expand_citation_group(group: str) -> tuple[set[int], list[str]]:
    numbers: set[int] = set()
    errors: list[str] = []
    for token in re.split(r"[,，;；]", group):
        token = token.strip()
        if token.isdigit():
            numbers.add(int(token))
            continue
        range_match = re.fullmatch(r"(\d+)\s*[-–—]\s*(\d+)", token)
        if range_match is None:
            errors.append(f"无法解析引用组 [{token}]")
            continue
        start, end = (int(value) for value in range_match.groups())
        if end < start:
            errors.append(f"倒序引用范围 [{token}]")
            continue
        if end - start > MAX_CITATION_RANGE:
            errors.append(f"引用范围过大 [{token}]")
            continue
        numbers.update(range(start, end + 1))
    return numbers, errors


def _extract_citations(body: str) -> tuple[set[int], list[Finding]]:
    cleaned = FENCED_CODE_PATTERN.sub("", body)
    cleaned = INLINE_CODE_PATTERN.sub("", cleaned)
    citations: set[int] = set()
    findings: list[Finding] = []
    for match in CITATION_PATTERN.finditer(cleaned):
        if re.fullmatch(r"\d{4}[-–—]\d{1,2}[-–—]\d{1,2}", match.group("group")):
            continue
        numbers, errors = _expand_citation_group(match.group("group"))
        citations.update(numbers)
        findings.extend(Finding("error", "E_CITATION_RANGE", message) for message in errors)
    return citations, findings


def _validate_numbering(entries: list[ReferenceEntry]) -> list[Finding]:
    findings: list[Finding] = []
    numbers = [entry.number for entry in entries]
    counts = Counter(numbers)
    for number, count in sorted(counts.items()):
        if count > 1:
            findings.append(
                Finding(
                    "error",
                    "E_NUMBER_DUPLICATE",
                    f"参考文献编号 [{number}] 重复 {count} 次",
                    reference_number=number,
                )
            )
    expected = list(range(1, len(entries) + 1))
    if numbers != expected:
        findings.append(
            Finding(
                "error",
                "E_NUMBER_SEQUENCE",
                f"参考文献编号应按 1..{len(entries)} 连续排列，实际为 {numbers}",
            )
        )
    return findings


def analyze_document(text: str, *, document: str = "<memory>") -> dict[str, object]:
    """Analyze one Markdown document and return a JSON-serializable report."""
    lines = text.splitlines()
    section = _find_reference_section(lines)
    if section is None:
        finding = Finding("error", "E_SECTION_MISSING", "未找到“参考文献”标题")
        return {
            "document": document,
            "valid": False,
            "reference_count": 0,
            "citation_numbers": [],
            "entries": [],
            "findings": [asdict(finding)],
        }

    start, end = section
    entries, findings = _parse_reference_entries(lines, start, end)
    if not entries:
        findings.append(Finding("error", "E_REFERENCE_EMPTY", "参考文献区没有可解析条目"))

    findings.extend(_validate_numbering(entries))
    for entry in entries:
        findings.extend(_validate_entry_structure(entry))

    body = "\n".join([*lines[: start - 1], *lines[end:]])
    citations, citation_findings = _extract_citations(body)
    findings.extend(citation_findings)
    listed = {entry.number for entry in entries}
    ai_numbers = {entry.number for entry in entries if entry.is_ai_tool}
    for number in sorted(citations - listed):
        findings.append(
            Finding(
                "error",
                "E_CITATION_UNLISTED",
                f"正文引用 [{number}]，但文末没有对应条目",
                reference_number=number,
            )
        )
    for number in sorted(listed - citations - ai_numbers):
        findings.append(
            Finding(
                "error",
                "E_REFERENCE_UNCITED",
                f"文末条目 [{number}] 未在正文引用",
                reference_number=number,
            )
        )
    if 0 < len(entries) < 8:
        findings.append(
            Finding(
                "warning",
                "W_REFERENCE_COUNT",
                f"当前 {len(entries)} 篇；8 篇只是常见建议值，方法创新型可少，不作机械失败",
            )
        )

    serialized_findings = [asdict(finding) for finding in findings]
    return {
        "document": document,
        "valid": not any(finding.severity == "error" for finding in findings),
        "reference_count": len(entries),
        "citation_numbers": sorted(citations),
        "entries": [asdict(entry) for entry in entries],
        "findings": serialized_findings,
    }


def render_report(report: dict[str, object]) -> str:
    """Render a concise deterministic CLI report."""
    status = "PASS" if report["valid"] else "FAIL"
    lines = [
        f"Reference check: {status}",
        f"Document: {report['document']}",
        f"References: {report['reference_count']}",
        "Citations: " + ", ".join(str(value) for value in report["citation_numbers"]),
    ]
    findings = report["findings"]
    assert isinstance(findings, list)
    if not findings:
        lines.append("Findings: none")
        return "\n".join(lines)
    lines.append("Findings:")
    for raw_finding in findings:
        assert isinstance(raw_finding, dict)
        location_parts = []
        if raw_finding["line"] is not None:
            location_parts.append(f"line {raw_finding['line']}")
        if raw_finding["reference_number"] is not None:
            location_parts.append(f"ref {raw_finding['reference_number']}")
        location = f" ({', '.join(location_parts)})" if location_parts else ""
        lines.append(
            f"- {str(raw_finding['severity']).upper()} "
            f"{raw_finding['code']}{location}: {raw_finding['message']}"
        )
    return "\n".join(lines)


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="检查 Markdown 参考文献结构与正文数字引用对应关系")
    parser.add_argument("document", help="相对于工作区的 Markdown 文档")
    parser.add_argument("--workspace", default=".", help="竞赛工作区，默认当前目录")
    parser.add_argument("--json", action="store_true", help="输出 JSON 报告")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    try:
        path = _safe_document_path(Path(args.workspace), args.document)
        report = analyze_document(
            path.read_text(encoding="utf-8"),
            document=str(Path(args.document)),
        )
    except (OSError, UnicodeError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(render_report(report))
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
