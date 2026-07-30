from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

PACK_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = PACK_ROOT.parent


def test_package_readme_guides_installation_and_first_run() -> None:
    readme = (PACK_ROOT / "README.md").read_text(encoding="utf-8")
    claude_workflow = (PACK_ROOT / "claude/workflows/cumcm-contest.md").read_text(
        encoding="utf-8"
    )

    for token in (
        "状态：已发布，维护期",
        "## 快速开始（3 步）",
        "install.sh claude",
        "### 让 Agent 帮你安装",
        "AGENT_INSTALL.md",
        "## 手动安装（备选）",
        "### 接下来会发生什么",
        "## Skill 索引",
        "每个竞赛项目只用一个 Agent",
        "--agent codex",
        "--agent claude-code",
        "npx skills list --agent codex --json",
        "npx skills list --agent <codex|claude-code> --json",
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
        'fork_turns="none"',
        "fallback_reason: subagent_unavailable",
        "必须 `blocked`，不得降级",
        "不是“全自动出赛论文”工具",
    ):
        assert token in readme

    for skill_name in (
        "cumcm-hub",
        "cumcm-env-doctor",
        "cumcm-modeling",
        "cumcm-coding",
        "cumcm-diagram",
        "cumcm-writing",
        "cumcm-review",
    ):
        assert f"[`{skill_name}`]" in readme
    claude_prompt = next(
        line for line in claude_workflow.splitlines() if line.startswith("> 加载 `$cumcm-hub`")
    )
    assert claude_prompt in readme
    assert re.search(r"^## M\d+ ", readme, re.MULTILINE) is None


def test_workspace_docs_identify_the_product() -> None:
    root_readme_path = WORKSPACE_ROOT / "README.md"
    root_claude_path = WORKSPACE_ROOT / "CLAUDE.md"
    if not (root_readme_path.is_file() and root_claude_path.is_file()):
        result = subprocess.run(
            [sys.executable, "scripts/validate_pack.py"],
            cwd=PACK_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, result.stdout + result.stderr
        assert "独立 checkout,跳过根文档契约" in result.stdout
        return

    root_readme = root_readme_path.read_text(encoding="utf-8")
    root_claude = root_claude_path.read_text(encoding="utf-8")

    for text in (root_readme, root_claude):
        assert "cumcm-mathmodel-skill/" in text
        assert "7 个 Skill" in text
