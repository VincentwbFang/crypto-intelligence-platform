from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import Any

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models import OHLCV, RelativeStrengthSnapshot

LOOKBACK_1H = 1
LOOKBACK_24H = 24
LOOKBACK_7D = 24 * 7
LOOKBACK_30D = 24 * 30


def calculate_return_pct(rows: list[dict[str, Any]], lookback: int) -> float | None:
    if len(rows) <= lookback:
        return None
    latest_close = _safe_float(rows[-1].get("close"))
    previous_close = _safe_float(rows[-1 - lookback].get("close"))
    if latest_close is None or previous_close in (None, 0):
        return None
    return ((latest_close - previous_close) / previous_close) * 100


def calculate_excess_return(
    coin_return: float | None,
    btc_return: float | None,
) -> float | None:
    if coin_return is None or btc_return is None:
        return None
    return coin_return - btc_return


def percentile_ranks(values: dict[str, float | None]) -> dict[str, float | None]:
    valid_values = {key: value for key, value in values.items() if value is not None}
    if not valid_values:
        return {key: None for key in values}
    if len(valid_values) == 1:
        return {key: 50.0 if value is not None else None for key, value in values.items()}

    ordered = list(valid_values.values())
    denominator = len(ordered) - 1
    ranks: dict[str, float | None] = {}
    for key, value in values.items():
        if value is None:
            ranks[key] = None
            continue
        less_count = sum(1 for candidate in ordered if candidate < value)
        equal_count = sum(1 for candidate in ordered if candidate == value)
        ranks[key] = ((less_count + (equal_count - 1) / 2) / denominator) * 100
    return ranks


def calculate_brsi_score(components: dict[str, float | None]) -> float | None:
    required_weights = {
        "excess_return_24h": 0.30,
        "excess_return_7d": 0.30,
        "excess_return_30d": 0.20,
        "relative_trend_score": 0.10,
        "volume_score": 0.10,
    }
    if any(components.get(key) is None for key in required_weights):
        return None
    score = sum(float(components[key]) * weight for key, weight in required_weights.items())
    return max(0.0, min(100.0, score))


def map_brsi_status(score: float | None) -> str:
    if score is None:
        return "Insufficient Data"
    if score >= 80:
        return "Very Strong"
    if score >= 65:
        return "Strong"
    if score >= 50:
        return "Slightly Strong"
    if score >= 35:
        return "Slightly Weak"
    if score >= 20:
        return "Weak"
    return "Very Weak"


