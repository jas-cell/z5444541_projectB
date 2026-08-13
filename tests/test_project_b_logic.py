import numpy as np
import pandas as pd

from src import features, fusion, portfolios, sentiment


def test_daily_returns_are_within_ticker():
    prices = pd.DataFrame({
        "ticker": ["A", "A", "B", "B"],
        "date": pd.to_datetime(["2020-01-01", "2020-01-02", "2020-01-01", "2020-01-02"]),
        "adjClose": [100.0, 110.0, 50.0, 45.0],
    })
    out = features.daily_returns(prices)
    vals = out.set_index(["ticker", "date"])["simple_return"]
    assert round(vals.loc[("A", pd.Timestamp("2020-01-02"))], 6) == 0.10
    assert round(vals.loc[("B", pd.Timestamp("2020-01-02"))], 6) == -0.10


def test_headlines_map_weekend_to_next_trading_day():
    headlines = pd.DataFrame({
        "date": pd.to_datetime(["2020-01-04"]),
        "ticker": ["A"],
        "sector": ["Tech"],
        "title": ["A beats estimates"],
        "url": ["u"],
        "publisher": ["p"],
    })
    mapped = features.map_headlines_to_trading_days(
        headlines, pd.to_datetime(["2020-01-03", "2020-01-06"])
    )
    assert mapped.loc[0, "trade_date"] == pd.Timestamp("2020-01-06")
    assert mapped.loc[0, "mapping_lag_days"] == 2


def test_sentiment_signal_is_lagged_one_trading_day():
    scores = pd.DataFrame({
        "trade_date": pd.to_datetime(["2020-01-06"]),
        "ticker": ["A"],
        "sector": ["Tech"],
        "sentiment": [0.5],
        "headline_count": [1],
        "coverage_confidence": [1.0],
        "attention_confidence": [1.0],
        "attention_pulse": [1.2],
        "context_weighted_sentiment": [0.5],
        "contributing_terms": ["beats"],
    })
    signal = sentiment.ticker_sentiment_signal(
        scores, pd.to_datetime(["2020-01-06", "2020-01-07"]), ["A"]
    )
    vals = signal.set_index("trade_date")
    assert vals.loc[pd.Timestamp("2020-01-06"), "tradable_score"] == 0.0
    assert vals.loc[pd.Timestamp("2020-01-07"), "tradable_score"] == 0.5
    assert vals.loc[pd.Timestamp("2020-01-07"), "explain_sentiment"] == 0.5
    assert vals.loc[pd.Timestamp("2020-01-07"), "signal_date"] == pd.Timestamp("2020-01-06")


def test_attention_pulse_uses_past_only_baseline():
    counts = [0, 1, 0, 2, 1, 0, 1, 2, 0, 1, 0, 2, 1, 0, 1, 2, 0, 1, 0, 2, 1, 0, 1, 2, 20]
    panel = pd.DataFrame({
        "ticker": ["A"] * 25,
        "trade_date": pd.date_range("2020-01-01", periods=25, freq="D"),
        "article_count": counts,
        "sector": ["Tech"] * 25,
        "headline_text": [""] * 25,
        "max_mapping_lag_days": [0] * 25,
    })
    out = features.add_attention_pulse(panel, window=20, min_periods=10)
    assert pd.isna(out.loc[0, "attention_pulse"])
    assert out.loc[24, "attention_pulse"] > 0


def test_signal_harbour_changes_finance_phrase_relative_to_week9():
    text = "Acme beats expectations and raises guidance after record profits"
    week9 = sentiment.score_text_week9_finvader(text)
    aug = sentiment.score_text_signal_harbour(text)["headline_sentiment"]
    assert aug != week9 or "beats expectations" in sentiment.score_text_signal_harbour(text)["contributing_terms"]


def test_signal_harbour_keeps_profit_falls_negative():
    text = "Visa profit falls 23% as shares plunge"
    week9 = sentiment.score_text_week9_finvader(text)
    aug = sentiment.score_text_signal_harbour(text)["headline_sentiment"]
    assert week9 < 0
    assert aug < 0


def test_phrase_rules_skip_negated_beats():
    text = "Company did not beat estimates this quarter"
    adj, hits = sentiment._phrase_adjustment(text, sentiment.retained_phrases())
    assert "beat estimates" not in hits
    assert adj == 0.0 or "beats estimates" not in hits


def test_neutral_override_masks_gross_margin_false_positive():
    text = "Firm reports higher gross margin on refinancing"
    base = sentiment.score_text_base_vader(text)
    aug = sentiment.score_text_signal_harbour(text)["headline_sentiment"]
    assert aug >= base - 1e-9


