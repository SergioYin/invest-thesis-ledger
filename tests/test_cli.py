from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "oklo-ai-power.json"
PRIOR_EXAMPLE = ROOT / "examples" / "oklo-ai-power-prior.json"
OUTPUT = ROOT / "examples" / "output"


class CliTests(unittest.TestCase):
    def run_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-m", "invest_thesis_ledger", *args],
            cwd=ROOT,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    def test_validate_example(self) -> None:
        result = self.run_cli("validate", str(EXAMPLE))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("ledger: oklo-ai-power", result.stdout)
        self.assertIn("reviews: 2", result.stdout)
        self.assertIn("status: valid", result.stdout)

    def test_command_help_describes_inputs_and_outputs(self) -> None:
        compare = self.run_cli("compare", "--help")
        self.assertEqual(compare.returncode, 0, compare.stderr)
        self.assertIn("OLD_LEDGER", compare.stdout)
        self.assertIn("current ledger JSON file", compare.stdout)
        self.assertIn("write JSON output to PATH", compare.stdout)

        brief = self.run_cli("brief", "--help")
        self.assertEqual(brief.returncode, 0, brief.stderr)
        self.assertIn("LEDGER", brief.stdout)
        self.assertIn("write Markdown output to PATH", brief.stdout)

    def test_brief_is_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            output_a = Path(temp) / "brief-a.md"
            output_b = Path(temp) / "brief-b.md"
            first = self.run_cli("brief", str(EXAMPLE), "--output", str(output_a))
            second = self.run_cli("brief", str(EXAMPLE), "--output", str(output_b))
            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertEqual(output_a.read_text(), output_b.read_text())
            self.assertIn("## Sources", output_a.read_text())

    def test_risk_writes_markdown_and_json(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            md_path = Path(temp) / "risk.md"
            json_path = Path(temp) / "risk.json"
            result = self.run_cli(
                "risk",
                str(EXAMPLE),
                "--output",
                str(md_path),
                "--json-output",
                str(json_path),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("# Risk Report", md_path.read_text())
            payload = json.loads(json_path.read_text())
            self.assertEqual(payload["thesis_id"], "oklo-ai-power")
            self.assertEqual(payload["risks"][0]["id"], "R1")

    def test_history_sorts_reviews(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            md_path = Path(temp) / "history.md"
            json_path = Path(temp) / "history.json"
            result = self.run_cli(
                "history",
                str(EXAMPLE),
                "--output",
                str(md_path),
                "--json-output",
                str(json_path),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("# History", md_path.read_text())
            payload = json.loads(json_path.read_text())
            dates = [review["date"] for review in payload["reviews"]]
            self.assertEqual(dates, sorted(dates))

    def test_calendar_writes_dated_catalysts(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            md_path = Path(temp) / "calendar.md"
            json_path = Path(temp) / "calendar.json"
            result = self.run_cli(
                "calendar",
                str(EXAMPLE),
                "--output",
                str(md_path),
                "--json-output",
                str(json_path),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("# Catalyst Calendar", md_path.read_text())
            payload = json.loads(json_path.read_text())
            self.assertEqual(payload["catalysts"][0]["id"], "CAT2")
            self.assertEqual(payload["catalysts"][0]["date"], "2026-08-15")

    def test_evidence_reports_coverage_and_stale_sources(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            temp_dir = Path(temp)
            ledger_path = temp_dir / "ledger.json"
            data = json.loads(EXAMPLE.read_text())
            data["sources"][0]["date"] = "2025-01-01"
            ledger_path.write_text(json.dumps(data), encoding="utf-8")
            md_path = temp_dir / "evidence.md"
            json_path = temp_dir / "evidence.json"
            result = self.run_cli(
                "evidence",
                str(ledger_path),
                "--output",
                str(md_path),
                "--json-output",
                str(json_path),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("## Stale Sources", md_path.read_text())
            payload = json.loads(json_path.read_text())
            self.assertEqual(payload["coverage"]["stale_source_count"], 1)
            self.assertEqual(payload["stale_sources"][0]["id"], "S1")

    def test_evidence_stale_sources_are_based_on_ledger_updated(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            temp_dir = Path(temp)
            ledger_path = temp_dir / "ledger.json"
            data = json.loads(EXAMPLE.read_text())
            data["updated"] = "2025-01-02"
            data["sources"][0]["date"] = "2024-09-01"
            ledger_path.write_text(json.dumps(data), encoding="utf-8")
            json_path = temp_dir / "evidence.json"
            result = self.run_cli(
                "evidence",
                str(ledger_path),
                "--output",
                str(temp_dir / "evidence.md"),
                "--json-output",
                str(json_path),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(json_path.read_text())
            self.assertEqual(payload["coverage"]["stale_source_count"], 0)
            self.assertEqual(payload["stale_sources"], [])

    def test_compare_reports_assumption_risk_review_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            temp_dir = Path(temp)
            old_path = temp_dir / "old.json"
            new_path = temp_dir / "new.json"
            old_data = json.loads(EXAMPLE.read_text())
            new_data = json.loads(EXAMPLE.read_text())
            old_data["assumptions"] = old_data["assumptions"][:1]
            new_data["assumptions"][0]["confidence"] = "high"
            new_data["risks"][0]["probability"] = "high"
            old_data["reviews"] = old_data["reviews"][:1]
            old_path.write_text(json.dumps(old_data), encoding="utf-8")
            new_path.write_text(json.dumps(new_data), encoding="utf-8")
            md_path = temp_dir / "drift.md"
            json_path = temp_dir / "drift.json"
            result = self.run_cli(
                "compare",
                str(old_path),
                str(new_path),
                "--output",
                str(md_path),
                "--json-output",
                str(json_path),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("# Thesis Drift", md_path.read_text())
            payload = json.loads(json_path.read_text())
            self.assertEqual(payload["assumptions"]["changed"][0]["id"], "A1")
            self.assertEqual(payload["risks"]["changed"][0]["id"], "R1")
            self.assertEqual(payload["reviews"]["added"][0]["id"], "REV2:2026-06-30")

    def test_compare_review_fallback_ids_do_not_depend_on_input_order(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            temp_dir = Path(temp)
            old_path = temp_dir / "old.json"
            new_path = temp_dir / "new.json"
            old_data = json.loads(EXAMPLE.read_text())
            new_data = json.loads(EXAMPLE.read_text())
            old_data["reviews"] = list(reversed(old_data["reviews"]))
            new_data["reviews"] = list(reversed(new_data["reviews"]))
            old_path.write_text(json.dumps(old_data), encoding="utf-8")
            new_path.write_text(json.dumps(new_data), encoding="utf-8")
            result = self.run_cli(
                "compare",
                str(old_path),
                str(new_path),
                "--output",
                str(temp_dir / "drift.md"),
                "--json-output",
                str(temp_dir / "drift.json"),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads((temp_dir / "drift.json").read_text())
            self.assertEqual(payload["reviews"]["added"], [])
            self.assertEqual(payload["reviews"]["removed"], [])
            self.assertEqual(payload["reviews"]["changed"], [])

    def test_demo_output_fixtures_match_cli(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            temp_dir = Path(temp)
            commands = [
                (
                    "brief",
                    [
                        "brief",
                        str(EXAMPLE),
                        "--output",
                        str(temp_dir / "oklo-ai-power-brief.md"),
                    ],
                    ["oklo-ai-power-brief.md"],
                ),
                (
                    "risk",
                    [
                        "risk",
                        str(EXAMPLE),
                        "--output",
                        str(temp_dir / "oklo-ai-power-risk.md"),
                        "--json-output",
                        str(temp_dir / "oklo-ai-power-risk.json"),
                    ],
                    ["oklo-ai-power-risk.md", "oklo-ai-power-risk.json"],
                ),
                (
                    "history",
                    [
                        "history",
                        str(EXAMPLE),
                        "--output",
                        str(temp_dir / "oklo-ai-power-history.md"),
                        "--json-output",
                        str(temp_dir / "oklo-ai-power-history.json"),
                    ],
                    ["oklo-ai-power-history.md", "oklo-ai-power-history.json"],
                ),
                (
                    "calendar",
                    [
                        "calendar",
                        str(EXAMPLE),
                        "--output",
                        str(temp_dir / "oklo-ai-power-calendar.md"),
                        "--json-output",
                        str(temp_dir / "oklo-ai-power-calendar.json"),
                    ],
                    ["oklo-ai-power-calendar.md", "oklo-ai-power-calendar.json"],
                ),
                (
                    "evidence",
                    [
                        "evidence",
                        str(EXAMPLE),
                        "--output",
                        str(temp_dir / "oklo-ai-power-evidence.md"),
                        "--json-output",
                        str(temp_dir / "oklo-ai-power-evidence.json"),
                    ],
                    ["oklo-ai-power-evidence.md", "oklo-ai-power-evidence.json"],
                ),
                (
                    "compare",
                    [
                        "compare",
                        str(PRIOR_EXAMPLE),
                        str(EXAMPLE),
                        "--output",
                        str(temp_dir / "oklo-ai-power-drift.md"),
                        "--json-output",
                        str(temp_dir / "oklo-ai-power-drift.json"),
                    ],
                    ["oklo-ai-power-drift.md", "oklo-ai-power-drift.json"],
                ),
            ]
            for label, args, filenames in commands:
                result = self.run_cli(*args)
                self.assertEqual(result.returncode, 0, f"{label}: {result.stderr}")
                for filename in filenames:
                    self.assertEqual(
                        (temp_dir / filename).read_text(),
                        (OUTPUT / filename).read_text(),
                        filename,
                    )

    def test_invalid_unknown_source_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            bad_path = Path(temp) / "bad.json"
            data = json.loads(EXAMPLE.read_text())
            data["risks"][0]["source_ids"] = ["missing"]
            bad_path.write_text(json.dumps(data), encoding="utf-8")
            result = self.run_cli("validate", str(bad_path))
            self.assertEqual(result.returncode, 1)
            self.assertIn("unknown source missing", result.stdout)

    def test_invalid_catalyst_source_ids_fail(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            bad_path = Path(temp) / "bad.json"
            data = json.loads(EXAMPLE.read_text())
            data["catalysts"][0]["source_ids"] = ["S1", "S1", "missing"]
            data["catalysts"][1]["source_ids"] = "S2"
            bad_path.write_text(json.dumps(data), encoding="utf-8")
            result = self.run_cli("validate", str(bad_path))
            self.assertEqual(result.returncode, 1)
            self.assertIn("ledger.catalysts[0].source_ids has duplicate source S1", result.stdout)
            self.assertIn("ledger.catalysts[0].source_ids references unknown source missing", result.stdout)
            self.assertIn("ledger.catalysts[1].source_ids must be a list", result.stdout)


if __name__ == "__main__":
    unittest.main()
