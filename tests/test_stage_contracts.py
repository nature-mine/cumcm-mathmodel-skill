import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_stage_skills_implement_contract_and_boundaries() -> None:
    required_by_skill = {
        "cumcm-modeling": [
            "task_id",
            "假设",
            "符号",
            "灵敏度",
            "编程接口",
            "ready_for_review",
        ],
        "cumcm-coding": [
            "固定种子",
            "约束",
            "results/run-log.md",
            "车道 A",
            "evidence_id",
            "ready_for_review",
        ],
        "cumcm-writing": [
            "status=frozen",
            "问题—方法—关键量化结果—结论",
            "$cumcm-diagram",
            "不手抄",
            "AI 披露",
            "ready_for_review",
        ],
        "cumcm-diagram": [
            "车道 A",
            "车道 B",
            "车道 C",
            ".drawio",
            "绝不用文生图",
            "默认不调用任何图像 API",
        ],
    }
    for name, tokens in required_by_skill.items():
        text = (ROOT / "skills" / name / "SKILL.md").read_text(encoding="utf-8")
        assert "尚未实现" not in text
        assert [token for token in tokens if token not in text] == []


def _parse_agent(path: Path) -> tuple[dict[str, str], str]:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"\A---\n(.*?)\n---\n", text, re.DOTALL)
    assert match is not None
    fields = {}
    for line in match.group(1).splitlines():
        key, value = line.split(":", maxsplit=1)
        fields[key] = value.strip().strip("\"'")
    return fields, text[match.end() :]


def _parse_codex_agent(path: Path) -> tuple[dict[str, str], str, str]:
    text = path.read_text(encoding="utf-8")
    fields = {}
    for key in ("name", "description"):
        match = re.search(rf'^{key}\s*=\s*"([^"\n]+)"$', text, re.MULTILINE)
        assert match is not None
        fields[key] = match.group(1)
    body_match = re.search(
        r'^developer_instructions\s*=\s*"""\n(.*?)\n"""$',
        text,
        re.MULTILINE | re.DOTALL,
    )
    assert body_match is not None
    return fields, body_match.group(1), text


def test_claude_agents_use_current_frontmatter_and_role_isolation() -> None:
    expected_skills = {
        "cumcm-modeler": "$cumcm-modeling",
        "cumcm-coder": "$cumcm-coding",
        "cumcm-writer": "$cumcm-writing",
        "cumcm-reviewer": "$cumcm-review",
    }
    for name, skill in expected_skills.items():
        fields, body = _parse_agent(ROOT / "claude" / "agents" / f"{name}.md")
        assert fields["name"] == name
        assert fields["model"] == "inherit"
        assert fields["color"] in {"blue", "cyan", "green", "magenta", "red", "yellow"}
        tools = json.loads(fields["tools"])
        assert tools
        assert skill in body
        assert "task_id" in body

        if name == "cumcm-reviewer":
            assert {"Write", "Edit", "Bash"}.isdisjoint(tools)
            assert "只评不改" in body
        else:
            assert "Task feedback" in body
    writer = (ROOT / "claude" / "agents" / "cumcm-writer.md").read_text(encoding="utf-8")
    assert "$cumcm-diagram" in writer


def test_codex_agents_use_current_toml_and_reviewer_guard() -> None:
    expected_skills = {
        "cumcm-modeler": "$cumcm-modeling",
        "cumcm-coder": "$cumcm-coding",
        "cumcm-writer": "$cumcm-writing",
        "cumcm-reviewer": "$cumcm-review",
    }
    for name, skill in expected_skills.items():
        fields, body, text = _parse_codex_agent(
            ROOT / "codex" / "agents" / f"{name}.toml"
        )
        assert fields["name"] == name
        assert fields["description"].startswith("Use this")
        assert skill in body
        assert "task_id" in body

        if name == "cumcm-reviewer":
            assert 'sandbox_mode = "read-only"' in text
            assert 'approval_policy = "never"' in text
            assert 'web_search = "disabled"' in text
            assert "只评不改" in body
            assert "不得读取 reviews/final_seat_" in body
        else:
            assert "Task feedback" in body


def test_workflow_covers_eight_steps_roles_and_rework_budget() -> None:
    workflow = (ROOT / "claude" / "workflows" / "cumcm-contest.md").read_text(encoding="utf-8")
    assert ".claude/workflows/cumcm-contest.md" in workflow
    for step in range(1, 9):
        assert f"### {step}." in workflow
    for agent in ("cumcm-modeler", "cumcm-coder", "cumcm-writer", "cumcm-reviewer"):
        assert agent in workflow
    assert "同一任务最多返工 2 轮" in workflow
    assert "最终返工最多 2 轮" in workflow
    assert "无隔离子代理环境降级" in workflow
    assert "同时启动 3 个" in workflow
    assert "review_mode: isolated_subagents" in workflow
    assert "review_mode: sequential_fallback" in workflow
    assert "self-review, 独立性受限" in workflow
