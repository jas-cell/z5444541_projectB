"""Walk-forward systematic funds for Project B."""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.optimize import minimize


METHOD_LABELS = {
    "equal_weight": "Equal Weight",
    "min_variance": "Minimum Variance",
    "max_sharpe": "Maximum Sharpe",
    "risk_parity": "Risk Parity",
}

# Numerical floor: daily variances are tiny; objectives are evaluated on an annualised scale.
_ANNUALISE = 252.0


def _clean_window(window: pd.DataFrame) -> pd.DataFrame:
    keep = window.columns[window.notna().mean().ge(0.90)]
    cleaned = window[keep].fillna(0.0)
    return cleaned.loc[:, cleaned.std(ddof=1).gt(1e-8)]


def _cov(window: pd.DataFrame) -> np.ndarray:
    cov = window.cov().to_numpy()
    return cov + np.eye(cov.shape[0]) * 1e-8


def project_capped_simplex(weights: np.ndarray, max_weight: float) -> np.ndarray:
    """Project onto {w >= 0, sum w = 1, w_i <= max_weight} by freezing capped coordinates."""

    w = np.maximum(np.asarray(weights, dtype=float), 0.0)
    n = len(w)
    if n == 0:
        return w
    cap = min(float(max_weight), 1.0)
    if cap * n < 1.0 - 1e-12:
        return np.full(n, 1.0 / n)
    if w.sum() <= 0:
        return np.full(n, 1.0 / n)
    free = np.ones(n, dtype=bool)
    for _ in range(n + 3):
        capped_n = int((~free).sum())
        remainder = 1.0 - cap * capped_n
        if remainder < -1e-12:
            return np.full(n, 1.0 / n)
        if not free.any():
            break
        mass = float(w[free].sum())
        if mass <= 0:
            w[free] = remainder / free.sum()
        else:
            w[free] = remainder * (w[free] / mass)
        w[~free] = cap
        viol = free & (w > cap + 1e-12)
        if not viol.any():
            w = np.maximum(w, 0.0)
            return w / w.sum()
        free[viol] = False
    w = np.maximum(w, 0.0)
    return w / w.sum()


def _solve_weights(
    window: pd.DataFrame,
    method: str,
    *,
    long_only: bool = True,
    max_weight: float = 0.25,
    periods_per_year: int = 252,
) -> pd.Series:
    window = _clean_window(window)
    n = len(window.columns)
    if n == 0:
        raise ValueError("no usable assets in estimation window")
    if method == "equal_weight":
        return pd.Series(np.full(n, 1.0 / n), index=window.columns)

    mu = window.mean().to_numpy()
    sigma = _cov(window)
    # Annualise mean/covariance so SLSQP does not stall on 1e-4 daily variances.
    scale = float(periods_per_year)
    mu_ann = mu * scale
    sigma_ann = sigma * scale
    if long_only:
        bounds = [(0.0, max_weight)] * n
    else:
        bounds = [(-max_weight, max_weight)] * n
    constraints = [{"type": "eq", "fun": lambda w: np.sum(w) - 1.0}]
    x0 = np.full(n, 1.0 / n)

    if method == "min_variance":
        objective = lambda w: float(w @ sigma_ann @ w)
    elif method == "max_sharpe":
        # Zero risk-free conventional Sharpe on the annualised moments.
        objective = lambda w: -float((w @ mu_ann) / max(np.sqrt(w @ sigma_ann @ w), 1e-12))
    elif method == "risk_parity":
        def objective(w: np.ndarray) -> float:
            port_var = float(w @ sigma_ann @ w)
            marginal = sigma_ann @ w
            contribution = w * marginal / max(port_var, 1e-12)
            return float(((contribution - 1.0 / n) ** 2).sum())
    else:
        raise ValueError(f"unknown optimisation method: {method}")

    result = minimize(
        objective,
        x0,
        method="SLSQP",
        bounds=bounds,
        constraints=constraints,
        options={"maxiter": 800, "ftol": 1e-12, "disp": False},
    )
    eq_obj = float(objective(x0))
    if (
        (not result.success)
        or (not np.isfinite(result.x).all())
        or (float(objective(result.x)) > eq_obj - 1e-12)
    ):
        # No measurable improvement over equal weight: keep the equal-weight fallback.
        weights = x0.copy()
    else:
        weights = np.asarray(result.x, dtype=float)
    if long_only:
        weights = project_capped_simplex(weights, max_weight=max_weight)
    else:
        weights = weights / weights.sum()
    return pd.Series(weights, index=window.columns)


def rebalance_dates(
    index: pd.DatetimeIndex,
    estimation_window: int,
    frequency: str = "ME",
) -> pd.DatetimeIndex:
    """First live session of each period after the estimation warm-up.

    ``frequency`` accepts pandas period/offset aliases. Month-end style codes
    (``M``, ``ME``, ``month``) select the first observation in each calendar month
    of the live sample — the decision date for that month's rebalance.
    """

    live = index[estimation_window:]
    if live.empty:
        raise ValueError("not enough observations for the requested estimation window")
    freq = frequency.upper()
    if freq in {"M", "ME", "MONTH", "MONTHLY", "1M"}:
        period_freq = "M"
    elif freq in {"W", "WE", "WEEK", "WEEKLY", "1W"}:
        period_freq = "W"
    else:
        period_freq = frequency
    chosen = pd.Series(live, index=live).groupby(pd.PeriodIndex(live, freq=period_freq)).first()
    return pd.DatetimeIndex(pd.to_datetime(chosen.to_numpy()))


