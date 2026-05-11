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
COMPARE_EXAMPLES = [
    (ROOT / "examples" / "oklo-ai-power-prior.json", ROOT / "examples" / "oklo-ai-power.json"),
]
FIXTURE_OUTPUTS = [
    "oklo-ai-power-brief.md",
    "oklo-ai-power-risk.md",
    "oklo-ai-power-risk.json",
    "oklo-ai-power-history.md",
    "oklo-ai-power-history.json",
    "oklo-ai-power-calendar.md",
    "oklo-ai-power-calendar.json",
    "oklo-ai-power-evidence.md",
    "oklo-ai-power-evidence.json",
    "oklo-ai-power-broker.md",
    "oklo-ai-power-broker.json",
    "oklo-ai-power-exposure.md",
    "oklo-ai-power-exposure.json",
    "oklo-ai-power-decision-memo.md",
    "oklo-ai-power-decision-memo.json",
    "oklo-ai-power-scenario-plan.md",
    "oklo-ai-power-scenario-plan.json",
    "oklo-ai-power-drift.md",
    "oklo-ai-power-drift.json",
    "portfolio-summary.md",
    "portfolio-summary.json",
    "evidence-audit.md",
    "evidence-audit.json",
    "review-queue.md",
    "review-queue.json",
    "watchlist.md",
    "watchlist.json",
    "action-plan.md",
    "action-plan.json",
    "demo-bundle/index.md",
    "demo-bundle/oklo-ai-power-brief.md",
    "demo-bundle/oklo-ai-power-risk.md",
    "demo-bundle/oklo-ai-power-history.md",
    "demo-bundle/oklo-ai-power-decision-memo.md",
    "demo-bundle/oklo-ai-power-scenario-plan.md",
    "demo-bundle/leveraged-etf-discipline-brief.md",
    "demo-bundle/leveraged-etf-discipline-risk.md",
    "demo-bundle/leveraged-etf-discipline-history.md",
    "demo-bundle/leveraged-etf-discipline-decision-memo.md",
    "demo-bundle/leveraged-etf-discipline-scenario-plan.md",
    "demo-bundle/portfolio-summary.md",
    "demo-bundle/evidence-audit.md",
    "demo-bundle/watchlist.md",
    "demo-bundle/action-plan.md",
    "demo-bundle/manifest.json",
    "archive/README.md",
    "archive/oklo-ai-power.json",
    "archive/oklo-ai-power-brief.md",
    "archive/oklo-ai-power-risk.md",
    "archive/oklo-ai-power-history.md",
    "archive/oklo-ai-power-decision.md",
    "archive/oklo-ai-power-scenario.md",
    "archive/leveraged-etf-discipline.json",
    "archive/leveraged-etf-discipline-brief.md",
    "archive/leveraged-etf-discipline-risk.md",
    "archive/leveraged-etf-discipline-history.md",
    "archive/leveraged-etf-discipline-decision.md",
    "archive/leveraged-etf-discipline-scenario.md",
    "archive/portfolio.md",
    "archive/evidence-audit.md",
    "archive/watchlist.md",
    "archive/action-plan.md",
    "archive/manifest.json",
    "archive/archive-summary.json",
    "html-dashboard/index.html",
    "html-dashboard/style.css",
    "html-dashboard/oklo-ai-power.html",
    "html-dashboard/leveraged-etf-discipline.html",
    "html-dashboard/portfolio.html",
    "html-dashboard/evidence-audit.html",
    "html-dashboard/watchlist.html",
    "html-dashboard/action-plan.html",
    "html-dashboard/manifest.json",
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
            _run(
                [
                    sys.executable,
                    "-m",
                    "invest_thesis_ledger",
                    "calendar",
                    str(ledger),
                    "--output",
                    str(temp_dir / f"{stem}-calendar.md"),
                    "--json-output",
                    str(temp_dir / f"{stem}-calendar.json"),
                ]
            )
            _run(
                [
                    sys.executable,
                    "-m",
                    "invest_thesis_ledger",
                    "evidence",
                    str(ledger),
                    "--output",
                    str(temp_dir / f"{stem}-evidence.md"),
                    "--json-output",
                    str(temp_dir / f"{stem}-evidence.json"),
                ]
            )
            _run(
                [
                    sys.executable,
                    "-m",
                    "invest_thesis_ledger",
                    "broker-matrix",
                    str(ledger),
                    "--output",
                    str(temp_dir / f"{stem}-broker.md"),
                    "--json-output",
                    str(temp_dir / f"{stem}-broker.json"),
                ]
            )
            _run(
                [
                    sys.executable,
                    "-m",
                    "invest_thesis_ledger",
                    "exposure",
                    str(ledger),
                    "--output",
                    str(temp_dir / f"{stem}-exposure.md"),
                    "--json-output",
                    str(temp_dir / f"{stem}-exposure.json"),
                ]
            )
            _run(
                [
                    sys.executable,
                    "-m",
                    "invest_thesis_ledger",
                    "decision-memo",
                    str(ledger),
                    "--output",
                    str(temp_dir / f"{stem}-decision-memo.md"),
                    "--json-output",
                    str(temp_dir / f"{stem}-decision-memo.json"),
                ]
            )
            _run(
                [
                    sys.executable,
                    "-m",
                    "invest_thesis_ledger",
                    "scenario-plan",
                    str(ledger),
                    "--output",
                    str(temp_dir / f"{stem}-scenario-plan.md"),
                    "--json-output",
                    str(temp_dir / f"{stem}-scenario-plan.json"),
                ]
            )
            _run(
                [
                    sys.executable,
                    "-m",
                    "invest_thesis_ledger",
                    "init-template",
                    "--asset",
                    "TST",
                    "--name",
                    "Test Asset",
                    "--type",
                    "equity",
                    "--output",
                    str(temp_dir / f"{stem}-template.json"),
                ]
            )
            _run(
                [
                    sys.executable,
                    "-m",
                    "invest_thesis_ledger",
                    "validate",
                    str(temp_dir / f"{stem}-template.json"),
                ]
            )
        for old_ledger, new_ledger in COMPARE_EXAMPLES:
            stem = new_ledger.stem
            _run(
                [
                    sys.executable,
                    "-m",
                    "invest_thesis_ledger",
                    "compare",
                    str(old_ledger),
                    str(new_ledger),
                    "--output",
                    str(temp_dir / f"{stem}-drift.md"),
                    "--json-output",
                    str(temp_dir / f"{stem}-drift.json"),
                ]
            )
        _run(
            [
                sys.executable,
                "-m",
                "invest_thesis_ledger",
                "portfolio",
                str(EXAMPLES[0]),
                str(EXAMPLES[1]),
                "--output",
                str(temp_dir / "portfolio-summary.md"),
                "--json-output",
                str(temp_dir / "portfolio-summary.json"),
            ]
        )
        _run(
            [
                sys.executable,
                "-m",
                "invest_thesis_ledger",
                "evidence-audit",
                str(EXAMPLES[0]),
                str(EXAMPLES[1]),
                "--output",
                str(temp_dir / "evidence-audit.md"),
                "--json-output",
                str(temp_dir / "evidence-audit.json"),
            ]
        )
        _run(
            [
                sys.executable,
                "-m",
                "invest_thesis_ledger",
                "review-queue",
                str(EXAMPLES[0]),
                str(EXAMPLES[1]),
                "--output",
                str(temp_dir / "review-queue.md"),
                "--json-output",
                str(temp_dir / "review-queue.json"),
            ]
        )
        _run(
            [
                sys.executable,
                "-m",
                "invest_thesis_ledger",
                "watchlist",
                str(EXAMPLES[0]),
                str(EXAMPLES[1]),
                "--output",
                str(temp_dir / "watchlist.md"),
                "--json-output",
                str(temp_dir / "watchlist.json"),
            ]
        )
        _run(
            [
                sys.executable,
                "-m",
                "invest_thesis_ledger",
                "action-plan",
                str(EXAMPLES[0]),
                str(EXAMPLES[1]),
                "--output",
                str(temp_dir / "action-plan.md"),
                "--json-output",
                str(temp_dir / "action-plan.json"),
            ]
        )
        _run(
            [
                sys.executable,
                "-m",
                "invest_thesis_ledger",
                "demo-bundle",
                str(EXAMPLES[0]),
                str(EXAMPLES[1]),
                "--output-dir",
                str(temp_dir / "demo-bundle"),
            ]
        )
        _run(
            [
                sys.executable,
                "-m",
                "invest_thesis_ledger",
                "archive",
                str(EXAMPLES[0]),
                str(EXAMPLES[1]),
                "--output-dir",
                str(temp_dir / "archive"),
            ]
        )
        _run([sys.executable, "-m", "invest_thesis_ledger", "verify-archive", str(temp_dir / "archive")])
        _run(
            [
                sys.executable,
                "-m",
                "invest_thesis_ledger",
                "html-dashboard",
                str(EXAMPLES[0]),
                str(EXAMPLES[1]),
                "--output-dir",
                str(temp_dir / "html-dashboard"),
            ]
        )
        _check_fixtures(temp_dir)
        _run([sys.executable, "-m", "unittest", "discover", "-s", str(ROOT / "tests")])
    print("selfcheck: ok")
    return 0


def _run(command: list[str]) -> None:
    subprocess.run(command, cwd=ROOT, check=True)


def _check_fixtures(temp_dir: Path) -> None:
    output_dir = ROOT / "examples" / "output"
    drifted = []
    for filename in FIXTURE_OUTPUTS:
        generated = temp_dir / filename
        checked_in = output_dir / filename
        if generated.read_text(encoding="utf-8") != checked_in.read_text(encoding="utf-8"):
            drifted.append(filename)
    if drifted:
        raise SystemExit("selfcheck: fixture drift: " + ", ".join(drifted))


if __name__ == "__main__":
    raise SystemExit(main())
