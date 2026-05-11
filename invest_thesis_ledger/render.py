"""Deterministic Markdown and JSON renderers."""

from __future__ import annotations

import json
import re
from datetime import date
from typing import Any, Dict, List, Mapping, Optional, Sequence

from .schema import source_lookup


_CLOSED_STATUSES = {"done", "closed", "passed", "complete"}
_REVIEW_REASON_ORDER = {
    "stale_sources": 0,
    "high_severity_risks": 1,
    "upcoming_open_catalysts": 2,
    "stale_review": 3,
    "open_checklist": 4,
    "open_position_rules": 5,
}
_POSITIVE_TRIGGER_TERMS = {
    "signed",
    "contract",
    "customer",
    "partnership",
    "raise",
    "reduces",
    "clear",
    "approval",
    "milestone",
}
_NEGATIVE_TRIGGER_TERMS = {
    "delay",
    "miss",
    "failed",
    "failure",
    "deny",
    "denial",
    "weak",
    "unclear",
}
_EVIDENCE_GAP_ORDER = {
    "low_confidence_assumption": 0,
    "stale_source": 1,
    "unused_source": 2,
    "unsupported_item": 3,
}


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
            for item in sorted(ledger["reviews"], key=_review_sort_key)
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


def evidence_audit_payload(ledgers: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
    """Build deterministic portfolio-level evidence audit output."""

    field_coverage: Dict[str, Dict[str, int]] = {}
    ledger_items = []
    unsupported_items = []
    unused_sources = []
    stale_sources = []
    duplicate_candidates: Dict[str, List[Dict[str, str]]] = {}
    totals = {
        "tracked_items": 0,
        "supported_items": 0,
        "unsupported_items": 0,
        "source_count": 0,
        "unused_source_count": 0,
        "stale_source_count": 0,
    }

    for ledger in ledgers:
        ledger_id = str(ledger["thesis_id"])
        asset = ledger["asset"]
        ticker = str(asset["ticker"])
        evidence = _evidence_payload(ledger, include_checklist=True)
        coverage = evidence["coverage"]
        for key in totals:
            totals[key] += int(coverage[key])

        for item in evidence["items"]:
            field = str(item["type"])
            if field not in field_coverage:
                field_coverage[field] = {"tracked_items": 0, "supported_items": 0, "unsupported_items": 0}
            field_coverage[field]["tracked_items"] += 1
            if item["source_ids"]:
                field_coverage[field]["supported_items"] += 1
            else:
                field_coverage[field]["unsupported_items"] += 1
                unsupported_items.append(
                    {
                        "ledger_id": ledger_id,
                        "ticker": ticker,
                        "type": field,
                        "id": str(item["id"]),
                    }
                )

        sources = source_lookup(ledger)
        for source_id in evidence["unused_sources"]:
            source = sources.get(source_id, {})
            unused_sources.append(
                {
                    "ledger_id": ledger_id,
                    "ticker": ticker,
                    "id": str(source_id),
                    "title": str(source.get("title", "")),
                    "url": str(source.get("url", "")),
                }
            )
        for source in evidence["stale_sources"]:
            source_id = str(source["id"])
            source_record = sources.get(source_id, {})
            item = dict(source)
            item["ledger_id"] = ledger_id
            item["ticker"] = ticker
            item["url"] = str(source_record.get("url", ""))
            stale_sources.append(item)
        for source_id, source in sorted(sources.items()):
            url = str(source.get("url", "")).strip()
            if not url:
                continue
            duplicate_candidates.setdefault(url, []).append(
                {
                    "ledger_id": ledger_id,
                    "ticker": ticker,
                    "source_id": str(source_id),
                    "title": str(source.get("title", "")),
                }
            )

        ledger_items.append(
            {
                "rank": 0,
                "thesis_id": ledger_id,
                "title": ledger["title"],
                "updated": ledger["updated"],
                "ticker": ticker,
                "asset_name": asset["name"],
                "asset_type": asset["type"],
                "quality_score": _evidence_quality_score(coverage),
                "coverage": coverage,
            }
        )

    ledger_items.sort(key=_evidence_audit_ledger_sort_key)
    for index, item in enumerate(ledger_items, start=1):
        item["rank"] = index

    duplicate_source_urls = []
    for url, occurrences in duplicate_candidates.items():
        ledger_ids = {item["ledger_id"] for item in occurrences}
        if len(ledger_ids) < 2:
            continue
        occurrences.sort(key=lambda item: (item["ledger_id"], item["ticker"], item["source_id"], item["title"]))
        duplicate_source_urls.append(
            {
                "url": url,
                "ledger_count": len(ledger_ids),
                "occurrence_count": len(occurrences),
                "occurrences": occurrences,
            }
        )
    duplicate_source_urls.sort(key=lambda item: (item["url"], item["ledger_count"], item["occurrence_count"]))
    unsupported_items.sort(key=lambda item: (item["ledger_id"], item["ticker"], item["type"], item["id"]))
    unused_sources.sort(key=lambda item: (item["ledger_id"], item["ticker"], item["id"], item["title"], item["url"]))
    stale_sources.sort(
        key=lambda item: (
            item["ledger_id"],
            item["ticker"],
            item["id"],
            item["date"],
            item["title"],
            item["age_days"],
            item["url"],
        )
    )

    return {
        "audit": {
            "ledger_count": len(ledgers),
            "tracked_items": totals["tracked_items"],
            "supported_items": totals["supported_items"],
            "unsupported_items": totals["unsupported_items"],
            "source_count": totals["source_count"],
            "unused_source_count": totals["unused_source_count"],
            "stale_source_count": totals["stale_source_count"],
            "duplicate_source_url_count": len(duplicate_source_urls),
        },
        "field_coverage": {field: field_coverage[field] for field in sorted(field_coverage)},
        "ledgers": ledger_items,
        "unsupported_items": unsupported_items,
        "unused_sources": unused_sources,
        "stale_sources": stale_sources,
        "duplicate_source_urls": duplicate_source_urls,
    }


def render_evidence_audit(ledgers: Sequence[Mapping[str, Any]]) -> str:
    """Render a Markdown portfolio evidence audit."""

    payload = evidence_audit_payload(ledgers)
    lines = [
        "# Portfolio Evidence Audit",
        "",
        "> This is a research organization tool, not investment advice.",
        "",
        f"- Ledgers: {payload['audit']['ledger_count']}",
        f"- Tracked Items: {payload['audit']['tracked_items']}",
        f"- Supported Items: {payload['audit']['supported_items']}",
        f"- Unsupported Items: {payload['audit']['unsupported_items']}",
        f"- Sources: {payload['audit']['source_count']}",
        f"- Unused Sources: {payload['audit']['unused_source_count']}",
        f"- Stale Sources: {payload['audit']['stale_source_count']}",
        f"- Duplicate Source URLs: {payload['audit']['duplicate_source_url_count']}",
        "",
        "## Ledger Scores",
        "",
        "| Rank | Score | Ticker | Ledger ID | Updated | Tracked | Unsupported | Unused Sources | Stale Sources |",
        "| ---: | ---: | --- | --- | --- | ---: | ---: | ---: | ---: |",
    ]
    for item in payload["ledgers"]:
        coverage = item["coverage"]
        lines.append(
            "| "
            + " | ".join(
                [
                    str(item["rank"]),
                    str(item["quality_score"]),
                    _cell(item["ticker"]),
                    _cell(item["thesis_id"]),
                    _cell(item["updated"]),
                    str(coverage["tracked_items"]),
                    str(coverage["unsupported_items"]),
                    str(coverage["unused_source_count"]),
                    str(coverage["stale_source_count"]),
                ]
            )
            + " |"
        )
    lines.extend(["", "## Field Coverage", ""])
    if payload["field_coverage"]:
        lines.extend(["| Field | Tracked | Supported | Unsupported |", "| --- | ---: | ---: | ---: |"])
        for field, coverage in payload["field_coverage"].items():
            lines.append(
                f"| {_cell(field)} | {coverage['tracked_items']} | {coverage['supported_items']} | {coverage['unsupported_items']} |"
            )
    else:
        lines.append("- No evidence-tracked items recorded.")
    lines.extend(["", "## Unsupported Items", ""])
    if payload["unsupported_items"]:
        lines.extend(["| Ledger ID | Ticker | Type | ID |", "| --- | --- | --- | --- |"])
        for item in payload["unsupported_items"]:
            lines.append(
                f"| {_cell(item['ledger_id'])} | {_cell(item['ticker'])} | {_cell(item['type'])} | {_cell(item['id'])} |"
            )
    else:
        lines.append("- No unsupported items detected.")
    lines.extend(["", "## Unused Sources", ""])
    if payload["unused_sources"]:
        lines.extend(["| Ledger ID | Ticker | Source | Title | URL |", "| --- | --- | --- | --- | --- |"])
        for item in payload["unused_sources"]:
            lines.append(
                f"| {_cell(item['ledger_id'])} | {_cell(item['ticker'])} | {_cell(item['id'])} | {_cell(item['title'])} | {_cell(item['url'])} |"
            )
    else:
        lines.append("- No unused sources detected.")
    lines.extend(["", "## Stale Sources", ""])
    if payload["stale_sources"]:
        lines.extend(["| Ledger ID | Ticker | Source | Title | Date | Age Days | URL |", "| --- | --- | --- | --- | --- | ---: | --- |"])
        for item in payload["stale_sources"]:
            lines.append(
                f"| {_cell(item['ledger_id'])} | {_cell(item['ticker'])} | {_cell(item['id'])} | {_cell(item['title'])} | {_cell(item['date'])} | {item['age_days']} | {_cell(item['url'])} |"
            )
    else:
        lines.append("- No stale sources detected.")
    lines.extend(["", "## Duplicate Source URLs", ""])
    if payload["duplicate_source_urls"]:
        lines.extend(["| URL | Ledgers | Occurrences |", "| --- | --- | --- |"])
        for item in payload["duplicate_source_urls"]:
            occurrences = ", ".join(
                f"{occurrence['ledger_id']}[{occurrence['source_id']}]" for occurrence in item["occurrences"]
            )
            lines.append(
                f"| {_cell(item['url'])} | {item['ledger_count']} | {_cell(occurrences)} |"
            )
    else:
        lines.append("- No duplicate source URLs across ledgers detected.")
    return "\n".join(lines) + "\n"


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


def review_queue_payload(ledgers: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
    """Build deterministic review queue output for multiple ledgers."""

    items = [_review_queue_item(ledger) for ledger in ledgers]
    items.sort(key=_review_queue_sort_key)
    return {
        "queue": {
            "ledger_count": len(items),
            "high_priority_count": sum(1 for item in items if item["priority"] == "high"),
            "medium_priority_count": sum(1 for item in items if item["priority"] == "medium"),
            "low_priority_count": sum(1 for item in items if item["priority"] == "low"),
        },
        "items": items,
    }


def render_review_queue(ledgers: Sequence[Mapping[str, Any]]) -> str:
    """Render a Markdown queue of ledgers needing human review."""

    payload = review_queue_payload(ledgers)
    lines = [
        "# Review Queue",
        "",
        "> This is a research organization tool, not investment advice.",
        "",
        f"- Ledgers: {payload['queue']['ledger_count']}",
        f"- High Priority: {payload['queue']['high_priority_count']}",
        f"- Medium Priority: {payload['queue']['medium_priority_count']}",
        f"- Low Priority: {payload['queue']['low_priority_count']}",
        "",
        "## Queue",
        "",
        "| Priority | Score | Ticker | Ledger ID | Updated | Next Action |",
        "| --- | ---: | --- | --- | --- | --- |",
    ]
    for item in payload["items"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    _cell(item["priority"]),
                    str(item["score"]),
                    _cell(item["ticker"]),
                    _cell(item["thesis_id"]),
                    _cell(item["updated"]),
                    _cell(item["next_action"]),
                ]
            )
            + " |"
        )
    lines.extend(["", "## Reasons", ""])
    for item in payload["items"]:
        lines.extend([f"### {_inline(item['ticker'])} - {_inline(item['title'])}", ""])
        lines.append(f"- Priority: {_inline(item['priority'])}")
        lines.append(f"- Score: {item['score']}")
        lines.append(f"- Next Action: {_inline(item['next_action'])}")
        if item["reasons"]:
            for reason in item["reasons"]:
                lines.append(
                    f"- {_inline(reason['type'])}: {_inline(reason['text'])} "
                    f"(count: {reason['count']}; score: {reason['score']})"
                )
        else:
            lines.append("- No review triggers detected.")
        lines.append("")
    return "\n".join(lines) + "\n"


