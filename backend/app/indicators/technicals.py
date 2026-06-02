import numpy as np
import pandas as pd

REQUIRED_COLUMNS = ("timestamp", "open", "high", "low", "close", "volume")


def _prepare_df(df: pd.DataFrame) -> pd.DataFrame:
    prepared = df.copy()
    for column in REQUIRED_COLUMNS:
        if column not in prepared.columns:
            prepared[column] = np.nan

    prepared["timestamp"] = pd.to_datetime(prepared["timestamp"], errors="coerce")
    prepared = prepared.sort_values("timestamp", ascending=True).reset_index(drop=True)
    for column in ("open", "high", "low", "close", "volume"):
        prepared[column] = pd.to_numeric(prepared[column], errors="coerce").astype(float)
    return prepared


def add_ema(df: pd.DataFrame, periods: list[int]) -> pd.DataFrame:
    result = _prepare_df(df)
    for period in periods:
        result[f"ema_{period}"] = (
            result["close"].ewm(span=period, adjust=False, min_periods=period).mean()
        ).astype(float)
    return result


def add_rsi(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    result = _prepare_df(df)
    delta = result["close"].diff()
    gains = delta.clip(lower=0)
    losses = -delta.clip(upper=0)
    avg_gain = gains.rolling(window=period, min_periods=period).mean()
    avg_loss = losses.rolling(window=period, min_periods=period).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    rsi = rsi.where(avg_loss != 0, 100.0)
    result[f"rsi_{period}"] = rsi.clip(0, 100).astype(float)
    return result


def add_macd(
    df: pd.DataFrame,
    fast: int = 12,
    slow: int = 26,
    signal: int = 9,
) -> pd.DataFrame:
    result = _prepare_df(df)
    ema_fast = result["close"].ewm(span=fast, adjust=False, min_periods=fast).mean()
    ema_slow = result["close"].ewm(span=slow, adjust=False, min_periods=slow).mean()
    result["macd"] = (ema_fast - ema_slow).astype(float)
    result["macd_signal"] = (
        result["macd"].ewm(span=signal, adjust=False, min_periods=signal).mean()
    ).astype(float)
    result["macd_histogram"] = (result["macd"] - result["macd_signal"]).astype(float)
    return result


def add_atr(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    result = _prepare_df(df)
    previous_close = result["close"].shift(1)
    high_low = result["high"] - result["low"]
    high_close = (result["high"] - previous_close).abs()
    low_close = (result["low"] - previous_close).abs()
    true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    result[f"atr_{period}"] = (
        true_range.rolling(window=period, min_periods=period).mean()
    ).astype(float)
    return result


def add_volume_zscore(df: pd.DataFrame, period: int = 20) -> pd.DataFrame:
    result = _prepare_df(df)
    rolling_mean = result["volume"].rolling(window=period, min_periods=period).mean()
    rolling_std = result["volume"].rolling(window=period, min_periods=period).std()
    result[f"volume_zscore_{period}"] = (
        (result["volume"] - rolling_mean) / rolling_std.replace(0, np.nan)
    ).astype(float)
    return result


def add_realized_volatility(df: pd.DataFrame, period: int = 20) -> pd.DataFrame:
    result = _prepare_df(df)
    returns = result["close"].pct_change()
    result[f"realized_volatility_{period}"] = (
        returns.rolling(window=period, min_periods=period).std() * np.sqrt(period)
    ).astype(float)
    return result


def add_rolling_high_low(df: pd.DataFrame, period: int = 20) -> pd.DataFrame:
    result = _prepare_df(df)
    result[f"rolling_high_{period}"] = (
        result["high"].rolling(window=period, min_periods=period).max()
    ).astype(float)
    result[f"rolling_low_{period}"] = (
        result["low"].rolling(window=period, min_periods=period).min()
    ).astype(float)
    return result


def add_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
    result = _prepare_df(df)
    result = add_ema(result, [20, 50, 200])
    result = add_rsi(result, 14)
    result = add_macd(result)
    result = add_atr(result, 14)
    result = add_volume_zscore(result, 20)
    result = add_realized_volatility(result, 20)
    result = add_rolling_high_low(result, 20)
    return result
