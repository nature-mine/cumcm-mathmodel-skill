from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "cumcm-env-doctor" / "scripts" / "check_env.py"


def _load_env_doctor() -> ModuleType:
    spec = importlib.util.spec_from_file_location("cumcm_env_doctor_check_env", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENV_DOCTOR = _load_env_doctor()


def _mock_all_available(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(ENV_DOCTOR.importlib.util, "find_spec", lambda _name: object())
    monkeypatch.setattr(ENV_DOCTOR.importlib.metadata, "version", lambda _name: "1.2.3")
    monkeypatch.setattr(ENV_DOCTOR.shutil, "which", lambda name: f"/mock/bin/{name}")
    monkeypatch.setattr(
        ENV_DOCTOR,
        "_find_cjk_fonts",
        lambda: ("Noto Sans CJK SC",),
    )


def _tier_checks(report: dict[str, object], tier_name: str) -> list[dict[str, str]]:
    tiers = report["tiers"]
    assert isinstance(tiers, dict)
    tier = tiers[tier_name]
    assert isinstance(tier, dict)
    checks = tier["checks"]
    assert isinstance(checks, list)
    return checks


def test_all_required_checks_green_and_reports_are_written(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _mock_all_available(monkeypatch)

    result = ENV_DOCTOR.main(
        [
            "--workspace",
            str(tmp_path),
            "--skill-pack-root",
            str(ROOT),
            "--network-channel",
            "WebSearch",
            "--network-channel",
            "WebSearch",
        ]
    )

    assert result == 0
    report = json.loads((tmp_path / "env_report.json").read_text(encoding="utf-8"))
    markdown = (tmp_path / "env_report.md").read_text(encoding="utf-8")
    assert report["overall_status"] == "OK"
    assert report["network"]["channels"] == ["WebSearch"]
    assert all(check["status"] == "OK" for check in _tier_checks(report, "tier0"))
    assert "可进入 hub startup lock" in markdown


def test_missing_tier0_package_blocks_but_preserves_diagnostics(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _mock_all_available(monkeypatch)
    monkeypatch.setattr(
        ENV_DOCTOR.importlib.util,
        "find_spec",
        lambda name: None if name == "numpy" else object(),
    )

    report = ENV_DOCTOR.build_report(tmp_path, ROOT, [])
    markdown_path, json_path = ENV_DOCTOR.write_reports(report, tmp_path)

    numpy_check = next(
        check for check in _tier_checks(report, "tier0") if check["key"] == "numpy"
    )
    assert report["overall_status"] == "BLOCKED"
    assert numpy_check["status"] == "MISS"
    assert json_path.is_file()
    assert markdown_path.is_file()
    assert "正式读题与建模必须停止" in markdown_path.read_text(encoding="utf-8")


def test_tier2_and_network_gaps_are_degraded_not_blocking(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _mock_all_available(monkeypatch)
    monkeypatch.setattr(
        ENV_DOCTOR.shutil,
        "which",
        lambda name: "/mock/bin/uv" if name == "uv" else None,
    )
    monkeypatch.setattr(ENV_DOCTOR, "_find_cjk_fonts", lambda: ())

    report = ENV_DOCTOR.build_report(tmp_path, ROOT, [])

    assert report["overall_status"] == "OK"
    assert report["network"]["status"] == "DEGRADED"
    assert all(check["status"] == "DEGRADED" for check in _tier_checks(report, "tier2"))


def test_workspace_must_be_an_existing_directory(
    tmp_path: Path,
) -> None:
    not_a_directory = tmp_path / "input.txt"
    not_a_directory.write_text("input", encoding="utf-8")

    with pytest.raises(SystemExit) as error:
        ENV_DOCTOR.main(["--workspace", str(not_a_directory)])

    assert error.value.code == 2
    assert not (tmp_path / "env_report.json").exists()
    assert not (tmp_path / "env_report.md").exists()


def test_network_channel_rejects_control_characters(tmp_path: Path) -> None:
    with pytest.raises(SystemExit) as error:
        ENV_DOCTOR.main(
            [
                "--workspace",
                str(tmp_path),
                "--network-channel",
                "WebSearch\nforged",
            ]
        )

    assert error.value.code == 2
