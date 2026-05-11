"""Deterministic Markdown and JSON renderers."""

from __future__ import annotations

import json
from datetime import date
from typing import Any, Dict, List, Mapping, Optional, Sequence

from .schema import source_lookup


def render_brief(ledger: Mapping[str, Any]) -> str:
    """Render a source-attributed investment thesis brief."""

    asset = ledger["asset"]
    lines = [
        f"# {ledger['title']}",
        "",
        "> This is a research organization tool, not investment advice.",
        "",
        "## Asset",
        "",
        f"- Name: {asset['name']}",
        f"- Type: {asset['type']}",
        f"- Ticker: {asset['ticker']}",
        f"- Ledger ID: {ledger['thesis_id']}",
        f"- Updated: {ledger['updated']}",
        "",
        "## Thesis",
        "",
        ledger["thesis"],
        "",
        "## Assumptions",
        "",
    ]
    for item in ledger["assumptions"]:
        lines.append(
            f"- {item['id']}: {item['statement']} "
            f"(confidence: {item['confidence']}; sources: {_refs(item['source_ids'])})"
        )
    lines.extend(["", "## Catalysts", ""])
    for item in calendar_payload(ledger)["catalysts"]:
        timing = _catalyst_timing(item)
        source_text = f"; sources: {_refs(item['source_ids'])}" if item["source_ids"] else ""
        lines.append(f"- {item['id']}: {item['title']}{timing}{source_text}")
    if not ledger.get("catalysts"):
        lines.append("- None recorded.")
    lines.extend(["", "## Current Position Notes", ""])
    for item in ledger.get("positions", []):
        lines.append(f"- {item}")
    if not ledger.get("positions"):
        lines.append("- None recorded.")
    lines.extend(["", "## Sources", ""])
    lines.extend(_source_lines(ledger))
    return "\n".join(lines) + "\n"


def risk_payload(ledger: Mapping[str, Any]) -> Dict[str, Any]:
    """Build deterministic structured risk output."""

    checklist = []
    for index, item in enumerate(ledger.get("checklist", []), start=1):
        if isinstance(item, dict):
            checklist.append(
                {
                    "id": item.get("id", f"C{index}"),
                    "item": item.get("item", ""),
                    "status": item.get("status", "open"),
                }
            )
        else:
            checklist.append({"id": f"C{index}", "item": str(item), "status": "open"})
    return {
        "thesis_id": ledger["thesis_id"],
        "title": ledger["title"],
        "updated": ledger["updated"],
        "risks": [
            {
                "id": item["id"],
                "name": item["name"],
                "severity": item["severity"],
                "probability": item["probability"],
                "mitigation": item["mitigation"],
                "tags": list(item.get("tags", [])) if isinstance(item.get("tags", []), list) else [],
                "source_ids": list(item["source_ids"]),
            }
            for item in ledger["risks"]
        ],
        "checklist": checklist,
    }


def render_risk(ledger: Mapping[str, Any]) -> str:
    """Render a Markdown risk and checklist report."""

    payload = risk_payload(ledger)
    lines = [
        f"# Risk Report: {payload['title']}",
        "",
        "> This is a research organization tool, not investment advice.",
        "",
        f"- Ledger ID: {payload['thesis_id']}",
        f"- Updated: {payload['updated']}",
        "",
        "## Risks",
        "",
    ]
    for item in payload["risks"]:
        lines.extend(
            [
                f"### {item['id']}: {item['name']}",
                "",
                f"- Severity: {item['severity']}",
                f"- Probability: {item['probability']}",
                f"- Tags: {', '.join(item['tags']) if item['tags'] else 'none'}",
                f"- Mitigation: {item['mitigation']}",
                f"- Sources: {_refs(item['source_ids'])}",
                "",
            ]
        )
    lines.extend(["## Checklist", ""])
    for item in payload["checklist"]:
        lines.append(f"- [{_checkbox(item['status'])}] {item['id']}: {item['item']} ({item['status']})")
    if not payload["checklist"]:
        lines.append("- No checklist items recorded.")
    lines.extend(["", "## Sources", ""])
    lines.extend(_source_lines(ledger))
    return "\n".join(lines) + "\n"


