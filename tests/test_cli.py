from __future__ import annotations

import contextlib
import io
import json
import hashlib
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
from pathlib import Path

from invest_thesis_ledger import cli as cli_module
from invest_thesis_ledger.cli import _write_demo_bundle_dir
from invest_thesis_ledger.render import (
    action_plan_payload,
    decision_memo_payload,
    review_queue_payload,
    scenario_plan_payload,
    watchlist_payload,
)


ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "oklo-ai-power.json"
ETF_EXAMPLE = ROOT / "examples" / "leveraged-etf-discipline.json"
PRIOR_EXAMPLE = ROOT / "examples" / "oklo-ai-power-prior.json"
OUTPUT = ROOT / "examples" / "output"
ARCHIVE_FIXTURE = OUTPUT / "archive"


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

    def run_cli_in_process(self, *args: str) -> tuple[int, str, str]:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            status = cli_module.main(args)
        return status, stdout.getvalue(), stderr.getvalue()

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

        evidence_audit = self.run_cli("evidence-audit", "--help")
        self.assertEqual(evidence_audit.returncode, 0, evidence_audit.stderr)
        self.assertIn("LEDGER", evidence_audit.stdout)
        self.assertIn("audit portfolio evidence quality", evidence_audit.stdout)
        self.assertIn("write JSON output to PATH", evidence_audit.stdout)

        review_queue = self.run_cli("review-queue", "--help")
        self.assertEqual(review_queue.returncode, 0, review_queue.stderr)
        self.assertIn("LEDGER", review_queue.stdout)
        self.assertIn("prioritize two or more ledgers", review_queue.stdout)
        self.assertIn("write JSON output to PATH", review_queue.stdout)

        watchlist = self.run_cli("watchlist", "--help")
        self.assertEqual(watchlist.returncode, 0, watchlist.stderr)
        self.assertIn("LEDGER", watchlist.stdout)
        self.assertIn("weekly watchlist", watchlist.stdout)
        self.assertIn("write JSON output to PATH", watchlist.stdout)

        action_plan = self.run_cli("action-plan", "--help")
        self.assertEqual(action_plan.returncode, 0, action_plan.stderr)
        self.assertIn("LEDGER", action_plan.stdout)
        self.assertIn("weekly action plan", action_plan.stdout)
        self.assertIn("write JSON output to PATH", action_plan.stdout)

        demo_bundle = self.run_cli("demo-bundle", "--help")
        self.assertEqual(demo_bundle.returncode, 0, demo_bundle.stderr)
        self.assertIn("LEDGER", demo_bundle.stdout)
        self.assertIn("static Markdown demo bundle", demo_bundle.stdout)
        self.assertIn("write static demo bundle to DIR", demo_bundle.stdout)

        html_dashboard = self.run_cli("html-dashboard", "--help")
        self.assertEqual(html_dashboard.returncode, 0, html_dashboard.stderr)
        self.assertIn("LEDGER", html_dashboard.stdout)
        self.assertIn("static no-JS HTML dashboard", html_dashboard.stdout)
        self.assertIn("write static HTML dashboard to DIR", html_dashboard.stdout)

        archive = self.run_cli("archive", "--help")
        self.assertEqual(archive.returncode, 0, archive.stderr)
        self.assertIn("LEDGER", archive.stdout)
        self.assertIn("portable research archive", archive.stdout)
        self.assertIn("write portable archive to DIR", archive.stdout)

        verify_archive = self.run_cli("verify-archive", "--help")
        self.assertEqual(verify_archive.returncode, 0, verify_archive.stderr)
        self.assertIn("ARCHIVE_DIR", verify_archive.stdout)
        self.assertIn("verify a deterministic portable research archive", verify_archive.stdout)

        diff_archive = self.run_cli("diff-archive", "--help")
        self.assertEqual(diff_archive.returncode, 0, diff_archive.stderr)
        self.assertIn("OLD_ARCHIVE_DIR", diff_archive.stdout)
        self.assertIn("NEW_ARCHIVE_DIR", diff_archive.stdout)
        self.assertIn("compare two deterministic portable research archives", diff_archive.stdout)
        self.assertIn("write Markdown output to PATH", diff_archive.stdout)
        self.assertIn("write JSON output to PATH", diff_archive.stdout)

        decision_memo = self.run_cli("decision-memo", "--help")
        self.assertEqual(decision_memo.returncode, 0, decision_memo.stderr)
        self.assertIn("LEDGER", decision_memo.stdout)
        self.assertIn("pre-trade/review decision memo", decision_memo.stdout)
        self.assertIn("write JSON output to PATH", decision_memo.stdout)

        scenario_plan = self.run_cli("scenario-plan", "--help")
        self.assertEqual(scenario_plan.returncode, 0, scenario_plan.stderr)
        self.assertIn("LEDGER", scenario_plan.stdout)
        self.assertIn("base/bull/bear scenario plan", scenario_plan.stdout)
        self.assertIn("write JSON output to PATH", scenario_plan.stdout)

    def test_single_file_output_write_error_returns_concise_exit_2(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            output_path = Path(temp) / "blocked.md"
            with mock.patch.object(cli_module, "_write_text", side_effect=PermissionError(13, "Permission denied")):
                status, stdout, stderr = self.run_cli_in_process("brief", str(EXAMPLE), "--output", str(output_path))

            self.assertEqual(status, 2)
            self.assertEqual(stdout, "")
            self.assertEqual(stderr, f"error: cannot write output {output_path}: Permission denied\n")
            self.assertNotIn("Traceback", stderr)

    def test_paired_output_write_error_reports_failing_path(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            md_path = Path(temp) / "risk.md"
            json_path = Path(temp) / "risk.json"
            with mock.patch.object(
                cli_module,
                "_write_text",
                side_effect=[None, OSError("disk full")],
            ):
                status, stdout, stderr = self.run_cli_in_process(
                    "risk",
                    str(EXAMPLE),
                    "--output",
                    str(md_path),
                    "--json-output",
                    str(json_path),
                )

            self.assertEqual(status, 2)
            self.assertEqual(stdout, "")
            self.assertEqual(stderr, f"error: cannot write output {json_path}: disk full\n")
            self.assertNotIn("Traceback", stderr)
            self.assertFalse(md_path.exists())

    def test_paired_outputs_do_not_leave_first_output_when_second_write_fails(self) -> None:
        commands = (
            ("risk", [str(EXAMPLE)]),
            ("history", [str(EXAMPLE)]),
            ("compare", [str(PRIOR_EXAMPLE), str(EXAMPLE)]),
            ("portfolio", [str(EXAMPLE), str(ETF_EXAMPLE)]),
            ("evidence-audit", [str(EXAMPLE), str(ETF_EXAMPLE)]),
            ("review-queue", [str(EXAMPLE), str(ETF_EXAMPLE)]),
            ("watchlist", [str(EXAMPLE), str(ETF_EXAMPLE)]),
            ("action-plan", [str(EXAMPLE), str(ETF_EXAMPLE)]),
            ("diff-archive", [str(ARCHIVE_FIXTURE), str(ARCHIVE_FIXTURE)]),
        )
        for command, positional_args in commands:
            with self.subTest(command=command), tempfile.TemporaryDirectory() as temp:
                temp_dir = Path(temp)
                md_path = temp_dir / f"{command}.md"
                blocked_parent = temp_dir / "blocked"
                blocked_parent.write_text("not a directory", encoding="utf-8")
                json_path = blocked_parent / f"{command}.json"

                status, stdout, stderr = self.run_cli_in_process(
                    command,
                    *positional_args,
                    "--output",
                    str(md_path),
                    "--json-output",
                    str(json_path),
                )

                self.assertEqual(status, 2)
                self.assertEqual(stdout, "")
                self.assertIn(f"error: cannot write output {json_path}:", stderr)
                self.assertNotIn("Traceback", stderr)
                self.assertFalse(md_path.exists())
                self.assertFalse(json_path.exists())

    def test_init_template_output_write_error_returns_concise_exit_2(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            output_path = Path(temp) / "ledger.json"
            with mock.patch.object(cli_module, "_write_text", side_effect=OSError("read-only target")):
                status, stdout, stderr = self.run_cli_in_process(
                    "init-template",
                    "--asset",
                    "TST",
                    "--name",
                    "Test Asset",
                    "--type",
                    "equity",
                    "--output",
                    str(output_path),
                )

            self.assertEqual(status, 2)
            self.assertEqual(stdout, "")
            self.assertEqual(stderr, f"error: cannot write output {output_path}: read-only target\n")
            self.assertNotIn("Traceback", stderr)

    def test_diff_archive_output_write_error_returns_concise_exit_2(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            md_path = Path(temp) / "archive-diff.md"
            json_path = Path(temp) / "archive-diff.json"
            with mock.patch.object(cli_module, "_write_text", side_effect=OSError("quota exceeded")):
                status, stdout, stderr = self.run_cli_in_process(
                    "diff-archive",
                    str(ARCHIVE_FIXTURE),
                    str(ARCHIVE_FIXTURE),
                    "--output",
                    str(md_path),
                    "--json-output",
                    str(json_path),
                )

            self.assertEqual(status, 2)
            self.assertEqual(stdout, "")
            self.assertEqual(stderr, f"error: cannot write output {md_path}: quota exceeded\n")
            self.assertNotIn("Traceback", stderr)

    def test_output_dir_write_errors_return_concise_exit_2(self) -> None:
        commands = (
            ("demo-bundle", "bundle"),
            ("archive", "archive"),
            ("html-dashboard", "html-dashboard"),
        )
        for command, dirname in commands:
            with self.subTest(command=command), tempfile.TemporaryDirectory() as temp:
                output_dir = Path(temp) / dirname
                with mock.patch.object(
                    cli_module,
                    "_write_demo_bundle_dir",
                    side_effect=PermissionError(13, "Permission denied"),
                ):
                    status, stdout, stderr = self.run_cli_in_process(
                        command,
                        str(EXAMPLE),
                        str(ETF_EXAMPLE),
                        "--output-dir",
                        str(output_dir),
                    )

                self.assertEqual(status, 2)
                self.assertEqual(stdout, "")
                self.assertEqual(stderr, f"error: cannot write output {output_dir}: Permission denied\n")
                self.assertNotIn("Traceback", stderr)

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

    def test_decision_memo_writes_pre_trade_review_payload(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            md_path = Path(temp) / "decision-memo.md"
            json_path = Path(temp) / "decision-memo.json"
            result = self.run_cli(
                "decision-memo",
                str(EXAMPLE),
                "--output",
                str(md_path),
                "--json-output",
                str(json_path),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            text = md_path.read_text()
            self.assertIn("# Decision Memo", text)
            self.assertIn("## Questions before action", text)
            payload = json.loads(json_path.read_text())
            self.assertEqual(payload["thesis_id"], "oklo-ai-power")
            self.assertEqual(payload["latest_review"]["date"], "2026-06-30")
            self.assertEqual(payload["broker_view_summary"]["rating_counts"]["cautious"], 1)
            self.assertEqual(payload["high_risks"][0]["id"], "R1")
            self.assertEqual(payload["catalyst_checklist"][0]["id"], "CAT2")
            self.assertEqual(payload["exposure"]["open_position_rules"][0]["id"], "P1")
            self.assertEqual(payload["evidence_summary"]["coverage"]["stale_source_count"], 0)
            self.assertEqual(payload["questions_before_action"][0]["id"], "Q1")

    def test_decision_memo_latest_review_tie_breaker_is_input_order_independent(self) -> None:
        data = json.loads(EXAMPLE.read_text())
        same_day_reviews = [
            {
                "date": "2026-07-01",
                "decision": "watch",
                "summary": "A same-day lower tie breaker.",
                "source_ids": ["S1"],
            },
            {
                "date": "2026-07-01",
                "decision": "watch",
                "summary": "Z same-day upper tie breaker.",
                "source_ids": ["S1"],
            },
        ]
        data["reviews"] = same_day_reviews
        forward = decision_memo_payload(data)
        data["reviews"] = list(reversed(same_day_reviews))
        reverse = decision_memo_payload(data)
        self.assertEqual(forward["latest_review"], reverse["latest_review"])
        self.assertEqual(forward["latest_review"]["summary"], "Z same-day upper tie breaker.")

    def test_decision_memo_escapes_markdown_title_and_reports_warnings(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            temp_dir = Path(temp)
            warning_path = temp_dir / "warning.json"
            data = json.loads(EXAMPLE.read_text())
            data["title"] = "Title | with\nbreak"
            data["reviews"] = list(reversed(data["reviews"]))
            warning_path.write_text(json.dumps(data), encoding="utf-8")
            md_path = temp_dir / "decision-memo.md"
            json_path = temp_dir / "decision-memo.json"
            result = self.run_cli(
                "decision-memo",
                str(warning_path),
                "--output",
                str(md_path),
                "--json-output",
                str(json_path),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("warning: ledger.reviews are not sorted by date", result.stderr)
            self.assertIn("# Decision Memo: Title \\| with break", md_path.read_text())

    def test_decision_memo_questions_prioritize_stale_evidence_over_closed_catalysts(self) -> None:
        data = json.loads(EXAMPLE.read_text())
        data["updated"] = "2026-12-31"
        data["risks"][0]["severity"] = "medium"
        data["risks"][1]["severity"] = "medium"
        data["catalysts"] = [
            {
                "id": "CAT-CLOSED",
                "title": "Closed item",
                "date": "2026-08-15",
                "window": "",
                "status": "closed",
                "source_ids": ["S1"],
            }
        ]
        data["position_rules"] = []
        data["checklist"] = []
        payload = decision_memo_payload(data)
        self.assertEqual(
            payload["questions_before_action"][-1]["question"],
            "Which stale sources must be refreshed before relying on this memo?",
        )

    def test_decision_memo_validates_before_writing(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            temp_dir = Path(temp)
            bad_path = temp_dir / "bad.json"
            data = json.loads(EXAMPLE.read_text())
            data["risks"][0]["source_ids"] = ["missing"]
            bad_path.write_text(json.dumps(data), encoding="utf-8")
            md_path = temp_dir / "decision-memo.md"
            json_path = temp_dir / "decision-memo.json"
            result = self.run_cli(
                "decision-memo",
                str(bad_path),
                "--output",
                str(md_path),
                "--json-output",
                str(json_path),
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("unknown source missing", result.stderr)
            self.assertFalse(md_path.exists())
            self.assertFalse(json_path.exists())

    def test_scenario_plan_writes_base_bull_bear_payload(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            md_path = Path(temp) / "scenario-plan.md"
            json_path = Path(temp) / "scenario-plan.json"
            result = self.run_cli(
                "scenario-plan",
                str(EXAMPLE),
                "--output",
                str(md_path),
                "--json-output",
                str(json_path),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            text = md_path.read_text()
            self.assertIn("# Scenario Plan", text)
            self.assertIn("## Base Case", text)
            self.assertIn("## Bull Case", text)
            self.assertIn("## Bear Case", text)
            payload = json.loads(json_path.read_text())
            self.assertEqual(payload["thesis_id"], "oklo-ai-power")
            self.assertEqual([item["id"] for item in payload["cases"]], ["base", "bull", "bear"])
            self.assertEqual(payload["scenario_plan"]["case_count"], 3)
            self.assertEqual(payload["scenario_plan"]["trigger_count"], 3)
            self.assertEqual(payload["cases"][1]["assumptions"][0]["id"], "A1")
            self.assertEqual(payload["cases"][2]["assumptions"][0]["id"], "A2")
            self.assertEqual(payload["cases"][2]["risks"][0]["id"], "R1")
            self.assertEqual(payload["cases"][0]["position_constraints"][0]["id"], "P1")
            self.assertEqual(payload["cases"][0]["evidence_gaps"][0]["id"], "ASSUMPTION-A2")

    def test_scenario_plan_order_is_input_order_independent(self) -> None:
        data = json.loads(EXAMPLE.read_text())
        forward = scenario_plan_payload(data)
        data["assumptions"] = list(reversed(data["assumptions"]))
        data["risks"] = list(reversed(data["risks"]))
        data["position_rules"] = list(reversed(data["position_rules"]))
        reverse = scenario_plan_payload(data)
        self.assertEqual(forward, reverse)
        self.assertEqual([item["id"] for item in forward["cases"][0]["risk_mitigations"]], ["R1", "R2"])
        self.assertEqual([item["id"] for item in forward["cases"][0]["position_constraints"]], ["P1", "P2"])

    def test_scenario_plan_infers_trigger_cases_by_whole_terms(self) -> None:
        data = json.loads(EXAMPLE.read_text())
        data["catalysts"] = [
            {"id": "CAT1", "title": "Nuclear licensing status update", "status": "watch", "source_ids": ["S3"]},
            {"id": "CAT2", "title": "Signed customer contract", "status": "watch", "source_ids": ["S1"]},
            {"id": "CAT3", "title": "Licensing delay", "status": "watch", "source_ids": ["S3"]},
        ]
        payload = scenario_plan_payload(data)
        cases = {item["id"]: item for item in payload["cases"]}
        self.assertEqual([(item["id"], item["direction"]) for item in cases["base"]["triggers"]], [("CAT1", "base")])
        self.assertEqual([(item["id"], item["direction"]) for item in cases["bull"]["triggers"]], [("CAT2", "bull")])
        self.assertEqual([(item["id"], item["direction"]) for item in cases["bear"]["triggers"]], [("CAT3", "bear")])

    def test_scenario_plan_orders_evidence_gaps_by_review_priority(self) -> None:
        data = json.loads(EXAMPLE.read_text())
        data["updated"] = "2027-01-01"
        data["sources"].append(
            {
                "id": "S4",
                "title": "Unused recent source",
                "publisher": "Desk",
                "date": "2026-12-31",
                "url": "https://example.com/unused",
            }
        )
        data["broker_views"][0]["source_ids"] = []
        gap_ids = [item["id"] for item in scenario_plan_payload(data)["cases"][0]["evidence_gaps"]]
        self.assertEqual(gap_ids[:5], ["ASSUMPTION-A2", "STALE-S1", "STALE-S2", "STALE-S3", "UNUSED-S4"])
        self.assertEqual(gap_ids[-1], "UNSUPPORTED-broker_view-B1")

    def test_scenario_plan_escapes_markdown_inline_values(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            temp_dir = Path(temp)
            ledger_path = temp_dir / "ledger.json"
            data = json.loads(EXAMPLE.read_text())
            data["title"] = "Scenario | Title\nBreak"
            data["assumptions"][0]["statement"] = "Power | demand\ncontinues"
            data["catalysts"][0]["title"] = "Signed | agreement\nwith buyer"
            data["risks"][0]["mitigation"] = "Refresh | licensing\nmilestones"
            data["position_rules"][0]["rule"] = "Keep | watchlist\nonly"
            data["sources"][0]["title"] = "Source | title\nbreak"
            ledger_path.write_text(json.dumps(data), encoding="utf-8")

            md_path = temp_dir / "scenario-plan.md"
            json_path = temp_dir / "scenario-plan.json"
            result = self.run_cli(
                "scenario-plan",
                str(ledger_path),
                "--output",
                str(md_path),
                "--json-output",
                str(json_path),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            text = md_path.read_text()
            self.assertIn("# Scenario Plan: Scenario \\| Title Break", text)
            self.assertIn("Power \\| demand continues", text)
            self.assertIn("Signed \\| agreement with buyer", text)
            self.assertIn("Refresh \\| licensing milestones", text)
            self.assertIn("Keep \\| watchlist only", text)
            self.assertIn("[S1] Source \\| title break.", text)

    def test_scenario_plan_validates_before_writing(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            temp_dir = Path(temp)
            bad_path = temp_dir / "bad.json"
            data = json.loads(EXAMPLE.read_text())
            data["position_rules"][0]["source_ids"] = ["missing"]
            bad_path.write_text(json.dumps(data), encoding="utf-8")
            md_path = temp_dir / "scenario-plan.md"
            json_path = temp_dir / "scenario-plan.json"
            result = self.run_cli(
                "scenario-plan",
                str(bad_path),
                "--output",
                str(md_path),
                "--json-output",
                str(json_path),
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("unknown source missing", result.stderr)
            self.assertFalse(md_path.exists())
            self.assertFalse(json_path.exists())

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

    def test_evidence_audit_aggregates_multiple_ledgers(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            md_path = Path(temp) / "audit.md"
            json_path = Path(temp) / "audit.json"
            result = self.run_cli(
                "evidence-audit",
                str(EXAMPLE),
                str(ETF_EXAMPLE),
                "--output",
                str(md_path),
                "--json-output",
                str(json_path),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("# Portfolio Evidence Audit", md_path.read_text())
            payload = json.loads(json_path.read_text())
            self.assertEqual(payload["audit"]["ledger_count"], 2)
            self.assertEqual(payload["audit"]["tracked_items"], 28)
            self.assertEqual(payload["audit"]["unsupported_items"], 6)
            self.assertEqual(payload["field_coverage"]["checklist"]["unsupported_items"], 5)
            self.assertEqual(payload["ledgers"][0]["thesis_id"], "oklo-ai-power")
            self.assertEqual(payload["ledgers"][0]["quality_score"], 92)
            self.assertEqual(payload["ledgers"][1]["quality_score"], 81)

    def test_evidence_audit_requires_two_ledgers(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            result = self.run_cli(
                "evidence-audit",
                str(EXAMPLE),
                "--output",
                str(Path(temp) / "audit.md"),
                "--json-output",
                str(Path(temp) / "audit.json"),
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("requires at least two", result.stderr)

    def test_evidence_audit_validates_all_ledgers_before_writing(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            temp_dir = Path(temp)
            bad_path = temp_dir / "bad.json"
            data = json.loads(ETF_EXAMPLE.read_text())
            data["checklist"][0]["source_ids"] = ["missing"]
            bad_path.write_text(json.dumps(data), encoding="utf-8")
            md_path = temp_dir / "audit.md"
            json_path = temp_dir / "audit.json"
            result = self.run_cli(
                "evidence-audit",
                str(EXAMPLE),
                str(bad_path),
                "--output",
                str(md_path),
                "--json-output",
                str(json_path),
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("unknown source missing", result.stderr)
            self.assertFalse(md_path.exists())
            self.assertFalse(json_path.exists())

    def test_evidence_audit_reports_duplicate_source_urls(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            temp_dir = Path(temp)
            dup_path = temp_dir / "dup.json"
            data = json.loads(ETF_EXAMPLE.read_text())
            data["sources"][0]["url"] = "https://example.com/oklo-investor-presentation"
            dup_path.write_text(json.dumps(data), encoding="utf-8")
            json_path = temp_dir / "audit.json"
            result = self.run_cli(
                "evidence-audit",
                str(EXAMPLE),
                str(dup_path),
                "--output",
                str(temp_dir / "audit.md"),
                "--json-output",
                str(json_path),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(json_path.read_text())
            self.assertEqual(payload["audit"]["duplicate_source_url_count"], 1)
            duplicate = payload["duplicate_source_urls"][0]
            self.assertEqual(duplicate["url"], "https://example.com/oklo-investor-presentation")
            self.assertEqual(duplicate["ledger_count"], 2)
            self.assertEqual(
                [(item["ledger_id"], item["source_id"]) for item in duplicate["occurrences"]],
                [("leveraged-etf-discipline", "S1"), ("oklo-ai-power", "S1")],
            )

    def test_evidence_audit_ignores_duplicate_source_urls_within_same_ledger_id(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            temp_dir = Path(temp)
            first_path = temp_dir / "first.json"
            second_path = temp_dir / "second.json"
            first_data = json.loads(EXAMPLE.read_text())
            first_data["sources"][1]["url"] = first_data["sources"][0]["url"]
            second_data = json.loads(EXAMPLE.read_text())
            second_data["updated"] = "2026-05-13"
            first_path.write_text(json.dumps(first_data), encoding="utf-8")
            second_path.write_text(json.dumps(second_data), encoding="utf-8")

            result = self.run_cli(
                "evidence-audit",
                str(first_path),
                str(second_path),
                "--output",
                str(temp_dir / "audit.md"),
                "--json-output",
                str(temp_dir / "audit.json"),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads((temp_dir / "audit.json").read_text())
            self.assertEqual(payload["audit"]["duplicate_source_url_count"], 0)
            self.assertEqual(payload["duplicate_source_urls"], [])

    def test_evidence_audit_scores_zero_source_ledgers_without_source_points(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            temp_dir = Path(temp)
            first_path = temp_dir / "first.json"
            second_path = temp_dir / "second.json"
            first_data = json.loads(EXAMPLE.read_text())
            first_data["sources"] = []
            for field in ("assumptions", "risks", "reviews", "catalysts", "broker_views", "position_rules", "checklist"):
                for item in first_data.get(field, []):
                    item["source_ids"] = []
            second_data = json.loads(ETF_EXAMPLE.read_text())
            first_path.write_text(json.dumps(first_data), encoding="utf-8")
            second_path.write_text(json.dumps(second_data), encoding="utf-8")

            result = self.run_cli(
                "evidence-audit",
                str(first_path),
                str(second_path),
                "--output",
                str(temp_dir / "audit.md"),
                "--json-output",
                str(temp_dir / "audit.json"),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads((temp_dir / "audit.json").read_text())
            by_id = {item["thesis_id"]: item for item in payload["ledgers"]}
            self.assertEqual(by_id["oklo-ai-power"]["coverage"]["source_count"], 0)
            self.assertEqual(by_id["oklo-ai-power"]["quality_score"], 0)

    def test_evidence_audit_counts_checklist_source_support(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            temp_dir = Path(temp)
            first_path = temp_dir / "first.json"
            first_data = json.loads(EXAMPLE.read_text())
            first_data["checklist"][0]["source_ids"] = ["S1"]
            first_data["checklist"][1]["source_ids"] = ["S2"]
            first_path.write_text(json.dumps(first_data), encoding="utf-8")

            result = self.run_cli(
                "evidence-audit",
                str(first_path),
                str(ETF_EXAMPLE),
                "--output",
                str(temp_dir / "audit.md"),
                "--json-output",
                str(temp_dir / "audit.json"),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads((temp_dir / "audit.json").read_text())
            self.assertEqual(payload["field_coverage"]["checklist"]["supported_items"], 2)
            self.assertEqual(payload["field_coverage"]["checklist"]["unsupported_items"], 3)

    def test_evidence_audit_stale_sources_are_based_on_each_ledger_updated(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            temp_dir = Path(temp)
            current_path = temp_dir / "current.json"
            stale_path = temp_dir / "stale.json"
            current_data = json.loads(EXAMPLE.read_text())
            current_data["updated"] = "2025-01-02"
            current_data["sources"][0]["date"] = "2024-09-01"
            stale_data = json.loads(ETF_EXAMPLE.read_text())
            stale_data["updated"] = "2026-12-31"
            for source in stale_data["sources"]:
                source["date"] = "2026-12-31"
            stale_data["sources"][0]["date"] = "2026-01-01"
            current_path.write_text(json.dumps(current_data), encoding="utf-8")
            stale_path.write_text(json.dumps(stale_data), encoding="utf-8")

            result = self.run_cli(
                "evidence-audit",
                str(current_path),
                str(stale_path),
                "--output",
                str(temp_dir / "audit.md"),
                "--json-output",
                str(temp_dir / "audit.json"),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads((temp_dir / "audit.json").read_text())
            self.assertEqual(payload["audit"]["stale_source_count"], 1)
            self.assertEqual(
                [(item["ledger_id"], item["id"]) for item in payload["stale_sources"]],
                [("leveraged-etf-discipline", "S1")],
            )

    def test_evidence_audit_order_does_not_depend_on_input_order_for_tied_items(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            temp_dir = Path(temp)
            first_path = temp_dir / "first.json"
            second_path = temp_dir / "second.json"
            first_data = json.loads(EXAMPLE.read_text())
            second_data = json.loads(EXAMPLE.read_text())
            second_data["thesis_id"] = "oklo-ai-power-copy"
            second_data["asset"]["ticker"] = "OKLB"
            first_path.write_text(json.dumps(first_data), encoding="utf-8")
            second_path.write_text(json.dumps(second_data), encoding="utf-8")

            forward_md = temp_dir / "forward.md"
            forward_json = temp_dir / "forward.json"
            reverse_md = temp_dir / "reverse.md"
            reverse_json = temp_dir / "reverse.json"
            forward = self.run_cli(
                "evidence-audit",
                str(first_path),
                str(second_path),
                "--output",
                str(forward_md),
                "--json-output",
                str(forward_json),
            )
            reverse = self.run_cli(
                "evidence-audit",
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

    def test_evidence_audit_escapes_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            temp_dir = Path(temp)
            stale_path = temp_dir / "stale.json"
            data = json.loads(EXAMPLE.read_text())
            data["sources"][0]["date"] = "2025-01-01"
            data["sources"][0]["title"] = "Audit | title\nbreak"
            data["checklist"][0]["id"] = "C|1"
            stale_path.write_text(json.dumps(data), encoding="utf-8")
            md_path = temp_dir / "audit.md"
            result = self.run_cli(
                "evidence-audit",
                str(stale_path),
                str(ETF_EXAMPLE),
                "--output",
                str(md_path),
                "--json-output",
                str(temp_dir / "audit.json"),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            text = md_path.read_text()
            self.assertIn("Audit \\| title break", text)
            self.assertIn("C\\|1", text)

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

    def test_watchlist_ranks_weekly_review_fields(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            md_path = Path(temp) / "watchlist.md"
            json_path = Path(temp) / "watchlist.json"
            result = self.run_cli(
                "watchlist",
                str(EXAMPLE),
                str(ETF_EXAMPLE),
                "--output",
                str(md_path),
                "--json-output",
                str(json_path),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("# Watchlist", md_path.read_text())
            payload = json.loads(json_path.read_text())
            self.assertEqual(payload["watchlist"]["ledger_count"], 2)
            self.assertEqual(payload["items"][0]["rank"], 1)
            self.assertEqual(payload["items"][0]["thesis_id"], "leveraged-etf-discipline")
            self.assertEqual(payload["items"][0]["review_queue_score"], 13)
            self.assertEqual(payload["items"][0]["priority"], "high")
            self.assertEqual(payload["items"][0]["nearest_open_catalyst"]["id"], "CAT2")
            self.assertEqual(payload["items"][0]["latest_review"], {"date": "2026-05-19", "decision": "policy"})
            self.assertEqual(payload["items"][0]["stale_source_count"], 0)
            self.assertEqual(payload["items"][0]["high_risk_count"], 2)
            self.assertEqual(payload["items"][0]["open_position_rule_count"], 2)
            self.assertEqual(payload["items"][1]["thesis_id"], "oklo-ai-power")
            self.assertEqual(payload["items"][1]["nearest_open_catalyst"]["id"], "CAT2")
            self.assertEqual(payload["items"][1]["latest_review"], {"date": "2026-06-30", "decision": "watch"})

    def test_watchlist_payload_is_input_order_independent_for_tied_items(self) -> None:
        first_data = json.loads(EXAMPLE.read_text())
        second_data = json.loads(ETF_EXAMPLE.read_text())
        first_data["asset"]["ticker"] = "TIE"
        second_data["asset"]["ticker"] = "TIE"
        second_data["risks"][1]["severity"] = "medium"
        forward = watchlist_payload([first_data, second_data])
        reverse = watchlist_payload([second_data, first_data])
        self.assertEqual(forward, reverse)

    def test_watchlist_handles_duplicate_thesis_ids_without_cross_matching_ledgers(self) -> None:
        first_data = json.loads(EXAMPLE.read_text())
        second_data = json.loads(EXAMPLE.read_text())
        for data in (first_data, second_data):
            data["thesis_id"] = "duplicate-thesis"
            data["title"] = "Duplicate Thesis"
            data["asset"]["ticker"] = "DUP"
            data["updated"] = "2026-05-12"
            data["reviews"] = [
                {
                    "date": "2026-05-12",
                    "decision": "watch",
                    "summary": "Current review.",
                    "source_ids": ["S1"],
                }
            ]
            data["catalysts"] = [
                {
                    "id": "CAT1",
                    "title": "Z catalyst",
                    "date": "2026-06-01",
                    "status": "watch",
                    "source_ids": ["S1"],
                }
            ]
        first_data["catalysts"][0]["title"] = "A catalyst"

        forward = watchlist_payload([first_data, second_data])
        reverse = watchlist_payload([second_data, first_data])

        self.assertEqual(forward, reverse)
        self.assertEqual(
            [item["nearest_open_catalyst"]["title"] for item in forward["items"]],
            ["A catalyst", "Z catalyst"],
        )
        self.assertEqual([item["thesis_id"] for item in forward["items"]], ["duplicate-thesis", "duplicate-thesis"])

    def test_watchlist_nearest_open_catalyst_tie_breaks_by_stable_fields(self) -> None:
        first_data = json.loads(EXAMPLE.read_text())
        second_data = json.loads(ETF_EXAMPLE.read_text())
        first_data["catalysts"] = [
            {
                "id": "CATX",
                "title": "Z same-date catalyst",
                "date": "2026-08-01",
                "window": "same",
                "status": "watch",
                "source_ids": ["S1"],
            },
            {
                "id": "CATX",
                "title": "A same-date catalyst",
                "date": "2026-08-01",
                "window": "same",
                "status": "watch",
                "source_ids": ["S1"],
            },
        ]
        payload = watchlist_payload([first_data, second_data])
        item = next(item for item in payload["items"] if item["thesis_id"] == "oklo-ai-power")
        self.assertEqual(item["nearest_open_catalyst"]["title"], "A same-date catalyst")

    def test_watchlist_latest_review_tie_breaker_is_input_order_independent(self) -> None:
        first_data = json.loads(EXAMPLE.read_text())
        second_data = json.loads(ETF_EXAMPLE.read_text())
        same_day_reviews = [
            {
                "date": "2026-07-01",
                "decision": "hold",
                "summary": "Z summary",
                "source_ids": ["S1"],
            },
            {
                "date": "2026-07-01",
                "decision": "watch",
                "summary": "A summary",
                "source_ids": ["S1"],
            },
        ]
        first_data["reviews"] = same_day_reviews
        forward = watchlist_payload([first_data, second_data])
        first_data["reviews"] = list(reversed(same_day_reviews))
        reverse = watchlist_payload([first_data, second_data])
        forward_item = next(item for item in forward["items"] if item["thesis_id"] == "oklo-ai-power")
        reverse_item = next(item for item in reverse["items"] if item["thesis_id"] == "oklo-ai-power")
        self.assertEqual(forward_item["latest_review"], reverse_item["latest_review"])
        self.assertEqual(forward_item["latest_review"], {"date": "2026-07-01", "decision": "watch"})

    def test_watchlist_json_shape_is_stable_when_optional_details_are_missing(self) -> None:
        first_data = json.loads(EXAMPLE.read_text())
        second_data = json.loads(ETF_EXAMPLE.read_text())
        first_data["catalysts"] = []
        first_data["reviews"] = []
        payload = watchlist_payload([first_data, second_data])
        item = next(item for item in payload["items"] if item["thesis_id"] == "oklo-ai-power")
        self.assertEqual(
            set(item),
            {
                "rank",
                "thesis_id",
                "ticker",
                "title",
                "review_queue_score",
                "priority",
                "next_action",
                "nearest_open_catalyst",
                "latest_review",
                "stale_source_count",
                "high_risk_count",
                "open_position_rule_count",
            },
        )
        self.assertIsNone(item["nearest_open_catalyst"])
        self.assertEqual(item["latest_review"], {"date": "", "decision": ""})

    def test_watchlist_requires_two_ledgers(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            result = self.run_cli(
                "watchlist",
                str(EXAMPLE),
                "--output",
                str(Path(temp) / "watchlist.md"),
                "--json-output",
                str(Path(temp) / "watchlist.json"),
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("requires at least two", result.stderr)

    def test_watchlist_validates_all_ledgers_before_writing(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            temp_dir = Path(temp)
            bad_path = temp_dir / "bad.json"
            data = json.loads(ETF_EXAMPLE.read_text())
            data["risks"][0]["source_ids"] = ["missing"]
            bad_path.write_text(json.dumps(data), encoding="utf-8")
            md_path = temp_dir / "watchlist.md"
            json_path = temp_dir / "watchlist.json"
            result = self.run_cli(
                "watchlist",
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

    def test_watchlist_escapes_markdown_cells(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            temp_dir = Path(temp)
            first_path = temp_dir / "first.json"
            second_path = temp_dir / "second.json"
            first_data = json.loads(EXAMPLE.read_text())
            first_data["title"] = "Title | with\nbreak"
            first_data["catalysts"][1]["title"] = "Catalyst | with\nbreak"
            first_path.write_text(json.dumps(first_data), encoding="utf-8")
            second_path.write_text(ETF_EXAMPLE.read_text(), encoding="utf-8")
            md_path = temp_dir / "watchlist.md"
            result = self.run_cli(
                "watchlist",
                str(first_path),
                str(second_path),
                "--output",
                str(md_path),
                "--json-output",
                str(temp_dir / "watchlist.json"),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            text = md_path.read_text()
            self.assertIn("Title \\| with break", text)
            self.assertIn("Catalyst \\| with break", text)

    def test_action_plan_writes_weekly_workflow_payload(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            md_path = Path(temp) / "action-plan.md"
            json_path = Path(temp) / "action-plan.json"
            result = self.run_cli(
                "action-plan",
                str(EXAMPLE),
                str(ETF_EXAMPLE),
                "--output",
                str(md_path),
                "--json-output",
                str(json_path),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            text = md_path.read_text()
            self.assertIn("# Weekly Action Plan", text)
            self.assertIn("not investment advice", text)
            self.assertIn("It does not include market data", text)
            payload = json.loads(json_path.read_text())
            self.assertEqual(payload["action_plan"]["ledger_count"], 2)
            self.assertFalse(payload["action_plan"]["includes_market_data"])
            self.assertEqual(payload["actions"][0]["owner"], "TBD")
            self.assertEqual(payload["actions"][0]["cadence"], "now")
            self.assertIn("RQ_HIGH_SEVERITY_RISKS", payload["actions"][0]["reason_codes"])
            self.assertIn("review_queue_payload", payload["actions"][0])
            self.assertIn("watchlist_payload", payload["actions"][0])
            self.assertIn("evidence_audit_payload", payload["actions"][0])
            self.assertIn("risk_payload", payload["actions"][0])
            self.assertIn("exposure_payload", payload["actions"][0])
            self.assertIn("catalyst_payload", payload["actions"][0])
            self.assertEqual(payload["ledger_checklists"][0]["next_checklist"][0]["id"], "AP1")

    def test_action_plan_payload_is_input_order_independent_for_tied_items(self) -> None:
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

            forward = action_plan_payload([first_data, second_data])
            reverse = action_plan_payload([second_data, first_data])
            self.assertEqual(forward, reverse)

            forward_md = temp_dir / "forward.md"
            forward_json = temp_dir / "forward.json"
            reverse_md = temp_dir / "reverse.md"
            reverse_json = temp_dir / "reverse.json"
            forward_result = self.run_cli(
                "action-plan",
                str(first_path),
                str(second_path),
                "--output",
                str(forward_md),
                "--json-output",
                str(forward_json),
            )
            reverse_result = self.run_cli(
                "action-plan",
                str(second_path),
                str(first_path),
                "--output",
                str(reverse_md),
                "--json-output",
                str(reverse_json),
            )
            self.assertEqual(forward_result.returncode, 0, forward_result.stderr)
            self.assertEqual(reverse_result.returncode, 0, reverse_result.stderr)
            self.assertEqual(forward_md.read_text(), reverse_md.read_text())
            self.assertEqual(forward_json.read_text(), reverse_json.read_text())

    def test_action_plan_tie_breaks_duplicate_ids_and_tickers_by_full_payload(self) -> None:
        first_data = json.loads(EXAMPLE.read_text())
        second_data = json.loads(EXAMPLE.read_text())
        for data in (first_data, second_data):
            data["thesis_id"] = "duplicate-thesis"
            data["title"] = "Duplicate Thesis"
            data["asset"]["ticker"] = "DUP"
            data["updated"] = "2026-05-12"
            data["risks"] = []
            data["catalysts"] = []
            data["position_rules"] = []
            data["checklist"] = []
            for source in data["sources"]:
                source["date"] = "2026-05-12"
            data["reviews"] = [
                {
                    "date": "2026-05-12",
                    "decision": "hold",
                    "summary": "Current review.",
                    "source_ids": ["S1"],
                }
            ]
        second_data["reviews"][0]["decision"] = "watch"

        forward = action_plan_payload([first_data, second_data])
        reverse = action_plan_payload([second_data, first_data])

        self.assertEqual(forward, reverse)
        self.assertEqual(
            [item["latest_review"]["decision"] for item in forward["actions"]],
            ["hold", "watch"],
        )

    def test_action_plan_escapes_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            temp_dir = Path(temp)
            first_path = temp_dir / "first.json"
            second_path = temp_dir / "second.json"
            first_data = json.loads(EXAMPLE.read_text())
            first_data["title"] = "Action | title\nbreak"
            first_data["risks"][0]["name"] = "Risk | name\nbreak"
            first_data["position_rules"][0]["rule"] = "Rule | text\nbreak"
            first_data["sources"][0]["date"] = "2025-01-01"
            first_path.write_text(json.dumps(first_data), encoding="utf-8")
            second_path.write_text(ETF_EXAMPLE.read_text(), encoding="utf-8")
            md_path = temp_dir / "action-plan.md"
            result = self.run_cli(
                "action-plan",
                str(first_path),
                str(second_path),
                "--output",
                str(md_path),
                "--json-output",
                str(temp_dir / "action-plan.json"),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            text = md_path.read_text()
            self.assertIn("Action \\| title break", text)
            self.assertIn("Risk \\| name break", text)
            self.assertIn("Rule \\| text break", text)

    def test_action_plan_validates_all_ledgers_before_writing(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            temp_dir = Path(temp)
            bad_path = temp_dir / "bad.json"
            data = json.loads(ETF_EXAMPLE.read_text())
            data["checklist"][0]["source_ids"] = ["missing"]
            bad_path.write_text(json.dumps(data), encoding="utf-8")
            md_path = temp_dir / "action-plan.md"
            json_path = temp_dir / "action-plan.json"
            result = self.run_cli(
                "action-plan",
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

    def test_action_plan_avoids_personal_buy_sell_wording(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            temp_dir = Path(temp)
            first_path = temp_dir / "first.json"
            data = json.loads(EXAMPLE.read_text())
            data["title"] = "Sell-side buy list wording from source data"
            data["sources"][0]["title"] = "Buy and sell wording in a source title"
            first_path.write_text(json.dumps(data), encoding="utf-8")
            md_path = temp_dir / "action-plan.md"
            json_path = Path(temp) / "action-plan.json"
            result = self.run_cli(
                "action-plan",
                str(first_path),
                str(ETF_EXAMPLE),
                "--output",
                str(md_path),
                "--json-output",
                str(json_path),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(json_path.read_text())
            generated_guidance = "\n".join(
                [item["action"] for item in payload["actions"]]
                + [
                    checklist_item["text"]
                    for item in payload["actions"]
                    for checklist_item in item["next_checklist"]
                ]
            ).lower()
            self.assertNotRegex(generated_guidance, r"\byou should\b")
            self.assertNotRegex(generated_guidance, r"\bbuy\b")
            self.assertNotRegex(generated_guidance, r"\bsell\b")

            dashboard_dir = temp_dir / "html-dashboard"
            dashboard = self.run_cli(
                "html-dashboard",
                str(first_path),
                str(ETF_EXAMPLE),
                "--output-dir",
                str(dashboard_dir),
            )
            self.assertEqual(dashboard.returncode, 0, dashboard.stderr)
            dashboard_action = (dashboard_dir / "action-plan.html").read_text().lower()
            self.assertIn("no market data included", dashboard_action)
            self.assertNotRegex(dashboard_action, r"\byou should\b")
            self.assertNotRegex(dashboard_action, r"\bbuy\b")
            self.assertNotRegex(dashboard_action, r"\bsell\b")

    def test_action_plan_source_quality_warnings_are_not_all_blockers(self) -> None:
        data = json.loads(EXAMPLE.read_text())
        data["thesis_id"] = "source-warning-only"
        data["title"] = "Source Warning Only"
        data["asset"]["ticker"] = "SWO"
        data["updated"] = "2026-05-12"
        for source in data["sources"]:
            source["date"] = "2026-05-12"
        data["reviews"] = [
            {
                "date": "2026-05-12",
                "decision": "watch",
                "summary": "Current review.",
                "source_ids": ["S1"],
            }
        ]
        data["risks"] = []
        data["catalysts"] = []
        data["position_rules"] = []
        data["checklist"] = []
        data["broker_views"] = []
        data["assumptions"][0]["source_ids"] = []

        payload = action_plan_payload([data, json.loads(ETF_EXAMPLE.read_text())])
        item = next(item for item in payload["actions"] if item["thesis_id"] == "source-warning-only")

        self.assertEqual(
            [warning["code"] for warning in item["source_quality_warnings"]],
            ["SOURCE_UNSUPPORTED_ITEM", "SOURCE_UNUSED"],
        )
        self.assertEqual(item["blockers"], [])
        self.assertEqual(item["cadence"], "watch")

    def test_action_plan_and_dashboard_surface_stale_source_blockers(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            temp_dir = Path(temp)
            first_path = temp_dir / "first.json"
            data = json.loads(EXAMPLE.read_text())
            data["updated"] = "2026-12-31"
            for source in data["sources"]:
                source["date"] = "2026-12-31"
            data["sources"][0]["date"] = "2026-01-01"
            first_path.write_text(json.dumps(data), encoding="utf-8")
            json_path = temp_dir / "action-plan.json"
            result = self.run_cli(
                "action-plan",
                str(first_path),
                str(ETF_EXAMPLE),
                "--output",
                str(temp_dir / "action-plan.md"),
                "--json-output",
                str(json_path),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(json_path.read_text())
            stale_item = next(item for item in payload["actions"] if item["thesis_id"] == "oklo-ai-power")
            self.assertIn("SOURCE_STALE", [blocker["code"] for blocker in stale_item["blockers"]])
            self.assertIn("SOURCE_STALE", [warning["code"] for warning in stale_item["source_quality_warnings"]])
            self.assertEqual(stale_item["cadence"], "now")

            dashboard_dir = temp_dir / "html-dashboard"
            dashboard = self.run_cli(
                "html-dashboard",
                str(first_path),
                str(ETF_EXAMPLE),
                "--output-dir",
                str(dashboard_dir),
            )
            self.assertEqual(dashboard.returncode, 0, dashboard.stderr)
            self.assertIn("SOURCE_STALE", (dashboard_dir / "action-plan.html").read_text())
            self.assertIn("Stale sources: 1", (dashboard_dir / "evidence-audit.html").read_text())

    def test_demo_bundle_writes_static_markdown_bundle_and_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            output_dir = Path(temp) / "bundle"
            result = self.run_cli(
                "demo-bundle",
                str(EXAMPLE),
                str(ETF_EXAMPLE),
                "--output-dir",
                str(output_dir),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            expected_files = [
                "index.md",
                "oklo-ai-power-brief.md",
                "oklo-ai-power-risk.md",
                "oklo-ai-power-history.md",
                "oklo-ai-power-decision-memo.md",
                "oklo-ai-power-scenario-plan.md",
                "leveraged-etf-discipline-brief.md",
                "leveraged-etf-discipline-risk.md",
                "leveraged-etf-discipline-history.md",
                "leveraged-etf-discipline-decision-memo.md",
                "leveraged-etf-discipline-scenario-plan.md",
                "portfolio-summary.md",
                "evidence-audit.md",
                "watchlist.md",
                "action-plan.md",
                "manifest.json",
            ]
            self.assertEqual(sorted(path.name for path in output_dir.iterdir()), sorted(expected_files))
            self.assertIn("# Invest Thesis Ledger Demo Bundle", (output_dir / "index.md").read_text())
            self.assertIn("# Portfolio Summary", (output_dir / "portfolio-summary.md").read_text())
            self.assertIn("# Portfolio Evidence Audit", (output_dir / "evidence-audit.md").read_text())
            self.assertIn("# Watchlist", (output_dir / "watchlist.md").read_text())
            self.assertIn("# Weekly Action Plan", (output_dir / "action-plan.md").read_text())
            manifest = json.loads((output_dir / "manifest.json").read_text())
            self.assertEqual(manifest["tool_version"], "1.7.1")
            self.assertEqual(manifest["ledger_ids"], ["oklo-ai-power", "leveraged-etf-discipline"])
            self.assertEqual(manifest["generated_files"], expected_files)
            index_links = [
                line.removeprefix("- [").split("](", 1)[1].removesuffix(")")
                for line in (output_dir / "index.md").read_text().splitlines()
                if line.startswith("- [")
            ]
            self.assertEqual(index_links, manifest["generated_files"])
            self.assertNotIn("timestamp", manifest)
            self.assertNotIn("generated_at", manifest)

    def test_demo_bundle_manifest_is_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            first_dir = Path(temp) / "first"
            second_dir = Path(temp) / "second"
            first = self.run_cli("demo-bundle", str(EXAMPLE), str(ETF_EXAMPLE), "--output-dir", str(first_dir))
            second = self.run_cli("demo-bundle", str(EXAMPLE), str(ETF_EXAMPLE), "--output-dir", str(second_dir))
            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertEqual((first_dir / "manifest.json").read_text(), (second_dir / "manifest.json").read_text())
            self.assertEqual((first_dir / "index.md").read_text(), (second_dir / "index.md").read_text())

    def test_demo_bundle_cleanly_overwrites_output_dir(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            output_dir = Path(temp) / "bundle"
            output_dir.mkdir()
            stale_file = output_dir / "stale.md"
            stale_dir = output_dir / "nested"
            stale_dir.mkdir()
            (stale_dir / "stale.md").write_text("stale", encoding="utf-8")
            stale_file.write_text("stale", encoding="utf-8")
            result = self.run_cli("demo-bundle", str(EXAMPLE), str(ETF_EXAMPLE), "--output-dir", str(output_dir))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse(stale_file.exists())
            self.assertFalse(stale_dir.exists())
            self.assertTrue((output_dir / "manifest.json").exists())

    def test_demo_bundle_validates_all_ledgers_before_writing(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            temp_dir = Path(temp)
            bad_path = temp_dir / "bad.json"
            output_dir = temp_dir / "bundle"
            output_dir.mkdir()
            sentinel = output_dir / "sentinel.md"
            sentinel.write_text("keep", encoding="utf-8")
            data = json.loads(ETF_EXAMPLE.read_text())
            data["risks"][0]["source_ids"] = ["missing"]
            bad_path.write_text(json.dumps(data), encoding="utf-8")
            result = self.run_cli("demo-bundle", str(EXAMPLE), str(bad_path), "--output-dir", str(output_dir))
            self.assertEqual(result.returncode, 1)
            self.assertIn("ledger: leveraged-etf-discipline", result.stderr)
            self.assertIn("unknown source missing", result.stderr)
            self.assertEqual(sentinel.read_text(), "keep")
            self.assertFalse((output_dir / "manifest.json").exists())

    def test_demo_bundle_requires_two_ledgers(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            result = self.run_cli("demo-bundle", str(EXAMPLE), "--output-dir", str(Path(temp) / "bundle"))
            self.assertEqual(result.returncode, 2)
            self.assertIn("requires at least two", result.stderr)

    def test_demo_bundle_disambiguates_duplicate_ledger_ids(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            temp_dir = Path(temp)
            first_path = temp_dir / "first.json"
            second_path = temp_dir / "second.json"
            first_data = json.loads(EXAMPLE.read_text())
            second_data = json.loads(ETF_EXAMPLE.read_text())
            second_data["thesis_id"] = first_data["thesis_id"]
            first_path.write_text(json.dumps(first_data), encoding="utf-8")
            second_path.write_text(json.dumps(second_data), encoding="utf-8")
            output_dir = temp_dir / "bundle"
            result = self.run_cli("demo-bundle", str(first_path), str(second_path), "--output-dir", str(output_dir))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((output_dir / "oklo-ai-power-brief.md").exists())
            self.assertTrue((output_dir / "oklo-ai-power-2-brief.md").exists())
            manifest = json.loads((output_dir / "manifest.json").read_text())
            self.assertEqual(manifest["ledger_ids"], ["oklo-ai-power", "oklo-ai-power"])
            self.assertIn("oklo-ai-power-2-brief.md", manifest["generated_files"])

    def test_demo_bundle_refuses_symlinked_output_dir(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            temp_dir = Path(temp)
            real_dir = temp_dir / "real"
            real_dir.mkdir()
            sentinel = real_dir / "sentinel.md"
            sentinel.write_text("keep", encoding="utf-8")
            output_dir = temp_dir / "bundle-link"
            try:
                output_dir.symlink_to(real_dir, target_is_directory=True)
            except OSError as exc:
                self.skipTest(f"symlink unavailable: {exc}")

            result = self.run_cli("demo-bundle", str(EXAMPLE), str(ETF_EXAMPLE), "--output-dir", str(output_dir))
            self.assertEqual(result.returncode, 2)
            self.assertIn("output dir is not a directory", result.stderr)
            self.assertEqual(sentinel.read_text(), "keep")
            self.assertFalse((real_dir / "manifest.json").exists())

    def test_demo_bundle_staged_write_preserves_existing_dir_on_write_error(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            output_dir = Path(temp) / "bundle"
            output_dir.mkdir()
            sentinel = output_dir / "sentinel.md"
            sentinel.write_text("keep", encoding="utf-8")

            with self.assertRaises(ValueError):
                _write_demo_bundle_dir(output_dir, [("index.md", "new"), ("nested/file.md", "bad")])

            self.assertEqual(sentinel.read_text(), "keep")
            self.assertFalse((output_dir / "index.md").exists())

    def test_archive_writes_portable_archive_manifest_and_summary(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            output_dir = Path(temp) / "archive"
            result = self.run_cli(
                "archive",
                str(EXAMPLE),
                str(ETF_EXAMPLE),
                "--output-dir",
                str(output_dir),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            expected_files = [
                "README.md",
                "oklo-ai-power.json",
                "oklo-ai-power-brief.md",
                "oklo-ai-power-risk.md",
                "oklo-ai-power-history.md",
                "oklo-ai-power-decision.md",
                "oklo-ai-power-scenario.md",
                "leveraged-etf-discipline.json",
                "leveraged-etf-discipline-brief.md",
                "leveraged-etf-discipline-risk.md",
                "leveraged-etf-discipline-history.md",
                "leveraged-etf-discipline-decision.md",
                "leveraged-etf-discipline-scenario.md",
                "portfolio.md",
                "evidence-audit.md",
                "watchlist.md",
                "action-plan.md",
                "manifest.json",
                "archive-summary.json",
            ]
            self.assertEqual(sorted(path.name for path in output_dir.iterdir()), sorted(expected_files))
            manifest = json.loads((output_dir / "manifest.json").read_text())
            self.assertEqual(manifest["archive_format"], "portable-research-archive")
            self.assertEqual(manifest["tool_version"], "1.7.1")
            self.assertEqual(manifest["ledger_ids"], ["oklo-ai-power", "leveraged-etf-discipline"])
            self.assertEqual(manifest["generated_files"], expected_files)
            summary = json.loads((output_dir / "archive-summary.json").read_text())
            self.assertEqual(summary["tool_version"], "1.7.1")
            self.assertEqual(summary["ledger_ids"], manifest["ledger_ids"])
            self.assertEqual(summary["archive"]["ledger_count"], 2)
            self.assertEqual(summary["archive"]["file_count"], len(expected_files))
            self.assertEqual(summary["archive"]["hashed_file_count"], len(expected_files) - 1)
            self.assertEqual(set(summary["file_hashes"]), set(expected_files) - {"archive-summary.json"})
            self.assertNotIn("archive-summary.json", summary["file_hashes"])
            self.assertEqual(
                summary["file_hashes"]["manifest.json"],
                hashlib.sha256((output_dir / "manifest.json").read_bytes()).hexdigest(),
            )

    def test_archive_hashes_are_deterministic_and_no_absolute_paths(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            first_dir = Path(temp) / "first"
            second_dir = Path(temp) / "second"
            first = self.run_cli("archive", str(EXAMPLE), str(ETF_EXAMPLE), "--output-dir", str(first_dir))
            second = self.run_cli("archive", str(EXAMPLE), str(ETF_EXAMPLE), "--output-dir", str(second_dir))
            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertEqual((first_dir / "manifest.json").read_text(), (second_dir / "manifest.json").read_text())
            self.assertEqual(
                (first_dir / "archive-summary.json").read_text(),
                (second_dir / "archive-summary.json").read_text(),
            )
            summary = json.loads((first_dir / "archive-summary.json").read_text())
            for filename, digest in summary["file_hashes"].items():
                self.assertFalse(Path(filename).is_absolute())
                self.assertEqual(digest, hashlib.sha256((first_dir / filename).read_bytes()).hexdigest())
            all_text = "\n".join(path.read_text() for path in first_dir.iterdir())
            self.assertNotIn(str(ROOT), all_text)
            self.assertNotIn(str(first_dir), all_text)
            self.assertNotIn(str(Path(temp)), all_text)
            self.assertNotIn("timestamp", all_text)
            self.assertNotIn("generated_at", all_text)

    def test_archive_validates_all_ledgers_before_writing(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            temp_dir = Path(temp)
            bad_path = temp_dir / "bad.json"
            output_dir = temp_dir / "archive"
            output_dir.mkdir()
            sentinel = output_dir / "sentinel.md"
            sentinel.write_text("keep", encoding="utf-8")
            data = json.loads(ETF_EXAMPLE.read_text())
            data["risks"][0]["source_ids"] = ["missing"]
            bad_path.write_text(json.dumps(data), encoding="utf-8")
            result = self.run_cli("archive", str(EXAMPLE), str(bad_path), "--output-dir", str(output_dir))
            self.assertEqual(result.returncode, 1)
            self.assertIn("ledger: leveraged-etf-discipline", result.stderr)
            self.assertIn("unknown source missing", result.stderr)
            self.assertEqual(sentinel.read_text(), "keep")
            self.assertFalse((output_dir / "manifest.json").exists())

    def test_archive_disambiguates_duplicate_and_reserved_ledger_filenames(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            temp_dir = Path(temp)
            first_path = temp_dir / "first.json"
            second_path = temp_dir / "second.json"
            third_path = temp_dir / "third.json"
            first_data = json.loads(EXAMPLE.read_text())
            second_data = json.loads(ETF_EXAMPLE.read_text())
            third_data = json.loads(EXAMPLE.read_text())
            second_data["thesis_id"] = first_data["thesis_id"]
            third_data["thesis_id"] = "manifest"
            first_path.write_text(json.dumps(first_data), encoding="utf-8")
            second_path.write_text(json.dumps(second_data), encoding="utf-8")
            third_path.write_text(json.dumps(third_data), encoding="utf-8")
            output_dir = temp_dir / "archive"
            result = self.run_cli(
                "archive",
                str(first_path),
                str(second_path),
                str(third_path),
                "--output-dir",
                str(output_dir),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((output_dir / "oklo-ai-power.json").exists())
            self.assertTrue((output_dir / "oklo-ai-power-2.json").exists())
            self.assertTrue((output_dir / "manifest-2.json").exists())
            manifest = json.loads((output_dir / "manifest.json").read_text())
            self.assertEqual(manifest["archive_format"], "portable-research-archive")
            self.assertIn("oklo-ai-power-2-brief.md", manifest["generated_files"])
            self.assertIn("manifest-2.json", manifest["generated_files"])
            self.assertEqual(len(manifest["generated_files"]), len(set(manifest["generated_files"])))

    def test_archive_cleanly_overwrites_output_dir_and_links_are_local(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            output_dir = Path(temp) / "archive"
            output_dir.mkdir()
            stale_file = output_dir / "stale.md"
            stale_dir = output_dir / "nested"
            stale_dir.mkdir()
            (stale_dir / "stale.md").write_text("stale", encoding="utf-8")
            stale_file.write_text("stale", encoding="utf-8")
            result = self.run_cli("archive", str(EXAMPLE), str(ETF_EXAMPLE), "--output-dir", str(output_dir))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse(stale_file.exists())
            self.assertFalse(stale_dir.exists())
            manifest = json.loads((output_dir / "manifest.json").read_text())
            readme_links = [
                line.removeprefix("- [").split("](", 1)[1].removesuffix(")")
                for line in (output_dir / "README.md").read_text().splitlines()
                if line.startswith("- [")
            ]
            self.assertEqual(readme_links, manifest["generated_files"])
            for href in readme_links:
                self.assertIn(href, manifest["generated_files"])
                self.assertNotIn("://", href)
                self.assertFalse(href.startswith(("/", "#")))

    def test_archive_refuses_to_replace_workspace_ancestor(self) -> None:
        result = self.run_cli("archive", str(EXAMPLE), str(ETF_EXAMPLE), "--output-dir", str(ROOT.parent))
        self.assertEqual(result.returncode, 2)
        self.assertIn("refusing to replace current working directory or ancestor", result.stderr)

    def test_archive_requires_two_ledgers(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            result = self.run_cli("archive", str(EXAMPLE), "--output-dir", str(Path(temp) / "archive"))
            self.assertEqual(result.returncode, 2)
            self.assertIn("requires at least two", result.stderr)

    def test_archive_does_not_add_workflow_files_or_dependencies(self) -> None:
        workflow_files = list((ROOT / ".github" / "workflows").glob("*")) if (ROOT / ".github" / "workflows").exists() else []
        dependency_files = [
            path
            for pattern in ("requirements*.txt", "Pipfile", "poetry.lock", "uv.lock")
            for path in ROOT.glob(pattern)
        ]
        pyproject = (ROOT / "pyproject.toml").read_text()
        self.assertEqual(workflow_files, [])
        self.assertEqual(dependency_files, [])
        self.assertIn("dependencies = []", pyproject)

    def test_verify_archive_accepts_checked_in_archive(self) -> None:
        result = self.run_cli("verify-archive", str(ARCHIVE_FIXTURE))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("archive validation summary", result.stdout)
        self.assertIn("generated_files: 19", result.stdout)
        self.assertIn("hashed_files: 18", result.stdout)
        self.assertIn("status: valid", result.stdout)
        self.assertEqual(result.stderr, "")

    def test_verify_archive_reports_tampered_hash_and_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            archive_dir = Path(temp) / "archive"
            shutil.copytree(ARCHIVE_FIXTURE, archive_dir)
            (archive_dir / "portfolio.md").write_text("tampered\n", encoding="utf-8")
            result = self.run_cli("verify-archive", str(archive_dir))
            self.assertEqual(result.returncode, 1)
            self.assertIn("status: invalid", result.stdout)
            self.assertIn("sha256 mismatch: portfolio.md", result.stdout)
            self.assertEqual(result.stderr, "")

    def test_verify_archive_reports_missing_generated_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            archive_dir = Path(temp) / "archive"
            shutil.copytree(ARCHIVE_FIXTURE, archive_dir)
            (archive_dir / "watchlist.md").unlink()
            result = self.run_cli("verify-archive", str(archive_dir))
            self.assertEqual(result.returncode, 1)
            self.assertIn("missing generated file: watchlist.md", result.stdout)

    def test_verify_archive_rejects_symlink_generated_file_before_hashing(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            archive_dir = Path(temp) / "archive"
            shutil.copytree(ARCHIVE_FIXTURE, archive_dir)
            watchlist_path = archive_dir / "watchlist.md"
            watchlist_path.unlink()
            watchlist_path.symlink_to("portfolio.md")
            result = self.run_cli("verify-archive", str(archive_dir))
            self.assertEqual(result.returncode, 1)
            self.assertIn("generated file is a symlink: watchlist.md", result.stdout)
            self.assertNotIn("sha256 mismatch: watchlist.md", result.stdout)

    def test_verify_archive_rejects_symlink_hash_listed_file_before_hashing(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            archive_dir = Path(temp) / "archive"
            shutil.copytree(ARCHIVE_FIXTURE, archive_dir)
            extra_path = archive_dir / "hash-listed-extra.md"
            extra_path.symlink_to("portfolio.md")
            summary_path = archive_dir / "archive-summary.json"
            summary = json.loads(summary_path.read_text())
            summary["file_hashes"]["hash-listed-extra.md"] = "0" * 64
            summary["archive"]["hashed_file_count"] = len(summary["file_hashes"])
            summary_path.write_text(json.dumps(summary, sort_keys=True, indent=2) + "\n", encoding="utf-8")
            result = self.run_cli("verify-archive", str(archive_dir))
            self.assertEqual(result.returncode, 1)
            self.assertIn("hash-listed file is a symlink: hash-listed-extra.md", result.stdout)
            self.assertNotIn("sha256 mismatch: hash-listed-extra.md", result.stdout)

    def test_verify_archive_reports_manifest_summary_ledger_ids_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            archive_dir = Path(temp) / "archive"
            shutil.copytree(ARCHIVE_FIXTURE, archive_dir)
            summary_path = archive_dir / "archive-summary.json"
            summary = json.loads(summary_path.read_text())
            summary["ledger_ids"] = ["leveraged-etf-discipline", "oklo-ai-power"]
            summary_path.write_text(json.dumps(summary, sort_keys=True, indent=2) + "\n", encoding="utf-8")
            result = self.run_cli("verify-archive", str(archive_dir))
            self.assertEqual(result.returncode, 1)
            self.assertIn("manifest ledger_ids do not match archive-summary ledger_ids", result.stdout)

    def test_verify_archive_reports_manifest_summary_tool_version_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            archive_dir = Path(temp) / "archive"
            shutil.copytree(ARCHIVE_FIXTURE, archive_dir)
            summary_path = archive_dir / "archive-summary.json"
            summary = json.loads(summary_path.read_text())
            summary["tool_version"] = "9.9.9"
            summary_path.write_text(json.dumps(summary, sort_keys=True, indent=2) + "\n", encoding="utf-8")
            result = self.run_cli("verify-archive", str(archive_dir))
            self.assertEqual(result.returncode, 1)
            self.assertIn("manifest tool_version does not match archive-summary tool_version", result.stdout)

    def test_verify_archive_reports_archive_ledger_count_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            archive_dir = Path(temp) / "archive"
            shutil.copytree(ARCHIVE_FIXTURE, archive_dir)
            summary_path = archive_dir / "archive-summary.json"
            summary = json.loads(summary_path.read_text())
            summary["archive"]["ledger_count"] = 3
            summary_path.write_text(json.dumps(summary, sort_keys=True, indent=2) + "\n", encoding="utf-8")
            result = self.run_cli("verify-archive", str(archive_dir))
            self.assertEqual(result.returncode, 1)
            self.assertIn("archive ledger_count does not match ledger_ids", result.stdout)

    def test_verify_archive_reports_duplicate_generated_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            archive_dir = Path(temp) / "archive"
            shutil.copytree(ARCHIVE_FIXTURE, archive_dir)
            manifest_path = archive_dir / "manifest.json"
            summary_path = archive_dir / "archive-summary.json"
            manifest = json.loads(manifest_path.read_text())
            summary = json.loads(summary_path.read_text())
            manifest["generated_files"].append("portfolio.md")
            summary["generated_files"].append("portfolio.md")
            summary["archive"]["file_count"] = len(summary["generated_files"])
            manifest_path.write_text(json.dumps(manifest, sort_keys=True, indent=2) + "\n", encoding="utf-8")
            summary["file_hashes"]["manifest.json"] = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
            summary_path.write_text(json.dumps(summary, sort_keys=True, indent=2) + "\n", encoding="utf-8")
            result = self.run_cli("verify-archive", str(archive_dir))
            self.assertEqual(result.returncode, 1)
            self.assertIn("manifest.json generated_files contains duplicate entries: portfolio.md", result.stdout)
            self.assertIn("archive-summary.json generated_files contains duplicate entries: portfolio.md", result.stdout)

    def test_verify_archive_reports_malformed_json_as_unreadable_archive(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            archive_dir = Path(temp) / "archive"
            shutil.copytree(ARCHIVE_FIXTURE, archive_dir)
            (archive_dir / "manifest.json").write_text("{bad json", encoding="utf-8")
            result = self.run_cli("verify-archive", str(archive_dir))
            self.assertEqual(result.returncode, 2)
            self.assertIn("malformed archive", result.stderr)
            self.assertIn("invalid JSON in manifest.json", result.stderr)
            self.assertEqual(result.stdout, "")

    def test_verify_archive_reports_absolute_path_in_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            archive_dir = Path(temp) / "archive"
            shutil.copytree(ARCHIVE_FIXTURE, archive_dir)
            manifest_path = archive_dir / "manifest.json"
            manifest = json.loads(manifest_path.read_text())
            manifest["generated_files"][1] = "/tmp/external.md"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            result = self.run_cli("verify-archive", str(archive_dir))
            self.assertEqual(result.returncode, 1)
            self.assertIn("manifest.json generated_files contains external path: /tmp/external.md", result.stdout)

    def test_verify_archive_reports_self_hash_inclusion(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            archive_dir = Path(temp) / "archive"
            shutil.copytree(ARCHIVE_FIXTURE, archive_dir)
            summary_path = archive_dir / "archive-summary.json"
            summary = json.loads(summary_path.read_text())
            summary["file_hashes"]["archive-summary.json"] = hashlib.sha256(summary_path.read_bytes()).hexdigest()
            summary_path.write_text(json.dumps(summary), encoding="utf-8")
            result = self.run_cli("verify-archive", str(archive_dir))
            self.assertEqual(result.returncode, 1)
            self.assertIn("archive-summary.json must be excluded from file_hashes", result.stdout)

    def test_verify_archive_reports_workflow_and_dependency_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            archive_dir = Path(temp) / "archive"
            shutil.copytree(ARCHIVE_FIXTURE, archive_dir)
            workflow_dir = archive_dir / ".github" / "workflows"
            workflow_dir.mkdir(parents=True)
            (workflow_dir / "ci.yml").write_text("name: ci\n", encoding="utf-8")
            (archive_dir / "requirements.txt").write_text("", encoding="utf-8")
            result = self.run_cli("verify-archive", str(archive_dir))
            self.assertEqual(result.returncode, 1)
            self.assertIn("workflow/dependency files present: .github/workflows/ci.yml, requirements.txt", result.stdout)

    def test_diff_archive_reports_unchanged_fixture_copy(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            old_archive = Path(temp) / "old"
            new_archive = Path(temp) / "new"
            output = Path(temp) / "diff.md"
            json_output = Path(temp) / "diff.json"
            shutil.copytree(ARCHIVE_FIXTURE, old_archive)
            shutil.copytree(ARCHIVE_FIXTURE, new_archive)
            result = self.run_cli(
                "diff-archive",
                str(old_archive),
                str(new_archive),
                "--output",
                str(output),
                "--json-output",
                str(json_output),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(json_output.read_text())
            self.assertEqual(payload["status"], "unchanged")
            self.assertEqual(payload["added_files"], [])
            self.assertEqual(payload["removed_files"], [])
            self.assertEqual(payload["changed_files"], [])
            self.assertEqual(payload["unchanged_count"], 19)
            self.assertEqual(payload["old_ledger_ids"], ["oklo-ai-power", "leveraged-etf-discipline"])
            self.assertEqual(payload["new_ledger_ids"], payload["old_ledger_ids"])
            self.assertIn("- Status: unchanged", output.read_text())
            self.assertIn("- none", output.read_text())

    def test_diff_archive_reports_changed_hash_for_tampered_valid_new_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            old_archive = Path(temp) / "old"
            new_archive = Path(temp) / "new"
            output = Path(temp) / "diff.md"
            json_output = Path(temp) / "diff.json"
            shutil.copytree(ARCHIVE_FIXTURE, old_archive)
            shutil.copytree(ARCHIVE_FIXTURE, new_archive)
            changed_path = new_archive / "portfolio.md"
            changed_path.write_text("tampered but rehashed\n", encoding="utf-8")
            summary_path = new_archive / "archive-summary.json"
            summary = json.loads(summary_path.read_text())
            summary["file_hashes"]["portfolio.md"] = hashlib.sha256(changed_path.read_bytes()).hexdigest()
            summary_path.write_text(json.dumps(summary, sort_keys=True, indent=2) + "\n", encoding="utf-8")
            result = self.run_cli(
                "diff-archive",
                str(old_archive),
                str(new_archive),
                "--output",
                str(output),
                "--json-output",
                str(json_output),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(json_output.read_text())
            self.assertEqual(payload["status"], "changed")
            self.assertEqual(payload["changed_files"], ["portfolio.md"])
            self.assertEqual(payload["unchanged_count"], 18)
            self.assertIn("- portfolio.md", output.read_text())

    def test_diff_archive_reports_added_and_removed_files_from_manifest_and_summary(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            old_archive = Path(temp) / "old"
            new_archive = Path(temp) / "new"
            output = Path(temp) / "diff.md"
            json_output = Path(temp) / "diff.json"
            shutil.copytree(ARCHIVE_FIXTURE, old_archive)
            shutil.copytree(ARCHIVE_FIXTURE, new_archive)

            (new_archive / "notes.md").write_text("new archive note\n", encoding="utf-8")
            (new_archive / "watchlist.md").unlink()
            manifest_path = new_archive / "manifest.json"
            manifest = json.loads(manifest_path.read_text())
            manifest["generated_files"] = [
                item for item in manifest["generated_files"] if item != "watchlist.md"
            ] + ["notes.md"]
            manifest_path.write_text(json.dumps(manifest, sort_keys=True, indent=2) + "\n", encoding="utf-8")

            summary_path = new_archive / "archive-summary.json"
            summary = json.loads(summary_path.read_text())
            summary["generated_files"] = list(manifest["generated_files"])
            summary["file_hashes"].pop("watchlist.md")
            summary["file_hashes"]["notes.md"] = hashlib.sha256((new_archive / "notes.md").read_bytes()).hexdigest()
            summary["file_hashes"]["manifest.json"] = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
            summary["archive"]["file_count"] = len(summary["generated_files"])
            summary["archive"]["hashed_file_count"] = len(summary["file_hashes"])
            summary_path.write_text(json.dumps(summary, sort_keys=True, indent=2) + "\n", encoding="utf-8")

            result = self.run_cli(
                "diff-archive",
                str(old_archive),
                str(new_archive),
                "--output",
                str(output),
                "--json-output",
                str(json_output),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(json_output.read_text())
            self.assertEqual(payload["status"], "changed")
            self.assertEqual(payload["added_files"], ["notes.md"])
            self.assertEqual(payload["removed_files"], ["watchlist.md"])
            self.assertEqual(payload["changed_files"], ["manifest.json"])
            self.assertEqual(payload["old_file_count"], 19)
            self.assertEqual(payload["new_file_count"], 19)
            markdown = output.read_text()
            self.assertIn("## Added Files\n\n- notes.md", markdown)
            self.assertIn("## Removed Files\n\n- watchlist.md", markdown)

    def test_diff_archive_reuses_invalid_archive_failure(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            old_archive = Path(temp) / "old"
            new_archive = Path(temp) / "new"
            output = Path(temp) / "diff.md"
            json_output = Path(temp) / "diff.json"
            shutil.copytree(ARCHIVE_FIXTURE, old_archive)
            shutil.copytree(ARCHIVE_FIXTURE, new_archive)
            (new_archive / "portfolio.md").write_text("tampered\n", encoding="utf-8")
            result = self.run_cli(
                "diff-archive",
                str(old_archive),
                str(new_archive),
                "--output",
                str(output),
                "--json-output",
                str(json_output),
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("archive validation summary", result.stdout)
            self.assertIn("status: invalid", result.stdout)
            self.assertIn("sha256 mismatch: portfolio.md", result.stdout)
            self.assertFalse(output.exists())
            self.assertFalse(json_output.exists())

    def test_diff_archive_reports_malformed_archive_as_unreadable_archive(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            old_archive = Path(temp) / "old"
            new_archive = Path(temp) / "new"
            output = Path(temp) / "diff.md"
            json_output = Path(temp) / "diff.json"
            shutil.copytree(ARCHIVE_FIXTURE, old_archive)
            shutil.copytree(ARCHIVE_FIXTURE, new_archive)
            (new_archive / "manifest.json").write_text("{bad json", encoding="utf-8")
            result = self.run_cli(
                "diff-archive",
                str(old_archive),
                str(new_archive),
                "--output",
                str(output),
                "--json-output",
                str(json_output),
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("malformed archive", result.stderr)
            self.assertIn("invalid JSON in manifest.json", result.stderr)
            self.assertEqual(result.stdout, "")
            self.assertFalse(output.exists())
            self.assertFalse(json_output.exists())

    def test_html_dashboard_writes_static_no_js_dashboard_and_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            output_dir = Path(temp) / "html-dashboard"
            result = self.run_cli(
                "html-dashboard",
                str(EXAMPLE),
                str(ETF_EXAMPLE),
                "--output-dir",
                str(output_dir),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            expected_files = [
                "index.html",
                "style.css",
                "oklo-ai-power.html",
                "leveraged-etf-discipline.html",
                "portfolio.html",
                "evidence-audit.html",
                "watchlist.html",
                "action-plan.html",
                "manifest.json",
            ]
            self.assertEqual(sorted(path.name for path in output_dir.iterdir()), sorted(expected_files))
            self.assertIn("<h1>Dashboard</h1>", (output_dir / "index.html").read_text())
            self.assertIn("<h2>Brief</h2>", (output_dir / "oklo-ai-power.html").read_text())
            self.assertIn("<h1>Portfolio Summary</h1>", (output_dir / "portfolio.html").read_text())
            self.assertIn("<h1>Portfolio Evidence Audit</h1>", (output_dir / "evidence-audit.html").read_text())
            self.assertIn("<h2>Weekly Review List</h2>", (output_dir / "watchlist.html").read_text())
            self.assertIn("<h1>Weekly Action Plan</h1>", (output_dir / "action-plan.html").read_text())
            self.assertNotIn("<script", (output_dir / "index.html").read_text().lower())
            self.assertNotIn("@import", (output_dir / "style.css").read_text().lower())
            manifest = json.loads((output_dir / "manifest.json").read_text())
            self.assertEqual(manifest["tool_version"], "1.7.1")
            self.assertEqual(manifest["ledger_ids"], ["oklo-ai-power", "leveraged-etf-discipline"])
            self.assertEqual(manifest["generated_files"], expected_files)
            self.assertNotIn("timestamp", manifest)
            self.assertNotIn("generated_at", manifest)

    def test_html_dashboard_links_are_generated_local_files_only(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            output_dir = Path(temp) / "html-dashboard"
            result = self.run_cli(
                "html-dashboard",
                str(EXAMPLE),
                str(ETF_EXAMPLE),
                "--output-dir",
                str(output_dir),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            manifest = json.loads((output_dir / "manifest.json").read_text())
            generated_files = set(manifest["generated_files"])
            html_files = [name for name in generated_files if name.endswith(".html")]

            for filename in html_files:
                text = (output_dir / filename).read_text()
                hrefs = re.findall(r'href="([^"]+)"', text)
                self.assertTrue(hrefs, filename)
                for href in hrefs:
                    self.assertIn(href, generated_files)
                    self.assertNotIn("://", href)
                    self.assertFalse(href.startswith(("/", "#")))
                self.assertNotIn("<script", text.lower())
                self.assertIn('<th scope="col">', text)

            css_text = (output_dir / "style.css").read_text()
            self.assertNotIn("@import", css_text.lower())
            self.assertNotIn("url(", css_text.lower())

    def test_html_dashboard_escapes_html_fields(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            temp_dir = Path(temp)
            first_path = temp_dir / "first.json"
            second_path = temp_dir / "second.json"
            first_data = json.loads(EXAMPLE.read_text())
            first_data["title"] = "<script>alert('x')</script> & title"
            first_data["thesis"] = "Thesis has <b>markup</b> & details."
            first_data["assumptions"][0]["statement"] = "Demand > supply & <unsafe>"
            first_data["risks"][0]["name"] = "Risk <img src=x>"
            first_data["sources"][0]["date"] = "2025-01-01"
            first_data["sources"][0]["title"] = "Source & <tag>"
            first_path.write_text(json.dumps(first_data), encoding="utf-8")
            second_path.write_text(ETF_EXAMPLE.read_text(), encoding="utf-8")
            output_dir = temp_dir / "html-dashboard"
            result = self.run_cli("html-dashboard", str(first_path), str(second_path), "--output-dir", str(output_dir))
            self.assertEqual(result.returncode, 0, result.stderr)
            text = (output_dir / "oklo-ai-power.html").read_text()
            audit_text = (output_dir / "evidence-audit.html").read_text()
            action_text = (output_dir / "action-plan.html").read_text()
            self.assertIn("&lt;script&gt;alert(&#x27;x&#x27;)&lt;/script&gt; &amp; title", text)
            self.assertIn("Thesis has &lt;b&gt;markup&lt;/b&gt; &amp; details.", text)
            self.assertIn("Demand &gt; supply &amp; &lt;unsafe&gt;", text)
            self.assertIn("Risk &lt;img src=x&gt;", text)
            self.assertIn("Source &amp; &lt;tag&gt;", text)
            self.assertIn("Risk &lt;img src=x&gt;", action_text)
            self.assertIn("Source &amp; &lt;tag&gt;", audit_text)
            self.assertNotIn("<script>alert", text)
            self.assertNotIn("<img src=x>", text)
            self.assertNotIn("<script>alert", audit_text)
            self.assertNotIn("<script>alert", action_text)

    def test_html_dashboard_manifest_is_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            first_dir = Path(temp) / "first"
            second_dir = Path(temp) / "second"
            first = self.run_cli("html-dashboard", str(EXAMPLE), str(ETF_EXAMPLE), "--output-dir", str(first_dir))
            second = self.run_cli("html-dashboard", str(EXAMPLE), str(ETF_EXAMPLE), "--output-dir", str(second_dir))
            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertEqual((first_dir / "manifest.json").read_text(), (second_dir / "manifest.json").read_text())
            self.assertEqual((first_dir / "index.html").read_text(), (second_dir / "index.html").read_text())
            self.assertEqual((first_dir / "oklo-ai-power.html").read_text(), (second_dir / "oklo-ai-power.html").read_text())

    def test_html_dashboard_disambiguates_duplicate_ledger_ids(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            temp_dir = Path(temp)
            first_path = temp_dir / "first.json"
            second_path = temp_dir / "second.json"
            first_data = json.loads(EXAMPLE.read_text())
            second_data = json.loads(ETF_EXAMPLE.read_text())
            second_data["thesis_id"] = first_data["thesis_id"]
            first_path.write_text(json.dumps(first_data), encoding="utf-8")
            second_path.write_text(json.dumps(second_data), encoding="utf-8")
            output_dir = temp_dir / "html-dashboard"
            result = self.run_cli("html-dashboard", str(first_path), str(second_path), "--output-dir", str(output_dir))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((output_dir / "oklo-ai-power.html").exists())
            self.assertTrue((output_dir / "oklo-ai-power-2.html").exists())
            manifest = json.loads((output_dir / "manifest.json").read_text())
            self.assertEqual(manifest["ledger_ids"], ["oklo-ai-power", "oklo-ai-power"])
            self.assertIn("oklo-ai-power-2.html", manifest["generated_files"])
            self.assertIn('href="oklo-ai-power-2.html"', (output_dir / "index.html").read_text())

    def test_html_dashboard_validates_all_ledgers_before_writing(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            temp_dir = Path(temp)
            bad_path = temp_dir / "bad.json"
            output_dir = temp_dir / "html-dashboard"
            output_dir.mkdir()
            sentinel = output_dir / "sentinel.html"
            sentinel.write_text("keep", encoding="utf-8")
            data = json.loads(ETF_EXAMPLE.read_text())
            data["risks"][0]["source_ids"] = ["missing"]
            bad_path.write_text(json.dumps(data), encoding="utf-8")
            result = self.run_cli("html-dashboard", str(EXAMPLE), str(bad_path), "--output-dir", str(output_dir))
            self.assertEqual(result.returncode, 1)
            self.assertIn("ledger: leveraged-etf-discipline", result.stderr)
            self.assertIn("unknown source missing", result.stderr)
            self.assertEqual(sentinel.read_text(), "keep")
            self.assertFalse((output_dir / "manifest.json").exists())

    def test_html_dashboard_requires_two_ledgers(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            result = self.run_cli("html-dashboard", str(EXAMPLE), "--output-dir", str(Path(temp) / "html-dashboard"))
            self.assertEqual(result.returncode, 2)
            self.assertIn("requires at least two", result.stderr)

    def test_html_dashboard_refuses_symlinked_output_dir(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            temp_dir = Path(temp)
            real_dir = temp_dir / "real"
            real_dir.mkdir()
            sentinel = real_dir / "sentinel.html"
            sentinel.write_text("keep", encoding="utf-8")
            output_dir = temp_dir / "html-dashboard-link"
            try:
                output_dir.symlink_to(real_dir, target_is_directory=True)
            except OSError as exc:
                self.skipTest(f"symlink unavailable: {exc}")

            result = self.run_cli("html-dashboard", str(EXAMPLE), str(ETF_EXAMPLE), "--output-dir", str(output_dir))
            self.assertEqual(result.returncode, 2)
            self.assertIn("output dir is not a directory", result.stderr)
            self.assertEqual(sentinel.read_text(), "keep")
            self.assertFalse((real_dir / "manifest.json").exists())

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
            self.assertEqual(payload["ledger_version"], "1.7.1")
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
                    "decision-memo",
                    [
                        "decision-memo",
                        str(EXAMPLE),
                        "--output",
                        str(temp_dir / "oklo-ai-power-decision-memo.md"),
                        "--json-output",
                        str(temp_dir / "oklo-ai-power-decision-memo.json"),
                    ],
                    ["oklo-ai-power-decision-memo.md", "oklo-ai-power-decision-memo.json"],
                ),
                (
                    "scenario-plan",
                    [
                        "scenario-plan",
                        str(EXAMPLE),
                        "--output",
                        str(temp_dir / "oklo-ai-power-scenario-plan.md"),
                        "--json-output",
                        str(temp_dir / "oklo-ai-power-scenario-plan.json"),
                    ],
                    ["oklo-ai-power-scenario-plan.md", "oklo-ai-power-scenario-plan.json"],
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
                    "evidence-audit",
                    [
                        "evidence-audit",
                        str(EXAMPLE),
                        str(ETF_EXAMPLE),
                        "--output",
                        str(temp_dir / "evidence-audit.md"),
                        "--json-output",
                        str(temp_dir / "evidence-audit.json"),
                    ],
                    ["evidence-audit.md", "evidence-audit.json"],
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
                (
                    "watchlist",
                    [
                        "watchlist",
                        str(EXAMPLE),
                        str(ETF_EXAMPLE),
                        "--output",
                        str(temp_dir / "watchlist.md"),
                        "--json-output",
                        str(temp_dir / "watchlist.json"),
                    ],
                    ["watchlist.md", "watchlist.json"],
                ),
                (
                    "action-plan",
                    [
                        "action-plan",
                        str(EXAMPLE),
                        str(ETF_EXAMPLE),
                        "--output",
                        str(temp_dir / "action-plan.md"),
                        "--json-output",
                        str(temp_dir / "action-plan.json"),
                    ],
                    ["action-plan.md", "action-plan.json"],
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
