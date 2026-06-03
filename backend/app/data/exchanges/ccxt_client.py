import logging
from datetime import UTC, datetime
from typing import Any

import ccxt
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


class MarketDataError(Exception):
    """Base exception for market data client errors."""


class UnsupportedExchangeError(MarketDataError):
    """Raised when a requested exchange is not available in CCXT."""


class UnsupportedOHLCVError(MarketDataError):
    """Raised when an exchange does not support OHLCV data."""


class SymbolNotFoundError(MarketDataError):
    """Raised when a symbol is not listed on the requested exchange."""


class MarketDataAPIError(MarketDataError):
    """Raised when an exchange API call fails."""


TemporaryCCXTError = (
    ccxt.NetworkError,
    ccxt.ExchangeNotAvailable,
    ccxt.RequestTimeout,
    ccxt.DDoSProtection,
    ccxt.RateLimitExceeded,
)


class CCXTMarketClient:
    def __init__(self, exchange_id: str) -> None:
        self.exchange_id = exchange_id.lower().strip()
        exchange_class = getattr(ccxt, self.exchange_id, None)
        if exchange_class is None:
            raise UnsupportedExchangeError(f"Unsupported exchange: {exchange_id}")

        self.exchange = exchange_class({"enableRateLimit": True})

    def load_markets(self) -> dict[str, Any]:
        try:
            markets = self._load_markets_with_retry()
        except TemporaryCCXTError as exc:
            logger.warning("Temporary exchange error while loading markets: %s", exc)
            raise MarketDataAPIError(self._exchange_error_message(exc, "loading markets")) from exc
        except ccxt.BaseError as exc:
            logger.exception("Exchange error while loading markets")
            raise MarketDataAPIError("Exchange error while loading markets") from exc

        return markets

    @retry(
        retry=retry_if_exception_type(TemporaryCCXTError),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        stop=stop_after_attempt(3),
        reraise=True,
    )
    def _load_markets_with_retry(self) -> dict[str, Any]:
        return self.exchange.load_markets()

    def fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str,
        limit: int = 200,
        since: datetime | None = None,
    ) -> list[dict[str, Any]]:
        if not self.exchange.has.get("fetchOHLCV"):
            raise UnsupportedOHLCVError(
                f"Exchange {self.exchange_id} does not support fetchOHLCV"
            )

        markets = self.load_markets()
        if symbol not in markets:
            raise SymbolNotFoundError(
                f"Symbol {symbol} was not found on {self.exchange_id}"
            )

        try:
            rows = self._fetch_ohlcv_with_retry(symbol, timeframe, limit, since)
        except ccxt.BadSymbol as exc:
            raise SymbolNotFoundError(
                f"Symbol {symbol} was not found on {self.exchange_id}"
            ) from exc
        except TemporaryCCXTError as exc:
            logger.warning("Temporary exchange error while fetching OHLCV: %s", exc)
            raise MarketDataAPIError(self._exchange_error_message(exc, "fetching OHLCV")) from exc
        except ccxt.BaseError as exc:
            logger.exception("Exchange error while fetching OHLCV")
            raise MarketDataAPIError("Exchange error while fetching OHLCV") from exc

        return [
            self._normalize_ohlcv_row(symbol=symbol, timeframe=timeframe, row=row)
            for row in rows
        ]

    @retry(
        retry=retry_if_exception_type(TemporaryCCXTError),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        stop=stop_after_attempt(3),
        reraise=True,
    )
    def _fetch_ohlcv_with_retry(
        self,
        symbol: str,
        timeframe: str,
        limit: int,
        since: datetime | None = None,
    ) -> list[list[float]]:
        since_ms = int(since.timestamp() * 1000) if since is not None else None
        return self.exchange.fetch_ohlcv(
            symbol,
            timeframe=timeframe,
            since=since_ms,
            limit=limit,
        )

    def timeframe_to_milliseconds(self, timeframe: str) -> int:
        try:
            return int(self.exchange.parse_timeframe(timeframe) * 1000)
        except Exception as exc:
            raise MarketDataAPIError(f"Unsupported timeframe: {timeframe}") from exc

    def _normalize_ohlcv_row(
        self,
        symbol: str,
        timeframe: str,
        row: list[float],
    ) -> dict[str, Any]:
        timestamp_ms, open_, high, low, close, volume = row
        timestamp = datetime.fromtimestamp(timestamp_ms / 1000, tz=UTC)
        return {
            "exchange": self.exchange_id,
            "symbol": symbol,
            "timeframe": timeframe,
            "timestamp": timestamp,
            "open": float(open_),
            "high": float(high),
            "low": float(low),
            "close": float(close),
            "volume": float(volume),
        }

    def _exchange_error_message(self, exc: Exception, action: str) -> str:
        message = str(exc)
        if "restricted location" in message.lower() or "451" in message:
            return (
                f"Exchange {self.exchange_id} is unavailable from the current network "
                f"or location while {action}. Choose another public exchange such as "
                "okx, kraken, coinbase, kucoin, or bitget."
            )
        return f"Temporary exchange error while {action}"