def history_payload(ledger: Mapping[str, Any]) -> Dict[str, Any]:
    """Build deterministic structured history output."""

    return {
        "thesis_id": ledger["thesis_id"],
        "title": ledger["title"],
        "created": ledger["created"],
        "updated": ledger["updated"],
        "reviews": [
            {
                "date": item["date"],
                "decision": item["decision"],
                "summary": item["summary"],
                "drift": item.get("drift", "none recorded"),
                "source_ids": list(item["source_ids"]),
            }
            for item in sorted(ledger["reviews"], key=lambda review: review["date"])
        ],
    }


def compare_payload(old: Mapping[str, Any], new: Mapping[str, Any]) -> Dict[str, Any]:
    """Build structured thesis drift output between two ledgers."""

    return {
        "thesis_id": {
            "old": old["thesis_id"],
            "new": new["thesis_id"],
            "changed": old["thesis_id"] != new["thesis_id"],
        },
        "title": {
            "old": old["title"],
            "new": new["title"],
            "changed": old["title"] != new["title"],
        },
        "updated": {"old": old["updated"], "new": new["updated"]},
        "thesis": {
            "changed": old["thesis"] != new["thesis"],
            "old": old["thesis"],
            "new": new["thesis"],
        },
        "assumptions": _compare_by_id(
            old.get("assumptions", []),
            new.get("assumptions", []),
            ("statement", "confidence", "source_ids"),
        ),
        "risks": _compare_by_id(
            old.get("risks", []),
            new.get("risks", []),
            ("name", "severity", "probability", "mitigation", "source_ids"),
        ),
        "reviews": _compare_by_id(
            _reviews_with_ids(old.get("reviews", [])),
            _reviews_with_ids(new.get("reviews", [])),
            ("date", "decision", "summary", "drift", "source_ids"),
        ),
    }


def render_compare(old: Mapping[str, Any], new: Mapping[str, Any]) -> str:
    """Render Markdown thesis drift output between two ledgers."""

    payload = compare_payload(old, new)
    lines = [
        f"# Thesis Drift: {payload['title']['old']} -> {payload['title']['new']}",
        "",
        "> This is a research organization tool, not investment advice.",
        "",
        f"- Ledger ID: {payload['thesis_id']['old']} -> {payload['thesis_id']['new']}",
        f"- Updated: {payload['updated']['old']} -> {payload['updated']['new']}",
        "",
        "## Thesis",
        "",
    ]
    if payload["thesis"]["changed"]:
        lines.extend(["- Status: changed", f"- Old: {payload['thesis']['old']}", f"- New: {payload['thesis']['new']}"])
    else:
        lines.append("- Status: unchanged")
    lines.extend(["", "## Assumptions", ""])
    _extend_compare_lines(lines, payload["assumptions"])
    lines.extend(["", "## Risks", ""])
    _extend_compare_lines(lines, payload["risks"])
    lines.extend(["", "## Reviews", ""])
    _extend_compare_lines(lines, payload["reviews"])
    return "\n".join(lines) + "\n"


def calendar_payload(ledger: Mapping[str, Any]) -> Dict[str, Any]:
    """Build structured catalyst calendar output."""

    catalysts = [_normalize_catalyst(item, index) for index, item in enumerate(ledger.get("catalysts", []), start=1)]
    catalysts.sort(key=lambda item: (item["date"] == "", item["date"], item["window"], item["id"]))
    return {
        "thesis_id": ledger["thesis_id"],
        "title": ledger["title"],
        "updated": ledger["updated"],
        "catalysts": catalysts,
    }


def render_calendar(ledger: Mapping[str, Any]) -> str:
    """Render a Markdown catalyst calendar."""

    payload = calendar_payload(ledger)
    lines = [
        f"# Catalyst Calendar: {payload['title']}",
        "",
        "> This is a research organization tool, not investment advice.",
        "",
        f"- Ledger ID: {payload['thesis_id']}",
        f"- Updated: {payload['updated']}",
        "",
        "## Catalysts",
        "",
    ]
    if not payload["catalysts"]:
        lines.append("- No catalysts recorded.")
    for item in payload["catalysts"]:
        lines.extend(
            [
                f"### {item['id']}: {item['title']}",
                "",
                f"- Date: {item['date'] or 'not specified'}",
                f"- Window: {item['window'] or 'not specified'}",
                f"- Status: {item['status']}",
                f"- Sources: {_refs(item['source_ids'])}",
                "",
            ]
        )
    lines.extend(["## Sources", ""])
    lines.extend(_source_lines(ledger))
    return "\n".join(lines) + "\n"


