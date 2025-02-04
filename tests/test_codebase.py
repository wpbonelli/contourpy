from __future__ import annotations

import re
from subprocess import run

from packaging.version import Version
import pytest

import contourpy


# From PEP440 appendix.
def version_is_canonical(version: str) -> bool:
    return re.match(
        r"^([1-9][0-9]*!)?(0|[1-9][0-9]*)(\.(0|[1-9][0-9]*))*((a|b|rc)(0|[1-9][0-9]*))?"
        r"(\.post(0|[1-9][0-9]*))?(\.dev(0|[1-9][0-9]*))?$", version) is not None


def test_cppcheck() -> None:
    # Skip test if cppcheck is not installed.
    cmd = ["cppcheck", "--version"]
    try:
        proc = run(cmd, capture_output=True)
    except FileNotFoundError:
        pytest.skip()

    cpp_version = Version(proc.stdout.decode("utf-8").strip().split()[-1])

    # Note excluding mpl2005 code.
    cmd = [
        "cppcheck", "--quiet", "--enable=all", "--error-exitcode=1", "src",
        "-isrc/mpl2005_original.cpp", "--suppress=missingIncludeSystem", "--inline-suppr"]

    if cpp_version >= Version("2.7"):
        cmd += ["--suppress=assertWithSideEffect"]

    proc = run(cmd, capture_output=True)
    assert proc.returncode == 0, f"cppcheck issues:\n{proc.stderr.decode('utf-8')}"


def test_mypy() -> None:
    # Skip test if mypy is not installed.
    cmd = ["mypy", "--version"]
    try:
        proc = run(cmd, capture_output=True)
    except FileNotFoundError:
        pytest.skip()

    cmd = ["mypy"]
    proc = run(cmd, capture_output=True)
    assert proc.returncode == 0, print(f"mypy issues:\n{proc.stdout.decode('utf-8')}")


def test_version() -> None:
    version_python = contourpy.__version__
    assert version_is_canonical(version_python)
    version_cxx = contourpy._contourpy.__version__
    assert version_python == version_cxx
