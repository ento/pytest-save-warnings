import json
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    try:
        from pytest import Pytester
    except ImportError:
        from _pytest.pytester import Pytester


def test_output_format(pytester: "Pytester", tmp_path: Path):
    pytester.copy_example("test_output_format.py")
    output_path = tmp_path / "warnings.txt"

    pytester.runpytest("--save-warnings-output", output_path)

    assert output_path.exists()
    lines = [line for line in output_path.read_text().splitlines() if line.strip()]
    assert len(lines) == 1
    warning = json.loads(lines[0])
    assert warning["nodeid"] == "test_output_format.py::test_with_warning"
    assert warning["path"] == "test_output_format.py"
    assert warning["line"] == 5
    assert "UserWarning: Warning from test body" in warning["message"]


def test_warning_during_import_gets_captured(pytester: "Pytester", tmp_path: Path):
    pytester.copy_example("test_warning_during_import_gets_captured.py")
    output_path = tmp_path / "warnings.txt"

    pytester.runpytest("--save-warnings-output", output_path)

    assert output_path.exists()
    lines = [line for line in output_path.read_text().splitlines() if line.strip()]
    assert len(lines) == 1
    warning = json.loads(lines[0])
    assert warning["nodeid"] == ""
    assert warning["path"] == "test_warning_during_import_gets_captured.py"
    assert warning["line"] == 3
    assert "UserWarning: Warning from module import" in warning["message"]


def test_warning_during_terminal_summary_gets_captured(
    pytester: "Pytester", tmp_path: Path
):
    pytester.makeconftest(
        """
import warnings

import pytest

@pytest.hookimpl
def pytest_terminal_summary(terminalreporter, exitstatus, config):
    warnings.warn("Warning from teardown")
    """
    )
    output_path = tmp_path / "warnings.txt"

    pytester.runpytest("--save-warnings-output", output_path)

    assert output_path.exists()
    lines = [line for line in output_path.read_text().splitlines() if line.strip()]
    assert len(lines) == 1
    warning = json.loads(lines[0])
    assert warning["nodeid"] == ""
    assert warning["path"] == "conftest.py"
    assert warning["line"] == 7
    assert "UserWarning: Warning from teardown" in warning["message"]
