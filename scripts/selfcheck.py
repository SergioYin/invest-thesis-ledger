#!/usr/bin/env python3
"""Run deterministic local checks for the project."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = [
    ROOT / "examples" / "oklo-ai-power.json",
    ROOT / "examples" / "leveraged-etf-discipline.json",
]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="invest-thesis-ledger-") as temp:
        temp_dir = Path(temp)
        for ledger in EXAMPLES:
            _run([sys.executable, "-m", "invest_thesis_ledger", "validate", str(ledger)])
            stem = ledger.stem
            _run(
                [
                    sys.executable,
                    "-m",
                    "invest_thesis_ledger",
                    "brief",
                    str(ledger),
                    "--output",
                    str(temp_dir / f"{stem}-brief.md"),
                ]
            )
            _run(
                [
                    sys.executable,
                    "-m",
                    "invest_thesis_ledger",
                    "risk",
                    str(ledger),
                    "--output",
                    str(temp_dir / f"{stem}-risk.md"),
                    "--json-output",
                    str(temp_dir / f"{stem}-risk.json"),
                ]
            )
            _run(
                [
                    sys.executable,
                    "-m",
                    "invest_thesis_ledger",
                    "history",
                    str(ledger),
                    "--output",
                    str(temp_dir / f"{stem}-history.md"),
                    "--json-output",
                    str(temp_dir / f"{stem}-history.json"),
                ]
            )
        _run([sys.executable, "-m", "unittest", "discover", "-s", str(ROOT / "tests")])
    print("selfcheck: ok")
    return 0


def _run(command: list[str]) -> None:
    subprocess.run(command, cwd=ROOT, check=True)


if __name__ == "__main__":
    raise SystemExit(main())