def broker_matrix_payload(ledger: Mapping[str, Any]) -> Dict[str, Any]:
    """Build structured broker/institution view output."""

    views = [_normalize_broker_view(item, index) for index, item in enumerate(ledger.get("broker_views", []), start=1)]
    views.sort(key=lambda item: (item["institution"].lower(), item["id"]))
    return {
        "thesis_id": ledger["thesis_id"],
        "title": ledger["title"],
        "updated": ledger["updated"],
        "asset": dict(ledger["asset"]),
        "broker_views": views,
        "rating_counts": _count_by(views, "rating"),
    }


def render_broker_matrix(ledger: Mapping[str, Any]) -> str:
    """Render a Markdown broker/institution rating and target matrix."""

    payload = broker_matrix_payload(ledger)
    lines = [
        f"# Broker Matrix: {payload['title']}",
        "",
        "> This is a research organization tool, not investment advice.",
        "",
        f"- Ledger ID: {payload['thesis_id']}",
        f"- Updated: {payload['updated']}",
        f"- Asset: {payload['asset']['ticker']} ({payload['asset']['name']})",
        "",
        "## Views",
        "",
        "| ID | Institution | Rating | Target | As Of | Thesis | Sources |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    if payload["broker_views"]:
        for item in payload["broker_views"]:
            lines.append(
                "| "
                + " | ".join(
                    [
                        _cell(item["id"]),
                        _cell(item["institution"]),
                        _cell(item["rating"]),
                        _cell(item["target"]),
                        _cell(item["as_of"]),
                        _cell(item["thesis"]),
                        _cell(_refs(item["source_ids"])),
                    ]
                )
                + " |"
            )
    else:
        lines.append("| none | none recorded | none | none | none | none | none |")
    lines.extend(["", "## Rating Counts", ""])
    if payload["rating_counts"]:
        for rating, count in payload["rating_counts"].items():
            lines.append(f"- {_inline(rating)}: {count}")
    else:
        lines.append("- No broker views recorded.")
    lines.extend(["", "## Sources", ""])
    lines.extend(_source_lines(ledger))
    return "\n".join(lines) + "\n"


def exposure_payload(ledger: Mapping[str, Any]) -> Dict[str, Any]:
    """Build structured exposure checklist output from risks and position rules."""

    risks = []
    tag_counts: Dict[str, int] = {}
    for risk in ledger.get("risks", []):
        tags = list(risk.get("tags", [])) if isinstance(risk.get("tags", []), list) else []
        for tag in tags:
            if isinstance(tag, str):
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        risks.append(
            {
                "id": risk["id"],
                "name": risk["name"],
                "severity": risk["severity"],
                "probability": risk["probability"],
                "tags": [tag for tag in tags if isinstance(tag, str)],
                "source_ids": list(risk["source_ids"]),
            }
        )
    rules = [_normalize_position_rule(item, index) for index, item in enumerate(ledger.get("position_rules", []), start=1)]
    rules.sort(key=lambda item: item["id"])
    checklist = []
    for item in risks:
        checklist.append(
            {
                "id": f"RISK-{item['id']}",
                "type": "risk",
                "item": item["name"],
                "status": "review",
                "tags": item["tags"],
                "source_ids": item["source_ids"],
            }
        )
    for item in rules:
        checklist.append(
            {
                "id": f"RULE-{item['id']}",
                "type": "position_rule",
                "item": item["rule"],
                "status": item["status"],
                "tags": item["tags"],
                "source_ids": item["source_ids"],
            }
        )
    checklist.sort(key=lambda item: (item["type"], item["id"]))
    return {
        "thesis_id": ledger["thesis_id"],
        "title": ledger["title"],
        "updated": ledger["updated"],
        "asset": dict(ledger["asset"]),
        "tag_counts": {key: tag_counts[key] for key in sorted(tag_counts)},
        "risks": sorted(risks, key=lambda item: item["id"]),
        "position_rules": rules,
        "checklist": checklist,
    }


def render_exposure(ledger: Mapping[str, Any]) -> str:
    """Render a Markdown exposure checklist."""

    payload = exposure_payload(ledger)
    lines = [
        f"# Exposure Checklist: {payload['title']}",
        "",
        "> This is a research organization tool, not investment advice.",
        "",
        f"- Ledger ID: {payload['thesis_id']}",
        f"- Updated: {payload['updated']}",
        f"- Asset: {payload['asset']['ticker']} ({payload['asset']['name']})",
        "",
        "## Risk Tags",
        "",
    ]
    if payload["tag_counts"]:
        for tag, count in payload["tag_counts"].items():
            lines.append(f"- {_inline(tag)}: {count}")
    else:
        lines.append("- No risk tags recorded.")
    lines.extend(["", "## Position Rules", ""])
    if payload["position_rules"]:
        for item in payload["position_rules"]:
            lines.append(
                f"- [{_checkbox(item['status'])}] {_inline(item['id'])}: {_inline(item['rule'])} "
                f"(status: {_inline(item['status'])}; exposure: {_inline(item['exposure']) if item['exposure'] else 'not specified'}; "
                f"tags: {_inline_join(item['tags'])}; sources: {_refs(item['source_ids'])})"
            )
    else:
        lines.append("- No position rules recorded.")
    lines.extend(["", "## Checklist", ""])
    if payload["checklist"]:
        for item in payload["checklist"]:
            lines.append(
                f"- [{_checkbox(item['status'])}] {_inline(item['id'])}: {_inline(item['item'])} "
                f"({_inline(item['type'])}; tags: {_inline_join(item['tags'])}; "
                f"sources: {_refs(item['source_ids'])})"
            )
    else:
        lines.append("- No exposure checklist items recorded.")
    lines.extend(["", "## Sources", ""])
    lines.extend(_source_lines(ledger))
    return "\n".join(lines) + "\n"


def portfolio_payload(ledgers: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
    """Build deterministic portfolio-level summary output."""

    assets = []
    risk_severity_counts: Dict[str, int] = {}
    risk_tag_counts: Dict[str, int] = {}
    catalyst_status_counts: Dict[str, int] = {}
    catalyst_window_counts: Dict[str, int] = {}
    catalysts = []
    broker_rating_counts: Dict[str, Dict[str, int]] = {}
    review_decision_counts: Dict[str, int] = {}
    stale_source_warnings = []

    for ledger in ledgers:
        ledger_id = str(ledger["thesis_id"])
        asset = ledger["asset"]
        ticker = str(asset["ticker"])
        assets.append(
            {
                "thesis_id": ledger_id,
                "title": ledger["title"],
                "ticker": ticker,
                "name": asset["name"],
                "type": asset["type"],
                "updated": ledger["updated"],
            }
        )

        for risk in ledger.get("risks", []):
            severity = str(risk.get("severity", "")) or "unspecified"
            risk_severity_counts[severity] = risk_severity_counts.get(severity, 0) + 1
            tags = risk.get("tags", [])
            if isinstance(tags, list):
                for tag in tags:
                    if isinstance(tag, str):
                        risk_tag_counts[tag] = risk_tag_counts.get(tag, 0) + 1

        for catalyst in calendar_payload(ledger)["catalysts"]:
            status = catalyst["status"] or "unspecified"
            window = catalyst["window"] or "unspecified"
            catalyst_status_counts[status] = catalyst_status_counts.get(status, 0) + 1
            catalyst_window_counts[window] = catalyst_window_counts.get(window, 0) + 1
            catalysts.append(
                {
                    "ledger_id": ledger_id,
                    "ticker": ticker,
                    "id": catalyst["id"],
                    "title": catalyst["title"],
                    "status": catalyst["status"],
                    "date": catalyst["date"],
                    "window": catalyst["window"],
                    "source_ids": catalyst["source_ids"],
                }
            )

        for view in broker_matrix_payload(ledger)["broker_views"]:
            institution = view["institution"] or "unspecified"
            rating = view["rating"] or "unspecified"
            if institution not in broker_rating_counts:
                broker_rating_counts[institution] = {}
            broker_rating_counts[institution][rating] = broker_rating_counts[institution].get(rating, 0) + 1

        for review in ledger.get("reviews", []):
            if isinstance(review, dict):
                decision = str(review.get("decision", "")) or "unspecified"
                review_decision_counts[decision] = review_decision_counts.get(decision, 0) + 1

        for source in evidence_payload(ledger)["stale_sources"]:
            warning = dict(source)
            warning["ledger_id"] = ledger_id
            warning["ticker"] = ticker
            stale_source_warnings.append(warning)

    assets.sort(
        key=lambda item: (
            item["ticker"],
            item["thesis_id"],
            item["name"],
            item["type"],
            item["updated"],
            item["title"],
        )
    )
    catalysts.sort(
        key=lambda item: (
            item["date"] == "",
            item["date"],
            item["window"],
            item["ticker"],
            item["ledger_id"],
            item["id"],
            item["title"],
        )
    )
    stale_source_warnings.sort(
        key=lambda item: (
            item["ledger_id"],
            item["ticker"],
            item["id"],
            item["date"],
            item["title"],
            item["age_days"],
        )
    )
    return {
        "portfolio": {
            "asset_count": len(assets),
            "thesis_count": len(ledgers),
        },
        "assets": assets,
        "risk_severity_counts": _sorted_counts(risk_severity_counts),
        "risk_tag_counts": _sorted_counts(risk_tag_counts),
        "catalyst_status_counts": _sorted_counts(catalyst_status_counts),
        "catalyst_window_counts": _sorted_counts(catalyst_window_counts),
        "catalysts": catalysts,
        "broker_rating_counts": {
            institution: _sorted_counts(ratings) for institution, ratings in sorted(broker_rating_counts.items())
        },
        "review_decision_counts": _sorted_counts(review_decision_counts),
        "stale_source_warnings": stale_source_warnings,
    }


def render_portfolio(ledgers: Sequence[Mapping[str, Any]]) -> str:
    """Render a Markdown portfolio-level summary."""

    payload = portfolio_payload(ledgers)
    lines = [
        "# Portfolio Summary",
        "",
        "> This is a research organization tool, not investment advice.",
        "",
        f"- Assets: {payload['portfolio']['asset_count']}",
        f"- Thesis Count: {payload['portfolio']['thesis_count']}",
        "",
        "## Assets",
        "",
        "| Ticker | Name | Type | Ledger ID | Updated |",
        "| --- | --- | --- | --- | --- |",
    ]
    for item in payload["assets"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    _cell(item["ticker"]),
                    _cell(item["name"]),
                    _cell(item["type"]),
                    _cell(item["thesis_id"]),
                    _cell(item["updated"]),
                ]
            )
            + " |"
        )
    lines.extend(["", "## Risk Severity Counts", ""])
    _extend_count_lines(lines, payload["risk_severity_counts"], "No risks recorded.")
    lines.extend(["", "## Risk Tag Counts", ""])
    _extend_count_lines(lines, payload["risk_tag_counts"], "No risk tags recorded.")
    lines.extend(["", "## Catalyst Status Counts", ""])
    _extend_count_lines(lines, payload["catalyst_status_counts"], "No catalysts recorded.")
    lines.extend(["", "## Catalyst Window Counts", ""])
    _extend_count_lines(lines, payload["catalyst_window_counts"], "No catalyst windows recorded.")
    lines.extend(["", "## Catalyst Dates", ""])
    if payload["catalysts"]:
        lines.extend(
            [
                "| Date | Window | Status | Ticker | ID | Title | Sources |",
                "| --- | --- | --- | --- | --- | --- | --- |",
            ]
        )
        for item in payload["catalysts"]:
            lines.append(
                "| "
                + " | ".join(
                    [
                        _cell(item["date"] or "not specified"),
                        _cell(item["window"] or "not specified"),
                        _cell(item["status"]),
                        _cell(item["ticker"]),
                        _cell(item["id"]),
                        _cell(item["title"]),
                        _cell(_refs(item["source_ids"])),
                    ]
                )
                + " |"
            )
    else:
        lines.append("- No catalysts recorded.")
    lines.extend(["", "## Broker Rating Counts", ""])
    if payload["broker_rating_counts"]:
        lines.extend(["| Institution | Rating | Count |", "| --- | --- | --- |"])
        for institution, ratings in payload["broker_rating_counts"].items():
            for rating, count in ratings.items():
                lines.append(f"| {_cell(institution)} | {_cell(rating)} | {count} |")
    else:
        lines.append("- No broker ratings recorded.")
    lines.extend(["", "## Review Decision Counts", ""])
    _extend_count_lines(lines, payload["review_decision_counts"], "No reviews recorded.")
    lines.extend(["", "## Stale Source Warnings", ""])
    if payload["stale_source_warnings"]:
        for item in payload["stale_source_warnings"]:
            lines.append(
                f"- {_inline(item['ledger_id'])} [{_inline(item['id'])}] {_inline(item['title'])} "
                f"({_inline(item['date'])}): "
                f"{item['age_days']} days old"
            )
    else:
        lines.append("- No stale sources detected.")
    return "\n".join(lines) + "\n"


