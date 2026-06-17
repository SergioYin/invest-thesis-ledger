"""Deterministic hygiene checks for public fixtures."""

from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path
from typing import Any, Iterable, Mapping, Optional, Union


PUBLIC_TEXT_NOTICE = "not investment advice"

PUBLIC_TEXT_EXTENSIONS = {".html", ".md"}
PUBLIC_LEDGER_DIRS = ("examples",)
PUBLIC_TEXT_DIRS = ("examples/output",)

PERSONAL_ACTION_PATTERNS = (
    re.compile(r"\b(?:you|we)\s+(?:should|must|need to|ought to)\s+(?:buy|sell|hold)\b", re.IGNORECASE),
)

RECOMMENDATION_WORDING_PATTERNS = (
    re.compile(r"\b(?:buy|sell|hold)\s+recommendation\b", re.IGNORECASE),
    re.compile(r"\brecommend(?:s|ed|ing)?\s+(?:buying|selling|holding|to\s+(?:buy|sell|hold))\b", re.IGNORECASE),
)

NEUTRAL_RECOMMENDATION_CONTEXTS = (
    "does not recommend",
    "do not recommend",
    "not recommend",
    "no buy/sell/hold recommendation",
)


def public_fixture_hygiene_issues(root: Union[str, Path]) -> list[str]:
    """Return deterministic public fixture hygiene issues under *root*."""

    root_path = Path(root)
    issues: list[str] = []
    issues.extend(_ledger_review_date_issues(root_path))
    issues.extend(_public_text_issues(root_path))
    return sorted(issues)


def _ledger_review_date_issues(root: Path) -> list[str]:
    issues: list[str] = []
    for path in _iter_public_json(root):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            issues.append(f"{_rel(root, path)}: invalid JSON: {exc.msg}")
            continue
        if _looks_like_ledger(payload):
            issues.extend(_review_date_issues(root, path, payload))
    return issues


def _iter_public_json(root: Path) -> Iterable[Path]:
    for dirname in PUBLIC_LEDGER_DIRS:
        base = root / dirname
        if base.exists():
            yield from sorted(path for path in base.rglob("*.json") if path.is_file())


def _looks_like_ledger(payload: Any) -> bool:
    return isinstance(payload, dict) and isinstance(payload.get("updated"), str) and isinstance(payload.get("reviews"), list)


def _review_date_issues(root: Path, path: Path, ledger: Mapping[str, Any]) -> list[str]:
    issues: list[str] = []
    updated_text = str(ledger["updated"])
    updated = _parse_iso_date(updated_text)
    if updated is None:
        return [f"{_rel(root, path)}: ledger.updated is not YYYY-MM-DD: {updated_text}"]

    for index, review in enumerate(ledger["reviews"]):
        if not isinstance(review, dict) or not isinstance(review.get("date"), str):
            continue
        review_date_text = review["date"]
        review_date = _parse_iso_date(review_date_text)
        if review_date is None:
            issues.append(f"{_rel(root, path)}: reviews[{index}].date is not YYYY-MM-DD: {review_date_text}")
        elif review_date > updated:
            issues.append(
                f"{_rel(root, path)}: reviews[{index}].date {review_date_text} is after ledger.updated {updated_text}"
            )
    return issues


def _parse_iso_date(value: str) -> Optional[date]:
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def _public_text_issues(root: Path) -> list[str]:
    issues: list[str] = []
    for path in _iter_public_text(root):
        text = path.read_text(encoding="utf-8")
        lower_text = text.lower()
        if PUBLIC_TEXT_NOTICE not in lower_text:
            issues.append(f"{_rel(root, path)}: missing not-investment-advice notice")
        for line_number, line in enumerate(text.splitlines(), start=1):
            if _has_personal_action_wording(line):
                issues.append(f"{_rel(root, path)}:{line_number}: contains buy/sell/hold recommendation wording")
    return issues


def _iter_public_text(root: Path) -> Iterable[Path]:
    for dirname in PUBLIC_TEXT_DIRS:
        base = root / dirname
        if base.exists():
            yield from sorted(
                path for path in base.rglob("*") if path.is_file() and path.suffix.lower() in PUBLIC_TEXT_EXTENSIONS
            )


def _has_personal_action_wording(line: str) -> bool:
    if any(pattern.search(line) for pattern in PERSONAL_ACTION_PATTERNS):
        return True
    lower_line = line.lower()
    if any(context in lower_line for context in NEUTRAL_RECOMMENDATION_CONTEXTS):
        return False
    return any(pattern.search(line) for pattern in RECOMMENDATION_WORDING_PATTERNS)


def _rel(root: Path, path: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()
