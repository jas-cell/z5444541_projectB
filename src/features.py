"""Station 2 foundations used by the Part B models."""
from __future__ import annotations

import numpy as np
import pandas as pd

from src.etl import normalise_date


def add_attention_pulse(
    panel: pd.DataFrame,
    *,
    window: int = 60,
    min_periods: int = 20,
) -> pd.DataFrame:
    """Part A Attention Pulse: past-only robust abnormal headline volume.

    Pulse = [log(1 + current articles) - trailing median] / scaled trailing MAD.
    The baseline is shifted by one day. Identical equation to Project A.
    """

    out = panel.copy().sort_values(["ticker", "trade_date"], kind="stable")
    out["log_article_count"] = np.log1p(out["article_count"].astype(float))

    def trailing_components(series: pd.Series) -> pd.DataFrame:
        history = series.shift(1)
        rolling = history.rolling(window, min_periods=min_periods)
        median = rolling.median()
        mad = rolling.apply(
            lambda values: np.median(np.abs(values - np.median(values))), raw=True
        ) / 0.6745
        iqr = (rolling.quantile(0.75) - rolling.quantile(0.25)) / 1.349
        scale = mad.mask(mad.le(1e-12), iqr).mask(lambda x: x.le(1e-12))
        return pd.DataFrame({"attention_baseline": median, "attention_scale": scale})

    components = (
        out.groupby("ticker", observed=True, group_keys=False)["log_article_count"]
        .apply(trailing_components)
        .reset_index(level=0, drop=True)
        .sort_index()
    )
    out[["attention_baseline", "attention_scale"]] = components
    out["attention_pulse"] = (
        out["log_article_count"] - out["attention_baseline"]
    ) / out["attention_scale"]
    return out.reset_index(drop=True)


def daily_returns(prices: pd.DataFrame, price_col: str = "adjClose") -> pd.DataFrame:
    required = {"ticker", "date", price_col}
    missing = sorted(required - set(prices.columns))
    if missing:
        raise ValueError(f"prices missing columns required for returns: {missing}")
    if prices.duplicated(["ticker", "date"]).any():
        raise ValueError("returns require unique ticker-date observations")
    out = prices.copy().sort_values(["ticker", "date"], kind="stable")
    out["simple_return"] = out.groupby("ticker", observed=True)[price_col].pct_change(fill_method=None)
    return out.reset_index(drop=True)


def returns_wide(returns: pd.DataFrame) -> pd.DataFrame:
    return returns.pivot(index="date", columns="ticker", values="simple_return").sort_index()


def align_returns_to_calendar(returns: pd.DataFrame, trading_calendar: pd.Series | pd.DatetimeIndex) -> pd.DataFrame:
    calendar = pd.DatetimeIndex(pd.to_datetime(trading_calendar)).drop_duplicates().sort_values()
    tickers = pd.Index(returns["ticker"].drop_duplicates().sort_values())
    grid = pd.MultiIndex.from_product([tickers, calendar], names=["ticker", "date"]).to_frame(index=False)
    return grid.merge(returns, on=["ticker", "date"], how="left", validate="one_to_one")


def map_headlines_to_trading_days(
    headlines: pd.DataFrame, trading_calendar: pd.Series | pd.DatetimeIndex
) -> pd.DataFrame:
    calendar = pd.DatetimeIndex(pd.to_datetime(trading_calendar)).drop_duplicates().sort_values()
    out = headlines.copy()
    out["date"] = normalise_date(out["date"])
    positions = calendar.searchsorted(out["date"].to_numpy(dtype="datetime64[ns]"), side="left")
    valid = positions < len(calendar)
    mapped = np.full(len(out), np.datetime64("NaT", "ns"), dtype="datetime64[ns]")
    mapped[valid] = calendar.to_numpy(dtype="datetime64[ns]")[positions[valid]]
    out["trade_date"] = pd.to_datetime(mapped)
    out["mapping_lag_days"] = (out["trade_date"] - out["date"]).dt.days.astype("Int64")
    return out


def assemble_headline_panel(
    headlines: pd.DataFrame,
    trading_calendar: pd.Series | pd.DatetimeIndex,
    sector_map: pd.DataFrame | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    mapped = map_headlines_to_trading_days(headlines, trading_calendar)
    valid = mapped.loc[mapped["trade_date"].notna()].copy()
    grouped = valid.groupby(["trade_date", "ticker", "sector"], observed=True).agg(
        article_count=("title", "size"),
        headline_text=("title", lambda values: " || ".join(values.astype(str))),
        first_publication_date=("date", "min"),
        last_publication_date=("date", "max"),
        max_mapping_lag_days=("mapping_lag_days", "max"),
    ).reset_index()
    calendar = pd.DatetimeIndex(pd.to_datetime(trading_calendar)).drop_duplicates().sort_values()
    if sector_map is None:
        sector_map = valid[["ticker", "sector"]].drop_duplicates()
    mapping = sector_map[["ticker", "sector"]].drop_duplicates().sort_values("ticker")
    grid = pd.MultiIndex.from_product([calendar, mapping["ticker"]], names=["trade_date", "ticker"]).to_frame(index=False)
    grid = grid.merge(mapping, on="ticker", how="left", validate="many_to_one")
    panel = grid.merge(grouped, on=["trade_date", "ticker", "sector"], how="left", validate="one_to_one")
    panel["article_count"] = panel["article_count"].fillna(0).astype("int64")
    panel["max_mapping_lag_days"] = panel["max_mapping_lag_days"].fillna(0).astype("int64")
    panel["headline_text"] = panel["headline_text"].fillna("")
    return panel.sort_values(["ticker", "trade_date"]).reset_index(drop=True), mapped
