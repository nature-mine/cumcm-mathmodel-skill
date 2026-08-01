#!/usr/bin/env python3
"""Validate the mechanical contract of the CUMCM skill pack."""

from __future__ import annotations

import json
import re
from collections.abc import Callable, Iterator
from pathlib import Path

PACK_ROOT = Path(__file__).resolve().parents[1]
SKILL_NAMES = (
    "cumcm-coding",
    "cumcm-diagram",
    "cumcm-env-doctor",
    "cumcm-hub",
    "cumcm-modeling",
    "cumcm-review",
    "cumcm-writing",
)
REQUIRED_FILES = (
    ".github/workflows/ci.yml",
    ".gitignore",
    "AGENT_INSTALL.md",
    "LICENSE",
    "README.md",
    "THIRD_PARTY_NOTICES.md",
    "install.sh",
    "codex/agents/cumcm-coder.toml",
    "codex/agents/cumcm-modeler.toml",
    "codex/agents/cumcm-reviewer.toml",
    "codex/agents/cumcm-writer.toml",
    "claude/agents/cumcm-coder.md",
    "claude/agents/cumcm-modeler.md",
    "claude/agents/cumcm-reviewer.md",
    "claude/agents/cumcm-writer.md",
    "claude/workflows/cumcm-contest.md",
    "pyproject.toml",
    "ruff.toml",
    "licenses/Apache-2.0.txt",
    "scripts/validate_pack.py",
    "scripts/validate_smoke_workspace.py",
    "skills/cumcm-coding/SKILL.md",
    "skills/cumcm-coding/agents/openai.yaml",
    "skills/cumcm-coding/references/figure-rules.md",
    "skills/cumcm-coding/scripts/profile_data.py",
    "skills/cumcm-diagram/SKILL.md",
    "skills/cumcm-diagram/agents/openai.yaml",
    "skills/cumcm-diagram/references/diagram-rules.md",
    "skills/cumcm-diagram/references/figure-registry.md",
    "skills/cumcm-diagram/scripts/schematic_prompt.py",
    "skills/cumcm-env-doctor/SKILL.md",
    "skills/cumcm-env-doctor/agents/openai.yaml",
    "skills/cumcm-env-doctor/references/env-requirements.md",
    "skills/cumcm-env-doctor/scripts/check_env.py",
    "skills/cumcm-hub/SKILL.md",
    "skills/cumcm-hub/agents/openai.yaml",
    "skills/cumcm-hub/references/cumcm-profile.md",
    "skills/cumcm-hub/references/evidence-ledger.md",
    "skills/cumcm-hub/references/problem-typing.md",
    "skills/cumcm-hub/references/task-contract.md",
    "skills/cumcm-hub/references/workflow.md",
    "skills/cumcm-modeling/SKILL.md",
    "skills/cumcm-modeling/agents/openai.yaml",
    "skills/cumcm-modeling/references/modeling-checklist.md",
    "skills/cumcm-review/SKILL.md",
    "skills/cumcm-review/agents/openai.yaml",
    "skills/cumcm-review/references/review-standards.md",
    "skills/cumcm-review/references/step-review-checklists.md",
    "skills/cumcm-review/scripts/check_references.py",
    "skills/cumcm-writing/SKILL.md",
    "skills/cumcm-writing/agents/openai.yaml",
    "skills/cumcm-writing/references/award-style-profile.md",
    "skills/cumcm-writing/references/layout-rules.md",
    "skills/cumcm-writing/references/paper-structure.md",
    "skills/cumcm-writing/references/style-quality.md",
    "skills/cumcm-writing/scripts/docx_export.py",
    "skills/cumcm-writing/scripts/mathml_to_omml.xsl",
    "skills/cumcm-writing/templates/cumcm-docx-spec.yaml",
    "skills/cumcm-writing/templates/paper-template.docx",
    "skills/cumcm-writing/templates/paper-template.md",
    "tests/test_docx_export.py",
    "tests/test_env_doctor.py",
    "tests/test_hub_contract.py",
    "tests/test_diagram_tools.py",
    "tests/test_readme_contract.py",
    "tests/test_reference_checker.py",
    "tests/test_review_contract.py",
    "tests/test_smoke_contract.py",
    "tests/test_stage_contracts.py",
    "tests/test_pack_contract.py",
    "tests/test_paper_template.py",
    "uv.lock",
)
PRODUCT_TOP_LEVEL = {
    ".github",
    ".gitignore",
    "AGENT_INSTALL.md",
    "LICENSE",
    "README.md",
    "THIRD_PARTY_NOTICES.md",
    "install.sh",
    "claude",
    "codex",
    "licenses",
    "pyproject.toml",
    "ruff.toml",
    "scripts",
    "skills",
    "tests",
    "uv.lock",
}
LOCAL_STATE_ENTRIES = {
    ".DS_Store",
    ".coverage",
    ".git",
    ".pytest_cache",
    ".ruff_cache",
    ".serena",
    ".venv",
    "__pycache__",
    "htmlcov",
}
NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
FRONTMATTER_PATTERN = re.compile(r"\A---\n(?P<content>.*?)\n---(?:\n|\Z)", re.DOTALL)
MARKDOWN_LINK_PATTERN = re.compile(r"\[[^\]]*]\(([^)]+)\)")
IGNORED_PARTS = LOCAL_STATE_ENTRIES
AGENT_SKILLS = {
    "cumcm-coder": "$cumcm-coding",
    "cumcm-modeler": "$cumcm-modeling",
    "cumcm-reviewer": "$cumcm-review",
    "cumcm-writer": "$cumcm-writing",
}
AGENT_COLORS = {"blue", "cyan", "green", "magenta", "red", "yellow"}