def evidence_payload(ledger: Mapping[str, Any]) -> Dict[str, Any]:
    """Build structured source coverage and stale-source output."""

    sources = source_lookup(ledger)
    source_ids = set(sources)
    usage: Dict[str, List[str]] = {source_id: [] for source_id in source_ids}
    records = []
    records.extend(_evidence_records("assumption", ledger.get("assumptions", []), source_ids, usage))
    records.extend(_evidence_records("risk", ledger.get("risks", []), source_ids, usage))
    records.extend(_evidence_records("review", _reviews_with_ids(ledger.get("reviews", [])), source_ids, usage))
    records.extend(_evidence_records("catalyst", calendar_payload(ledger)["catalysts"], source_ids, usage))
    records.extend(_evidence_records("broker_view", broker_matrix_payload(ledger)["broker_views"], source_ids, usage))
    records.extend(_evidence_records("position_rule", exposure_payload(ledger)["position_rules"], source_ids, usage))
    stale_sources = _stale_sources(ledger)
    unsupported = [item for item in records if not item["source_ids"]]
    return {
        "thesis_id": ledger["thesis_id"],
        "title": ledger["title"],
        "updated": ledger["updated"],
        "coverage": {
            "tracked_items": len(records),
            "supported_items": len(records) - len(unsupported),
            "unsupported_items": len(unsupported),
            "source_count": len(sources),
            "unused_source_count": sum(1 for refs in usage.values() if not refs),
            "stale_source_count": len(stale_sources),
        },
        "items": sorted(records, key=lambda item: (item["type"], item["id"])),
        "unused_sources": sorted(source_id for source_id, refs in usage.items() if not refs),
        "stale_sources": stale_sources,
    }


