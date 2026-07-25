from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REVIEW_ROOT = ROOT / "skills" / "cumcm-review"


def test_review_skill_defines_two_modes_independence_and_blind_panel() -> None:
    skill = (REVIEW_ROOT / "SKILL.md").read_text(encoding="utf-8")
    for token in (
        "### 分步模式",
        "### 最终模式",
        "只评不改",
        "self-review, 独立性受限",
        "P0-candidate",
        "上下文隔离、互不可见",
        "sequential_fallback",
        'fork_turns="none"',
        "review_mode: isolated_subagents",
        "review_mode: sequential_fallback",
        "fallback_reason: subagent_unavailable",
        "不得切换成顺序复评",
        "中位数",
        "P0 取并集",
        "≥15",
    ):
        assert token in skill


def test_final_review_weights_sum_to_100_and_calibrate_innovation() -> None:
    standards = (REVIEW_ROOT / "references" / "review-standards.md").read_text(encoding="utf-8")
    expected = {
        "假设合理性": 20,
        "建模创造性": 25,
        "结果表述清晰性": 25,
        "格式规范性": 15,
        "参考文献与引用": 15,
    }
    assert sum(expected.values()) == 100
    for name, weight in expected.items():
        assert f"{name}（{weight}）" in standards
    assert "不得仅因无先例而压分" in standards
    assert "不预测奖项" in standards


def test_step_checklists_cover_three_axes_and_stage_failure_modes() -> None:
    checklists = (REVIEW_ROOT / "references" / "step-review-checklists.md").read_text(
        encoding="utf-8"
    )
    for heading in ("## 建模件", "## 代码件", "## 论文件"):
        assert heading in checklists
    for axis in ("数学核验", "跨材料一致性", "官方合规"):
        assert axis in checklists
    for token in (
        "框架锁死检查",
        "失败模式检查",
        "数据泄漏",
        "硬编码答案",
        "程式化 AI 文风",
        "引用幻觉",
        "摘要缺关键量化结论",
    ):
        assert token in checklists


def test_profile_data_declares_expected_upstream_url() -> None:
    script = (ROOT / "skills" / "cumcm-coding" / "scripts" / "profile_data.py").read_text(
        encoding="utf-8"
    )
    assert "https://github.com/Haojae/scipilot-figure-skill" in script
    assert "haojae-science" not in script