class ValidationFailure(Exception):
    """Raised when a pack contract check fails."""


def _iter_files(suffix: str) -> Iterator[Path]:
    for path in sorted(PACK_ROOT.rglob(f"*{suffix}")):
        relative_parts = path.relative_to(PACK_ROOT).parts
        if not IGNORED_PARTS.intersection(relative_parts):
            yield path


def _parse_frontmatter(path: Path) -> tuple[dict[str, str], str]:
    text = path.read_text(encoding="utf-8")
    match = FRONTMATTER_PATTERN.match(text)
    if match is None:
        raise ValidationFailure(f"{path.relative_to(PACK_ROOT)} 缺少 YAML frontmatter")

    fields: dict[str, str] = {}
    for line in match.group("content").splitlines():
        field_match = re.fullmatch(r"([A-Za-z0-9_-]+):\s*(.+)", line)
        if field_match is None:
            raise ValidationFailure(f"{path.relative_to(PACK_ROOT)} frontmatter 行无效：{line}")
        key, value = field_match.groups()
        fields[key] = value.strip().strip("\"'")
    return fields, text[match.end() :]


def _parse_codex_agent(path: Path) -> tuple[dict[str, str], str, str]:
    text = path.read_text(encoding="utf-8")
    fields: dict[str, str] = {}
    for key in ("name", "description"):
        match = re.search(rf'^{key}\s*=\s*"([^"\n]+)"$', text, re.MULTILINE)
        if match is None:
            raise ValidationFailure(
                f"{path.relative_to(PACK_ROOT)} 缺少单行 TOML 字段 {key}"
            )
        fields[key] = match.group(1)
    body_match = re.search(
        r'^developer_instructions\s*=\s*"""\n(?P<body>.*?)\n"""$',
        text,
        re.MULTILINE | re.DOTALL,
    )
    if body_match is None:
        raise ValidationFailure(
            f"{path.relative_to(PACK_ROOT)} 缺少多行 developer_instructions"
        )
    return fields, body_match.group("body"), text


def check_required_files() -> str:
    missing = [relative for relative in REQUIRED_FILES if not (PACK_ROOT / relative).is_file()]
    if missing:
        raise ValidationFailure("缺少必需产品或质量文件：" + ", ".join(missing))
    return f"{len(REQUIRED_FILES)} 个必需产品与质量文件存在"


def check_product_boundary() -> str:
    discovered = {path.name for path in PACK_ROOT.iterdir()}
    forbidden = sorted(discovered.intersection({"AGENTS.md"}))
    if forbidden:
        raise ValidationFailure("包内含工作区级或开发期文件：" + ", ".join(forbidden))

    unexpected = sorted(discovered - PRODUCT_TOP_LEVEL - LOCAL_STATE_ENTRIES)
    if unexpected:
        raise ValidationFailure("包顶层含未归类文件：" + ", ".join(unexpected))
    return "包顶层仅含发布产物、使用者文档、合规件与质量工具链"


