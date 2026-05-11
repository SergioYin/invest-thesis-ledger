"""Command line interface for invest-thesis-ledger."""

from __future__ import annotations

import argparse
import html
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


def _cmd_evidence_audit(args: argparse.Namespace) -> int:
    ledgers, status = _load_validated_ledgers(args.ledgers, "evidence-audit")
    if ledgers is None:
        return status

    _write_text(args.output, render_evidence_audit(ledgers))
    _write_text(args.json_output, to_json(evidence_audit_payload(ledgers)))
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


def _cmd_watchlist(args: argparse.Namespace) -> int:
    ledgers, status = _load_validated_ledgers(args.ledgers, "watchlist")
    if ledgers is None:
        return status

    _write_text(args.output, render_watchlist(ledgers))
    _write_text(args.json_output, to_json(watchlist_payload(ledgers)))
    sys.stdout.write(f"wrote: {args.output}, {args.json_output}\n")
    return 0


def _cmd_action_plan(args: argparse.Namespace) -> int:
    ledgers, status = _load_validated_ledgers(args.ledgers, "action-plan")
    if ledgers is None:
        return status

    _write_text(args.output, render_action_plan(ledgers))
    _write_text(args.json_output, to_json(action_plan_payload(ledgers)))
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
    if output_dir.resolve() == Path.cwd().resolve():
        sys.stderr.write(f"error: refusing to replace current working directory: {output_dir}\n")
        return 2

    try:
        _write_demo_bundle_dir(output_dir, files)
    except OSError as exc:
        sys.stderr.write(f"error: cannot write demo bundle {output_dir}: {exc}\n")
        return 2
    except ValueError as exc:
        sys.stderr.write(f"error: cannot write demo bundle {output_dir}: {exc}\n")
        return 2
    sys.stdout.write(f"wrote: {output_dir}\n")
    return 0


def _cmd_html_dashboard(args: argparse.Namespace) -> int:
    ledgers, status = _load_validated_ledgers(args.ledgers, "html-dashboard")
    if ledgers is None:
        return status

    output_dir = Path(args.output_dir)
    files = _html_dashboard_files(ledgers)
    if output_dir.exists() and (not output_dir.is_dir() or output_dir.is_symlink()):
        sys.stderr.write(f"error: output dir is not a directory: {output_dir}\n")
        return 2
    if output_dir.resolve() == Path.cwd().resolve():
        sys.stderr.write(f"error: refusing to replace current working directory: {output_dir}\n")
        return 2

    try:
        _write_demo_bundle_dir(output_dir, files)
    except OSError as exc:
        sys.stderr.write(f"error: cannot write HTML dashboard {output_dir}: {exc}\n")
        return 2
    except ValueError as exc:
        sys.stderr.write(f"error: cannot write HTML dashboard {output_dir}: {exc}\n")
        return 2
    sys.stdout.write(f"wrote: {output_dir}\n")
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
            ("watchlist.md", render_watchlist(ledgers)),
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
    ledger_prefixes = _bundle_prefixes(ledgers)
    ledger_pages = [
        (f"{ledger_id}.html", _render_html_ledger_page(ledger, ledger_id))
        for ledger, ledger_id in zip(ledgers, ledger_prefixes)
    ]
    body_files: list[tuple[str, str]] = []
    body_files.extend(ledger_pages)
    body_files.extend(
        [
            ("portfolio.html", _render_html_portfolio_page(ledgers)),
            ("watchlist.html", _render_html_watchlist_page(ledgers)),
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
        "<nav><a href=\"index.html\">Index</a> <a href=\"portfolio.html\">Portfolio</a> <a href=\"watchlist.html\">Watchlist</a></nav>",
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
        "<nav><a href=\"index.html\">Index</a> <a href=\"watchlist.html\">Watchlist</a></nav>",
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


def _render_html_watchlist_page(ledgers: Sequence[dict]) -> str:
    payload = watchlist_payload(ledgers)
    content = [
        "<nav><a href=\"index.html\">Index</a> <a href=\"portfolio.html\">Portfolio</a></nav>",
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


def _bundle_prefixes(ledgers: Sequence[dict]) -> list[str]:
    used: set[str] = set()
    prefixes = []
    for ledger in ledgers:
        base = _bundle_slug(str(ledger["thesis_id"]))
        candidate = base
        index = 2
        while candidate in used:
            candidate = f"{base}-{index}"
            index += 1
        used.add(candidate)
        prefixes.append(candidate)
    return prefixes


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
        "ledger_version": "1.2.0",
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
