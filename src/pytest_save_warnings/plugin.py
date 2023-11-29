import copy
import json
from typing import Tuple
from typing import TYPE_CHECKING
from typing import Union

import pytest

if TYPE_CHECKING:
    from _pytest.terminal import WarningReport
    from _pytest.terminal import TerminalReporter


def pytest_addoption(parser: pytest.Parser):
    group = parser.getgroup("save warnings")
    group.addoption(
        "--save-warnings-output",
        default="warnings.txt",
        help="Path of file to save warnings to.",
    )


@pytest.hookimpl(hookwrapper=True)
def pytest_terminal_summary(
    terminalreporter: "TerminalReporter", exitstatus: int, config: pytest.Config
):
    # let the teardown phase run
    yield
    all_warnings = terminalreporter.stats.get("warnings") or []
    output_path = config.option.save_warnings_output
    with open(output_path, "w") as f:
        for wr in all_warnings:
            relpath, lineno = _get_relpath_and_lineno(wr, config)
            row = {
                "nodeid": wr.nodeid,
                "path": relpath,
                "line": lineno,
                "message": wr.message.strip(),
            }
            f.write(json.dumps(row))
            f.write("\n")


def _get_relpath_and_lineno(
    warning_report: "WarningReport", config: pytest.Config
) -> Union[Tuple[str, int], Tuple[None, None]]:
    without_nodeid = copy.copy(warning_report)
    without_nodeid.nodeid = None
    location = without_nodeid.get_location(config)
    if not location:
        return (None, None)
    parts = location[::-1].split(":", 1)
    if not len(parts) == 2:
        return (None, None)
    lineno, relpath = parts
    return (relpath[::-1], int(lineno[::-1], 10))