def render_evidence(ledger: Mapping[str, Any]) -> str:
    """Render a Markdown evidence coverage report."""

    payload = evidence_payload(ledger)
    lines = [
        f"# Evidence Report: {payload['title']}",
        "",
        "> This is a research organization tool, not investment advice.",
        "",
        f"- Ledger ID: {payload['thesis_id']}",
        f"- Updated: {payload['updated']}",
        "",
        "## Coverage",
        "",
    ]
    for key, value in payload["coverage"].items():
        lines.append(f"- {key.replace('_', ' ').title()}: {value}")
    lines.extend(["", "## Items", ""])
    for item in payload["items"]:
        status = "supported" if item["source_ids"] else "unsupported"
        lines.append(f"- {item['type']} {item['id']}: {status}; sources: {_refs(item['source_ids'])}")
    lines.extend(["", "## Stale Sources", ""])
    if payload["stale_sources"]:
        for item in payload["stale_sources"]:
            lines.append(f"- [{item['id']}] {item['title']} ({item['date']}): {item['age_days']} days old")
    else:
        lines.append("- No stale sources detected.")
    lines.extend(["", "## Unused Sources", ""])
    if payload["unused_sources"]:
        for source_id in payload["unused_sources"]:
            lines.append(f"- [{source_id}]")
    else:
        lines.append("- No unused sources detected.")
    return "\n".join(lines) + "\n"


