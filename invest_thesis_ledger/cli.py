"""Command line interface for invest-thesis-ledger."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Callable, Mapping, Optional, Sequence

from . import __version__
from .render import (
    action_plan_payload,
    broker_matrix_payload,
    calendar_payload,
    compare_payload,
    decision_memo_payload,
    evidence_audit_payload,
    evidence_payload,
    exposure_payload,
    history_payload,
    portfolio_payload,
    render_action_plan,
    render_broker_matrix,
    render_brief,
    render_calendar,
    render_compare,
    render_decision_memo,
    render_evidence,
    render_evidence_audit,
    render_exposure,
    render_history,
    render_portfolio,
    render_review_queue,
    render_risk,
    render_scenario_plan,
    render_watchlist,
    risk_payload,
    review_queue_payload,
    scenario_plan_payload,
    to_json,
    watchlist_payload,
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

    evidence_audit = subparsers.add_parser(
        "evidence-audit",
        help="audit portfolio evidence quality across two or more ledgers",
        description="audit portfolio evidence quality across two or more ledgers.",
    )
    evidence_audit.add_argument("ledgers", metavar="LEDGER", nargs="+", help="ledger JSON file")
    _add_output_args(evidence_audit)
    evidence_audit.set_defaults(func=_cmd_evidence_audit)

    review_queue = subparsers.add_parser(
        "review-queue",
        help="prioritize two or more ledgers for human review",
        description="prioritize two or more ledgers for human review.",
    )
    review_queue.add_argument("ledgers", metavar="LEDGER", nargs="+", help="ledger JSON file")
    _add_output_args(review_queue)
    review_queue.set_defaults(func=_cmd_review_queue)

    watchlist = subparsers.add_parser(
        "watchlist",
        help="render a weekly watchlist from two or more ledgers",
        description="render a weekly watchlist from two or more ledgers.",
    )
    watchlist.add_argument("ledgers", metavar="LEDGER", nargs="+", help="ledger JSON file")
    _add_output_args(watchlist)
    watchlist.set_defaults(func=_cmd_watchlist)

    action_plan = subparsers.add_parser(
        "action-plan",
        help="render a weekly action plan from two or more ledgers",
        description="render a weekly action plan from two or more ledgers.",
    )
    action_plan.add_argument("ledgers", metavar="LEDGER", nargs="+", help="ledger JSON file")
    _add_output_args(action_plan)
    action_plan.set_defaults(func=_cmd_action_plan)

    demo_bundle = subparsers.add_parser(
        "demo-bundle",
        help="write a static Markdown demo bundle from two or more ledgers",
        description="write a static Markdown demo bundle from two or more ledgers.",
    )
    demo_bundle.add_argument("ledgers", metavar="LEDGER", nargs="+", help="ledger JSON file")
    demo_bundle.add_argument("--output-dir", required=True, metavar="DIR", help="write static demo bundle to DIR")
    demo_bundle.set_defaults(func=_cmd_demo_bundle)

    archive = subparsers.add_parser(
        "archive",
        help="write a deterministic portable research archive from two or more ledgers",
        description="write a deterministic portable research archive from two or more ledgers.",
    )
    archive.add_argument("ledgers", metavar="LEDGER", nargs="+", help="ledger JSON file")
    archive.add_argument("--output-dir", required=True, metavar="DIR", help="write portable archive to DIR")
    archive.set_defaults(func=_cmd_archive)

    verify_archive = subparsers.add_parser(
        "verify-archive",
        help="verify a deterministic portable research archive",
        description="verify a deterministic portable research archive.",
    )
    verify_archive.add_argument("archive_dir", metavar="ARCHIVE_DIR", help="archive directory created by archive")
    verify_archive.set_defaults(func=_cmd_verify_archive)

    diff_archive = subparsers.add_parser(
        "diff-archive",
        help="compare two deterministic portable research archives",
        description="compare two deterministic portable research archives.",
    )
    diff_archive.add_argument("old_archive_dir", metavar="OLD_ARCHIVE_DIR", help="prior archive directory")
    diff_archive.add_argument("new_archive_dir", metavar="NEW_ARCHIVE_DIR", help="current archive directory")
    _add_output_args(diff_archive)
    diff_archive.set_defaults(func=_cmd_diff_archive)

    html_dashboard = subparsers.add_parser(
        "html-dashboard",
        help="write a static no-JS HTML dashboard from two or more ledgers",
        description="write a static no-JS HTML dashboard from two or more ledgers.",
    )
    html_dashboard.add_argument("ledgers", metavar="LEDGER", nargs="+", help="ledger JSON file")
    html_dashboard.add_argument("--output-dir", required=True, metavar="DIR", help="write static HTML dashboard to DIR")
    html_dashboard.set_defaults(func=_cmd_html_dashboard)

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
    status = _write_rendered_outputs(new, outputs)
    if status:
        return status
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

    status = _write_text_outputs(
        (
            (args.output, render_portfolio(ledgers)),
            (args.json_output, to_json(portfolio_payload(ledgers))),
        )
    )
    if status:
        return status
    sys.stdout.write(f"wrote: {args.output}, {args.json_output}\n")
    return 0


def _cmd_evidence_audit(args: argparse.Namespace) -> int:
    ledgers, status = _load_validated_ledgers(args.ledgers, "evidence-audit")
    if ledgers is None:
        return status

    status = _write_text_outputs(
        (
            (args.output, render_evidence_audit(ledgers)),
            (args.json_output, to_json(evidence_audit_payload(ledgers))),
        )
    )
    if status:
        return status
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

    status = _write_text_outputs(
        (
            (args.output, render_review_queue(ledgers)),
            (args.json_output, to_json(review_queue_payload(ledgers))),
        )
    )
    if status:
        return status
    sys.stdout.write(f"wrote: {args.output}, {args.json_output}\n")
    return 0


def _cmd_watchlist(args: argparse.Namespace) -> int:
    ledgers, status = _load_validated_ledgers(args.ledgers, "watchlist")
    if ledgers is None:
        return status

    status = _write_text_outputs(
        (
            (args.output, render_watchlist(ledgers)),
            (args.json_output, to_json(watchlist_payload(ledgers))),
        )
    )
    if status:
        return status
    sys.stdout.write(f"wrote: {args.output}, {args.json_output}\n")
    return 0


def _cmd_action_plan(args: argparse.Namespace) -> int:
    ledgers, status = _load_validated_ledgers(args.ledgers, "action-plan")
    if ledgers is None:
        return status

    status = _write_text_outputs(
        (
            (args.output, render_action_plan(ledgers)),
            (args.json_output, to_json(action_plan_payload(ledgers))),
        )
    )
    if status:
        return status
    sys.stdout.write(f"wrote: {args.output}, {args.json_output}\n")
    return 0


def _cmd_demo_bundle(args: argparse.Namespace) -> int:
    ledgers, status = _load_validated_ledgers(args.ledgers, "demo-bundle")
    if ledgers is None:
        return status

    output_dir = Path(args.output_dir)
    files = _demo_bundle_files(ledgers)
    if output_dir.exists() and (not output_dir.is_dir() or output_dir.is_symlink()):
        sys.stderr.write(f"error: output dir is not a directory: {output_dir}\n")
        return 2
    if _is_unsafe_output_dir(output_dir):
        sys.stderr.write(f"error: refusing to replace current working directory or ancestor: {output_dir}\n")
        return 2

    status = _write_output_dir(output_dir, lambda: _write_demo_bundle_dir(output_dir, files))
    if status:
        return status
    sys.stdout.write(f"wrote: {output_dir}\n")
    return 0


def _cmd_archive(args: argparse.Namespace) -> int:
    ledgers, status = _load_validated_ledgers(args.ledgers, "archive")
    if ledgers is None:
        return status

    output_dir = Path(args.output_dir)
    files = _archive_files(ledgers)
    if output_dir.exists() and (not output_dir.is_dir() or output_dir.is_symlink()):
        sys.stderr.write(f"error: output dir is not a directory: {output_dir}\n")
        return 2
    if _is_unsafe_output_dir(output_dir):
        sys.stderr.write(f"error: refusing to replace current working directory or ancestor: {output_dir}\n")
        return 2

    status = _write_output_dir(output_dir, lambda: _write_demo_bundle_dir(output_dir, files))
    if status:
        return status
    sys.stdout.write(f"wrote: {output_dir}\n")
    return 0


def _cmd_verify_archive(args: argparse.Namespace) -> int:
    archive_dir = Path(args.archive_dir)
    try:
        errors, summary = _verify_archive_dir(archive_dir)
    except OSError as exc:
        sys.stderr.write(f"error: cannot read archive {archive_dir}: {exc}\n")
        return 2
    except ValueError as exc:
        sys.stderr.write(f"error: malformed archive {archive_dir}: {exc}\n")
        return 2

    sys.stdout.write(_archive_validation_summary(summary, errors))
    return 1 if errors else 0


def _cmd_diff_archive(args: argparse.Namespace) -> int:
    old_archive_dir = Path(args.old_archive_dir)
    new_archive_dir = Path(args.new_archive_dir)
    try:
        old_errors, old_summary = _read_archive_for_diff(old_archive_dir)
        new_errors, new_summary = _read_archive_for_diff(new_archive_dir)
    except OSError as exc:
        sys.stderr.write(f"error: cannot read archive {exc}\n")
        return 2
    except ValueError as exc:
        sys.stderr.write(f"error: malformed archive {exc}\n")
        return 2

    if old_errors or new_errors:
        if old_errors:
            sys.stdout.write(_archive_validation_summary(old_summary, old_errors))
        if new_errors:
            sys.stdout.write(_archive_validation_summary(new_summary, new_errors))
        return 1

    payload = _archive_diff_payload(old_summary, new_summary)
    status = _write_text_outputs(
        (
            (args.output, _render_archive_diff(payload)),
            (args.json_output, to_json(payload)),
        )
    )
    if status:
        return status
    sys.stdout.write(f"wrote: {args.output}, {args.json_output}\n")
    return 0


def _read_archive_for_diff(archive_dir: Path) -> tuple[list[str], dict]:
    try:
        return _verify_archive_dir(archive_dir)
    except OSError as exc:
        raise OSError(f"{archive_dir}: {exc}") from exc
    except ValueError as exc:
        raise ValueError(f"{archive_dir}: {exc}") from exc


def _cmd_html_dashboard(args: argparse.Namespace) -> int:
    ledgers, status = _load_validated_ledgers(args.ledgers, "html-dashboard")
    if ledgers is None:
        return status

    output_dir = Path(args.output_dir)
    files = _html_dashboard_files(ledgers)
    if output_dir.exists() and (not output_dir.is_dir() or output_dir.is_symlink()):
        sys.stderr.write(f"error: output dir is not a directory: {output_dir}\n")
        return 2
    if _is_unsafe_output_dir(output_dir):
        sys.stderr.write(f"error: refusing to replace current working directory or ancestor: {output_dir}\n")
        return 2

    status = _write_output_dir(output_dir, lambda: _write_demo_bundle_dir(output_dir, files))
    if status:
        return status
    sys.stdout.write(f"wrote: {output_dir}\n")
    return 0


def _cmd_init_template(args: argparse.Namespace) -> int:
    ledger = _starter_ledger(args.asset, args.name, args.type)
    status = _write_text_outputs(((args.output, to_json(ledger)),))
    if status:
        return status
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
    status = _write_rendered_outputs(ledger, outputs)
    if status:
        return status
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


def _load_validated_ledgers(paths: Sequence[str], command: str) -> tuple[Optional[list[dict]], int]:
    if len(paths) < 2:
        sys.stderr.write(f"error: {command} requires at least two ledger JSON files\n")
        return None, 2
    ledgers = []
    for path in paths:
        ledger = _load_or_report(path)
        if ledger is None:
            return None, 2
        ledgers.append(ledger)

    validation_results = [(ledger, *validate_ledger(ledger)) for ledger in ledgers]
    if any(errors for _, errors, _ in validation_results):
        for ledger, errors, warnings in validation_results:
            if errors:
                sys.stderr.write(validation_summary(ledger, errors, warnings))
        return None, 1
    for ledger, errors, warnings in validation_results:
        if warnings:
            sys.stderr.write(validation_summary(ledger, errors, warnings))
    return ledgers, 0


def _write_text(path: str, text: str) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(text, encoding="utf-8")


def _write_rendered_outputs(ledger: dict, outputs: Sequence[tuple[str, Callable[[dict], str]]]) -> int:
    for output_path, renderer in outputs:
        status = _write_text_outputs(((output_path, renderer(ledger)),))
        if status:
            return status
    return 0


def _write_text_outputs(outputs: Sequence[tuple[str, str]]) -> int:
    for output_path, text in outputs:
        status = _write_output(output_path, lambda output_path=output_path, text=text: _write_text(output_path, text))
        if status:
            return status
    return 0


def _write_output(path: object, write: Callable[[], None]) -> int:
    try:
        write()
    except OSError as exc:
        _report_output_write_error(path, exc)
        return 2
    return 0


def _write_output_dir(path: object, write: Callable[[], None]) -> int:
    try:
        write()
    except OSError as exc:
        _report_output_write_error(path, exc)
        return 2
    except ValueError as exc:
        sys.stderr.write(f"error: cannot write output {path}: {exc}\n")
        return 2
    return 0


def _report_output_write_error(path: object, exc: OSError) -> None:
    reason = exc.strerror or str(exc)
    sys.stderr.write(f"error: cannot write output {path}: {reason}\n")


def _is_unsafe_output_dir(output_dir: Path) -> bool:
    resolved = output_dir.resolve()
    cwd = Path.cwd().resolve()
    return resolved == cwd or resolved in cwd.parents


def _write_demo_bundle_dir(output_dir: Path, files: Sequence[tuple[str, str]]) -> None:
    parent = output_dir.parent
    parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=f".{output_dir.name}.", suffix=".tmp", dir=parent))
    backup: Optional[Path] = None
    try:
        for filename, text in files:
            path = Path(filename)
            if path.is_absolute() or path.name != filename:
                raise ValueError(f"generated filename must stay inside output dir: {filename}")
            (stage / filename).write_text(text, encoding="utf-8")

        if output_dir.exists():
            backup = Path(tempfile.mkdtemp(prefix=f".{output_dir.name}.", suffix=".backup", dir=parent))
            backup.rmdir()
            output_dir.replace(backup)
        stage.replace(output_dir)
        if backup is not None:
            shutil.rmtree(backup)
    except Exception:
        if stage.exists():
            shutil.rmtree(stage)
        if backup is not None and backup.exists() and not output_dir.exists():
            backup.replace(output_dir)
        raise


def _demo_bundle_files(ledgers: Sequence[dict]) -> list[tuple[str, str]]:
    body_files: list[tuple[str, str]] = []
    ledger_prefixes = _bundle_prefixes(ledgers)
    ledger_artifacts = (
        ("brief", render_brief),
        ("risk", render_risk),
        ("history", render_history),
        ("decision-memo", render_decision_memo),
        ("scenario-plan", render_scenario_plan),
    )
    for ledger, ledger_id in zip(ledgers, ledger_prefixes):
        for suffix, renderer in ledger_artifacts:
            body_files.append((f"{ledger_id}-{suffix}.md", renderer(ledger)))
    body_files.extend(
        [
            ("portfolio-summary.md", render_portfolio(ledgers)),
            ("evidence-audit.md", render_evidence_audit(ledgers)),
            ("watchlist.md", render_watchlist(ledgers)),
            ("action-plan.md", render_action_plan(ledgers)),
        ]
    )
    filenames = ["index.md"] + [filename for filename, _ in body_files] + ["manifest.json"]
    index_text = _render_demo_bundle_index(ledgers, filenames)
    manifest = {
        "generated_files": filenames,
        "ledger_ids": [str(ledger["thesis_id"]) for ledger in ledgers],
        "tool_version": __version__,
    }
    files = [("index.md", index_text)]
    files.extend(body_files)
    files.append(("manifest.json", to_json(manifest)))
    return files


def _archive_files(ledgers: Sequence[dict]) -> list[tuple[str, str]]:
    body_files: list[tuple[str, str]] = []
    ledger_artifacts = (
        ("brief", render_brief),
        ("risk", render_risk),
        ("history", render_history),
        ("decision", render_decision_memo),
        ("scenario", render_scenario_plan),
    )
    aggregate_files = [
        "portfolio.md",
        "evidence-audit.md",
        "watchlist.md",
        "action-plan.md",
    ]
    metadata_files = ["README.md", "manifest.json", "archive-summary.json"]
    ledger_prefixes = _bundle_prefixes(
        ledgers,
        reserved_filenames=metadata_files + aggregate_files,
        primary_extension=".json",
        artifact_suffixes=[suffix for suffix, _renderer in ledger_artifacts],
    )
    for ledger, ledger_id in zip(ledgers, ledger_prefixes):
        body_files.append((f"{ledger_id}.json", to_json(ledger)))
        for suffix, renderer in ledger_artifacts:
            body_files.append((f"{ledger_id}-{suffix}.md", renderer(ledger)))
    body_files.extend(
        [
            (aggregate_files[0], render_portfolio(ledgers)),
            (aggregate_files[1], render_evidence_audit(ledgers)),
            (aggregate_files[2], render_watchlist(ledgers)),
            (aggregate_files[3], render_action_plan(ledgers)),
        ]
    )
    filenames = [metadata_files[0]] + [filename for filename, _ in body_files] + metadata_files[1:]
    manifest = {
        "archive_format": "portable-research-archive",
        "generated_files": filenames,
        "ledger_ids": [str(ledger["thesis_id"]) for ledger in ledgers],
        "tool_version": __version__,
    }
    files = [("README.md", _render_archive_readme(ledgers, filenames))]
    files.extend(body_files)
    files.append(("manifest.json", to_json(manifest)))
    summary = _archive_summary(ledgers, files, filenames)
    files.append(("archive-summary.json", to_json(summary)))
    return files


def _archive_summary(
    ledgers: Sequence[dict],
    hashed_files: Sequence[tuple[str, str]],
    generated_files: Sequence[str],
) -> dict:
    file_hashes = {
        filename: hashlib.sha256(text.encode("utf-8")).hexdigest()
        for filename, text in sorted(hashed_files, key=lambda item: item[0])
    }
    return {
        "archive": {
            "file_count": len(generated_files),
            "hashed_file_count": len(file_hashes),
            "ledger_count": len(ledgers),
        },
        "file_hashes": file_hashes,
        "generated_files": list(generated_files),
        "ledger_ids": [str(ledger["thesis_id"]) for ledger in ledgers],
        "tool_version": __version__,
    }


_ARCHIVE_DEPENDENCY_FILENAMES = {
    "Pipfile",
    "Pipfile.lock",
    "poetry.lock",
    "pyproject.toml",
    "requirements.txt",
    "uv.lock",
}


def _verify_archive_dir(archive_dir: Path) -> tuple[list[str], dict]:
    if not archive_dir.is_dir():
        raise OSError(f"not a directory: {archive_dir}")

    manifest = _read_archive_json(archive_dir / "manifest.json", "manifest.json")
    summary = _read_archive_json(archive_dir / "archive-summary.json", "archive-summary.json")
    manifest_files = _require_string_list(manifest, "generated_files", "manifest.json")
    summary_files = _require_string_list(summary, "generated_files", "archive-summary.json")
    manifest_ledger_ids = _require_string_list(manifest, "ledger_ids", "manifest.json")
    summary_ledger_ids = _require_string_list(summary, "ledger_ids", "archive-summary.json")
    file_hashes = _require_string_mapping(summary, "file_hashes", "archive-summary.json")

    errors: list[str] = []
    generated_files = _stable_unique(manifest_files + summary_files)
    hash_files = sorted(file_hashes)

    if manifest.get("archive_format") != "portable-research-archive":
        errors.append("manifest archive_format is not portable-research-archive")
    for source_name, filenames in (("manifest.json", manifest_files), ("archive-summary.json", summary_files)):
        duplicate_files = _duplicate_values(filenames)
        if duplicate_files:
            errors.append(f"{source_name} generated_files contains duplicate entries: {', '.join(duplicate_files)}")
    if manifest_files != summary_files:
        errors.append("manifest generated_files do not match archive-summary generated_files")
    if manifest_ledger_ids != summary_ledger_ids:
        errors.append("manifest ledger_ids do not match archive-summary ledger_ids")
    if manifest.get("tool_version") != summary.get("tool_version"):
        errors.append("manifest tool_version does not match archive-summary tool_version")
    if "archive-summary.json" not in manifest_files or "archive-summary.json" not in summary_files:
        errors.append("archive-summary.json is missing from generated_files")
    if "archive-summary.json" in file_hashes:
        errors.append("archive-summary.json must be excluded from file_hashes")

    expected_hash_files = sorted(set(filename for filename in manifest_files if filename != "archive-summary.json"))
    if hash_files != expected_hash_files:
        missing_hashes = sorted(set(expected_hash_files) - set(hash_files))
        extra_hashes = sorted(set(hash_files) - set(expected_hash_files))
        if missing_hashes:
            errors.append("missing file_hashes entries: " + ", ".join(missing_hashes))
        if extra_hashes:
            errors.append("unexpected file_hashes entries: " + ", ".join(extra_hashes))

    for source_name, filenames in (("manifest.json", manifest_files), ("archive-summary.json", summary_files)):
        for filename in filenames:
            if not _is_archive_local_filename(filename):
                errors.append(f"{source_name} generated_files contains external path: {filename}")
    for filename in file_hashes:
        if not _is_archive_local_filename(filename):
            errors.append(f"archive-summary.json file_hashes contains external path: {filename}")

    for filename in generated_files:
        if not _is_archive_local_filename(filename):
            continue
        path = archive_dir / filename
        if path.is_symlink():
            errors.append(f"generated file is a symlink: {filename}")
        elif not path.is_file():
            errors.append(f"missing generated file: {filename}")
    for filename in sorted(file_hashes):
        if not _is_archive_local_filename(filename):
            continue
        path = archive_dir / filename
        if path.is_symlink() and filename not in generated_files:
            errors.append(f"hash-listed file is a symlink: {filename}")

    for filename, expected_digest in sorted(file_hashes.items()):
        if not _is_archive_local_filename(filename):
            continue
        path = archive_dir / filename
        if path.is_symlink() or not path.is_file():
            continue
        actual_digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual_digest != expected_digest:
            errors.append(f"sha256 mismatch: {filename}")

    present_forbidden = _archive_forbidden_files(archive_dir)
    if present_forbidden:
        errors.append("workflow/dependency files present: " + ", ".join(present_forbidden))

    archive_counts = summary.get("archive")
    if isinstance(archive_counts, dict):
        if archive_counts.get("file_count") != len(summary_files):
            errors.append("archive file_count does not match generated_files")
        if archive_counts.get("hashed_file_count") != len(file_hashes):
            errors.append("archive hashed_file_count does not match file_hashes")
        if archive_counts.get("ledger_count") != len(summary_ledger_ids):
            errors.append("archive ledger_count does not match ledger_ids")
    else:
        errors.append("archive ledger_count does not match ledger_ids")

    validation = {
        "archive_dir": str(archive_dir),
        "archive_summary": summary,
        "file_count": len(generated_files),
        "generated_files": list(summary_files),
        "hashed_file_count": len(file_hashes),
        "ledger_count": len(summary_ledger_ids),
        "ledger_ids": list(summary_ledger_ids),
        "manifest": manifest,
        "tool_version": str(summary.get("tool_version", "")),
    }
    return errors, validation


def _read_archive_json(path: Path, label: str) -> dict:
    if path.is_symlink():
        raise OSError(f"{label} is a symlink")
    text = path.read_text(encoding="utf-8")
    try:
        payload = json.loads(text)
    except ValueError as exc:
        raise ValueError(f"invalid JSON in {label}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"{label} must contain a JSON object")
    return payload


def _require_string_list(payload: Mapping[str, object], key: str, label: str) -> list[str]:
    value = payload.get(key)
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ValueError(f"{label} {key} must be a list of strings")
    return list(value)


def _require_string_mapping(payload: Mapping[str, object], key: str, label: str) -> dict[str, str]:
    value = payload.get(key)
    if not isinstance(value, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in value.items()):
        raise ValueError(f"{label} {key} must be an object mapping strings to strings")
    return dict(value)


def _is_archive_local_filename(filename: str) -> bool:
    path = Path(filename)
    return bool(filename) and not path.is_absolute() and path.name == filename and "://" not in filename


def _archive_forbidden_files(archive_dir: Path) -> list[str]:
    forbidden: set[str] = set()
    for path in archive_dir.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(archive_dir).as_posix()
        if relative.startswith(".github/workflows/"):
            forbidden.add(relative)
        if path.name in _ARCHIVE_DEPENDENCY_FILENAMES:
            forbidden.add(relative)
        if path.name.startswith("requirements") and path.suffix == ".txt":
            forbidden.add(relative)
    return sorted(forbidden)


def _stable_unique(items: Sequence[str]) -> list[str]:
    seen: set[str] = set()
    unique: list[str] = []
    for item in items:
        if item not in seen:
            unique.append(item)
            seen.add(item)
    return unique


def _duplicate_values(items: Sequence[str]) -> list[str]:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for item in items:
        if item in seen:
            duplicates.add(item)
        else:
            seen.add(item)
    return sorted(duplicates)


def _summary_ledger_count(summary: Mapping[str, object]) -> int:
    archive = summary.get("archive")
    if isinstance(archive, dict) and isinstance(archive.get("ledger_count"), int):
        return archive["ledger_count"]
    ledger_ids = summary.get("ledger_ids")
    if isinstance(ledger_ids, list):
        return len(ledger_ids)
    return 0


def _archive_validation_summary(summary: Mapping[str, object], errors: Sequence[str]) -> str:
    lines = [
        "archive validation summary",
        f"archive: {summary['archive_dir']}",
        f"ledgers: {summary['ledger_count']}",
        f"generated_files: {summary['file_count']}",
        f"hashed_files: {summary['hashed_file_count']}",
        f"status: {'invalid' if errors else 'valid'}",
    ]
    if errors:
        lines.append("errors:")
        lines.extend(f"- {error}" for error in sorted(errors))
    return "\n".join(lines) + "\n"


def _archive_diff_payload(old_summary: Mapping[str, object], new_summary: Mapping[str, object]) -> dict:
    old_archive_summary = _archive_validation_object(old_summary, "archive_summary")
    new_archive_summary = _archive_validation_object(new_summary, "archive_summary")

    old_files = _archive_validation_string_list(old_summary, "generated_files")
    new_files = _archive_validation_string_list(new_summary, "generated_files")
    old_hashes = _require_string_mapping(old_archive_summary, "file_hashes", "old archive-summary.json")
    new_hashes = _require_string_mapping(new_archive_summary, "file_hashes", "new archive-summary.json")

    old_file_set = set(old_files)
    new_file_set = set(new_files)
    added_files = sorted(new_file_set - old_file_set)
    removed_files = sorted(old_file_set - new_file_set)
    common_files = sorted(old_file_set & new_file_set)
    changed_files = [
        filename
        for filename in common_files
        if filename in old_hashes and filename in new_hashes and old_hashes[filename] != new_hashes[filename]
    ]
    unchanged_count = sum(
        1
        for filename in common_files
        if filename not in old_hashes and filename not in new_hashes
        or filename in old_hashes
        and filename in new_hashes
        and old_hashes[filename] == new_hashes[filename]
    )

    old_ledger_ids = _archive_validation_string_list(old_summary, "ledger_ids")
    new_ledger_ids = _archive_validation_string_list(new_summary, "ledger_ids")
    old_tool_version = str(old_summary.get("tool_version", ""))
    new_tool_version = str(new_summary.get("tool_version", ""))
    old_file_count = int(old_summary["file_count"])
    new_file_count = int(new_summary["file_count"])
    changed = bool(
        added_files
        or removed_files
        or changed_files
        or old_ledger_ids != new_ledger_ids
        or old_tool_version != new_tool_version
        or old_file_count != new_file_count
    )

    return {
        "added_files": added_files,
        "changed_files": changed_files,
        "new_file_count": new_file_count,
        "new_ledger_ids": new_ledger_ids,
        "new_tool_version": new_tool_version,
        "old_file_count": old_file_count,
        "old_ledger_ids": old_ledger_ids,
        "old_tool_version": old_tool_version,
        "removed_files": removed_files,
        "status": "changed" if changed else "unchanged",
        "unchanged_count": unchanged_count,
    }


def _archive_validation_object(summary: Mapping[str, object], key: str) -> Mapping[str, object]:
    value = summary.get(key)
    if not isinstance(value, dict):
        raise ValueError(f"archive validation missing {key}")
    return value


def _archive_validation_string_list(summary: Mapping[str, object], key: str) -> list[str]:
    value = summary.get(key)
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ValueError(f"archive validation missing {key}")
    return list(value)


def _archive_file_count(summary: Mapping[str, object], generated_files: Sequence[str]) -> int:
    archive = summary.get("archive")
    if isinstance(archive, dict) and isinstance(archive.get("file_count"), int):
        return archive["file_count"]
    return len(generated_files)


def _render_archive_diff(payload: Mapping[str, object]) -> str:
    lines = [
        "# Archive Diff",
        "",
        f"- Status: {payload['status']}",
        f"- Old Tool Version: {payload['old_tool_version']}",
        f"- New Tool Version: {payload['new_tool_version']}",
        f"- Old File Count: {payload['old_file_count']}",
        f"- New File Count: {payload['new_file_count']}",
        f"- Unchanged Files: {payload['unchanged_count']}",
        "",
        "## Ledger IDs",
        "",
        f"- Old: {_archive_diff_list(payload['old_ledger_ids'])}",
        f"- New: {_archive_diff_list(payload['new_ledger_ids'])}",
        "",
        "## Added Files",
        "",
    ]
    lines.extend(_archive_diff_bullets(payload["added_files"]))
    lines.extend(["", "## Removed Files", ""])
    lines.extend(_archive_diff_bullets(payload["removed_files"]))
    lines.extend(["", "## Changed Files", ""])
    lines.extend(_archive_diff_bullets(payload["changed_files"]))
    return "\n".join(lines) + "\n"


def _archive_diff_list(value: object) -> str:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return "none"
    items = [str(item) for item in value]
    return ", ".join(items) if items else "none"


def _archive_diff_bullets(value: object) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)) or not value:
        return ["- none"]
    return [f"- {item}" for item in value]


def _render_archive_readme(ledgers: Sequence[dict], generated_files: Sequence[str]) -> str:
    lines = [
        "# Invest Thesis Ledger Portable Archive",
        "",
        "> This is a research organization tool, not investment advice.",
        "",
        f"- Tool Version: {__version__}",
        f"- Ledgers: {len(ledgers)}",
        "",
        "## Input Ledgers",
        "",
        "| Ticker | Title | Ledger ID | Updated |",
        "| --- | --- | --- | --- |",
    ]
    for ledger in ledgers:
        asset = ledger["asset"]
        lines.append(
            "| "
            + " | ".join(
                [
                    _bundle_cell(str(asset["ticker"])),
                    _bundle_cell(str(ledger["title"])),
                    _bundle_cell(str(ledger["thesis_id"])),
                    _bundle_cell(str(ledger["updated"])),
                ]
            )
            + " |"
        )
    lines.extend(["", "## Archive Files", ""])
    for filename in generated_files:
        lines.append(f"- [{_bundle_link_label(filename)}]({filename})")
    return "\n".join(lines) + "\n"


def _render_demo_bundle_index(ledgers: Sequence[dict], generated_files: Sequence[str]) -> str:
    lines = [
        "# Invest Thesis Ledger Demo Bundle",
        "",
        "> This is a research organization tool, not investment advice.",
        "",
        f"- Tool Version: {__version__}",
        f"- Ledgers: {len(ledgers)}",
        "",
        "## Input Ledgers",
        "",
        "| Ticker | Title | Ledger ID | Updated |",
        "| --- | --- | --- | --- |",
    ]
    for ledger in ledgers:
        asset = ledger["asset"]
        lines.append(
            "| "
            + " | ".join(
                [
                    _bundle_cell(str(asset["ticker"])),
                    _bundle_cell(str(ledger["title"])),
                    _bundle_cell(str(ledger["thesis_id"])),
                    _bundle_cell(str(ledger["updated"])),
                ]
            )
            + " |"
        )
    lines.extend(["", "## Bundle Files", ""])
    for filename in generated_files:
        lines.append(f"- [{_bundle_link_label(filename)}]({filename})")
    return "\n".join(lines) + "\n"


def _html_dashboard_files(ledgers: Sequence[dict]) -> list[tuple[str, str]]:
    ledger_prefixes = _bundle_prefixes(
        ledgers,
        reserved_filenames=[
            "index.html",
            "style.css",
            "portfolio.html",
            "evidence-audit.html",
            "watchlist.html",
            "action-plan.html",
            "manifest.json",
        ],
        primary_extension=".html",
    )
    ledger_pages = [
        (f"{ledger_id}.html", _render_html_ledger_page(ledger, ledger_id))
        for ledger, ledger_id in zip(ledgers, ledger_prefixes)
    ]
    body_files: list[tuple[str, str]] = []
    body_files.extend(ledger_pages)
    body_files.extend(
        [
            ("portfolio.html", _render_html_portfolio_page(ledgers)),
            ("evidence-audit.html", _render_html_evidence_audit_page(ledgers)),
            ("watchlist.html", _render_html_watchlist_page(ledgers)),
            ("action-plan.html", _render_html_action_plan_page(ledgers)),
        ]
    )
    filenames = ["index.html", "style.css"] + [filename for filename, _ in body_files] + ["manifest.json"]
    manifest = {
        "generated_files": filenames,
        "ledger_ids": [str(ledger["thesis_id"]) for ledger in ledgers],
        "tool_version": __version__,
    }
    files = [
        ("index.html", _render_html_dashboard_index(ledgers, ledger_pages, filenames)),
        ("style.css", _html_dashboard_css()),
    ]
    files.extend(body_files)
    files.append(("manifest.json", to_json(manifest)))
    return files


def _render_html_dashboard_index(
    ledgers: Sequence[dict],
    ledger_pages: Sequence[tuple[str, str]],
    generated_files: Sequence[str],
) -> str:
    rows = []
    for ledger, (filename, _page) in zip(ledgers, ledger_pages):
        asset = ledger["asset"]
        rows.append(
            "<tr>"
            f"<td><a href=\"{_ha(filename)}\">{_h(asset['ticker'])}</a></td>"
            f"<td>{_h(ledger['title'])}</td>"
            f"<td>{_h(ledger['thesis_id'])}</td>"
            f"<td>{_h(ledger['updated'])}</td>"
            "</tr>"
        )
    links = "".join(f"<li><a href=\"{_ha(filename)}\">{_h(filename)}</a></li>" for filename in generated_files)
    content = [
        "<section class=\"summary\">",
        "<p class=\"notice\">Research organization only. Not investment advice.</p>",
        f"<p>Tool version {_h(__version__)}. Ledgers: {len(ledgers)}.</p>",
        "</section>",
        "<section>",
        "<h2>Input Ledgers</h2>",
        "<table><thead><tr><th scope=\"col\">Ticker</th><th scope=\"col\">Title</th><th scope=\"col\">Ledger ID</th><th scope=\"col\">Updated</th></tr></thead>",
        "<tbody>",
        "".join(rows),
        "</tbody></table>",
        "</section>",
        "<section>",
        "<h2>Dashboard Files</h2>",
        f"<ul>{links}</ul>",
        "</section>",
    ]
    return _html_page("Invest Thesis Ledger Dashboard", "Dashboard", "\n".join(content))


def _render_html_ledger_page(ledger: dict, ledger_id: str) -> str:
    risk = risk_payload(ledger)
    history = history_payload(ledger)
    decision = decision_memo_payload(ledger)
    scenario = scenario_plan_payload(ledger)
    asset = ledger["asset"]
    content = [
        "<nav><a href=\"index.html\">Index</a> <a href=\"portfolio.html\">Portfolio</a> <a href=\"evidence-audit.html\">Evidence Audit</a> <a href=\"watchlist.html\">Watchlist</a> <a href=\"action-plan.html\">Action Plan</a></nav>",
        "<section class=\"summary\">",
        f"<p class=\"eyebrow\">{_h(asset['ticker'])} / {_h(asset['type'])}</p>",
        f"<p>{_h(asset['name'])}</p>",
        f"<p>Ledger ID: {_h(ledger['thesis_id'])}. Updated: {_h(ledger['updated'])}.</p>",
        "</section>",
        "<section>",
        "<h2>Brief</h2>",
        f"<p>{_h(ledger['thesis'])}</p>",
        "<h3>Assumptions</h3>",
        _html_list(
            [
                f"{item['id']}: {item['statement']} (confidence: {item['confidence']}; sources: {_source_ids(item['source_ids'])})"
                for item in ledger.get("assumptions", [])
                if isinstance(item, dict)
            ],
            "No assumptions recorded.",
        ),
        "<h3>Catalysts</h3>",
        _html_list(
            [
                f"{item['id']}: {item['title']}{_catalyst_label(item)} (status: {item['status']}; sources: {_source_ids(item['source_ids'])})"
                for item in calendar_payload(ledger)["catalysts"]
            ],
            "No catalysts recorded.",
        ),
        "<h3>Positions</h3>",
        _html_list([str(item) for item in ledger.get("positions", [])], "No position notes recorded."),
        "</section>",
        "<section>",
        "<h2>Risk</h2>",
        _html_table(
            ["ID", "Name", "Severity", "Probability", "Mitigation", "Sources"],
            [
                [
                    item["id"],
                    item["name"],
                    item["severity"],
                    item["probability"],
                    item["mitigation"],
                    _source_ids(item["source_ids"]),
                ]
                for item in risk["risks"]
            ],
        ),
        "<h3>Checklist</h3>",
        _html_list(
            [f"{item['id']}: {item['item']} ({item['status']})" for item in risk["checklist"]],
            "No checklist items recorded.",
        ),
        "</section>",
        "<section>",
        "<h2>History</h2>",
        _html_table(
            ["Date", "Decision", "Summary", "Drift", "Sources"],
            [
                [
                    item["date"],
                    item["decision"],
                    item["summary"],
                    item["drift"],
                    _source_ids(item["source_ids"]),
                ]
                for item in history["reviews"]
            ],
        ),
        "</section>",
        "<section>",
        "<h2>Decision</h2>",
        _html_definition_list(
            [
                ("Latest review", _review_label(decision["latest_review"])),
                ("High risks", str(len(decision["high_risks"]))),
                ("Open position rules", str(len(decision["exposure"]["open_position_rules"]))),
                ("Open checklist items", str(len(decision["exposure"]["open_checklist"]))),
                ("Stale sources", str(decision["evidence_summary"]["coverage"]["stale_source_count"])),
            ]
        ),
        "<h3>Questions Before Action</h3>",
        _html_list(
            [f"{item['id']}: {item['question']}" for item in decision["questions_before_action"]],
            "No questions recorded.",
        ),
        "</section>",
        "<section>",
        "<h2>Scenario</h2>",
        _html_definition_list(
            [
                ("Cases", str(scenario["scenario_plan"]["case_count"])),
                ("Open triggers", str(scenario["scenario_plan"]["trigger_count"])),
                ("Position constraints", str(scenario["scenario_plan"]["position_constraint_count"])),
                ("Risk mitigation actions", str(scenario["scenario_plan"]["risk_mitigation_count"])),
                ("Evidence gaps", str(scenario["scenario_plan"]["evidence_gap_count"])),
            ]
        ),
        _html_table(
            ["Case", "Summary", "Assumptions", "Risks", "Triggers", "Evidence Gaps"],
            [
                [
                    item["name"],
                    item["summary"],
                    str(len(item["assumptions"])),
                    str(len(item["risks"])),
                    str(len(item["triggers"])),
                    str(len(item["evidence_gaps"])),
                ]
                for item in scenario["cases"]
            ],
        ),
        "</section>",
        "<section>",
        "<h2>Sources</h2>",
        _html_table(
            ["ID", "Title", "Publisher", "Date", "URL"],
            [
                [source["id"], source["title"], source["publisher"], source["date"], source["url"]]
                for source in sorted(ledger.get("sources", []), key=lambda item: str(item.get("id", "")))
                if isinstance(source, dict)
            ],
        ),
        "</section>",
    ]
    return _html_page(str(ledger["title"]), str(ledger["title"]), "\n".join(content))


def _render_html_portfolio_page(ledgers: Sequence[dict]) -> str:
    payload = portfolio_payload(ledgers)
    content = [
        "<nav><a href=\"index.html\">Index</a> <a href=\"evidence-audit.html\">Evidence Audit</a> <a href=\"watchlist.html\">Watchlist</a> <a href=\"action-plan.html\">Action Plan</a></nav>",
        "<section class=\"summary\">",
        f"<p>Assets: {payload['portfolio']['asset_count']}. Thesis count: {payload['portfolio']['thesis_count']}.</p>",
        "</section>",
        "<section>",
        "<h2>Assets</h2>",
        _html_table(
            ["Ticker", "Name", "Type", "Ledger ID", "Updated"],
            [
                [item["ticker"], item["name"], item["type"], item["thesis_id"], item["updated"]]
                for item in payload["assets"]
            ],
        ),
        "</section>",
        "<section>",
        "<h2>Risk Summary</h2>",
        _html_counts("Severity", payload["risk_severity_counts"])
        + _html_counts("Tag", payload["risk_tag_counts"]),
        "</section>",
        "<section>",
        "<h2>Catalyst Summary</h2>",
        _html_counts("Status", payload["catalyst_status_counts"])
        + _html_counts("Window", payload["catalyst_window_counts"]),
        _html_table(
            ["Date", "Window", "Status", "Ticker", "ID", "Title"],
            [
                [
                    item["date"] or "not specified",
                    item["window"] or "not specified",
                    item["status"],
                    item["ticker"],
                    item["id"],
                    item["title"],
                ]
                for item in payload["catalysts"]
            ],
        ),
        "</section>",
        "<section>",
        "<h2>Review Decisions</h2>",
        _html_counts("Decision", payload["review_decision_counts"]),
        "</section>",
        "<section>",
        "<h2>Stale Sources</h2>",
        _html_list(
            [
                f"{item['ledger_id']} {item['id']}: {item['title']} ({item['date']}), {item['age_days']} days old"
                for item in payload["stale_source_warnings"]
            ],
            "No stale sources detected.",
        ),
        "</section>",
    ]
    return _html_page("Portfolio Summary", "Portfolio Summary", "\n".join(content))


def _render_html_evidence_audit_page(ledgers: Sequence[dict]) -> str:
    payload = evidence_audit_payload(ledgers)
    audit = payload["audit"]
    content = [
        "<nav><a href=\"index.html\">Index</a> <a href=\"portfolio.html\">Portfolio</a> <a href=\"watchlist.html\">Watchlist</a> <a href=\"action-plan.html\">Action Plan</a></nav>",
        "<section class=\"summary\">",
        f"<p>Ledgers: {audit['ledger_count']}. Tracked items: {audit['tracked_items']}. "
        f"Unsupported items: {audit['unsupported_items']}. Unused sources: {audit['unused_source_count']}. "
        f"Stale sources: {audit['stale_source_count']}.</p>",
        "</section>",
        "<section>",
        "<h2>Ledger Scores</h2>",
        _html_table(
            ["Rank", "Score", "Ticker", "Ledger ID", "Updated", "Tracked", "Unsupported", "Unused Sources", "Stale Sources"],
            [
                [
                    str(item["rank"]),
                    str(item["quality_score"]),
                    item["ticker"],
                    item["thesis_id"],
                    item["updated"],
                    str(item["coverage"]["tracked_items"]),
                    str(item["coverage"]["unsupported_items"]),
                    str(item["coverage"]["unused_source_count"]),
                    str(item["coverage"]["stale_source_count"]),
                ]
                for item in payload["ledgers"]
            ],
        ),
        "</section>",
        "<section>",
        "<h2>Field Coverage</h2>",
        _html_table(
            ["Field", "Tracked", "Supported", "Unsupported"],
            [
                [field, str(coverage["tracked_items"]), str(coverage["supported_items"]), str(coverage["unsupported_items"])]
                for field, coverage in payload["field_coverage"].items()
            ],
        ),
        "</section>",
        "<section>",
        "<h2>Unsupported Items</h2>",
        _html_table(
            ["Ledger ID", "Ticker", "Type", "ID"],
            [
                [item["ledger_id"], item["ticker"], item["type"], item["id"]]
                for item in payload["unsupported_items"]
            ],
        ),
        "</section>",
        "<section>",
        "<h2>Unused Sources</h2>",
        _html_table(
            ["Ledger ID", "Ticker", "Source", "Title", "URL"],
            [
                [item["ledger_id"], item["ticker"], item["id"], item["title"], item["url"]]
                for item in payload["unused_sources"]
            ],
        ),
        "</section>",
        "<section>",
        "<h2>Stale Sources</h2>",
        _html_table(
            ["Ledger ID", "Ticker", "Source", "Title", "Date", "Age Days", "URL"],
            [
                [item["ledger_id"], item["ticker"], item["id"], item["title"], item["date"], str(item["age_days"]), item["url"]]
                for item in payload["stale_sources"]
            ],
        ),
        "</section>",
        "<section>",
        "<h2>Duplicate Source URLs</h2>",
        _html_table(
            ["URL", "Ledgers", "Occurrences"],
            [
                [
                    item["url"],
                    str(item["ledger_count"]),
                    ", ".join(f"{occurrence['ledger_id']}[{occurrence['source_id']}]" for occurrence in item["occurrences"]),
                ]
                for item in payload["duplicate_source_urls"]
            ],
        ),
        "</section>",
    ]
    return _html_page("Portfolio Evidence Audit", "Portfolio Evidence Audit", "\n".join(content))


def _render_html_watchlist_page(ledgers: Sequence[dict]) -> str:
    payload = watchlist_payload(ledgers)
    content = [
        "<nav><a href=\"index.html\">Index</a> <a href=\"portfolio.html\">Portfolio</a> <a href=\"evidence-audit.html\">Evidence Audit</a> <a href=\"action-plan.html\">Action Plan</a></nav>",
        "<section class=\"summary\">",
        f"<p>Ledgers: {payload['watchlist']['ledger_count']}. High priority: {payload['watchlist']['high_priority_count']}. "
        f"Medium priority: {payload['watchlist']['medium_priority_count']}. Low priority: {payload['watchlist']['low_priority_count']}.</p>",
        "</section>",
        "<section>",
        "<h2>Weekly Review List</h2>",
        _html_table(
            [
                "Rank",
                "Score",
                "Ticker",
                "Title",
                "Priority",
                "Next Action",
                "Nearest Open Catalyst",
                "Latest Review",
                "Stale Sources",
                "High Risks",
                "Open Position Rules",
            ],
            [
                [
                    str(item["rank"]),
                    str(item["review_queue_score"]),
                    item["ticker"],
                    item["title"],
                    item["priority"],
                    item["next_action"],
                    _html_watchlist_catalyst_label(item["nearest_open_catalyst"]),
                    _html_watchlist_review_label(item["latest_review"]),
                    str(item["stale_source_count"]),
                    str(item["high_risk_count"]),
                    str(item["open_position_rule_count"]),
                ]
                for item in payload["items"]
            ],
        ),
        "</section>",
    ]
    return _html_page("Watchlist", "Watchlist", "\n".join(content))


def _render_html_action_plan_page(ledgers: Sequence[dict]) -> str:
    payload = action_plan_payload(ledgers)
    summary = payload["action_plan"]
    content = [
        "<nav><a href=\"index.html\">Index</a> <a href=\"portfolio.html\">Portfolio</a> <a href=\"evidence-audit.html\">Evidence Audit</a> <a href=\"watchlist.html\">Watchlist</a></nav>",
        "<section class=\"summary\">",
        "<p class=\"notice\">Educational research organization only. Not investment advice. No market data included.</p>",
        f"<p>Ledgers: {summary['ledger_count']}. Ranked actions: {summary['action_count']}. "
        f"Now: {summary['now_count']}. This week: {summary['this_week_count']}. Watch: {summary['watch_count']}.</p>",
        "</section>",
        "<section>",
        "<h2>Ranked Actions</h2>",
        _html_table(
            ["Rank", "Cadence", "Owner", "Ticker", "Ledger ID", "Priority", "Score", "Action", "Reason Codes", "Source Warnings"],
            [
                [
                    str(item["rank"]),
                    item["cadence"],
                    item["owner"],
                    item["ticker"],
                    item["thesis_id"],
                    item["priority"],
                    str(item["score"]),
                    item["action"],
                    ", ".join(item["reason_codes"]) if item["reason_codes"] else "none",
                    ", ".join(warning["code"] for warning in item["source_quality_warnings"]) if item["source_quality_warnings"] else "none",
                ]
                for item in payload["actions"]
            ],
        ),
        "</section>",
        "<section>",
        "<h2>Blockers</h2>",
        _html_table(
            ["Rank", "Ticker", "Code", "Text"],
            [
                [str(item["rank"]), item["ticker"], blocker["code"], blocker["text"]]
                for item in payload["actions"]
                for blocker in item["blockers"]
            ],
        ),
        "</section>",
        "<section>",
        "<h2>Source-Quality Warnings</h2>",
        _html_table(
            ["Rank", "Ticker", "Code", "Text"],
            [
                [str(item["rank"]), item["ticker"], warning["code"], warning["text"]]
                for item in payload["actions"]
                for warning in item["source_quality_warnings"]
            ],
        ),
        "</section>",
        "<section>",
        "<h2>Next Checklist</h2>",
        _html_table(
            ["Rank", "Ticker", "ID", "Text", "Source"],
            [
                [str(item["rank"]), item["ticker"], checklist_item["id"], checklist_item["text"], checklist_item["source"]]
                for item in payload["actions"]
                for checklist_item in item["next_checklist"]
            ],
        ),
        "</section>",
    ]
    return _html_page("Weekly Action Plan", "Weekly Action Plan", "\n".join(content))


def _html_page(title: str, heading: str, body: str) -> str:
    return "\n".join(
        [
            "<!doctype html>",
            "<html lang=\"en\">",
            "<head>",
            "<meta charset=\"utf-8\">",
            "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">",
            f"<title>{_h(title)}</title>",
            "<link rel=\"stylesheet\" href=\"style.css\">",
            "</head>",
            "<body>",
            "<main>",
            f"<h1>{_h(heading)}</h1>",
            body,
            "</main>",
            "</body>",
            "</html>",
            "",
        ]
    )


def _html_dashboard_css() -> str:
    return "\n".join(
        [
            ":root { color-scheme: light; --ink: #172026; --muted: #5c6870; --line: #d7dde2; --soft: #f4f6f8; --accent: #0f6b57; }",
            "* { box-sizing: border-box; }",
            "body { margin: 0; background: #ffffff; color: var(--ink); font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; line-height: 1.5; }",
            "main { max-width: 1180px; margin: 0 auto; padding: 32px 20px 56px; }",
            "h1 { margin: 0 0 18px; font-size: 2rem; line-height: 1.15; letter-spacing: 0; }",
            "h2 { margin: 30px 0 12px; font-size: 1.25rem; letter-spacing: 0; }",
            "h3 { margin: 20px 0 8px; font-size: 1rem; letter-spacing: 0; }",
            "section { border-top: 1px solid var(--line); padding-top: 18px; margin-top: 18px; }",
            "section.summary { background: var(--soft); border: 1px solid var(--line); border-radius: 8px; padding: 16px; }",
            "nav { display: flex; gap: 14px; flex-wrap: wrap; margin-bottom: 18px; }",
            "a { color: var(--accent); }",
            ".notice, .eyebrow { color: var(--muted); font-weight: 600; }",
            "table { width: 100%; border-collapse: collapse; margin: 10px 0 18px; font-size: 0.92rem; }",
            "th, td { border: 1px solid var(--line); padding: 8px 10px; text-align: left; vertical-align: top; }",
            "th { background: var(--soft); font-weight: 700; }",
            "dl { display: grid; grid-template-columns: minmax(160px, 240px) 1fr; gap: 6px 16px; }",
            "dt { color: var(--muted); font-weight: 700; }",
            "dd { margin: 0; }",
            "ul { padding-left: 22px; }",
            "@media (max-width: 720px) { main { padding: 24px 14px 42px; } table { display: block; overflow-x: auto; } dl { grid-template-columns: 1fr; } }",
            "",
        ]
    )


def _html_table(headers: Sequence[str], rows: Sequence[Sequence[str]]) -> str:
    if not rows:
        return "<p>No records.</p>"
    header_html = "".join(f"<th scope=\"col\">{_h(header)}</th>" for header in headers)
    row_html = []
    for row in rows:
        row_html.append("<tr>" + "".join(f"<td>{_h(cell)}</td>" for cell in row) + "</tr>")
    return f"<table><thead><tr>{header_html}</tr></thead><tbody>{''.join(row_html)}</tbody></table>"


def _html_list(items: Sequence[str], empty_text: str) -> str:
    if not items:
        return f"<p>{_h(empty_text)}</p>"
    return "<ul>" + "".join(f"<li>{_h(item)}</li>" for item in items) + "</ul>"


def _html_definition_list(items: Sequence[tuple[str, str]]) -> str:
    return "<dl>" + "".join(f"<dt>{_h(term)}</dt><dd>{_h(value)}</dd>" for term, value in items) + "</dl>"


def _html_counts(label: str, counts: Mapping[str, int]) -> str:
    if not counts:
        return f"<p>No {html.escape(label.lower())} counts recorded.</p>"
    return _html_table([label, "Count"], [[key, str(value)] for key, value in counts.items()])


def _h(value: object) -> str:
    return html.escape(str(value), quote=True)


def _ha(value: object) -> str:
    return html.escape(str(value), quote=True)


def _source_ids(source_ids: Sequence[str]) -> str:
    return ", ".join(str(source_id) for source_id in source_ids) if source_ids else "none"


def _catalyst_label(item: Mapping[str, str]) -> str:
    if item.get("date"):
        return f" on {item['date']}"
    if item.get("window"):
        return f" during {item['window']}"
    return ""


def _review_label(item: Mapping[str, str]) -> str:
    if not item.get("date"):
        return "No review recorded."
    return f"{item.get('date', '')}: {item.get('decision', '')} - {item.get('summary', '')}"


def _html_watchlist_catalyst_label(item: object) -> str:
    if not isinstance(item, dict):
        return "none"
    timing = _catalyst_label(item)
    return f"{item.get('id', '')}: {item.get('title', '')}{timing}"


def _html_watchlist_review_label(item: object) -> str:
    if not isinstance(item, dict) or not item.get("date"):
        return "none"
    return f"{item.get('date', '')}: {item.get('decision', '')}"


def _bundle_slug(value: str) -> str:
    slug = "".join(char.lower() if char.isalnum() else "-" for char in value).strip("-")
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug or "ledger"


def _bundle_prefixes(
    ledgers: Sequence[dict],
    reserved_filenames: Sequence[str] = (),
    primary_extension: Optional[str] = None,
    artifact_suffixes: Sequence[str] = (),
) -> list[str]:
    used_prefixes: set[str] = set()
    used_filenames = set(reserved_filenames)
    prefixes = []
    for ledger in ledgers:
        base = _bundle_slug(str(ledger["thesis_id"]))
        candidate = base
        index = 2
        while (
            candidate in used_prefixes
            or _bundle_generated_names(candidate, primary_extension, artifact_suffixes) & used_filenames
        ):
            candidate = f"{base}-{index}"
            index += 1
        used_prefixes.add(candidate)
        used_filenames.update(_bundle_generated_names(candidate, primary_extension, artifact_suffixes))
        prefixes.append(candidate)
    return prefixes


def _bundle_generated_names(
    prefix: str,
    primary_extension: Optional[str],
    artifact_suffixes: Sequence[str],
) -> set[str]:
    names = {f"{prefix}-{suffix}.md" for suffix in artifact_suffixes}
    if primary_extension is not None:
        names.add(f"{prefix}{primary_extension}")
    return names


def _bundle_cell(value: str) -> str:
    return value.replace("\r", " ").replace("\n", " ").replace("|", "\\|")


def _bundle_link_label(value: str) -> str:
    return value.replace("[", "\\[").replace("]", "\\]")


def _starter_ledger(asset: str, name: str, asset_type: str) -> dict:
    ticker = asset.strip().upper()
    slug = "".join(char.lower() if char.isalnum() else "-" for char in ticker).strip("-") or "asset"
    clean_name = name.strip()
    clean_type = asset_type.strip()
    return {
        "ledger_version": __version__,
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
