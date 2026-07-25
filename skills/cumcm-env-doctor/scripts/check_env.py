#!/usr/bin/env python3
"""Deterministically inspect a CUMCM contest workspace environment."""

from __future__ import annotations

import argparse
import importlib.metadata
import importlib.util
import json
import platform
import re
import shutil
import subprocess
import sys
from collections import Counter
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

PACK_ROOT = Path(__file__).resolve().parents[3]
REPORT_JSON = "env_report.json"
REPORT_MARKDOWN = "env_report.md"
MINIMUM_PYTHON = (3, 10)
EXPECTED_SKILLS = (
    "cumcm-coding",
    "cumcm-diagram",
    "cumcm-env-doctor",
    "cumcm-hub",
    "cumcm-modeling",
    "cumcm-review",
    "cumcm-writing",
)
TIER0_PACKAGES = (
    ("numpy", "numpy", "NumPy", "uv add numpy"),
    ("pandas", "pandas", "pandas", "uv add pandas"),
    ("scipy", "scipy", "SciPy", "uv add scipy"),
    ("matplotlib", "matplotlib", "Matplotlib", "uv add matplotlib"),
    ("openpyxl", "openpyxl", "openpyxl", "uv add openpyxl"),
    ("docx", "python-docx", "python-docx", "uv add python-docx"),
)
TIER1_PACKAGES = (
    ("sklearn", "scikit-learn", "scikit-learn", "uv add scikit-learn"),
    ("statsmodels", "statsmodels", "statsmodels", "uv add statsmodels"),
    ("networkx", "networkx", "NetworkX", "uv add networkx"),
    ("pulp", "PuLP", "PuLP", "uv add pulp"),
    ("ortools", "ortools", "OR-Tools", "uv add ortools"),
    ("scipy.optimize", "scipy", "SciPy optimize", "uv add scipy"),
    ("seaborn", "seaborn", "seaborn", "uv add seaborn"),
)
CJK_FONT_CANDIDATES = (
    "Noto Sans CJK SC",
    "Noto Serif CJK SC",
    "Source Han Sans SC",
    "Source Han Serif SC",
    "SimHei",
    "Microsoft YaHei",
    "微软雅黑",
)
CHANNEL_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]{0,79}$")
FRONTMATTER_NAME_PATTERN = re.compile(r"^name:\s*[\"']?([^\"'\n]+)[\"']?\s*$", re.MULTILINE)


@dataclass(frozen=True)
class Check:
    """One environment check result."""

    key: str
    label: str
    status: str
    detail: str
    install: str


def _existing_directory(value: str) -> Path:
    path = Path(value).expanduser()
    try:
        resolved = path.resolve(strict=True)
    except OSError as error:
        raise argparse.ArgumentTypeError(f"目录不存在或不可访问：{value}") from error
    if not resolved.is_dir():
        raise argparse.ArgumentTypeError(f"不是目录：{value}")
    return resolved


def _network_channel(value: str) -> str:
    channel = value.strip()
    if not CHANNEL_PATTERN.fullmatch(channel):
        raise argparse.ArgumentTypeError(
            "联网通路名只能含字母、数字、点、下划线、冒号、斜线或连字符，最长 80 字符"
        )
    return channel


def _python_check() -> Check:
    version = platform.python_version()
    if sys.version_info >= MINIMUM_PYTHON:
        return Check("python", "Python ≥3.10", "OK", version, "")
    return Check(
        "python",
        "Python ≥3.10",
        "MISS",
        f"当前版本 {version}",
        "安装 Python 3.10 或更高版本",
    )


def _package_check(
    import_name: str,
    distribution_name: str,
    label: str,
    install: str,
) -> Check:
    try:
        available = importlib.util.find_spec(import_name) is not None
    except (ImportError, ModuleNotFoundError, ValueError):
        available = False
    if not available:
        return Check(import_name, label, "MISS", f"无法导入 {import_name}", install)

    try:
        version = importlib.metadata.version(distribution_name)
    except importlib.metadata.PackageNotFoundError:
        version = "版本未知"
    return Check(import_name, label, "OK", version, "")


def _environment_manager_check() -> Check:
    executable = shutil.which("uv")
    if executable:
        return Check("uv", "uv 环境管理器", "OK", executable, "")
    return Check(
        "uv",
        "uv 环境管理器",
        "DEGRADED",
        "未在 PATH 中找到 uv；可降级为 python -m venv",
        "curl -LsSf https://astral.sh/uv/install.sh | sh",
    )