def check_skill_frontmatter() -> str:
    skill_root = PACK_ROOT / "skills"
    discovered = tuple(
        sorted(path.name for path in skill_root.iterdir() if (path / "SKILL.md").is_file())
    )
    if discovered != SKILL_NAMES:
        raise ValidationFailure(f"Skill 集合不匹配：{discovered!r}")

    for name in SKILL_NAMES:
        fields, body = _parse_frontmatter(skill_root / name / "SKILL.md")
        if set(fields) != {"description", "name"}:
            raise ValidationFailure(f"{name}/SKILL.md frontmatter 只能含 name 与 description")
        if fields["name"] != name:
            raise ValidationFailure(f"{name}/SKILL.md 的 name 与目录名不一致")
        if not NAME_PATTERN.fullmatch(name) or len(name) > 64:
            raise ValidationFailure(f"Skill 名称不符合 kebab-case 或长度限制：{name}")
        if not fields["description"].strip():
            raise ValidationFailure(f"{name}/SKILL.md 的 description 为空")
        if not body.strip():
            raise ValidationFailure(f"{name}/SKILL.md 正文为空")
    return f"{len(SKILL_NAMES)} 个 Skill frontmatter 有效"


def check_openai_metadata() -> str:
    required_keys = ("display_name", "short_description", "default_prompt")
    for name in SKILL_NAMES:
        relative = Path("skills") / name / "agents" / "openai.yaml"
        text = (PACK_ROOT / relative).read_text(encoding="utf-8")
        if not text.startswith("interface:\n"):
            raise ValidationFailure(f"{relative} 缺少 interface 顶层字段")

        values: dict[str, str] = {}
        for key in required_keys:
            match = re.search(rf'^  {key}: "([^"]+)"$', text, re.MULTILINE)
            if match is None:
                raise ValidationFailure(f"{relative} 缺少带引号的 {key}")
            values[key] = match.group(1)

        if not 25 <= len(values["short_description"]) <= 64:
            raise ValidationFailure(f"{relative} 的 short_description 长度须为 25–64")
        if f"${name}" not in values["default_prompt"]:
            raise ValidationFailure(f"{relative} 的 default_prompt 未显式提及 ${name}")
    return f"{len(SKILL_NAMES)} 份 OpenAI 元数据有效"


def check_claude_agents() -> str:
    agent_root = PACK_ROOT / "claude" / "agents"
    discovered = {path.stem for path in agent_root.glob("*.md")}
    if discovered != set(AGENT_SKILLS):
        raise ValidationFailure(f"Claude agent 集合不匹配：{sorted(discovered)}")

    required_fields = {"name", "description", "model", "color", "tools"}
    for name, required_skill in AGENT_SKILLS.items():
        path = agent_root / f"{name}.md"
        fields, body = _parse_frontmatter(path)
        if set(fields) != required_fields:
            raise ValidationFailure(f"{path.relative_to(PACK_ROOT)} frontmatter 字段不完整")
        if fields["name"] != name:
            raise ValidationFailure(f"{path.relative_to(PACK_ROOT)} 的 name 与文件名不一致")
        if fields["model"] != "inherit":
            raise ValidationFailure(f"{path.relative_to(PACK_ROOT)} 必须使用 model: inherit")
        if fields["color"] not in AGENT_COLORS:
            raise ValidationFailure(f"{path.relative_to(PACK_ROOT)} 的 color 无效")
        if not fields["description"].startswith("Use this agent"):
            raise ValidationFailure(f"{path.relative_to(PACK_ROOT)} description 未写触发条件")
        try:
            tools = json.loads(fields["tools"])
        except json.JSONDecodeError as error:
            raise ValidationFailure(
                f"{path.relative_to(PACK_ROOT)} 的 tools 必须是 JSON 风格 YAML 数组"
            ) from error
        if (
            not isinstance(tools, list)
            or not tools
            or not all(isinstance(tool, str) for tool in tools)
        ):
            raise ValidationFailure(f"{path.relative_to(PACK_ROOT)} 的 tools 无效")
        for token in (required_skill, "task_id"):
            if token not in body:
                raise ValidationFailure(f"{path.relative_to(PACK_ROOT)} 正文缺少 {token}")

        if name == "cumcm-reviewer":
            forbidden = {"Write", "Edit", "Bash"}
            if forbidden.intersection(tools):
                raise ValidationFailure("cumcm-reviewer 必须保持只读工具集")
            if "只评不改" not in body:
                raise ValidationFailure("cumcm-reviewer 未声明只评不改")
        else:
            if "Task feedback" not in body:
                raise ValidationFailure(f"{path.relative_to(PACK_ROOT)} 缺少反馈契约")
    return f"{len(AGENT_SKILLS)} 个 Claude subagent 定义有效"