class RelativeStrengthService:
    def __init__(self, db_session: Session) -> None:
        self.db_session = db_session

    def calculate_and_store(
        self,
        symbols: list[str] | None = None,
        base_symbol: str | None = None,
        timeframe: str | None = None,
        created_at: datetime | None = None,
    ) -> list[dict[str, Any]]:
        base = base_symbol or settings.RELATIVE_STRENGTH_BASE_SYMBOL
        timeframe = timeframe or settings.RELATIVE_STRENGTH_TIMEFRAME
        tracked_symbols = symbols or settings.relative_strength_symbols_list
        now = created_at or datetime.now(UTC)
        btc_rows = self._load_ohlcv_rows(base, timeframe, settings.RELATIVE_STRENGTH_LOOKBACK_LIMIT)
        if not btc_rows:
            return []

        btc_metrics = self._calculate_btc_metrics(btc_rows)
        preliminary: list[dict[str, Any]] = []
        for symbol in tracked_symbols:
            if symbol == base:
                continue
            rows = self._load_ohlcv_rows(symbol, timeframe, settings.RELATIVE_STRENGTH_LOOKBACK_LIMIT)
            if not rows:
                continue
            preliminary.append(self._calculate_symbol_metrics(symbol, base, rows, btc_rows, btc_metrics))

        self._apply_brsi_scores(preliminary)
        stored = [self._store_snapshot(snapshot, now) for snapshot in preliminary]
        self.db_session.commit()
        return stored

    def get_latest_ranking(self, limit: int = 100) -> list[dict[str, Any]]:
        snapshots = self.db_session.scalars(
            select(RelativeStrengthSnapshot).order_by(desc(RelativeStrengthSnapshot.created_at))
        ).all()
        latest_by_symbol: dict[str, RelativeStrengthSnapshot] = {}
        for snapshot in snapshots:
            if snapshot.symbol not in latest_by_symbol:
                latest_by_symbol[snapshot.symbol] = snapshot
            if len(latest_by_symbol) >= limit:
                break
        data = [_snapshot_to_dict(snapshot) for snapshot in latest_by_symbol.values()]
        return sorted(
            data,
            key=lambda item: item["brsi_score"] if item["brsi_score"] is not None else -1,
            reverse=True,
        )

    def get_symbol_history(self, symbol: str, limit: int = 500) -> list[dict[str, Any]]:
        rows = self.db_session.scalars(
            select(RelativeStrengthSnapshot)
            .where(RelativeStrengthSnapshot.symbol == symbol)
            .order_by(desc(RelativeStrengthSnapshot.created_at))
            .limit(limit)
        ).all()
        return [_snapshot_to_dict(snapshot) for snapshot in reversed(rows)]

    def _load_ohlcv_rows(self, symbol: str, timeframe: str, limit: int) -> list[dict[str, Any]]:
        rows = self.db_session.scalars(
            select(OHLCV)
            .where(OHLCV.symbol == symbol, OHLCV.timeframe == timeframe)
            .order_by(desc(OHLCV.timestamp))
            .limit(limit)
        ).all()
        return [
            {
                "timestamp": row.timestamp,
                "close": float(row.close),
                "volume": float(row.volume),
            }
            for row in reversed(rows)
        ]

    def _calculate_btc_metrics(self, rows: list[dict[str, Any]]) -> dict[str, float | None]:
        return {
            "btc_price": _safe_float(rows[-1].get("close")),
            "btc_return_1h": calculate_return_pct(rows, LOOKBACK_1H),
            "btc_return_24h": calculate_return_pct(rows, LOOKBACK_24H),
            "btc_return_7d": calculate_return_pct(rows, LOOKBACK_7D),
            "btc_return_30d": calculate_return_pct(rows, LOOKBACK_30D),
        }

    def _calculate_symbol_metrics(
        self,
        symbol: str,
        base_symbol: str,
        rows: list[dict[str, Any]],
        btc_rows: list[dict[str, Any]],
        btc_metrics: dict[str, float | None],
    ) -> dict[str, Any]:
        price = _safe_float(rows[-1].get("close"))
        btc_price = btc_metrics["btc_price"]
        returns = {
            "return_1h": calculate_return_pct(rows, LOOKBACK_1H),
            "return_24h": calculate_return_pct(rows, LOOKBACK_24H),
            "return_7d": calculate_return_pct(rows, LOOKBACK_7D),
            "return_30d": calculate_return_pct(rows, LOOKBACK_30D),
        }
        relative_price = price / btc_price if price is not None and btc_price not in (None, 0) else None
        return {
            "symbol": symbol,
            "base_symbol": base_symbol,
            "price": price,
            "btc_price": btc_price,
            **returns,
            "btc_return_1h": btc_metrics["btc_return_1h"],
            "btc_return_24h": btc_metrics["btc_return_24h"],
            "btc_return_7d": btc_metrics["btc_return_7d"],
            "btc_return_30d": btc_metrics["btc_return_30d"],
            "excess_return_1h": calculate_excess_return(
                returns["return_1h"],
                btc_metrics["btc_return_1h"],
            ),
            "excess_return_24h": calculate_excess_return(
                returns["return_24h"],
                btc_metrics["btc_return_24h"],
            ),
            "excess_return_7d": calculate_excess_return(
                returns["return_7d"],
                btc_metrics["btc_return_7d"],
            ),
            "excess_return_30d": calculate_excess_return(
                returns["return_30d"],
                btc_metrics["btc_return_30d"],
            ),
            "relative_price": relative_price,
            "relative_trend_score": _calculate_relative_trend_score(rows, btc_rows),
            "volume_score": _calculate_volume_score(rows),
        }

    def _apply_brsi_scores(self, snapshots: list[dict[str, Any]]) -> None:
        percentile_fields = (
            "excess_return_24h",
            "excess_return_7d",
            "excess_return_30d",
            "relative_trend_score",
            "volume_score",
        )
        ranks_by_field = {
            field: percentile_ranks({snapshot["symbol"]: snapshot.get(field) for snapshot in snapshots})
            for field in percentile_fields
        }
        for snapshot in snapshots:
            symbol = snapshot["symbol"]
            components = {
                field: ranks_by_field[field].get(symbol)
                for field in percentile_fields
            }
            score = calculate_brsi_score(components)
            snapshot["brsi_score"] = score
            snapshot["status"] = map_brsi_status(score)

    def _store_snapshot(
        self,
        snapshot: dict[str, Any],
        created_at: datetime,
    ) -> dict[str, Any]:
        score = snapshot.get("brsi_score")
        changes = {
            "brsi_change_1h": self._calculate_brsi_change(snapshot["symbol"], score, 1, created_at),
            "brsi_change_4h": self._calculate_brsi_change(snapshot["symbol"], score, 4, created_at),
            "brsi_change_24h": self._calculate_brsi_change(snapshot["symbol"], score, 24, created_at),
        }
        model = RelativeStrengthSnapshot(
            symbol=snapshot["symbol"],
            base_symbol=snapshot["base_symbol"],
            price=_decimal_or_none(snapshot.get("price")),
            btc_price=_decimal_or_none(snapshot.get("btc_price")),
            return_1h=_decimal_or_none(snapshot.get("return_1h")),
            return_24h=_decimal_or_none(snapshot.get("return_24h")),
            return_7d=_decimal_or_none(snapshot.get("return_7d")),
            return_30d=_decimal_or_none(snapshot.get("return_30d")),
            btc_return_1h=_decimal_or_none(snapshot.get("btc_return_1h")),
            btc_return_24h=_decimal_or_none(snapshot.get("btc_return_24h")),
            btc_return_7d=_decimal_or_none(snapshot.get("btc_return_7d")),
            btc_return_30d=_decimal_or_none(snapshot.get("btc_return_30d")),
            excess_return_1h=_decimal_or_none(snapshot.get("excess_return_1h")),
            excess_return_24h=_decimal_or_none(snapshot.get("excess_return_24h")),
            excess_return_7d=_decimal_or_none(snapshot.get("excess_return_7d")),
            excess_return_30d=_decimal_or_none(snapshot.get("excess_return_30d")),
            relative_price=_decimal_or_none(snapshot.get("relative_price")),
            relative_trend_score=_decimal_or_none(snapshot.get("relative_trend_score")),
            volume_score=_decimal_or_none(snapshot.get("volume_score")),
            brsi_score=_decimal_or_none(score),
            brsi_change_1h=_decimal_or_none(changes["brsi_change_1h"]),
            brsi_change_4h=_decimal_or_none(changes["brsi_change_4h"]),
            brsi_change_24h=_decimal_or_none(changes["brsi_change_24h"]),
            status=snapshot["status"],
            created_at=created_at,
        )
        self.db_session.add(model)
        self.db_session.flush()
        return _snapshot_to_dict(model)

    def _calculate_brsi_change(
        self,
        symbol: str,
        current_score: float | None,
        hours: int,
        created_at: datetime,
    ) -> float | None:
        if current_score is None:
            return None
        cutoff = created_at - timedelta(hours=hours)
        previous_score = self.db_session.scalar(
            select(RelativeStrengthSnapshot.brsi_score)
            .where(
                RelativeStrengthSnapshot.symbol == symbol,
                RelativeStrengthSnapshot.created_at <= cutoff,
                RelativeStrengthSnapshot.brsi_score.is_not(None),
            )
            .order_by(desc(RelativeStrengthSnapshot.created_at))
            .limit(1)
        )
        if previous_score is None:
            return None
        return current_score - float(previous_score)


