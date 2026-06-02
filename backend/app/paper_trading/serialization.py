from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any


def to_float(value: Any) -> float:
    if value is None:
        return 0.0
    return float(value)


def to_optional_float(value: Any) -> float | None:
    if value is None:
        return None
    return float(value)


def to_decimal(value: Any) -> Decimal:
    return Decimal(str(value or 0))


def to_iso(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.isoformat()
    return str(value)