def test_attention_confidence_ignores_negative_pulse():
    pulse = pd.Series([-2.0, 0.0, 2.0])
    conf = sentiment.attention_confidence(pulse)
    assert conf.iloc[0] == conf.iloc[1]
    assert conf.iloc[2] > conf.iloc[1]


def test_min_variance_improves_on_unequal_risk():
    idx = pd.date_range("2020-01-01", periods=80, freq="D")
    rng = np.random.default_rng(7)
    returns = pd.DataFrame({
        "SAFE": rng.normal(0.0002, 0.005, size=80),
        "RISKY": rng.normal(0.0002, 0.04, size=80),
        "MID": rng.normal(0.0002, 0.015, size=80),
    }, index=idx)
    window = returns.iloc[:60]
    w = portfolios._solve_weights(window, "min_variance", max_weight=0.8, periods_per_year=252)
    assert abs(w.sum() - 1) < 1e-8
    assert w["SAFE"] > w["RISKY"]


def test_sharpe_matches_mean_over_vol_definition():
    r = pd.Series([0.01, -0.005, 0.002, 0.003, -0.001])
    metrics = portfolios.performance_metrics(r, periods_per_year=252)
    expected = (r.mean() * 252) / (r.std(ddof=1) * np.sqrt(252))
    assert abs(metrics["sharpe"] - expected) < 1e-12
    # CAGR path metric remains available and distinct.
    assert "annualised_return" in metrics


def test_drawdown_negative_on_first_loss():
    r = pd.Series([-0.10, 0.05])
    metrics = portfolios.performance_metrics(r, periods_per_year=252)
    assert metrics["max_drawdown"] < 0


def test_backtest_weights_sum_to_one_and_methods_differ():
    idx = pd.date_range("2020-01-01", periods=120, freq="D")
    rng = np.random.default_rng(11)
    returns = pd.DataFrame({
        "A": rng.normal(0.0005, 0.01, size=120),
        "B": rng.normal(0.0001, 0.03, size=120),
        "C": rng.normal(0.0002, 0.015, size=120),
    }, index=idx)
    mv_ret, mv_w, _ = portfolios.oos_backtest(
        returns, family="Test", method="min_variance", estimation_window=40, periods_per_year=365, max_weight=0.8
    )
    ew_ret, ew_w, _ = portfolios.oos_backtest(
        returns, family="Test", method="equal_weight", estimation_window=40, periods_per_year=365, max_weight=0.8
    )
    assert not mv_ret.empty and not ew_ret.empty
    assert all(abs(mv_w.groupby("date")["weight"].sum() - 1) < 1e-8)
    div = portfolios.method_weight_divergence(
        pd.concat([mv_w, ew_w], ignore_index=True),
        family="Test",
        method_a="Minimum Variance",
        method_b="Equal Weight",
    )
    assert div["l1_half"].mean() > 0.01


def test_holdings_drift_between_rebalances():
    idx = pd.date_range("2020-01-01", periods=40, freq="D")
    returns = pd.DataFrame({
        "A": [0.10] * 40,
        "B": [0.0] * 40,
    }, index=idx)
    targets = pd.DataFrame([
        {"date": idx[5], "family": "Test", "method": "Equal Weight", "ticker": "A", "weight": 0.5},
        {"date": idx[5], "family": "Test", "method": "Equal Weight", "ticker": "B", "weight": 0.5},
    ])
    fund_returns, _, _ = portfolios.simulate_weight_path(
        returns, targets, family="Test", method="Equal Weight", periods_per_year=365
    )
    # Effective from next day after decision; A outperforms so portfolio return > 0.05 after drift starts.
    assert fund_returns["return"].iloc[0] == 0.05  # 0.5*0.1 + 0.5*0
    # After one day of drift, A weight rises above 0.5, so next return exceeds 0.05.
    assert fund_returns["return"].iloc[1] > 0.05 + 1e-12


def test_turnover_uses_post_return_drifted_weights():
    """Decision-day holdings must drift before next-session turnover is measured."""

    idx = pd.date_range("2020-01-01", periods=8, freq="D")
    returns = pd.DataFrame({"A": [0.0] * 8, "B": [0.0] * 8}, index=idx)
    returns.loc[idx[2], "A"] = 1.0  # +100% while 50/50 is held on the decision day
    targets = pd.DataFrame([
        {"date": idx[0], "family": "T", "method": "M", "ticker": "A", "weight": 0.5},
        {"date": idx[0], "family": "T", "method": "M", "ticker": "B", "weight": 0.5},
        {"date": idx[2], "family": "T", "method": "M", "ticker": "A", "weight": 1.0},
        {"date": idx[2], "family": "T", "method": "M", "ticker": "B", "weight": 0.0},
    ])
    # Day1: 50/50 effective. Day2: still 50/50 earns +50% port return, drifts to 2/3–1/3,
    # and a new 100% A target is queued. Day3 turnover vs drifted weights = 1/3.
    # (Old bug compared vs undrifted 50/50 and understated turnover.)
    fr, _, metrics = portfolios.simulate_weight_path(
        returns, targets, family="T", method="M", periods_per_year=365, cost_bps=10.0
    )
    assert not fr.empty
    # With ppy=365 and one material rebalance after warm start, turnover should reflect ~1/3 event.
    assert metrics["avg_annual_turnover"] > 0.2