def render_history(ledger: Mapping[str, Any]) -> str:
    """Render a Markdown review timeline and thesis drift report."""

    payload = history_payload(ledger)
    lines = [
        f"# History: {payload['title']}",
        "",
        "> This is a research organization tool, not investment advice.",
        "",
        f"- Ledger ID: {payload['thesis_id']}",
        f"- Created: {payload['created']}",
        f"- Updated: {payload['updated']}",
        "",
        "## Timeline",
        "",
    ]
    for item in payload["reviews"]:
        lines.extend(
            [
                f"### {item['date']} - {item['decision']}",
                "",
                f"- Summary: {item['summary']}",
                f"- Drift: {item['drift']}",
                f"- Sources: {_refs(item['source_ids'])}",
                "",
            ]
        )
    lines.extend(["## Sources", ""])
    lines.extend(_source_lines(ledger))
    return "\n".join(lines) + "\n"


def to_json(data: Mapping[str, Any]) -> str:
    """Serialize JSON deterministically."""

    return json.dumps(data, indent=2, sort_keys=True) + "\n"


def _refs(source_ids: Sequence[str]) -> str:
    return ", ".join(f"[{_inline(source_id)}]" for source_id in source_ids) if source_ids else "none"


def _source_lines(ledger: Mapping[str, Any]) -> List[str]:
    sources = source_lookup(ledger)
    lines = []
    for source_id in sorted(sources):
        source = sources[source_id]
        lines.append(
            f"- [{_inline(source_id)}] {_inline(source['title'])}. {_inline(source['publisher'])}, "
            f"{_inline(source['date'])}. {_inline(source['url'])}"
        )
    return lines


