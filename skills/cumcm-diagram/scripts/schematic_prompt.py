#!/usr/bin/env python3
"""Create a lane-C concept prompt payload and a labeled placeholder.

Design informed by the Apache-2.0 licensed implementation:
  nature-skills/skills/nature-figure/scripts/generate_openrouter_schematic.py

This is a clean, API-free adaptation for CUMCM. It never reads credentials,
makes network requests, or generates an image. The output is provider-neutral
so the user can choose a generator later.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

FIGURE_ID_PATTERN = re.compile(r"^FIG-(?:P[1-9][0-9]*|G)-[0-9]{2,}$")


def _safe_path(workspace: Path, relative: str | Path) -> Path:
    candidate = Path(relative)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise ValueError(f"路径必须是工作区相对路径且不能包含 '..'：{relative}")
    root = workspace.resolve()
    resolved = (root / candidate).resolve()
    try:
        resolved.relative_to(root)
    except ValueError as error:
        raise ValueError(f"路径越出工作区：{relative}") from error
    return resolved


def _clean_items(items: list[str]) -> list[str]:
    cleaned = [item.strip() for item in items if item.strip()]
    if not cleaned:
        raise ValueError("至少提供一个非空 --element")
    return cleaned


def build_prompt(
    *,
    title: str,
    purpose: str,
    elements: list[str],
    relationships: list[str],
    exclusions: list[str],
    aspect_ratio: str,
) -> str:
    """Build a provider-neutral concept illustration prompt."""
    relationship_text = "；".join(relationships) if relationships else "按目的形成清晰主次"
    exclusion_text = "；".join(
        [
            "定量坐标和数据曲线",
            "无法核实的数字、p 值或实验结果",
            "机构 logo、奖项标识和身份信息",
            "长段文字与伪造引用",
            *exclusions,
        ]
    )
    return "\n".join(
        [
            "生成一张用于数学建模论文的概念示意图草稿；它不是数据证据。",
            f"标题：{title}",
            f"表达目的：{purpose}",
            f"画面元素：{'；'.join(elements)}",
            f"关系与构图：{relationship_text}",
            (
                "视觉要求：平面矢量感、白色背景、克制配色、层级清晰、短标签、"
                f"适合后续人工重绘，画幅 {aspect_ratio}。"
            ),
            f"禁止内容：{exclusion_text}",
            "只呈现已提供的实体和关系，不新增机制，不把概念画面伪装成计算或实验结果。",
        ]
    )


def build_payload(args: argparse.Namespace) -> dict[str, object]:
    elements = _clean_items(args.element)
    relationships = [item.strip() for item in args.relationship if item.strip()]
    exclusions = [item.strip() for item in args.exclude if item.strip()]
    return {
        "schema": "cumcm-concept-placeholder/v1",
        "figure_id": args.figure_id,
        "lane": "C",
        "status": "placeholder",
        "title": args.title.strip(),
        "chapter": args.chapter.strip(),
        "purpose": args.purpose.strip(),
        "aspect_ratio": args.aspect_ratio,
        "elements": elements,
        "relationships": relationships,
        "exclusions": exclusions,
        "prompt": build_prompt(
            title=args.title.strip(),
            purpose=args.purpose.strip(),
            elements=elements,
            relationships=relationships,
            exclusions=exclusions,
            aspect_ratio=args.aspect_ratio,
        ),
        "generation": {
            "api_called": False,
            "provider": None,
            "model": None,
            "requires_user_authorization": True,
        },
    }


def render_placeholder(payload: dict[str, object], prompt_path: str) -> str:
    elements = payload["elements"]
    assert isinstance(elements, list)
    return "\n".join(
        [
            f"# 概念图占位：{payload['figure_id']}",
            "",
            f"- 状态：`{payload['status']}`",
            f"- 车道：`{payload['lane']}`",
            f"- 拟放章节：{payload['chapter']}",
            f"- 图题：{payload['title']}",
            f"- 表达目的：{payload['purpose']}",
            f"- 期望元素：{'；'.join(str(item) for item in elements)}",
            f"- Prompt/payload：`{prompt_path}`",
            "",
            "> 此处仅预留概念图槽位，不是数据证据。用户生成、核实并定稿后再替换。",
            "",
        ]
    )


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="生成车道 C 概念图 payload 与占位文件")
    parser.add_argument("--workspace", default=".", help="竞赛工作区，默认当前目录")
    parser.add_argument("--figure-id", required=True, help="如 FIG-G-02 或 FIG-P1-02")
    parser.add_argument("--title", required=True)
    parser.add_argument("--chapter", required=True)
    parser.add_argument("--purpose", required=True)
    parser.add_argument("--element", action="append", default=[], help="画面元素，可重复")
    parser.add_argument(
        "--relationship",
        action="append",
        default=[],
        help="已核实的元素关系，可重复",
    )
    parser.add_argument("--exclude", action="append", default=[], help="额外排除项，可重复")
    parser.add_argument(
        "--aspect-ratio",
        default="4:3",
        choices=("16:9", "4:3", "1:1"),
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    try:
        if not FIGURE_ID_PATTERN.fullmatch(args.figure_id):
            raise ValueError("figure id 必须匹配 FIG-P<正整数>-<两位序号> 或 FIG-G-<两位序号>")
        for field_name in ("title", "chapter", "purpose"):
            if not getattr(args, field_name).strip():
                raise ValueError(f"--{field_name.replace('_', '-')} 不能为空")

        workspace = Path(args.workspace)
        figures_directory = _safe_path(workspace, "figures")
        prompt_relative = f"figures/{args.figure_id}_prompt.json"
        placeholder_relative = f"figures/{args.figure_id}_placeholder.md"
        prompt_path = _safe_path(workspace, prompt_relative)
        placeholder_path = _safe_path(workspace, placeholder_relative)
        figures_directory.mkdir(parents=True, exist_ok=True)

        payload = build_payload(args)
        prompt_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        placeholder_path.write_text(
            render_placeholder(payload, prompt_relative),
            encoding="utf-8",
        )
    except (OSError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2

    print(f"WROTE {prompt_path}")
    print(f"WROTE {placeholder_path}")
    print("API_CALLED false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