def watchlist_payload(ledgers: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
    """Build deterministic weekly watchlist output from existing report payloads."""

    items = [_watchlist_item(ledger) for ledger in ledgers]
    items.sort(key=_watchlist_sort_key)
    for rank, item in enumerate(items, start=1):
        item["rank"] = rank
    return {
        "watchlist": {
            "ledger_count": len(items),
            "high_priority_count": sum(1 for item in items if item["priority"] == "high"),
            "medium_priority_count": sum(1 for item in items if item["priority"] == "medium"),
            "low_priority_count": sum(1 for item in items if item["priority"] == "low"),
        },
        "items": items,
    }


def render_watchlist(ledgers: Sequence[Mapping[str, Any]]) -> str:
    """Render a deterministic weekly watchlist report."""

    payload = watchlist_payload(ledgers)
    lines = [
        "# Watchlist",
        "",
        "> This is a research organization tool, not investment advice.",
        "",
        f"- Ledgers: {payload['watchlist']['ledger_count']}",
        f"- High Priority: {payload['watchlist']['high_priority_count']}",
        f"- Medium Priority: {payload['watchlist']['medium_priority_count']}",
        f"- Low Priority: {payload['watchlist']['low_priority_count']}",
        "",
        "## Weekly Review List",
        "",
        "| Rank | Score | Ticker | Title | Priority | Next Action | Nearest Open Catalyst | Latest Review | Stale Sources | High Risks | Open Position Rules |",
        "| ---: | ---: | --- | --- | --- | --- | --- | --- | ---: | ---: | ---: |",
    ]
    for item in payload["items"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    str(item["rank"]),
                    str(item["review_queue_score"]),
                    _cell(item["ticker"]),
                    _cell(item["title"]),
                    _cell(item["priority"]),
                    _cell(item["next_action"]),
                    _cell(_watchlist_catalyst_label(item["nearest_open_catalyst"])),
                    _cell(_watchlist_review_label(item["latest_review"])),
                    str(item["stale_source_count"]),
                    str(item["high_risk_count"]),
                    str(item["open_position_rule_count"]),
                ]
            )
            + " |"
        )
    return "\n".join(lines) + "\n"


