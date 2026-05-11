from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from invest_thesis_ledger.render import review_queue_payload


ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "oklo-ai-power.json"
ETF_EXAMPLE = ROOT / "examples" / "leveraged-etf-discipline.json"
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

        init_template = self.run_cli("init-template", "--help")
        self.assertEqual(init_template.returncode, 0, init_template.stderr)
        self.assertIn("--asset", init_template.stdout)
        self.assertIn("write starter ledger JSON to PATH", init_template.stdout)

        portfolio = self.run_cli("portfolio", "--help")
        self.assertEqual(portfolio.returncode, 0, portfolio.stderr)
        self.assertIn("LEDGER", portfolio.stdout)
        self.assertIn("write Markdown output to PATH", portfolio.stdout)
        self.assertIn("write JSON output to PATH", portfolio.stdout)

        review_queue = self.run_cli("review-queue", "--help")
        self.assertEqual(review_queue.returncode, 0, review_queue.stderr)
        self.assertIn("LEDGER", review_queue.stdout)
        self.assertIn("prioritize two or more ledgers", review_queue.stdout)
        self.assertIn("write JSON output to PATH", review_queue.stdout)

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

    def test_broker_matrix_writes_markdown_and_json(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            md_path = Path(temp) / "broker.md"
            json_path = Path(temp) / "broker.json"
            result = self.run_cli(
                "broker-matrix",
                str(EXAMPLE),
                "--output",
                str(md_path),
                "--json-output",
                str(json_path),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("# Broker Matrix", md_path.read_text())
            payload = json.loads(json_path.read_text())
            self.assertEqual(payload["broker_views"][0]["institution"], "Grid Infrastructure Desk")
            self.assertEqual(payload["rating_counts"]["cautious"], 1)

    def test_exposure_maps_risk_tags_and_position_rules(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            md_path = Path(temp) / "exposure.md"
            json_path = Path(temp) / "exposure.json"
            result = self.run_cli(
                "exposure",
                str(EXAMPLE),
                "--output",
                str(md_path),
                "--json-output",
                str(json_path),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("# Exposure Checklist", md_path.read_text())
            payload = json.loads(json_path.read_text())
            self.assertEqual(payload["tag_counts"]["regulatory"], 1)
            self.assertEqual(payload["position_rules"][0]["id"], "P1")
            self.assertIn("RISK-R1", [item["id"] for item in payload["checklist"]])

    def test_portfolio_aggregates_multiple_ledgers(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            md_path = Path(temp) / "portfolio.md"
            json_path = Path(temp) / "portfolio.json"
            result = self.run_cli(
                "portfolio",
                str(EXAMPLE),
                str(ETF_EXAMPLE),
                "--output",
                str(md_path),
                "--json-output",
                str(json_path),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("# Portfolio Summary", md_path.read_text())
            payload = json.loads(json_path.read_text())
            self.assertEqual(payload["portfolio"]["asset_count"], 2)
            self.assertEqual(payload["portfolio"]["thesis_count"], 2)
            self.assertEqual(payload["risk_severity_counts"]["high"], 3)
            self.assertEqual(payload["risk_tag_counts"]["leverage"], 2)
            self.assertEqual(payload["catalyst_status_counts"]["required"], 2)
            self.assertEqual(payload["review_decision_counts"]["watch"], 2)
            self.assertEqual(payload["broker_rating_counts"]["Grid Infrastructure Desk"]["constructive"], 1)
            self.assertEqual(payload["stale_source_warnings"], [])

    def test_portfolio_requires_two_ledgers(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            result = self.run_cli(
                "portfolio",
                str(EXAMPLE),
                "--output",
                str(Path(temp) / "portfolio.md"),
                "--json-output",
                str(Path(temp) / "portfolio.json"),
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("requires at least two", result.stderr)

    def test_portfolio_validates_all_ledgers_before_writing(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            temp_dir = Path(temp)
            bad_path = temp_dir / "bad.json"
            data = json.loads(ETF_EXAMPLE.read_text())
            data["risks"][0]["source_ids"] = ["missing"]
            bad_path.write_text(json.dumps(data), encoding="utf-8")
            md_path = temp_dir / "portfolio.md"
            json_path = temp_dir / "portfolio.json"
            result = self.run_cli(
                "portfolio",
                str(EXAMPLE),
                str(bad_path),
                "--output",
                str(md_path),
                "--json-output",
                str(json_path),
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("ledger: leveraged-etf-discipline", result.stderr)
            self.assertIn("unknown source missing", result.stderr)
            self.assertFalse(md_path.exists())
            self.assertFalse(json_path.exists())

    def test_portfolio_reports_stale_sources(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            temp_dir = Path(temp)
            stale_path = temp_dir / "stale.json"
            data = json.loads(EXAMPLE.read_text())
            data["sources"][0]["date"] = "2025-01-01"
            stale_path.write_text(json.dumps(data), encoding="utf-8")
            json_path = temp_dir / "portfolio.json"
            result = self.run_cli(
                "portfolio",
                str(stale_path),
                str(ETF_EXAMPLE),
                "--output",
                str(temp_dir / "portfolio.md"),
                "--json-output",
                str(json_path),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(json_path.read_text())
            self.assertEqual(payload["stale_source_warnings"][0]["ledger_id"], "oklo-ai-power")
            self.assertEqual(payload["stale_source_warnings"][0]["id"], "S1")

    def test_portfolio_order_does_not_depend_on_input_order_for_tied_items(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            temp_dir = Path(temp)
            first_path = temp_dir / "first.json"
            second_path = temp_dir / "second.json"
            first_data = json.loads(EXAMPLE.read_text())
            second_data = json.loads(ETF_EXAMPLE.read_text())
            for data in (first_data, second_data):
                data["asset"]["ticker"] = "TIE"
                data["catalysts"][0]["id"] = "CATX"
                data["catalysts"][0]["date"] = "2026-07-01"
                data["catalysts"][0]["window"] = "same"
            first_path.write_text(json.dumps(first_data), encoding="utf-8")
            second_path.write_text(json.dumps(second_data), encoding="utf-8")

            forward_md = temp_dir / "forward.md"
            forward_json = temp_dir / "forward.json"
            reverse_md = temp_dir / "reverse.md"
            reverse_json = temp_dir / "reverse.json"
            forward = self.run_cli(
                "portfolio",
                str(first_path),
                str(second_path),
                "--output",
                str(forward_md),
                "--json-output",
                str(forward_json),
            )
            reverse = self.run_cli(
                "portfolio",
                str(second_path),
                str(first_path),
                "--output",
                str(reverse_md),
                "--json-output",
                str(reverse_json),
            )
            self.assertEqual(forward.returncode, 0, forward.stderr)
            self.assertEqual(reverse.returncode, 0, reverse.stderr)
            self.assertEqual(forward_json.read_text(), reverse_json.read_text())
            self.assertEqual(forward_md.read_text(), reverse_md.read_text())

    def test_portfolio_escapes_stale_source_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            temp_dir = Path(temp)
            stale_path = temp_dir / "stale.json"
            data = json.loads(EXAMPLE.read_text())
            data["sources"][0]["date"] = "2025-01-01"
            data["sources"][0]["title"] = "Title | with\nbreak"
            stale_path.write_text(json.dumps(data), encoding="utf-8")
            md_path = temp_dir / "portfolio.md"
            result = self.run_cli(
                "portfolio",
                str(stale_path),
                str(ETF_EXAMPLE),
                "--output",
                str(md_path),
                "--json-output",
                str(temp_dir / "portfolio.json"),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Title \\| with break", md_path.read_text())

    def test_review_queue_scores_and_prioritizes_ledgers(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            md_path = Path(temp) / "review-queue.md"
            json_path = Path(temp) / "review-queue.json"
            result = self.run_cli(
                "review-queue",
                str(EXAMPLE),
                str(ETF_EXAMPLE),
                "--output",
                str(md_path),
                "--json-output",
                str(json_path),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("# Review Queue", md_path.read_text())
            payload = json.loads(json_path.read_text())
            self.assertEqual(payload["queue"]["ledger_count"], 2)
            self.assertEqual(payload["queue"]["high_priority_count"], 2)
            self.assertEqual(payload["items"][0]["thesis_id"], "leveraged-etf-discipline")
            self.assertEqual(payload["items"][0]["score"], 13)
            self.assertEqual(payload["items"][1]["thesis_id"], "oklo-ai-power")
            self.assertEqual(payload["items"][1]["score"], 10)
            self.assertEqual(payload["items"][1]["priority"], "high")
            self.assertIn("high_severity_risks", [reason["type"] for reason in payload["items"][1]["reasons"]])

    def test_review_queue_includes_stale_review_and_stale_source_reasons(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            temp_dir = Path(temp)
            first_path = temp_dir / "first.json"
            second_path = temp_dir / "second.json"
            first_data = json.loads(EXAMPLE.read_text())
            second_data = json.loads(ETF_EXAMPLE.read_text())
            first_data["updated"] = "2026-12-31"
            first_data["sources"][0]["date"] = "2026-01-01"
            first_data["sources"][1]["date"] = "2026-12-01"
            first_data["sources"][2]["date"] = "2026-12-01"
            first_path.write_text(json.dumps(first_data), encoding="utf-8")
            second_path.write_text(json.dumps(second_data), encoding="utf-8")
            json_path = temp_dir / "review-queue.json"
            result = self.run_cli(
                "review-queue",
                str(first_path),
                str(second_path),
                "--output",
                str(temp_dir / "review-queue.md"),
                "--json-output",
                str(json_path),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(json_path.read_text())
            item = next(item for item in payload["items"] if item["thesis_id"] == "oklo-ai-power")
            reasons = {reason["type"]: reason for reason in item["reasons"]}
            self.assertEqual(reasons["stale_sources"]["items"], ["S1"])
            self.assertEqual(reasons["stale_review"]["score"], 3)
            self.assertEqual(item["next_action"], "Run a human review and record a new review entry.")

    def test_review_queue_priority_boundaries_and_reason_order_are_documented(self) -> None:
        def ledger_with_score(thesis_id: str, ticker: str, risk_count: int, checklist_count: int, rule_count: int) -> dict:
            ledger = json.loads(EXAMPLE.read_text())
            ledger["thesis_id"] = thesis_id
            ledger["title"] = thesis_id
            ledger["asset"]["ticker"] = ticker
            ledger["updated"] = "2026-05-12"
            for source in ledger["sources"]:
                source["date"] = "2026-05-12"
            ledger["reviews"] = [
                {
                    "date": "2026-05-12",
                    "decision": "hold",
                    "summary": "Current review.",
                    "source_ids": ["S1"],
                }
            ]
            ledger["risks"] = [
                {
                    "id": f"R{index}",
                    "name": f"Risk {index}",
                    "severity": "high",
                    "probability": "medium",
                    "mitigation": "Monitor.",
                    "source_ids": ["S1"],
                }
                for index in range(1, risk_count + 1)
            ]
            ledger["catalysts"] = []
            ledger["checklist"] = [
                {"id": f"C{index}", "item": f"Checklist {index}", "status": "open"}
                for index in range(checklist_count, 0, -1)
            ]
            ledger["position_rules"] = [
                {
                    "id": f"P{index}",
                    "rule": f"Rule {index}",
                    "status": "open",
                    "source_ids": ["S1"],
                }
                for index in range(rule_count, 0, -1)
            ]
            return ledger

        payload = review_queue_payload(
            [
                ledger_with_score("low-score", "LOW", risk_count=0, checklist_count=0, rule_count=0),
                ledger_with_score("medium-score", "MED", risk_count=1, checklist_count=1, rule_count=0),
                ledger_with_score("high-score", "HI", risk_count=2, checklist_count=1, rule_count=1),
            ]
        )
        by_id = {item["thesis_id"]: item for item in payload["items"]}
        self.assertEqual((by_id["low-score"]["score"], by_id["low-score"]["priority"]), (0, "low"))
        self.assertEqual((by_id["medium-score"]["score"], by_id["medium-score"]["priority"]), (4, "medium"))
        self.assertEqual((by_id["high-score"]["score"], by_id["high-score"]["priority"]), (8, "high"))
        self.assertEqual(
            [reason["type"] for reason in by_id["high-score"]["reasons"]],
            ["high_severity_risks", "open_checklist", "open_position_rules"],
        )
        self.assertEqual(by_id["high-score"]["reasons"][1]["items"], ["C1"])
        self.assertEqual(by_id["high-score"]["reasons"][2]["items"], ["P1"])

    def test_review_queue_escapes_markdown_headings(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            temp_dir = Path(temp)
            first_path = temp_dir / "first.json"
            second_path = temp_dir / "second.json"
            first_data = json.loads(EXAMPLE.read_text())
            first_data["title"] = "Title | with\nbreak"
            first_path.write_text(json.dumps(first_data), encoding="utf-8")
            second_path.write_text(ETF_EXAMPLE.read_text(), encoding="utf-8")
            md_path = temp_dir / "review-queue.md"
            result = self.run_cli(
                "review-queue",
                str(first_path),
                str(second_path),
                "--output",
                str(md_path),
                "--json-output",
                str(temp_dir / "review-queue.json"),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("### OKLO - Title \\| with break", md_path.read_text())

    def test_review_queue_requires_two_ledgers(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            result = self.run_cli(
                "review-queue",
                str(EXAMPLE),
                "--output",
                str(Path(temp) / "review-queue.md"),
                "--json-output",
                str(Path(temp) / "review-queue.json"),
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("requires at least two", result.stderr)

    def test_review_queue_validates_all_ledgers_before_writing(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            temp_dir = Path(temp)
            bad_path = temp_dir / "bad.json"
            data = json.loads(ETF_EXAMPLE.read_text())
            data["risks"][0]["source_ids"] = ["missing"]
            bad_path.write_text(json.dumps(data), encoding="utf-8")
            md_path = temp_dir / "review-queue.md"
            json_path = temp_dir / "review-queue.json"
            result = self.run_cli(
                "review-queue",
                str(EXAMPLE),
                str(bad_path),
                "--output",
                str(md_path),
                "--json-output",
                str(json_path),
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("ledger: leveraged-etf-discipline", result.stderr)
            self.assertIn("unknown source missing", result.stderr)
            self.assertFalse(md_path.exists())
            self.assertFalse(json_path.exists())

    def test_review_queue_order_does_not_depend_on_input_order_for_tied_items(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            temp_dir = Path(temp)
            first_path = temp_dir / "first.json"
            second_path = temp_dir / "second.json"
            first_data = json.loads(EXAMPLE.read_text())
            second_data = json.loads(ETF_EXAMPLE.read_text())
            first_data["asset"]["ticker"] = "TIE"
            second_data["asset"]["ticker"] = "TIE"
            second_data["risks"][1]["severity"] = "medium"
            first_path.write_text(json.dumps(first_data), encoding="utf-8")
            second_path.write_text(json.dumps(second_data), encoding="utf-8")

            forward_md = temp_dir / "forward.md"
            forward_json = temp_dir / "forward.json"
            reverse_md = temp_dir / "reverse.md"
            reverse_json = temp_dir / "reverse.json"
            forward = self.run_cli(
                "review-queue",
                str(first_path),
                str(second_path),
                "--output",
                str(forward_md),
                "--json-output",
                str(forward_json),
            )
            reverse = self.run_cli(
                "review-queue",
                str(second_path),
                str(first_path),
                "--output",
                str(reverse_md),
                "--json-output",
                str(reverse_json),
            )
            self.assertEqual(forward.returncode, 0, forward.stderr)
            self.assertEqual(reverse.returncode, 0, reverse.stderr)
            self.assertEqual(forward_json.read_text(), reverse_json.read_text())
            self.assertEqual(forward_md.read_text(), reverse_md.read_text())

    def test_review_queue_reports_validation_warnings_without_blocking_output(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            temp_dir = Path(temp)
            warning_path = temp_dir / "warning.json"
            data = json.loads(EXAMPLE.read_text())
            data["reviews"] = list(reversed(data["reviews"]))
            warning_path.write_text(json.dumps(data), encoding="utf-8")
            md_path = temp_dir / "review-queue.md"
            json_path = temp_dir / "review-queue.json"
            result = self.run_cli(
                "review-queue",
                str(warning_path),
                str(ETF_EXAMPLE),
                "--output",
                str(md_path),
                "--json-output",
                str(json_path),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("warning: ledger.reviews are not sorted by date", result.stderr)
            self.assertTrue(md_path.exists())
            self.assertTrue(json_path.exists())

    def test_portfolio_reports_validation_warnings_without_blocking_output(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            temp_dir = Path(temp)
            warning_path = temp_dir / "warning.json"
            data = json.loads(EXAMPLE.read_text())
            data["reviews"] = list(reversed(data["reviews"]))
            warning_path.write_text(json.dumps(data), encoding="utf-8")
            md_path = temp_dir / "portfolio.md"
            json_path = temp_dir / "portfolio.json"
            result = self.run_cli(
                "portfolio",
                str(warning_path),
                str(ETF_EXAMPLE),
                "--output",
                str(md_path),
                "--json-output",
                str(json_path),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("warning: ledger.reviews are not sorted by date", result.stderr)
            self.assertTrue(md_path.exists())
            self.assertTrue(json_path.exists())

    def test_init_template_is_deterministic_and_valid(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            output_a = Path(temp) / "ledger-a.json"
            output_b = Path(temp) / "ledger-b.json"
            first = self.run_cli(
                "init-template",
                "--asset",
                "msft",
                "--name",
                "Microsoft Corporation",
                "--type",
                "equity",
                "--output",
                str(output_a),
            )
            second = self.run_cli(
                "init-template",
                "--asset",
                "msft",
                "--name",
                "Microsoft Corporation",
                "--type",
                "equity",
                "--output",
                str(output_b),
            )
            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertEqual(output_a.read_text(), output_b.read_text())
            payload = json.loads(output_a.read_text())
            self.assertEqual(payload["ledger_version"], "0.5.0")
            self.assertEqual(payload["thesis_id"], "msft-thesis")
            self.assertEqual(payload["sources"][0]["id"], "S1")
            self.assertEqual(payload["assumptions"][0]["source_ids"], ["S1"])
            self.assertEqual(payload["risks"][0]["source_ids"], ["S1"])
            self.assertEqual(payload["reviews"][0]["source_ids"], ["S1"])
            validate = self.run_cli("validate", str(output_a))
            self.assertEqual(validate.returncode, 0, validate.stdout + validate.stderr)

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
                    "broker-matrix",
                    [
                        "broker-matrix",
                        str(EXAMPLE),
                        "--output",
                        str(temp_dir / "oklo-ai-power-broker.md"),
                        "--json-output",
                        str(temp_dir / "oklo-ai-power-broker.json"),
                    ],
                    ["oklo-ai-power-broker.md", "oklo-ai-power-broker.json"],
                ),
                (
                    "exposure",
                    [
                        "exposure",
                        str(EXAMPLE),
                        "--output",
                        str(temp_dir / "oklo-ai-power-exposure.md"),
                        "--json-output",
                        str(temp_dir / "oklo-ai-power-exposure.json"),
                    ],
                    ["oklo-ai-power-exposure.md", "oklo-ai-power-exposure.json"],
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
                (
                    "portfolio",
                    [
                        "portfolio",
                        str(EXAMPLE),
                        str(ETF_EXAMPLE),
                        "--output",
                        str(temp_dir / "portfolio-summary.md"),
                        "--json-output",
                        str(temp_dir / "portfolio-summary.json"),
                    ],
                    ["portfolio-summary.md", "portfolio-summary.json"],
                ),
                (
                    "review-queue",
                    [
                        "review-queue",
                        str(EXAMPLE),
                        str(ETF_EXAMPLE),
                        "--output",
                        str(temp_dir / "review-queue.md"),
                        "--json-output",
                        str(temp_dir / "review-queue.json"),
                    ],
                    ["review-queue.md", "review-queue.json"],
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

    def test_invalid_v3_optional_source_ids_and_tags_fail(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            bad_path = Path(temp) / "bad.json"
            data = json.loads(EXAMPLE.read_text())
            data["broker_views"][0]["source_ids"] = ["missing"]
            data["position_rules"][0]["tags"] = "regulatory"
            data["risks"][0]["tags"] = ["regulatory", 3]
            bad_path.write_text(json.dumps(data), encoding="utf-8")
            result = self.run_cli("validate", str(bad_path))
            self.assertEqual(result.returncode, 1)
            self.assertIn("ledger.broker_views[0].source_ids references unknown source missing", result.stdout)
            self.assertIn("ledger.position_rules[0].tags must be a list", result.stdout)
            self.assertIn("ledger.risks[0].tags entries must be strings", result.stdout)

    def test_invalid_broker_view_source_and_tag_fields_fail(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            bad_path = Path(temp) / "bad.json"
            data = json.loads(EXAMPLE.read_text())
            data["sources"][0]["id"] = ""
            data["broker_views"][0]["id"] = "B1"
            data["broker_views"][0]["rating"] = ["buy"]
            data["broker_views"][0]["source_ids"] = ["S2", "S2", 5]
            data["broker_views"].append(dict(data["broker_views"][0]))
            data["position_rules"][0]["tags"] = ["regulatory", 7]
            bad_path.write_text(json.dumps(data), encoding="utf-8")
            result = self.run_cli("validate", str(bad_path))
            self.assertEqual(result.returncode, 1)
            self.assertIn("ledger.sources has empty id", result.stdout)
            self.assertIn("ledger.broker_views[0].rating must be a string", result.stdout)
            self.assertIn("ledger.broker_views[0].source_ids has duplicate source S2", result.stdout)
            self.assertIn("ledger.broker_views[0].source_ids entries must be strings", result.stdout)
            self.assertIn("ledger.broker_views has duplicate id B1", result.stdout)
            self.assertIn("ledger.position_rules[0].tags entries must be strings", result.stdout)

    def test_broker_and_exposure_markdown_escape_inline_values(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            temp_dir = Path(temp)
            ledger_path = temp_dir / "ledger.json"
            data = json.loads(EXAMPLE.read_text())
            data["sources"][0]["title"] = "Title | with\nbreak"
            data["broker_views"][0]["institution"] = "Desk | Alpha"
            data["broker_views"][0]["thesis"] = "Line one\nLine | two"
            data["risks"][0]["tags"] = ["reg | tag"]
            data["position_rules"][0]["rule"] = "Keep | size\nsmall"
            ledger_path.write_text(json.dumps(data), encoding="utf-8")

            broker_md = temp_dir / "broker.md"
            exposure_md = temp_dir / "exposure.md"
            broker = self.run_cli(
                "broker-matrix",
                str(ledger_path),
                "--output",
                str(broker_md),
                "--json-output",
                str(temp_dir / "broker.json"),
            )
            exposure = self.run_cli(
                "exposure",
                str(ledger_path),
                "--output",
                str(exposure_md),
                "--json-output",
                str(temp_dir / "exposure.json"),
            )
            self.assertEqual(broker.returncode, 0, broker.stderr)
            self.assertEqual(exposure.returncode, 0, exposure.stderr)
            self.assertIn("Desk \\| Alpha", broker_md.read_text())
            self.assertIn("Line one Line \\| two", broker_md.read_text())
            self.assertIn("Title \\| with break", broker_md.read_text())
            self.assertIn("reg \\| tag", exposure_md.read_text())
            self.assertIn("Keep \\| size small", exposure_md.read_text())


if __name__ == "__main__":
    unittest.main()
