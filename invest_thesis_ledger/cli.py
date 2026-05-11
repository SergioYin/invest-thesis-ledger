"""Command line interface for invest-thesis-ledger."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Callable, Optional, Sequence

from . import __version__
from .render import history_payload, render_brief, render_history, render_risk, risk_payload, to_json
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
    validate.add_argument("ledger")
    validate.set_defaults(func=_cmd_validate)

    brief = subparsers.add_parser("brief", help="render a source-attributed Markdown brief")
    brief.add_argument("ledger")
    brief.add_argument("--output", required=True)
    brief.set_defaults(func=_cmd_brief)

    risk = subparsers.add_parser("risk", help="render a risk/checklist report")
    risk.add_argument("ledger")
    risk.add_argument("--output", required=True)
    risk.add_argument("--json-output", required=True)
    risk.set_defaults(func=_cmd_risk)

    history = subparsers.add_parser("history", help="render a review timeline and thesis drift report")
    history.add_argument("ledger")
    history.add_argument("--output", required=True)
    history.add_argument("--json-output", required=True)
    history.set_defaults(func=_cmd_history)
    return parser


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