def decision_memo_payload(ledger: Mapping[str, Any]) -> Dict[str, Any]:
    """Build structured pre-trade/review decision memo output."""

    reviews = history_payload(ledger)["reviews"]
    latest_review = reviews[-1] if reviews else {}
    broker = broker_matrix_payload(ledger)
    exposure = exposure_payload(ledger)
    evidence = evidence_payload(ledger)
    high_risks = [
        {
            "id": risk["id"],
            "name": risk["name"],
            "severity": risk["severity"],
            "probability": risk["probability"],
            "mitigation": risk["mitigation"],
            "tags": list(risk.get("tags", [])) if isinstance(risk.get("tags", []), list) else [],
            "source_ids": list(risk["source_ids"]),
        }
        for risk in ledger.get("risks", [])
        if isinstance(risk, dict) and str(risk.get("severity", "")).lower() in {"high", "critical", "severe"}
    ]
    high_risks.sort(key=lambda item: item["id"])
    open_position_rules = [
        item for item in exposure["position_rules"] if not _is_closed_status(str(item.get("status", "")))
    ]
    open_checklist = [
        item for item in risk_payload(ledger)["checklist"] if not _is_closed_status(str(item.get("status", "")))
    ]
    catalysts = calendar_payload(ledger)["catalysts"]
    open_catalysts = [item for item in catalysts if not _is_closed_status(str(item.get("status", "")))]
    questions = _decision_questions(
        latest_review, high_risks, open_catalysts, open_position_rules, open_checklist, evidence
    )
    return {
        "thesis_id": ledger["thesis_id"],
        "title": ledger["title"],
        "updated": ledger["updated"],
        "asset": dict(ledger["asset"]),
        "thesis": ledger["thesis"],
        "assumptions": [
            {
                "id": item["id"],
                "statement": item["statement"],
                "confidence": item["confidence"],
                "source_ids": list(item["source_ids"]),
            }
            for item in sorted(
                [item for item in ledger.get("assumptions", []) if isinstance(item, dict)],
                key=lambda item: str(item.get("id", "")),
            )
        ],
        "latest_review": {
            "date": latest_review.get("date", ""),
            "decision": latest_review.get("decision", ""),
            "summary": latest_review.get("summary", ""),
            "drift": latest_review.get("drift", "none recorded"),
            "source_ids": list(latest_review.get("source_ids", [])),
        },
        "broker_view_summary": {
            "view_count": len(broker["broker_views"]),
            "rating_counts": broker["rating_counts"],
            "views": broker["broker_views"],
        },
        "high_risks": high_risks,
        "catalyst_checklist": catalysts,
        "exposure": {
            "positions": [str(item) for item in ledger.get("positions", [])],
            "tag_counts": exposure["tag_counts"],
            "open_position_rules": open_position_rules,
            "open_checklist": open_checklist,
        },
        "evidence_summary": {
            "coverage": evidence["coverage"],
            "stale_sources": evidence["stale_sources"],
            "unused_sources": evidence["unused_sources"],
            "unsupported_items": [item for item in evidence["items"] if not item["source_ids"]],
        },
        "questions_before_action": questions,
    }


