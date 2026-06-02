from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from math import isfinite
from typing import Any

import numpy as np
import pandas as pd


def to_iso(value: Any) -> str | None:
    if value is None or pd.isna(value):
        return None
    if isinstance(value, pd.Timestamp):
        value = value.to_pydatetime()
    if isinstance(value, datetime):
        return value.isoformat()
    return str(value)


def to_float(value: Any) -> float | None:
    if value is None or pd.isna(value):
        return None
    result = float(value)
    if not isfinite(result):
        return None
    return result


def to_decimal(value: Any) -> Decimal | None:
    numeric = to_float(value)
    if numeric is None:
        return None
    return Decimal(str(numeric))


def sanitize_json(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): sanitize_json(child) for key, child in value.items()}
    if isinstance(value, list):
        return [sanitize_json(child) for child in value]
    if isinstance(value, tuple):
        return [sanitize_json(child) for child in value]
    if isinstance(value, (datetime, pd.Timestamp)):
        return to_iso(value)
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, np.generic):
        return sanitize_json(value.item())
    if isinstance(value, float) and not isfinite(value):
        return None
    return value
