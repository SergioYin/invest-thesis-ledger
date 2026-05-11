"""Command line interface for invest-thesis-ledger."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Callable, Optional, Sequence

from . import __version__
from .render import (
    calendar_payload,
    compare_payload,
    evidence_payload,
    history_payload,
    render_brief,
    render_calendar,
    render_compare,
    render_evidence,
    render_history,
    render_risk,
    risk_payload,
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