def _checkbox(status: str) -> str:
    return "x" if status.lower() in {"done", "closed", "passed", "complete"} else " "


def _compare_by_id(
    old_items: Sequence[Mapping[str, Any]], new_items: Sequence[Mapping[str, Any]], fields: Sequence[str]
) -> Dict[str, Any]:
    old_by_id = {str(item["id"]): item for item in old_items if isinstance(item, dict) and "id" in item}
    new_by_id = {str(item["id"]): item for item in new_items if isinstance(item, dict) and "id" in item}
    added = []
    removed = []
    changed = []
    unchanged = []
    for item_id in sorted(new_by_id.keys() - old_by_id.keys()):
        added.append(_project(new_by_id[item_id], fields))
    for item_id in sorted(old_by_id.keys() - new_by_id.keys()):
        removed.append(_project(old_by_id[item_id], fields))
    for item_id in sorted(old_by_id.keys() & new_by_id.keys()):
        old_projected = _project(old_by_id[item_id], fields)
        new_projected = _project(new_by_id[item_id], fields)
        field_changes = [field for field in fields if old_projected.get(field) != new_projected.get(field)]
        if field_changes:
            changed.append({"id": item_id, "changes": field_changes, "old": old_projected, "new": new_projected})
        else:
            unchanged.append(item_id)
    return {"added": added, "removed": removed, "changed": changed, "unchanged": unchanged}


def _project(item: Mapping[str, Any], fields: Sequence[str]) -> Dict[str, Any]:
    projected = {"id": str(item["id"])}
    for field in fields:
        value = item.get(field, "" if field != "source_ids" else [])
        projected[field] = list(value) if isinstance(value, list) else value
    return projected


def _reviews_with_ids(reviews: Sequence[Any]) -> List[Dict[str, Any]]:
    items = []
    review_items = [review for review in reviews if isinstance(review, dict)]
    review_items.sort(
        key=lambda review: (
            str(review.get("date", "")),
            str(review.get("decision", "")),
            str(review.get("summary", "")),
        )
    )
    for index, review in enumerate(review_items, start=1):
        item = dict(review)
        item["id"] = item.get("id", f"REV{index}:{item.get('date', '')}")
        items.append(item)
    return items


def _extend_compare_lines(lines: List[str], section: Mapping[str, Any]) -> None:
    for label in ("added", "removed"):
        if section[label]:
            lines.append(f"### {label.title()}")
            lines.append("")
            for item in section[label]:
                lines.append(f"- {item['id']}: {_compare_label(item)}")
            lines.append("")
    if section["changed"]:
        lines.extend(["### Changed", ""])
        for item in section["changed"]:
            lines.append(f"- {item['id']}: {', '.join(item['changes'])}")
        lines.append("")
    if not section["added"] and not section["removed"] and not section["changed"]:
        lines.append("- No material changes.")


def _compare_label(item: Mapping[str, Any]) -> str:
    for field in ("statement", "name", "summary", "title"):
        if item.get(field):
            return str(item[field])
    return "record"