def _calculate_relative_trend_score(
    coin_rows: list[dict[str, Any]],
    btc_rows: list[dict[str, Any]],
) -> float | None:
    if len(coin_rows) <= LOOKBACK_7D or len(btc_rows) <= LOOKBACK_7D:
        return None
    coin_latest = _safe_float(coin_rows[-1].get("close"))
    btc_latest = _safe_float(btc_rows[-1].get("close"))
    coin_previous = _safe_float(coin_rows[-1 - LOOKBACK_7D].get("close"))
    btc_previous = _safe_float(btc_rows[-1 - LOOKBACK_7D].get("close"))
    if None in (coin_latest, btc_latest, coin_previous, btc_previous):
        return None
    if btc_latest == 0 or btc_previous == 0:
        return None
    latest_relative = coin_latest / btc_latest
    previous_relative = coin_previous / btc_previous
    if previous_relative == 0:
        return None
    return ((latest_relative - previous_relative) / previous_relative) * 100


def _calculate_volume_score(rows: list[dict[str, Any]]) -> float | None:
    if len(rows) < LOOKBACK_30D:
        return None
    current_24h_volume = sum(_safe_float(row.get("volume")) or 0 for row in rows[-LOOKBACK_24H:])
    average_daily_volume = sum(_safe_float(row.get("volume")) or 0 for row in rows[-LOOKBACK_30D:]) / 30
    if average_daily_volume <= 0:
        return None
    return (current_24h_volume / average_daily_volume) * 100