def check_codex_agents() -> str:
    agent_root = PACK_ROOT / "codex" / "agents"
    discovered = {path.stem for path in agent_root.glob("*.toml")}
    if discovered != set(AGENT_SKILLS):
        raise ValidationFailure(f"Codex agent 集合不匹配：{sorted(discovered)}")

    for name, required_skill in AGENT_SKILLS.items():
        path = agent_root / f"{name}.toml"
        fields, body, text = _parse_codex_agent(path)
        if fields["name"] != name:
            raise ValidationFailure(f"{path.relative_to(PACK_ROOT)} 的 name 与文件名不一致")
        if not fields["description"].startswith("Use this"):
            raise ValidationFailure(f"{path.relative_to(PACK_ROOT)} description 未写触发条件")
        for token in (required_skill, "task_id"):
            if token not in body:
                raise ValidationFailure(f"{path.relative_to(PACK_ROOT)} 正文缺少 {token}")

        if name == "cumcm-reviewer":
            required_settings = (
                'sandbox_mode = "read-only"',
                'approval_policy = "never"',
                'web_search = "disabled"',
            )
            missing_settings = [
                setting for setting in required_settings if setting not in text
            ]
            if missing_settings:
                raise ValidationFailure(
                    f"{path.relative_to(PACK_ROOT)} 缺少 reviewer 限权："
                    f"{missing_settings}"
                )
            for token in ("只评不改", "不得读取 reviews/final_seat_", "只返回评审文本"):
                if token not in body:
                    raise ValidationFailure(
                        f"{path.relative_to(PACK_ROOT)} 缺少隔离条款：{token}"
                    )
        elif "Task feedback" not in body:
            raise ValidationFailure(f"{path.relative_to(PACK_ROOT)} 缺少反馈契约")
    return f"{len(AGENT_SKILLS)} 个 Codex custom agent TOML 有效"


def check_claude_workflow() -> str:
    relative = Path("claude/workflows/cumcm-contest.md")
    text = (PACK_ROOT / relative).read_text(encoding="utf-8")
    required = (
        "### 1. 环境自检",
        "### 2. Startup lock",
        "### 3. 读题、数据剖析与分型",
        "### 4. 拆解",
        "### 5. 模型路线确认",
        "### 6. 契约派发循环",
        "### 7. 阶段推进与返工传播",
        "### 8. 最终评审与提交门禁",
        "cumcm-modeler",
        "cumcm-coder",
        "cumcm-writer",
        "cumcm-reviewer",
        "最多返工 2 轮",
        "self-review, 独立性受限",
        "无隔离子代理环境降级",
        "同时启动 3 个",
        ".claude/workflows/cumcm-contest.md",
    )
    missing = [token for token in required if token not in text]
    if missing:
        raise ValidationFailure(f"{relative} 缺少工作流条款：{missing}")
    return "Claude 八步 workflow 定义有效"


def check_stage_assets() -> str:
    stage_paths = (
        "skills/cumcm-modeling/SKILL.md",
        "skills/cumcm-modeling/references/modeling-checklist.md",
        "skills/cumcm-coding/SKILL.md",
        "skills/cumcm-coding/references/figure-rules.md",
        "skills/cumcm-coding/scripts/profile_data.py",
        "skills/cumcm-diagram/SKILL.md",
        "skills/cumcm-diagram/references/diagram-rules.md",
        "skills/cumcm-diagram/references/figure-registry.md",
        "skills/cumcm-diagram/scripts/schematic_prompt.py",
        "skills/cumcm-writing/SKILL.md",
        "skills/cumcm-writing/references/paper-structure.md",
    )
    for relative in stage_paths:
        text = (PACK_ROOT / relative).read_text(encoding="utf-8")
        if "尚未实现" in text:
            raise ValidationFailure(f"{relative} 仍含占位标记")

    diagram = (PACK_ROOT / "skills/cumcm-diagram/SKILL.md").read_text(encoding="utf-8")
    for token in ("车道 A", "车道 B", "车道 C", ".drawio", "默认不调用任何图像 API"):
        if token not in diagram:
            raise ValidationFailure(f"cumcm-diagram 缺少关键路由规则：{token}")
    return f"{len(stage_paths)} 个阶段工件契约完整"