def _validate_skill_pack(skill_pack_root: Path) -> Check:
    problems: list[str] = []
    for name in EXPECTED_SKILLS:
        skill_path = skill_pack_root / "skills" / name / "SKILL.md"
        if not skill_path.is_file():
            problems.append(f"缺少 {skill_path.relative_to(skill_pack_root)}")
            continue
        text = skill_path.read_text(encoding="utf-8")
        match = FRONTMATTER_NAME_PATTERN.search(text)
        if match is None or match.group(1).strip() != name:
            problems.append(f"{name}/SKILL.md 的 name 不匹配")

    if problems:
        return Check(
            "skill-pack",
            "CUMCM Skill 包",
            "MISS",
            "；".join(problems),
            "重新安装或修复 cumcm-mathmodel-skill",
        )
    return Check(
        "skill-pack",
        "CUMCM Skill 包",
        "OK",
        f"{len(EXPECTED_SKILLS)} 个 Skill 结构有效",
        "",
    )


def _tool_check(
    key: str,
    label: str,
    candidates: Sequence[str],
    install: str,
    fallback: str,
) -> Check:
    for candidate in candidates:
        executable = shutil.which(candidate)
        if executable:
            return Check(key, label, "OK", f"{candidate}: {executable}", "")
    return Check(key, label, "DEGRADED", fallback, install)


def _find_cjk_fonts() -> tuple[str, ...]:
    fc_list = shutil.which("fc-list")
    if not fc_list:
        return ()
    try:
        result = subprocess.run(
            [fc_list, ":", "family"],
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return ()
    if result.returncode != 0:
        return ()

    font_text = result.stdout.casefold()
    return tuple(candidate for candidate in CJK_FONT_CANDIDATES if candidate.casefold() in font_text)


def _font_check() -> Check:
    fonts = _find_cjk_fonts()
    if fonts:
        return Check("cjk-font", "CJK 字体", "OK", "、".join(fonts), "")
    return Check(
        "cjk-font",
        "CJK 字体",
        "DEGRADED",
        "未发现推荐中文字体；中文图可能出现方框",
        "Linux 可安装 fonts-noto-cjk；绘图设置 axes.unicode_minus=False",
    )


def _tier2_checks() -> list[Check]:
    return [
        _font_check(),
        _tool_check(
            "drawio",
            "draw.io",
            ("drawio", "draw.io"),
            "安装 draw.io Desktop",
            "保留 .drawio XML，使用网页版人工导出",
        ),
        _tool_check(
            "graphviz",
            "Graphviz dot",
            ("dot",),
            "安装 Graphviz",
            "改用 draw.io 或保留 .dot 源文件",
        ),
        _tool_check(
            "officecli",
            "OfficeCLI",
            ("officecli",),
            "查看 https://officecli.ai",
            "改用 LibreOffice + pdftoppm 或人工打开 DOCX",
        ),
        _tool_check(
            "libreoffice",
            "LibreOffice",
            ("soffice", "libreoffice"),
            "安装 LibreOffice",
            "优先使用 OfficeCLI；否则人工检查 DOCX",
        ),
        _tool_check(
            "pdftoppm",
            "pdftoppm",
            ("pdftoppm",),
            "Linux 可安装 poppler-utils",
            "优先使用 OfficeCLI；否则人工逐页检查",
        ),
    ]


def _count_status(checks: Sequence[Check]) -> dict[str, int]:
    counts = Counter(check.status for check in checks)
    return {
        "ok": counts["OK"],
        "miss": counts["MISS"],
        "degraded": counts["DEGRADED"],
        "total": len(checks),
    }


def build_report(
    workspace: Path,
    skill_pack_root: Path,
    network_channels: Sequence[str],
) -> dict[str, object]:
    """Collect all checks without writing files."""

    tier0 = [
        _python_check(),
        *(_package_check(*requirement) for requirement in TIER0_PACKAGES),
        _validate_skill_pack(skill_pack_root),
    ]
    tier1 = [_package_check(*requirement) for requirement in TIER1_PACKAGES]
    tier2 = _tier2_checks()
    unique_channels = list(dict.fromkeys(network_channels))
    network_status = "OK" if unique_channels else "DEGRADED"
    overall_status = "BLOCKED" if any(check.status == "MISS" for check in tier0) else "OK"

    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "workspace": str(workspace),
        "skill_pack_root": str(skill_pack_root),
        "overall_status": overall_status,
        "environment_manager": asdict(_environment_manager_check()),
        "tiers": {
            "tier0": {
                "blocking": True,
                "summary": _count_status(tier0),
                "checks": [asdict(check) for check in tier0],
            },
            "tier1": {
                "blocking": False,
                "summary": _count_status(tier1),
                "checks": [asdict(check) for check in tier1],
            },
            "tier2": {
                "blocking": False,
                "summary": _count_status(tier2),
                "checks": [asdict(check) for check in tier2],
            },
        },
        "network": {
            "status": network_status,
            "channels": unique_channels,
            "detail": (
                "宿主已实测至少一条联网通路"
                if unique_channels
                else "未收到可用通路；文献与赛制复核须人工完成"
            ),
        },
    }