def performance_metrics(daily_returns: pd.Series, periods_per_year: int = 252) -> dict:
    """Fact-sheet metrics. Sharpe is the conventional zero-rf sample Sharpe.

    ``annualised_return`` remains CAGR (growth-of-one path). ``sharpe`` uses
    arithmetic mean return / volatility, both annualised — the same ratio the
    Maximum Sharpe optimiser targets.
    """

    r = pd.Series(daily_returns).dropna().astype(float)
    if r.empty:
        return {
            "observations": 0,
            "annualised_return": float("nan"),
            "annualised_volatility": float("nan"),
            "sharpe": float("nan"),
            "max_drawdown": float("nan"),
            "terminal_growth": float("nan"),
            "avg_annual_turnover": float("nan"),
        }
    # Prepend wealth = 1 so a negative first return creates a non-zero drawdown.
    growth = pd.concat([pd.Series([1.0]), (1.0 + r).cumprod()], ignore_index=True)
    years = len(r) / periods_per_year
    ann_return = float(growth.iloc[-1] ** (1.0 / years) - 1.0) if years > 0 else float("nan")
    ann_vol = float(r.std(ddof=1) * np.sqrt(periods_per_year))
    ann_mean = float(r.mean() * periods_per_year)
    sharpe = ann_mean / ann_vol if ann_vol and ann_vol > 0 else float("nan")
    drawdown = growth / growth.cummax() - 1.0
    return {
        "observations": int(len(r)),
        "annualised_return": ann_return,
        "annualised_volatility": ann_vol,
        "sharpe": float(sharpe),
        "max_drawdown": float(drawdown.min()),
        "terminal_growth": float(growth.iloc[-1]),
    }


def simulate_weight_path(
    wide: pd.DataFrame,
    target_weights: pd.DataFrame,
    *,
    family: str,
    method: str,
    periods_per_year: int = 252,
    cost_bps: float = 0.0,
) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """Apply decision-date targets with next-session effectiveness and intra-month drift.

    Timing convention
    -----------------
    On a rebalance *decision* date ``T``, target weights are formed from returns
    strictly before ``T``. The close-to-close return on ``T`` still uses the prior
    holdings. New targets become effective at the open of the next session, then
    holdings drift with relative asset performance until the next rebalance.
    """

    wide = wide.sort_index()
    dates = list(wide.index)
    targets = {
        pd.Timestamp(date): group.set_index("ticker")["weight"].astype(float)
        for date, group in target_weights.groupby("date", sort=True)
    }
    decision_dates = set(targets)
    daily_rows: list[dict] = []
    held_rows: list[dict] = []
    turnover_events: list[float] = []
    current: pd.Series | None = None
    pending: pd.Series | None = None

    for date in dates:
        ts = pd.Timestamp(date)
        session_turnover = 0.0

        # New targets decided on a prior session become effective today.
        if pending is not None:
            if current is None:
                session_turnover = 0.5 * float(pending.abs().sum())  # from cash/flat
            else:
                idx = sorted(set(current.index).union(set(pending.index)))
                prior = current.reindex(idx).fillna(0.0)
                traded = pending.reindex(idx).fillna(0.0)
                session_turnover = 0.5 * float((traded - prior).abs().sum())
            current = pending / pending.sum()
            pending = None
            turnover_events.append(session_turnover)
            for ticker, weight in current.items():
                held_rows.append({
                    "date": ts,
                    "family": family,
                    "method": method,
                    "ticker": ticker,
                    "weight": float(weight),
                    "weight_kind": "effective",
                })

        if ts in decision_dates:
            pending = targets[ts].copy()
            pending = pending[pending > 0]
            if pending.sum() > 0:
                pending = pending / pending.sum()
            for ticker, weight in targets[ts].items():
                held_rows.append({
                    "date": ts,
                    "family": family,
                    "method": method,
                    "ticker": ticker,
                    "weight": float(weight),
                    "weight_kind": "decision_target",
                })

        if current is None:
            continue

        asset_rets = wide.loc[ts, current.index].astype(float).fillna(0.0)
        gross = float(asset_rets @ current)
        cost = session_turnover * (cost_bps / 10_000.0)
        daily_rows.append({
            "date": ts,
            "family": family,
            "method": method,
            "return": gross - cost,
        })

        # Always drift through the decision-day return. Next-session turnover then
        # compares the new target against post-return holdings, not stale pre-return weights.
        drifted = current * (1.0 + asset_rets.reindex(current.index).fillna(0.0))
        total = float(drifted.sum())
        if total > 0:
            current = drifted / total

    fund_returns = pd.DataFrame(daily_rows)
    if fund_returns.empty:
        raise ValueError(f"no fund returns produced for {family} {method}")
    fund_returns["fund"] = fund_returns["family"] + " - " + fund_returns["method"]
    wealth = pd.concat(
        [pd.Series([1.0]), (1.0 + fund_returns["return"]).cumprod()],
        ignore_index=True,
    )
    fund_returns["growth"] = wealth.iloc[1:].to_numpy()
    fund_returns["drawdown"] = (wealth / wealth.cummax() - 1.0).iloc[1:].to_numpy()

    weights = pd.DataFrame(held_rows)
    if weights.empty:
        raise ValueError(f"no weights produced for {family} {method}")
    # Public weight panel used by fusion / app: decision targets (sum to 1 on decision dates).
    decision_weights = weights.loc[weights["weight_kind"].eq("decision_target")].drop(
        columns=["weight_kind"]
    )
    metrics = performance_metrics(fund_returns["return"], periods_per_year=periods_per_year)
    years = max(len(fund_returns) / periods_per_year, 1e-12)
    metrics["avg_annual_turnover"] = float(sum(turnover_events) / years) if turnover_events else 0.0
    metrics.update({
        "family": family,
        "method": method,
        "fund": f"{family} - {method}",
        "first_live_date": pd.Timestamp(fund_returns["date"].min()).date().isoformat(),
        "periods_per_year": periods_per_year,
    })
    return fund_returns, decision_weights, metrics