def check_review_assets() -> str:
    review_root = PACK_ROOT / "skills" / "cumcm-review"
    skill = (review_root / "SKILL.md").read_text(encoding="utf-8")
    standards = (review_root / "references" / "review-standards.md").read_text(encoding="utf-8")
    checklists = (review_root / "references" / "step-review-checklists.md").read_text(
        encoding="utf-8"
    )
    checker = (review_root / "scripts" / "check_references.py").read_text(encoding="utf-8")
    for relative, text in (
        ("skills/cumcm-review/SKILL.md", skill),
        ("skills/cumcm-review/references/review-standards.md", standards),
        ("skills/cumcm-review/references/step-review-checklists.md", checklists),
        ("skills/cumcm-review/scripts/check_references.py", checker),
    ):
        if "尚未实现" in text:
            raise ValidationFailure(f"{relative} 仍含占位标记")

    required_skill_tokens = (
        "### 分步模式",
        "### 最终模式",
        "self-review, 独立性受限",
        "P0-candidate",
        "三席盲评",
        "sequential_fallback",
        'fork_turns="none"',
        "review_mode: isolated_subagents",
        "review_mode: sequential_fallback",
        "fallback_reason: subagent_unavailable",
        "不得切换成顺序复评",
        "只评不改",
    )
    required_standard_tokens = (
        "假设合理性（20）",
        "建模创造性（25）",
        "结果表述清晰性（25）",
        "格式规范性（15）",
        "参考文献与引用（15）",
        "不得仅因无先例而压分",
    )
    required_checklist_tokens = (
        "## 建模件",
        "## 代码件",
        "## 论文件",
        "框架锁死检查",
        "失败模式检查",
        "程式化 AI 文风",
    )
    for label, text, tokens in (
        ("cumcm-review", skill, required_skill_tokens),
        ("review-standards", standards, required_standard_tokens),
        ("step-review-checklists", checklists, required_checklist_tokens),
    ):
        missing = [token for token in tokens if token not in text]
        if missing:
            raise ValidationFailure(f"{label} 缺少评审条款：{missing}")

    profile_script = (
        PACK_ROOT / "skills" / "cumcm-coding" / "scripts" / "profile_data.py"
    ).read_text(encoding="utf-8")
    expected_url = "https://github.com/Haojae/scipilot-figure-skill"
    if expected_url not in profile_script or "haojae-science" in profile_script:
        raise ValidationFailure("profile_data.py 上游 URL 契约不匹配")
    return "双模式评审、三类检查单、五维标准与引用脚本契约完整"


