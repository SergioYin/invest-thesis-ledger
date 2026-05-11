"""Command line interface for invest-thesis-ledger."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Callable, Optional, Sequence

from . import __version__
from .render import (
    broker_matrix_payload,
    calendar_payload,
    compare_payload,
    decision_memo_payload,
    evidence_payload,
    exposure_payload,
    history_payload,
    portfolio_payload,
    render_broker_matrix,
    render_brief,
    render_calendar,
    render_compare,
    render_decision_memo,
    render_evidence,
    render_exposure,
    render_history,
    render_portfolio,
    render_review_queue,
    render_risk,
    render_scenario_plan,
    risk_payload,
    review_queue_payload,
    scenario_plan_payload,
    to_json,
)
from .schema import load_ledger, validate_ledger, validation_summary


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="invest-thesis-ledger",
        description="Validate and render investment thesis ledgers.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate", help="validate required schema and print summary")
    _add_ledger_arg(validate)
    validate.set_defaults(func=_cmd_validate)

    brief = subparsers.add_parser("brief", help="render a source-attributed Markdown brief")
    _add_ledger_arg(brief)
    _add_output_args(brief, json_output=False)
    brief.set_defaults(func=_cmd_brief)

    risk = subparsers.add_parser("risk", help="render a risk/checklist report")
    _add_ledger_arg(risk)
    _add_output_args(risk)
    risk.set_defaults(func=_cmd_risk)

    history = subparsers.add_parser("history", help="render a review timeline and thesis drift report")
    _add_ledger_arg(history)
    _add_output_args(history)
    history.set_defaults(func=_cmd_history)

    compare = subparsers.add_parser("compare", help="compare two ledgers and render thesis drift")
    compare.add_argument("old", metavar="OLD_LEDGER", help="prior ledger JSON file")
    compare.add_argument("new", metavar="NEW_LEDGER", help="current ledger JSON file")
    _add_output_args(compare)
    compare.set_defaults(func=_cmd_compare)

    calendar = subparsers.add_parser("calendar", help="render a catalyst calendar")
    _add_ledger_arg(calendar)
    _add_output_args(calendar)
    calendar.set_defaults(func=_cmd_calendar)

    evidence = subparsers.add_parser("evidence", help="render source coverage and stale-source warnings")
    _add_ledger_arg(evidence)
    _add_output_args(evidence)
    evidence.set_defaults(func=_cmd_evidence)

    broker_matrix = subparsers.add_parser(
        "broker-matrix", help="render broker/institution rating, target, and thesis matrix"
    )
    _add_ledger_arg(broker_matrix)
    _add_output_args(broker_matrix)
    broker_matrix.set_defaults(func=_cmd_broker_matrix)

    exposure = subparsers.add_parser("exposure", help="render exposure checklist from risks and position rules")
    _add_ledger_arg(exposure)
    _add_output_args(exposure)
    exposure.set_defaults(func=_cmd_exposure)

    decision_memo = subparsers.add_parser(
        "decision-memo",
        help="render a pre-trade/review decision memo",
        description="render a pre-trade/review decision memo.",
    )
    _add_ledger_arg(decision_memo)
    _add_output_args(decision_memo)
    decision_memo.set_defaults(func=_cmd_decision_memo)

    scenario_plan = subparsers.add_parser(
        "scenario-plan",
        help="render a deterministic base/bull/bear scenario plan",
        description="render a deterministic base/bull/bear scenario plan.",
    )
    _add_ledger_arg(scenario_plan)
    _add_output_args(scenario_plan)
    scenario_plan.set_defaults(func=_cmd_scenario_plan)

    portfolio = subparsers.add_parser("portfolio", help="aggregate two or more ledgers into a portfolio summary")
    portfolio.add_argument("ledgers", metavar="LEDGER", nargs="+", help="ledger JSON file")
    _add_output_args(portfolio)
    portfolio.set_defaults(func=_cmd_portfolio)

    review_queue = subparsers.add_parser(
        "review-queue",
        help="prioritize two or more ledgers for human review",
        description="prioritize two or more ledgers for human review.",
    )
    review_queue.add_argument("ledgers", metavar="LEDGER", nargs="+", help="ledger JSON file")
    _add_output_args(review_queue)
    review_queue.set_defaults(func=_cmd_review_queue)

    init_template = subparsers.add_parser("init-template", help="create a deterministic starter ledger")
    init_template.add_argument("--asset", required=True, metavar="TICKER", help="asset ticker or symbol")
    init_template.add_argument("--name", required=True, metavar="NAME", help="asset or issuer name")
    init_template.add_argument("--type", required=True, metavar="TYPE", help="asset class or instrument type")
    init_template.add_argument("--output", required=True, metavar="PATH", help="write starter ledger JSON to PATH")
    init_template.set_defaults(func=_cmd_init_template)
    return parser


def _add_ledger_arg(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("ledger", metavar="LEDGER", help="ledger JSON file")


def _add_output_args(parser: argparse.ArgumentParser, json_output: bool = True) -> None:
    parser.add_argument("--output", required=True, metavar="PATH", help="write Markdown output to PATH")
    if json_output:
        parser.add_argument("--json-output", required=True, metavar="PATH", help="write JSON output to PATH")


def _cmd_validate(args: argparse.Namespace) -> int:
    ledger = _load_or_report(args.ledger)
    if ledger is None:
        return 2
    errors, warnings = validate_ledger(ledger)
    sys.stdout.write(validation_summary(ledger, errors, warnings))
    return 1 if errors else 0


def _cmd_brief(args: argparse.Namespace) -> int:
    return _render_validated(args.ledger, ((args.output, render_brief),))


def _cmd_risk(args: argparse.Namespace) -> int:
    return _render_validated(
        args.ledger,
        (
            (args.output, render_risk),
            (args.json_output, lambda ledger: to_json(risk_payload(ledger))),
        ),
    )


def _cmd_history(args: argparse.Namespace) -> int:
    return _render_validated(
        args.ledger,
        (
            (args.output, render_history),
            (args.json_output, lambda ledger: to_json(history_payload(ledger))),
        ),
    )


def _cmd_compare(args: argparse.Namespace) -> int:
    old = _load_or_report(args.old)
    if old is None:
        return 2
    new = _load_or_report(args.new)
    if new is None:
        return 2
    old_errors, old_warnings = validate_ledger(old)
    new_errors, new_warnings = validate_ledger(new)
    if old_errors or new_errors:
        if old_errors:
            sys.stderr.write(validation_summary(old, old_errors, old_warnings))
        if new_errors:
            sys.stderr.write(validation_summary(new, new_errors, new_warnings))
        return 1
    outputs = (
        (args.output, lambda _ledger: render_compare(old, new)),
        (args.json_output, lambda _ledger: to_json(compare_payload(old, new))),
    )
    for output_path, renderer in outputs:
        _write_text(output_path, renderer(new))
    sys.stdout.write(f"wrote: {args.output}, {args.json_output}\n")
    return 0


def _cmd_calendar(args: argparse.Namespace) -> int:
    return _render_validated(
        args.ledger,
        (
            (args.output, render_calendar),
            (args.json_output, lambda ledger: to_json(calendar_payload(ledger))),
        ),
    )


def _cmd_evidence(args: argparse.Namespace) -> int:
    return _render_validated(
        args.ledger,
        (
            (args.output, render_evidence),
            (args.json_output, lambda ledger: to_json(evidence_payload(ledger))),
        ),
    )


def _cmd_broker_matrix(args: argparse.Namespace) -> int:
    return _render_validated(
        args.ledger,
        (
            (args.output, render_broker_matrix),
            (args.json_output, lambda ledger: to_json(broker_matrix_payload(ledger))),
        ),
    )


def _cmd_exposure(args: argparse.Namespace) -> int:
    return _render_validated(
        args.ledger,
        (
            (args.output, render_exposure),
            (args.json_output, lambda ledger: to_json(exposure_payload(ledger))),
        ),
    )


def _cmd_decision_memo(args: argparse.Namespace) -> int:
    return _render_validated(
        args.ledger,
        (
            (args.output, render_decision_memo),
            (args.json_output, lambda ledger: to_json(decision_memo_payload(ledger))),
        ),
    )


def _cmd_scenario_plan(args: argparse.Namespace) -> int:
    return _render_validated(
        args.ledger,
        (
            (args.output, render_scenario_plan),
            (args.json_output, lambda ledger: to_json(scenario_plan_payload(ledger))),
        ),
    )


def _cmd_portfolio(args: argparse.Namespace) -> int:
    if len(args.ledgers) < 2:
        sys.stderr.write("error: portfolio requires at least two ledger JSON files\n")
        return 2
    ledgers = []
    for path in args.ledgers:
        ledger = _load_or_report(path)
        if ledger is None:
            return 2
        ledgers.append(ledger)

    validation_results = [(ledger, *validate_ledger(ledger)) for ledger in ledgers]
    if any(errors for _, errors, _ in validation_results):
        for ledger, errors, warnings in validation_results:
            if errors:
                sys.stderr.write(validation_summary(ledger, errors, warnings))
        return 1
    for ledger, errors, warnings in validation_results:
        if warnings:
            sys.stderr.write(validation_summary(ledger, errors, warnings))

    _write_text(args.output, render_portfolio(ledgers))
    _write_text(args.json_output, to_json(portfolio_payload(ledgers)))
    sys.stdout.write(f"wrote: {args.output}, {args.json_output}\n")
    return 0


def _cmd_review_queue(args: argparse.Namespace) -> int:
    if len(args.ledgers) < 2:
        sys.stderr.write("error: review-queue requires at least two ledger JSON files\n")
        return 2
    ledgers = []
    for path in args.ledgers:
        ledger = _load_or_report(path)
        if ledger is None:
            return 2
        ledgers.append(ledger)

    validation_results = [(ledger, *validate_ledger(ledger)) for ledger in ledgers]
    if any(errors for _, errors, _ in validation_results):
        for ledger, errors, warnings in validation_results:
            if errors:
                sys.stderr.write(validation_summary(ledger, errors, warnings))
        return 1
    for ledger, errors, warnings in validation_results:
        if warnings:
            sys.stderr.write(validation_summary(ledger, errors, warnings))

    _write_text(args.output, render_review_queue(ledgers))
    _write_text(args.json_output, to_json(review_queue_payload(ledgers)))
    sys.stdout.write(f"wrote: {args.output}, {args.json_output}\n")
    return 0


def _cmd_init_template(args: argparse.Namespace) -> int:
    ledger = _starter_ledger(args.asset, args.name, args.type)
    _write_text(args.output, to_json(ledger))
    sys.stdout.write(f"wrote: {args.output}\n")
    return 0


def _render_validated(
    ledger_path: str,
    outputs: Sequence[tuple[str, Callable[[dict], str]]],
) -> int:
    ledger = _load_or_report(ledger_path)
    if ledger is None:
        return 2
    errors, warnings = validate_ledger(ledger)
    if errors:
        sys.stderr.write(validation_summary(ledger, errors, warnings))
        return 1
    if warnings:
        sys.stderr.write(validation_summary(ledger, errors, warnings))
    for output_path, renderer in outputs:
        _write_text(output_path, renderer(ledger))
    sys.stdout.write(f"wrote: {', '.join(path for path, _ in outputs)}\n")
    return 0


def _load_or_report(path: str) -> Optional[dict]:
    try:
        return load_ledger(path)
    except OSError as exc:
        sys.stderr.write(f"error: cannot read {path}: {exc}\n")
    except ValueError as exc:
        sys.stderr.write(f"error: invalid ledger {path}: {exc}\n")
    return None


def _write_text(path: str, text: str) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(text, encoding="utf-8")


def _starter_ledger(asset: str, name: str, asset_type: str) -> dict:
    ticker = asset.strip().upper()
    slug = "".join(char.lower() if char.isalnum() else "-" for char in ticker).strip("-") or "asset"
    clean_name = name.strip()
    clean_type = asset_type.strip()
    return {
        "ledger_version": "0.7.0",
        "thesis_id": f"{slug}-thesis",
        "title": f"{clean_name} Thesis Ledger",
        "asset": {
            "name": clean_name,
            "type": clean_type,
            "ticker": ticker,
        },
        "created": "1970-01-01",
        "updated": "1970-01-01",
        "thesis": "TODO: state the current investment thesis.",
        "sources": [
            {
                "id": "S1",
                "title": "TODO: primary source title",
                "publisher": "TODO: publisher",
                "date": "1970-01-01",
                "url": "TODO: source URL or internal reference",
            }
        ],
        "positions": [],
        "assumptions": [
            {
                "id": "A1",
                "statement": f"TODO: key assumption for {clean_name or ticker}.",
                "confidence": "watch",
                "source_ids": ["S1"],
            }
        ],
        "broker_views": [],
        "catalysts": [],
        "risks": [
            {
                "id": "R1",
                "name": "TODO: primary risk",
                "severity": "watch",
                "probability": "watch",
                "mitigation": "TODO: mitigation or review trigger.",
                "tags": ["TODO"],
                "source_ids": ["S1"],
            }
        ],
        "position_rules": [],
        "checklist": [],
        "reviews": [
            {
                "date": "1970-01-01",
                "decision": "watch",
                "summary": "TODO: initial review summary.",
                "drift": "none recorded",
                "source_ids": ["S1"],
            }
        ],
    }
