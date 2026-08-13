"""Reproduce Project B results into results/."""
from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

plt.rcParams.update(
    {
        "font.size": 11,
        "axes.titlesize": 13,
        "axes.labelsize": 11.5,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "legend.fontsize": 9,
        "axes.titlepad": 10,
        "axes.labelpad": 6,
    }
)

from src import etl, features, fusion, portfolios, sentiment


ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "results" / "data"
TABLE_DIR = ROOT / "results" / "tables"
FIG_DIR = ROOT / "results" / "figures"


def _save_fig(fig, name: str) -> None:
    """Pad the saved PNG so axis titles are not flush with the crop box."""
    fig.savefig(FIG_DIR / name, dpi=220, bbox_inches="tight", pad_inches=0.28)
    plt.close(fig)


def ensure_vader() -> None:
    import nltk
    try:
        from nltk.sentiment import SentimentIntensityAnalyzer
        SentimentIntensityAnalyzer()
    except LookupError:
        nltk.download("vader_lexicon", quiet=True)


def save_growth_figure(fund_returns: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(10.2, 7.0))
    for fund, group in fund_returns.groupby("fund"):
        ax.plot(group["date"], group["growth"], lw=1.35, label=fund)
    ax.set_title("Growth of $1 by investable fund, out-of-sample")
    ax.set_ylabel("Wealth index ($1 at first live date)")
    ax.set_xlabel("Date")
    ax.grid(axis="y", alpha=0.25)
    ax.legend(
        fontsize=8.5,
        ncol=2,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.16),
        frameon=False,
    )
    fig.tight_layout()
    _save_fig(fig, "growth_of_one_dollar.png")


def save_drawdown_figure(fund_returns: pd.DataFrame) -> None:
    sample = fund_returns.loc[fund_returns["family"].eq("Combined")]
    fig, ax = plt.subplots(figsize=(10.2, 7.2))
    for fund, group in sample.groupby("fund"):
        ax.plot(group["date"], 100 * group["drawdown"], lw=1.35, label=fund)
    ax.set_title("Combined-fund drawdowns, out-of-sample")
    ax.set_ylabel("Drawdown (%)")
    ax.set_xlabel("Date")
    ax.grid(axis="y", alpha=0.25)
    ax.legend(fontsize=9, loc="lower left", framealpha=0.92)
    fig.tight_layout()
    _save_fig(fig, "combined_drawdowns.png")


def save_weights_figure(weights: pd.DataFrame) -> None:
    sample = weights.loc[
        weights["family"].eq("Combined") & weights["method"].isin(["Minimum Variance", "Risk Parity"])
    ].copy()
    top = sample.groupby("ticker")["weight"].mean().sort_values(ascending=False).head(10).index
    sample["plot_ticker"] = np.where(sample["ticker"].isin(top), sample["ticker"], "Other")
    pivot = sample.pivot_table(
        index="date", columns=["method", "plot_ticker"], values="weight", aggfunc="sum"
    )
    fig, axes = plt.subplots(2, 1, figsize=(10.5, 8.4), sharex=True)
    for ax, method in zip(axes, ["Minimum Variance", "Risk Parity"], strict=True):
        data = pivot[method].fillna(0)
        # Keep stacked areas summing to one by retaining the Other residual.
        order = [c for c in data.columns if c != "Other"] + (["Other"] if "Other" in data.columns else [])
        data = data[order]
        ax.stackplot(data.index, data.T, labels=data.columns)
        ax.set_title(f"Combined {method}: top holdings plus Other residual")
        ax.set_ylabel("Weight")
        ax.set_ylim(0, 1)
        ax.legend(fontsize=8, ncol=4, loc="upper left", framealpha=0.92)
    axes[-1].set_xlabel("Rebalance decision date")
    fig.tight_layout()
    _save_fig(fig, "combined_weights_over_time.png")


def save_sharpe_figure(metrics: pd.DataFrame) -> None:
    ordered = metrics.sort_values("sharpe")
    fig, ax = plt.subplots(figsize=(10, 6.8))
    ax.barh(ordered["fund"], ordered["sharpe"], color="#007C83")
    ax.set_title("Out-of-sample Sharpe ratios across funds")
    ax.set_xlabel("Annualised Sharpe ratio, risk-free rate assumed zero")
    ax.grid(axis="x", alpha=0.25)
    fig.tight_layout()
    _save_fig(fig, "fund_sharpe_barplot.png")