def check_docx_assets() -> str:
    writing_root = PACK_ROOT / "skills" / "cumcm-writing"
    skill = (writing_root / "SKILL.md").read_text(encoding="utf-8")
    layout = (writing_root / "references" / "layout-rules.md").read_text(encoding="utf-8")
    structure = (writing_root / "references" / "paper-structure.md").read_text(
        encoding="utf-8"
    )
    style = (writing_root / "references" / "style-quality.md").read_text(encoding="utf-8")
    award_style = (writing_root / "references" / "award-style-profile.md").read_text(
        encoding="utf-8"
    )
    exporter = (writing_root / "scripts" / "docx_export.py").read_text(encoding="utf-8")
    spec_path = writing_root / "templates" / "cumcm-docx-spec.yaml"
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    template_source = (writing_root / "templates" / "paper-template.md").read_text(
        encoding="utf-8"
    )
    template_docx = writing_root / "templates" / "paper-template.docx"
    notices = (PACK_ROOT / "THIRD_PARTY_NOTICES.md").read_text(encoding="utf-8")

    for relative, text in (
        ("skills/cumcm-writing/SKILL.md", skill),
        ("skills/cumcm-writing/references/layout-rules.md", layout),
        ("skills/cumcm-writing/references/award-style-profile.md", award_style),
        ("skills/cumcm-writing/references/style-quality.md", style),
        ("skills/cumcm-writing/scripts/docx_export.py", exporter),
    ):
        if "尚未实现" in text:
            raise ValidationFailure(f"{relative} 仍含占位标记")

    required_skill_tokens = (
        "执行集中文风 pass",
        "scripts/docx_export.py",
        "support_manifest.json",
        "OfficeCLI",
        "templates/paper-template.md",
        "references/award-style-profile.md",
    )
    required_layout_tokens = (
        "[[EQUATION",
        "[[FIGURE",
        "[[PLACEHOLDER",
        "[[TABLE",
        "input/",
        "data/",
        "code/",
        "OfficeCLI",
        "libreoffice/soffice",
    )
    required_style_tokens = (
        "不得触碰的内容",
        "三步改写",
        "集中文风 pass",
        "不用于规避 AI 检测",
        "frozen",
    )
    required_exporter_tokens = (
        "chinese-thesis-workbench-skill/scripts/docx/generate_thesis_docx.py",
        "mathml_to_omml.xsl",
        "build_support_manifest",
        "_read_source_files",
        "_normalize_docx_zip",
        "SOURCE_CODE_FILES",
    )
    required_template_tokens = (
        "复制到竞赛工作区 `paper/paper.md`",
        "【待替换】问题：",
        "【待替换】方法：",
        "【待替换】关键结果：",
        "【待替换】结论：",
        "关键词：【待替换】",
        "[[TABLE",
        'lane="B"',
        'lane="C"',
        "`[[FIGURE",
    )
    required_award_tokens = (
        "My-MathModeling-skills",
        "national-prize-style-profile.md",
        "section-format-controls.md",
        "section_templates_national.md",
        "figure_registry.md",
        "frozen",
        "车道 A",
        "车道 B",
        "车道 C",
        "固定句式库",
    )
    for label, text, tokens in (
        ("cumcm-writing", skill, required_skill_tokens),
        ("layout-rules", layout, required_layout_tokens),
        ("style-quality", style, required_style_tokens),
        ("docx-export", exporter, required_exporter_tokens),
        ("paper-template", template_source, required_template_tokens),
        ("award-style-profile", award_style, required_award_tokens),
    ):
        missing = [token for token in tokens if token not in text]
        if missing:
            raise ValidationFailure(f"{label} 缺少 DOCX 条款：{missing}")

    if spec.get("schema_version") != 1:
        raise ValidationFailure("cumcm-docx-spec.yaml schema_version 必须为 1")
    page = spec.get("page")
    if not isinstance(page, dict):
        raise ValidationFailure("cumcm-docx-spec.yaml 缺少 page")
    for side in ("top", "bottom", "left", "right"):
        if page.get(f"margin_{side}_mm", 0) < 25:
            raise ValidationFailure(f"cumcm-docx-spec.yaml 的 {side} 页边距小于 25 mm")
    if "recommended_style_not_official_typography" != spec.get("status"):
        raise ValidationFailure("cumcm-docx-spec.yaml 未声明推荐样式边界")
    if "chinese-thesis-workbench-skill" not in notices:
        raise ValidationFailure("THIRD_PARTY_NOTICES.md 缺少 DOCX 上游声明")
    if "My-MathModeling-skills" not in notices:
        raise ValidationFailure("THIRD_PARTY_NOTICES.md 缺少风格画像上游声明")

    structure_headings = re.findall(r"^### (\d+\.\s+.+)$", structure, re.MULTILINE)
    template_headings = re.findall(r"^## (\d+\.\s+.+)$", template_source, re.MULTILINE)
    if len(structure_headings) != 10 or template_headings != structure_headings:
        raise ValidationFailure("paper-template.md 正文十节未与 paper-structure.md 对齐")
    if "<!--" in template_source:
        raise ValidationFailure("paper-template.md 不得使用会泄漏到 DOCX 的 HTML 注释")
    if len(re.findall(r"^\[\[TABLE\b", template_source, re.MULTILINE)) != 2:
        raise ValidationFailure("paper-template.md 必须含假设表和符号表两处 TABLE 真指令")
    for lane in ("B", "C"):
        pattern = rf'^\[\[PLACEHOLDER\b.*lane="{lane}"'
        if len(re.findall(pattern, template_source, re.MULTILINE)) != 1:
            raise ValidationFailure(f"paper-template.md 必须含一处车道 {lane} 真占位")
    if re.search(r"^\[\[FIGURE\b", template_source, re.MULTILINE):
        raise ValidationFailure("paper-template.md 的 FIGURE 只能以内联代码展示")
    for section in re.split(
        r"^## \d+\.\s+.+$", template_source, flags=re.MULTILINE
    )[1:]:
        placeholders = [
            line for line in section.splitlines() if line.startswith("【待替换】")
        ]
        if not 1 <= len(placeholders) <= 3:
            raise ValidationFailure("paper-template.md 每个正文节须含 1–3 行待替换正文")
    if len(award_style.splitlines()) > 150:
        raise ValidationFailure("award-style-profile.md 超过 150 行")
    template_bytes = template_docx.read_bytes()
    if not template_bytes.startswith(b"PK") or not 10_000 <= len(template_bytes) <= 200_000:
        raise ValidationFailure("paper-template.docx 不是预期体积的 DOCX")
    return "DOCX 导出、双格式模板、版式、文风画像、附录和支撑材料契约完整"