def _escape_table(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def _render_check_table(checks: Sequence[dict[str, str]]) -> list[str]:
    lines = [
        "| 状态 | 检查项 | 详情 | 安装/降级建议 |",
        "|---|---|---|---|",
    ]
    for check in checks:
        lines.append(
            "| {status} | {label} | {detail} | {install} |".format(
                status=_escape_table(check["status"]),
                label=_escape_table(check["label"]),
                detail=_escape_table(check["detail"]),
                install=_escape_table(check["install"] or "—"),
            )
        )
    return lines


def render_markdown(report: dict[str, object]) -> str:
    """Render a human-readable Chinese report."""

    tiers = report["tiers"]
    assert isinstance(tiers, dict)
    manager = report["environment_manager"]
    assert isinstance(manager, dict)
    network = report["network"]
    assert isinstance(network, dict)

    lines = [
        "# CUMCM 环境报告",
        "",
        f"- 生成时间：{report['generated_at']}",
        f"- 工作区：`{report['workspace']}`",
        f"- Skill 包：`{report['skill_pack_root']}`",
        f"- 总状态：**{report['overall_status']}**",
        "",
        "## Step 0：环境管理器",
        "",
        *_render_check_table([manager]),
    ]

    for tier_name, title in (
        ("tier0", "Tier 0：硬性依赖"),
        ("tier1", "Tier 1：按题型依赖"),
        ("tier2", "Tier 2：系统工具"),
    ):
        tier = tiers[tier_name]
        assert isinstance(tier, dict)
        summary = tier["summary"]
        checks = tier["checks"]
        assert isinstance(summary, dict)
        assert isinstance(checks, list)
        lines.extend(
            [
                "",
                f"## {title}",
                "",
                (
                    f"OK {summary['ok']}/{summary['total']}；"
                    f"MISS {summary['miss']}；DEGRADED {summary['degraded']}。"
                ),
                "",
                *_render_check_table(checks),
            ]
        )

    channels = network["channels"]
    assert isinstance(channels, list)
    channel_text = "、".join(str(channel) for channel in channels) if channels else "无"
    lines.extend(
        [
            "",
            "## 联网能力",
            "",
            f"- 状态：**{network['status']}**",
            f"- 可用通路：{channel_text}",
            f"- 说明：{network['detail']}",
            "",
            "## Hub 判定",
            "",
        ]
    )
    if report["overall_status"] == "BLOCKED":
        lines.append("Tier 0 存在缺项，正式读题与建模必须停止；完成安装后重新运行检查。")
    else:
        lines.append("Tier 0 全部通过，可进入 hub startup lock；Tier 1/2 缺项按报告降级。")
    return "\n".join(lines) + "\n"


def _atomic_write(path: Path, content: str) -> None:
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(content, encoding="utf-8")
    temporary.replace(path)


def write_reports(report: dict[str, object], workspace: Path) -> tuple[Path, Path]:
    """Write fixed report names inside the resolved workspace."""

    json_path = workspace / REPORT_JSON
    markdown_path = workspace / REPORT_MARKDOWN
    _atomic_write(json_path, json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    _atomic_write(markdown_path, render_markdown(report))
    return markdown_path, json_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="检查 CUMCM 竞赛工作区环境")
    parser.add_argument(
        "--workspace",
        type=_existing_directory,
        default=Path.cwd().resolve(),
        help="已存在的竞赛工作区；报告固定写入其根目录",
    )
    parser.add_argument(
        "--skill-pack-root",
        type=_existing_directory,
        default=PACK_ROOT,
        help="cumcm-mathmodel-skill 根目录",
    )
    parser.add_argument(
        "--network-channel",
        action="append",
        default=[],
        type=_network_channel,
        help="宿主已实测可用的联网通路名，可重复",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    report = build_report(args.workspace, args.skill_pack_root, args.network_channel)
    markdown_path, json_path = write_reports(report, args.workspace)
    print(f"env_report.md: {markdown_path}")
    print(f"env_report.json: {json_path}")
    print(f"overall_status: {report['overall_status']}")
    return 0 if report["overall_status"] == "OK" else 1


if __name__ == "__main__":
    raise SystemExit(main())
