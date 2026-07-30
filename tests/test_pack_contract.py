from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL_NAMES = {
    "cumcm-coding",
    "cumcm-diagram",
    "cumcm-env-doctor",
    "cumcm-hub",
    "cumcm-modeling",
    "cumcm-review",
    "cumcm-writing",
}
EXPECTED_TOP_LEVEL = {
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
LOCAL_STATE_TOP_LEVEL = {"__pycache__", "htmlcov"}
NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def _frontmatter_value(text: str, key: str) -> str:
    match = re.search(rf"^{key}:\s*(.+)$", text, re.MULTILINE)
    return "" if match is None else match.group(1).strip().strip("\"'")


def test_top_level_and_skill_directories_match_product_boundary() -> None:
    visible_entries = {
        path.name
        for path in ROOT.iterdir()
        if not path.name.startswith(".") or path.name in EXPECTED_TOP_LEVEL
    }
    assert visible_entries - LOCAL_STATE_TOP_LEVEL == EXPECTED_TOP_LEVEL
    assert not (ROOT / "AGENTS.md").exists()
    discovered = {
        path.name
        for path in (ROOT / "skills").iterdir()
        if path.is_dir() and (path / "SKILL.md").is_file()
    }
    assert discovered == SKILL_NAMES


def test_skill_frontmatter_and_openai_metadata() -> None:
    for name in SKILL_NAMES:
        skill_text = (ROOT / "skills" / name / "SKILL.md").read_text(encoding="utf-8")
        metadata = (ROOT / "skills" / name / "agents" / "openai.yaml").read_text(
            encoding="utf-8"
        )

        assert NAME_PATTERN.fullmatch(name)
        assert _frontmatter_value(skill_text, "name") == name
        assert _frontmatter_value(skill_text, "description")
        assert "interface:" in metadata
        assert "display_name:" in metadata
        assert "short_description:" in metadata
        assert "default_prompt:" in metadata
        assert f"${name}" in metadata


def test_required_product_files_exist() -> None:
    required = {
        "codex/agents/cumcm-coder.toml",
        "codex/agents/cumcm-modeler.toml",
        "codex/agents/cumcm-reviewer.toml",
        "codex/agents/cumcm-writer.toml",
        "claude/agents/cumcm-coder.md",
        "claude/agents/cumcm-modeler.md",
        "claude/agents/cumcm-reviewer.md",
        "claude/agents/cumcm-writer.md",
        "claude/workflows/cumcm-contest.md",
        "skills/cumcm-coding/references/figure-rules.md",
        "skills/cumcm-coding/scripts/profile_data.py",
        "skills/cumcm-diagram/references/diagram-rules.md",
        "skills/cumcm-diagram/references/figure-registry.md",
        "skills/cumcm-diagram/scripts/schematic_prompt.py",
        "skills/cumcm-env-doctor/references/env-requirements.md",
        "skills/cumcm-env-doctor/scripts/check_env.py",
        "skills/cumcm-hub/references/cumcm-profile.md",
        "skills/cumcm-hub/references/evidence-ledger.md",
        "skills/cumcm-hub/references/problem-typing.md",
        "skills/cumcm-hub/references/task-contract.md",
        "skills/cumcm-hub/references/workflow.md",
        "skills/cumcm-modeling/references/modeling-checklist.md",
        "skills/cumcm-review/references/review-standards.md",
        "skills/cumcm-review/references/step-review-checklists.md",
        "skills/cumcm-review/scripts/check_references.py",
        "skills/cumcm-writing/references/award-style-profile.md",
        "skills/cumcm-writing/references/layout-rules.md",
        "skills/cumcm-writing/references/paper-structure.md",
        "skills/cumcm-writing/references/style-quality.md",
        "skills/cumcm-writing/scripts/docx_export.py",
        "skills/cumcm-writing/templates/cumcm-docx-spec.yaml",
        "skills/cumcm-writing/templates/paper-template.docx",
        "skills/cumcm-writing/templates/paper-template.md",
    }
    missing = sorted(relative for relative in required if not (ROOT / relative).is_file())
    assert missing == []


def test_all_python_sources_compile() -> None:
    for path in ROOT.rglob("*.py"):
        if ".venv" in path.parts:
            continue
        compile(path.read_text(encoding="utf-8"), str(path), "exec")


def test_validate_pack_cli_passes() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/validate_pack.py"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "Validation passed" in result.stdout