def check_smoke_validator_contract() -> str:
    smoke_validator = (PACK_ROOT / "scripts/validate_smoke_workspace.py").read_text(
        encoding="utf-8"
    )
    profile = (
        PACK_ROOT / "skills" / "cumcm-coding" / "scripts" / "profile_data.py"
    ).read_text(encoding="utf-8")
    exporter = (
        PACK_ROOT / "skills" / "cumcm-writing" / "scripts" / "docx_export.py"
    ).read_text(encoding="utf-8")

    required_validator_tokens = (
        "冒烟工作区必须位于 Skill 包外",
        "仍可写",
        "SHA-256",
        "A=done、B=draft、C=placeholder",
        "support_manifest.json",
        "review_mode: isolated_subagents",
        "review_mode: sequential_fallback",
        "论文正文泄漏内部流程词",
        "图表章节不一致",
    )
    missing = [token for token in required_validator_tokens if token not in smoke_validator]
    if missing:
        raise ValidationFailure(f"smoke validator 缺少行为条款：{missing}")
    if "profile_workbook" not in profile or "args.sheet is None" not in profile:
        raise ValidationFailure("profile_data.py 未实现 XLSX 默认全工作表与单表覆盖")
    if '("support", True' not in exporter:
        raise ValidationFailure("docx_export.py 未将 support/ 纳入支撑材料")
    return "包外只读冒烟、全表剖析、披露材料与可重复门禁契约完整"