def oos_backtest(
    returns: pd.DataFrame,
    *,
    family: str,
    method: str = "min_variance",
    estimation_window: int = 252,
    periods_per_year: int = 252,
    max_weight: float = 0.25,
    frequency: str = "ME",
    cost_bps: float = 0.0,
) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """Monthly walk-forward backtest with drifting holdings and next-day effectiveness."""

    wide = returns.sort_index().copy()
    dates = wide.index
    rebalances = rebalance_dates(dates, estimation_window, frequency=frequency)
    weight_rows: list[dict] = []

    for date in rebalances:
        i = dates.get_loc(date)
        if isinstance(i, slice):
            i = i.start
        history = wide.iloc[i - estimation_window:i]
        solved = _solve_weights(
            history,
            method,
            max_weight=max_weight,
            periods_per_year=periods_per_year,
        )
        for ticker, weight in solved.items():
            weight_rows.append({
                "date": pd.Timestamp(date),
                "family": family,
                "method": METHOD_LABELS[method],
                "ticker": ticker,
                "weight": float(weight),
            })

    targets = pd.DataFrame(weight_rows)
    fund_returns, decision_weights, metrics = simulate_weight_path(
        wide,
        targets,
        family=family,
        method=METHOD_LABELS[method],
        periods_per_year=periods_per_year,
        cost_bps=cost_bps,
    )
    metrics["estimation_window"] = estimation_window
    metrics["rebalance_frequency"] = frequency
    metrics["execution_timing"] = (
        "decision at rebalance date using past returns only; "
        "new weights earn from the next session; holdings drift between rebalances"
    )
    return fund_returns, decision_weights, metrics


def method_weight_divergence(
    weights: pd.DataFrame,
    *,
    family: str,
    method_a: str,
    method_b: str,
) -> pd.DataFrame:
    """Per-rebalance L1 distance between two methods (0 = identical weights)."""

    a = weights.loc[(weights["family"].eq(family)) & (weights["method"].eq(method_a))]
    b = weights.loc[(weights["family"].eq(family)) & (weights["method"].eq(method_b))]
    rows = []
    for date in sorted(set(a["date"]).intersection(set(b["date"]))):
        wa = a.loc[a["date"].eq(date)].set_index("ticker")["weight"]
        wb = b.loc[b["date"].eq(date)].set_index("ticker")["weight"]
        idx = sorted(set(wa.index).union(set(wb.index)))
        dist = 0.5 * float((wa.reindex(idx).fillna(0) - wb.reindex(idx).fillna(0)).abs().sum())
        rows.append({"date": date, "family": family, "method_a": method_a, "method_b": method_b, "l1_half": dist})
    return pd.DataFrame(rows)


def run_fund_grid(
    panels: dict[str, tuple[pd.DataFrame, int, int]],
    methods: tuple[str, ...] = ("equal_weight", "min_variance", "max_sharpe", "risk_parity"),
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    returns, weights, metrics = [], [], []
    for family, (wide, periods_per_year, estimation_window) in panels.items():
        cap = 0.40 if wide.shape[1] <= 10 else 0.25
        for method in methods:
            fund_returns, fund_weights, fund_metrics = oos_backtest(
                wide,
                family=family,
                method=method,
                estimation_window=estimation_window,
                periods_per_year=periods_per_year,
                max_weight=cap,
            )
            returns.append(fund_returns)
            weights.append(fund_weights)
            metrics.append(fund_metrics)
    return pd.concat(returns, ignore_index=True), pd.concat(weights, ignore_index=True), pd.DataFrame(metrics)