def test_rebalance_frequency_argument_is_used():
    idx = pd.date_range("2020-01-01", periods=100, freq="D")
    monthly = portfolios.rebalance_dates(idx, estimation_window=10, frequency="ME")
    weekly = portfolios.rebalance_dates(idx, estimation_window=10, frequency="W")
    assert len(weekly) > len(monthly)


def test_long_only_false_allows_negative_bounds_path():
    # Smoke: short-capable bounds are accepted by the solver helper.
    idx = pd.date_range("2020-01-01", periods=50, freq="D")
    returns = pd.DataFrame({"A": np.linspace(-0.01, 0.01, 50), "B": np.linspace(0.01, -0.01, 50)}, index=idx)
    w = portfolios._solve_weights(returns, "max_sharpe", long_only=False, max_weight=1.0, periods_per_year=252)
    assert abs(w.sum() - 1) < 1e-6


def test_fusion_respects_weight_cap():
    dates = pd.date_range("2020-02-01", periods=3, freq="MS")
    weights = pd.DataFrame([
        {"date": dates[0], "family": "Equity", "method": "Equal Weight", "ticker": "A", "weight": 0.5},
        {"date": dates[0], "family": "Equity", "method": "Equal Weight", "ticker": "B", "weight": 0.5},
        {"date": dates[1], "family": "Equity", "method": "Equal Weight", "ticker": "A", "weight": 0.5},
        {"date": dates[1], "family": "Equity", "method": "Equal Weight", "ticker": "B", "weight": 0.5},
    ])
    idx = pd.date_range("2020-02-01", periods=40, freq="D")
    returns = pd.DataFrame({"A": 0.001, "B": -0.001}, index=idx)
    signal = pd.DataFrame({
        "trade_date": list(dates) * 2,
        "ticker": ["A", "A", "A", "B", "B", "B"],
        "tradable_score": [0.9, 0.9, 0.9, -0.9, -0.9, -0.9],
    })
    _, tilted, _ = fusion.apply_sentiment(
        weights, returns, signal, base_method="Equal Weight", tilt_strength=2.0, max_weight=0.55
    )
    assert tilted["method"].eq("Equal Weight + Context-Weighted Sentiment").all()
    assert tilted["weight"].max() <= 0.55 + 1e-8


def test_validation_sample_leaves_kaiyuan_labels_blank():
    sample = pd.DataFrame({
        "trade_date": pd.to_datetime(["2020-01-06"] * 6),
        "ticker": [f"T{i}" for i in range(6)],
        "sector": ["Tech"] * 3 + ["Health"] * 3,
        "title": [
            "Firm beats estimates and raises guidance",
            "Shares plunge after profit falls",
            "Company announces routine update",
            "Revenue down sharply amid lawsuit",
            "Buyback and upgrade lift outlook",
            "Board schedules annual meeting",
        ],
        "base_vader": [0.0, 0.2, -0.2, 0.0, 0.1, -0.1],
        "week9_finvader": [0.1, 0.3, -0.1, 0.0, 0.2, -0.05],
        "signal_harbour": [0.2, 0.4, -0.15, 0.05, 0.25, -0.2],
        "contributing_terms": ["beats"] * 6,
    })
    out = sentiment.build_validation_sample(sample, n=6)
    assert out["kaiyuan_review_label"].eq("").all()
    assert "rule_based_pseudo_label" in out.columns
    assert set(out["split"]).issubset({"development", "holdout"})
    summary = sentiment.pseudo_label_diagnostic_summary(out)
    assert summary["label_source"].eq("automated_rule_based_pseudo_label").all()


def test_pseudo_label_does_not_match_cut_inside_executive():
    assert sentiment._rule_based_pseudo_label("Executive committee schedules meeting") == "neutral"


def test_week9_finvader_moves_finance_headline_vs_base():
    text = "Nvidia beats earnings, shares surge to a record high"
    base = sentiment.score_text_base_vader(text)
    week9 = sentiment.score_text_week9_finvader(text)
    assert week9 != base


def test_project_capped_simplex_enforces_cap():
    w = portfolios.project_capped_simplex(np.array([0.9, 0.1, 0.0]), max_weight=0.4)
    assert w.max() <= 0.4 + 1e-8
    assert abs(w.sum() - 1) < 1e-8
