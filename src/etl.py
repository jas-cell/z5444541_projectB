"""Station 1 foundations reused for Part B."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np
import pandas as pd

from src import data_access


END_DATE = pd.Timestamp("2023-12-31")
PRICE_COLUMNS = {"ticker", "date", "open", "high", "low", "close", "adjClose", "volume"}
NEWS_COLUMNS = {"date", "ticker", "sector", "title", "url", "publisher"}


@dataclass(frozen=True)
class CleanData:
    equities: pd.DataFrame
    crypto: pd.DataFrame
    news: pd.DataFrame


def normalise_date(values: pd.Series) -> pd.Series:
    return pd.to_datetime(values, utc=True).dt.tz_convert(None).dt.normalize()


def _require_columns(frame: pd.DataFrame, required: Iterable[str], name: str) -> None:
    missing = sorted(set(required) - set(frame.columns))
    if missing:
        raise ValueError(f"{name} missing required columns: {missing}")


def clean_price_panel(prices: pd.DataFrame, *, name: str, end_date: pd.Timestamp | None = None) -> pd.DataFrame:
    _require_columns(prices, PRICE_COLUMNS, name)
    out = prices.copy()
    out["date"] = normalise_date(out["date"])
    out["ticker"] = out["ticker"].astype("string").str.strip()
    if end_date is not None:
        out = out.loc[out["date"].le(end_date)].copy()
    out = out.drop_duplicates(["ticker", "date"], keep="first")
    numeric = ["open", "high", "low", "close", "adjClose", "volume"]
    if out[numeric].isna().any().any() or not np.isfinite(out[numeric].astype(float)).all().all():
        raise ValueError(f"{name} contains missing or non-finite OHLCV values")
    if out[["open", "high", "low", "close", "adjClose"]].le(0).any().any():
        raise ValueError(f"{name} contains non-positive prices")
    if out["volume"].lt(0).any():
        raise ValueError(f"{name} contains negative volume")
    bad_ohlc = out["high"].lt(out[["open", "close", "low"]].max(axis=1)) | out["low"].gt(
        out[["open", "close", "high"]].min(axis=1)
    )
    if bad_ohlc.any():
        raise ValueError(f"{name} contains {int(bad_ohlc.sum())} OHLC-inconsistent rows")
    return out.sort_values(["ticker", "date"], kind="stable").reset_index(drop=True)


def clean_headlines(headlines: pd.DataFrame) -> pd.DataFrame:
    _require_columns(headlines, NEWS_COLUMNS, "news_headlines")
    out = headlines.copy()
    out["date"] = normalise_date(out["date"])
    for col in ["ticker", "sector", "title", "url", "publisher"]:
        out[col] = out[col].astype("string").str.strip()
    invalid = out[["date", "ticker", "sector", "title"]].isna().any(axis=1) | out["title"].eq("")
    if invalid.any():
        raise ValueError(f"news_headlines contains {int(invalid.sum())} invalid core rows")
    return out.drop_duplicates(["ticker", "date", "title"], keep="first").sort_values(
        ["date", "ticker", "title"], kind="stable"
    ).reset_index(drop=True)


def load_all_clean() -> CleanData:
    return CleanData(
        equities=clean_price_panel(data_access.load_equity_prices(), name="equity_prices"),
        crypto=clean_price_panel(data_access.load_crypto_prices(), name="crypto_prices", end_date=END_DATE),
        news=clean_headlines(data_access.load_news_headlines()),
    )


def load_clean_equities() -> pd.DataFrame:
    return load_all_clean().equities


def load_clean_crypto() -> pd.DataFrame:
    return load_all_clean().crypto
