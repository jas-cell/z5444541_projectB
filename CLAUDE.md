# CLAUDE.md — Kaiyuan Lan (z5444541) Project B working rules

This file records the instructions I actually give the coding assistant for FINS3645 Project B (Signal Harbour).

## Authorship (hard rule)

- I am the sole author of the assessed report, economic interpretation, critiques, and final evaluation claims.
- Reviews of the package are mine, optionally with suggestions from a third-party Claude session. That combination is fine. The coding assistant does not own those review findings.
- The coding assistant implements code and pulls supporting evidence under my direction only.

## Project

- Folder: `/Users/jaysonlan/Desktop/z5444541_projectB`
- Course: FINS3645 Part B; continuity with Part A at `/Users/jaysonlan/Desktop/z5444541_projectA`
- Product identity: Signal Harbour — research product for a small wealth-advisory firm; day-to-day user is a portfolio analyst
- Data: official course ZIP via `FINS_DATA_ZIP` or `src/data_access.py` helper (do not commit parquet)

## Hard modelling rules

1. Walk-forward only. Form weights from returns strictly before the rebalance decision date.
2. Monthly decisions, next-session effectiveness, holdings drift between rebalances. Do not hold constant target weights every day and call it monthly rebalancing.
3. One Sharpe definition everywhere: zero risk-free arithmetic mean / volatility (annualised). Keep CAGR as a separate metric.
4. Rescale optimiser objectives (annualised covariance). `success=True` is not enough — require measurable improvement versus equal weight and check methods differ.
5. Sentiment is equity headlines only; lag at least one equity session before any trading use.
6. Signal Harbour primary model must start from the Week 9 finVADER base, then add masks/terms/phrases and context weights. Do not call a plain-VADER heuristic “augmented finVADER”.
7. Attention confidence uses elevated Attention Pulse only; low volume must not raise confidence.
8. Precompute under `results/`. Streamlit loads CSV artifacts only — no runtime VADER or backtests.
9. Treat missing headline days as neutral after the lag; justify in the report.
10. Equity calendar annualises at 252; crypto native funds at 365; document mixed-sleeve handling in the app.

## Folder layout

- `src/` modelling code
- `scripts/run_part_b.py` reproducible rebuild
- `results/{data,tables,figures}` app/report inputs
- `report/` assessed report is `report.docx` / `report.pdf` (I author the prose)
- `ai/` prompt log, iteration log, research, continuity docs
- `tests/` regression checks for lag, drift, Sharpe, caps, calendars

## Verification I expect

- `python scripts/run_part_b.py`
- `python -m pytest -q`
- `python scripts/check_handin.py`
- Manual checks: weight sums, method divergence, headline weekend→Monday mapping, explain-tab date alignment, Allocate calendar behaviour
- Do not invent prompts, mistakes, or human labels. If a review sheet is blank, say so; if I label headlines, record that separately.

## Report / app voice

- I write the assessed report in my own words for a financially literate non-technical reader.
- Assistant role: pull genuine strong points from generated tables, figures, CSVs, source files, or cited methods as supporting evidence; help with structure and exhibit notes; never invent results; never author final economic claims.
- Every exhibit must be self-contained (period, source, plain interpretation) and referenced in the text.
- Final claims are checked and rewritten by me against the evidence before they enter the report.
- Weak or negative fusion/model outcomes stay disclosed; add turnover/cost context instead of overselling.
