from __future__ import annotations

import hashlib
import importlib.util
import json
import stat
import sys
import zipfile
from pathlib import Path
from types import ModuleType

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate_smoke_workspace.py"


def _load_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("validate_smoke_workspace", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_docx(path: Path) -> None:
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("word/document.xml", "<w:document>源程序：solver.py</w:document>")
        archive.writestr("word/footer1.xml", "<w:instrText> PAGE </w:instrText>")


def _prepare_workspace(tmp_path: Path) -> tuple[Path, Path, Path]:
    workspace = tmp_path / "smoke"
    source = tmp_path / "source"
    for dirname in (
        "code",
        "contracts",
        "data",
        "evidence",
        "figures",
        "input",
        "paper",
        "reports",
        "results",
        "reviews",
        "support",
    ):
        (workspace / dirname).mkdir(parents=True)
    source.mkdir()

    problem_source = source / "problem.pdf"
    attachment_source = source / "attachment.xlsx"
    problem_source.write_bytes(b"problem")
    attachment_source.write_bytes(b"attachment")
    for source_path in (problem_source, attachment_source):
        target = workspace / "input" / source_path.name
        target.write_bytes(source_path.read_bytes())
        target.chmod(stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)

    (workspace / "env_report.md").write_text("OK\n", encoding="utf-8")
    (workspace / "env_report.json").write_text(
        json.dumps(
            {
                "overall_status": "OK",
                "tiers": {
                    "tier0": {
                        "summary": {"ok": 2, "miss": 0, "degraded": 0, "total": 2}
                    }
                },
            }
        ),
        encoding="utf-8",
    )
    (workspace / "plan.md").write_text("route confirmed\n", encoding="utf-8")
    (workspace / "todo.md").write_text(
        "\n".join(f"| T{index} | task | role | dep | frozen | out |" for index in range(8)),
        encoding="utf-8",
    )
    (workspace / "data_profile.md").write_text("three sheets\n", encoding="utf-8")
    (workspace / "data_profile.json").write_text(
        json.dumps(
            {
                "sheet_count": 3,
                "sheets": {
                    "S1": {"n_rows": 1, "n_cols": 2},
                    "S2": {"n_rows": 2, "n_cols": 3},
                    "S3": {"n_rows": 3, "n_cols": 4},
                },
            }
        ),
        encoding="utf-8",
    )
    (workspace / "ai_usage_log.md").write_text("logged\n", encoding="utf-8")
    (workspace / "evidence/ledger.md").write_text(
        "\n".join(
            f"| E-P{index}-001 | P{index} | claim | value | result | code | run | fig | review | frozen | — |"
            for index in range(1, 5)
        ),
        encoding="utf-8",
    )
    (workspace / "figure_registry.md").write_text(
        "\n".join(
            (
                "| id | lane | type | status | claim | source | method | chapter | path | provenance | review |",
                "|---|---|---|---|---|---|---|---|---|---|---|",
                "| FIG-P1-01 | A | plot | done | claim | source | method | 1 | figures/result.png | prov | review |",
                "| FIG-G-01 | B | roadmap | draft | claim | source | method | 2 | figures/FIG-G-01.drawio | prov | review |",
                "| FIG-G-02 | C | concept | placeholder | claim | source | method | 3 | figures/FIG-G-02_placeholder.md | prov | review |",
            )
        ),
        encoding="utf-8",
    )
    (workspace / "figures/FIG-G-02_placeholder.md").write_text(
        "- 拟放章节：3\n",
        encoding="utf-8",
    )
    (workspace / "figures/FIG-G-02_prompt.json").write_text(
        json.dumps({"chapter": "3"}),
        encoding="utf-8",
    )
    (workspace / "code/solver.py").write_text("print('ok')\n", encoding="utf-8")
    for index in range(6):
        (workspace / f"contracts/TASK-{index}.md").write_text(
            "contract\n",
            encoding="utf-8",
        )
    for index in range(4):
        (workspace / f"reports/analysis_modeling_P{index + 1}.md").write_text(
            "model\n",
            encoding="utf-8",
        )
        (workspace / f"reviews/review_model_P{index + 1}_round1.md").write_text(
            "verdict: 通过\n",
            encoding="utf-8",
        )
    (workspace / "reports/code_feedback_round1.md").write_text(
        "code feedback\n",
        encoding="utf-8",
    )
    (workspace / "reviews/review_code_round1.md").write_text(
        "verdict: 通过\n",
        encoding="utf-8",
    )
    (workspace / "data/derived.csv").write_text("x\n1\n", encoding="utf-8")
    (workspace / "results/run-log.md").write_text("exit_status: 0\n", encoding="utf-8")
    (workspace / "results/summary.json").write_text(
        json.dumps(
            {
                "valid_classified_samples": 1,
                "valid_artifacts": 1,
                "unknown_samples": 1,
                "q1": {},
                "q2": {},
                "q3": {},
                "q4": {},
            }
        ),
        encoding="utf-8",
    )
    (workspace / "paper/paper.md").write_text(
        "\n".join(
            (
                "# paper",
                "## 1 数据分析",
                '[[FIGURE id="FIG-P1-01" path="figures/result.png" caption="结果"]]',
                "## 2 技术路线",
                '[[PLACEHOLDER id="FIG-G-01" lane="B" chapter="2" expected="车道 B 占位槽"]]',
                "## 3 机制解释",
                '[[PLACEHOLDER id="FIG-G-02" lane="C" chapter="3" expected="机制图占位槽"]]',
            )
        )
        + "\n",
        encoding="utf-8",
    )
    _write_docx(workspace / "paper/cumcm-paper.docx")
    (workspace / "paper/cumcm-paper.pdf").write_bytes(b"%PDF-1.7\n")
    for suffix in ("md", "docx", "pdf"):
        (workspace / f"support/AI工具使用详情.{suffix}").write_bytes(b"detail")
    (workspace / "reviews/review_writing_round1.md").write_text(
        "verdict: 通过\n",
        encoding="utf-8",
    )
    for seat in ("A", "B", "C"):
        (workspace / f"reviews/final_seat_{seat}_round1.md").write_text(
            "reviewer: isolated\nsubmit_ready: yes\n## P0\n- 无。\n## P1\n- 无。\n",
            encoding="utf-8",
        )
    (workspace / "reviews/final_summary_round1.md").write_text(
        "review_mode: isolated_subagents\n三席上下文隔离\n中位数总分：80\n"
        "## P0 并集\n- 空。\n## P1 并集\n- 空。\n",
        encoding="utf-8",
    )

    manifest_paths = (
        ("input/problem.pdf", "input", False),
        ("input/attachment.xlsx", "input", False),
        ("data/derived.csv", "data", True),
        ("code/solver.py", "code", True),
        ("support/AI工具使用详情.pdf", "support", True),
    )
    entries = [
        {
            "path": relative,
            "category": category,
            "included": included,
            "reason": "test",
            "sha256": _sha256(workspace / relative),
        }
        for relative, category, included in manifest_paths
    ]
    (workspace / "paper/support_manifest.json").write_text(
        json.dumps({"schema_version": 1, "entries": entries}),
        encoding="utf-8",
    )
    return workspace, problem_source, attachment_source


def test_validate_smoke_workspace_accepts_complete_external_workspace(
    tmp_path: Path,
) -> None:
    module = _load_module()
    workspace, problem, attachment = _prepare_workspace(tmp_path)

    messages = module.validate_smoke_workspace(
        workspace,
        problem_source=problem,
        attachment_source=attachment,
    )

    assert len(messages) == 10
    assert any("A/B/C=1/1/1" in message for message in messages)
    assert any("input 排除" in message for message in messages)
    assert any("内部流程词" in message for message in messages)
    assert any("registry/占位材料章节一致" in message for message in messages)


def test_validate_smoke_workspace_rejects_writable_input(tmp_path: Path) -> None:
    module = _load_module()
    workspace, problem, attachment = _prepare_workspace(tmp_path)
    (workspace / "input/problem.pdf").chmod(stat.S_IRUSR | stat.S_IWUSR)

    with pytest.raises(module.SmokeValidationFailure, match="仍可写"):
        module.validate_smoke_workspace(
            workspace,
            problem_source=problem,
            attachment_source=attachment,
        )


def test_validate_smoke_workspace_rejects_manifest_hash_mismatch(tmp_path: Path) -> None:
    module = _load_module()
    workspace, problem, attachment = _prepare_workspace(tmp_path)
    (workspace / "data/derived.csv").write_text("changed\n", encoding="utf-8")

    with pytest.raises(module.SmokeValidationFailure, match="SHA-256 不一致"):
        module.validate_smoke_workspace(
            workspace,
            problem_source=problem,
            attachment_source=attachment,
        )


def test_review_validation_accepts_disclosed_sequential_fallback(tmp_path: Path) -> None:
    module = _load_module()
    workspace, _, _ = _prepare_workspace(tmp_path)
    for seat in ("A", "B", "C"):
        path = workspace / f"reviews/final_seat_{seat}_round1.md"
        path.write_text(
            path.read_text(encoding="utf-8").replace(
                "reviewer: isolated",
                "self-review, 独立性受限",
            ),
            encoding="utf-8",
        )
    summary = workspace / "reviews/final_summary_round1.md"
    summary.write_text(
        summary.read_text(encoding="utf-8").replace(
            "review_mode: isolated_subagents\n三席上下文隔离",
            "review_mode: sequential_fallback\n三席非上下文隔离",
        ),
        encoding="utf-8",
    )

    assert "A/B/C 顺序降级评审" in module._validate_reviews_and_status(workspace)


def test_review_validation_rejects_self_review_in_isolated_mode(tmp_path: Path) -> None:
    module = _load_module()
    workspace, _, _ = _prepare_workspace(tmp_path)
    seat_a = workspace / "reviews/final_seat_A_round1.md"
    seat_a.write_text(
        seat_a.read_text(encoding="utf-8").replace(
            "reviewer: isolated",
            "self-review, 独立性受限",
        ),
        encoding="utf-8",
    )

    with pytest.raises(module.SmokeValidationFailure, match="未声明 reviewer: isolated"):
        module._validate_reviews_and_status(workspace)


def test_paper_language_rejects_internal_process_terms_but_exempts_placeholder(
    tmp_path: Path,
) -> None:
    module = _load_module()
    workspace, _, _ = _prepare_workspace(tmp_path)

    assert "PLACEHOLDER 指令已豁免" in module._validate_paper_language(workspace)

    paper = workspace / "paper/paper.md"
    paper.write_text(
        paper.read_text(encoding="utf-8") + "本文进入下一里程碑。\n",
        encoding="utf-8",
    )
    with pytest.raises(module.SmokeValidationFailure, match="里程碑"):
        module._validate_paper_language(workspace)


def test_figure_chapter_validation_rejects_registry_mismatch(tmp_path: Path) -> None:
    module = _load_module()
    workspace, _, _ = _prepare_workspace(tmp_path)
    registry = workspace / "figure_registry.md"
    registry.write_text(
        registry.read_text(encoding="utf-8").replace(
            "| FIG-P1-01 | A | plot | done | claim | source | method | 1 |",
            "| FIG-P1-01 | A | plot | done | claim | source | method | 9 |",
        ),
        encoding="utf-8",
    )

    with pytest.raises(
        module.SmokeValidationFailure,
        match=r"FIG-P1-01 登记章节=9、正文章节=1",
    ):
        module._validate_figure_chapters(workspace)