def _normalize_catalyst(item: Any, index: int) -> Dict[str, Any]:
    if isinstance(item, dict):
        source_ids = item.get("source_ids", [])
        return {
            "id": str(item.get("id", f"CAT{index}")),
            "title": str(item.get("title") or item.get("name") or item.get("summary") or item.get("description") or ""),
            "date": str(item.get("date", "")),
            "window": str(item.get("window", "")),
            "status": str(item.get("status", "watch")),
            "source_ids": list(source_ids) if isinstance(source_ids, list) else [],
        }
    return {"id": f"CAT{index}", "title": str(item), "date": "", "window": "", "status": "watch", "source_ids": []}


def _normalize_broker_view(item: Any, index: int) -> Dict[str, Any]:
    if isinstance(item, dict):
        source_ids = item.get("source_ids", [])
        return {
            "id": str(item.get("id", f"B{index}")),
            "institution": str(item.get("institution", "")),
            "rating": str(item.get("rating", "")),
            "target": str(item.get("target", "")),
            "as_of": str(item.get("as_of", item.get("date", ""))),
            "thesis": str(item.get("thesis", "")),
            "source_ids": list(source_ids) if isinstance(source_ids, list) else [],
        }
    return {
        "id": f"B{index}",
        "institution": str(item),
        "rating": "",
        "target": "",
        "as_of": "",
        "thesis": "",
        "source_ids": [],
    }


def _normalize_position_rule(item: Any, index: int) -> Dict[str, Any]:
    if isinstance(item, dict):
        source_ids = item.get("source_ids", [])
        tags = item.get("tags", [])
        return {
            "id": str(item.get("id", f"P{index}")),
            "rule": str(item.get("rule") or item.get("item") or item.get("description") or ""),
            "status": str(item.get("status", "open")),
            "exposure": str(item.get("exposure", "")),
            "tags": [str(tag) for tag in tags] if isinstance(tags, list) else [],
            "source_ids": list(source_ids) if isinstance(source_ids, list) else [],
        }
    return {"id": f"P{index}", "rule": str(item), "status": "open", "exposure": "", "tags": [], "source_ids": []}


def _catalyst_timing(item: Mapping[str, Any]) -> str:
    parts = []
    if item["date"]:
        parts.append(f"date: {item['date']}")
    if item["window"]:
        parts.append(f"window: {item['window']}")
    return f" ({'; '.join(parts)})" if parts else ""


def _evidence_records(
    item_type: str, items: Sequence[Mapping[str, Any]], source_ids: set[str], usage: Dict[str, List[str]]
) -> List[Dict[str, Any]]:
    records = []
    for index, item in enumerate(items, start=1):
        item_id = str(item.get("id", f"{item_type.upper()}{index}"))
        refs = [ref for ref in item.get("source_ids", []) if isinstance(ref, str) and ref in source_ids]
        for ref in refs:
            usage[ref].append(f"{item_type}:{item_id}")
        records.append({"type": item_type, "id": item_id, "source_ids": refs})
    return records


def _stale_sources(ledger: Mapping[str, Any]) -> List[Dict[str, Any]]:
    updated = _parse_date(str(ledger.get("updated", "")))
    if updated is None:
        return []
    stale = []
    for source_id, source in sorted(source_lookup(ledger).items()):
        source_date = _parse_date(str(source.get("date", "")))
        if source_date is None:
            continue
        age_days = (updated - source_date).days
        if age_days > 180:
            stale.append(
                {
                    "id": source_id,
                    "title": source["title"],
                    "date": source["date"],
                    "age_days": age_days,
                    "warning": "source is more than 180 days older than ledger.updated",
                }
            )
    return stale


def _parse_date(value: str) -> Optional[date]:
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def _count_by(items: Sequence[Mapping[str, Any]], field: str) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for item in items:
        value = str(item.get(field, "")) or "unspecified"
        counts[value] = counts.get(value, 0) + 1
    return {key: counts[key] for key in sorted(counts)}


def _sorted_counts(counts: Mapping[str, int]) -> Dict[str, int]:
    return {key: counts[key] for key in sorted(counts)}


def _extend_count_lines(lines: List[str], counts: Mapping[str, int], empty_text: str) -> None:
    if counts:
        for key, count in counts.items():
            lines.append(f"- {_inline(key)}: {count}")
    else:
        lines.append(f"- {empty_text}")


def _cell(value: Any) -> str:
    return _inline(value)


def _inline(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\r", " ").replace("\n", " ")


def _inline_join(values: Sequence[Any]) -> str:
    return ", ".join(_inline(value) for value in values) if values else "none"
