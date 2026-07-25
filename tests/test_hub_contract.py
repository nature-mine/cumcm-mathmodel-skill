from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HUB_ROOT = ROOT / "skills" / "cumcm-hub"


def _read(relative_path: str) -> str:
    return (HUB_ROOT / relative_path).read_text(encoding="utf-8")


def test_hub_contains_all_eight_protocol_steps_and_budgets() -> None:
    hub = _read("SKILL.md")
    required = [
        "### 1. 环境自检",
        "### 2. Startup lock",
        "### 3. 读题、数据剖析与分型",
        "### 4. 拆解",
        "### 5. 模型路线确认",
        "### 6. 契约派发循环",
        "### 7. 阶段推进与返工传播",
        "### 8. 最终评审与提交门禁",
        "每个任务最多返工 2 轮",
        "最终评审最多返工 2 轮",
    ]
    assert [token for token in required if token not in hub] == []


def test_startup_lock_is_actionable_and_blocks_unknown_constraints() -> None:
    hub = _read("SKILL.md")
    for token in (
        "选择哪一道题",
        "`input/` 中哪份是题面",
        "显式交付物",
        "官方规则与赛区补充规则",
        "逐问确认",
        "unknown",
        "blocked",
    ):
        assert token in hub


def test_contract_evidence_and_workflow_references_are_complete() -> None:
    task_contract = _read("references/task-contract.md")
    evidence = _read("references/evidence-ledger.md")
    workflow = _read("references/workflow.md")

    for field in (
        "task_id",
        "subquestion",
        "role",
        "inputs",
        "expected_outputs",
        "acceptance",
        "constraints",
    ):
        assert field in task_contract
    for field in (
        "evidence_id",
        "result_path",
        "code_path",
        "run_log",
        "frozen",
        "superseded_by",
    ):
        assert field in evidence
    for state in ("pending", "ready", "review", "rework", "frozen", "blocked", "superseded"):
        assert f"`{state}`" in workflow


def test_hub_routes_by_isolated_subagent_capability() -> None:
    hub = _read("SKILL.md")
    workflow = _read("references/workflow.md")
    for token in (
        "一个竞赛工作区只选择一个宿主",
        "subagent_capability: available | unavailable",
        "agent_mode: isolated_subagents | sequential_fallback",
        "context_mode: clean_thread | shared_context",
        "reviewer_guard: read_only_enforced | instruction_only",
        'fork_turns="none"',
        "三席全部结束后",
        "只有明确确认宿主版本本身没有 subagent 功能时",
        "fallback_reason: subagent_unavailable",
        "不得把宿主配置错误伪装成",
    ):
        assert token in hub
    for token in (
        "每个竞赛工作区只使用一个宿主",
        "isolated_subagents",
        "sequential_fallback",
        "fallback_reason: subagent_unavailable",
        "必须 `blocked`，不得降级",
        "全部结束后再写评审文件",
    ):
        assert token in workflow


def test_profile_records_official_2026_baseline_and_ai_disclosure() -> None:
    profile = _read("references/cumcm-profile.md")
    required = [
        "2026-07-25",
        "至少 2.5 cm",
        "不超过 30 页",
        "不超过 20MB",
        "AI 工具使用详情",
        "核心建模与分析必须由参赛队独立完成",
        "mcm.edu.cn/html_cn/node/4cd596519c9eb9fbd866398f6df0caa3.html",
        "mcm.edu.cn/html_cn/node/9d8e511fe7a1447b35f53a82c908e2e0.html",
        "mcm.edu.cn/html_cn/node/eebcfb6dc37fd2de9603dc16026fdf01.html",
    ]
    assert [token for token in required if token not in profile] == []