def save_sentiment_figure(sector_index: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(10.2, 7.2))
    for sector, group in sector_index.groupby("sector"):
        smoothed = group.set_index("trade_date")["sentiment"].rolling(21, min_periods=5).mean()
        ax.plot(smoothed.index, smoothed, lw=1.25, label=sector)
    ax.axhline(0, color="black", lw=0.8)
    ax.set_title("Context-weighted sector sentiment index, 21-trading-day average")
    ax.set_ylabel("Context-weighted Signal Harbour compound score")
    ax.set_xlabel("Mapped equity trading date")
    ax.grid(axis="y", alpha=0.25)
    ax.legend(fontsize=8.5, ncol=2, loc="upper left", framealpha=0.92)
    fig.tight_layout()
    _save_fig(fig, "sector_sentiment_index.png")

    # Distinct companion exhibit: dispersion of active ticker coverage by sector.
    fig, ax = plt.subplots(figsize=(10.2, 6.8))
    coverage = (
        sector_index.groupby("sector", observed=True)
        .agg(mean_active=("active_tickers", "mean"), mean_headlines=("headline_count", "mean"))
        .sort_values("mean_active", ascending=False)
    )
    ax.bar(coverage.index.astype(str), coverage["mean_active"], color="#007C83")
    ax.set_title("Average active tickers per sector-day in the context-weighted index")
    ax.set_ylabel("Mean active tickers")
    ax.tick_params(axis="x", rotation=30)
    fig.tight_layout()
    _save_fig(fig, "context_weighted_sector_sentiment.png")


def save_fusion_figure(fund_returns: pd.DataFrame) -> None:
    compare = fund_returns.loc[
        fund_returns["fund"].isin([
            "Equity - Minimum Variance",
            "Equity - Minimum Variance + Context-Weighted Sentiment",
        ])
    ]
    fig, ax = plt.subplots(figsize=(10.2, 6.8))
    for fund, group in compare.groupby("fund"):
        ax.plot(group["date"], group["growth"], lw=1.6, label=fund)
    ax.set_title("Fusion test: base equity fund versus lagged context-weighted sentiment tilt")
    ax.set_ylabel("Wealth index")
    ax.set_xlabel("Date")
    ax.grid(axis="y", alpha=0.25)
    ax.legend(fontsize=9, loc="upper left", framealpha=0.92)
    fig.tight_layout()
    _save_fig(fig, "fusion_before_after.png")


def save_fusion_sensitivity_figure(sensitivity: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(10.2, 6.8))
    for method, group in sensitivity.groupby("base_method"):
        ax.plot(group["tilt_strength"], group["sharpe"], marker="o", lw=1.6, label=method)
    ax.set_title("Fusion robustness: Sharpe ratio by tilt strength and equity base method")
    ax.set_xlabel("Sentiment tilt strength")
    ax.set_ylabel("Out-of-sample Sharpe ratio")
    ax.grid(axis="both", alpha=0.25)
    ax.legend(fontsize=9, loc="best", framealpha=0.92)
    fig.tight_layout()
    _save_fig(fig, "fusion_sensitivity.png")


def save_model_comparison_figure(summary: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(10.2, 7.0))
    x = np.arange(len(summary))
    width = 0.25
    ax.bar(x - width, summary["share_positive"], width=width, label="Positive", color="#1b7f79")
    ax.bar(x, summary["share_neutral"], width=width, label="Neutral", color="#9aa5a1")
    ax.bar(x + width, summary["share_negative"], width=width, label="Negative", color="#b85c38")
    ax.set_xticks(x)
    ax.set_xticklabels(summary["model"], rotation=12)
    ax.set_ylabel("Share of sampled headlines")
    ax.set_title("Sentiment model comparison: polarity shares")
    ax.set_ylim(0, 1)
    ax.legend(fontsize=9, loc="upper right", framealpha=0.92)
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    _save_fig(fig, "sentiment_model_comparison.png")


def save_coverage_neutrality_figure(coverage: pd.DataFrame) -> None:
    """Distinct coverage exhibit: mean headlines and zero-raw share by sector."""

    frame = coverage.sort_values("mean_headline_count", ascending=True).copy()
    fig, ax1 = plt.subplots(figsize=(10.2, 7.4))
    ax1.barh(frame["sector"].astype(str), frame["mean_headline_count"], color="#0f4c5c", alpha=0.85)
    ax1.set_xlabel("Mean headlines per ticker-day with news")
    ax1.set_title("Headline coverage intensity and exact-zero raw-score share by sector")
    ax2 = ax1.twiny()
    ax2.plot(frame["share_zero_raw"], frame["sector"].astype(str), "o-", color="#b85c38", label="Share exact-zero raw")
    ax2.set_xlabel("Share of raw scores exactly zero")
    ax2.set_xlim(0, 1)
    ax2.legend(loc="lower right", fontsize=9, framealpha=0.92)
    fig.tight_layout()
    _save_fig(fig, "sentiment_coverage_neutrality.png")


