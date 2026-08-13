# Report Evidence Notes - Project B

Student: Kaiyuan Lan (z5444541)

This file is not the final report and is not a substitute for it. I author the assessed report in `report/report.docx` / `report/report.pdf`. These notes are a working scrapbook of candidate evidence only. Prefer live CSVs under `results/tables/` and `results/data/` over any stale figures written here earlier.

## Product framing

- App name: Signal Harbour.
- User: a small advisory team or self-directed investor who wants to compare systematic equity, crypto, and combined funds in one place and see current holdings, realised risk, and sector-level news sentiment without re-running models inside the app.
- Gap filled: many portfolio dashboards either stop at historical charting or treat crypto and equities as if they share one calendar and one risk structure. Signal Harbour separates family-specific backtests, then offers combined funds on the equity trading calendar that a mixed-asset investor could actually implement.

## Backtest design points to state clearly

- Out-of-sample period starts on 4 January 2021 for equity and combined funds, and 1 January 2021 for crypto funds.
- Estimation window is 252 trading days for equity and combined funds, and 365 daily observations for crypto.
- Rebalancing is monthly using the first live trading day of each month.
- Portfolio weights are formed only from trailing returns available before the rebalance date.
- Sharpe ratios use a zero risk-free rate.
- Combined funds use crypto returns aligned onto the equity calendar after returns are computed on the native crypto calendar.

## Main fund results

### Best risk-adjusted fund

- Combined Risk Parity has the highest Sharpe ratio at 0.871.
- Its annualised return is 13.95% with annualised volatility of 16.02%.
- Max drawdown is -19.85%, which is materially smaller than the drawdowns on the crypto-only funds.

Interpretation angle:
This is the cleanest candidate for a client-facing flagship fund because it preserves most of the upside of the combined universe without inheriting the extreme drawdown profile of the crypto sleeve.

### Best raw-growth combined fund

- Combined Maximum Sharpe has the highest terminal wealth among combined funds at 1.70x.
- Annualised return is 19.37%, but volatility rises to 22.69% and max drawdown reaches -24.08%.

Interpretation angle:
This fund earns its higher growth through concentration. It is a stronger option for a return-seeking investor, but it is harder to defend as the default recommendation because the path is rougher and the holdings are more concentrated.

### Equity-only comparison

- Equity Equal Weight is the strongest equity-only baseline on Sharpe at 0.782.
- Equity Risk Parity lowers volatility to 14.58% and drawdown to -18.53%, but its Sharpe remains below Equal Weight at 0.682.
- Equity Maximum Sharpe underperforms the simpler alternatives in both Sharpe and drawdown.

Interpretation angle:
Within the equity sleeve, the simple baseline is hard to beat. That matters because it keeps the report honest: more optimisation is not automatically better.

### Crypto-only comparison

- Crypto Minimum Variance is the strongest crypto-only fund in this run, with annualised return of 45.02% and Sharpe of 0.641.
- Crypto Maximum Sharpe performs poorly out of sample, with negative annualised return of -7.02% and Sharpe of -0.093.
- All crypto-only funds carry very large drawdowns, from about -74% to -85%.

Interpretation angle:
Crypto diversification can lift returns, but the standalone crypto sleeve remains too volatile to present without a strong warning about drawdowns.

## Holdings evidence

### Combined Risk Parity latest holdings

Largest weights at the latest rebalance on 1 December 2023:

- MRK: 3.75%
- ABBV: 3.72%
- WMT: 3.40%
- KO: 3.24%
- TMUS: 3.21%

Interpretation angle:
The strongest Sharpe fund is diversified and defensive rather than momentum-chasing. That helps explain why it outperforms on risk-adjusted terms even though it does not post the highest raw return.

### Combined Maximum Sharpe latest holdings

Largest weights at the latest rebalance on 1 December 2023:

- GE: 25.00%
- NVDA: 20.09%
- SO: 16.81%
- ADBE: 10.35%
- BTC-USD: 10.30%

Interpretation angle:
This portfolio is concentrated in a small set of assets with strong trailing realised behaviour. That concentration is exactly why the return is higher and the path risk is higher.

## Sentiment index results

- Primary model is Signal Harbour Context-Weighted finVADER: augmented score × coverage confidence × Attention Pulse confidence, lagged one equity session.
- On a 4,000-headline sample:
  - base VADER: neutral 49.6%, exact zero 48.9%
  - Week 9 finVADER: neutral 62.1%, exact zero 17.4% (moves many exact zeros into small non-zero scores)
  - Signal Harbour: neutral 46.3%, exact zero 45.5%, highest positive share 41.3%
- Week 9 finVADER is now the true course benchmark (SentiBigNomics*0.1 + Henry), not a Henry-only fallback.
- Ablation: removing custom terms widens neutrality again; phrases contribute a smaller incremental effect on the sampled subset.
- The displayed app series uses a 21-trading-day rolling average for readability, while the underlying file keeps the raw daily sector index.

Interpretation angle:
The sector index is best presented as a slow-moving information backdrop rather than a direct trading trigger. Coverage gains are real, but denser sentiment is not automatic alpha.

## Fusion result

### Base comparison

- After optimiser rescaling, conventional Sharpe, and drifting monthly holdings, Equity Minimum Variance has zero-rf Sharpe about 0.4740.
- Equity Minimum Variance plus the lagged context-weighted tilt has Sharpe about 0.4711.
- The tilt is look-ahead-safe, but the economic result is a small deterioration, not an improvement.

Interpretation angle:
Do not claim fusion uplift. The honest conclusion is that the lagged overlay slightly worsens the MinVar path in this sample and weakens further under equal turnover costs.

### Robustness grid

Across the tested fixed grid:

- Equal Weight plus a mild tilt of 0.15 gives the strongest fusion Sharpe at 0.779, but this remains below the un-tilted Equity Equal Weight baseline of 0.782.
- Risk Parity plus sentiment also weakens slightly as tilt strength increases.
- Minimum Variance plus sentiment is effectively flat across 0.15, 0.35, and 0.60.

Interpretation angle:
The main result is robust in a useful way: the sentiment overlay does not collapse performance, but it also does not produce compelling incremental alpha across reasonable tilt strengths. That makes it a credible extension rather than an overclaimed breakthrough.

## Recommendation ideas for the final report

1. Recommend Combined Risk Parity as the default diversified fund for a broad client base.
2. Recommend Combined Maximum Sharpe as an aggressive satellite option for return-seeking investors willing to accept concentration and larger drawdowns.
3. Keep the sentiment analytics in the app as a decision-support layer and research extension, not as the main selling point of the investable funds.

## Limits to acknowledge

- Headline sentiment is a noisy proxy and not the same as article-level or earnings-call sentiment.
- The helper loads public hosted data, so first-run reproducibility still depends on network access unless a local ZIP is supplied through `FINS_DATA_ZIP`.
- The fusion rule is intentionally simple. It is useful as an honest baseline, but not yet a fully developed signal model.