def _snapshot_to_dict(snapshot: RelativeStrengthSnapshot) -> dict[str, Any]:
    return {
        "id": snapshot.id,
        "symbol": snapshot.symbol,
        "base_symbol": snapshot.base_symbol,
        "price": _float_or_none(snapshot.price),
        "btc_price": _float_or_none(snapshot.btc_price),
        "return_1h": _float_or_none(snapshot.return_1h),
        "return_24h": _float_or_none(snapshot.return_24h),
        "return_7d": _float_or_none(snapshot.return_7d),
        "return_30d": _float_or_none(snapshot.return_30d),
        "btc_return_1h": _float_or_none(snapshot.btc_return_1h),
        "btc_return_24h": _float_or_none(snapshot.btc_return_24h),
        "btc_return_7d": _float_or_none(snapshot.btc_return_7d),
        "btc_return_30d": _float_or_none(snapshot.btc_return_30d),
        "excess_return_1h": _float_or_none(snapshot.excess_return_1h),
        "excess_return_24h": _float_or_none(snapshot.excess_return_24h),
        "excess_return_7d": _float_or_none(snapshot.excess_return_7d),
        "excess_return_30d": _float_or_none(snapshot.excess_return_30d),
        "relative_price": _float_or_none(snapshot.relative_price),
        "relative_trend_score": _float_or_none(snapshot.relative_trend_score),
        "volume_score": _float_or_none(snapshot.volume_score),
        "brsi_score": _float_or_none(snapshot.brsi_score),
        "brsi_change_1h": _float_or_none(snapshot.brsi_change_1h),
        "brsi_change_4h": _float_or_none(snapshot.brsi_change_4h),
        "brsi_change_24h": _float_or_none(snapshot.brsi_change_24h),
        "status": snapshot.status,
        "created_at": snapshot.created_at.isoformat(),
    }


def _safe_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _float_or_none(value: Any) -> float | None:
    return None if value is None else float(value)


def _decimal_or_none(value: Any) -> Decimal | None:
    return None if value is None else Decimal(str(value))