def render_decision_memo(ledger: Mapping[str, Any]) -> str:
    """Render a deterministic pre-trade/review decision memo."""

    payload = decision_memo_payload(ledger)
    lines = [
        f"# Decision Memo: {_inline(payload['title'])}",
        "",
        "> This is a research organization tool, not investment advice.",
        "",
        "## Asset / Thesis Snapshot",
        "",
        f"- Ledger ID: {_inline(payload['thesis_id'])}",
        f"- Updated: {_inline(payload['updated'])}",
        f"- Asset: {_inline(payload['asset']['ticker'])} ({_inline(payload['asset']['name'])})",
        f"- Type: {_inline(payload['asset']['type'])}",
        f"- Thesis: {_inline(payload['thesis'])}",
        "",
        "### Assumptions",
        "",
    ]
    if payload["assumptions"]:
        for item in payload["assumptions"]:
            lines.append(
                f"- {_inline(item['id'])}: {_inline(item['statement'])} "
                f"(confidence: {_inline(item['confidence'])}; sources: {_refs(item['source_ids'])})"
            )
    else:
        lines.append("- No assumptions recorded.")
    latest = payload["latest_review"]
    lines.extend(["", "## Latest Review", ""])
    if latest["date"]:
        lines.extend(
            [
                f"- Date: {_inline(latest['date'])}",
                f"- Decision: {_inline(latest['decision'])}",
                f"- Summary: {_inline(latest['summary'])}",
                f"- Drift: {_inline(latest['drift'])}",
                f"- Sources: {_refs(latest['source_ids'])}",
            ]
        )
    else:
        lines.append("- No review recorded.")
    lines.extend(["", "## Broker View Summary", ""])
    broker = payload["broker_view_summary"]
    lines.append(f"- Views: {broker['view_count']}")
    if broker["rating_counts"]:
        for rating, count in broker["rating_counts"].items():
            lines.append(f"- Rating {_inline(rating)}: {count}")
    else:
        lines.append("- No broker ratings recorded.")
    if broker["views"]:
        lines.extend(["", "| Institution | Rating | Target | As Of | Thesis | Sources |", "| --- | --- | --- | --- | --- | --- |"])
        for item in broker["views"]:
            lines.append(
                "| "
                + " | ".join(
                    [
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
    lines.extend(["", "## High Risks", ""])
    if payload["high_risks"]:
        for item in payload["high_risks"]:
            lines.append(
                f"- {_inline(item['id'])}: {_inline(item['name'])} "
                f"(severity: {_inline(item['severity'])}; probability: {_inline(item['probability'])}; "
                f"tags: {_inline_join(item['tags'])}; mitigation: {_inline(item['mitigation'])}; "
                f"sources: {_refs(item['source_ids'])})"
            )
    else:
        lines.append("- No high-severity risks recorded.")
    lines.extend(["", "## Catalyst Checklist", ""])
    if payload["catalyst_checklist"]:
        for item in payload["catalyst_checklist"]:
            timing = _catalyst_timing(item)
            lines.append(
                f"- [{_checkbox(item['status'])}] {_inline(item['id'])}: {_inline(item['title'])}"
                f"{_inline(timing)} (status: {_inline(item['status'])}; sources: {_refs(item['source_ids'])})"
            )
    else:
        lines.append("- No catalysts recorded.")
    lines.extend(["", "## Exposure / Open Position Rules", ""])
    if payload["exposure"]["positions"]:
        for item in payload["exposure"]["positions"]:
            lines.append(f"- Position note: {_inline(item)}")
    else:
        lines.append("- No position notes recorded.")
    if payload["exposure"]["open_position_rules"]:
        for item in payload["exposure"]["open_position_rules"]:
            lines.append(
                f"- [ ] {_inline(item['id'])}: {_inline(item['rule'])} "
                f"(exposure: {_inline(item['exposure']) if item['exposure'] else 'not specified'}; "
                f"tags: {_inline_join(item['tags'])}; sources: {_refs(item['source_ids'])})"
            )
    else:
        lines.append("- No open position rules recorded.")
    if payload["exposure"]["open_checklist"]:
        for item in payload["exposure"]["open_checklist"]:
            lines.append(f"- [ ] {_inline(item['id'])}: {_inline(item['item'])} ({_inline(item['status'])})")
    lines.extend(["", "## Evidence / Stale-Source Summary", ""])
    coverage = payload["evidence_summary"]["coverage"]
    lines.extend(
        [
            f"- Tracked Items: {coverage['tracked_items']}",
            f"- Supported Items: {coverage['supported_items']}",
            f"- Unsupported Items: {coverage['unsupported_items']}",
            f"- Sources: {coverage['source_count']}",
            f"- Unused Sources: {coverage['unused_source_count']}",
            f"- Stale Sources: {coverage['stale_source_count']}",
        ]
    )
    if payload["evidence_summary"]["stale_sources"]:
        for item in payload["evidence_summary"]["stale_sources"]:
            lines.append(f"- Stale [{_inline(item['id'])}] {_inline(item['title'])} ({_inline(item['date'])}): {item['age_days']} days old")
    else:
        lines.append("- No stale sources detected.")
    if payload["evidence_summary"]["unsupported_items"]:
        for item in payload["evidence_summary"]["unsupported_items"]:
            lines.append(f"- Unsupported {_inline(item['type'])} {_inline(item['id'])}")
    lines.extend(["", "## Questions before action", ""])
    for item in payload["questions_before_action"]:
        lines.append(f"- [ ] {_inline(item['id'])}: {_inline(item['question'])}")
    lines.extend(["", "## Sources", ""])
    lines.extend(_source_lines(ledger))
    return "\n".join(lines) + "\n"


def scenario_plan_payload(ledger: Mapping[str, Any]) -> Dict[str, Any]:
    """Build deterministic scenario planning output from existing ledger fields."""

    assumptions = [
        {
            "id": str(item["id"]),
            "statement": str(item["statement"]),
            "confidence": str(item["confidence"]),
            "source_ids": list(item["source_ids"]),
        }
        for item in ledger.get("assumptions", [])
        if isinstance(item, dict)
    ]
    assumptions.sort(key=lambda item: item["id"])
    risks = [
        {
            "id": str(item["id"]),
            "name": str(item["name"]),
            "severity": str(item["severity"]),
            "probability": str(item["probability"]),
            "mitigation": str(item["mitigation"]),
            "tags": list(item.get("tags", [])) if isinstance(item.get("tags", []), list) else [],
            "source_ids": list(item["source_ids"]),
        }
        for item in ledger.get("risks", [])
        if isinstance(item, dict)
    ]
    risks.sort(key=lambda item: item["id"])
    catalysts = calendar_payload(ledger)["catalysts"]
    open_catalysts = [item for item in catalysts if not _is_closed_status(str(item.get("status", "")))]
    position_rules = exposure_payload(ledger)["position_rules"]
    open_position_rules = [
        item for item in position_rules if not _is_closed_status(str(item.get("status", "")))
    ]
    evidence = evidence_payload(ledger)
    evidence_gaps = _scenario_evidence_gaps(assumptions, evidence)
    return {
        "thesis_id": ledger["thesis_id"],
        "title": ledger["title"],
        "updated": ledger["updated"],
        "asset": dict(ledger["asset"]),
        "thesis": ledger["thesis"],
        "scenario_plan": {
            "case_count": 3,
            "trigger_count": len(open_catalysts),
            "position_constraint_count": len(open_position_rules),
            "risk_mitigation_count": len(risks),
            "evidence_gap_count": len(evidence_gaps),
        },
        "cases": [
            _scenario_case(
                "base",
                "Base Case",
                "Current thesis remains intact if source-backed assumptions hold and open risks stay controlled.",
                [item for item in assumptions if _confidence_rank(item["confidence"]) >= 1],
                risks,
                [item for item in open_catalysts if _scenario_trigger_direction(item) == "base"],
                risks,
                open_position_rules,
                evidence_gaps,
            ),
            _scenario_case(
                "bull",
                "Bull Case",
                "Upside case requires higher-conviction assumptions and positive catalysts becoming source-backed.",
                [item for item in assumptions if _confidence_rank(item["confidence"]) >= 2],
                [item for item in risks if _risk_rank(item["severity"], item["probability"]) <= 1],
                [item for item in open_catalysts if _scenario_trigger_direction(item) == "bull"],
                risks,
                open_position_rules,
                evidence_gaps,
            ),
            _scenario_case(
                "bear",
                "Bear Case",
                "Downside case is driven by low-confidence assumptions, severe risks, or unresolved evidence gaps.",
                [item for item in assumptions if _confidence_rank(item["confidence"]) <= 0],
                [item for item in risks if _risk_rank(item["severity"], item["probability"]) >= 2],
                [item for item in open_catalysts if _scenario_trigger_direction(item) == "bear"],
                risks,
                open_position_rules,
                evidence_gaps,
            ),
        ],
        "source_summary": {
            "coverage": evidence["coverage"],
            "stale_sources": evidence["stale_sources"],
            "unused_sources": evidence["unused_sources"],
        },
    }


def render_scenario_plan(ledger: Mapping[str, Any]) -> str:
    """Render deterministic scenario planning output."""

    payload = scenario_plan_payload(ledger)
    asset = payload["asset"]
    lines = [
        f"# Scenario Plan: {_inline(payload['title'])}",
        "",
        "> This is a research organization tool, not investment advice.",
        "",
        "## Asset / Thesis",
        "",
        f"- Ledger ID: {_inline(payload['thesis_id'])}",
        f"- Updated: {_inline(payload['updated'])}",
        f"- Asset: {_inline(asset['ticker'])} ({_inline(asset['name'])})",
        f"- Type: {_inline(asset['type'])}",
        f"- Thesis: {_inline(payload['thesis'])}",
        "",
        "## Plan Summary",
        "",
    ]
    summary = payload["scenario_plan"]
    lines.extend(
        [
            f"- Cases: {summary['case_count']}",
            f"- Open Scenario Triggers: {summary['trigger_count']}",
            f"- Open Position Constraints: {summary['position_constraint_count']}",
            f"- Risk Mitigation Actions: {summary['risk_mitigation_count']}",
            f"- Evidence Gaps: {summary['evidence_gap_count']}",
        ]
    )
    for case in payload["cases"]:
        lines.extend(["", f"## {case['name']}", "", _inline(case["summary"]), "", "### Assumptions", ""])
        if case["assumptions"]:
            for item in case["assumptions"]:
                lines.append(
                    f"- {_inline(item['id'])}: {_inline(item['statement'])} "
                    f"(confidence: {_inline(item['confidence'])}; sources: {_refs(item['source_ids'])})"
                )
        else:
            lines.append("- No assumptions mapped to this case.")
        lines.extend(["", "### Risk Conditions", ""])
        if case["risks"]:
            for item in case["risks"]:
                lines.append(
                    f"- {_inline(item['id'])}: {_inline(item['name'])} "
                    f"(severity: {_inline(item['severity'])}; probability: {_inline(item['probability'])})"
                )
        else:
            lines.append("- No risks mapped to this case.")
        lines.extend(["", "### Catalyst Triggers", ""])
        if case["triggers"]:
            for item in case["triggers"]:
                timing = _catalyst_timing(item)
                lines.append(
                    f"- {_inline(item['id'])}: {_inline(item['title'])}{_inline(timing)} "
                    f"(direction: {_inline(item['direction'])}; status: {_inline(item['status'])}; "
                    f"sources: {_refs(item['source_ids'])})"
                )
        else:
            lines.append("- No open catalyst triggers mapped to this case.")
        lines.extend(["", "### Risk Mitigation Actions", ""])
        if case["risk_mitigations"]:
            for item in case["risk_mitigations"]:
                lines.append(f"- {_inline(item['id'])}: {_inline(item['action'])} (risk: {_inline(item['risk'])})")
        else:
            lines.append("- No risk mitigation actions recorded.")
        lines.extend(["", "### Position-Rule Constraints", ""])
        if case["position_constraints"]:
            for item in case["position_constraints"]:
                lines.append(
                    f"- [{_checkbox(item['status'])}] {_inline(item['id'])}: {_inline(item['rule'])} "
                    f"(exposure: {_inline(item['exposure']) if item['exposure'] else 'not specified'}; "
                    f"tags: {_inline_join(item['tags'])}; sources: {_refs(item['source_ids'])})"
                )
        else:
            lines.append("- No open position-rule constraints recorded.")
        lines.extend(["", "### Evidence Gaps", ""])
        if case["evidence_gaps"]:
            for item in case["evidence_gaps"]:
                lines.append(f"- {_inline(item['id'])}: {_inline(item['gap'])}")
        else:
            lines.append("- No evidence gaps detected.")
    lines.extend(["", "## Sources", ""])
    lines.extend(_source_lines(ledger))
    return "\n".join(lines) + "\n"


def evidence_payload(ledger: Mapping[str, Any]) -> Dict[str, Any]:
    """Build structured source coverage and stale-source output."""

    return _evidence_payload(ledger, include_checklist=False)


def _evidence_payload(ledger: Mapping[str, Any], include_checklist: bool) -> Dict[str, Any]:
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
    if include_checklist:
        records.extend(_evidence_records("checklist", _checklist_evidence_items(ledger), source_ids, usage))
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


def _review_queue_item(ledger: Mapping[str, Any]) -> Dict[str, Any]:
    ledger_id = str(ledger["thesis_id"])
    asset = ledger["asset"]
    stale_sources = evidence_payload(ledger)["stale_sources"]
    high_risks = [
        risk
        for risk in ledger.get("risks", [])
        if isinstance(risk, dict) and str(risk.get("severity", "")).lower() in {"high", "critical", "severe"}
    ]
    open_catalysts = _review_open_catalysts(ledger)
    stale_review = _stale_review(ledger)
    open_checklist = [
        item for item in risk_payload(ledger)["checklist"] if not _is_closed_status(str(item.get("status", "")))
    ]
    open_rules = [
        item for item in exposure_payload(ledger)["position_rules"] if not _is_closed_status(str(item.get("status", "")))
    ]

    reasons = []
    if stale_sources:
        reasons.append(
            {
                "type": "stale_sources",
                "count": len(stale_sources),
                "score": len(stale_sources) * 2,
                "text": f"{len(stale_sources)} source(s) are more than 180 days older than ledger.updated.",
                "items": [str(source["id"]) for source in stale_sources],
            }
        )
    if high_risks:
        reasons.append(
            {
                "type": "high_severity_risks",
                "count": len(high_risks),
                "score": len(high_risks) * 3,
                "text": f"{len(high_risks)} high-severity risk(s) need human review.",
                "items": [
                    str(risk["id"])
                    for risk in sorted(high_risks, key=lambda risk: str(risk.get("id", "")))
                ],
            }
        )
    if open_catalysts:
        reasons.append(
            {
                "type": "upcoming_open_catalysts",
                "count": len(open_catalysts),
                "score": len(open_catalysts),
                "text": f"{len(open_catalysts)} upcoming or open catalyst(s) remain unresolved.",
                "items": [str(item["id"]) for item in open_catalysts],
            }
        )
    if stale_review:
        reasons.append(
            {
                "type": "stale_review",
                "count": 1,
                "score": 3,
                "text": stale_review,
                "items": [],
            }
        )
    if open_checklist:
        reasons.append(
            {
                "type": "open_checklist",
                "count": len(open_checklist),
                "score": len(open_checklist),
                "text": f"{len(open_checklist)} checklist item(s) remain open.",
                "items": [
                    str(item["id"])
                    for item in sorted(open_checklist, key=lambda item: str(item.get("id", "")))
                ],
            }
        )
    if open_rules:
        reasons.append(
            {
                "type": "open_position_rules",
                "count": len(open_rules),
                "score": len(open_rules),
                "text": f"{len(open_rules)} position rule(s) remain open.",
                "items": [
                    str(item["id"])
                    for item in sorted(open_rules, key=lambda item: str(item.get("id", "")))
                ],
            }
        )

    reasons.sort(
        key=lambda reason: (
            _REVIEW_REASON_ORDER.get(str(reason["type"]), 99),
            str(reason["type"]),
        )
    )
    score = sum(reason["score"] for reason in reasons)
    priority = _review_priority(score)
    return {
        "thesis_id": ledger_id,
        "title": ledger["title"],
        "updated": ledger["updated"],
        "ticker": asset["ticker"],
        "asset_name": asset["name"],
        "asset_type": asset["type"],
        "score": score,
        "priority": priority,
        "next_action": _review_next_action(reasons),
        "reasons": reasons,
    }


def _review_queue_sort_key(item: Mapping[str, Any]) -> tuple[Any, ...]:
    return (
        -int(item["score"]),
        _priority_rank(str(item["priority"])),
        str(item["ticker"]),
        str(item["thesis_id"]),
        str(item["title"]),
        str(item["updated"]),
        str(item["asset_name"]),
        str(item["asset_type"]),
        str(item["next_action"]),
        json.dumps(item.get("reasons", []), sort_keys=True),
    )


def _watchlist_item(ledger: Mapping[str, Any]) -> Dict[str, Any]:
    queue_item = _review_queue_item(ledger)
    evidence = evidence_payload(ledger)
    exposure = exposure_payload(ledger)
    latest_review = _latest_review(ledger)
    open_position_rules = [
        item for item in exposure["position_rules"] if not _is_closed_status(str(item.get("status", "")))
    ]
    return {
        "rank": 0,
        "thesis_id": queue_item["thesis_id"],
        "ticker": queue_item["ticker"],
        "title": queue_item["title"],
        "review_queue_score": queue_item["score"],
        "priority": queue_item["priority"],
        "next_action": queue_item["next_action"],
        "nearest_open_catalyst": _nearest_open_catalyst(ledger),
        "latest_review": {
            "date": latest_review.get("date", ""),
            "decision": latest_review.get("decision", ""),
        },
        "stale_source_count": evidence["coverage"]["stale_source_count"],
        "high_risk_count": _high_risk_count(ledger),
        "open_position_rule_count": len(open_position_rules),
    }


def _watchlist_sort_key(item: Mapping[str, Any]) -> tuple[Any, ...]:
    return (
        -int(item["review_queue_score"]),
        _priority_rank(str(item["priority"])),
        str(item["ticker"]),
        str(item["thesis_id"]),
        str(item["title"]),
        str(item["latest_review"]["date"]),
        str(item["latest_review"]["decision"]),
        json.dumps(item.get("nearest_open_catalyst"), sort_keys=True),
        int(item["stale_source_count"]),
        int(item["high_risk_count"]),
        int(item["open_position_rule_count"]),
        str(item["next_action"]),
    )


def _evidence_quality_score(coverage: Mapping[str, Any]) -> int:
    tracked = int(coverage.get("tracked_items", 0))
    supported = int(coverage.get("supported_items", 0))
    source_count = int(coverage.get("source_count", 0))
    unused = int(coverage.get("unused_source_count", 0))
    stale = int(coverage.get("stale_source_count", 0))
    support_points = (supported * 60 // tracked) if tracked else 0
    used_source_points = ((source_count - unused) * 20 // source_count) if source_count else 0
    fresh_source_points = ((source_count - stale) * 20 // source_count) if source_count else 0
    return max(0, min(100, support_points + used_source_points + fresh_source_points))


def _evidence_audit_ledger_sort_key(item: Mapping[str, Any]) -> tuple[Any, ...]:
    coverage = item["coverage"]
    return (
        -int(item["quality_score"]),
        int(coverage["unsupported_items"]),
        int(coverage["unused_source_count"]),
        int(coverage["stale_source_count"]),
        str(item["ticker"]),
        str(item["thesis_id"]),
        str(item["title"]),
        str(item["updated"]),
        str(item["asset_name"]),
        str(item["asset_type"]),
    )


def _latest_review(ledger: Mapping[str, Any]) -> Dict[str, Any]:
    reviews = history_payload(ledger)["reviews"]
    return reviews[-1] if reviews else {}


def _nearest_open_catalyst(ledger: Mapping[str, Any]) -> Optional[Dict[str, Any]]:
    catalysts = _review_open_catalysts(ledger)
    if not catalysts:
        return None
    item = catalysts[0]
    return {
        "id": item["id"],
        "title": item["title"],
        "date": item["date"],
        "window": item["window"],
        "status": item["status"],
    }


def _high_risk_count(ledger: Mapping[str, Any]) -> int:
    return sum(
        1
        for risk in ledger.get("risks", [])
        if isinstance(risk, dict) and str(risk.get("severity", "")).lower() in {"high", "critical", "severe"}
    )


def _watchlist_catalyst_label(catalyst: Optional[Mapping[str, Any]]) -> str:
    if catalyst is None:
        return "none"
    timing = _catalyst_timing(catalyst)
    return f"{catalyst['id']}: {catalyst['title']}{timing} ({catalyst['status']})"


def _watchlist_review_label(review: Mapping[str, Any]) -> str:
    if not review.get("date"):
        return "none"
    return f"{review['date']} - {review.get('decision', '')}"


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
    review_items.sort(key=_review_sort_key)
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


def _checklist_evidence_items(ledger: Mapping[str, Any]) -> List[Dict[str, Any]]:
    items = []
    for index, item in enumerate(ledger.get("checklist", []), start=1):
        if isinstance(item, dict):
            source_ids = item.get("source_ids", [])
            items.append(
                {
                    "id": str(item.get("id", f"C{index}")),
                    "source_ids": list(source_ids) if isinstance(source_ids, list) else [],
                }
            )
        else:
            items.append({"id": f"C{index}", "source_ids": []})
    return items


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


def _review_open_catalysts(ledger: Mapping[str, Any]) -> List[Dict[str, Any]]:
    updated = _parse_date(str(ledger.get("updated", "")))
    items = []
    for catalyst in calendar_payload(ledger)["catalysts"]:
        if _is_closed_status(catalyst["status"]):
            continue
        catalyst_date = _parse_date(catalyst["date"]) if catalyst["date"] else None
        if not catalyst["date"] or updated is None or catalyst_date is None or catalyst_date >= updated:
            items.append(catalyst)
    items.sort(
        key=lambda item: (
            item["date"] == "",
            item["date"],
            item["window"],
            item["id"],
            item["title"],
            item["status"],
        )
    )
    return items


def _stale_review(ledger: Mapping[str, Any]) -> str:
    updated = _parse_date(str(ledger.get("updated", "")))
    if updated is None:
        return ""
    review_dates = []
    for review in ledger.get("reviews", []):
        if isinstance(review, dict):
            review_date = _parse_date(str(review.get("date", "")))
            if review_date is not None:
                review_dates.append(review_date)
    if not review_dates:
        return "No dated review is recorded."
    latest_review = max(review_dates)
    if latest_review < updated:
        age_days = (updated - latest_review).days
        return f"Latest review is {age_days} day(s) before ledger.updated."
    return ""


def _review_priority(score: int) -> str:
    if score >= 8:
        return "high"
    if score >= 4:
        return "medium"
    return "low"


def _priority_rank(priority: str) -> int:
    return {"high": 0, "medium": 1, "low": 2}.get(priority, 3)


def _review_next_action(reasons: Sequence[Mapping[str, Any]]) -> str:
    reason_types = [str(reason["type"]) for reason in reasons]
    if "stale_review" in reason_types:
        return "Run a human review and record a new review entry."
    if "high_severity_risks" in reason_types:
        return "Review high-severity risks and update mitigation evidence."
    if "upcoming_open_catalysts" in reason_types:
        return "Check catalyst status and update dated evidence."
    if "stale_sources" in reason_types:
        return "Refresh stale sources before relying on the thesis."
    if "open_position_rules" in reason_types:
        return "Resolve open position rules before changing exposure."
    if "open_checklist" in reason_types:
        return "Close or update open checklist items."
    return "No immediate human review trigger detected."


def _decision_questions(
    latest_review: Mapping[str, Any],
    high_risks: Sequence[Mapping[str, Any]],
    catalysts: Sequence[Mapping[str, Any]],
    open_position_rules: Sequence[Mapping[str, Any]],
    open_checklist: Sequence[Mapping[str, Any]],
    evidence: Mapping[str, Any],
) -> List[Dict[str, str]]:
    questions = [
        {
            "id": "Q1",
            "question": "Does the latest review decision still support the contemplated action?",
        },
        {
            "id": "Q2",
            "question": "Are all high-severity risks understood with current mitigation evidence?",
        },
        {
            "id": "Q3",
            "question": "Have open catalysts been checked for new source-backed status changes?",
        },
        {
            "id": "Q4",
            "question": "Do open position rules permit the proposed exposure?",
        },
        {
            "id": "Q5",
            "question": "Are stale, unused, or unsupported evidence gaps acceptable before action?",
        },
    ]
    if not latest_review.get("date"):
        questions.append({"id": "Q6", "question": "Should a dated review be recorded before any action?"})
    elif evidence.get("coverage", {}).get("stale_source_count", 0):
        questions.append({"id": "Q6", "question": "Which stale sources must be refreshed before relying on this memo?"})
    elif not high_risks and not catalysts and not open_position_rules and not open_checklist:
        questions.append({"id": "Q6", "question": "Is there any off-ledger constraint that should be added before action?"})
    else:
        questions.append({"id": "Q6", "question": "What evidence would falsify the action after execution?"})
    return questions


def _scenario_case(
    case_id: str,
    name: str,
    summary: str,
    assumptions: Sequence[Mapping[str, Any]],
    risks: Sequence[Mapping[str, Any]],
    triggers: Sequence[Mapping[str, Any]],
    mitigation_risks: Sequence[Mapping[str, Any]],
    position_rules: Sequence[Mapping[str, Any]],
    evidence_gaps: Sequence[Mapping[str, Any]],
) -> Dict[str, Any]:
    return {
        "id": case_id,
        "name": name,
        "summary": summary,
        "assumptions": list(assumptions),
        "risks": list(risks),
        "triggers": [_scenario_trigger(item) for item in triggers],
        "risk_mitigations": [
            {"id": str(item["id"]), "risk": str(item["name"]), "action": str(item["mitigation"])}
            for item in mitigation_risks
        ],
        "position_constraints": list(position_rules),
        "evidence_gaps": list(evidence_gaps),
    }


def _scenario_trigger(item: Mapping[str, Any]) -> Dict[str, Any]:
    trigger = dict(item)
    trigger["direction"] = _scenario_trigger_direction(item)
    return trigger


def _scenario_trigger_direction(item: Mapping[str, Any]) -> str:
    text = f"{item.get('title', '')} {item.get('status', '')}".lower()
    if _contains_trigger_term(text, _NEGATIVE_TRIGGER_TERMS):
        return "bear"
    if _contains_trigger_term(text, _POSITIVE_TRIGGER_TERMS):
        return "bull"
    return "base"


def _scenario_evidence_gaps(
    assumptions: Sequence[Mapping[str, Any]], evidence: Mapping[str, Any]
) -> List[Dict[str, str]]:
    gaps = []
    for item in assumptions:
        if _confidence_rank(str(item.get("confidence", ""))) <= 0:
            gaps.append(
                {
                    "id": f"ASSUMPTION-{item['id']}",
                    "type": "low_confidence_assumption",
                    "gap": f"Low-confidence assumption needs stronger evidence: {item['statement']}",
                }
            )
    for item in evidence.get("stale_sources", []):
        gaps.append(
            {
                "id": f"STALE-{item['id']}",
                "type": "stale_source",
                "gap": f"Refresh stale source {item['id']} dated {item['date']}.",
            }
        )
    for item in evidence.get("items", []):
        if not item.get("source_ids"):
            gaps.append(
                {
                    "id": f"UNSUPPORTED-{item['type']}-{item['id']}",
                    "type": "unsupported_item",
                    "gap": f"Add source support for {item['type']} {item['id']}.",
                }
            )
    for source_id in evidence.get("unused_sources", []):
        gaps.append(
            {
                "id": f"UNUSED-{source_id}",
                "type": "unused_source",
                "gap": f"Either connect source {source_id} to a ledger item or remove it.",
            }
        )
    gaps.sort(key=lambda item: (_EVIDENCE_GAP_ORDER.get(item["type"], 99), item["id"]))
    return gaps


def _contains_trigger_term(text: str, terms: set[str]) -> bool:
    words = set(re.findall(r"[a-z0-9]+", text.lower()))
    for term in terms:
        if term in words:
            return True
        if f"{term}s" in words or f"{term}ed" in words:
            return True
    return False


def _confidence_rank(confidence: str) -> int:
    value = confidence.lower()
    if value in {"high", "strong", "confirmed", "validated"}:
        return 3
    if value in {"medium", "moderate"}:
        return 2
    if value in {"watch", "watchlist", "neutral"}:
        return 1
    if value in {"low", "weak", "unproven", "unknown"}:
        return 0
    return 1


def _risk_rank(severity: str, probability: str) -> int:
    return max(_risk_label_rank(severity), _risk_label_rank(probability))


def _risk_label_rank(value: str) -> int:
    label = value.lower()
    if label in {"critical", "severe", "high"}:
        return 3
    if label in {"medium", "moderate"}:
        return 2
    if label in {"low", "minor"}:
        return 1
    return 2


def _review_sort_key(review: Mapping[str, Any]) -> tuple[str, str, str, tuple[str, ...]]:
    source_ids = review.get("source_ids", [])
    return (
        str(review.get("date", "")),
        str(review.get("decision", "")),
        str(review.get("summary", "")),
        tuple(str(source_id) for source_id in source_ids) if isinstance(source_ids, list) else (),
    )


def _is_closed_status(status: str) -> bool:
    return status.lower() in _CLOSED_STATUSES


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