def save_ablation_figure(robustness: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(10.2, 6.8))
    ordered = robustness.sort_values("share_neutral")
    ax.barh(ordered["specification"], ordered["share_neutral"], color="#0f4c5c")
    ax.set_xlabel("Neutral share (|compound| <= 0.05)")
    ax.set_title("Signal Harbour ablation on Week 9 finVADER base (neutral share)")
    ax.grid(axis="x", alpha=0.25)
    fig.tight_layout()
    _save_fig(fig, "innovation_ablation.png")


def latest_holdings_snapshot(weights: pd.DataFrame) -> pd.DataFrame:
    latest_date = weights.groupby(["family", "method"], as_index=False)["date"].max()
    latest = weights.merge(latest_date, on=["family", "method", "date"], how="inner")
    latest = latest.sort_values(["family", "method", "weight"], ascending=[True, True, False])
    return latest.reset_index(drop=True)


def ablation_neutral_rates(sample_titles: pd.Series) -> pd.DataFrame:
    """Ablation of Signal Harbour components on the Week 9 finVADER base analyser."""

    from copy import deepcopy

    spec = sentiment.load_lexicon_spec()
    week9 = sentiment.build_week9_finvader()
    plain = sentiment._vader()
    variants = {
        "full_signal_harbour": ("week9_base", spec),
        "no_phrases": ("week9_base", {**deepcopy(spec), "phrases": []}),
        "no_neutral_overrides": ("week9_base", {**deepcopy(spec), "neutral_overrides": []}),
        "no_custom_terms": ("week9_base", {**deepcopy(spec), "terms": []}),
        "week9_finvader_only": ("week9_only", None),
        "base_vader": ("plain", None),
    }
    rows = []
    for name, (mode, variant) in variants.items():
        scores = []
        for text in sample_titles.astype(str):
            if mode == "plain":
                scores.append(sentiment.score_text_base_vader(text, plain))
            elif mode == "week9_only":
                scores.append(sentiment.score_text_week9_finvader(text, week9))
            else:
                scores.append(
                    sentiment.score_text_signal_harbour(text, week9, spec=variant)["headline_sentiment"]
                )
        s = pd.Series(scores, dtype=float)
        rows.append({
            "specification": name,
            "analyser_base": "week9_finvader" if mode != "plain" else "plain_vader",
            "n_headlines": int(len(s)),
            "mean_compound": float(s.mean()),
            "share_neutral": float((s.abs() <= 0.05).mean()),
            "share_exact_zero": float((s == 0.0).mean()),
        })
    return pd.DataFrame(rows)


