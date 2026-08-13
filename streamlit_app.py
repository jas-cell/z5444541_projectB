"""Signal Harbour: precomputed systematic-fund dashboard."""
from __future__ import annotations

import pathlib

import numpy as np
import pandas as pd
import streamlit as st


ROOT = pathlib.Path(__file__).resolve().parent
DATA = ROOT / "results" / "data"
TABLES = ROOT / "results" / "tables"


st.set_page_config(page_title="Signal Harbour Funds", layout="wide")
st.markdown(
    """
    <style>
    .stApp {background: linear-gradient(180deg, #f6fbfb 0%, #eef5f4 100%);}
    div[data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid #d7e6e3;
        border-radius: 10px;
        padding: 0.8rem 0.9rem;
    }
    .hero {
        background: linear-gradient(135deg, #0f4c5c 0%, #1b7f79 62%, #d8f0ea 100%);
        color: white;
        border-radius: 12px;
        padding: 1.2rem 1.2rem 1rem 1.2rem;
        margin-bottom: 1rem;
    }
    .hero p {margin-bottom: 0.2rem;}
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner=False)
def load_outputs():
    returns = pd.read_csv(DATA / "fund_returns.csv", parse_dates=["date"])
    weights = pd.read_csv(DATA / "fund_weights.csv", parse_dates=["date"])
    sentiment_idx = pd.read_csv(DATA / "sector_sentiment_index.csv", parse_dates=["trade_date"])
    metrics = pd.read_csv(TABLES / "performance_metrics.csv")
    ticker_signal = pd.read_csv(DATA / "ticker_sentiment_signal.csv", parse_dates=["trade_date"])
    explain = pd.read_csv(TABLES / "sentiment_explainability_snapshot.csv", parse_dates=["trade_date"])
    model_compare = pd.read_csv(TABLES / "sentiment_model_comparison.csv")
    return returns, weights, sentiment_idx, metrics, ticker_signal, explain, model_compare


def pct(value: float) -> str:
    return f"{100 * value:.1f}%"


def infer_periods_per_year(fund_name: str, metrics: pd.DataFrame) -> int:
    row = metrics.loc[metrics["fund"].eq(fund_name)]
    if not row.empty and "periods_per_year" in row.columns:
        return int(row.iloc[0]["periods_per_year"])
    return 365 if "Crypto" in fund_name and "Combined" not in fund_name else 252


def allocation_panel(fund_returns: pd.DataFrame, chosen: list[str]) -> tuple[pd.DataFrame, int]:
    """Align selected funds on an economically consistent calendar.

    Crypto-only and mixed sleeves that include crypto use the native union calendar:
    missing legs contribute 0 that day (equity closed / crypto weekend). Equity-only
    sleeves stay on intersecting equity sessions at 252-day annualisation.
    """

    series = {
        name: fund_returns.loc[fund_returns["fund"].eq(name)].set_index("date")["return"].astype(float)
        for name in chosen
    }
    families = {name.split(" - ")[0] for name in chosen}
    has_crypto = "Crypto" in families
    if has_crypto:
        panel = pd.concat(series, axis=1).sort_index().fillna(0.0)
        return panel, 365
    panel = pd.concat(series, axis=1).dropna(how="any")
    return panel, 252


(
    fund_returns,
    fund_weights,
    sector_sentiment,
    metrics,
    ticker_signal,
    explain_snapshot,
    model_compare,
) = load_outputs()
fusion_sensitivity = pd.read_csv(TABLES / "fusion_sensitivity.csv")
fusion_compare = pd.read_csv(TABLES / "fusion_before_after.csv")
cost_path = TABLES / "fusion_cost_sensitivity.csv"
fusion_costs = pd.read_csv(cost_path) if cost_path.exists() else pd.DataFrame()

top_sharpe = metrics.sort_values("sharpe", ascending=False).iloc[0]
top_growth = metrics.sort_values("terminal_growth", ascending=False).iloc[0]
latest_sentiment = (
    sector_sentiment.sort_values("trade_date").groupby("sector", as_index=False).tail(1)
    .sort_values("sentiment", ascending=False)
)
sample_end = pd.to_datetime(fund_returns["date"]).max().date().isoformat()

st.markdown(
    f"""
    <div class="hero">
      <h1 style="margin:0 0 0.35rem 0;">Signal Harbour</h1>
      <p style="font-size:1.02rem;">Research dashboard for a small wealth-advisory firm. The day-to-day user is a portfolio analyst comparing walk-forward funds and lagged equity-news context before an investment-committee discussion.</p>
      <p style="opacity:0.92;">Strongest zero-rf Sharpe in sample: <strong>{top_sharpe['fund']}</strong> ({top_sharpe['sharpe']:.2f}). Highest terminal growth: <strong>{top_growth['fund']}</strong> ({top_growth['terminal_growth']:.2f}x). Sample ends {sample_end}.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

tab_compare, tab_fact, tab_allocate, tab_sentiment, tab_explain = st.tabs(
    ["Compare funds", "Fact sheet", "Allocate", "Sentiment", "Explain signal"]
)

with tab_compare:
    st.subheader("Fund comparison")
    c1, c2, c3 = st.columns(3)
    c1.metric("Best Sharpe", top_sharpe["fund"], f"{top_sharpe['sharpe']:.2f}")
    c2.metric("Best growth", top_growth["fund"], f"{top_growth['terminal_growth']:.2f}x")
    c3.metric("Funds tracked", str(metrics["fund"].nunique()), f"OOS through {sample_end}")
    shown = metrics.copy()
    for col in ["annualised_return", "annualised_volatility", "max_drawdown"]:
        shown[col] = shown[col].map(pct)
    shown["sharpe"] = shown["sharpe"].map(lambda x: f"{x:.2f}")
    st.dataframe(
        shown[["fund", "annualised_return", "annualised_volatility", "sharpe", "max_drawdown", "terminal_growth"]],
        width="stretch",
        hide_index=True,
    )
    selected = st.multiselect(
        "Funds to plot",
        sorted(fund_returns["fund"].unique()),
        default=list(metrics.sort_values("sharpe", ascending=False)["fund"].head(5)),
    )
    if selected:
        chart = fund_returns.loc[fund_returns["fund"].isin(selected)].pivot(index="date", columns="fund", values="growth")
        st.line_chart(chart, height=360)
    st.caption(
        "Growth uses precomputed out-of-sample fund returns. "
        "Sharpe is the conventional zero risk-free mean/volatility ratio (annualised). "
        "Annualised return in the table is CAGR from the growth-of-one path."
    )

with tab_fact:
    fund = st.selectbox("Open a fund fact sheet", sorted(fund_returns["fund"].unique()))
    row = metrics.loc[metrics["fund"].eq(fund)].iloc[0]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("CAGR", pct(row["annualised_return"]))
    c2.metric("Annualised volatility", pct(row["annualised_volatility"]))
    c3.metric("Sharpe (zero rf)", f"{row['sharpe']:.2f}")
    c4.metric("Max drawdown", pct(row["max_drawdown"]))
    series = fund_returns.loc[fund_returns["fund"].eq(fund)].set_index("date")
    left, right = st.columns([1.3, 1])
    with left:
        st.line_chart(series[["growth"]], height=310)
        st.area_chart(100 * series[["drawdown"]], height=220)
    with right:
        latest = fund_weights.loc[
            (fund_weights["family"].eq(row["family"])) & (fund_weights["method"].eq(row["method"]))
        ]
        latest = latest.loc[latest["date"].eq(latest["date"].max())].sort_values("weight", ascending=False)
        top = latest.head(20).copy()
        shown_weight = float(latest.head(20)["weight"].sum())
        residual = max(0.0, 1.0 - shown_weight)
        top["weight"] = top["weight"].map(lambda x: f"{100 * x:.2f}%")
        st.dataframe(top[["ticker", "weight"]], width="stretch", hide_index=True)
        st.caption(
            f"Most recent rebalance *decision* weights for {fund}. "
            f"Top 20 shown ({100 * shown_weight:.1f}%); residual not listed = {100 * residual:.1f}%."
        )

with tab_allocate:
    st.subheader("Allocation sandbox")
    chosen = st.multiselect(
        "Select funds",
        sorted(fund_returns["fund"].unique()),
        default=list(metrics.sort_values("sharpe", ascending=False)["fund"].head(3)),
    )
    if chosen:
        n = len(chosen)
        # Defaults that always sum to 100 (e.g. 34/33/33).
        defaults = [100 // n + (1 if i < 100 % n else 0) for i in range(n)]
        raw_weights = {}
        cols = st.columns(min(3, n))
        for i, fund_name in enumerate(chosen):
            raw_weights[fund_name] = cols[i % len(cols)].slider(fund_name, 0, 100, defaults[i])
        total = sum(raw_weights.values())
        if total != 100:
            st.warning(f"Raw slider total is {total}. Weights are renormalised to 100% for the sandbox path.")
        if total == 0:
            st.warning("Set at least one positive allocation.")
        else:
            allocation = pd.Series({k: v / total for k, v in raw_weights.items()})
            panel, ppy = allocation_panel(fund_returns, chosen)
            portfolio = (panel * allocation).sum(axis=1)
            wealth = (1 + portfolio).cumprod()
            st.line_chart(wealth.rename("custom allocation"), height=330)
            ann_ret = wealth.iloc[-1] ** (ppy / len(portfolio)) - 1
            ann_vol = portfolio.std(ddof=1) * (ppy ** 0.5)
            st.write({
                "annualised return (CAGR)": pct(ann_ret),
                "annualised volatility": pct(ann_vol),
                "sharpe (zero rf)": f"{(portfolio.mean() * ppy) / ann_vol:.2f}" if ann_vol > 0 else "n/a",
                "terminal growth": f"{wealth.iloc[-1]:.2f}x",
                "periods_per_year_used": ppy,
                "calendar_note": (
                    "Any selection that includes a Crypto fund uses the native union calendar "
                    "at 365 (missing legs = 0 that day). Equity-only selections use intersecting "
                    "equity sessions at 252."
                ),
                "normalised allocation": {k: f"{100 * v:.1f}%" for k, v in allocation.items()},
            })
            st.caption(
                "Sandbox combines precomputed fund return streams only. "
                "It does not re-optimise holdings or restate individual fact sheets for mixed calendars."
            )

with tab_sentiment:
    st.subheader("Equity-sector context-weighted sentiment")
    left, right = st.columns([1.35, 1])
    with right:
        display_latest = latest_sentiment.copy()
        display_latest["sentiment"] = display_latest["sentiment"].map(lambda x: f"{x:.3f}")
        st.dataframe(display_latest[["sector", "sentiment", "headline_count"]], width="stretch", hide_index=True)
        st.dataframe(
            fusion_compare[["fund", "annualised_return", "annualised_volatility", "sharpe", "max_drawdown"]],
            width="stretch",
            hide_index=True,
        )
        st.dataframe(model_compare, width="stretch", hide_index=True)
        if not fusion_costs.empty:
            st.caption("Fusion cost sensitivity (principal Min-Var overlay)")
            st.dataframe(fusion_costs, width="stretch", hide_index=True)
    with left:
        st.caption(
            "Standalone sector index uses Signal Harbour scores built on the Week 9 finVADER base, "
            "then multiplied by coverage confidence and elevated Attention Pulse confidence. "
            "Trading use is lagged by one equity session."
        )
    sectors = st.multiselect(
        "Sectors",
        sorted(sector_sentiment["sector"].unique()),
        default=sorted(sector_sentiment["sector"].unique())[:4],
    )
    if sectors:
        view = sector_sentiment.loc[sector_sentiment["sector"].isin(sectors)].copy()
        view["sentiment_21d"] = view.groupby("sector")["sentiment"].transform(lambda s: s.rolling(21, min_periods=5).mean())
        chart = view.pivot(index="trade_date", columns="sector", values="sentiment_21d")
        st.line_chart(chart, height=360)
    st.dataframe(
        fusion_sensitivity[["base_method", "tilt_strength", "sharpe", "annualised_return", "max_drawdown"]],
        width="stretch",
        hide_index=True,
    )

with tab_explain:
    st.subheader("Signal explainability")
    st.caption(
        "Fields below describe the prior equity session that produced today's lagged tradable score. "
        "They are not same-day headlines paired with yesterday's score."
    )
    latest_trade_date = pd.to_datetime(explain_snapshot["trade_date"]).max()
    conf_col = "explain_coverage_confidence" if "explain_coverage_confidence" in explain_snapshot.columns else "coverage_confidence"
    att_col = "explain_attention_confidence" if "explain_attention_confidence" in explain_snapshot.columns else "attention_confidence"
    count_col = "explain_headline_count" if "explain_headline_count" in explain_snapshot.columns else "headline_count"

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Portfolio trade date", latest_trade_date.date().isoformat())
    c2.metric("Tickers in snapshot", str(explain_snapshot["ticker"].nunique()))
    c3.metric("Mean coverage confidence (signal day)", f"{pd.to_numeric(explain_snapshot[conf_col], errors='coerce').mean():.2f}")
    c4.metric("Mean attention confidence (signal day)", f"{pd.to_numeric(explain_snapshot[att_col], errors='coerce').mean():.2f}")

    options = sorted(explain_snapshot["ticker"].dropna().unique())
    busiest_rows = explain_snapshot.sort_values(
        [count_col, "tradable_score"], ascending=[False, False]
    )
    busiest = busiest_rows["ticker"].iloc[0] if not busiest_rows.empty else options[0]
    ticker = st.selectbox(
        "Inspect ticker — defaults to the most-covered name on the signal day",
        options,
        index=options.index(busiest) if busiest in options else 0,
    )
    row = explain_snapshot.loc[explain_snapshot["ticker"].eq(ticker)].iloc[0]

    def _get(name: str, default=np.nan):
        explain_name = f"explain_{name}"
        if explain_name in row.index and pd.notna(row.get(explain_name)):
            return row.get(explain_name)
        return row.get(name, default)

    sector_val = _get("sector")
    sector_txt = sector_val if isinstance(sector_val, str) and sector_val else "sector unavailable"
    signal_date = row.get("signal_date")
    signal_date_str = "—" if pd.isna(signal_date) else pd.to_datetime(signal_date).date().isoformat()
    st.markdown(
        f"**{ticker}** · {sector_txt} · headlines from signal day **{signal_date_str}** "
        f"drive the score traded on **{latest_trade_date.date().isoformat()}**"
    )

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Tradable score used today", f"{float(row.get('tradable_score', 0.0) or 0.0):+.3f}")
    m2.metric("Raw sentiment (signal day)", f"{float(_get('sentiment', 0.0) or 0.0):+.3f}")
    m3.metric("Coverage confidence", f"{float(_get('coverage_confidence', 0.0) or 0.0):.2f}")
    pulse_val = _get("attention_pulse")
    m4.metric("Attention pulse", "warm-up" if pd.isna(pulse_val) else f"{float(pulse_val):+.2f}")
    m5.metric("Headlines (signal day)", str(int(_get("headline_count", 0) or 0)))

    terms_val = _get("contributing_terms", "")
    terms_txt = str(terms_val).strip() if isinstance(terms_val, str) else ""
    if terms_txt:
        chips = " ".join(f"`{t}`" for t in terms_txt.split("|") if t)
        st.markdown(f"Finance terms and rules that contributed on the signal day: {chips}")
    elif int(_get("headline_count", 0) or 0) > 0:
        st.caption(
            "No Signal Harbour-specific terms or phrase rules fired on the signal day — "
            "the score comes from the Week 9 finVADER base lexicon alone."
        )
    else:
        st.caption(
            "No headlines on the signal day — the lagged tradable score defaults to neutral."
        )
    display_cols = [
        c for c in [
            "ticker",
            "explain_sector",
            "explain_headline_count",
            "explain_sentiment",
            "explain_coverage_confidence",
            "explain_attention_confidence",
            "explain_context_weighted_sentiment",
            "tradable_score",
            "explain_contributing_terms",
            "signal_date",
        ] if c in explain_snapshot.columns
    ]
    st.dataframe(
        explain_snapshot.sort_values("tradable_score", ascending=False)[display_cols].head(25),
        width="stretch",
        hide_index=True,
    )
    st.caption(
        "Model comparison is summarised in the Sentiment tab. "
        "The deployed app never re-runs VADER; all values are precomputed under results/."
    )