def check_user_documentation() -> str:
    readme = (PACK_ROOT / "README.md").read_text(encoding="utf-8")
    agent_install = (PACK_ROOT / "AGENT_INSTALL.md").read_text(encoding="utf-8")
    claude_workflow = (PACK_ROOT / "claude/workflows/cumcm-contest.md").read_text(
        encoding="utf-8"
    )
    root_readme_path = PACK_ROOT.parent / "README.md"
    root_claude_path = PACK_ROOT.parent / "CLAUDE.md"
    has_root_document_contract = root_readme_path.is_file() and root_claude_path.is_file()

    required_readme_tokens = (
        "## 快速开始（3 步）",
        "install.sh claude",
        "### 让 Agent 帮你安装",
        "AGENT_INSTALL.md",
        "## 手动安装（备选）",
        "### 接下来会发生什么",
        "## Skill 索引",
        "## Agent 部署与分派规则",
        "npx skills add \"$CUMCM_SKILL_PACK\" --list",
        "每个竞赛项目只用一个 Agent",
        "vercel-labs/skills",
        "WSL",
        "不是环境变量",
        "--agent codex",
        "--agent claude-code",
        "npx skills list --agent codex --json",
        "npx skills list --agent <codex|claude-code> --json",
        "codex features list",
        "multi_agent",
        "stable true",
        "把题面 PDF 与官方附件放进 `input/`",
        "env_report.md",
        "startup lock 六问",
        "模型路线确认是人工决策点",
        "全权委托",
        "旧会话看不到新安装的 Skill",
        ".agents/skills/",
        ".claude/skills/",
        "codex/agents/*.toml",
        "claude/agents/*.md",
        "claude/workflows/cumcm-contest.md",
        "skills add` 只安装 `skills/",
        "fork_turns=\"none\"",
        "fallback_reason: subagent_unavailable",
        "必须 `blocked`，不得降级",
        "Tier 0 硬性依赖",
        "不是“全自动出赛论文”工具",
        "skills/cumcm-writing/templates/paper-template.md",
        "tests/test_paper_template.py",
        "`tests/` 与包顶层 `scripts/` 是包质量工具链，不随 `skills add` 安装",
    )
    required_agent_install_tokens = (
        "install.sh",
        "npx skills list --agent <codex|claude-code> --json",
        ".agents/skills/",
        ".claude/skills/",
        ".codex/agents/",
        ".claude/workflows/cumcm-contest.md",
        "codex features list",
        "不得修改克隆下来的包内容",
        "不要在当前会话中替用户启动建模流程",
    )
    for skill_name in SKILL_NAMES:
        if f"[`{skill_name}`]" not in readme:
            raise ValidationFailure(f"package README 的 Skill 索引缺少 {skill_name}")
        if f"`{skill_name}`" not in agent_install:
            raise ValidationFailure(f"AGENT_INSTALL.md 验收清单缺少 {skill_name}")

    claude_prompt = next(
        (
            line
            for line in claude_workflow.splitlines()
            if line.startswith("> 加载 `$cumcm-hub`")
        ),
        None,
    )
    if claude_prompt is None or claude_prompt not in readme:
        raise ValidationFailure("package README 与 Claude workflow 的启动提示语不一致")
    if claude_prompt not in agent_install:
        raise ValidationFailure("AGENT_INSTALL.md 与 Claude workflow 的启动提示语不一致")

    documents = [
        ("package README", readme, required_readme_tokens),
        ("AGENT_INSTALL", agent_install, required_agent_install_tokens),
    ]
    if has_root_document_contract:
        stable_root_tokens = ("cumcm-mathmodel-skill/", "7 个 Skill")
        documents.extend(
            (
                (
                    "root README",
                    root_readme_path.read_text(encoding="utf-8"),
                    stable_root_tokens,
                ),
                (
                    "root CLAUDE",
                    root_claude_path.read_text(encoding="utf-8"),
                    stable_root_tokens,
                ),
            )
        )
    for label, text, tokens in documents:
        missing = [token for token in tokens if token not in text]
        if missing:
            raise ValidationFailure(f"{label} 缺少产品文档条款：{missing}")
    if re.search(r"^## M\d+ ", readme, re.MULTILINE):
        raise ValidationFailure("package README 仍含里程碑实现约定")
    message = "快速开始、七 Skill 索引、Agent 安装说明、单 Agent 部署与使用边界说明完整"
    if not has_root_document_contract:
        message += "；独立 checkout,跳过根文档契约"
    return message


def check_markdown_links() -> str:
    checked = 0
    for path in _iter_files(".md"):
        text = path.read_text(encoding="utf-8")
        for raw_target in MARKDOWN_LINK_PATTERN.findall(text):
            target = raw_target.strip().strip("<>")
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            target_path = target.split("#", maxsplit=1)[0]
            if not target_path:
                continue
            resolved = (path.parent / target_path).resolve()
            if not resolved.exists():
                relative = path.relative_to(PACK_ROOT)
                raise ValidationFailure(f"{relative} 包含失效相对链接：{raw_target}")
        checked += 1
    return f"{checked} 个 Markdown 文件的相对链接可解析"


def check_python_syntax() -> str:
    checked = 0
    for path in _iter_files(".py"):
        source = path.read_text(encoding="utf-8")
        try:
            compile(source, str(path), "exec")
        except SyntaxError as error:
            relative = path.relative_to(PACK_ROOT)
            raise ValidationFailure(f"{relative} 无法编译：{error}") from error
        checked += 1
    return f"{checked} 个 Python 文件可编译"


def main() -> int:
    checks: tuple[tuple[str, Callable[[], str]], ...] = (
        ("产品边界", check_product_boundary),
        ("目录结构", check_required_files),
        ("Skill frontmatter", check_skill_frontmatter),
        ("OpenAI 元数据", check_openai_metadata),
        ("Claude subagent", check_claude_agents),
        ("Codex subagent", check_codex_agents),
        ("Claude workflow", check_claude_workflow),
        ("阶段工件", check_stage_assets),
        ("评审工件", check_review_assets),
        ("DOCX 工件", check_docx_assets),
        ("冒烟校验契约", check_smoke_validator_contract),
        ("使用者文档", check_user_documentation),
        ("Markdown 链接", check_markdown_links),
        ("Python 语法", check_python_syntax),
    )
    try:
        for label, check in checks:
            print(f"PASS {label}：{check()}")
    except ValidationFailure as error:
        print(f"FAIL：{error}")
        return 1

    print(f"Validation passed：{len(checks)} 项检查全部通过")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