def main() -> None:
    for path in [DATA_DIR, TABLE_DIR, FIG_DIR]:
        path.mkdir(parents=True, exist_ok=True)
    ensure_vader()

    clean = etl.load_all_clean()
    equity_returns = features.daily_returns(clean.equities)
    crypto_returns = features.daily_returns(clean.crypto)
    equity_wide = features.returns_wide(equity_returns).dropna(how="all")
    crypto_wide_native = features.returns_wide(crypto_returns).dropna(how="all")
    crypto_equity_calendar = features.returns_wide(
        features.align_returns_to_calendar(crypto_returns, equity_wide.index)
    )
    combined_wide = pd.concat([equity_wide, crypto_equity_calendar], axis=1)

    panels = {
        "Equity": (equity_wide, 252, 252),
        "Crypto": (crypto_wide_native, 365, 365),
        "Combined": (combined_wide, 252, 252),
    }
    fund_returns, fund_weights, metrics = portfolios.run_fund_grid(panels)

    sector_map = clean.equities[["ticker", "sector"]].drop_duplicates()
    headline_panel, mapped_headlines = features.assemble_headline_panel(
        clean.news, equity_wide.index, sector_map
    )
    attention_panel = features.add_attention_pulse(headline_panel)

    print("Scoring Signal Harbour (Week-9-based) context-weighted sentiment...")
    scores = sentiment.score_headlines(mapped_headlines, model="signal_harbour")
    scores = sentiment.attach_context_weights(scores, attention_panel)
    # Complete ticker-day grid first (no-news days = neutral), then sector index from that grid.
    ticker_signal = sentiment.ticker_sentiment_signal(
        scores,
        equity_wide.index,
        list(equity_wide.columns),
        sentiment_col="context_weighted_sentiment",
        sector_map=sector_map,
    )
    sector_index = sentiment.sector_sentiment_index(
        ticker_signal, sentiment_col="context_weighted_sentiment"
    )

    fusion_returns, fusion_weights, fusion_metrics = fusion.apply_sentiment(
        fund_weights, equity_wide, ticker_signal
    )
    fund_returns = pd.concat([fund_returns, fusion_returns], ignore_index=True)
    fund_weights = pd.concat([fund_weights, fusion_weights], ignore_index=True)
    metrics = pd.concat([metrics, pd.DataFrame([fusion_metrics])], ignore_index=True)
    keep_cols = [
        "fund", "family", "method", "observations", "annualised_return", "annualised_volatility",
        "sharpe", "max_drawdown", "terminal_growth", "first_live_date", "estimation_window",
        "periods_per_year", "avg_annual_turnover",
    ]
    metrics = metrics[[c for c in keep_cols if c in metrics.columns]]
    holdings_snapshot = latest_holdings_snapshot(fund_weights)

    # Solver differentiation diagnostics (Equity Min-Var vs Equal Weight).
    divergence = portfolios.method_weight_divergence(
        fund_weights,
        family="Equity",
        method_a="Minimum Variance",
        method_b="Equal Weight",
    )
    divergence.to_csv(TABLE_DIR / "method_weight_divergence.csv", index=False)
    print(
        "Equity Min-Var vs Equal-Weight: "
        f"mean L1/2={divergence['l1_half'].mean():.4f}, "
        f"share differing>1%={(divergence['l1_half'] > 0.01).mean():.1%}"
    )

    print("Building model comparison sample...")
    scored_sample = sentiment.compare_models_on_headlines(mapped_headlines, sample_n=4000)
    model_summary = sentiment.model_comparison_summary(scored_sample)
    lexicon_audit = sentiment.lexicon_audit_table()
    validation_sample = sentiment.build_validation_sample(scored_sample, n=120)
    validation_sample = sentiment.preserve_kaiyuan_review_labels(
        validation_sample, DATA_DIR / "headline_validation_sample.csv"
    )
    pseudo_diag = sentiment.pseudo_label_diagnostic_summary(validation_sample)
    kaiyuan_diag = sentiment.kaiyuan_label_agreement_summary(validation_sample)

    coverage = scores.groupby("sector", observed=True).agg(
        ticker_days=("ticker", "size"),
        mean_headline_count=("headline_count", "mean"),
        mean_coverage_confidence=("coverage_confidence", "mean"),
        mean_attention_confidence=("attention_confidence", "mean"),
        mean_raw_sentiment=("sentiment", "mean"),
        mean_context_weighted=("context_weighted_sentiment", "mean"),
        share_zero_raw=("sentiment", lambda s: float((s == 0).mean())),
    ).reset_index()

    ablation = ablation_neutral_rates(scored_sample["title"].sample(800, random_state=5444541))
    open_source_method = pd.DataFrame([
        {
            "method": "unchanged_vader",
            "role": "baseline",
            "source": "NLTK/vaderSentiment",
            "used_in_trading": False,
            "notes": "Transparent social-media lexicon baseline (Week 8 starting point).",
        },
        {
            "method": "week9_finvader",
            "role": "benchmark",
            "source": "FINS3645 Week 9 fear_greed_tools.build_finvader = PetrKorab FinVADER lexicons",
            "used_in_trading": False,
            "notes": "SentiBigNomics*0.1 + Henry on NLTK VADER; lexicons vendored under src/vendor/course_finvader for Python 3.13.",
        },
        {
            "method": "signal_harbour_context_weighted_finvader",
            "role": "primary_innovation",
            "source": "Week 9 finVADER base + Signal Harbour masks/terms/phrases + Attention Pulse + coverage confidence",
            "used_in_trading": True,
            "notes": "Augments the Week 9 analyser, then applies context weights and a one-session lag before fusion.",
        },
        {
            "method": "hierarchical_risk_parity",
            "role": "researched_deferred",
            "source": "PyPortfolioOpt research",
            "used_in_trading": False,
            "notes": "Deferred: weaker Part A continuity than context-weighted sentiment.",
        },
    ])

    fund_returns.to_csv(DATA_DIR / "fund_returns.csv", index=False)
    fund_weights.to_csv(DATA_DIR / "fund_weights.csv", index=False)
    sector_index.to_csv(DATA_DIR / "sector_sentiment_index.csv", index=False)
    ticker_signal.to_csv(DATA_DIR / "ticker_sentiment_signal.csv", index=False)
    metrics.to_csv(TABLE_DIR / "performance_metrics.csv", index=False)
    # Fact sheets add plain-language notes; not a duplicate dump of metrics.
    fact_sheets = metrics.copy()
    fact_sheets["sharpe_definition"] = "zero_rf_mean_over_vol_annualised"
    fact_sheets["annualised_return_definition"] = "CAGR_from_growth_of_one"
    fact_sheets["rebalance_rule"] = "monthly_decision_next_session_effective_with_drift"
    fact_sheets.to_csv(TABLE_DIR / "fund_fact_sheets.csv", index=False)
    holdings_snapshot.to_csv(TABLE_DIR / "latest_holdings_snapshot.csv", index=False)

    # Representative samples: stratified across tickers, not alphabetical head().
    def stratified_ticker_sample(panel: pd.DataFrame, n: int = 5000) -> pd.DataFrame:
        if len(panel) <= n:
            return panel.copy()
        per = max(1, n // panel["ticker"].nunique())
        parts = [
            g.sample(min(len(g), per), random_state=5444541)
            for _, g in panel.groupby("ticker", observed=True)
        ]
        out = pd.concat(parts, ignore_index=True)
        if len(out) > n:
            out = out.sample(n, random_state=5444541)
        return out.sort_values(["trade_date", "ticker"]).reset_index(drop=True)

    stratified_ticker_sample(headline_panel, 5000).to_csv(DATA_DIR / "headline_panel_sample.csv", index=False)
    stratified_ticker_sample(attention_panel, 5000).to_csv(DATA_DIR / "attention_pulse_panel_sample.csv", index=False)

    fusion_compare = metrics.loc[
        metrics["fund"].isin([
            "Equity - Minimum Variance",
            "Equity - Minimum Variance + Context-Weighted Sentiment",
        ])
    ].copy()
    fusion_compare.to_csv(TABLE_DIR / "fusion_before_after.csv", index=False)
    # Keep the robustness grid manageable: strengths × bases at zero cost, plus a cost table.
    fusion_grid = fusion.fusion_sensitivity(
        fund_weights,
        equity_wide,
        ticker_signal,
        cost_bps_grid=(0.0,),
    )
    fusion_grid.to_csv(TABLE_DIR / "fusion_sensitivity.csv", index=False)
    cost_table = fusion.turnover_cost_table(fund_weights, equity_wide, ticker_signal)
    cost_table.to_csv(TABLE_DIR / "fusion_cost_sensitivity.csv", index=False)

    model_summary.to_csv(TABLE_DIR / "sentiment_model_comparison.csv", index=False)
    lexicon_audit.to_csv(TABLE_DIR / "finvader_lexicon_audit.csv", index=False)
    coverage.to_csv(TABLE_DIR / "sentiment_coverage_by_sector.csv", index=False)
    ablation.to_csv(TABLE_DIR / "sentiment_robustness.csv", index=False)
    open_source_method.to_csv(TABLE_DIR / "open_source_method_comparison.csv", index=False)
    validation_sample.to_csv(DATA_DIR / "headline_validation_sample.csv", index=False)
    pseudo_diag.to_csv(TABLE_DIR / "headline_pseudo_label_diagnostic.csv", index=False)
    if not kaiyuan_diag.empty:
        kaiyuan_diag.to_csv(TABLE_DIR / "headline_kaiyuan_label_agreement.csv", index=False)

    # Explainability snapshot: latest trade date, fields aligned to signal_date.
    latest_date = ticker_signal["trade_date"].max()
    explain = ticker_signal.loc[ticker_signal["trade_date"].eq(latest_date)].copy()
    # Prefer rows with a real prior signal date and mapped sector for the analyst view.
    explain = explain.sort_values(
        ["explain_headline_count", "tradable_score"],
        ascending=[False, False],
    )
    explain.to_csv(TABLE_DIR / "sentiment_explainability_snapshot.csv", index=False)

    save_growth_figure(fund_returns)
    save_drawdown_figure(fund_returns)
    save_weights_figure(fund_weights)
    save_sharpe_figure(metrics)
    save_sentiment_figure(sector_index)
    save_fusion_figure(fund_returns)
    save_fusion_sensitivity_figure(fusion_grid)
    save_model_comparison_figure(model_summary)
    save_coverage_neutrality_figure(coverage)
    save_ablation_figure(ablation)

    print(f"fund returns: {fund_returns.shape}")
    print(f"fund weights: {fund_weights.shape}")
    print(f"sector sentiment index: {sector_index.shape}")
    print(f"metrics: {metrics.shape}")
    print(model_summary.to_string(index=False))
    print(fusion_compare[["fund", "sharpe", "annualised_return", "max_drawdown"]].to_string(index=False))


if __name__ == "__main__":
    main()
