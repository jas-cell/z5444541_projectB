"""Look-ahead-safe sentiment tilts."""
from __future__ import annotations

import numpy as np
import pandas as pd

from src.portfolios import performance_metrics, project_capped_simplex, simulate_weight_path


def _tilt_group(
    group: pd.DataFrame,
    *,
    tilt_strength: float,
    max_weight: float,
) -> pd.Series:
    scores = group["tradable_score"] - group["tradable_score"].mean()
    multiplier = np.exp(tilt_strength * scores.clip(-1, 1))
    tilted = group["weight"].to_numpy() * multiplier.to_numpy()
    tilted = project_capped_simplex(tilted, max_weight=max_weight)
    return pd.Series(tilted, index=group.index)


def apply_sentiment(
    weights: pd.DataFrame,
    returns: pd.DataFrame,
    sentiment_signal: pd.DataFrame,
    *,
    base_family: str = "Equity",
    base_method: str = "Minimum Variance",
    tilt_strength: float = 0.35,
    max_weight: float = 0.30,
    cost_bps: float = 0.0,
) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """Tilt rebalance *decision* weights using lagged tradable sentiment scores."""

    base = weights.loc[(weights["family"].eq(base_family)) & (weights["method"].eq(base_method))].copy()
    if base.empty:
        raise ValueError("base weights for sentiment tilt not found")
    signals = sentiment_signal.rename(columns={"trade_date": "date"})
    score_col = "tradable_score" if "tradable_score" in signals.columns else "sentiment_lag1"
    base = base.merge(
        signals[["date", "ticker", score_col]].rename(columns={score_col: "tradable_score"}),
        on=["date", "ticker"],
        how="left",
    )
    base["tradable_score"] = base["tradable_score"].fillna(0.0)
    method_name = f"{base_method} + Context-Weighted Sentiment"

    tilted_rows = []
    for _, group in base.groupby("date", observed=True):
        tmp = group.copy()
        tmp["weight"] = _tilt_group(tmp, tilt_strength=tilt_strength, max_weight=max_weight).to_numpy()
        # Cap enforcement check: after projection every weight must respect the cap.
        if tmp["weight"].max() > max_weight + 1e-8:
            raise RuntimeError("sentiment tilt breached max_weight after projection")
        tmp["family"] = base_family
        tmp["method"] = method_name
        tilted_rows.append(tmp[["date", "family", "method", "ticker", "weight"]])
    tilted_weights = pd.concat(tilted_rows, ignore_index=True)

    fund_returns, decision_weights, metrics = simulate_weight_path(
        returns.sort_index(),
        tilted_weights,
        family=base_family,
        method=method_name,
        periods_per_year=252,
        cost_bps=cost_bps,
    )
    metrics.update({
        "family": base_family,
        "method": method_name,
        "fund": f"{base_family} - {method_name}",
        "estimation_window": "same as base",
        "tilt_strength": tilt_strength,
        "max_weight": max_weight,
        "base_method": base_method,
        "execution_timing": (
            "decision targets tilted on rebalance dates using lagged tradable_score; "
            "new weights earn from the next session; holdings drift between rebalances"
        ),
    })
    return fund_returns, decision_weights, metrics


def fusion_sensitivity(
    weights: pd.DataFrame,
    returns: pd.DataFrame,
    sentiment_signal: pd.DataFrame,
    *,
    base_family: str = "Equity",
    base_methods: tuple[str, ...] = ("Minimum Variance", "Risk Parity", "Equal Weight"),
    tilt_strengths: tuple[float, ...] = (0.15, 0.35, 0.60),
    max_weight: float = 0.30,
    cost_bps_grid: tuple[float, ...] = (0.0, 5.0, 10.0),
) -> pd.DataFrame:
    """Evaluate lagged sentiment tilts across bases, strengths, and simple cost assumptions."""

    rows: list[dict] = []
    for base_method in base_methods:
        base = weights.loc[(weights["family"].eq(base_family)) & (weights["method"].eq(base_method))]
        if base.empty:
            continue
        for tilt_strength in tilt_strengths:
            for cost_bps in cost_bps_grid:
                fund_returns, _, metrics = apply_sentiment(
                    weights,
                    returns,
                    sentiment_signal,
                    base_family=base_family,
                    base_method=base_method,
                    tilt_strength=tilt_strength,
                    max_weight=max_weight,
                    cost_bps=cost_bps,
                )
                rows.append({
                    "base_method": base_method,
                    "tilt_strength": tilt_strength,
                    "cost_bps": cost_bps,
                    "observations": int(len(fund_returns)),
                    "annualised_return": metrics["annualised_return"],
                    "annualised_volatility": metrics["annualised_volatility"],
                    "sharpe": metrics["sharpe"],
                    "max_drawdown": metrics["max_drawdown"],
                    "terminal_growth": metrics["terminal_growth"],
                    "avg_annual_turnover": metrics.get("avg_annual_turnover", np.nan),
                })
    return (
        pd.DataFrame(rows)
        .sort_values(["cost_bps", "sharpe", "annualised_return"], ascending=[True, False, False])
        .reset_index(drop=True)
    )


def turnover_cost_table(
    weights: pd.DataFrame,
    returns: pd.DataFrame,
    sentiment_signal: pd.DataFrame,
    *,
    base_family: str = "Equity",
    base_method: str = "Minimum Variance",
    tilt_strength: float = 0.35,
    cost_bps_grid: tuple[float, ...] = (0.0, 5.0, 10.0, 25.0),
) -> pd.DataFrame:
    """Compare base and fusion under the same per-turnover cost assumptions."""

    base = weights.loc[
        (weights["family"].eq(base_family)) & (weights["method"].eq(base_method))
    ][["date", "family", "method", "ticker", "weight"]].copy()
    rows = []
    for cost_bps in cost_bps_grid:
        _, _, base_metrics = simulate_weight_path(
            returns.sort_index(),
            base,
            family=base_family,
            method=base_method,
            periods_per_year=252,
            cost_bps=cost_bps,
        )
        fund_returns, _, tilt_metrics = apply_sentiment(
            weights,
            returns,
            sentiment_signal,
            base_family=base_family,
            base_method=base_method,
            tilt_strength=tilt_strength,
            cost_bps=cost_bps,
        )
        for label, metrics in [("base", base_metrics), ("fusion", tilt_metrics)]:
            rows.append({
                "sleeve": label,
                "fund": metrics["fund"],
                "cost_bps": cost_bps,
                "sharpe": metrics["sharpe"],
                "annualised_return": metrics["annualised_return"],
                "terminal_growth": round(float(metrics["terminal_growth"]), 6),
                "max_drawdown": metrics["max_drawdown"],
                "avg_annual_turnover": metrics.get("avg_annual_turnover", np.nan),
                "observations": int(metrics.get("observations", len(fund_returns))),
            })
    return pd.DataFrame(rows)
